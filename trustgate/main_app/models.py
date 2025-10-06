from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    PLAN_FREE = "FREE"
    PLAN_PRO = "PRO"
    PLAN_CHOICES = [(PLAN_FREE, "Free"), (PLAN_PRO, "Pro")]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default=PLAN_FREE)

    @property
    def is_paid(self):
        return self.plan == self.PLAN_PRO

    def __str__(self):
        return f"{self.user.username} ({self.plan})"

