from django.http import JsonResponse
from .models import ApiKey, hash_key
from billing.utils import record_usage_or_block

def authenticate_api_key(request):
    key = request.headers.get("X-API-Key") or request.GET.get("api_key")
    if not key:
        return None, JsonResponse({"error":"Missing API key"}, status=401)
    try:
        obj = ApiKey.objects.get(key_hash=hash_key(key))
        return obj.user, None
    except ApiKey.DoesNotExist:
        return None, JsonResponse({"error":"Invalid API key"}, status=401)

def enforce_quota(user):
    msg = record_usage_or_block(user, feature="api")
    if msg:
        return JsonResponse({"error": msg}, status=429)
    return None
# trustgate/api/auth.py
from billing.utils import record_usage_or_block

def enforce_quota(user):
    if not record_usage_or_block(user):
        raise Exception("Quota exceeded! Please upgrade your plan.")
