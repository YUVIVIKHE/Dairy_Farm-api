import secrets
import string

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from accounts.models import Role, User
from field_executives.models import FieldExecutive


def generate_employee_id() -> str:
    last = FieldExecutive.objects.order_by("-id").first()
    next_number = (last.id + 1) if last else 1
    candidate = f"DFE-{next_number:03d}"
    while FieldExecutive.objects.filter(employee_id=candidate).exists():
        next_number += 1
        candidate = f"DFE-{next_number:03d}"
    return candidate


def generate_secure_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
        ):
            return password


class FieldExecutiveSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="pk", read_only=True)
    employeeId = serializers.CharField(source="employee_id", read_only=True)
    fullName = serializers.SerializerMethodField()
    mobile = serializers.CharField(source="user.mobile_number", read_only=True)
    email = serializers.SerializerMethodField()
    profilePhotoUrl = serializers.SerializerMethodField()
    assignedArea = serializers.CharField(source="assigned_area")
    address = serializers.SerializerMethodField()
    status = serializers.CharField()
    farmersCount = serializers.IntegerField(source="farmers_count")
    todaysCollectionLiters = serializers.IntegerField(
        source="todays_collection_liters"
    )
    joinedDate = serializers.DateField(source="joined_date", format="%Y-%m-%d")
    createdAt = serializers.DateTimeField(source="created_at")
    updatedAt = serializers.DateTimeField(source="updated_at")

    class Meta:
        model = FieldExecutive
        fields = [
            "id",
            "employeeId",
            "fullName",
            "mobile",
            "email",
            "profilePhotoUrl",
            "assignedArea",
            "address",
            "status",
            "farmersCount",
            "todaysCollectionLiters",
            "joinedDate",
            "createdAt",
            "updatedAt",
        ]

    def get_fullName(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_email(self, obj):
        return obj.user.email or None

    def get_address(self, obj):
        return obj.address or None

    def get_profilePhotoUrl(self, obj):
        if not obj.profile_photo:
            return None
        request = self.context.get("request")
        url = obj.profile_photo.url
        return request.build_absolute_uri(url) if request else url


class CreateFieldExecutiveSerializer(serializers.Serializer):
    fullName = serializers.CharField(max_length=150)
    mobile = serializers.RegexField(regex=r"^[6-9]\d{9}$")
    email = serializers.EmailField(required=False, allow_blank=True)
    assignedArea = serializers.CharField(max_length=120)
    address = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )
    profilePhoto = serializers.ImageField(required=False, allow_null=True)
    passwordMode = serializers.ChoiceField(choices=["GENERATE", "TEMPORARY"])
    temporaryPassword = serializers.CharField(
        required=False, allow_blank=True, min_length=8
    )

    def validate_mobile(self, value):
        if User.objects.filter(mobile_number=value).exists():
            raise serializers.ValidationError(
                "A field executive with this mobile number already exists."
            )
        return value

    def validate(self, attrs):
        if attrs["passwordMode"] == "TEMPORARY" and not attrs.get(
            "temporaryPassword"
        ):
            raise serializers.ValidationError(
                {"temporaryPassword": "Enter a temporary password."}
            )
        return attrs

    @transaction.atomic
    def save(self, **kwargs):
        data = self.validated_data
        employee_id = generate_employee_id()

        password = (
            data["temporaryPassword"]
            if data["passwordMode"] == "TEMPORARY"
            else generate_secure_password()
        )

        full_name = data["fullName"].strip()
        first_name, _, last_name = full_name.partition(" ")

        user = User.objects.create_user(
            username=employee_id,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=data.get("email", "") or "",
            mobile_number=data["mobile"],
            role=Role.MILK_COLLECTION_OFFICER,
        )

        field_executive = FieldExecutive.objects.create(
            user=user,
            employee_id=employee_id,
            assigned_area=data["assignedArea"],
            address=data.get("address", "") or "",
            profile_photo=data.get("profilePhoto"),
            joined_date=timezone.localdate(),
        )

        return {
            "fieldExecutive": field_executive,
            "loginId": employee_id,
            "temporaryPassword": password,
        }
