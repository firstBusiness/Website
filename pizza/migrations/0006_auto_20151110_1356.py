# -*- coding: utf-8 -*-
# Generated by Django 1.9a1 on 2015-11-10 12:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pizza', '0005_pizza_ingredients'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pizza',
            options={'permissions': (('manage_pizza', 'Can manage pizza'),)},
        ),
    ]
