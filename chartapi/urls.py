from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    'chartapi.views',
    # url(r'^query/$', 'mongodb_query', name='mongodb_query'),
    url(r'^tb_inc_status/$', 'tb_inc_status', name='tb_inc_status'),
    url(r'^dbstatus/$', 'dbstatus', name='dbstatus'),
)
