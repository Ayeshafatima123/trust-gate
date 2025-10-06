from django.contrib import admin# billing/admin.py
from django.contrib import admin
from .models import Plan, Subscription, Usage, Wallet, WithdrawRequest

admin.site.register(Plan)
admin.site.register(Subscription)
admin.site.register(Usage)
admin.site.register(Wallet)
admin.site.register(WithdrawRequest)



