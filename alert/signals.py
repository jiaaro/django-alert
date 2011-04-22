import django.dispatch

alert_sent = django.dispatch.Signal(providing_args=['alert'])