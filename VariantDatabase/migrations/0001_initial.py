# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-27 08:15
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
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('time', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
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
            name='Evidence',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, null=True, upload_to='uploads/%y/%m/')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Comment')),
            ],
        ),
        migrations.CreateModel(
            name='EvidenceType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('evidence_type', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ExonCoverage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exon', models.CharField(max_length=20)),
                ('x100', models.IntegerField()),
                ('x200', models.IntegerField()),
                ('x300', models.IntegerField()),
                ('x400', models.IntegerField()),
                ('x500', models.IntegerField()),
                ('x600', models.IntegerField()),
                ('min_coverage', models.IntegerField()),
                ('max_coverage', models.IntegerField()),
                ('mean_coverage', models.FloatField()),
                ('number_of_regions', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Gene',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='GeneCoverage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x100', models.IntegerField()),
                ('x200', models.IntegerField()),
                ('x300', models.IntegerField()),
                ('x400', models.IntegerField()),
                ('x500', models.IntegerField()),
                ('x600', models.IntegerField()),
                ('min_coverage', models.IntegerField()),
                ('max_coverage', models.IntegerField()),
                ('mean_coverage', models.FloatField()),
                ('number_of_regions', models.IntegerField()),
                ('gene', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Gene')),
            ],
        ),
        migrations.CreateModel(
            name='ReadLaneQuality',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('read', models.IntegerField()),
                ('lane', models.IntegerField()),
                ('yield_g', models.FloatField()),
                ('density', models.FloatField()),
                ('cluster_count_pf', models.FloatField()),
                ('cluster_count', models.FloatField()),
                ('phasing', models.FloatField()),
                ('prephasing', models.FloatField()),
                ('read_count', models.FloatField()),
                ('reads_pf', models.FloatField()),
                ('percent_gt_q30', models.FloatField(null=True)),
                ('percent_aligned', models.FloatField(null=True)),
                ('error_rate', models.FloatField(null=True)),
                ('error_rate_35', models.FloatField(null=True)),
                ('error_rate_50', models.FloatField(null=True)),
                ('error_rate_75', models.FloatField(null=True)),
                ('error_rate_100', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('1', 'New Report'), ('2', 'Awaiting 1st Check'), ('3', 'Awaiting 2nd Check'), ('4', 'Complete')], max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='ReportVariant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('1', 'None'), ('2', 'Pathogenic'), ('3', 'Benign'), ('4', 'VUS')], max_length=1)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Report')),
            ],
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('vcf_file', models.TextField(blank=True, null=True)),
                ('bam_file_pindel', models.TextField(blank=True, null=True)),
                ('bam_file_bwa', models.TextField(blank=True, null=True)),
                ('visible', models.BooleanField()),
                ('status', models.CharField(choices=[('1', 'New Sample'), ('2', 'Awaiting 1st Check'), ('3', 'Awaiting 2nd Check'), ('4', 'Complete')], max_length=1)),
                ('sample_well', models.CharField(max_length=10)),
                ('i7_index_id', models.IntegerField()),
                ('index', models.CharField(max_length=50)),
                ('sample_project', models.CharField(blank=True, max_length=50, null=True)),
                ('raw_total_sequences', models.IntegerField(blank=True, null=True)),
                ('filtered_sequences', models.IntegerField(blank=True, null=True)),
                ('sequences', models.IntegerField(blank=True, null=True)),
                ('first_fragments', models.IntegerField(blank=True, null=True)),
                ('last_fragments', models.IntegerField(blank=True, null=True)),
                ('reads_mapped', models.IntegerField(blank=True, null=True)),
                ('reads_mapped_and_paired', models.IntegerField(blank=True, null=True)),
                ('reads_unmapped', models.IntegerField(blank=True, null=True)),
                ('reads_properly_paired', models.IntegerField(blank=True, null=True)),
                ('reads_paired', models.IntegerField(blank=True, null=True)),
                ('reads_duplicated', models.IntegerField(blank=True, null=True)),
                ('reads_MQ0', models.IntegerField(blank=True, null=True)),
                ('reads_QC_failed', models.IntegerField(blank=True, null=True)),
                ('non_primary_alignments', models.IntegerField(blank=True, null=True)),
                ('total_length', models.IntegerField(blank=True, null=True)),
                ('bases_mapped', models.IntegerField(blank=True, null=True)),
                ('bases_mapped_cigar', models.IntegerField(blank=True, null=True)),
                ('bases_trimmed', models.IntegerField(blank=True, null=True)),
                ('bases_duplicated', models.IntegerField(blank=True, null=True)),
                ('mismatches', models.IntegerField(blank=True, null=True)),
                ('average_length', models.IntegerField(blank=True, null=True)),
                ('maximum_length', models.IntegerField(blank=True, null=True)),
                ('average_quality', models.FloatField(blank=True, null=True)),
                ('insert_size_average', models.FloatField(blank=True, null=True)),
                ('insert_size_standard_deviation', models.FloatField(blank=True, null=True)),
                ('inward_oriented_pairs', models.IntegerField(blank=True, null=True)),
                ('outward_oriented_pairs', models.IntegerField(blank=True, null=True)),
                ('pairs_with_other_orientation', models.IntegerField(blank=True, null=True)),
                ('pairs_on_different_chromosomes', models.IntegerField(blank=True, null=True)),
                ('acgt_cycles_image', models.FileField(blank=True, null=True, upload_to='uploads/%y/%m/')),
                ('coverage_image', models.FileField(blank=True, null=True, upload_to='uploads/%y/%m/')),
                ('gc_content_image', models.FileField(blank=True, null=True, upload_to='uploads/%y/%m/')),
                ('gc_depth_image', models.FileField(blank=True, null=True, upload_to='uploads/%y/%m/')),
                ('indel_cycles_image', models.FileField(blank=True, null=True, upload_to='uploads/%y/%m/')),
                ('indel_dist_image', models.FileField(blank=True, null=True, upload_to='uploads/%y/%m/')),
                ('insert_size_image', models.FileField(blank=True, null=True, upload_to='uploads/%y/%m/')),
                ('quality_cycle_image', models.FileField(blank=True, null=True, upload_to='uploads/%y/%m/')),
                ('quality_cycle_read_image', models.FileField(blank=True, null=True, upload_to='uploads/%y/%m/')),
                ('quality_cycle_read_freq_image', models.FileField(blank=True, null=True, upload_to='uploads/%y/%m/')),
                ('quality_heatmap_image', models.FileField(blank=True, null=True, upload_to='uploads/%y/%m/')),
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
            name='SubSection',
            fields=[
                ('name', models.CharField(max_length=25, primary_key=True, serialize=False)),
                ('min_read_count', models.IntegerField()),
                ('min_average_read_length', models.IntegerField()),
                ('max_average_read_length', models.IntegerField()),
                ('min_mapped_rate', models.FloatField()),
                ('max_error_rate', models.FloatField()),
                ('stop_lost', models.BooleanField()),
                ('stop_gained', models.BooleanField()),
                ('start_lost', models.BooleanField()),
                ('splice_region_variant', models.BooleanField()),
                ('splice_donor_variant', models.BooleanField()),
                ('splice_acceptor_variant', models.BooleanField()),
                ('regulatory_region_variant', models.BooleanField()),
                ('regulatory_region_amplification', models.BooleanField()),
                ('regulatory_region_ablation', models.BooleanField()),
                ('protein_altering_variant', models.BooleanField()),
                ('non_coding_transcript_variant', models.BooleanField()),
                ('non_coding_transcript_exon_variant', models.BooleanField()),
                ('missense_variant', models.BooleanField()),
                ('mature_miRNA_variant', models.BooleanField()),
                ('intron_variant', models.BooleanField()),
                ('intergenic_variant', models.BooleanField()),
                ('inframe_insertion', models.BooleanField()),
                ('inframe_deletion', models.BooleanField()),
                ('incomplete_terminal_codon_variant', models.BooleanField()),
                ('frameshift_variant', models.BooleanField()),
                ('feature_truncation', models.BooleanField()),
                ('feature_elongation', models.BooleanField()),
                ('downstream_gene_variant', models.BooleanField()),
                ('coding_sequence_variant', models.BooleanField()),
                ('TF_binding_site_variant', models.BooleanField()),
                ('TFBS_amplification', models.BooleanField()),
                ('TFBS_ablation', models.BooleanField()),
                ('NMD_transcript_variant', models.BooleanField()),
                ('five_prime_UTR_variant', models.BooleanField()),
                ('three_prime_UTR_variant', models.BooleanField()),
                ('freq_max_af', models.FloatField()),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Section')),
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
            name='UserSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('columns_to_hide', models.CharField(default='allele_depth,vafs,tcf,tcr,clinsig', max_length=200)),
                ('igv_view', models.BooleanField(default=True)),
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
                ('last_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('rs_number', models.TextField()),
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
                ('worst_consequence', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Consequence')),
            ],
        ),
        migrations.CreateModel(
            name='VariantSample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genotype', models.CharField(max_length=50)),
                ('caller', models.CharField(max_length=50)),
                ('allele_depth', models.CharField(max_length=50)),
                ('filter_status', models.CharField(max_length=100)),
                ('vafs', models.CharField(max_length=25)),
                ('total_count_forward', models.IntegerField(blank=True, null=True)),
                ('total_count_reverse', models.IntegerField(blank=True, null=True)),
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
                ('picked', models.BooleanField()),
                ('codons', models.TextField()),
                ('cdna_position', models.CharField(max_length=20)),
                ('protein_position', models.CharField(max_length=20)),
                ('amino_acids', models.TextField()),
                ('transcript', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Transcript')),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Variant')),
            ],
        ),
        migrations.CreateModel(
            name='Worksheet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('comment', models.TextField()),
                ('status', models.CharField(choices=[('1', 'New Worksheet - Awaiting Sequencing'), ('2', 'Awaiting QC Check'), ('3', 'Analysis Underway'), ('4', 'Complete'), ('5', 'Failed')], max_length=1)),
                ('sub_section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.SubSection')),
            ],
        ),
        migrations.AddField(
            model_name='sample',
            name='worksheet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Worksheet'),
        ),
        migrations.AddField(
            model_name='reportvariant',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Variant'),
        ),
        migrations.AddField(
            model_name='report',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Sample'),
        ),
        migrations.AddField(
            model_name='readlanequality',
            name='worksheet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Worksheet'),
        ),
        migrations.AddField(
            model_name='genecoverage',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Sample'),
        ),
        migrations.AddField(
            model_name='exoncoverage',
            name='gene',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Gene'),
        ),
        migrations.AddField(
            model_name='exoncoverage',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.Sample'),
        ),
        migrations.AddField(
            model_name='comment',
            name='variant_sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VariantDatabase.VariantSample'),
        ),
    ]
