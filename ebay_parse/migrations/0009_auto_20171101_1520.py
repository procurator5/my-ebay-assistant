# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-01 15:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ebay_parse', '0008_auto_20171101_1517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ebayitem',
            name='ebay_item_postalcode',
            field=models.CharField(max_length=10),
        ),
    ]
