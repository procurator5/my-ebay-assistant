# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-17 08:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ebay_parse', '0014_auto_20171110_1516'),
        ('species', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Scpecies2Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ebay_parse.eBayItem')),
                ('species', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='species.Species')),
            ],
        ),
    ]
