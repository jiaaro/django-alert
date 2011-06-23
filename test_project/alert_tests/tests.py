import time
from uuid import uuid1
from datetime import datetime, timedelta

from threading import Thread

from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User, Group
from django.core import management, mail
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import post_save

from alert.utils import BaseAlert, ALERT_TYPES, BaseAlertBackend, ALERT_BACKENDS,\
    super_accepter, unsubscribe_user
from alert.exceptions import AlertIDAlreadyInUse, AlertBackendIDAlreadyInUse, CouldNotSendError
from alert.models import Alert, AlertPreference, AdminAlert
from alert.forms import AlertPreferenceForm, UnsubscribeForm
from alert.signals import admin_alert_saved
from alert.admin import AdminAlertAdmin


class SubclassTestingAlert(BaseAlert):
    """
    This will never send any alerts - it's just a check to make sure that
    subclassing alerts doesn't explode
    """
    title = 'Welcome new users'
    description = 'When a new user signs up, send them a welcome email'

    signal = post_save
    sender = User
    
    default = True
    
    def before(self, **kwargs):
        return False
    
    def get_applicable_users(self, instance, **kwargs):
        return [instance]


class WelcomeAlert(SubclassTestingAlert):
    """
    everything is inherited from SubclassTestingAlert
    
    only change is that alerts will actually be sent
    """

    def before(self, created, **kwargs):
        return created


class DummyBackend(BaseAlertBackend):
    title = "Dummy"

    def send(self, alert):
        pass



class EpicFailBackend(BaseAlertBackend):
    """
    Backend that fails to send on the first try for every alert
    """
    id = "EpicFail"
    title = "Epic Fail"

    def send(self, alert):
        if not alert.failed:
            raise CouldNotSendError
        

class SlowBackend(BaseAlertBackend):
    """
    Backend that takes a full second to send an alert
    """
    title = "Slow backend"
    
    def send(self, alert):
        time.sleep(1)
        send_mail("asdf", 'woot', 'fake@gmail.com', ['superfake@gmail.com'])




#################################################
###                 Tests                     ###
#################################################

class AlertTests(TestCase):        

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
        self.assertEquals(len(ALERT_TYPES), 3)
        
        def define_again():
            class WelcomeAlert(BaseAlert):
                title = 'Welcome new users'
                signal = post_save
        
        self.assertRaises(AlertIDAlreadyInUse, define_again)
        
    def test_alert_id_is_key_in_ALERT_TYPES(self):
        for key, alert in ALERT_TYPES.items():
            self.assertEqual(key, alert.id)
        


class AlertBackendTests(TestCase):

    def setUp(self):
        username = str(uuid1().hex)[:16]
        email = "%s@example.com" % username
        
        self.user = User.objects.create(username=username, email=email)
    
    
    def test_backend_creation(self):
        self.assertTrue(isinstance(ALERT_BACKENDS["DummyBackend"], DummyBackend))
        
    
    def test_backends_use_supplied_id(self):
        self.assertTrue(isinstance(ALERT_BACKENDS["EpicFail"], EpicFailBackend))
    
    def test_pending_manager(self):
        self.assertEqual(Alert.pending.all().count(), len(ALERT_BACKENDS))
        management.call_command("send_alerts")
        self.assertEqual(Alert.pending.all().count(), 1)
    
    
    def test_backend_registration_only_happens_once(self):
        self.assertEquals(len(ALERT_BACKENDS), 4)
        
        def define_again():
            class DummyBackend(BaseAlertBackend):
                title = 'dummy'
        
        self.assertRaises(AlertBackendIDAlreadyInUse, define_again)
        
        
    def test_backend_fails_to_send(self):        
        alert_that_should_fail = Alert.objects.filter(backend='EpicFail')[0]
        
        before_send = datetime.now()
        alert_that_should_fail.send()
        after_send = datetime.now()
        
        self.assertTrue(alert_that_should_fail.failed)
        self.assertFalse(alert_that_should_fail.is_sent)
        self.assertTrue(alert_that_should_fail.last_attempt is not None)
        
        self.assertTrue(alert_that_should_fail.last_attempt > before_send)
        self.assertTrue(alert_that_should_fail.last_attempt < after_send)
        
        # and now retry
        before_send = datetime.now()
        alert_that_should_fail.send()
        after_send = datetime.now()
        
        self.assertFalse(alert_that_should_fail.failed)
        self.assertTrue(alert_that_should_fail.is_sent)
        self.assertTrue(alert_that_should_fail.last_attempt is not None)
        
        self.assertTrue(alert_that_should_fail.last_attempt > before_send)
        self.assertTrue(alert_that_should_fail.last_attempt < after_send)

        

class ConcurrencyTests(TransactionTestCase):
    
    def setUp(self):
        username = str(uuid1().hex)[:16]
        email = "%s@example.com" % username
        
        self.user = User.objects.create(username=username, email=email)
        
        
    def testMultipleSimultaneousSendScripts(self):    
        self.assertFalse("sqlite" in settings.DATABASES['default']['ENGINE'],
            """Sqlite uses an in-memory database, which does not work with the concurrency tests.
                Please change the test database to another database (such as MySql).
                
                Note that the alert django app will work fine with Sqlite. It's only the 
                concurrency *tests* that do not work with sqlite.""")
        
        self.assertEqual(len(mail.outbox), 0)
            
        threads = [Thread(target=management.call_command, args=('send_alerts',)) for i in range(100)]
        
        for t in threads:
            t.start()
            
            # space them out a little tiny bit
            time.sleep(0.001)
        
        [t.join() for t in threads]
        
        self.assertEqual(len(mail.outbox), 2)



class EmailBackendTests(TestCase):
    
    def setUp(self):
        pass



class FormTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(username='wootz', email='wootz@woot.com')
    
    
    def testNoArgs(self):
        pref_form = self.assertRaises(TypeError, AlertPreferenceForm)
        unsubscribe_form = self.assertRaises(TypeError, UnsubscribeForm)
        
        
    def testSimpleCase(self):
        pref_form = AlertPreferenceForm(user=self.user)
        unsubscribe_form = UnsubscribeForm(user=self.user)
        
        self.assertEqual(len(pref_form.fields), len(ALERT_TYPES) * len(ALERT_BACKENDS))
        self.assertEqual(len(unsubscribe_form.fields), len(ALERT_TYPES) * len(ALERT_BACKENDS))
        
        
    def testUnsubscribeFormHasNoVisibleFields(self):
        from django.forms import HiddenInput
        unsubscribe_form = UnsubscribeForm(user=self.user)
        
        for field in unsubscribe_form.fields.values():
            self.assertTrue(isinstance(field.widget, HiddenInput))
            
            
    def testSuperAccepterNone(self):
        types = super_accepter(None, ALERT_TYPES)
        backends = super_accepter(None, ALERT_BACKENDS)
        
        self.assertEqual(len(types), len(ALERT_TYPES))
        self.assertEqual(len(backends), len(ALERT_BACKENDS))
        
        
    def testSuperAccepterSingle(self):
        backends_by_class = super_accepter(EpicFailBackend, ALERT_BACKENDS)
        backends_by_id = super_accepter("EpicFail", ALERT_BACKENDS)
        
        self.assertEqual(len(backends_by_class), 1)
        self.assertEqual(len(backends_by_id), 1)
        self.assertEqual(backends_by_class, backends_by_id)
        
        
    def testSuperAccepterList(self):
        backends_by_class = super_accepter([EpicFailBackend, DummyBackend], ALERT_BACKENDS)
        backends_by_id = super_accepter(["EpicFail", "DummyBackend"], ALERT_BACKENDS)
        backends_by_mixed = super_accepter(["EpicFail", DummyBackend], ALERT_BACKENDS)
        
        self.assertEqual(len(backends_by_class), 2)
        self.assertEqual(len(backends_by_id), 2)
        self.assertEqual(len(backends_by_mixed), 2)
        
        self.assertEqual(backends_by_class, backends_by_id)
        self.assertEqual(backends_by_class, backends_by_mixed)
        self.assertEqual(backends_by_mixed, backends_by_id)
        
        
    def testSuperAccepterDuplicates(self):
        backends = super_accepter([EpicFailBackend, DummyBackend, "EpicFail"], ALERT_BACKENDS)
        self.assertEqual(len(backends), 2)
        
    
    def testUnsubscribe(self):
        details = {
            "alert_type": WelcomeAlert.id,
            "backend": EpicFailBackend.id,
            "user": self.user,
        }
        AlertPreference.objects.create(preference=True, **details)
        self.assertEqual(AlertPreference.objects.get(**details).preference, True)
        
        unsubscribe_user(self.user, alerts=WelcomeAlert, backends=EpicFailBackend)
        self.assertEqual(AlertPreference.objects.get(**details).preference, False)
        

class AdminAlertTests(TestCase):
    
    def setUp(self):
        group = Group.objects.create(name='test_group')
        self.admin_alert = AdminAlert(
                                      title="Hello users!",
                                      body="woooord!",
                                      recipients=group
                                      )
        
    def send_it(self):
        AdminAlertAdmin.save_model(AdminAlertAdmin(AdminAlert, None), None, self.admin_alert, None, None)
    
    
    def testDraftMode(self):
        self.admin_alert.draft = True
        self.send_it()
        
        self.assertEqual(Alert.objects.count(), 0)
        
        self.send_it()
        self.assertEqual(Alert.objects.count(), User.objects.count())
    
    
    def testScheduling(self):
        send_at = datetime.now() + timedelta(days=1)
        
        self.admin_alert.send_at = send_at
        self.send_it()

        for alert in Alert.objects.all():
            self.assertEqual(alert.when, send_at)
    
    
    def testOnlySendOnce(self):
        self.assertFalse(self.admin_alert.sent) 
        self.send_it()
        self.assertTrue(self.admin_alert.sent)
        
        alert_count = Alert.objects.count()
        
        self.send_it()
        
        self.assertEqual(alert_count, Alert.objects.count())
    
    
