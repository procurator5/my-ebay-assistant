# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-01 13:26
from __future__ import unicode_literals

from django.db import migrations, models

import ebay_parse.models


class Migration(migrations.Migration):

    dependencies = [
        ('ebay_parse', '0006_auto_20171031_1648'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebayitem',
            name='ebay_gallery_icon',
            field=models.ImageField(default=ebay_parse.models.load_empty_image, upload_to=''),
        ),
    ]