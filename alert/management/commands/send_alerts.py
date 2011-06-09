from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
from alert.models import Alert
from django.contrib.sites.models import Site


class CacheRequiredError(Exception): pass


class Command(BaseCommand):
    help = "Send pending alerts"
    
    _cache_key = 'currently_sending_alerts'
    
    def handle(self, *args, **kwargs):
        cache.set("_dummy_cache_key", True, 60)
        if not cache.get("_dummy_cache_key", False): 
            raise CacheRequiredError
        
        if cache.get(self._cache_key, False):
            return
        
        one_day = 60*60*24
        cache.set(self._cache_key, True, one_day)
        
        alerts = Alert.pending.filter(site=settings.SITE_ID)
        [alert.send() for alert in alerts]
        
        cache.delete(self._cache_key)
        