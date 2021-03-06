from django.conf.urls import patterns, include, url
from watersafe_site.views import Search, LearnMore, search_form, SendTweet, \
    AboutUs, PWSFacts, SearchByCounty

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    ('^$', search_form),
    ('^results$', Search),
    ('(?P<county>[A-Za-z ]*)/(?P<state>[A-Za-z]{2})/violations$', SearchByCounty),
    ('^sendTweet$', SendTweet),
    ('^aboutus$', AboutUs),
    ('^pwsfacts$', PWSFacts),    
    url(r'^historicalMotionChart', 'watersafe_site.view.data_viz_views.historicalMotionChart'),
    # url(r'^$', 'watersafe.views.home', name='home'),
    # url(r'^watersafe/', include('watersafe.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

handler500 = 'watersafe_site.view.error_views.handler500'