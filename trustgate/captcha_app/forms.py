from django import forms
from captcha.fields import CaptchaField


class CaptchaForm(forms.Form):
    name = forms.CharField(max_length=100)
    captcha = CaptchaField()

from django import forms
from captcha.fields import CaptchaField

class CaptchaTestForm(forms.Form):
    username = forms.CharField(max_length=100)
    captcha = CaptchaField()
from django import forms
from captcha.fields import CaptchaField

class CaptchaForm(forms.Form):
    email = forms.EmailField(required=True)
    captcha = CaptchaField()
from django import forms
from captcha.fields import CaptchaField

class CaptchaSubmissionForm(forms.Form):
    answer = forms.CharField(
        max_length=255,
        label="Enter answer",
        widget=forms.TextInput(attrs={
            "placeholder": "Enter answer",
            "required": "required",
            "class": "input"
        })
    )
    captcha = CaptchaField()  # yahi image + input render karega
