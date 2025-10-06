# projects/admin.py
from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "site_key", "created_at")
    search_fields = ("name", "user__username", "site_key")
    readonly_fields = ("site_key", "secret_key", "created_at")

