# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-14 12:22
from __future__ import unicode_literals

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ebay_parse', '0015_ebayitem_search_index'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='ebayitem',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search_index'], name='ebay_parse__search__d1bd95_gin'),
        ),
    ]