import django.dispatch

alert_sent = django.dispatch.Signal(providing_args=['alert'])
preference_updated = django.dispatch.Signal(providing_args=['user', 'preference', 'instance'])