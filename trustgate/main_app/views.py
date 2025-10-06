from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import SignUpForm
from .decorators import paid_required
from .models import Profile

def home(request):
    return render(request, "home.html")

@login_required
def dashboard(request):
    return render(request, "dashboard.html")

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})

@login_required
@paid_required
def prd(request):
    # “Paid Resource/PRD area”
    return render(request, "prd.html")

@login_required
def upgrade(request):
    return render(request, "upgrade.html")

@login_required
def billing_complete(request):
    # demo: mark user Pro (replace with real Stripe later)
    request.user.profile.plan = Profile.PLAN_PRO
    request.user.profile.save()
    messages.success(request, "You're Pro now! Enjoy PRD features.")
    return redirect("prd")


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    return render(request, "home.html")
from django.shortcuts import render, redirect
from django import forms
from captcha.fields import CaptchaField

class CaptchaTestForm(forms.Form):
    captcha = CaptchaField()

def captcha_page(request):
    if request.method == "POST":
        form = CaptchaTestForm(request.POST)
        if form.is_valid():
            return redirect("success")
    else:
        form = CaptchaTestForm()
    return render(request, "captcha_page.html", {"form": form})

def success(request):
    return render(request, "success.html")


from django.shortcuts import render

def home(request):
    return render(request, "home.html")

from django.shortcuts import render

def success_page(request):
    return render(request, "success.html")


from django.shortcuts import render

def success_page(request):
    return render(request, "main_app/success.html")
from django.shortcuts import render

def home(request):
    return render(request, "home.html")












