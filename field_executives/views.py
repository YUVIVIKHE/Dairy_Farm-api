from django.db.models import Q
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from field_executives.models import FieldExecutive, FieldExecutiveStatus
from field_executives.permissions import IsAdmin
from field_executives.serializers import (
    CreateFieldExecutiveSerializer,
    FieldExecutiveSerializer,
    generate_secure_password,
)


class FieldExecutiveListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        queryset = FieldExecutive.objects.select_related("user").all()

        search = request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(employee_id__icontains=search)
                | Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__mobile_number__icontains=search)
                | Q(assigned_area__icontains=search)
            )

        status_filter = request.query_params.get("status")
        if status_filter in FieldExecutiveStatus.values:
            queryset = queryset.filter(status=status_filter)

        area = request.query_params.get("area")
        if area:
            queryset = queryset.filter(assigned_area=area)

        joined_after = request.query_params.get("joinedAfter")
        if joined_after:
            queryset = queryset.filter(joined_date__gte=joined_after)

        joined_before = request.query_params.get("joinedBefore")
        if joined_before:
            queryset = queryset.filter(joined_date__lte=joined_before)

        try:
            page = max(int(request.query_params.get("page", 1)), 1)
            page_size = max(int(request.query_params.get("pageSize", 50)), 1)
        except ValueError:
            page, page_size = 1, 50

        total = queryset.count()
        start = (page - 1) * page_size
        items = queryset[start : start + page_size]

        serializer = FieldExecutiveSerializer(
            items, many=True, context={"request": request}
        )
        return Response(
            {
                "items": serializer.data,
                "total": total,
                "page": page,
                "pageSize": page_size,
            }
        )

    def post(self, request):
        serializer = CreateFieldExecutiveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(
            {
                "fieldExecutive": FieldExecutiveSerializer(
                    result["fieldExecutive"], context={"request": request}
                ).data,
                "loginId": result["loginId"],
                "temporaryPassword": result["temporaryPassword"],
            },
            status=status.HTTP_201_CREATED,
        )


class FieldExecutiveDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, pk):
        field_executive = get_object_or_404(
            FieldExecutive.objects.select_related("user"), pk=pk
        )
        serializer = FieldExecutiveSerializer(
            field_executive, context={"request": request}
        )
        return Response(serializer.data)


class FieldExecutiveActivateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        field_executive = get_object_or_404(FieldExecutive, pk=pk)
        field_executive.status = FieldExecutiveStatus.ACTIVE
        field_executive.save(update_fields=["status", "updated_at"])
        field_executive.user.is_active = True
        field_executive.user.save(update_fields=["is_active"])
        serializer = FieldExecutiveSerializer(
            field_executive, context={"request": request}
        )
        return Response(serializer.data)


class FieldExecutiveDeactivateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        field_executive = get_object_or_404(FieldExecutive, pk=pk)
        field_executive.status = FieldExecutiveStatus.INACTIVE
        field_executive.save(update_fields=["status", "updated_at"])
        field_executive.user.is_active = False
        field_executive.user.save(update_fields=["is_active"])
        serializer = FieldExecutiveSerializer(
            field_executive, context={"request": request}
        )
        return Response(serializer.data)


class FieldExecutiveResetPasswordView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        field_executive = get_object_or_404(FieldExecutive, pk=pk)
        new_password = generate_secure_password()
        field_executive.user.set_password(new_password)
        field_executive.user.save(update_fields=["password"])
        return Response({"temporaryPassword": new_password})


class FieldExecutiveAreasView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        areas = (
            FieldExecutive.objects.exclude(assigned_area="")
            .order_by("assigned_area")
            .values_list("assigned_area", flat=True)
            .distinct()
        )
        return Response(list(areas))
