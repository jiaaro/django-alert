from datetime import datetime
from collections import defaultdict
from django.db.models import Manager
from alert.utils import ALERT_TYPES, ALERT_BACKENDS
from django.contrib.auth.models import User


class AlertManager(Manager): pass


class PendingAlertManager(AlertManager):
    
    def get_queryset(self, *args, **kwargs):
        qs = super(PendingAlertManager, self).get_queryset(*args, **kwargs)
        return qs.filter(is_sent=False, failed=False, when__gte=datetime.now())
    
    
    
    
class AlertPrefsManager(Manager):
    
    def get_user_prefs(self, user):
        alert_prefs = self.get_query_set().filter(user=user)
        
        prefs = {}
        for pref in alert_prefs:
            prefs[pref.alert_type, pref.backend] = pref.preference
        
        for notice_type in ALERT_TYPES.values():
            for backend in ALERT_BACKENDS.values():
                if (notice_type.id, backend.id) not in prefs:
                    default_pref = notice_type.get_default(backend.id)
                    prefs[notice_type.id, backend.id] = default_pref
        return prefs
    
                
    def get_recipients_for_notice(self, notice_type, users):
        if isinstance(notice_type, basestring):
            notice_type = ALERT_TYPES[notice_type]
        
        alert_prefs = self.get_query_set().filter(alert_type=notice_type.id).filter(user__in=users)
        
        prefs = {}
        for pref in alert_prefs:
            prefs[pref.user_id, pref.backend] = pref.preference
        
        for user in users:
            for backend in ALERT_BACKENDS.values():
                if (user.id, backend.id) not in prefs:
                    prefs[user.id, backend.id] = notice_type.get_default(backend.id)
        
        return tuple((User.objects.get(id=user_id), ALERT_BACKENDS[backend_id]) for ((user_id, backend_id), pref) in prefs.items() if pref)
    
