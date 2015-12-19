# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('controller', '0002_auto_20150912_2226'),
    ]

    operations = [
        migrations.CreateModel(
            name='Controller',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(default='New controller', max_length=20)),
                ('modules', models.CharField(max_length=1000)),
                ('ws_id', models.PositiveIntegerField()),
                ('online', models.BooleanField(default=False)),
                ('api_key', models.ForeignKey(to='controller.ApiKey')),
            ],
        ),
    ]
