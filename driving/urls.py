#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$',include('app.urls')),
                       url(r'^app/', include('app.urls')),
                       url(r'^admin/', include('admin.urls')),
)

urlpatterns += staticfiles_urlpatterns()

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)