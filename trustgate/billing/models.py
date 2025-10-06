from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


# 📌 Payment Plans
class Plan(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)  # Rs
    monthly_quota_captcha = models.IntegerField(default=0)
    stripe_price_id = models.CharField(max_length=100, blank=True, null=True)
    

    def __str__(self):
        return f"{self.name} (Rs. {self.price})"


# 📌 User Subscription
class Subscription(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=False)
    started_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name if self.plan else 'No Plan'}"


# 📌 Usage Tracking (monthly)
class Usage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    month = models.DateField()  # e.g. 2025-09-01
    captcha_count = models.IntegerField(default=0)
    api_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ("user", "month")

    def __str__(self):
        return f"{self.user.username} - {self.month} (Captcha: {self.captcha_count}, API: {self.api_count})"


# 📌 Wallet (for earnings / balance)
class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # har user ka ek wallet
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

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
        return f"{self.user.username} Wallet: Rs. {self.balance}"


# 📌 Withdraw Requests (Easypaisa / JazzCash etc.)
class WithdrawRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("rejected", "Rejected"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    mobile_number = models.CharField(max_length=20, default="03000000000") 
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
 

    def __str__(self):
        return f"{self.user.username} - Rs {self.amount} ({self.status})"
# billing/models.py
from django.db import models
from django.conf import settings
from decimal import Decimal

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    def deposit(self, amount):
        self.balance = Decimal(self.balance) + Decimal(amount)
        self.save()

    def withdraw(self, amount):
        amount = Decimal(amount)
        if amount > self.balance:
            raise ValueError("Insufficient balance")
        self.balance = Decimal(self.balance) - amount
        self.save()

    def __str__(self):
        return f"{self.user} - {self.balance}"

class WithdrawRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="withdraw_requests")
    phone = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    external_id = models.CharField(max_length=255, blank=True, null=True, unique=True)  # tx id from gateway
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Withdraw {self.id} {self.user} {self.amount} {self.status}"
    
class Plan(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    captcha_limit = models.IntegerField()

    def __str__(self):
        return self.name
from django.contrib.auth.models import User


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    captchas_used = models.IntegerField(default=0)

    def remaining_captchas(self):
        return self.plan.captcha_limit - self.captchas_used
from django.db import models
from django.contrib.auth.models import User

class Plan(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_quota_captcha = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)   # <-- relation
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"
