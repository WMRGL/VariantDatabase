from django.conf.urls import url, include
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from .forms import CustomPasswordChangeForm


urlpatterns = [ url(r"^$", views.home_page, name="home_page"),
				url(r"^sections/$", views.list_sections, name="list_sections"),
				url(r"^worksheet/(?P<pk_worksheet>\d+)/$", views.list_worksheet_samples, name="list_worksheet_samples"),
				url(r"^sample/(?P<pk_sample>\d+)/summary/$", views.sample_summary, name="sample_summary"),
				url(r"^gene/(?P<gene_pk>\w+)/$", views.view_gene, name="view_gene"),
				url(r"^sample/(?P<pk_sample>\d+)/variant/(?P<variant_hash>\w+)/$", views.variant_detail, name="variant_detail"),
				url(r"^variant/(?P<variant_hash>\w+)/$", views.view_detached_variant, name="view_detached_variant"),
				url(r"^search/$", views.search, name="search"),
				url(r"^login/$", auth_views.login, {"template_name": "VariantDatabase/login.html"}, name="login"),
				url(r"^logout/$", auth_views.logout, {"template_name": "VariantDatabase/logout.html"}, name="logout"),
				url(r"^password_change/$", auth_views.password_change, {"template_name": "VariantDatabase/change_password.html", 'password_change_form': CustomPasswordChangeForm}, name="password_change"),
				url(r"^password_change_done/$", auth_views.password_change_done, {"template_name": "VariantDatabase/change_password_done.html"}, name="password_change_done"),
				url(r"^ajax/ajax_detail/$", views.ajax_detail, name="ajax_detail"),
				url(r"^ajax/ajax_comments/$", views.ajax_comments, name="ajax_comments"),
				url(r"^ajax/ajax_table_expand/$", views.ajax_table_expand, name="ajax_table_expand"),
				url(r"^ajax/ajax_receive_classification_data/$", views.ajax_receive_classification_data, name="ajax_receive_classification_data"),
				url(r"^ajax/update_panel/$", views.ajax_update_panel, name="ajax_update_panel"),
				url(r"^user_settings/$", views.user_settings, name="user_settings"),

				url(r"^api/variants/$", views.VariantView.as_view(), name="api_variants"),

				url(r"^sample/(?P<pk_sample>\d+)/report/(?P<pk_report>\d+)/(?P<check_number>(1|2))/$", views.create_sample_report, name="create_sample_report"),
				url(r"^sample/(?P<pk_sample>\d+)/report/(?P<pk_report>\d+)/view/$", views.view_sample_report, name="view_sample_report"),
				url(r"^sample/(?P<pk_sample>\d+)/report/(?P<pk_report>\d+)/resolve/$", views.resolve_check_differences, name="resolve_check_differences"),
				url(r"^panels/$", views.panel_list, name="panel_list"),
				url(r"^panels/(?P<pk_panel>\w+)/edit/$", views.panel_edit_create, name="panel_edit_create"),
				url(r"^panels/(?P<pk_panel>\w+)/view/$", views.panel_view, name="panel_view"),
				url(r"^search/location/(?P<location>[-\w]+)/$", views.view_location_search, name="view_location_search"),
				url(r"^search/region/(?P<location>[-\w]+)/$", views.view_region_search, name="view_region_search"),
				url(r"^search/samples/(?P<sample_query>[-\w]+)/$", views.view_sample_search, name="view_sample_search"),

				] 

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG is True:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

