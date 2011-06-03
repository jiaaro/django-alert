__doc__ = """
Send alerts, notifications, and messages based on events in your django application.

See the README file for details, usage info, and a list of gotchas.
"""

from setuptools import setup

setup(
    name='django-alert',
    version='0.2.2',
    author='James Robert',
    author_email='jiaaro@gmail.com',
    description=('Send alerts, notifications, and messages based '
                'on events in your django application'),
    license='MIT',
    keywords='django alerts notifications social',
    url='https://github.com/jiaaro/django-alert/',
    packages=['alert', 'alert.management', 'alert.management.commands'],
    long_description=__doc__,
    classifiers=[
    	'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Framework :: Django',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Utilities'
    ]
)
