# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-23 09:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('VariantDatabase', '0003_auto_20170222_1512'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='samplebatch',
            name='batch',
        ),
        migrations.RemoveField(
            model_name='samplebatch',
            name='sample',
        ),
        migrations.AddField(
            model_name='sample',
            name='batch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Batch'),
        ),
        migrations.DeleteModel(
            name='SampleBatch',
        ),
    ]
