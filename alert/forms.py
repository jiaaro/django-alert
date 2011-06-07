from django import forms

from alert.models import AlertPreference, Alert
from alert.utils import ALERT_TYPES, ALERT_BACKENDS, BaseAlert, super_accepter



class AlertPreferenceForm(forms.Form):
    """
    Shows a form with a checkbox for each alert/backend combination for
    the user to choose whether or not to receive the alert through that
    backend.
    """
    
    def __init__(self, *args, **kwargs):
        kwargs = kwargs.copy()
        alerts = kwargs.pop('alerts', None)
        backends = kwargs.pop('backends', None)
        
        if 'user' not in kwargs.keys():
            raise TypeError("The \"user\" keyword argument is required but no keyword argument \"user\" was passed")
        
        user = kwargs.pop('user')
                
        self.user = user
        self.alerts = super_accepter(alerts, ALERT_TYPES)
        self.backends = super_accepter(backends, ALERT_BACKENDS)
        self.prefs = AlertPreference.objects.get_user_prefs(user).items()
        
        super(AlertPreferenceForm, self).__init__(*args, **kwargs)
        
        ids = lambda lst: (x.id for x in lst)
        
        for ((alert_type, backend), pref) in self.prefs:
            if (alert_type not in ids(self.alerts) or backend not in ids(self.backends)): 
                continue
            
            attr = self._field_id(alert_type, backend)
            alert = ALERT_TYPES[alert_type]
            self.fields[attr] = forms.BooleanField(
                                                   label=alert.title, 
                                                   help_text=alert.description,
                                                   initial=pref,
                                                   required=False
                                                   )
        
        
    def save(self, *args, **kwargs):
        alert_prefs = []
        for backend in self.backends:
            for alert in self.alerts:
                attr = self._field_id(alert.id, backend.id)
    
                alert_pref, created = AlertPreference.objects.get_or_create(
                                                user=self.user,
                                                alert_type=alert.id,
                                                backend=backend.id
                                                )
                alert_pref.preference = self.cleaned_data[attr]
                alert_pref.save()
                
                alert_prefs.append(alert_pref)
        
        return alert_prefs
            
        
            
            
    def _field_id(self, alert_type, backend):
        return "%s__%s" % (alert_type, backend)
    


class UnsubscribeForm(AlertPreferenceForm):
    """
    This form does not show any check boxes, it expects to be placed into
    the page with only a submit button and some text explaining that by
    clicking the submit button the user will unsubscribe form the Alert
    notifications. (the alert that is passed in)
    """
    
    def __init__(self, *args, **kwargs):
        super(UnsubscribeForm, self).__init__(*args, **kwargs)
        
        for backend in self.backends:
            for alert in self.alerts:
                field_id = self._field_id(alert.id, backend.id)
                self.fields[field_id].widget = forms.HiddenInput()
                self.fields[field_id].initial = False
    
    
    def save(self, *args, **kwargs):
        alert_prefs = super(UnsubscribeForm, self).save(*args, **kwargs)
        affected_alerts = Alert.objects.filter(
                                               is_sent=False,
                                               user=self.user,
                                               backend__in=[backend.id for backend in self.backends],
                                               alert_type__in=[alert.id for alert in self.alerts]
                                               )
        affected_alerts.delete()
        return alert_prefs
        
            
                
            
