from django.conf.urls.defaults import patterns, include
from django.contrib import admin
from quiz import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^$', 'web.views.start'),
    (r'^question/(?P<question>\d+)$', 'web.views.question'),
    (r'^highscores', 'web.views.highscores'),
    (r'^video', 'web.views.video'),
    (r'^(?P<quiz>[a-f0-9]+)-(?P<digest>.+)-.*$', 'web.views.quiz'),
)

if not settings.PRODUCTION:
    urlpatterns += patterns('', 
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'web/static'})
    )
