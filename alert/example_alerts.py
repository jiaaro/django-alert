from alert.utils import BaseAlert
from django.contrib.auth.models import User



class WelcomeAlert(BaseAlert):
    title = 'Welcome Users'
    description = 'When news breaks, be the first to react and profit.'
    
    signal = new_feature
    default = False
    
    def get_applicable_users(self, **kwargs):
        return User.objects.all()


class NewTopic(BaseAlert):
    title = 'New Topic Alert'
    description = 'Get notified as soon as new topics go live.'
    
    signal = market_opened
    default = False
    
    def get_applicable_users(self, **kwargs):
        return User.objects.all()


class CashOut(BaseAlert):
    title = 'Topic cash-out alert'
    description = 'Get notified of your results when a topic is judged.'
    
    signal = market_cashed_out
    default = True
    
    def get_applicable_users(self, cashout_orders, **kwargs):
        profiles = set(order.userprofile for order in cashout_orders)
        return set(prof.user for prof in profiles)
    
    def get_template_context(self, BACKEND, USER, cashout_orders, **kwargs):
        order = [o for o in cashout_orders if o.userprofile.user_id == USER.id]
        locals().update(kwargs)
        return locals()


class TopicClosing(BaseAlert):
    title = 'Closing soon alert'
    description = 'Get notified when topics are closing.'
    
    signal = market_closing_soon
    default = True
    
    def get_applicable_users(self, instance, days_left, **kwargs):
        if days_left != 1:
            return User.objects.none()
        market = instance
        return User.objects.filter(userprofile__order__market=market).distinct()

    
    