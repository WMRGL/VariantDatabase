# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-16 14:20
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('patient_initials', models.CharField(max_length=50)),
                ('vcf_file', models.FilePathField(path='/home/cuser/Documents/Project/DatabaseData', recursive=True)),
                ('vcf_hash', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='SampleStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SampleStatusUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Sample')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.SampleStatus')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Variant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chromosome', models.CharField(max_length=25)),
                ('position', models.IntegerField()),
                ('ref', models.TextField()),
                ('alt', models.TextField()),
                ('variant_hash', models.CharField(db_index=True, max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='VariantInformation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('information', models.CharField(max_length=50)),
                ('label', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='VariantSample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Sample')),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Variant')),
            ],
        ),
        migrations.CreateModel(
            name='Worksheet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=' ', max_length=100)),
                ('comment', models.TextField()),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Section')),
            ],
        ),
        migrations.CreateModel(
            name='WorkSheetStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='WorksheetStatusUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('sample', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Worksheet')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.WorkSheetStatus')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='usersetting',
            name='variant_information',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.VariantInformation'),
        ),
        migrations.AddField(
            model_name='sample',
            name='worksheet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Worksheet'),
        ),
    ]
