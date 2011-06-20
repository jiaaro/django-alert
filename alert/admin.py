from django.contrib import admin
from models import Alert, AlertPreference, AdminAlert



class AlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'backend', 'alert_type', 'failed', 'is_sent', 'created',)
    list_filter = ('alert_type', 'backend', 'is_sent', 'failed')
    search_fields = ('=user__username', '=user__email')
    actions = ['resend']
    
    
    def resend(self, request, qs):
        for alert in qs:
            alert.send()
    resend.short_description = "Resend selected alerts"



class AlertPrefAdmin(admin.ModelAdmin):
    list_display = ("user", 'alert_type', "backend", 'preference')
    list_filter = ('alert_type', 'backend', 'preference')
    search_fields = ('=user__username', '=user__email')
    actions = ['subscribe', 'unsubscribe']
    
    
    def unsubscribe(self, request, qs): 
        qs.update(preference=False)
    unsubscribe.short_description = 'Set selected preferences to "Unsubscribed"'
    
    
    def subscribe(self, request, qs): 
        qs.update(preference=True)
    subscribe.short_description = 'Set selected preferences to "Subscribed"'



class AdminAlertAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "send_at",)
    exclude = ('sent',)
    search_fields = ("title",)
    
    
    def get_readonly_fields(self, request, obj):
        # don't allow editing if it's already sent
        if obj and obj.sent:
            return self.fields
    
    

admin.site.register(Alert, AlertAdmin)
admin.site.register(AlertPreference, AlertPrefAdmin)
admin.site.register(AdminAlert, AdminAlertAdmin)