from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
  list_display = ("id", "name", "user", "type", "nature", "balance")
  list_filter = ("type", "nature")
  search_fields = ("name", "user")
