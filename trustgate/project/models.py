import secrets
from django.db import models
from django.contrib.auth.models import User

def gen_site_key():
    return secrets.token_urlsafe(16)  # public key

def gen_secret_key():
    return secrets.token_urlsafe(32)  # server key, keep private

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    captcha_verified = models.BooleanField(default=False)
    site_key = models.CharField(max_length=64, unique=True, default=gen_site_key)
    secret_key = models.CharField(max_length=128, unique=True, default=gen_secret_key)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

