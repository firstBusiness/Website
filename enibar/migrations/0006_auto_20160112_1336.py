# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-12 12:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enibar', '0005_auto_20151208_1802'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historyline',
            name='foreign_id',
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='note',
            name='foreign_id',
            field=models.IntegerField(db_index=True, unique=True),
        ),
    ]
