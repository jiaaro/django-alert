from collections import defaultdict
from django.db.models import Manager
from django.db.models.query import QuerySet
from django.utils import timezone
from alert.utils import ALERT_TYPES, ALERT_BACKENDS


class AlertManager(Manager):
    pass


class PendingAlertManager(AlertManager):
    """
    Alerts that are ready to send NOW.
    
    This is not the same as unsent alerts; alerts scheduled to be sent in the
    future will not be affected by this manager.
    """
    def get_query_set(self, *args, **kwargs):
        qs = super(PendingAlertManager, self).get_query_set(*args, **kwargs)
        return qs.filter(when__lte=timezone.now(), is_sent=False)
    
    def get_queryset(self, *args, **kwargs):
        qs = super(PendingAlertManager, self).get_queryset(*args, **kwargs)
        return qs.filter(when__lte=timezone.now(), is_sent=False)


class AlertPrefsManager(Manager):
    def get_queryset_compat(self, *args, **kwargs):
        getqs = self.get_queryset if hasattr(Manager, "get_queryset") else self.get_query_set
        return getqs(*args, **kwargs)
    
    def get_user_prefs(self, user):
        if not user.is_authenticated():
            return dict(((notice_type.id, backend.id), False)
                            for notice_type in ALERT_TYPES.values()
                            for backend in ALERT_BACKENDS.values()
                        )
        
            
        alert_prefs = self.get_queryset_compat().filter(user=user)
        
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
        
        # this optimization really shouldn't be necessary, but it makes a huge difference on mysql
        if isinstance(users, QuerySet):
          user_ids = list(users.values_list("id", flat=True))
        else:
          user_ids = [u.id for u in users]
        
        alert_prefs = self.get_queryset_compat().filter(alert_type=notice_type.id).filter(user__in=user_ids)
        
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
    
