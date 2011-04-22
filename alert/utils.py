from alert.exceptions import AlertIDAlreadyInUse, AlertBackendIDAlreadyInUse
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

ALERT_TYPES = {}
ALERT_BACKENDS = {}

ALERT_TYPE_CHOICES = [] 
ALERT_BACKEND_CHOICES = []



class AlertMeta(type):

    def __new__(cls, name, bases, attrs):
        new_alert = super(AlertMeta, cls).__new__(cls, name, bases, attrs)
        
        # If this isn't a subclass of BaseAlert, don't do anything special.
        parents = [b for b in bases if isinstance(b, AlertMeta)]
        if not parents: 
            return new_alert
        
        new_alert.id = getattr(new_alert, 'id', name)
        
        if new_alert.id in ALERT_TYPE_CHOICES: 
            raise AlertIDAlreadyInUse("The alert ID, \"%s\" was delared more than once" % new_alert.id)
        
        ALERT_TYPES[new_alert.id] = new_alert()
        ALERT_TYPE_CHOICES.append((new_alert.id, new_alert.title))
        
        return new_alert



class BaseAlert(object):
    __metaclass__ = AlertMeta
    
    default = False
    sender = None
    
    
    def __init__(self):
    	kwargs = {}
    	if self.sender:
    		kwargs['sender'] = self.sender
        
        self.signal.connect(self.signal_handler, **kwargs)
    
    
    def signal_handler(self, **kwargs):
    
		if self.before(**kwargs) is False: 
			return

        from alert.models import AlertPreference
        from alert.models import Alert as AlertModel
        
        users = self.get_applicable_users(**kwargs)
        site = Site.objects.get_current()
        
        for user, backend in AlertPreference.objects.get_recipients_for_notice(self.id, users):
            context = self.get_template_context(BACKEND=backend, USER=user, SITE=site, **kwargs)
            template_kwargs = {'backend': backend, 'context': context } 
            AlertModel.objects.create(
                                            user=user, 
                                            method=backend.id,
                                            title=self.get_title(**template_kwargs),
                                            body=self.get_body(**template_kwargs)
                                            )
    
    
    def before(self, **kwargs):
    	pass
    
    
    def get_applicable_users(self, instance, **kwargs):
        return [instance.user]
    
    
    def get_template_context(self, **kwargs):
        return kwargs
    
    
    def get_title_template(self, backend, context):
        return "alerts/%s/%s/title.txt" % (self.id, backend.id)
    
    
    def get_body_template(self, backend, context):
        return "alerts/%s/%s/body.txt" % (self.id, backend.id)
    
    
    def get_title(self, backend, context):
        template = self.get_title_template(backend, context)
        return render_to_string(template, context)
    
    
    def get_body(self, backend, context):
        template = self.get_body_template(backend, context)
        return render_to_string(template, context)
    
    
    def get_default(self, backend):
        if isinstance(self.default, bool): 
            return self.default
        return self.default[backend]
    
    

class AlertBackendMeta(type):

    def __new__(cls, name, bases, attrs):
        new_alert_backend = super(AlertBackendMeta, cls).__new__(cls, name, bases, attrs)
        new_alert_backend.id = getattr(new_alert_backend, 'id', name)
        
        # If this isn't a subclass of BaseAlert, don't do anything special.
        parents = [b for b in bases if isinstance(b, AlertBackendMeta)]
        if not parents: 
            return new_alert_backend
        
        if new_alert_backend.id in ALERT_BACKEND_CHOICES: 
            raise AlertBackendIDAlreadyInUse("The alert ID, \"%s\" was delared more than once" % new_alert_backend.id)
        
        ALERT_BACKENDS[new_alert_backend.id] = new_alert_backend()
        ALERT_BACKEND_CHOICES.append((new_alert_backend.id, new_alert_backend.title))
        
        return new_alert_backend


class AlertBackend(object):
    __metaclass__ = AlertBackendMeta
    
    