from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from .models import SiteConfiguration

def get_site_config():
    config = cache.get('site_config')
    if not config:
        config = SiteConfiguration.objects.first()
        cache.set('site_config', config, 3600)  # Cache for 1 hour
    return config

def home(request):
    config = get_site_config()
    context = {
        'site_name': config.site_name,
        'welcome_message': config.welcome_message,
    }
    return render(request, 'core/home.html', context)

@login_required
def dashboard(request):
    user = request.user
    context = {
        'user': user,
        'points': user.profile.points,
        'tasks_completed': user.taskcompletion_set.count(),
    }
    return render(request, 'core/dashboard.html', context)

def maintenance_mode(request):
    config = get_site_config()
    if not config.maintenance_mode:
        return redirect('home')
    return render(request, 'core/maintenance.html')