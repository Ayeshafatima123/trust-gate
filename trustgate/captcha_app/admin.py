from django.contrib import admin
from .models import CaptchaSubmission

@admin.register(CaptchaSubmission)
class CaptchaSubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "task", "user_answer", "correct", "reward", "created_at")
    list_filter = ("correct", "created_at")

