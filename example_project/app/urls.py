from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.defaults import patterns, url, include
from django.views.generic import TemplateView
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

from django.contrib.auth.views import password_reset

urlpatterns = i18n_patterns('',
        (r'^exports/', include('data_exports.urls', namespace='data_exports')),
        (r'^admin/', include(admin.site.urls)),
        (r'^', include('signalbox.urls')),
        (r'^accounts/', include('registration.backends.simple.urls')),
        (r'^', include('cms.urls')),        
        (r'^reset/password/$', password_reset, {}),
        (r'^robots\.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
)

# # if settings.DEBUG or settings.OFFLINE:
# urlpatterns = urlpatterns + patterns('',
#     (r'^media/(?P<path>.*)$', 'django.views.static.serve',
#         {'document_root': settings.MEDIA_ROOT}),
# )
