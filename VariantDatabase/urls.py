from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [ url(r'^$', views.home_page, name='home_page'),
				url(r'^sections/$', views.list_sections, name='list_sections'),
				url(r'^worksheet/(?P<pk_worksheet>\d+)/$', views.list_worksheet_samples, name='list_worksheet_samples'),
				url(r'^sample/(?P<pk_sample>\d+)/summary/$', views.sample_summary, name='sample_summary'),
				url(r'^sample/(?P<pk_sample>\d+)/variants$', views.list_sample_variants, name='list_sample_variants'),
				url(r'^gene/(?P<gene_pk>\w+)/$', views.view_gene, name='view_gene'),
				url(r'^sample/(?P<pk_sample>\d+)/variant/(?P<variant_hash>\w+)/$', views.variant_detail, name='variant_detail'),
				url(r'^variant/(?P<variant_hash>\w+)/$', views.view_detached_variant, name='view_detached_variant'),
				url(r'^settings/$', views.settings, name='settings'),
				url(r'^view_all_variants/$', views.view_all_variants, name='view_all_variants'),
				url(r'^all_questions/(?P<pk_interpretation>\d+)/$', views.all_questions, name = 'all_questions'),
				url(r'^variant_report/(?P<pk_interpretation>\d+)/$', views.report, name = 'report' ),
				url(r'^login/$', auth_views.login, {'template_name': 'VariantDatabase/login.html'}, name='login'),
				url(r'^logout/$', auth_views.logout, {'template_name': 'VariantDatabase/logout.html'}, name='logout'),
				url(r'^sample/(?P<pk_sample>\d+)/report/(?P<pk_report>\d+)$', views.create_sample_report, name='create_sample_report'),
				url(r'^sample/(?P<pk_sample>\d+)/report/(?P<pk_report>\d+)/view$', views.view_sample_report, name='view_sample_report'),
				url(r'^uploadsamplesheet/$', views.upload_sample_sheet, name='upload_sample_sheet'),

]


