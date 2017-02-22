from django.conf.urls import url
from . import views

urlpatterns = [ url(r'^$', views.home_page, name='home_page'),
				url(r'^list_projects$', views.list_projects, name='list_projects'),
				url(r'^project/(?P<pk>\d+)/$', views.list_batches, name='list_batches'),


]


