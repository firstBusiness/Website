# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-21 17:17
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0014_buyinghistory_seller'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buyinghistory',
            name='pack',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.Packs'),
        ),
        migrations.AlterField(
            model_name='buyinghistory',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.Product'),
        ),
        migrations.AlterField(
            model_name='buyinghistory',
            name='seller',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='seller', to=settings.AUTH_USER_MODEL),
        ),
    ]