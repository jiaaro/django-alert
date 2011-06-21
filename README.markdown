## Installation ##

 1. Install lib with pip:
 
    `pip install django-alert`
   
    **- OR -**

    Put the "alert" directory somewhere in your python path

 2. Add "alert" to your installed apps (in the settings.py file)


## Making Alerts ##

Create an "alerts.py" file and import it at the bottom of your 
models.py file. This is where you will define your alert class. Every 
alert is subclassed from "alert.utils.BaseAlert"

Here is an example alert that is sent to users when they first sign up:

    from alert.utils import BaseAlert
    from django.contrib.auth.models import User

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


## Writing Alert Backends ##

Alert includes an Email Backend by default. But you can write a backend
for *any* messaging medium!

Alert Backends just need to subclass BaseAlertBackend and implement a
`send()` method that accepts an alert instance

You can copy and paste the following code to get started:

    from alert.utils import BaseAlertBackend
    
    class MyAlertBackend(BaseAlertBackend):
        def send()


## Signals ##

When an alert is sent, a signal is fired (found in alert.signals). The 
"sender" keyword argument is the Alert you defined (WelcomeAlert in 
this case).

example:

    from alert.signals import alert_sent

    def do_something_after_welcome_alert_is_sent(sender, alert, **kwargs):
        pass

    alert_sent.connect(do_something_after_welcome_alert_is_sent, 
                          sender=WelcomeAlert)
