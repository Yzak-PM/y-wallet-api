from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Account
from categories.models import Category
from tags.models import Tag
from faker import Faker
from decimal import Decimal
import random

User = get_user_model()
fake = Faker()

def random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

class Command(BaseCommand):
    help = "Seed database with users, accounts, and categories"

    def handle(self, *args, **kwargs):
        self.stdout.write("Cleaning database...")

        #* ORDEN IMPORTANTE (por foreign keys)
        Account.objects.all().delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()
        User.objects.all().delete()

        self.stdout.write("Database cleaned.")

        #* Create superuser admin
        admin = User.objects.create_superuser(
            email = "admin@mail.com",
            username = "admin",
            password = "1234"
        )
        self.stdout.write(self.style.SUCCESS(f"Superuser created: {admin.username} / 1234"))

        for _ in range(2):
            # 🔹 Create user
            user = User.objects.create(
                email=fake.unique.email(),
                username=fake.unique.user_name()
            )
            user.set_password("123456")
            user.save()

            self.stdout.write(f"Created user: {user.username}")

            # 🔹 Create accounts (1 por tipo relevante)
            account_configs = [
                ("Cash Wallet", Account.Type.CASH, Account.Nature.ASSET),
                ("Main Bank", Account.Type.BANK, Account.Nature.ASSET),
                ("Savings Account", Account.Type.SAVINGS, Account.Nature.ASSET),
                ("Credit Card", Account.Type.CREDIT, Account.Nature.LIABILITY),
                ("Personal Loan", Account.Type.LOAN, Account.Nature.LIABILITY),
            ]

            for name, acc_type, nature in account_configs:
                Account.objects.create(
                    user=user,
                    name=name,
                    type=acc_type,
                    nature=nature,
                    color=random_color(),
                    balance=Decimal(random.randint(100, 10000))
                )

            self.stdout.write(f"Accounts created for {user.username}")

            # 🔹 Create categories
            category_names = [
                "Food",
                "Transport",
                "Entertainment",
                "Health",
                "Salary",
                "Bills",
                "Shopping",
                "Education"
            ]

            for name in category_names:
                Category.objects.create(
                    user=user,
                    title=name,
                    color=random_color()
                )

            self.stdout.write(f"Categories created for {user.email}")

            #* Create tags
            tag_configs = [
                ("deductible",  "#4CAF50", "receipt"),
                ("urgent",      "#F44336", "alert-circle"),
                ("recurring",   "#2196F3", "refresh-cw"),
                ("work",        "#9C27B0", "briefcase"),
                ("family",      "#FF9800", "home"),
                ("travel",      "#00BCD4", "plane"),
                ("subscription","#607D8B", "credit-card"),
                ("savings-goal","#8BC34A", "target"),
            ]

            for name, color, icon in tag_configs:
                Tag.objects.create(
                    user=user,
                    name=name,
                    color=color,
                    icon=icon
                )

            self.stdout.write(f"Tags created for {user.username}")

        self.stdout.write(self.style.SUCCESS("Seeding completed!"))