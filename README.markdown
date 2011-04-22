## Installation ##

 1. Install lib with pip:
 
    `pip install django-alert`
   
    **- OR -**

    Put the "alert" directory somewhere in your python path

 2. Add "alert" to your installed apps (in the settings.py file)


## Making Alerts ##

Create an "alerts.py" file and import it at the bottom of your 
models.py file. This is where you will define all your alert classes. Every 
alert is subclassed from "alert.Alert"

Here is an example alert that is sent to users when they first sign up:

    from alert import Alert
    from django.contrib.auth.models import User

    class WelcomeAlert(Alert):
        model = UserProfile
        one_time_only = True

        title = "Autobiographer"
        description = "Completed the User Profile"
        level = "1"

        progress_start = 0
        progress_finish = 2
        
        def get_user(self, instance):
            return instance.user

        def get_progress(self, user):
            has_email = 1 if user.email else 0
            has_bio = 1 if user.get_profile().bio else 0
            return has_email + has_bio
        
        def check_email(self, instance):
            return instance.user.email

        def check_bio(self, instance):
            return instance.bio

The badges are awarded using the post_save signal. So whenever a member of 
the model, in this case "UserProfile," is saved,
it checks to see if the user should be awarded a badge.

In this example, whenever a user profile is saved, the badges app checks 
each of the conditions and if they are 
all True, then the badge is awarded.

The "get_user" method is passed the same instance as the condition checks 
and needs to return the    user who should receive the badge. The default is 
instance.user

The "one_time_only" attribute determines whether a user can earn the badge 
more than once. If a badge was awarded for writing a post that got 1000 
views, you may want to award it for EACH post that gets 1000 views, instead 
of just the first time.
    
Conditions are callback functions. Any methods of your badge class whose 
names start with "check" will be passed an instance of the model instance 
that has just been saved. If all the conditions    return "True," the badge 
will be awarded (unless it's a one-time-only and the user already has it).

### Progress Reporting (optional)

If you would like to display a progress bar to your users, set the 
`progress_start`, and `progress_end`, attributes and define the `get_progress()`
function as seen in the example above.

By default, `progress_start` is 0, and `progress_end` is 1. The default 
`get_progress()` returns 0 if the user has not yet earned the badge
and 1 if they have (so it jumps from 0% to 100% when they earn the badge)

You can get the percent completion of a badge for a given user like so:

    >>> user = User.objects.create(username='tester', email='tester@example.com')
    >>> badge = Badge.objects.get(id='autobiographer')

    >>> badge.meta_badge.get_progress(user)
    ... 1

    >>> badge.meta_badge.get_progress_percentage(user=user)
    ... 50.0

    >>> profile = user.get_profile()
    >>> profile.bio = "hello, world!"
    >>> profile.save()

    >>> badge.meta_badge.get_progress(user)
    ... 2

    >>> badge.meta_badge.get_progress_percentage(user=user)
    ... 100.0

    

### Badge Attributes

There are some badge info attributes which define the information about 
the badge that will be shown on your website:

    
#### id
the unique name that will be used to identify the badge in your 
database. The reason for this is so that you can change the title, 
description, and level without worry


#### title
the Name of the badge as it will appear on the website.


#### description
a short description of the badge as it will appear on 
the website.


#### level
badges are either easy (bronze/b), medium (silver/s), or hard 
(gold/g) to get. It    would not be very hard to change the levels to 
something else like numbers.


#### progress_start (optional | default == 0)
Indicates the value `get_progress()` should return when the user has not made
any progress on this badge.


#### progress_end (optional | default == 1)
Indicates the value `get_progress()` should return when the user has earned
the badge. Note that  if `get_progress()` returns a value larger than progress_end
for a given user, `get_progress_percentage()` will still only return 100.0 (ie. 100%)



## Signals ##

When a badge is awarded, a signal is fired (found in badges.signals). The 
"sender" keyword argument is the metaBadge you defined (Autobiographer in 
this case), and NOT the badge model instance that is automatically created. 
The "user" keyword argument is the user who the badge was awarded to, and 
the "badge" keyword argument is the model instance of the badge in the 
database (badges.models.Badge)

example:

    from badges.signals import badge_awarded

    def do_something_after_badge_is_awarded(sender, user, badge):
        pass

    badge_awarded.connect(do_something_after_badge_is_awarded, 
                          sender=Autobiographer)



## Manually Awarding a Badge ##

You can manually award a badge to a user using the "award_to" method on the
Badge model instance.

Example: Award a random badge to a random user...

    from django.contrib.auth.models import User
    from badges.models import Badge

    random_user = User.objects.order_by("?")[0]
    random_badge = Badges.objects.order_by("?")[0]

    random_badge.award_to(random_user)
