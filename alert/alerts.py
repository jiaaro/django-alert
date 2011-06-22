from alert.utils import BaseAlert
from alert.signals import admin_alert_saved

class DjangoAdminAlert(BaseAlert):
    title = 'Admin Alert (created in Django Admin Interface)'
    description = "Send alerts directly to the site's users from the django admin"
    
    signal = admin_alert_saved
    template_filetype = 'html'
    
    # by default all users will receive this alert
    default = True
    
    def get_applicable_users(self, instance, recipients, **kwargs):
        return recipients

    def get_send_time(self, instance, **kwargs):
        return instance.send_at