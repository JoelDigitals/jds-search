import hashlib
import json
from functools import wraps
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from .models import APIKey, APIRateLimit


RATE_LIMIT = 100


def api_auth(require_key=True):
    def decorator(view_func):
        @wraps(view_func)
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            if require_key:
                auth = request.headers.get("Authorization", "")
                if not auth.startswith("Bearer "):
                    return JsonResponse({"error": "API-Key erforderlich. Header: Authorization: Bearer jds_..."}, status=401)

                raw_key = auth[7:]
                key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

                try:
                    api_key = APIKey.objects.get(key_hash=key_hash, is_active=True)
                except APIKey.DoesNotExist:
                    return JsonResponse({"error": "Ungültiger API-Key"}, status=403)

                endpoint = request.path
                rl, _ = APIRateLimit.objects.get_or_create(api_key=api_key, endpoint=endpoint)
                if rl.window_start < timezone.now() - timedelta(hours=1):
                    rl.count = 0
                    rl.window_start = timezone.now()

                if rl.count >= RATE_LIMIT:
                    return JsonResponse({"error": f"Rate-Limit erreicht ({RATE_LIMIT}/Stunde)"}, status=429)

                rl.count += 1
                rl.save()
                api_key.log_use()
                request.api_key = api_key

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


def json_response(data, status=200):
    return JsonResponse(data, status=status, json_dumps_params={"ensure_ascii": False, "indent": 2})
