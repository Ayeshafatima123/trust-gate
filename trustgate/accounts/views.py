from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages

def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "⚠ Username already exists!")
        else:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect("home")  # 👈 after signup go to home

    return render(request, "accounts/signup.html")
from django.shortcuts import render

def account_dashboard(request):
    return render(request, "accounts/dashboard.html")
# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

def account_dashboard(request):
    return render(request, "accounts/dashboard.html")  # 👈 yehi colorful HTML use hoga

def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("accounts:dashboard")
    else:
        form = UserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("accounts:dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("home")  # 👈 apne home page par redirect hoga
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from billing.models import Wallet

@login_required
def withdraw(request):
    wallet = Wallet.objects.get(user=request.user)
    if request.method == "POST":
        amount = float(request.POST.get("amount", 0))
        if amount > 0 and wallet.balance >= amount:
            wallet.balance -= amount
            wallet.save()
            # TODO: yahan Easypaisa API call karke user ko paisay bhejna hai
            return render(request, "accounts/withdraw_success.html", {"amount": amount})
        else:
            return render(request, "accounts/withdraw.html", {"wallet": wallet, "error": "Invalid amount or insufficient balance."})

    return render(request, "accounts/withdraw.html", {"wallet": wallet})

# accounts/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def my_wallet(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    return render(request, "accounts/wallet.html", {"wallet": wallet})
