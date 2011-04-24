from django.contrib import admin
from models import Alert, AlertPreference

class AlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'backend', 'title', 'created', 'failed', 'is_sent')

class AlertPrefAdmin(admin.ModelAdmin):
    list_display = ("user", 'alert_type', "backend", 'preference')

admin.site.register(Alert, AlertnAdmin)
admin.site.register(AlertPreference, AlertPrefAdmin)