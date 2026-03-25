from django.db import models
from django.conf import settings
from walletapp.core.models import BaseSoftDeleteModel

class Transaction(BaseSoftDeleteModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    account = models.ForeignKey(
        'accounts.account',
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    
    destination_account = models.ForeignKey(
        'accounts.account',
        on_delete=models.SET_NULL,
        related_name="incoming_transactions",
        null=True,
        blank=True
    )

    category = models.ForeignKey(
        'categories.category',
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    tags = models.ManyToManyField(
        'tags.tag',
        related_name="transactions",
        blank=True
    )

    class Type(models.TextChoices):
        INCOME = "income", "Income"
        EXPENSE = "expense", "Expense"
        MOVEMENT = "movement", "Movement"

    date = models.DateField()
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=Type.choices)
    amount = models.DecimalField(max_digits=12,decimal_places=2)
