from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from .models import Project
from billing.models import Subscription
from .models import CaptchaLog
from captcha_app.models import CaptchaTask, CaptchaSubmission

PLAN_LIMITS = {"FREE": 200, "PRO": 10000, "ENTERPRISE": 100000}  # per day

def get_plan(user):
    from billing.models import Subscription
    sub = Subscription.objects.filter(user=user).first()
    return (sub.plan if sub else "FREE")

def today_usage_count(project):
    today = timezone.now().date()
    return CaptchaLog.objects.filter(project=project, created_at__date=today).count()

def within_quota(project):
    plan = get_plan(project.user)
    limit = PLAN_LIMITS.get(plan, 200)
    return today_usage_count(project) < limit

@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])  # no session/csrf
def new_captcha(request):
    """
    GET /api/captcha/new?site_key=PUBLIC_KEY
    -> {hashkey, image_url}
    """
    site_key = request.GET.get("site_key")
    if not site_key:
        return Response({"detail": "site_key required"}, status=400)

    try:
        project = Project.objects.get(site_key=site_key)
    except Project.DoesNotExist:
        return Response({"detail": "invalid site_key"}, status=404)

    if not within_quota(project):
        return Response({"detail": "quota exceeded for your plan"}, status=429)

    hashkey = CaptchaStore.generate_key()
    image_url = captcha_image_url(hashkey)  # needs captcha.urls included
    return Response({"hashkey": hashkey, "image_url": image_url})

@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def verify_captcha(request):
    """
    POST JSON: {secret_key, hashkey, user_response}
    -> {ok: bool}
    Keep secret_key on your server only.
    """
    secret_key = request.data.get("secret_key")
    hashkey = request.data.get("hashkey")
    user_response = request.data.get("user_response")

    if not all([secret_key, hashkey, user_response]):
        return Response({"detail": "secret_key, hashkey, user_response required"}, status=400)

    try:
        project = Project.objects.get(secret_key=secret_key)
    except Project.DoesNotExist:
        return Response({"ok": False, "detail": "invalid secret_key"}, status=403)

    # check quota again for safety
    if not within_quota(project):
        return Response({"ok": False, "detail": "quota exceeded"}, status=429)

    ok = CaptchaStore.objects.filter(hashkey=hashkey, response=user_response).exists()

    # delete store so same captcha can't be reused (recommended)
    CaptchaStore.objects.filter(hashkey=hashkey).delete()

    CaptchaLog.objects.create(
        project=project, ok=ok,
        ip=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT")
    )
    return Response({"ok": bool(ok)})

from django.http import JsonResponse

def hello_api(request):
    return JsonResponse({"message": "TrustGate API working 🚀"})
from django.http import JsonResponse

def api_home(request):
    return JsonResponse({
        "status": "ok",
        "message": "Welcome to TrustGate API 🚀"
    })
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .auth import authenticate_api_key, enforce_quota
from .models import ApiKey

class PingView(View):
    # Public API endpoint: GET /api/ping
    def get(self, request):
        user, err = authenticate_api_key(request)
        if err: return err
        qerr = enforce_quota(user)
        if qerr: return qerr
        return JsonResponse({"ok": True, "message": "pong"})

@method_decorator(login_required, name="dispatch")
class KeysView(View):
    # Simple UI-less JSON for creating keys (you can add an HTML page later)
    def post(self, request):
        obj, raw = ApiKey.create_for(request.user, name="default")
        return JsonResponse({"api_key": raw, "prefix": obj.prefix})

