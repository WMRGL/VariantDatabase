# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-04 13:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VariantDatabase', '0010_auto_20170704_1445'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sample',
            name='insert_size_average',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='sample',
            name='insert_size_standard_deviation',
            field=models.FloatField(null=True),
        ),
    ]