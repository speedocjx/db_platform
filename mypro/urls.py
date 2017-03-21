"""mypro URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from django.conf import settings
from myapp import views as myapp_view
urlpatterns = (
    url(r'^$', myapp_view.index, name='index'),
    url(r'^accounts/login/$',myapp_view.login,name='login'),
    url(r'^accounts/logout/$',myapp_view.logout,name='logout'),
    url(r'^admin/', admin.site.urls),
    url(r'^log_query/$', myapp_view.log_query,name='log_query'),
    url(r'^mysql_query/$', myapp_view.mysql_query,name='mysql_query'),
    url(r'^mysql_admin/$', myapp_view.mysql_admin, name='mysql_admin'),
    url(r'^binlog_parse/$', myapp_view.mysql_binlog_parse,name='binlog_parse'),
    url(r'^tb_check/$', myapp_view.tb_check, name='tb_check'),
    url(r'^meta_data/$', myapp_view.meta_data,name='meta_data'),
    url(r'^mysql_exec/$', myapp_view.mysql_exec,name='mysql_exec'),
    url(r'^captcha/',include('captcha.urls')),
    url(r'^sqlcheck/$', myapp_view.inception,name='inception'),
    url(r'^task/$', myapp_view.task_manager,name='task_manager'),
    url(r'^pre_query/$', myapp_view.pre_query,name='pre_query'),
    url(r'^pass_reset/$', myapp_view.pass_reset,name='pass_reset'),
    url(r'^pre_set/$', myapp_view.pre_set,name='pre_set'),
    url(r'^set_dbgroup/$', myapp_view.set_dbgroup,name='set_dbgroup'),
    url(r'^set_ugroup/$', myapp_view.set_ugroup,name='set_ugroup'),
    url(r'^fast_dbset/$', myapp_view.fast_dbset,name='fast_dbset'),
    url(r'^set_dbname/$', myapp_view.set_dbname,name='set_dbname'),
    url(r'^update_task/$', myapp_view.update_task,name='update_task'),
    url(r'^salt/', include('salt.urls')),
    url(r'^mongodb/', include('mongodb.urls')),
    url(r'^chartapi/', include('chartapi.urls')),
    url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
)

