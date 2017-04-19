from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    'passforget.views',
    url(r'^pass_forget/$', 'pass_forget', name='pass_forget'),
    url(r'^pass_rec/$', 'pass_rec', name='pass_rec'),
)

