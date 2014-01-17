
# Compatibility for Django<1.5
try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
    get_user_model = lambda: User
