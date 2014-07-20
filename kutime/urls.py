from django.conf.urls import patterns, include, url

from django.contrib import admin

from models.sugang import *
admin.autodiscover()
admin.site.register(College)
admin.site.register(Department)
admin.site.register(Lecture)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'kutime.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
