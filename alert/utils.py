from datetime import datetime
from alert.exceptions import AlertIDAlreadyInUse, AlertBackendIDAlreadyInUse,\
    InvalidApplicableUsers
from django.template.loader import render_to_string, find_template
from django.contrib.sites.models import Site
from django.template import TemplateDoesNotExist
from django.contrib.auth.models import User
from django.db import models

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
        
        # allow subclasses to use the auto id feature
        id = getattr(new_alert, 'id', name)
        for parent in parents:
            if getattr(parent, 'id', None) == id:
                id = name
                break
        
        new_alert.id = id
        
        if new_alert.id in ALERT_TYPES.keys():
            raise AlertIDAlreadyInUse("The alert ID, \"%s\" was delared more than once" % new_alert.id)
        
        ALERT_TYPES[new_alert.id] = new_alert()
        ALERT_TYPE_CHOICES.append((new_alert.id, new_alert.title))
        
        return new_alert



class BaseAlert(object):
    __metaclass__ = AlertMeta
    
    default = False
    sender = None
    template_filetype = "txt"
    
    
    
    def __init__(self):
        kwargs = {}
        if self.sender:
            kwargs['sender'] = self.sender
        
        self.signal.connect(self.signal_handler, **kwargs)
    
    def __repr__(self):
        return "<Alert: %s>" % self.id
    
    def __str__(self):
        return str(self.id)
    
    def signal_handler(self, **kwargs):
    
        if self.before(**kwargs) is False: 
            return

        from alert.models import AlertPreference
        from alert.models import Alert
        
        users = self.get_applicable_users(**kwargs)
        if isinstance(users, models.Model):
            users = [users]
        
        if len(users) and not isinstance(users[0], User):
            raise InvalidApplicableUsers("%s.get_applicable_users() returned an invalid value. Acceptable values are a django.contrib.auth.models.User instance OR an iterable containing 0 or more User instances" % (self.id))
        
        site = Site.objects.get_current()
        
        for user, backend in AlertPreference.objects.get_recipients_for_notice(self.id, users):
            context = self.get_template_context(BACKEND=backend, USER=user, SITE=site, ALERT=self, **kwargs)
            template_kwargs = {'backend': backend, 'context': context } 
            Alert.objects.create(
                                 user=user, 
                                 backend=backend.id,
                                 alert_type=self.id,
                                 when=self.get_send_time(**kwargs),
                                 title=self.get_title(**template_kwargs),
                                 body=self.get_body(**template_kwargs)
                                 )
    
    
    def before(self, **kwargs):
        pass
    
    
    def get_send_time(self, **kwargs):
        return datetime.now()
    
    
    def get_applicable_users(self, instance, **kwargs):
        return [instance.user]
    
    
    def get_template_context(self, **kwargs):
        return kwargs


    def _get_template(self, backend, part, filetype='txt'):
        template = "alerts/%s/%s/%s.%s" % (self.id, backend.id, part, filetype)
        try:
            find_template(template)
            return template
        except TemplateDoesNotExist:
            pass
        
        template = "alerts/%s/%s.%s" % (self.id, part, filetype)
        find_template(template)
        
        return template
        
    
    def get_title_template(self, backend, context):
        return self._get_template(backend, 'title', self.template_filetype)
    
    
    def get_body_template(self, backend, context):
        return self._get_template(backend, 'body', self.template_filetype)
    
    
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
        
        # If this isn't a subclass of BaseAlert, don't do anything special.
        parents = [b for b in bases if isinstance(b, AlertBackendMeta)]
        if not parents: 
            return new_alert_backend
        
        new_alert_backend.id = getattr(new_alert_backend, 'id', name)
        
        if new_alert_backend.id in ALERT_BACKENDS.keys(): 
            raise AlertBackendIDAlreadyInUse("The alert ID, \"%s\" was delared more than once" % new_alert_backend.id)
        
        ALERT_BACKENDS[new_alert_backend.id] = new_alert_backend()
        ALERT_BACKEND_CHOICES.append((new_alert_backend.id, new_alert_backend.title))
        
        return new_alert_backend



class BaseAlertBackend(object):
    __metaclass__ = AlertBackendMeta
    
    def __repr__(self):
        return "<AlertBackend: %s>" % self.id
    
    def __str__(self):
        return str(self.id)
    
    def mass_send(self, alerts):
        from .models import Alert
        if isinstance(alerts, Alert):
            self.send(alerts)
        else:
            [self.send(alert) for alert in alerts]
              
              
def super_accepter(arg, lookup_dict):
    """  
    for the alerts and backends keyword arguments... 
      - provides resonable defaults
      - accept a single alert/backend or a list of them
      - accept alert/backend class or the a string containing the alert/backend id
    """
    # reasonable default
    if arg is None: return lookup_dict.values()
    
    # single item or a list
    if not isinstance(arg, (tuple, list)): 
        arg = [arg]
        
    # normalize the arguments
    ids = ((a if isinstance(a, basestring) else a.id) for a in arg)
    
    # remove duplicates
    _set = {}
    ids = (_set.setdefault(id,id) for id in ids if id not in _set)
    
    # lookup the objects 
    return [lookup_dict[id] for id in ids]


def unsubscribe_user(user, alerts=None, backends=None):
    from .forms import UnsubscribeForm 
    form = UnsubscribeForm(user=user, alerts=alerts, backends=backends)
    
    data = dict((field, False) for field in form.fields.keys())
    
    form = UnsubscribeForm(data, user=user, alerts=alerts, backends=backends)
    assert(form.is_valid())
    form.save()
