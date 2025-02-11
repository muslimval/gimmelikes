from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import SiteConfiguration

@receiver(post_save, sender=SiteConfiguration)
def clear_site_config_cache(sender, instance, **kwargs):
    cache.delete('site_config')