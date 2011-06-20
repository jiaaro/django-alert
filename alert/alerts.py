from .utils import BaseAlert
from .models import AdminAlert
from django.db.models.signals import pre_save

class DjangoAdminAlert(BaseAlert):
    title = 'Admin Alert (created in Django Admin Interface)'
    description = "Send alerts directly to the site's users from the django admin"
    
    signal = pre_save
    sender = AdminAlert
    
    template_filetype = 'html'
    
    # by default all users will receive this alert
    default = True
    
    def before(self, instance, **kwargs):
        if instance.draft:
            # set the draft property false for next time
            instance.draft = False
            return False
        else:
            instance.status = True
    
    def get_applicable_users(self, instance, **kwargs):
        return instance.users.all()

    def get_send_time(self, instance, **kwargs):
        return instance.send_at