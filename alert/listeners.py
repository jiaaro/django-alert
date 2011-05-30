from django.db.models.signals import post_init, post_save
from alert.models import AlertPreference
from alert.signals import preference_updated
from alert.utils import ALERT_TYPE_CHOICES, ALERT_BACKEND_CHOICES, ALERT_TYPES, ALERT_BACKENDS

def alertpref_post_init(instance, **kwargs):
    instance._current_pref = instance.preference

def alertpref_post_save(instance, **kwargs):
    if instance._current_pref != instance.preference:
        preference_updated.send(
                                sender=instance.alert_type_obj, 
                                user=instance.user, 
                                preference=instance.preference, 
                                instance=instance
                                )

post_init.connect(alertpref_post_init, sender=AlertPreference)
post_save.connect(alertpref_post_save, sender=AlertPreference)




