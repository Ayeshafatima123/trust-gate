from django.db import models
from django.conf import settings
from decimal import Decimal
from django.utils import timezone


class CaptchaTask(models.Model):
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    reward = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.50"))  # Rs. 0.50 per captcha
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CaptchaTask #{self.id} - {self.question}"


class CaptchaSubmission(models.Model):
    task = models.ForeignKey(CaptchaTask, on_delete=models.CASCADE, related_name="submissions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    user_answer = models.CharField(max_length=255, default="", blank=True)
    correct = models.BooleanField(default=False)
    reward = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now, blank=True)

    def __str__(self):
        status = "✔ Correct" if self.correct else "✘ Wrong"
        return f"{self.user.username} - Task {self.task.id} - {status}"


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="captcha_wallet")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def deposit(self, amount):
        self.balance += amount
        self.save()

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.user.username} - {self.balance}"
    
from django.db import models
from django.contrib.auth.models import User   # 👈 ye line zaroor add karocd 

class CaptchaSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="captcha_submissions")
    task = models.ForeignKey(CaptchaTask, on_delete=models.CASCADE)
    user_answer = models.CharField(max_length=255)
    correct = models.BooleanField(default=False)
    reward = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
