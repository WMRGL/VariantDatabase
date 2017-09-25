from django.test import  TestCase
from VariantDatabase.models import *

class TestViews(TestCase):


	fixtures = ['test_data.json']

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

	def test_view_list_worksheet_samples(self):

		response = self.client.get('/worksheet/1/')

		self.assertEqual(response.status_code,200)	

	def test_view_sample_summary(self):

		response = self.client.get('/sample/2/summary/')

		self.assertEqual(response.status_code,200)	


	def test_view_variant_detail(self):

		response = self.client.get('/sample/2/variant/90627e8fd634a3c6e96e85ddbd6c738bd154a928c1fe40be38db3624951cfb67/')

		self.assertEqual(response.status_code,200)	


	def test_view_search(self):

		response = self.client.get('/search/')

		self.assertEqual(response.status_code,200)	


	def test_view_gene(self):

		response = self.client.get('/gene/TP53/')

		self.assertEqual(response.status_code,200)	

	def test_view_detached_variant(self):

		response = self.client.get('/variant/185ad6ee127cb6b3705f847b00683f261c6ad9ece558c793c51c6e7fac9b175f/')

		self.assertEqual(response.status_code,200)	

	def test_view_sample_report(self):

		response = self.client.get('/sample/2/report/1/view/')

		self.assertEqual(response.status_code,200)	

	def test_view_ajax_detail(self):

		response = self.client.get('/ajax/ajax_detail/', {'variant_hash': 'fab0f49adc03c6ca36c5d8185541c73f53b7189e9cd0ce562a74d318a55848ce', 'sample_pk': '2'},HTTP_X_REQUESTED_WITH='XMLHttpRequest')

		self.assertEqual(response.status_code,200)	