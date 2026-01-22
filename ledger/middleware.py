
# ledger/middleware.py
from datetime import datetime, timedelta, timezone
from django.shortcuts import redirect
from django.urls import reverse

from Expense_Tracker import settings

class IdleSessionTimeoutMiddleware:
    """
    Logs out the user if there is no activity for IDLE_TIMEOUT minutes.
    We store 'last_activity' in the session and update it on each request.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # default 60 minutes; override with env var if needed
        self.idle_timeout = timedelta(minutes=1)

    def __call__(self, request):
        if request.user.is_authenticated:
            now = datetime.now(timezone.utc)
            last = request.session.get("last_activity")

            # Paths we don't want to trigger redirects (login, logout, keepalive, static, admin login)
            path = request.path
            exempt_paths = {
                reverse("login"),
                reverse("logout"),
                reverse("keepalive"),  # we’ll add this
            }
            # Allow admin login page; avoid redirect loops
            if path.startswith("/admin/login"):
                exempt_paths.add(path)

            try:
                # Update or check idle time
                if last:
                    last_dt = datetime.fromisoformat(last)
                    if now - last_dt > self.idle_timeout and path not in exempt_paths:
                        # Clear the session; redirect to login with a message param if you want
                        for k in ["last_activity"]:
                            request.session.pop(k, None)
                        return redirect(f"{reverse('login')}?next={request.path}")
                # Update activity timestamp on any authenticated request
                request.session["last_activity"] = now.isoformat()
            except Exception:
                # Be defensive: if parsing failed, reset the timestamp
                request.session["last_activity"] = now.isoformat()

        response = self.get_response(request)
        return response