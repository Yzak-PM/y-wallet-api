from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
  list_display = ("id", "user", "category", "type", "account", "destination_account", "date", "amount")
  list_filter = ("category", "type")
  search_fields = ("user", "date")
  ordering = ("id", )