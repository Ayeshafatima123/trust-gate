from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from captcha.fields import CaptchaField
from .models import Profile

class SignUpForm(UserCreationForm):
    plan = forms.ChoiceField(choices=Profile.PLAN_CHOICES)
    captcha = CaptchaField()

    class Meta:
        model = User
        fields = ("username", "password1", "password2", "plan")

    def save(self, commit=True):
        user = super().save(commit=commit)
        # ensure profile exists (signal creates it)
        plan = self.cleaned_data["plan"]
        user.profile.plan = plan
        user.profile.save()
        return user
