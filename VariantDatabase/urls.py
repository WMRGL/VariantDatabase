from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [ url(r'^$', views.home_page, name='home_page'),
				url(r'^list_projects$', views.list_projects, name='list_projects'),
				url(r'^project/(?P<pk>\d+)/$', views.list_batches, name='list_batches'),
				url(r'^batch/(?P<pk>\d+)/$', views.list_batch_samples, name='list_batch_samples'),
				url(r'^login/$', auth_views.login, {'template_name': 'VariantDatabase/login.html'}, name='login'),
				url(r'^logout/$', auth_views.logout, {'template_name': 'VariantDatabase/logout.html'}, name='logout'),


				

]


