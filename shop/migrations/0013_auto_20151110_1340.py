# -*- coding: utf-8 -*-
# Generated by Django 1.9a1 on 2015-11-10 12:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0012_auto_20151003_1738'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='buyinghistory',
            options={'permissions': (('view_history', 'Can view history'),)},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'permissions': (('sell_product', 'Can sell products'), ('manage_product', 'Can manage products and packs'))},
        ),
    ]
