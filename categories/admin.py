from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "type")
    list_filter = ("type",)
    search_fields = ("title", "user")
    ordering = ("title",)