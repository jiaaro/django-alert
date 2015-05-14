# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone
import alert.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminAlert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250)),
                ('body', models.TextField()),
                ('send_at', models.DateTimeField(default=django.utils.timezone.now, help_text=b'schedule the sending of this message in the future')),
                ('draft', models.BooleanField(default=False, verbose_name=b"Save as draft (don't send/queue now)")),
                ('sent', models.BooleanField(default=False)),
                ('recipients', models.ForeignKey(to='auth.Group', help_text=b'who should receive this message?', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('backend', models.CharField(default=b'EmailBackend', max_length=20)),
                ('alert_type', models.CharField(max_length=25)),
                ('title', models.CharField(default=alert.models.get_alert_default_title, max_length=250)),
                ('body', models.TextField()),
                ('when', models.DateTimeField(default=django.utils.timezone.now)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_attempt', models.DateTimeField(null=True, blank=True)),
                ('is_sent', models.BooleanField(default=False)),
                ('failed', models.BooleanField(default=False)),
                ('site', models.ForeignKey(default=alert.models.get_alert_default_site, to='sites.Site')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AlertPreference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alert_type', models.CharField(max_length=25)),
                ('backend', models.CharField(max_length=25)),
                ('preference', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='alertpreference',
            unique_together=set([('user', 'alert_type', 'backend')]),
        ),
    ]
