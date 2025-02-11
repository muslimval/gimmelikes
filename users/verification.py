# users/verification.py

from django.core.cache import cache
from django.conf import settings
import requests
import ipapi
from user_agents import parse

class UserVerification:
    def __init__(self, request):
        self.request = request
        self.ip = self.get_client_ip()
        self.user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
        
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return self.request.META.get('REMOTE_ADDR')
    
    def check_vpn(self):
        try:
            response = requests.get(
                f'https://vpnapi.io/api/{self.ip}?key={settings.VPNAPI_KEY}'
            )
            data = response.json()
            return data.get('security', {}).get('vpn', False)
        except:
            return False
    
    def check_location(self):
        try:
            location = ipapi.location(ip=self.ip)
            return location
        except:
            return None
    
    def is_bot(self):
        return self.user_agent.is_bot
    
    def get_device_fingerprint(self):
        return {
            'browser': self.user_agent.browser.family,
            'os': self.user_agent.os.family,
            'device': self.user_agent.device.family,
            'ip': self.ip
        }
    
    def check_rate_limit(self, action, limit=100, period=3600):
        cache_key = f'ratelimit:{self.ip}:{action}'
        
        # Get current count from cache
        count = cache.get(cache_key, 0)
        
        if count >= limit:
            return False
            
        # Increment count
        cache.set(cache_key, count + 1, period)
        return True

class FraudDetection:
    def __init__(self):
        self.suspicious_patterns = {
            'multiple_accounts': [],
            'rapid_points': [],
            'suspicious_ips': set()
        }
    
    def check_multiple_accounts(self, user):
        fingerprint = UserVerification(user.request).get_device_fingerprint()
        
        # Check for multiple accounts from same device/IP
        if fingerprint in self.suspicious_patterns['multiple_accounts']:
            return True
            
        self.suspicious_patterns['multiple_accounts'].append(fingerprint)
        return False
    
    def check_rapid_points_gain(self, user, points_gained, timeframe=3600):
        cache_key = f'points_gained:{user.id}'
        previous_points = cache.get(cache_key, 0)
        
        if points_gained - previous_points > settings.MAX_POINTS_PER_HOUR:
            self.suspicious_patterns['rapid_points'].append(user.id)
            return True
            
        cache.set(cache_key, points_gained, timeframe)
        return False
    
    def mark_suspicious_ip(self, ip):
        self.suspicious_patterns['suspicious_ips'].add(ip)
    
    def is_suspicious(self, user):
        verification = UserVerification(user.request)
        
        # Check if IP is in suspicious list
        if verification.ip in self.suspicious_patterns['suspicious_ips']:
            return True
        
        # Check if using VPN
        if verification.check_vpn():
            self.mark_suspicious_ip(verification.ip)
            return True
        
        # Check for multiple accounts
        if self.check_multiple_accounts(user):
            return True
        
        # Check for suspicious points gain
        if self.check_rapid_points_gain(user, user.profile.points):
            return True
        
        return False

# Initialize fraud detection
fraud_detection = FraudDetection()

```python project="gimmelikes" file="users/signals.py"
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
from .verification import fraud_detection

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        
        # Check for potential fraud
        if fraud_detection.is_suspicious(instance):
            instance.profile.is_suspended = True
            instance.profile.save()

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()