from django import forms

from alert.models import AlertPreference
from alert.utils import ALERT_TYPES



class AlertPreferenceForm(forms.Form):
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.prefs = AlertPreference.objects.get_user_prefs(user).items()
        
        super(AlertPreferenceForm, self).__init__(*args, **kwargs)
        
        for ((notice_type, backend), pref) in self.prefs:
            attr = self._field_id(notice_type, backend)
            alert = ALERT_TYPES[notice_type]
            self.fields[attr] = forms.BooleanField(
                                                   label=alert.title, 
                                                   help_text=alert.description,
                                                   initial=pref,
                                                   required=False
                                                   )
        
        
    def save(self):
        for (notice_type, backend), pref in self.prefs:
            attr = self._field_id(notice_type, backend)

            alert_pref, created = AlertPreference.objects.get_or_create(
                                            user=self.user,
                                            alert_type=notice_type,
                                            backend=backend
                                            )
            alert_pref.preference = self.cleaned_data[attr]
            alert_pref.save()
            
            
    def _field_id(self, notice_type, backend):
        return "%s__%s" % (notice_type, backend)