from django.test import TestCase
from django.contrib.auth.models import User
from django.core import management
from django.db.models.signals import post_save
from alert.utils import BaseAlert


class BadgeTests(TestCase):

    def _send_alerts(self):
        management.call_command("send_alerts")
        

    def setUp(self):
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
            
        self.alert = WelcomeAlert
    
    
    def test_alert_creation(self):
        pass
    
    
    def test_alert_registration(self):
        pass
    
    
    def test_badge_registration_only_happens_once(self):
        pass


    def test_alert_sending(self):
        pass
        
        
                
