from django.db import models
from django.conf import settings
from walletapp.core.models import BaseSoftDeleteModel

class Account(BaseSoftDeleteModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="accounts"
    )

    class Type(models.TextChoices):
        CASH = "cash", "Cash"
        BANK = "bank", "Bank"
        CREDIT = "credit", "Credit"
        LOAN = "loan", "Loan"
        SAVINGS = "savings", "Savings"

    class Nature(models.TextChoices):
            ASSET = "asset", "Asset"
            LIABILITY = "liability", "Liability"

    name = models.CharField(max_length=20)
    type = models.CharField(max_length=20, choices=Type.choices)
    nature = models.CharField(max_length=10, choices=Nature.choices)
    color = models.CharField(max_length=7, default="#B88BFD")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.name