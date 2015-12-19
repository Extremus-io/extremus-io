# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pubsub', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubIdentifier',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('module', models.CharField(max_length=40, verbose_name='Module location')),
                ('cls_name', models.CharField(max_length=40, verbose_name='Class name')),
                ('identifier', models.CharField(max_length=50, verbose_name='Identity in that class')),
            ],
        ),
        migrations.RenameField(
            model_name='room',
            old_name='sockets',
            new_name='str_ids',
        ),
        migrations.AlterField(
            model_name='room',
            name='name',
            field=models.CharField(unique=True, max_length=30),
        ),
    ]
