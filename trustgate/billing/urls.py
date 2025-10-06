# billing/urls.py
from django.urls import path
from . import views

app_name = "billing"

urlpatterns = [
    path("", views.billing_home, name="billing_home"),
    path("easypaisa/checkout/<int:plan_id>/", views.easypaisa_checkout, name="easypaisa_checkout"),
    path("success/", views.success, name="success"),
    # add callback if you implement real Easypaisa webhook later
    # path("easypaisa/callback/", views.easypaisa_callback, name="easypaisa_callback"),
]
from django.urls import path
from . import views

app_name = "billing"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),  # 👈 /billing/ open karega billing dashboard
    path("easypaisa/callback/", views.easypaisa_callback, name="easypaisa_callback"),
    path("easypaisa/checkout/<int:plan_id>/", views.easypaisa_checkout, name="easypaisa_checkout"),
    path("withdraw/", views.withdraw, name="withdraw"),
]

from django.urls import path
from .views import withdraw_view

urlpatterns = [
    path("", withdraw_view, name="billing_home"),   # billing/ open hote hi withdraw dikhaye
    path("withdraw/", withdraw_view, name="withdraw"),

]

from django.urls import path
from . import views

app_name = "billing"

urlpatterns = [
    path("", views.billing_home, name="billing_home"),  # 👈 yahan plan_id nahi hoga
    path("checkout/<int:plan_id>/", views.easypaisa_checkout, name="easypaisa_checkout"),


]
from django.urls import path
from . import views

app_name = "billing"

urlpatterns = [
    path("", views.billing_view, name="billing_home"),
    path("checkout/<int:plan_id>/", views.easypaisa_checkout, name="easypaisa_checkout"),
    path("callback/", views.easypaisa_callback, name="easypaisa_callback"),
]
from django.urls import path
from .views import withdraw_request_view


app_name = "billing"

urlpatterns = [
    path("", views.billing_home, name="billing_home"),
    path("checkout/<int:plan_id>/", views.easypaisa_checkout, name="easypaisa_checkout"),
    path("callback/", views.easypaisa_callback, name="easypaisa_callback"),
    path("easypaisa/", views.easypaisa_withdraw, name="easypaisa_withdraw"),
    path("withdraw/", withdraw_request_view, name="withdraw_request"),

]
from django.urls import path
from . import  webhooks,views
from django.shortcuts import redirect


app_name = "billing"

urlpatterns = [
    path("", views.billing_home, name="billing_home"),
    path("checkout/<int:plan_id>/", views.easypaisa_checkout, name="easypaisa_checkout"),
    path("callback/", views.easypaisa_callback, name="easypaisa_callback"),
    path("", lambda request: redirect("billing:wallet")),
    path("wallet/", views.wallet_view, name="wallet"),
    path("withdraw/", views.withdraw_view, name="withdraw"),
    path("pay/", views.easypaisa_payment_view, name="easypaisa_payment"),
    path("webhook/easypaisa/", webhooks.easypaisa_webhook, name="easypaisa_webhook"),
    path("activate-free/", views.activate_free_plan, name="activate_free_plan"),



]




