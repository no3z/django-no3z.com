from django.conf.urls.defaults import *
from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^$', include('no3z_www.main.urls')),
   (r'^music', 'no3z_www.main.views.music'),    
      (r'^news', 'no3z_www.main.views.news'),    
   (r'^getfeeds', 'no3z_www.main.views.getfeeds'),    
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/filebrowser/', include('filebrowser.urls')),
    
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    from django.views.static import serve
    _media_url = settings.MEDIA_URL
    if _media_url.startswith('/'):
        _media_url = _media_url[1:]
        urlpatterns += patterns('', (r'^%s(?P<path>.*)$' % _media_url, serve,
                                     {'document_root': settings.MEDIA_ROOT}))
        del(_media_url, serve)
