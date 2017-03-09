from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [ url(r'^$', views.home_page, name='home_page'),
				url(r'^sections$', views.list_sections, name='list_sections'),
				url(r'^worksheet/(?P<pk_worksheet>\d+)/$', views.list_worksheet_samples, name='list_worksheet_samples'),
				url(r'^sample/(?P<pk_sample>\d+)/$', views.list_sample_variants, name='list_sample_variants'),
				url(r'^variant_detail$', views.variant_detail, name='variant_detail'),


				url(r'^login/$', auth_views.login, {'template_name': 'VariantDatabase/login.html'}, name='login'),
				url(r'^logout/$', auth_views.logout, {'template_name': 'VariantDatabase/logout.html'}, name='logout'),
				url(r'^search/$', views.search_page, name='search_page'),


				

]


