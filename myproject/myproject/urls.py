from django.conf.urls import patterns, include, url
from django.contrib import admin
from myproject import views
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'myproject.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', views.index, name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^creatures/', include('creatures.urls', namespace="creatures")),
    url(r'^accounts/', include('accounts.urls', namespace="accounts")),

#    url(r'^login/$', 'django.contrib.auth.views.login'),
#    url(r'^logout/$', 'django.contrib.auth.views.logout'),
#    url(r'^register/$', 'creatures.views.register'),

)
