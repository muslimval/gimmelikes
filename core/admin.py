from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import SiteConfiguration

@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'maintenance_mode', 'last_updated')
    list_editable = ('maintenance_mode',)
    
    def has_add_permission(self, request):
        # Prevent creating multiple configurations
        return SiteConfiguration.objects.count() == 0

    def has_delete_permission(self, request, obj=None):
        # Prevent deleting the configuration
        return False