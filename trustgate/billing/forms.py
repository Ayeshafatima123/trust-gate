# billing/forms.py
from django import forms
from captcha.fields import CaptchaField

class BillingForm(forms.Form):
    name = forms.CharField(max_length=100)
    captcha = CaptchaField()
from django import forms
from captcha.fields import CaptchaField

class WithdrawForm(forms.Form):
    captcha = CaptchaField()
# billing/forms.py
from django import forms
from .models import WithdrawRequest

class WithdrawRequestForm(forms.ModelForm):
    class Meta:
        model = WithdrawRequest
        fields = ["amount"]  # ✅ sirf valid fields rakho
