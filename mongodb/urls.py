from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    'mongodb.views',
    # url(r'^$', 'oms.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^query/$', 'mongodb_query', name='mongodb_query'),
    url(r'^map/$', 'map', name='map'),
)
