# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-08 13:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='contributor_only',
            field=models.BooleanField(default=False),
        ),
    ]
