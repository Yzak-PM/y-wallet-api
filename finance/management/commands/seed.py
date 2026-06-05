from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Account
from categories.models import Category
from tags.models import Tag
from transactions.models import Transaction
from django.db import transaction
from faker import Faker
from decimal import Decimal
import random
from datetime import date

User = get_user_model()
fake = Faker()

def random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def random_date_in_month(year, month):
    """Returns a random date within the given month."""
    import calendar
    max_day = calendar.monthrange(year, month)[1]
    return date(year, month, random.randint(1, max_day))

class Command(BaseCommand):
    help = "Seed database with users, accounts, categories, tags and transactions"

    def handle(self, *args, **kwargs):
        self.stdout.write("Cleaning database...")

        with transaction.atomic():
            Transaction.objects.all().delete()
            Tag.objects.all().delete()
            Category.objects.all().delete()
            Account.objects.all().delete()
            User.objects.all().delete()

        self.stdout.write("Database cleaned.")

        admin = User.objects.create_superuser(
            email="admin@mail.com",
            username="admin",
            password="1234"
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

            # 🔹 Create accounts
            account_configs = [
                ("Cash Wallet",     Account.Type.CASH,    Account.Nature.ASSET),
                ("Main Bank",       Account.Type.BANK,    Account.Nature.ASSET),
                ("Savings Account", Account.Type.SAVINGS, Account.Nature.ASSET),
                ("Credit Card",     Account.Type.CREDIT,  Account.Nature.LIABILITY),
                ("Personal Loan",   Account.Type.LOAN,    Account.Nature.LIABILITY),
            ]

            accounts = []
            for name, acc_type, nature in account_configs:
                acc = Account.objects.create(
                    user=user,
                    name=name,
                    type=acc_type,
                    nature=nature,
                    color=random_color(),
                    balance=Decimal(random.randint(100, 10000))
                )
                accounts.append(acc)
            self.stdout.write(f"Accounts created for {user.username}")

            # 🔹 Create categories
            category_configs = [
                ("Food",          Transaction.Type.EXPENSE),
                ("Transport",     Transaction.Type.EXPENSE),
                ("Entertainment", Transaction.Type.EXPENSE),
                ("Health",        Transaction.Type.EXPENSE),
                ("Bills",         Transaction.Type.EXPENSE),
                ("Shopping",      Transaction.Type.EXPENSE),
                ("Education",     Transaction.Type.EXPENSE),
                ("Salary",        Transaction.Type.INCOME),
            ]

            categories_by_type = {
                Transaction.Type.EXPENSE: [],
                Transaction.Type.INCOME:  [],
            }

            for name, tx_type in category_configs:
                cat = Category.objects.create(
                    user=user,
                    title=name,
                    color=random_color()
                )
                categories_by_type[tx_type].append(cat)
            self.stdout.write(f"Categories created for {user.email}")

            # 🔹 Create tags
            tag_configs = [
                ("deductible",   "#4CAF50"),
                ("urgent",       "#F44336"),
                ("recurring",    "#2196F3"),
                ("work",         "#9C27B0"),
                ("family",       "#FF9800"),
                ("travel",       "#00BCD4"),
                ("subscription", "#607D8B"),
                ("savings-goal", "#8BC34A"),
            ]

            tags = []
            for name, color in tag_configs:
                tag = Tag.objects.create(
                    user=user,
                    name=name,
                    color=color
                )
                tags.append(tag)
            self.stdout.write(f"Tags created for {user.username}")

            # 🔹 Create transactions (at least 2 per month: Jan–Apr 2026)
            asset_accounts = [a for a in accounts if a.nature == Account.Nature.ASSET]

            # Templates per month to guarantee variety
            monthly_templates = [
                # (type, category_type, description, amount_range)
                (Transaction.Type.INCOME,  Transaction.Type.INCOME,  "Monthly salary",          (1500, 4000)),
                (Transaction.Type.EXPENSE, Transaction.Type.EXPENSE, "Grocery shopping",        (30,   150)),
                (Transaction.Type.EXPENSE, Transaction.Type.EXPENSE, "Electricity bill",        (40,   120)),
                (Transaction.Type.EXPENSE, Transaction.Type.EXPENSE, "Restaurant dinner",       (15,   80)),
                (Transaction.Type.INCOME,  Transaction.Type.INCOME,  "Freelance payment",       (200,  800)),
                (Transaction.Type.EXPENSE, Transaction.Type.EXPENSE, "Transport / Uber",        (10,   50)),
                (Transaction.Type.MOVEMENT, None,                    "Transfer to savings",     (100,  500)),
                (Transaction.Type.EXPENSE, Transaction.Type.EXPENSE, "Online subscription",     (5,    20)),
            ]

            for month in [1, 2, 3, 4]:
                # Shuffle to get different combos each month
                month_templates = random.sample(monthly_templates, k=random.randint(4, len(monthly_templates)))

                for tx_type, cat_type, description, amount_range in month_templates:
                    tx_date = random_date_in_month(2026, month)
                    amount  = Decimal(str(round(random.uniform(*amount_range), 2)))

                    if tx_type == Transaction.Type.MOVEMENT:
                        if len(asset_accounts) < 2:
                            continue
                        src, dst = random.sample(asset_accounts, 2)
                        cat = random.choice(
                            categories_by_type[Transaction.Type.EXPENSE]
                        )
                        tx = Transaction.objects.create(
                            user=user,
                            account=src,
                            destination_account=dst,
                            category=cat,
                            date=tx_date,
                            description=description,
                            type=Transaction.Type.MOVEMENT,
                            amount=amount,
                        )
                    else:
                        cat = random.choice(categories_by_type[cat_type])
                        account = random.choice(
                            asset_accounts if tx_type == Transaction.Type.INCOME
                            else accounts
                        )
                        tx = Transaction.objects.create(
                            user=user,
                            account=account,
                            category=cat,
                            date=tx_date,
                            description=description,
                            type=tx_type,
                            amount=amount,
                        )

                    # Assign 0–3 random tags
                    tx.tags.set(random.sample(tags, k=random.randint(0, 3)))

            tx_count = Transaction.objects.filter(user=user).count()
            self.stdout.write(self.style.SUCCESS(
                f"Transactions created for {user.username}: {tx_count} total"
            ))

        self.stdout.write(self.style.SUCCESS("Seeding completed!"))