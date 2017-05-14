from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    'blacklist.views',
    url(r'^blist/$', 'blist', name='blist'),
    url(r'^bl_delete/$', 'bl_delete', name='bl_delete'),
    url(r'^bl_edit/$', 'bl_edit', name='bl_edit'),
)
