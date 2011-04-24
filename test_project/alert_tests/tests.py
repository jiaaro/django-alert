from uuid import uuid1

from django.test import TestCase
from django.contrib.auth.models import User
from django.core import management
from django.db.models.signals import post_save

from alert.utils import BaseAlert, ALERT_TYPES, BaseAlertBackend, ALERT_BACKENDS
from alert.exceptions import AlertIDAlreadyInUse, AlertBackendIDAlreadyInUse
from alert.models import Alert



class WelcomeAlert(BaseAlert):
    title = 'Welcome new users'
    description = 'When a new user signs up, send them a welcome email'

    signal = post_save
    sender = User
    
    default = False

    def before(self, created, **kwargs):
        return created


    def get_applicable_users(self, instance, **kwargs):
        return [instance]



class DummyBackend(BaseAlertBackend):
    title = "Dummy"



class AlertTests(TestCase):

    def _send_alerts(self):
        management.call_command("send_alerts")
        

    def setUp(self):
        pass
    
    
    def test_alert_creation(self):
        username = str(uuid1().hex)[:16]
        email = "%s@example.com" % username
        
        user = User.objects.create(username=username, email=email)
        
        alerts = Alert.objects.filter(user=user)
        self.assertEqual(len(alerts), len(ALERT_BACKENDS))
        for alert in alerts:
            self.assertEqual(alert.alert_type, "WelcomeAlert")
            if alert.backend == 'EmailBackend':
                self.assertEqual(alert.title, "email subject")
                self.assertEqual(alert.body, "email body")
            else:
                self.assertEqual(alert.title, "default title")
                self.assertEqual(alert.body, "default body")
        
    
    
    def test_alert_registration_only_happens_once(self):
        self.assertTrue(isinstance(ALERT_TYPES["WelcomeAlert"], WelcomeAlert))
        self.assertEquals(len(ALERT_TYPES), 1)
        
        def define_again():
            class WelcomeAlert(BaseAlert):
                title = 'Welcome new users'
                signal = post_save
        
        self.assertRaises(AlertIDAlreadyInUse, define_again)


    def test_alert_sending(self):
        pass
        
        
               
class AlertBackendTests(TestCase):

    def setUp(self):
        pass
    
    
    def test_backend_creation(self):
        self.assertTrue(isinstance(ALERT_BACKENDS["DummyBackend"], DummyBackend))
    
    
    def test_backent_registration_only_happens_once(self):
        self.assertEquals(len(ALERT_BACKENDS), 2)
        
        def define_again():
            class DummyBackend(BaseAlertBackend):
                title = 'dummy'
        
        self.assertRaises(AlertBackendIDAlreadyInUse, define_again)
