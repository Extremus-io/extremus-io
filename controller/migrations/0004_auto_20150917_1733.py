# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('controller', '0003_controller'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controller',
            name='ws_id',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
