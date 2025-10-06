from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def paid_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        prof = getattr(request.user, "profile", None)
        if not prof or not prof.is_paid:
            messages.info(request, "Upgrade to Pro to access this page.")
            return redirect("upgrade")
        return view_func(request, *args, **kwargs)
    return _wrapped
