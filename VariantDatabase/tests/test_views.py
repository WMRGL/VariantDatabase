from django.test import  TestCase
from VariantDatabase.models import *

class TestViews(TestCase):
	"""
	Tests for most of the views.
	Only test if we get a successful response.


	Note:

	 - Reports and ajax forms are tested elsewhere due to complexity.

	 - Panel create is the same.



	"""
	fixtures = ['17-11-23-test-data.json']

	def setUp(self):

		self.client.login(username='admin', password= 'hello123')

	def test_view_login(self):

		response = self.client.get('/login/')

		self.assertEqual(response.status_code,200)

	def test_view_home(self):

		response = self.client.get('/')

		self.assertEqual(response.status_code,200)

	def test_view_list_sections(self):

		response = self.client.get('/sections/')

		self.assertEqual(response.status_code,200)

		self.assertEqual(len(response.context['all_sections']),5 )
	
	def test_view_list_worksheet_samples(self):

		response = self.client.get('/worksheet/1/')

		samples = response.context['samples_in_worksheet']

		worksheet = response.context['worksheet']

		quality_data = response.context['quality_data']

		self.assertEqual(response.status_code,200)

		self.assertEqual(len(samples),10)
		self.assertEqual(worksheet.name, 'MPN_213837' )
		self.assertEqual(samples[0].name, '1')
		self.assertEqual(len(quality_data), 3)

	def test_view_sample_summary(self):

		response = self.client.get('/sample/2/summary/')

		self.assertEqual(response.status_code,200)

		sample = response.context['sample']
		variants = response.context['variants']
		reports = response.context['reports']
		summary = response.context['summary']
		real_summary =  {'total': 2, 'synonymous': 1, 'missense_count': 0, 'lof_count': 0, 'indel_count': 1}
		total_summary = response.context['total_summary']
		real_total_summary = {'total': 49, 'synonymous': 21, 'missense_count': 20, 'lof_count': 2, 'indel_count': 3}
		
		self.assertEqual(sample.name, '2')
		self.assertEqual(len(variants), 2)
		self.assertEqual(len(reports), 0)
		self.assertEqual(summary,real_summary)
		self.assertEqual(total_summary, real_total_summary)

	def test_view_variant_detail(self):

		response = self.client.get('/sample/2/variant/90627e8fd634a3c6e96e85ddbd6c738bd154a928c1fe40be38db3624951cfb67/')

		self.assertEqual(response.status_code,200)	

	def test_view_gene(self):

		response = self.client.get('/gene/TP53/')

		self.assertEqual(response.status_code,200)	

	def test_view_detached_variant(self):

		response = self.client.get('/variant/185ad6ee127cb6b3705f847b00683f261c6ad9ece558c793c51c6e7fac9b175f/')

		self.assertEqual(response.status_code,200)	

	def test_view_user_settings(self):

		response = self.client.get('/variant/185ad6ee127cb6b3705f847b00683f261c6ad9ece558c793c51c6e7fac9b175f/')

		self.assertEqual(response.status_code,200)	

	def test_view_search(self):

		response = self.client.get('/search/')

		self.assertEqual(response.status_code,200)	

	def test_view_location_search(self):

		response = self.client.get('/search/location/9-5073770/')
		self.assertEqual(response.status_code,200)	

	def test_view_region_search(self):

		response = self.client.get('/search/region/9-5073720-5073780/')
		self.assertEqual(response.status_code,200)	

	def test_panel_view(self):

		response = self.client.get('/panels/1/view/')
		self.assertEqual(response.status_code,200)	

	def test_view_ajax_detail(self):

		response = self.client.get('/ajax/ajax_detail/', {'variant_hash': 'fab0f49adc03c6ca36c5d8185541c73f53b7189e9cd0ce562a74d318a55848ce', 'sample_pk': '2'},HTTP_X_REQUESTED_WITH='XMLHttpRequest')

		self.assertEqual(response.status_code,200)

	def test_view_ajax_table_expand(self):

		response = self.client.get('/ajax/ajax_table_expand/', {'variant_hash': 'fab0f49adc03c6ca36c5d8185541c73f53b7189e9cd0ce562a74d318a55848ce'},HTTP_X_REQUESTED_WITH='XMLHttpRequest')

		self.assertEqual(response.status_code,200)





