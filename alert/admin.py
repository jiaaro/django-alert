from datetime import datetime
from django.contrib import admin
from django.contrib.auth.models import User
from alert.models import Alert, AlertPreference, AdminAlert
from alert.signals import admin_alert_saved


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
    list_display = ("title", "status", "send_time",)
    search_fields = ("title",)
    
    fieldsets = (
        (None, {
            'fields': ('title', 'body',)
        }),
        ("Recipients", {
#            'classes': ('collapse',),
            'fields': ('recipients',) 
        }),
        ("Advanced", {
            'classes': ('collapse',),
            'fields': ('send_at', 'draft')
        }),
    )
    
    
    def get_readonly_fields(self, request, obj=None):
        # don't allow editing if it's already sent
        if obj and obj.sent:
            return ("title", 'body', 'recipients', 'send_at', 'draft')
        else: 
            return ()
        
        
    def save_model(self, request, obj, form, change):
        is_draft = obj.draft
        if is_draft:
            # set the draft property false for next time
            obj.draft = False
        
        # if it's already been sent then that's it
        obj.sent = obj.sent or not is_draft
        
        obj.save()
        
        # for now, sent to all site users
        recipients = obj.recipients.user_set.all()
        
        if not is_draft:
            admin_alert_saved.send(sender=AdminAlert, instance=obj, recipients=recipients)
        
        
    def status(self, obj):
        if obj.sent:
            return "scheduled" if obj.send_at < datetime.now() else "sent"
        else:
            return "unsent (saved as draft)"
        

    def send_time(self, obj):
        return "-" if not obj.sent else obj.send_at
        
    
    

admin.site.register(Alert, AlertAdmin)
admin.site.register(AlertPreference, AlertPrefAdmin)
admin.site.register(AdminAlert, AdminAlertAdmin)