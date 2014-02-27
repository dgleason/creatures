from django.conf.urls import patterns, url
from creatures import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<creature_id>\d+)/$', views.cdetail, name='creature_detail'),
    url(r'^fight/$', views.cfight, name='fight'),
    url(r'^create/$', views.create, name='create'),
    url(r'^make/$', views.make, name='make'),
    url(r'^(?P<creature_id>\d+)/delete/$', views.delete, name='creature_delete'),
    url(r'^(?P<creature_id>\d+)/(?P<evolution_id>\d+)/buy/$', views.buy, name='buy_evo'),
    
)
