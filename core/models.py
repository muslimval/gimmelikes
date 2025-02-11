

# Create your models here.
from django.db import models
from django.core.cache import cache

class SiteConfiguration(models.Model):
    site_name = models.CharField(max_length=255, default="GimmeLikes")
    maintenance_mode = models.BooleanField(default=False)
    welcome_message = models.TextField(blank=True)
    footer_text = models.TextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Clear cache when configuration is updated
        cache.clear()

    class Meta:
        verbose_name = "Site Configuration"
        verbose_name_plural = "Site Configuration"

    def __str__(self):
        return self.site_name