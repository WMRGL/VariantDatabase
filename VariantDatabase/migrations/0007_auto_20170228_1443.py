# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-28 14:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VariantDatabase', '0006_auto_20170228_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batch',
            name='vcf_file',
            field=models.FilePathField(path='/home/cuser/Documents/Project/DatabaseData', recursive=True),
        ),
    ]
