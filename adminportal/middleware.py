import base64
from django.utils.crypto import get_random_string

class CSPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        nonce = base64.b64encode(get_random_string(16).encode()).decode()
        request.csp_nonce = nonce
        response = self.get_response(request)
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            f"script-src 'self' 'nonce-{nonce}' https://unpkg.com 'strict-dynamic'; "  # Allow Alpine.js from unpkg
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "img-src 'self' https://demo.bootstrapdash.com/skydash/themes/assets/images/logo-mini.svg https://demo.bootstrapdash.com/skydash/themes/assets/images/logo.svg https://demo.bootstrapdash.com/skydash/themes/assets/images/dashboard/people.svg data:; "
            "connect-src 'self'; "
            "frame-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self';"
        )
        return response