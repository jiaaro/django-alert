from django import forms

from alert.models import AlertPreference, Alert
from alert.utils import ALERT_TYPES, ALERT_BACKENDS, BaseAlert



class AlertPreferenceForm(forms.Form):
    """
    Shows a form with a checkbox for each alert/backend combination for
    the user to choose whether or not to receive the alert through that
    backend.
    """
    
    def __init__(self, user, alerts=None, backends=None, *args, **kwargs):
        self.user = user
        
        if alerts is None: 
            alerts = ALERT_TYPES.values()
        if backends is None: 
            backends = ALERT_BACKENDS.values()
            
        self.alerts = alerts
        self.backends = backends
        
        self.prefs = AlertPreference.objects.get_user_prefs(user).items()
        
        super(AlertPreferenceForm, self).__init__(*args, **kwargs)
        
        for ((alert_type, backend), pref) in self.prefs:
            if (alert_type not in [a.id for a in self.alerts] or backend not in [b.id for b in self.backends]): 
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
    
    def __init__(self, user, *args, **kwargs):
        super(UnsubscribeForm, self).__init__(user, *args, **kwargs)
        
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
        
            
                
            
