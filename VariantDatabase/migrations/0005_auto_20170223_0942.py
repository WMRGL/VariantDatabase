# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-23 09:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('VariantDatabase', '0004_auto_20170223_0939'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='batch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Batch'),
        ),
    ]
