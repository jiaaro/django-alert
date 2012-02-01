from setuptools import setup

setup(
    name='django-alert',
    version='0.6.6',
    
    author='James Robert',
    author_email='jiaaro@gmail.com',
    
    description=('Send alerts, notifications, and messages based '
                'on events in your django application'),
    long_description=open('README.markdown').read(),
    
    license='MIT',
    keywords='django alerts notifications social',
    
    url='https://djangoalert.com',
    
    install_requires=[
        "django",
    ],
    
    packages=[
        'alert', 
        'alert.management', 
        'alert.management.commands', 
        'alert.migrations',
    ],
    
    include_package_data=True,
    
    
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
