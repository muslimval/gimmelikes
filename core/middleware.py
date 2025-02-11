from django.shortcuts import redirect
from django.urls import reverse
from .models import SiteConfiguration

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        config = SiteConfiguration.objects.first()
        if config and config.maintenance_mode:
            if not request.path == reverse('maintenance'):
                return redirect('maintenance')
        response = self.get_response(request)
        return response