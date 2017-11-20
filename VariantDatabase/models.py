from __future__ import unicode_literals
from django.db import models
from django.utils import timezone
from django.db.models import Q
import parsers.vcf_parser as vcf_parser
from django.contrib.contenttypes.models import ContentType
from auditlog.models import LogEntry
from auditlog.registry import auditlog
import numpy as np

class Section(models.Model):
	"""
	The Section model represents a section within the WMRGL laboratory e.g. Germline
	This is stored in the database to allow flexibility.
	Each Section can contain many Worksheets.

	"""

	owner = models.ForeignKey("auth.User")
	title = models.CharField(max_length=200)
	description = models.TextField()

	def __str__(self):
		return self.title


	def get_worksheets(self):

		"""
		Return all worksheets related 

		"""

		all_worksheets = Worksheet.objects.filter(sub_section__section=self)

		return all_worksheets

class SampleFilter(models.Model):
	"""
	Holds the filter settings for either a subsection or a report.


	"""
	name = models.CharField(max_length=15)
	upstream_gene_variant = models.BooleanField()
	transcript_amplification = models.BooleanField()
	transcript_ablation = models.BooleanField()
	synonymous_variant = models.BooleanField()
	stop_retained_variant = models.BooleanField()
	stop_lost = models.BooleanField()
	stop_gained = models.BooleanField()
	start_lost = models.BooleanField()
	splice_region_variant = models.BooleanField()
	splice_donor_variant = models.BooleanField()
	splice_acceptor_variant = models.BooleanField()
	regulatory_region_variant = models.BooleanField()
	regulatory_region_amplification = models.BooleanField()
	regulatory_region_ablation = models.BooleanField()
	protein_altering_variant = models.BooleanField()
	non_coding_transcript_variant = models.BooleanField()
	non_coding_transcript_exon_variant = models.BooleanField()
	missense_variant = models.BooleanField()
	mature_miRNA_variant = models.BooleanField()
	intron_variant = models.BooleanField()
	intergenic_variant = models.BooleanField()
	inframe_insertion = models.BooleanField()
	inframe_deletion = models.BooleanField()
	incomplete_terminal_codon_variant = models.BooleanField()
	frameshift_variant = models.BooleanField()
	feature_truncation = models.BooleanField()
	feature_elongation = models.BooleanField()
	downstream_gene_variant = models.BooleanField()
	coding_sequence_variant = models.BooleanField()
	TF_binding_site_variant = models.BooleanField()
	TFBS_amplification = models.BooleanField()
	TFBS_ablation = models.BooleanField()
	NMD_transcript_variant = models.BooleanField()
	five_prime_UTR_variant = models.BooleanField()
	three_prime_UTR_variant = models.BooleanField()
	freq_max_af = models.FloatField()

	def __str__(self):
		return self.name

	def create_filter_dict(self):
		"""
		Return a dictionary with all the filter settings in e.g. stop_lost=False

		"""


		filter_dict ={}


		filter_dict["upstream_gene_variant"] = self.upstream_gene_variant
		filter_dict["transcript_amplification"] = self.transcript_amplification
		filter_dict["transcript_ablation"] = self.transcript_ablation
		filter_dict["synonymous_variant"] = self.synonymous_variant
		filter_dict["stop_retained_variant"] = self.stop_retained_variant
		filter_dict["stop_lost"]=self.stop_lost
		filter_dict["stop_gained"]=self.stop_gained
		filter_dict["start_lost"]=self.start_lost
		filter_dict["splice_region_variant"]=self.splice_region_variant
		filter_dict["splice_donor_variant"]=self.splice_donor_variant
		filter_dict["splice_acceptor_variant"]=self.splice_acceptor_variant
		filter_dict["regulatory_region_variant"]=self.regulatory_region_variant
		filter_dict["regulatory_region_amplification"]=self.regulatory_region_amplification
		filter_dict["regulatory_region_ablation"]=self.regulatory_region_ablation
		filter_dict["protein_altering_variant"]=self.protein_altering_variant
		filter_dict["non_coding_transcript_variant"]=self.non_coding_transcript_variant
		filter_dict["non_coding_transcript_exon_variant"]=self.non_coding_transcript_exon_variant
		filter_dict["missense_variant"]=self.missense_variant
		filter_dict["mature_miRNA_variant"]=self.mature_miRNA_variant
		filter_dict["intron_variant"]=self.intron_variant
		filter_dict["intergenic_variant"]=self.intergenic_variant
		filter_dict["inframe_insertion"]=self.inframe_insertion
		filter_dict["inframe_deletion"]=self.inframe_deletion
		filter_dict["incomplete_terminal_codon_variant"]=self.incomplete_terminal_codon_variant
		filter_dict["frameshift_variant"]=self.frameshift_variant
		filter_dict["feature_truncation"]=self.feature_truncation
		filter_dict["feature_elongation"]=self.feature_elongation
		filter_dict["downstream_gene_variant"]=self.downstream_gene_variant
		filter_dict["coding_sequence_variant"]=self.coding_sequence_variant
		filter_dict["TF_binding_site_variant"]=self.TF_binding_site_variant
		filter_dict["TFBS_amplification"]=self.TFBS_amplification
		filter_dict["TFBS_ablation"]=self.TFBS_ablation
		filter_dict["NMD_transcript_variant"]=self.NMD_transcript_variant
		filter_dict["5_prime_UTR_variant"]=self.five_prime_UTR_variant
		filter_dict["3_prime_UTR_variant"]=self.three_prime_UTR_variant
		filter_dict["freq_max_af"]=self.freq_max_af
		
		return filter_dict

class SubSection(models.Model):
	"""
	A Model to represent a subsection.
	This is similar to the concept of a project e.g. MPN
	Can also represent a panel or chemisry for example.

	"""
	name = models.CharField(max_length=25, primary_key=True)
	section = models.ForeignKey(Section)
	

	#QC sample pass info - the levels needed for a sample to pass

	min_read_count = models.IntegerField()
	min_average_read_length = models.IntegerField()
	max_average_read_length = models.IntegerField()
	min_mapped_rate = models.FloatField()
	max_error_rate = models.FloatField()
	default_filter = models.ForeignKey(SampleFilter)


	def __str__(self):
		return self.name

	def get_number_samples(self):

		return Sample.objects.filter(worksheet__sub_section=self).count()
	




class Worksheet(models.Model):
	"""
	The Worksheet model represents a laboratory worksheet.
	Each Worksheet belongs to a Section.
	Each Worksheet can have many Samples assigned to it.

	"""

	choices =(
			("1", "New Worksheet - Awaiting Sequencing"),
			("2", "Awaiting QC Check"),
			("3", "Analysis Underway"),
			("4", "Complete"),
			("5", "Failed"))
			

	name = models.CharField(max_length=100, unique=True)
	sub_section = models.ForeignKey(SubSection)
	comment = models.TextField()
	status = models.CharField(max_length=1, choices = choices)


	def __str__(self):
		return self.name

	def get_status(self):
		"""
		Returns current status.
		"""
		choices =(
				("1", "New Worksheet - Awaiting Sequencing"),
				("2", "Awaiting QC Check"),
				("3", "Analysis Underway"),
				("4", "Complete"),
				("5", "Failed"))

		try:

			return choices[int(self.status)-1][1]

		except:

			return None

	def awaiting_qc_approval(self):
		"""
		Returns True if we are at the first stage i.e "New Worksheet".
		"""

		if self.status == "2":

			return True

		else:

			return False

	def get_history(self):
		"""
		Returns entire history from the audit log.
		"""

		content_type = ContentType.objects.get(app_label ="VariantDatabase", model="worksheet")

		return LogEntry.objects.filter(object_pk = self.pk, content_type=content_type)

	def get_creation_date(self):
		"""
		Returns creation date.
		"""

		try:

			content_type = ContentType.objects.get(app_label ="VariantDatabase", model="worksheet")

			return (LogEntry
					.objects
					.filter(object_pk = self.pk, content_type=content_type, action=0)
					.order_by("timestamp")[0].timestamp)

		except:

			return None


	def get_quality_data(self):
		"""
		Gets the ReadLaneQuality objects associated with the worksheet.
		Sort into correct order for display. 

		"""

		data = ReadLaneQuality.objects.filter(worksheet=self).order_by("read", "lane")

		data_list = []

		read_num = None

		for read_lane in data:

			if read_lane.read != read_num:

				read_num = read_lane.read

				data_list.append([read_lane])

			else:

				data_list[len(data_list)-1].append(read_lane)


		return data_list

	def qc_present(self):
		"""
		Returns True if QC has been uploaded.
		"""

		data = ReadLaneQuality.objects.filter(worksheet=self)

		if data.exists():

			return True

		else:

			return False

class Panel(models.Model):
	"""
	A model for storing gene lists that the variants in a sample to be filtered by.

	For example: D-MPD-001 has JAK2,CALR, MPL, CBL

	Therefore for samples with project set as D-MPD-001 we will only see variants in those genes.


	"""

	name = models.CharField(max_length=20, unique=True)
	description = models.TextField()
	subsection = models.ForeignKey(SubSection, null=True, blank=True)

	def __str__(self):
		return self.name


	def number_of_genes(self):
		"""
		Number of genes in the SampleGeneFilter

		Output:

		int, number of genes

		"""

		return PanelGene.objects.filter(panel=self).count()

	def get_genes(self):
		"""
		Get all genes in a panel.

		Output:

		genes =  List of genes 
		"""

		genes = PanelGene.objects.filter(panel =self).select_related('gene')

		genes = [gene.gene for gene in genes]

		return genes


class Sample(models.Model):
	"""
	The Sample model holds information on a particular sample
	There can be many samples in a Worksheet.
	Each sample must have a unique name.
	Each sample contains a link to a VCF file where the data is (originally) stored.

	"""
	choices =(
			("1", "New Sample"),
			("2", "Report Complete"),
			("3", "Invalid"))


	name = models.CharField(max_length=50, unique=True)
	worksheet = models.ForeignKey(Worksheet)
	vcf_file = models.TextField(null=True, blank=True)
	bam_file_pindel = models.TextField(null=True, blank=True)
	bam_file_bwa = models.TextField(null=True, blank=True)
	visible = models.BooleanField() #To allow the hiding of a sample
	status = models.CharField(max_length=1, choices = choices)

	sample_well = models.CharField(max_length =10)
	i7_index_id = models.IntegerField()
	index = models.CharField(max_length =50)
	panel = models.ForeignKey(Panel)

	#QC data from SamStats

	raw_total_sequences = models.IntegerField(null=True,blank=True)
	filtered_sequences = models.IntegerField(null=True,blank=True)
	sequences = models.IntegerField(null=True,blank=True)
	first_fragments = models.IntegerField(null=True,blank=True)
	last_fragments = models.IntegerField(null=True,blank=True)
	reads_mapped = models.IntegerField(null=True,blank=True)
	reads_mapped_and_paired = models.IntegerField(null=True,blank=True)
	reads_unmapped = models.IntegerField(null=True,blank=True)
	reads_properly_paired = models.IntegerField(null=True,blank=True)
	reads_paired = models.IntegerField(null=True,blank=True)
	reads_duplicated = models.IntegerField(null=True,blank=True)
	reads_MQ0 = models.IntegerField(null=True,blank=True)
	reads_QC_failed = models.IntegerField(null=True,blank=True)
	non_primary_alignments = models.IntegerField(null=True,blank=True)
	total_length = models.IntegerField(null=True,blank=True)
	bases_mapped = models.IntegerField(null=True,blank=True)
	bases_mapped_cigar = models.IntegerField(null=True,blank=True)
	bases_trimmed = models.IntegerField(null=True,blank=True)
	bases_duplicated = models.IntegerField(null=True,blank=True)
	mismatches = models.IntegerField(null=True,blank=True)
	average_length = models.IntegerField(null=True,blank=True)
	maximum_length = models.IntegerField(null=True,blank=True)
	average_quality = models.FloatField(null=True,blank=True)
	insert_size_average = models.FloatField(null=True,blank=True)
	insert_size_standard_deviation = models.FloatField(null=True,blank=True)
	inward_oriented_pairs = models.IntegerField(null=True,blank=True)
	outward_oriented_pairs = models.IntegerField(null=True,blank=True)
	pairs_with_other_orientation = models.IntegerField(null=True,blank=True)
	pairs_on_different_chromosomes = models.IntegerField(null=True,blank=True)

	#QC images from SamStats

	acgt_cycles_image = models.FileField(upload_to="uploads/%y/%m/", null=True, blank=True)
	coverage_image = models.FileField(upload_to="uploads/%y/%m/", null=True, blank=True)
	gc_content_image = models.FileField(upload_to="uploads/%y/%m/", null=True, blank=True)
	gc_depth_image = models.FileField(upload_to="uploads/%y/%m/", null=True, blank=True)
	indel_cycles_image = models.FileField(upload_to="uploads/%y/%m/", null=True, blank=True)
	indel_dist_image = models.FileField(upload_to="uploads/%y/%m/", null=True, blank=True)
	insert_size_image = models.FileField(upload_to="uploads/%y/%m/", null=True, blank=True)
	quality_cycle_image = models.FileField(upload_to="uploads/%y/%m/", null=True, blank=True)
	quality_cycle_read_image = models.FileField(upload_to="uploads/%y/%m/", null=True, blank=True)

	quality_cycle_read_freq_image = models.FileField(upload_to="uploads/%y/%m/",
													 null=True, blank=True)
	quality_heatmap_image = models.FileField(upload_to="uploads/%y/%m/", null=True, blank=True)

	def __str__(self):
		return self.name

	def already_exists(self, query_name):

		"""
		Checks if a sample with that name already exists so can be rejected.
		Used in the import_vcf.py management command.

		"""

		count = Sample.objects.filter(name=query_name).count()

		if count >0:

			return True

		else:

			return False


	def get_status(self):
		"""
		Returns current status.
		"""
		choices =(
				("1", "New Sample"),
				("2", "Report Complete"),
				("3", "Invalid"))


		try:

			return choices[int(self.status)-1][1]

		except:

			return None


	def get_error_rate(self):
		"""
		Calculate the error rate for the sample using the information imported from the .stats file.

		"""

		if self.mismatches == None or self.bases_mapped_cigar == None:

			return None

		else:

			return self.mismatches /float(self.bases_mapped_cigar)




	def get_mapped_percentage(self):
		"""
		Get percentage of reads mapped
		"""
		if self.reads_mapped == None or self.raw_total_sequences ==None:

			return None

		else:

			return float(self.reads_mapped)/float(self.raw_total_sequences)


	def sample_qc_passed(self):
		"""
		Checks the sample QC against the Subsection options.


		"""

		if (self.raw_total_sequences == None or 
			self.average_length == None or
			self.get_mapped_percentage() == None or
			self.get_error_rate() == None):

			return "NO QC"

		else:

			subsection = self.worksheet.sub_section

			if (self.raw_total_sequences < subsection.min_read_count or 
				self.average_length < subsection.min_average_read_length or 
				self.average_length > subsection.max_average_read_length or
				self.get_mapped_percentage() < subsection.min_mapped_rate or
				self.get_error_rate() > subsection.max_error_rate):


				return "FAIL"

			else:

				return "PASS"






class Consequence(models.Model):
	"""
	A model to hold the VEP consequences.
	See : http://www.ensembl.org/info/genome/variation/predicted_data.html
	The worst_consequence field in the Variant model links to an object in this model.

	"""

	name = models.CharField(max_length = 100, primary_key =True)
	impact = models.IntegerField() #number giving impact rating 1-28

	def __str__(self):
		return self.name


class Gene(models.Model):

	"""
	Stores genes that have been seen before.
	Each Transcript links to a Gene.
	Each Variant can fall in many Transcripts - VariantTranscript 


	"""

	name = models.CharField(max_length=50, db_index=True, unique=True)



	def __str__(self):
		return self.name

	def get_all_variants(self):
		"""
		Returns all variants within a Gene.

		"""
		variants = (VariantTranscript
					.objects
					.filter(transcript__gene = self)
					.values("variant")
					.distinct())

		variants = Variant.objects.filter(variant_hash__in=variants)

		variants = variants.order_by("-position")

		return variants


	def get_canonical_transcript(self):
		"""
		A Gene may have multiple Transcripts assosiated with it.
		This function returns the canonical Transcript for the gene

		"""

		canonical = Transcript.objects.filter(gene=self, canonical=True)

		return canonical

	def get_transcripts(self):
		"""
		Return all Transcripts assosiated with a Gene.

		"""

		return Transcript.objects.filter(gene=self)

class PanelGene(models.Model):

	"""
	The genes which are in a specific SampleGeneFilter

	"""

	panel = models.ForeignKey(Panel)
	gene = models.ForeignKey(Gene)

class Transcript(models.Model):
	"""
	Each Gene can be associated with one or more Transcripts.
	A Transcript can be associated with a Gene, although this is not required.

	"""

	name = models.CharField(max_length=64, primary_key=True)
	canonical = models.BooleanField()
	gene = models.ForeignKey(Gene, null=True)

	def __str__(self):
		return self.name

	def get_gene(self):
		"""
		Return the gene that a Transcript falls within.
		Returns None if the Transcript is not associated with a Gene.

		"""

		if self.gene is not None:

			return self.gene.name

		else:

			return None

class Variant(models.Model):

	"""
	The Variant model holds unique variants.

	If a variant is seen in another vcf it will not appear twice in this model.

	"""
	#Variant Data
	variant_hash = models.CharField(max_length=64, primary_key = True)
	chromosome  = models.CharField(max_length=25)
	position  = models.IntegerField()
	ref = models.TextField()
	alt = models.TextField()
	last_updated =  models.DateTimeField(default = timezone.now)
	rs_number = models.TextField()
	worst_consequence = models.ForeignKey(Consequence)
	clinical_sig = models.TextField()

	#Frequency Data
	max_af = models.FloatField()
	af = models.FloatField()
	afr_af = models.FloatField()
	amr_af = models.FloatField()
	eur_af = models.FloatField()
	eas_af = models.FloatField()
	sas_af = models.FloatField()
	exac_af = models.FloatField()
	exac_adj_af = models.FloatField()
	exac_afr_af = models.FloatField()
	exac_amr_af = models.FloatField()
	exac_eas_af = models.FloatField()
	exac_fin_af = models.FloatField()
	exac_nfe_af = models.FloatField()
	exac_oth_af = models.FloatField()
	exac_sas_af = models.FloatField()
	esp_ea_af = models.FloatField()
	esp_aa_af = models.FloatField()



	def __str__(self):
		return self.chromosome + " " + str(self.position) + " " +  self.ref + " " +self.alt

	def get_sample_count(self):
		"""
		Returns the number of samples this variant has been seen in.

		"""

		return VariantSample.objects.filter(variant=self).count()

	def get_worksheet_count(self):
		"""
		Returns the number of worksheets that a variant has occured in.

		"""
		worksheet_dict ={}

		variant_samples = VariantSample.objects.filter(variant=self)



		for variant_sample in variant_samples:

			worksheet = variant_sample.sample.worksheet

			if worksheet not in worksheet_dict:

				worksheet_dict[worksheet] =1


		return len(worksheet_dict)
		
	def get_samples_with_variant(self):
		"""
		Returns all samples in which the Variant has been found.

		"""

		samples =VariantSample.objects.filter(variant=self)

		samples =list(set([variant_sample.sample for variant_sample in samples]))

		return samples


	def get_genes(self):
		"""
		Return all Genes that a variant is found in.

		"""

		variant_transcripts = VariantTranscript.objects.filter(variant =self)

		my_list = []

		for var in variant_transcripts:

			if var.transcript.gene is not None:

				my_list.append(var.transcript.gene)


		return list(set(my_list))



	def display_ids(self):
		"""
		Return IDs as a list e.g ids seperated by & symbols
		"""

		variant_ids = self.rs_number.split("&")

		return variant_ids



	def same_codon_missense(self):
		"""
		Is the variant in the same codon as an existing variant in the DB?

		How does this work?

		1) Only look at missense variants
		2) Get all variants that could be in the same codon e.g. +2 or -2 in position.
		3) Get the hgvsp for our variant
		4) For each of the variants that are nearby i.e. the query in part 2
			4a) only look at missense variants
			4b) get the hgvp for that variant
			4c) for each of the hgvsp for that variant
				4d) See if the codon is the same as the original
				4e) if so then add to list to be returned


		NOTE : NOT TESTED!
		"""

		if self.worst_consequence.name == "missense_variant":

			same_codon = []

			position_range =2

			variant_list = (Variant
							.objects
							.filter(chromosome=self.chromosome)
							.filter(position__range=(self.position-position_range,self.position+position_range ))
							.exclude(variant_hash =self.variant_hash))

			transcript_list =[]

			self_hgvsp = VariantTranscript.objects.filter(variant=self).values_list("hgvsp", flat=True)

			for hgvsp in self_hgvsp:

				transcript, codon = vcf_parser.extract_codon_from_hgvs(hgvsp)

				if transcript == False:

					return None

				transcript_list.append((transcript.strip(), codon))


			for variant in variant_list:

				if variant.worst_consequence.name == "missense_variant":

					variant_hgvsp_list = (VariantTranscript
											.objects
											.filter(variant=variant)
											.values_list("hgvsp", flat=True))

					transcript_list_vars =[]

					for hgvsp in variant_hgvsp_list:

						transcript, codon = vcf_parser.extract_codon_from_hgvs(hgvsp)

						transcript_list_vars.append((transcript.strip(),codon))

						both = set(transcript_list) & set(transcript_list_vars)


						if len(both) >0:

							same_codon.append(variant)

			if len(list(set(same_codon))) == 0:

				return None

			else:

				return list(set(same_codon))



	def get_other_alleles(self):
		"""	
		Returns any other variants at the same position
		"""

		other_alleles = (Variant
							.objects
							.filter(chromosome = self.chromosome, position = self.position)
							.exclude(variant_hash = self.variant_hash))

		return other_alleles


	def get_picked_transcript(self):

		"""
		Return the transcript that has been picked by VEP
		This is the variant with "1" in the PICK field of the VEP annotation
		Data stored in VariantTranscript model

		"""

		picked = VariantTranscript.objects.filter(variant=self).filter(picked=True)

		return picked



	def get_picked_hgvsc(self):
		"""
		Which hgvsc to show in the summary page.

		Can go with the one that VEP has picked i.e added a PICK flag too.

		Some problems with this when there are multiple genes. 

		So if we get no hgvsc for the picked we get one that does have one.

		"""

		picked = VariantTranscript.objects.filter(variant=self).filter(picked=True)
	
		if len(picked) ==1:

			picked = picked[0]

		
			if picked.transcript == None or picked.hgvsc=="":
				
				transcripts = VariantTranscript.objects.filter(variant=self)

				if len(transcripts) ==1:

					return None

				else:


					transcripts = transcripts.exclude(hgvsc="")

					if len(transcripts) == 0:

						return None

					else:

						return transcripts[0].hgvsc


			else:

				return picked.hgvsc

	
		else:

			return "Error"

		

	def get_picked_hgvsp(self):

		"""
		Which hgvsp to show in the summary page.

		Can go with the one that VEP has picked i.e added a PICK flag too.

		Some problems with this when there are multiple genes. 

		So if we get no hgvsp for the picked we get one that does have one.

		"""

		picked = VariantTranscript.objects.filter(variant=self).filter(picked=True)
	
		if len(picked) ==1:

			picked = picked[0]

		
			if picked.transcript == None or picked.hgvsp=="":
				
				transcripts = VariantTranscript.objects.filter(variant=self)

				if len(transcripts) ==1:

					return None

				else:


					if len(transcripts) == 0:

						return None

					else:

						return transcripts[0].hgvsp


			else:

				return picked.hgvsp

	
		else:

			return "Error"



	def get_frequency_data(self):

		"""
		Function to get all the relevent frequency data for display.

		Output:

		frequency_dict = A dictionary containing:

			1) Global Frequency, Sample Count

			2) For each subsection/project:

				a) Frequency, sample_count

		"""

		frequency_dict ={"global":{}, "projects":{}}

		#Global stats

		global_sample_count = self.get_sample_count()

		total_sample_count = Sample.objects.count()

		global_frequency = float(global_sample_count) / float(total_sample_count)

		#Per subsection/project count

		projects = (VariantSample
					.objects
					.filter(variant=self)
					.values_list("sample__worksheet__sub_section")
					.distinct())

		variant_samples = VariantSample.objects.filter(variant=self)

		for project in projects:

			name = project[0]

			project_obj = SubSection.objects.get(name=name)

			project_count = (VariantSample
								.objects.filter(variant=self)
								.filter(sample__worksheet__sub_section=project_obj)
								.count())

			project_sample_count = project_obj.get_number_samples()

			project_frequency = float(project_count) / float(project_sample_count)


			frequency_dict["projects"][name] =[ project_count,
												project_sample_count,
												project_frequency ]


		frequency_dict["global"] = [ global_sample_count,
									 total_sample_count,
									 global_frequency ]

		return frequency_dict



	def previous_classifications(self):
		"""
		For getting all classifications for a variant.
		No organisation by subsection etc.

		Output:

		classifications = queryset, all classifications for a variant

		"""

		classifications = (ReportVariantSampleClassification
					.objects
					.filter(variant=self)
					.exclude(final_classification=None)
					.order_by("-report__resolver_date"))


		return classifications




	def previous_classifications_tuple_list(self):
		"""
		Returns a list of tuples containing information on previous \
		classifications. This is intended to be used by futher functions \
		that will display the information e.g list by sebsection.

		Output:

		classifications = list, list of tuples (final_class, subsection, date, sample)

		"""

		classifications_dict = {}


		classifications = (ReportVariantSampleClassification
							.objects
							.filter(variant=self)
							.exclude(final_classification=None)
							.select_related('final_classification'))

		classifications = [(x.final_classification,
							x.report.sample.worksheet.sub_section,
							x.final_date,
							x.report.sample) for x in classifications]

		return classifications






class VariantSample(models.Model):

	"""
	The VariantSample model stores which sample a Variant has appears in.


	Allows queries such as "which other samples have we seen this variant in?"

	"""

	variant = models.ForeignKey(Variant)
	sample = models.ForeignKey(Sample)
	genotype = models.CharField(max_length =50)
	caller = models.CharField(max_length=50)
	allele_depth = models.CharField(max_length=50)
	filter_status = models.CharField(max_length=100)
	vafs = models.CharField(max_length=25) #list of VAFs in the order listed in - Caller
	total_count_forward = models.IntegerField(null=True, blank=True)
	total_count_reverse = models.IntegerField(null=True, blank=True)

	def __str__(self):
		return str(self.variant) + str(self.sample)


	def get_subsection_count(self):
		"""
		Returns the count within a subsection/project.
		e.g. how many samples within MPN have we seen this variant in?

		"""

		section = self.sample.worksheet.sub_section

		count = (VariantSample
				.objects
				.filter(variant=self.variant,sample__worksheet__sub_section=section)
				.count())

		return count


	def get_subsection_frequency(self):
		"""
		Returns the frequency within a subsection/project. \
		e.g. how many samples within MPN have we seen this variant in / total subsection samples

		"""

		subsection = self.sample.worksheet.sub_section

		total = subsection.get_number_samples()

		count = self.get_subsection_count()

		frequency = round(float(count) /float(total),2)

		return frequency


	def get_worksheet_count(self):
		"""
		Number of patients that a variant appears in within the worksheet.

		"""

		return VariantSample.objects.filter(variant=self).count()

	def display_genotype(self):

		"""
		Takes genotype and displays in as either Het or Hom

		"""

		if self.genotype == "0/1":

			return "Het"

		elif self.genotype == "1/1":

			return "Hom"

		else:

			return self.genotype

	def calculate_allele_balance(self):
		"""
		Uses the vcf_parser.calculate_allele_balance() to calculate the AB

		Note: Do we calculate this on the fly or at import for performance?


		"""

		return vcf_parser.calculate_allele_balance(self.vafs, self.caller)

	def allele_balance_out_of_range(self):
		"""
		Look at other instances of the variant in the same run (worksheet).

		If the allele balance for this variant is > 2std away from the mean
		allele balance then return True, Otherwise return False



		"""

		#get all instances of this variant in this worksheet. 

		variant_samples = (VariantSample
							.objects
							.filter(sample__worksheet=self.sample.worksheet, variant=self.variant)
							.exclude(sample__name__contains="D00-00000")
							.values_list("vafs","caller", "pk"))

		#If it is a singleton then we can ignore
		if len(variant_samples) ==1:

			return 0.0

		allele_balance_list = [vcf_parser.calculate_allele_balance(vs_list[0], vs_list[1]) for vs_list in variant_samples]

		allele_balance_array = np.array(allele_balance_list)

		mean = allele_balance_array.mean()

		std = allele_balance_array.std()

		variant_ab = self.calculate_allele_balance()

		zscore = (variant_ab - mean) / std

		return zscore



		
	def get_previous_classification(self):
		"""
		returns classifications done in the same section.

		"""

		classifications = ReportVariantSampleClassification.objects.filter(variant=self.variant)

		classifications = classifications.exclude(final_classification=None)

		same_section = classifications.filter(report__sample__worksheet__sub_section__section =self.sample.worksheet.sub_section.section)

		same_section = same_section.order_by("-report__resolver_date")

		if same_section.exists():

			return same_section[0].final_classification

		else:

			return None







class VariantTranscript(models.Model):
	"""
	A Variant can be in mutiple Transcripts.
	This model holds the information on how a particular Variant affects a Transcript.

	"""

	variant = models.ForeignKey(Variant)
	transcript = models.ForeignKey(Transcript)
	consequence = models.TextField()
	exon = models.CharField(max_length =25)
	intron = models.CharField(max_length =25)
	hgvsc = models.TextField()
	hgvsp = models.TextField()
	picked =models.BooleanField()
	codons = models.TextField()
	cdna_position = models.CharField(max_length=20)
	protein_position = models.CharField(max_length=20)
	amino_acids = models.TextField()

	def __str__(self):

		return self.variant.chromosome+ " " + str(self.variant.position) + self.transcript.name


class ReadLaneQuality(models.Model):
	"""
	This model hold the data parsed from the Illumina InterOp files.

	A separate object is created for each lane-read combination.


	"""

	worksheet = models.ForeignKey(Worksheet)
	read = models.IntegerField()
	lane = models.IntegerField()

	yield_g = models.FloatField()
	density = models.FloatField()
	cluster_count_pf = models.FloatField()
	cluster_count = models.FloatField()
	phasing = models.FloatField()
	prephasing = models.FloatField()
	read_count = models.FloatField()
	reads_pf = models.FloatField()
	percent_gt_q30 = models.FloatField(null=True)
	percent_aligned = models.FloatField(null=True)
	error_rate = models.FloatField(null=True)
	error_rate_35 = models.FloatField(null=True)
	error_rate_50 = models.FloatField(null=True)
	error_rate_75 = models.FloatField(null=True)
	error_rate_100 = models.FloatField(null=True)


	def __str__(self):

		return self.worksheet.name+ " " + str(self.pk)


	def format_density(self):

		return self.density/1000

	def cluster_pf_percent(self):

		return (self.cluster_count_pf/self.cluster_count)*100

	def format_reads(self):

		return self.read_count/1000000

	def format_reads_pf(self):

		return self.reads_pf/1000000

class GeneCoverage(models.Model):
	"""
	Model to hold the gene coverage data for a sample.
	Each Gene that a variant occurs in within a sample will have an entry in this model.

	"""

	sample = models.ForeignKey(Sample)
	gene = models.ForeignKey(Gene)

	x100 = models.IntegerField()
	x200 = models.IntegerField()
	x300 = models.IntegerField()
	x400 = models.IntegerField()
	x500 = models.IntegerField()
	x600 = models.IntegerField()
	min_coverage = models.IntegerField()
	max_coverage = models.IntegerField()
	mean_coverage = models.FloatField()
	number_of_regions = models.IntegerField()


	def __str__(self):

		return self.sample.name+ " " + self.gene.name + " " +str(self.pk)



	def get_percentages(self):

		raw_data = [self.x100, self.x200, self.x300, self.x400, self.x500, self.x600]

		return map(lambda x: round((float(x)/float(self.number_of_regions)*100),1), raw_data)

class ExonCoverage(models.Model):
	"""
	Model to hold the exon coverage data for a sample.
	Each Exon that a variant occurs in within a sample will have an entry in this model.

	"""

	sample = models.ForeignKey(Sample)
	gene = models.ForeignKey(Gene)
	exon = models.CharField(max_length=20)

	x100 = models.IntegerField()
	x200 = models.IntegerField()
	x300 = models.IntegerField()
	x400 = models.IntegerField()
	x500 = models.IntegerField()
	x600 = models.IntegerField()
	min_coverage = models.IntegerField()
	max_coverage = models.IntegerField()
	mean_coverage = models.FloatField()
	number_of_regions = models.IntegerField()


	def __str__(self):

		return self.sample.name+ " " + self.gene.name + " " +str(self.pk)

	def get_percentages(self):

		raw_data = [self.x100, self.x200, self.x300, self.x400, self.x500, self.x600]

		return map(lambda x: round((float(x)/float(self.number_of_regions)*100),1), raw_data)


class Comment(models.Model):
	"""
	Model to hold user comments on a VariantSample

	"""

	user = models.ForeignKey("auth.User")
	text = models.TextField()
	time = models.DateTimeField()
	variant_sample = models.ForeignKey("VariantSample")

	def __str__(self):

		return str(self.variant_sample) + " " +str(self.pk)


	def get_evidence(self):

		evidence = Evidence.objects.filter(comment=self)

		if len(evidence) == 0:

			return None

		else:

			return evidence


class Evidence(models.Model):
	"""
	Model to hold files that relate to evidence e.g. pdfs, screenshots.

	Must be associated with a comment.

	"""
	file = models.FileField(upload_to="uploads/%y/%m/", null=True, blank=True)
	comment = models.ForeignKey(Comment)


class UserSetting(models.Model):

	"""
	A class for storing user settings - mainly which columns we want to see.


	"""

	default = "allele_depth,vafs,tcf,tcr,clinsig,filter_status"

	columns_to_hide= models.CharField(max_length=200, default=default)
	igv_view = models.BooleanField(default=True) #does the user want to see the IGV viewer
	user = models.ForeignKey("auth.User")



class Report(models.Model):

	"""
	A class for reporting a sample.

	Made for the Haem-Onc team workflow - may require different ormat for different teams.

	"""

	choices =(
		("1", "Awaiting First Check"),
		("2", "Awaiting Second Check"),
		("3", "Complete"),
		("4", "Invalid"))



	sample = models.ForeignKey(Sample)
	status = models.CharField(max_length=1, choices =choices)
	panel = models.ForeignKey(Panel)
	default_filter = models.ForeignKey(SampleFilter)


	report_creator = models.ForeignKey("auth.User", related_name="report_creator")
	first_checker = models.ForeignKey("auth.User", related_name="first_checker", null=True, blank=True)
	second_checker = models.ForeignKey("auth.User", related_name="second_checker", null=True, blank=True)
	resolver = models.ForeignKey("auth.User", related_name="resolver", null=True, blank=True)

	creation_date = models.DateTimeField()
	first_check_date = models.DateTimeField(null=True, blank=True)
	second_check_date = models.DateTimeField(null=True, blank=True)
	resolver_date = models.DateTimeField(null=True, blank=True)



	def get_status(self):
		"""
		Returns current status.
		"""
		choices =(
			("1", "Awaiting First Check"),
			("2", "Awaiting Second Check"),
			("3", "Awaiting Resolution"),
			("4", "Complete"),
			("5", "Invalid"),
			)

		try:

			return choices[int(self.status)-1][1]

		except:

			return None


	def number_of_mismatches(self):
		"""
		Returns the number of mismatches between in the 
		ReportVariantSampleClassification model i.e.

		- The number of ReportVariantSampleClassification where the classifications made by
		  users in the 1st check does not macth that by the user doing the second check.

		 -Also where the hgvs does not match


		"""

		report_sample_variant_classifications = (ReportVariantSampleClassification
													.objects
													.filter(report=self))

		count =0

		for variant_classification in report_sample_variant_classifications:

			if variant_classification.classification_match() != True:

				count = count+1


		return count







class Classification(models.Model):
	"""
	Stores the possible classifications for variants.
	Linked with SubSection Class in case different projects
	have different requirements.

	"""

	name = models.CharField(max_length=20)
	subsection = models.ForeignKey(SubSection)

	def __str__(self):

		return str(self.name)


class ReportVariantSampleClassification(models.Model):
	"""

	Stores the classification for a VariantSample for a particular report.

	e.g. Variant Chr3-39253-A-G in report x was classed as Artefact 
	

	"""

	report = models.ForeignKey(Report)
	variant = models.ForeignKey(Variant)
	user_hgvs1 = models.TextField()
	classification1 = models.ForeignKey(Classification, related_name="classification1")
	user_hgvs2 = models.TextField(blank=True, null=True)
	classification2 = models.ForeignKey( Classification,
										 related_name="classification2",
										 blank=True,
										 null=True)
	final_classification = models.ForeignKey(Classification,
												related_name="final_classification",
												blank=True,
												null=True)
	final_hgvs = models.TextField(blank=True, null=True)


	def classification_match(self):
		"""
		Do classification1 and classification2 match?

		"""

		if self.classification1 == self.classification2 and self.user_hgvs1 == self.user_hgvs2:

			return True

		else:

			return False


auditlog.register(Worksheet)