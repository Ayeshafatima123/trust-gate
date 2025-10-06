from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import stripe
from .models import Plan, Subscription

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.STRIPE_WEBHOOK_SECRET)
    except Exception:
        return HttpResponseBadRequest("Invalid webhook")

    # Minimal: when subscription is created/active, move user to Pro
    if event["type"] in ("checkout.session.completed", "customer.subscription.updated"):
        data = event["data"]["object"]
        sub_id = (data.get("subscription") or data.get("id"))
        customer_id = data.get("customer")
        # You would map customer_id or email back to your user
        # Here we do a simple lookup by stripe_subscription_id
        try:
            sub = Subscription.objects.get(stripe_subscription_id=sub_id)
        except Subscription.DoesNotExist:
            # fallback: if you stored pending plan in session, you can update when user returns
            return HttpResponse("ok")
        pro = Plan.objects.get(code="pro")
        sub.plan = pro
        sub.status = "active"
        sub.save()

    return HttpResponse("ok")
# billing/webhooks.py
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from .models import WithdrawRequest

@csrf_exempt
def easypaisa_webhook(request):
    # 1) verify signature if gateway provides (use settings.EASYPAY_WEBHOOK_SECRET)
    # 2) parse JSON and find external_id or request_id
    import json
    try:
        payload = json.loads(request.body)
    except Exception:
        return HttpResponse(status=400)

    external_id = payload.get("transaction_id") or payload.get("request_id")
    status = payload.get("status")  # depends on gateway: "success" / "failed"
    withdraw = WithdrawRequest.objects.filter(external_id=external_id).first()
    if not withdraw:
        return HttpResponse(status=404)

    if status == "success":
        withdraw.status = WithdrawRequest.STATUS_COMPLETED
        withdraw.save()
    elif status == "failed":
        if withdraw.status != WithdrawRequest.STATUS_FAILED:
            # refund user
            wallet = withdraw.user.wallet
            wallet.deposit(withdraw.amount)
        withdraw.status = WithdrawRequest.STATUS_FAILED
        withdraw.error_message = payload
        withdraw.save()

    return JsonResponse({"ok": True})
