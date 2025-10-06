# billing/easypaisa.py
import uuid
import requests
from django.conf import settings

EASYPAY_BASE = settings.EASYPAY_BASE_URL
CLIENT_SECRET = settings.EASYPAY_CLIENT_SECRET

def send_payout(phone: str, amount, request_id: str | None = None, timeout=30):
    """
    Make a payout request to gateway.
    Returns (success: bool, external_id_or_error: str, raw_response: dict/str)
    """
    req_id = request_id or str(uuid.uuid4())
    url = f"{EASYPAY_BASE}/payouts"   # <-- replace with real path
    payload = {
        "phone": phone,
        "amount": str(amount),
        "request_id": req_id,
    }
    headers = {
        "Authorization": f"Bearer {CLIENT_SECRET}",  # change according to gateway
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
    except requests.RequestException as e:
        return False, str(e), None

    try:
        data = resp.json()
    except ValueError:
        data = resp.text

    if resp.status_code in (200, 201):
        # assume API returns {"transaction_id": "..."}
        tx = data.get("transaction_id", req_id) if isinstance(data, dict) else req_id
        return True, tx, data
    else:
        # return error message
        err = data.get("error") if isinstance(data, dict) else data
        return False, err, data
def send_easypaisa_payment(phone: str, amount, request_id: str | None = None, timeout=30):
    # purana send_payout wala code yahan paste kar do
    ...
import requests

def send_easypaisa_payment(phone: str, amount: float, request_id: str | None = None, timeout=30):
    """
    Dummy function for Easypaisa API integration.
    Replace with real Easypaisa API call.
    """
    payload = {
        "phone": phone,
        "amount": amount,
        "request_id": request_id or "REQ12345"
    }
    # yahan tum EasyPaisa API call karogi
    # abhi dummy return kar rahe hain
    return {
        "status": "success",
        "message": f"Payment of {amount} sent to {phone}",
        "payload": payload
    }


