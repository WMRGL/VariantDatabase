# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-13 10:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VariantDatabase', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VariantInformation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('displayable_data', models.CharField(max_length=50)),
                ('description', models.TextField()),
            ],
        ),
    ]
