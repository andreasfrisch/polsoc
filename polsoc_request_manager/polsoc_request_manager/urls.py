from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$', "polsoc_request_manager.views.home", name="home"),
    url(r'^api/serveFile/(\d+)/', 'polsoc_request_manager.views.serveFile'),
    url(r'^api/getNextInQueue/', 'polsoc_request_manager.views.getNextInQueue'),
    url(r'^api/markAsCompleted/(\d+)/', 'polsoc_request_manager.views.markAsCompleted'),
    url(r'^api/getDownloadedRequests/', 'polsoc_request_manager.views.getDownloadedRequests'),
    url(r'^api/markAsRemoved/(\d+)/', 'polsoc_request_manager.views.markAsRemoved'),
    url(r'^admin/', include(admin.site.urls)),

)
