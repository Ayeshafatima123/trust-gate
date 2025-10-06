
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserWallet

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        UserWallet.objects.create(user=instance)
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserWallet, Subscription, Plan

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        UserWallet.objects.create(user=instance)
        # Default FREE plan
        free_plan = Plan.objects.filter(name="FREE").first()
        if free_plan:
            Subscription.objects.create(user=instance, plan=free_plan, active=True)
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from billing.models import Plan, Subscription

@receiver(post_save, sender=User)
def assign_free_plan(sender, instance, created, **kwargs):
    if created:
        free_plan = Plan.objects.get(name="Free")
        Subscription.objects.create(user=instance, plan=free_plan)
