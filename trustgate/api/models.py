from django.db import models
from project.models import Project

class CaptchaLog(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    ok = models.BooleanField(default=False)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
import secrets, hashlib
from django.db import models
from django.contrib.auth.models import User

def hash_key(raw): return hashlib.sha256(raw.encode()).hexdigest()

class ApiKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    prefix = models.CharField(max_length=8)      # showable
    key_hash = models.CharField(max_length=64)   # sha256
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def create_for(user, name="default"):
        raw = "tg_" + secrets.token_urlsafe(24)
        obj = ApiKey.objects.create(
            user=user,
            name=name,
            prefix=raw[:8],
            key_hash=hash_key(raw),
        )
        return obj, raw
# api/models.py
from django.db import models
from django.contrib.auth.models import User

class CaptchaTask(models.Model):
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    reward = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.question

class CaptchaSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(CaptchaTask, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)
    correct = models.BooleanField(default=False)
    reward = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.task.question}"
    
