# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-04 10:46
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassificationCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='Consequence',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('impact', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Gene',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=50, unique=True)),
                ('strand', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Interpretation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('finished', models.BooleanField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('classification', models.CharField(max_length=25)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=300)),
                ('description', models.TextField()),
                ('start', models.BooleanField()),
                ('end', models.BooleanField()),
                ('classification', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.ClassificationCode')),
            ],
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('patient_initials', models.CharField(max_length=50)),
                ('vcf_file', models.TextField()),
                ('visible', models.BooleanField()),
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
            name='Transcript',
            fields=[
                ('name', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('canonical', models.BooleanField()),
                ('gene', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Gene')),
            ],
        ),
        migrations.CreateModel(
            name='UserAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('user_answer', models.CharField(default='', max_length=30)),
                ('interpretation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Interpretation')),
                ('user_question', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Question')),
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
                ('variant_hash', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('chromosome', models.CharField(max_length=25)),
                ('position', models.IntegerField()),
                ('ref', models.TextField()),
                ('alt', models.TextField()),
                ('HGVSc', models.TextField()),
                ('HGVSp', models.TextField()),
                ('last_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('rs_number', models.CharField(max_length=50)),
                ('clinical_sig', models.TextField()),
                ('max_af', models.FloatField()),
                ('af', models.FloatField()),
                ('afr_af', models.FloatField()),
                ('amr_af', models.FloatField()),
                ('eur_af', models.FloatField()),
                ('eas_af', models.FloatField()),
                ('sas_af', models.FloatField()),
                ('exac_af', models.FloatField()),
                ('exac_adj_af', models.FloatField()),
                ('exac_afr_af', models.FloatField()),
                ('exac_amr_af', models.FloatField()),
                ('exac_eas_af', models.FloatField()),
                ('exac_fin_af', models.FloatField()),
                ('exac_nfe_af', models.FloatField()),
                ('exac_oth_af', models.FloatField()),
                ('exac_sas_af', models.FloatField()),
                ('esp_ea_af', models.FloatField()),
                ('esp_aa_af', models.FloatField()),
                ('allele_count', models.IntegerField()),
                ('worst_consequence', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Consequence')),
            ],
        ),
        migrations.CreateModel(
            name='VariantGene',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gene', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Gene')),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Variant')),
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
            name='VariantTranscript',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consequence', models.TextField()),
                ('exon', models.CharField(max_length=25)),
                ('intron', models.CharField(max_length=25)),
                ('hgvsc', models.TextField()),
                ('hgvsp', models.TextField()),
                ('transcript', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Transcript')),
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
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.WorkSheetStatus')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('worksheet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Worksheet')),
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
        migrations.AddField(
            model_name='interpretation',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Sample'),
        ),
        migrations.AddField(
            model_name='interpretation',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Variant'),
        ),
    ]
