# billing/utils.py
from billing.models import Wallet

def update_wallet(user, reward):
    wallet, _ = Wallet.objects.get_or_create(user=user)
    wallet.balance += reward
    wallet.save()
# billing/utils.py
from datetime import datetime, timedelta
from django.utils.timezone import now
from billing.models import Subscription

def record_usage_or_block(user):
    """
    Har API call ya captcha use hone par quota check karta hai.
    Agar quota exceed ho gaya to False return karega, warna usage count karega.
    """

    try:
        subscription = Subscription.objects.get(user=user)
    except Subscription.DoesNotExist:
        return False  # user ke paas subscription hi nahi hai → block

    plan = subscription.plan
    if not plan:
        return False

    # Abhi ke month ka usage check karo
    if subscription.usage_count >= plan.monthly_quota_captcha:
        return False  # ❌ Quota khatam

    # ✅ Usage update
    subscription.usage_count += 1
    subscription.save()
    return True
# billing/utils.py
from billing.models import Wallet

def update_wallet(user, reward):
    wallet, _ = Wallet.objects.get_or_create(user=user)
    wallet.balance += reward
    wallet.save()
from .models import Wallet

def update_wallet(user, reward):
    wallet, _ = Wallet.objects.get_or_create(user=user)
    wallet.balance += reward
    wallet.save()
# billing/utils.py

def send_to_easypaisa(mobile, amount):
    """
    Dummy Easypaisa API call
    """
    print(f"✅ Sending Rs.{amount} to Easypaisa number {mobile}...")
    return {
        "status": "SUCCESS",
        "transaction_id": "TXN123456789"
    }
from billing.models import Wallet
from decimal import Decimal

def reward_user(user, amount=Decimal("0.50")):  # har captcha = Rs 0.50
    wallet, created = Wallet.objects.get_or_create(user=user)
    wallet.balance += amount
    wallet.save()
    return wallet.balance

