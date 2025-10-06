from django.shortcuts import render

def home(request):
    return render(request, "home.html")



def captcha_view(request):
    return render(request, "captcha.html")
# trustgate/views.py
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to TrustGate Project — Go to /billing/ for billing or /captcha/ for captcha test.")
# trustgate/views.py
from django.shortcuts import render
from django.http import HttpResponse
from captcha.fields import CaptchaField
from django import forms

# Simple Captcha Form
class CaptchaTestForm(forms.Form):
    captcha = CaptchaField()

def captcha_page(request):
    if request.method == "POST":
        form = CaptchaTestForm(request.POST)
        if form.is_valid():
            return render(request, "success.html")  # success page template
    else:
        form = CaptchaTestForm()
    return render(request, "captcha_page.html", {"form": form})

def success(request):
    return render(request, "success.html")
from django.shortcuts import render

def home(request):
    return render(request, "home.html")

