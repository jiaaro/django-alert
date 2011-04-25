from datetime import datetime

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models

from alert.utils import ALERT_TYPE_CHOICES, ALERT_BACKEND_CHOICES, ALERT_TYPES, ALERT_BACKENDS
from alert.managers import AlertManager, PendingAlertManager, AlertPrefsManager
from alert.exceptions import CouldNotSendError
from alert.signals import alert_sent


class Alert(models.Model):
    user = models.ForeignKey(User)
    backend = models.CharField(max_length=20, default='EmailBackend', choices=ALERT_BACKEND_CHOICES)
    alert_type = models.CharField(max_length=25, choices=ALERT_TYPE_CHOICES)
    
    title = models.CharField(max_length=250, default=lambda: "%s alert" % Site.objects.get_current().name)
    body = models.TextField()
    
    when = models.DateTimeField(default=datetime.now)
    created = models.DateTimeField(default=datetime.now)
    last_attempt = models.DateTimeField(blank=True, null=True)
    
    is_sent = models.BooleanField(default=False)
    failed = models.BooleanField(default=False)
    
    objects = AlertManager()
    pending = PendingAlertManager()
    
    
    def send(self):
        backend = Alert._get_backend(self.backend)
        try:
            backend.send(self)
            self.is_sent = True
            self.failed = False
            alert_sent.send(sender=ALERT_TYPES[self.alert_type], alert=self)
            
        except CouldNotSendError:
            self.failed = True
        
        self.last_attempt = datetime.now()
        self.save()
        
        
    @classmethod
    def _get_backend(cls, backend):
        return ALERT_BACKENDS[backend]



class AlertPreference(models.Model):
    user = models.ForeignKey(User)
    alert_type = models.CharField(max_length=25, choices=ALERT_TYPE_CHOICES)
    backend = models.CharField(max_length=25, choices=ALERT_BACKEND_CHOICES)
    
    preference = models.BooleanField()
    
    objects = AlertPrefsManager()
    
    class Meta:
        unique_together = ('user', 'alert_type', 'backend')
   

import alert.backends #@UnusedImport