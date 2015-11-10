# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('controller', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controlleruser',
            name='api_keys',
        ),
        migrations.AddField(
            model_name='controlleruser',
            name='api_keys',
            field=models.ManyToManyField(to='controller.ApiKey'),
        ),
    ]
