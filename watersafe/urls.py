from django.conf.urls import patterns, include, url
from watersafe_site.views import Search, LearnMore, search_form, SendEmail

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    ('^$', search_form),
    ('^results$', Search),
    ('^learn_more$', LearnMore),
    ('^sendEmail$', SendEmail),    
    url(r'^motionChart$', 'watersafe_site.view.data_viz_views.motionChart'),
    # url(r'^$', 'watersafe.views.home', name='home'),
    # url(r'^watersafe/', include('watersafe.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

handler500 = 'watersafe_site.view.error_views.handler500'