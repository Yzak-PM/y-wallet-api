from django.db import models
from django.conf import settings
from walletapp.core.models import BaseSoftDeleteModel

class Category(BaseSoftDeleteModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories"
    )

    class Type(models.TextChoices):
        INCOME = "income", "Income"
        EXPENSE = "expense", "Expense"

    type = models.CharField(max_length=20, choices=Type.choices)
    title = models.CharField(max_length=75)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#C90F0F")
    icon = models.CharField(max_length=10, default="🏷️")

    class Meta: 
        unique_together = ("user", "title")

    def __str__(self):
        return self.title