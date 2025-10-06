
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages

from .models import Plan, Subscription  # adjust import to your models

def billing_home(request):
    plans = Plan.objects.all()
    subscription = None
    if request.user.is_authenticated:
        subscription = Subscription.objects.filter(user=request.user).first()
    return render(request, "billing/billing.html", {"plans": plans, "subscription": subscription})

@require_POST
@login_required
def easypaisa_checkout(request, plan_id):
    # 1) load plan
    plan = get_object_or_404(Plan, id=plan_id)

    # 2) update or create subscription for the logged in user
    subscription, created = Subscription.objects.update_or_create(
        user=request.user,
        defaults={"plan": plan}
    )

    # 3) Simulate payment / or redirect to payment gateway integration.
    # For local testing we simulate success and redirect to a success page.
    messages.success(request, "Subscription initialized (simulated Easypaisa).")
    return redirect("billing:success")

@login_required
def success(request):
    return render(request, "billing/success.html")
# billing/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Plan

def billing_home(request):
    plans = Plan.objects.all()   # 👈 sab plans le kar bhej do
    subscription = None          # 👈 agar tumne subscription system banaya hai to usko fetch karo

    return render(request, "billing/billing.html", {
        "plans": plans,
        "subscription": subscription,
    })

def easypaisa_checkout(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    # 👇 yahan tum apna easypaisa API integration karoge (abhi placeholder rakha hai)
    return render(request, "billing/success.html", {"plan": plan})

def success(request):
    return render(request, "billing/success.html")

def cancel(request):
    return render(request, "billing/cancel.html")
import requests
from django.shortcuts import redirect
from django.conf import settings
from .models import Plan, Subscription

EASYPAY_API_URL = "https://easypay.easypaisa.com.pk/easypay/"

def start_payment(request, plan_id):
    plan = Plan.objects.get(id=plan_id)

    # API request to EasyPaisa
    payload = {
        "storeId": settings.EASYPAY_STORE_ID,
        "amount": plan.price,
        "postBackURL": "http://127.0.0.1:8000/billing/easypaisa/callback/",
        "orderRefNum": f"ORDER-{request.user.id}-{plan.id}",
        "expiryDate": "2025-12-31 23:59:59",
    }

    response = requests.post(EASYPAY_API_URL + "initiateTransaction", json=payload)

    if response.status_code == 200:
        data = response.json()
        return redirect(data["paymentURL"])
    else:
        return redirect("/billing/error/")
from django.http import HttpResponse
from .models import Subscription
from .models import Wallet


def easypaisa_callback(request):
    order_ref = request.GET.get("orderRefNum")
    transaction_status = request.GET.get("transactionStatus")

    if transaction_status == "SUCCESS":
        try:
            user_id, plan_id = order_ref.split("-")[1:]  # ORDER-user-plan
            # ✅ Agar subscription pehle se exist hai to update karna
            subscription, created = Subscription.objects.get_or_create(
                user_id=user_id,
                defaults={"plan_id": plan_id, "active": True}
            )
            if not created:
                subscription.plan_id = plan_id
                subscription.active = True
                subscription.save()

            return HttpResponse("Payment Success! Plan Activated ✅")
        except Exception as e:
            return HttpResponse(f"Error: {str(e)} ❌")

    return HttpResponse("Payment Failed ❌")
from django.shortcuts import render
from .models import Plan, Subscription

def billing_home(request):
    plans = Plan.objects.all()
    subscription = None
    if request.user.is_authenticated:
        subscription = Subscription.objects.filter(user=request.user).first()

    return render(request, "billing/home.html", {
        "plans": plans,
        "subscription": subscription,
    })

from django.shortcuts import render
from .models import Plan, Subscription

def dashboard(request):
    plans = Plan.objects.all()
    subscription = None
    if request.user.is_authenticated:
        subscription = Subscription.objects.filter(user=request.user).first()
    return render(request, "billing/dashboard.html", {
        "plans": plans,
        "subscription": subscription
    })
# billing/views.py
from django.shortcuts import render
from django.http import HttpResponse
from .models import Wallet

def withdraw(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    if request.method == "POST":
        amount = float(request.POST.get("amount"))
        phone = request.POST.get("phone")

        if wallet.balance >= amount:
            wallet.balance -= amount
            wallet.save()
            return HttpResponse(f"✅ Rs.{amount} sent to {phone} via Easypaisa")
        else:
            return HttpResponse("❌ Insufficient balance")

    return render(request, "billing/withdraw.html", {"wallet": wallet})


from django.shortcuts import render, redirect
from django.contrib import messages
from billing.models import Wallet, WithdrawRequest
from decimal import Decimal
import requests

def withdraw_view(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    if request.method == "POST":
        phone = request.POST.get("phone")
        amount = Decimal(request.POST.get("amount", "0"))

        if amount <= 0:
            messages.error(request, "Invalid amount ❌")
            return redirect("billing:withdraw")

        if amount > wallet.balance:
            messages.error(request, "Insufficient balance ❌")
            return redirect("billing:withdraw")

        # Create withdraw request
        withdraw = WithdrawRequest.objects.create(
            user=request.user,
            phone=phone,
            amount=amount,
        )

        # [Step 1] Call Easypaisa API (example, sandbox URL)
        payload = {
            "storeId": "YOUR_STORE_ID",
            "transactionAmount": str(amount),
            "mobileNum": phone,
            "orderId": f"WDR-{withdraw.id}",
        }
        response = requests.post("https://easypaystg.easypaisa.com.pk/easypay-service/rest/v4/walletpayment", json=payload)

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "SUCCESS":
                withdraw.status = "success"
                wallet.balance -= amount
                wallet.save()
                withdraw.save()
                messages.success(request, "Withdraw successful ✅ Money sent to your Easypaisa.")
            else:
                withdraw.status = "failed"
                withdraw.save()
                messages.error(request, "Withdraw failed ❌ Please try again.")
        else:
            withdraw.status = "failed"
            withdraw.save()
            messages.error(request, "Error contacting Easypaisa API ❌")

        return redirect("billing:withdraw")

    return render(request, "billing/withdraw.html", {"wallet": wallet})
from django.shortcuts import render
from billing.models import Plan, Wallet

def billing_home(request):
    plans = Plan.objects.all()
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    return render(request, "billing/home.html", {
        "plans": plans,
        "wallet": wallet,
    })
from django.shortcuts import render, get_object_or_404
from .models import Plan, Wallet, Subscription

def billing_home(request):
    plans = Plan.objects.all()
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    subscription, _ = Subscription.objects.get_or_create(user=request.user)

    return render(request, "billing/home.html", {
        "plans": plans,
        "wallet": wallet,
        "subscription": subscription,
    })


def subscribe_plan(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    subscription, _ = Subscription.objects.get_or_create(user=request.user)

    if wallet.balance >= plan.price:
        wallet.balance -= plan.price
        wallet.save()

        subscription.plan = plan
        subscription.active = True
        subscription.save()

        message = f"🎉 Successfully subscribed to {plan.name} using Wallet balance!"
    else:
        message = "⚠️ Wallet balance insufficient. Pay with Easypaisa."

    return render(request, "billing/subscribe_result.html", {
        "plan": plan,
        "message": message,
        "wallet": wallet
    })
# billing/views.py
def billing_home(request):
    plans = Plan.objects.all()
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    subscription, _ = Subscription.objects.get_or_create(user=request.user)

    return render(request, "billing/home.html", {
        "plans": plans,
        "wallet": wallet,
        "subscription": subscription,
    })
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Wallet

def withdraw_easypaisa(request):
    if request.method == "POST":
        amount = float(request.POST.get("amount"))
        wallet = Wallet.objects.get(user=request.user)

        if wallet.withdraw(amount):
            # yahan EasyPaisa API integrate hogi (dummy for now)
            messages.success(request, f"Withdraw request of Rs.{amount} submitted via EasyPaisa.")
        else:
            messages.error(request, "Insufficient balance.")

        return redirect("wallet")

    wallet = Wallet.objects.get(user=request.user)
    return render(request, "withdraw.html", {"wallet": wallet})
from django.shortcuts import render

# dummy data for testing
class Plan:
    def __init__(self, id, name, price, monthly_quota_captcha):
        self.id = id
        self.name = name
        self.price = price
        self.monthly_quota_captcha = monthly_quota_captcha

def billing_home(request):
    # Example plans
    plans = [
        Plan(1, "Free", 0, 50),
        Plan(2, "Basic", 499, 500),
        Plan(3, "Pro", 999, 1500),
    ]

    # agar user ke pass subscription hai (dummy test ke liye None rakha hai)
    subscription = None  

    return render(request, "billing/billing.html", {
        "plans": plans,
        "subscription": subscription,
    })
from django.shortcuts import render, redirect
from django.contrib import messages

class Plan:
    def __init__(self, id, name, price, monthly_quota_captcha):
        self.id = id
        self.name = name
        self.price = price
        self.monthly_quota_captcha = monthly_quota_captcha

plans = [
    Plan(1, "Free", 0, 50),
    Plan(2, "Basic", 499, 500),
    Plan(3, "Pro", 999, 1500),
]

def billing_home(request):
    """Billing homepage -> show all plans"""
    subscription = None
    return render(request, "billing/billing.html", {
        "plans": plans,
        "subscription": subscription,
    })

def easypaisa_checkout(request, plan_id):
    """Checkout page for specific plan"""
    plan = next((p for p in plans if p.id == plan_id), None)
    if not plan:
        messages.error(request, "Invalid plan selected.")
        return redirect("billing:billing_home")

    if request.method == "POST":
        messages.success(request, f"You subscribed to {plan.name} plan ✅")
        return redirect("billing:billing_home")

    return render(request, "billing/checkout.html", {"plan": plan})


def easypaisa_checkout(request, plan_id):
    plan = next((p for p in plans if p.id == plan_id), None)
    if not plan:
        messages.error(request, "Invalid plan selected.")
        return redirect("billing:billing_home")

    if request.method == "POST":
        # confirm karne ke baad redirect
        messages.success(request, f"You successfully subscribed to {plan.name} ✅")
        return redirect("billing:billing_home")

    # Agar POST nahi hai -> checkout page dikhana
    return render(request, "billing/checkout.html", {"plan": plan})
def easypaisa_checkout(request, plan_id):
    plan = next((p for p in plans if p.id == plan_id), None)
    if not plan:
        messages.error(request, "Invalid plan selected.")
        return redirect("billing:billing_home")

    if request.method == "POST":
        # confirm karne ke baad redirect
        messages.success(request, f"You successfully subscribed to {plan.name} ✅")
        return redirect("billing:billing_home")

    # Agar POST nahi hai -> checkout page dikhana
    return render(request, "billing/checkout.html", {"plan": plan})
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Wallet

@login_required
def wallet_view(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    return render(request, "billing/wallet.html", {"wallet": wallet})


@login_required
def withdraw_request(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)

    if request.method == "POST":
        amount = float(request.POST.get("amount"))
        method = request.POST.get("method")  # Easy Paisa / JazzCash
        number = request.POST.get("number")

        if wallet.withdraw(amount):
            # ✅ Withdraw record save karna chaho to ek model bana sakte ho
            return render(request, "billing/withdraw_success.html", {"amount": amount, "method": method, "number": number})
        else:
            return render(request, "billing/withdraw_failed.html")

    return render(request, "billing/withdraw_form.html", {"wallet": wallet}),
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Plan, Subscription

@login_required
def billing_view(request):
    # Sab plans database se lao
    plans = Plan.objects.all()

    # Current user ka subscription check karo
    subscription = Subscription.objects.filter(user=request.user).first()

    context = {
        "plans": plans,
        "subscription": subscription,
    }
    return render(request, "billing/billing.html", context)
from django.shortcuts import render
from django.http import HttpResponse

def easypaisa_withdraw(request):
    if request.method == "POST":
        # yahan tum apna Easypaisa integration add kar sakti ho
        # for now just success message
        return HttpResponse("✅ Easypaisa Withdraw Successful! Amount Sent.")

    return render(request, "billing/easypaisa_withdraw.html")
from django.shortcuts import render
from django.http import HttpResponse
from .forms import WithdrawForm

def easypaisa_withdraw(request):
    if request.method == "POST":
        form = WithdrawForm(request.POST)
        if form.is_valid():
            # Yahan tum real Easypaisa withdraw ka code add kar sakti ho
            return HttpResponse("✅ Easypaisa Withdraw Successful! Amount Sent.")
    else:
        form = WithdrawForm()

    return render(request, "billing/easypaisa_withdraw.html", {"form": form})

import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages

def easypaisa_withdraw(request):
    if request.method == "POST":
        mobile_number = request.POST.get("mobile_number")
        amount = float(request.POST.get("amount"))

        wallet = Wallet.objects.get(user=request.user)
        if wallet.balance < amount:
            messages.error(request, "Insufficient balance in wallet.")
            return redirect("easypaisa_withdraw")

        # ✅ Real Easypaisa API call
        payload = {
            "storeId": settings.EASYPAY_STORE_ID,
            "amount": str(amount),
            "mobileNum": mobile_number,
            "orderRefNum": "WD" + str(request.user.id),
            "postBackURL": settings.EASYPAY_POSTBACK_URL,
            "expiryDate": "20251231 235959",
            "autoRedirect": "0",
        }

        response = requests.post("https://easypay.easypaisa.com.pk/easypay/transaction/initiate.jsf", data=payload)

        if response.status_code == 200:
            # ✅ Balance minus only if API accepted
            wallet.balance -= amount
            wallet.save()
            messages.success(request, f"✅ Withdraw request sent! {amount} PKR will be transferred to {mobile_number}.")
        else:
            messages.error(request, "❌ Easypaisa API error. Try again later.")

        return redirect("wallet_page")

    return render(request, "billing/easypaisa_withdraw.html")
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import WithdrawRequest

@login_required
def withdraw_request(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)

    if request.method == "POST":
        amount = Decimal(request.POST.get("amount"))
        mobile = request.POST.get("mobile_number")

        if amount > wallet.balance:
            return render(request, "billing/withdraw_form.html", {
                "wallet": wallet,
                "error": "Insufficient balance!"
            })

        # Save withdraw request
        WithdrawRequest.objects.create(
            user=request.user,
            mobile_number=mobile,
            amount=amount,
        )

        # Wallet balance abhi reduce NA karo (jab tak admin approve na kare)
        return redirect("my_wallet")

    return render(request, "billing/withdraw_form.html", {"wallet": wallet})

# billing/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import WithdrawRequestForm
from .models import Wallet, WithdrawRequest

@login_required
def withdraw_request_view(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = WithdrawRequestForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]

            if amount > wallet.balance:
                messages.error(request, "Insufficient balance!")
            else:
                withdraw = form.save(commit=False)
                withdraw.user = request.user
                withdraw.save()

                # balance deduct
                wallet.balance -= amount
                wallet.save()

                messages.success(request, "Withdraw request submitted successfully!")
                return redirect("withdraw_form")
    else:
        form = WithdrawRequestForm()

    return render(request, "billing/withdraw_form.html", {"wallet": wallet, "form": form})
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import WithdrawRequestForm
from .models import Wallet, WithdrawRequest
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def withdraw_view(request):
    ...

@login_required
def withdraw_request_view(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = WithdrawRequestForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]

            # balance check
            if amount > wallet.balance:
                messages.error(request, "Insufficient balance!")
            else:
                withdraw = form.save(commit=False)
                withdraw.user = request.user
                withdraw.save()

                # balance deduct
                wallet.balance -= amount
                wallet.save()

                messages.success(request, "Withdraw request submitted successfully! Admin will review.")
                return redirect("withdraw_request")
    else:
        form = WithdrawRequestForm()

    # show user’s past withdraw requests
    withdraws = WithdrawRequest.objects.filter(user=request.user).order_by("-created_at")

    return render(
        request,
        "billing/withdraw_request.html",
        {"wallet": wallet, "form": form, "withdraws": withdraws},
    )
# captcha_app/views.py  (or billing/views.py)
from decimal import Decimal
import random, string, re
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from billing.easypaisa import send_payout

from billing.models import Wallet, WithdrawRequest


# simple phone validator for Pakistani numbers
PHONE_RE = re.compile(r"^03\d{9}$")

def _make_captcha_code(length=6):
    import string, random
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@login_required
def withdraw_view(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    # ensure captcha in session
    if "captcha_code" not in request.session:
        request.session["captcha_code"] = _make_captcha_code()

    error = None
    success = None

    if request.method == "POST":
        amount = Decimal(request.POST.get("amount", "0") or "0")
        phone = request.POST.get("phone", "").strip()
        captcha_answer = request.POST.get("captcha_answer", "").strip()

        if captcha_answer != request.session.get("captcha_code"):
            error = "Captcha incorrect. Try again."
        elif amount <= 0:
            error = "Invalid amount."
        elif wallet.balance < amount:
            error = "Insufficient balance in wallet."
        elif not PHONE_RE.match(phone):
            error = "Invalid phone number format (example: 03XXXXXXXXX)."
        else:
            # create withdraw request and deduct balance atomically
            with transaction.atomic():
                wallet.withdraw(amount)   # will raise if insufficient
                wr = WithdrawRequest.objects.create(user=request.user, phone=phone, amount=amount, status=WithdrawRequest.STATUS_PROCESSING)

            # call gateway (could be async via Celery — recommended for production)
            success_api, ext_id_or_err, raw = send_payout(phone, amount, request_id=str(wr.id))
            if success_api:
                wr.status = WithdrawRequest.STATUS_COMPLETED
                wr.external_id = ext_id_or_err
                wr.save()
                success = f"Withdraw sent: Rs {amount}. Tx id: {ext_id_or_err}"
            else:
                # refund and mark failed
                with transaction.atomic():
                    wallet.deposit(amount)
                    wr.status = WithdrawRequest.STATUS_FAILED
                    wr.error_message = str(ext_id_or_err)
                    wr.save()
                error = f"Withdraw failed: {ext_id_or_err}"

        # refresh captcha for every attempt
        request.session["captcha_code"] = _make_captcha_code()

    return render(request, "captcha_app/withdraw.html", {
        "wallet": wallet,
        "captcha_code": request.session["captcha_code"],
        "error": error,
        "success": success,
    })
from django.shortcuts import render
from django.http import JsonResponse
from billing.easypaisa import send_easypaisa_payment

def wallet_view(request):
    return render(request, "billing/wallet.html")

def withdraw_view(request):
    return render(request, "billing/withdraw.html")

def easypaisa_payment_view(request):
    if request.method == "POST":
        phone = request.POST.get("phone")
        amount = request.POST.get("amount")
        try:
            result = send_easypaisa_payment(phone, amount)
            return JsonResponse({"status": "success", "data": result})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Invalid request"})
from billing.easypaisa import send_easypaisa_payment

def upgrade_plan(request, plan_id):
    plan = Plan.objects.get(id=plan_id)

    if request.method == "POST":
        phone = request.POST.get("phone")
        result = send_easypaisa_payment(phone, plan.price)

        if result["status"] == "success":
            # deactivate old subscription
            Subscription.objects.filter(user=request.user, active=True).update(active=False)
            # create new subscription
            Subscription.objects.create(user=request.user, plan=plan)

            return JsonResponse({"success": f"Upgraded to {plan.name}"})

    return render(request, "billing/upgrade.html", {"plan": plan})
from django.shortcuts import redirect
from django.contrib import messages
from .models import Subscription, Plan

def activate_free_plan(request):
    if request.method == "POST":
        plan = Plan.objects.filter(name="Free").first()
        if not plan:
            messages.error(request, "Free plan not found.")
            return redirect("wallet")

        # deactivate old subscriptions
        Subscription.objects.filter(user=request.user, active=True).update(active=False)

        # activate new free subscription
        Subscription.objects.create(
            user=request.user,
            plan=plan,
            active=True,
            captchas_used=0
        )

        messages.success(request, "Free plan activated ✅")
        return redirect("wallet")
def activate_free_plan(request):
    if request.method == "POST":
        ...
from django.shortcuts import redirect, render
from django.contrib import messages
from .models import Plan, Subscription

def activate_free_plan(request):
    if request.method == "POST":
        plan = Plan.objects.filter(name="Free").first()
        if not plan:
            messages.error(request, "Free plan is not available yet.")
            return redirect("billing")  # redirect billing page

        # user ki subscription set/update
        Subscription.objects.update_or_create(
            user=request.user,
            defaults={"plan": plan}
        )
        messages.success(request, "🎉 Free plan activated successfully!")
        return redirect("wallet")  # ya jahan tum dikhana chahti ho

    # Agar koi GET request kare (jaise tumne URL bar me dala tha)
    return redirect("billing")  # Safe redirect instead of None
from django.shortcuts import redirect

def activate_free_plan(request):
    # yahan tum free plan activate karne ka logic likh chuki ho
    # jaise user ko 50 free captchas dena etc.
    
    return redirect("billing_home")  # 👈 yahan "billing" ki jagah "billing_home"

from django.shortcuts import render

def billing_home(request):
    return render(request, "billing/billing.html")
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Plan, Subscription

@login_required
def billing_home(request):
    plans = Plan.objects.all()
    subscription = Subscription.objects.filter(user=request.user).first()
    return render(request, "billing/billing_home.html", {
        "plans": plans,
        "subscription": subscription,
    })

@login_required
def activate_free_plan(request):
    if request.method == "POST":
        free_plan = get_object_or_404(Plan, price=0)  # Free plan fetch
        subscription, created = Subscription.objects.get_or_create(
            user=request.user,
            defaults={"plan": free_plan}
        )
        if not created:
            subscription.plan = free_plan
            subscription.save()

        return redirect("billing:billing_home")  # 👈 redirect to billing home

    return redirect("billing:billing_home")
from django.contrib.auth.decorators import login_required

@login_required
def billing_home(request):
    ...
def billing_home(request):
    plans = Plan.objects.all()
    subscription = None
    if request.user.is_authenticated:
        subscription = Subscription.objects.filter(user=request.user).first()
    return render(request, "billing/billing.html", {"plans": plans, "subscription": subscription})
