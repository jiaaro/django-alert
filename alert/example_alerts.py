from collections import defaultdict
from datetime import datetime, timedelta
from django.db.models.signals import post_save
from django.contrib.auth.models import User

from alert.utils import BaseAlert

from example_news_app.models import NewsItem



class WelcomeAlert(BaseAlert):
    title = 'Welcome Users'
    description = 'When a user signs up, send them a nice welcome email.'
    
    signal = post_save
    sender = User
    
    # by default all users will receive this alert
    default = True
    
    def before(self, created, **kwargs):
        # if created is false, no alert will be sent
        return created
    
    def get_applicable_users(self, instance, **kwargs):
        return instance



class NewsAlert(BaseAlert):
    title = 'News'
    description = 'Get notified as soon as news updates go out.'
    
    signal = post_save
    sender = NewsItem
    
    # by default users will not receive this alert (i.e. it's opt-in)
    default = False
    
    def before(self, created, **kwargs):
        return created
    
    def get_applicable_users(self, **kwargs):
        # this alert applies to all users (but this queryset will be
        # filtered based on the users' respective alert preferences
        return User.objects.all()



# When a user signs up, one way to keep them engaged is to contact them
# periodically over the next month
#
# The easiest way to do this is to schedule all their emails in advance (we'll
# do 3 in this example:
#
#  - 3 days after signup
#  - 7 days after signup
#  - 30 days after signup 

class MarketingDrip1(BaseAlert):
    """
    first alert in the marketing drip (3 days after signup)
    
    templates...
    
    subject line: 
    "alerts/MarketingDrip1/EmailBackend/title.txt"
    
    body text:
    "alerts/MarketingDrip1/EmailBackend/body.txt"
    
    html version:
    "alerts/MarketingDrip1/EmailBackend/body.html"
    """
    title = "Trickle"
    description = "Send scheduled marketing emails to users once they give their email"
    
    # don't send on any backends except email
    default = defaultdict(lambda: False)
    default['EmailBackend'] = True
    
    signal = post_save
    sender = User
    
    def before(self, created, **kwargs):
        return created
    
    def get_applicable_users(self, instance, **kwargs):
        return instance

    def get_send_time(self, **kwargs):
        return datetime.now + timedelta(days=3)
    


class MarketingDrip2(MarketingDrip1):
    """
    second alert in the marketing drip (7 days after signup)
    
    We subclass MarketingDrip1 to avoid re-writing all that logic
    
    templates...
    
    subject line: 
    "alerts/MarketingDrip2/EmailBackend/title.txt"
    
    body text:
    "alerts/MarketingDrip2/EmailBackend/body.txt"
    
    html version:
    "alerts/MarketingDrip2/EmailBackend/body.html"
    """

    def get_send_time(self, **kwargs):
        return datetime.now + timedelta(days=7)
    

class MarketingDrip3(MarketingDrip1):
    """
    third alert in the marketing drip (30 days after signup)
    
    We could subclass MarketingDrip1 or MarketingDrip2 at this point. I'm
    using MarketingDrip1 to keep things consistent.
    
    templates...
    
    subject line: 
    "alerts/MarketingDrip3/EmailBackend/title.txt"
    
    body text:
    "alerts/MarketingDrip3/EmailBackend/body.txt"
    
    html version:
    "alerts/MarketingDrip4/EmailBackend/body.html"
    """

    def get_send_time(self, **kwargs):
        return datetime.now + timedelta(days=30)

    
    