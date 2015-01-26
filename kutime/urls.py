from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

from models.kutime import *
admin.autodiscover()
admin.site.register(College)
admin.site.register(Department)
admin.site.register(Lecture)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'kutime.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^dept/(?P<col_num>\d{2,4})/$', 'kutime.views.dept', name='dept'),
    url(r'^lec/(?P<dept_num>[\w|\d]+)/$', 'kutime.views.lec', name='lec'),
    url(r'^search/$', 'kutime.views.search', name='search'),
    url(r'^$', 'kutime.views.index', name='index'),
)
