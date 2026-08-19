from django.core.management.base import BaseCommand

from accounts.models import Role, User

SEED_USERS = [
    {
        "username": "admin",
        "password": "Admin@123",
        "role": Role.ADMIN,
        "first_name": "Farm",
        "last_name": "Admin",
        "mobile_number": "9000000001",
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "username": "mco",
        "password": "Mco@12345",
        "role": Role.MILK_COLLECTION_OFFICER,
        "first_name": "Milk Collection",
        "last_name": "Officer",
        "mobile_number": "9000000002",
        "is_staff": True,
        "is_superuser": False,
    },
    {
        "username": "farmer",
        "password": "Farmer@123",
        "role": Role.FARMER,
        "first_name": "Demo",
        "last_name": "Farmer",
        "mobile_number": "9000000003",
        "is_staff": False,
        "is_superuser": False,
    },
]


class Command(BaseCommand):
    help = "Seeds one demo user for each role: Admin, MCO, Farmer."

    def handle(self, *args, **options):
        for entry in SEED_USERS:
            username = entry["username"]
            password = entry.pop("password")
            user, created = User.objects.update_or_create(
                username=username,
                defaults={k: v for k, v in entry.items() if k != "username"},
            )
            user.set_password(password)
            user.save()

            status = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f"{status} {user.role} user -> username: {username} / password: {password}"
                )
            )
