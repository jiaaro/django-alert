from datetime import datetime
from collections import defaultdict
from django.db.models import Manager
from alert.utils import ALERT_TYPES, ALERT_BACKENDS
from django.contrib.auth.models import User


class AlertManager(Manager): pass


class PendingAlertManager(AlertManager):
    """
    Alerts that are ready to send NOW.
    
    This is not the same as unsent alerts; alerts scheduled to be sent in the
    future will not be affected by this manager.
    """
    
    def get_query_set(self, *args, **kwargs):
        qs = super(PendingAlertManager, self).get_query_set(*args, **kwargs)
        return qs.filter(when__lte=datetime.now(), is_sent=False)
    
    
    
    
class AlertPrefsManager(Manager):
    
    def get_user_prefs(self, user):
        if not user.is_authenticated():
            return dict(((notice_type.id, backend.id), False)
                            for notice_type in ALERT_TYPES.values()
                            for backend in ALERT_BACKENDS.values()
                        )
        
            
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
        
        if not users: return ()
        
        alert_prefs = self.get_query_set().filter(alert_type=notice_type.id).filter(user__in=users)
        
        prefs = {}
        for pref in alert_prefs:
            prefs[pref.user_id, pref.backend] = pref.preference
        
        user_cache = {}
        for user in users:
            user_cache[user.id] = user
            for backend in ALERT_BACKENDS.values():
                if (user.id, backend.id) not in prefs:
                    prefs[user.id, backend.id] = notice_type.get_default(backend.id)
        
        return ((user_cache[user_id], ALERT_BACKENDS[backend_id]) for ((user_id, backend_id), pref) in prefs.items() if pref)
    
