import re

from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from alert.utils import BaseAlertBackend
from alert.exceptions import CouldNotSendError
from django.template.defaultfilters import striptags

strip_head = re.compile(r"<head.*?</head>", re.DOTALL)
strip_style = re.compile(r"<style.*?</style>", re.DOTALL)
strip_script = re.compile(r"<script.*?</script>", re.DOTALL)
gt_2_lines_whitespace = re.compile(r"\s*\n\s*\n\s*", re.DOTALL)
multiple_spaces = re.compile(r"[\f\v\t ]+", re.DOTALL)

link1 = re.compile(r"(<a.*?href=\"([^\"]*)\".*?</a>)", re.I)
link2 = re.compile(r"(<a.*?href='([^']*)'.*?</a>)", re.I)
link_replace = lambda m: "%s (%s)" % m.groups()

def to_text(html_content):
    html_content = strip_style.sub("", html_content)
    html_content = strip_script.sub("", html_content)
    html_content = strip_head.sub("", html_content)
    
    html_content = link1.sub(link_replace, html_content)
    html_content = link2.sub(link_replace, html_content)
    
    html_content = striptags(html_content)
    
    # max out at 2 empty lines
    html_content = gt_2_lines_whitespace.sub("\n\n", html_content)
    html_content = multiple_spaces.sub(" ", html_content)
    
    return html_content


class EmailBackend(BaseAlertBackend):
    title = "Email"
    
    def send(self, alert):
        recipient = alert.user.email
        if not recipient: raise CouldNotSendError
        
        subject = alert.title.replace("\n", "").strip()
        to = [recipient]
        from_email = settings.DEFAULT_FROM_EMAIL 
        
        if alert.alert_type_obj.template_filetype == 'html':
            html_content = alert.body
            text_content = to_text(html_content)
            
            msg = EmailMultiAlternatives(subject, text_content, from_email, to)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
        else:
            send_mail(subject, alert.body, from_email, to)
        
        