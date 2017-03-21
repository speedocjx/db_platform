from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    'salt.views',
    # url(r'^$', 'oms.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^api/execute$', 'execute', name='execute'),
    url(r'^salt_exec/$', 'salt_exec', name='salt_exec'),
    url(r'^hardware_info/$', 'hardware_info', name='hardware_info'),
    url(r'^api/getjobinfo$','getjobinfo', name='getjobinfo'),
    url(r'^key_con/$','key_con', name='key_con'),
    url(r'^hist_salt/$','hist_salt', name='hist_salt'),
)
