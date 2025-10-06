from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CaptchaTask, CaptchaSubmission
from billing.models import Wallet

@login_required
def solve_captcha(request, task_id):
    task = get_object_or_404(CaptchaTask, id=task_id)
    submission = None

    if request.method == "POST":
        answer = request.POST.get("answer", "").strip()
        is_correct = (answer.lower() == task.answer.lower())

        reward_amount = task.reward if is_correct else 0

        # Save submission
        submission = CaptchaSubmission.objects.create(
            user=request.user,
            task=task,
            answer=answer,
            correct=is_correct,
            reward=reward_amount
        )

        # Agar sahi hai → Wallet update
        if is_correct:
            wallet, _ = Wallet.objects.get_or_create(user=request.user)
            wallet.balance += reward_amount
            wallet.save()

    return render(request, "captcha_app/solve.html", {
        "task": task,
        "submission": submission
    })
from django.shortcuts import render
import random, string

def _make_captcha(length=6):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))

def captcha_view(request):
    if request.method == "POST":
        user_value = request.POST.get("captcha_input", "").strip().upper()
        expected = request.session.get("captcha_text", "")

        if user_value and expected and user_value == expected:
            request.session.pop("captcha_text", None)
            return render(request, "captcha_app/success.html")

        captcha_text = _make_captcha()
        request.session["captcha_text"] = captcha_text
        return render(request, "captcha_app/captcha.html", {
            "captcha_text": captcha_text,
            "error": "Wrong captcha. Try again."
        })

    captcha_text = _make_captcha()
    request.session["captcha_text"] = captcha_text
    return render(request, "captcha_app/captcha.html", {"captcha_text": captcha_text})

# captcha_app/views.py
from django.shortcuts import render

def home(request):
    return render(request, "captcha_app/home.html")
from django.shortcuts import render

def success_view(request):
    return render(request, "captcha_app/success.html")


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Wallet

@login_required
def captcha_view(request):
    if request.method == "POST":
        user_input = request.POST.get("captcha_input", "").strip().upper()
        expected = request.session.get("captcha_text", "")

        if user_input == expected:
            # ✅ User ka wallet load karo
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            wallet.balance += 5   # har captcha solve pe 5 Rs add hoga
            wallet.save()

            return redirect("captcha_app:success")

        return render(request, "captcha_app/captcha_test.html", {"error": "Wrong captcha!"})

    return render(request, "captcha_app/captcha_test.html")
@login_required
def withdraw_view(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)

    if request.method == "POST":
        amount = float(request.POST.get("amount", 0))
        if amount > 0 and wallet.balance >= amount:
            wallet.balance -= amount
            wallet.save()
            # 🚀 Yahan EasyPaisa/JazzCash API connect karna hoga
            return render(request, "captcha_app/withdraw_success.html", {"amount": amount})

        return render(request, "captcha_app/withdraw.html", {"wallet": wallet, "error": "Insufficient balance!"})

    return render(request, "captcha_app/withdraw.html", {"wallet": wallet})
from django.shortcuts import render, get_object_or_404
from .models import CaptchaTask  # ya jo bhi aapka model hai

def solve_captcha(request, captcha_id):
    captcha = get_object_or_404(CaptchaTask, id=captcha_id)

    if request.method == "POST":
        user_answer = request.POST.get("answer", "").strip().lower()
        if user_answer == captcha.answer.lower():
            return render(request, "captcha_app/success.html", {"captcha": captcha})
        else:
            return render(
                request,
                "captcha_app/solve.html",
                {"captcha": captcha, "error": "Wrong answer, try again!"}
            )

    return render(request, "captcha_app/solve.html", {"captcha": captcha})

import random
import string
from django.shortcuts import render

def captcha_view(request):
    # Agar pehli dafa open kare to naya captcha generate hoga
    if "captcha_code" not in request.session:
        request.session["captcha_code"] = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )

    error = None
    success = None

    if request.method == "POST":
        user_answer = request.POST.get("answer", "").strip()
        if user_answer == request.session.get("captcha_code"):
            success = "Easypaisa Withdraw Successful! Amount Sent."
            # Naya captcha generate karo next attempt ke liye
            request.session["captcha_code"] = ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=6)
            )
        else:
            error = "Captcha Incorrect! Try again."
            # Naya captcha bhi generate ho
            request.session["captcha_code"] = ''.join(
                random.choices(string.ascii_uppercase + string.digits, k=6)
            )

    return render(request, "captcha_app/captcha_test.html", {
        "captcha_code": request.session["captcha_code"],
        "error": error,
        "success": success,
    })
import random
import string
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Wallet

@login_required
def withdraw_view(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)

    # agar captcha session me nahi hai to bana lo
    if "captcha_code" not in request.session:
        request.session["captcha_code"] = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )

    error = None
    success = None

    if request.method == "POST":
        amount = int(request.POST.get("amount", 0))
        easypaisa_number = request.POST.get("easypaisa_number", "").strip()
        captcha_answer = request.POST.get("captcha_answer", "").strip()

        if captcha_answer != request.session.get("captcha_code"):
            error = "Captcha Incorrect! Try again."
        elif amount <= 0:
            error = "Invalid amount!"
        elif wallet.balance < amount:
            error = "Insufficient Balance!"
        elif not easypaisa_number.startswith("03") or len(easypaisa_number) != 11:
            error = "Invalid Easypaisa number!"
        else:
            wallet.balance -= amount
            wallet.save()
            success = f"✅ Withdraw Successful! Rs {amount} sent to Easypaisa {easypaisa_number}"

        # har attempt ke baad captcha refresh
        request.session["captcha_code"] = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )

    return render(request, "billing/withdraw.html", {
        "wallet": wallet,
        "captcha_code": request.session["captcha_code"],
        "error": error,
        "success": success,
    })

import random, string
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Wallet

@login_required
def withdraw_view(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)

    # Captcha generate agar pehle se session me na ho
    if "captcha_code" not in request.session:
        request.session["captcha_code"] = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )

    error, success = None, None

    if request.method == "POST":
        amount = int(request.POST.get("amount", 0))
        easypaisa_number = request.POST.get("easypaisa_number", "").strip()
        captcha_answer = request.POST.get("captcha_answer", "").strip()

        if captcha_answer != request.session.get("captcha_code"):
            error = "❌ Captcha galat hai!"
        elif amount <= 0:
            error = "❌ Invalid amount!"
        elif wallet.balance < amount:
            error = "❌ Balance kam hai!"
        elif not easypaisa_number.startswith("03") or len(easypaisa_number) != 11:
            error = "❌ Easypaisa number sahi nahi hai!"
        else:
            wallet.balance -= amount
            wallet.save()
            success = f"✅ Rs {amount} sent to Easypaisa {easypaisa_number}"

        # Har POST ke baad captcha refresh karo
        request.session["captcha_code"] = ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )

    return render(request, "captcha_app/withdraw.html", {
        "wallet": wallet,
        "captcha_code": request.session["captcha_code"],
        "error": error,
        "success": success,
    })

from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, "captcha_app/home.html")

def captcha_page(request):
    return render(request, "captcha_app/captcha_test.html")

def success(request):
    return render(request, "captcha_app/success.html")

def withdraw(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        easypaisa_number = request.POST.get("easypaisa_number")

        # ⚡ Yahan tum apna withdraw logic lagao (DB save, API call, etc.)
        # Filhal sirf success message dikhayenge
        msg = f"Withdraw request of Rs.{amount} to {easypaisa_number} submitted!"
        return HttpResponse(msg)

    return render(request, "captcha_app/withdraw.html")
from billing.models import Wallet
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import CaptchaTask, CaptchaSubmission

@login_required
def captcha_test(request):
    if request.method == "POST":
        task_id = request.POST.get("task_id")
        user_answer = request.POST.get("answer")
        task = CaptchaTask.objects.get(id=task_id)

        # Save submission
        submission = CaptchaSubmission.objects.create(
            task=task,
            user_answer=user_answer,
        )

        # Check answer
        if user_answer.strip().lower() == task.answer.lower():
            # ✅ User ka wallet balance update
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            wallet.deposit(task.reward)

            return redirect("billing:wallet")  # Billing page pe bhej do
        else:
            return render(request, "captcha/failed.html")

    task = CaptchaTask.objects.order_by("?").first()
    return render(request, "captcha/test.html", {"task": task})

import random
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from billing.models import Wallet
from billing.easypaisa import send_easypaisa_payment

@login_required
def captcha_withdraw(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    captcha_code = str(random.randint(1000, 9999))

    if request.method == "POST":
        captcha_answer = request.POST.get("captcha_answer")
        easypaisa_number = request.POST.get("easypaisa_number")
        amount = int(request.POST.get("amount", 0))

        # Captcha check
        if captcha_answer != request.session.get("captcha_code"):
            return render(request, "captcha_app/captcha_withdraw.html", {
                "wallet": wallet,
                "captcha_code": captcha_code,
                "error": "❌ Captcha galat hai!"
            })

        # Balance check
        if amount > wallet.balance:
            return render(request, "captcha_app/captcha_withdraw.html", {
                "wallet": wallet,
                "captcha_code": captcha_code,
                "error": "❌ Wallet me itna paisa nahi hai!"
            })

        # Call Easypaisa API
        success, message = send_easypaisa_payment(easypaisa_number, amount)

        if success:
            wallet.balance -= amount
            wallet.save()
            return render(request, "captcha_app/captcha_withdraw.html", {
                "wallet": wallet,
                "captcha_code": captcha_code,
                "success": f"✅ Rs.{amount} sent! {message}"
            })
        else:
            return render(request, "captcha_app/captcha_withdraw.html", {
                "wallet": wallet,
                "captcha_code": captcha_code,
                "error": f"❌ Withdraw failed: {message}"
            })

    request.session["captcha_code"] = captcha_code
    return render(request, "captcha_app/captcha_withdraw.html", {
        "wallet": wallet,
        "captcha_code": captcha_code
    })
from django.contrib import messages   # ✅ yeh import zaroori hai


def solve_captcha(request, captcha_id):
    captcha = get_object_or_404(CaptchaTask, id=captcha_id)
    if request.method == "POST":
        answer = request.POST.get("captcha")
        if answer == captcha.answer:
            # ✅ reward add to wallet
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            wallet.balance += captcha.reward  # reward from task
            wallet.save()

            messages.success(request, f"Correct! {captcha.reward} PKR added to your wallet.")
            return redirect("wallet_page")
        else:
            messages.error(request, "Wrong captcha!")
    return render(request, "captcha_app/solve_captcha.html", {"captcha": captcha})


    # captcha_app/views.py (example)
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CaptchaTask, CaptchaSubmission


@login_required
def solve_captcha(request, task_id):
    task = CaptchaTask.objects.get(id=task_id)

    if request.method == "POST":
        answer = request.POST.get("answer")
        if answer.strip().lower() == task.answer.lower():
            submission = CaptchaSubmission.objects.create(
                task=task,
                user=request.user,
                user_answer=answer,
                correct=True,
                reward=task.reward
            )
            # ✅ Add reward to wallet
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            wallet.balance += task.reward
            wallet.save()
            return render(request, "captcha/success.html", {"reward": task.reward, "balance": wallet.balance})
        else:
            return render(request, "captcha/fail.html", {"task": task})

    return render(request, "captcha/captcha_test.html", {"task": task})

@login_required
def solve_captcha(request, captcha_id):
    # yahan captcha_id use karke DB se captcha fetch karo
    captcha = get_object_or_404(CaptchaTask, id=captcha_id)

    if request.method == "POST":
        # captcha solve logic yahan
        ...
    
    return render(request, "captcha_app/solve.html", {"captcha": captcha})

@login_required
def solve_captcha(request, captcha_id):
    captcha = get_object_or_404(CaptchaTask, id=captcha_id)

    if request.method == "POST":
        user_answer = request.POST.get("answer")
        if user_answer == captcha.answer:
            # User ka balance add karo
            profile = request.user.profile  # मान लो tumhare UserProfile me balance hai
            profile.balance += captcha.reward
            profile.save()

            # Agla captcha laao
            next_captcha = CaptchaTask.objects.order_by("?").first()
            return redirect("solve_captcha", captcha_id=next_captcha.id)

    return render(request, "captcha_app/solve.html", {"captcha": captcha})

from billing.models import Subscription
from django.http import JsonResponse


def solve_captcha(request, task_id):
    sub = Subscription.objects.filter(user=request.user, active=True).first()
    if not sub:
        return JsonResponse({"error": "No active subscription"})

    if sub.captchas_used >= sub.plan.captcha_limit:
        return JsonResponse({"error": "Captcha limit reached, please upgrade your plan"})

    # captcha solve logic...
    sub.captchas_used += 1
    sub.save()

    return JsonResponse({"success": "Captcha solved", "remaining": sub.remaining_captchas()})
