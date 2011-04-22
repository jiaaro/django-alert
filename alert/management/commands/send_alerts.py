from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.core.cache import cache
from alert.models import Alert


class Command(BaseCommand):
    help = "Send pending alerts"
    
    _cache_key = 'currently_sending_alerts'
    
    def handle(self, *args, **kwargs):
        if cache.get(self._cache_key, False):
            return
        
        one_day = 60*60*24
        cache.set(self._cache_key, True, one_day)
        
        alerts = Alert.pending.all()
        [alert.send() for alert in alerts]
        
        cache.delete(self._cache_key)
        