# gimmelikes/middleware.py

from django.middleware.security import SecurityMiddleware
from django.http import HttpResponsePermanentRedirect
import re

class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        
        # Security Headers
        response['X-Frame-Options'] = 'DENY'
        response['X-Content-Type-Options'] = 'nosniff'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://code.jquery.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://stackpath.bootstrapcdn.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "connect-src 'self' https:; "
            "frame-src 'self' https:; "
            "object-src 'none';"
        )
        response['Content-Security-Policy'] = csp
        
        return response

class SSLRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if not request.is_secure() and not request.META.get('HTTP_X_FORWARDED_PROTO', '') == 'https':
            if request.method == 'GET':
                return HttpResponsePermanentRedirect(
                    f'https://{request.get_host()}{request.path}'
                )
        return self.get_response(request)