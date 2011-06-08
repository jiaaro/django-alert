from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from alert.utils import BaseAlertBackend
from alert.exceptions import CouldNotSendError
from django.template.defaultfilters import striptags


class EmailBackend(BaseAlertBackend):
    title = "Email"
    
    def send(self, alert):
        recipient = alert.user.email
        if not recipient: raise CouldNotSendError
        
        subject = alert.title
        to = [recipient]
        from_email = settings.DEFAULT_FROM_EMAIL 
        
        if alert.alert_type_obj.template_filetype == 'html':
            html_content = alert.body
            text_content = striptags(html_content)
            
            msg = EmailMultiAlternatives(subject, text_content, from_email, to)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
        else:
            send_mail(subject, alert.body, from_email, to)
        
        