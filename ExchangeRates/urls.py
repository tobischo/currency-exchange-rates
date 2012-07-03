from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='/currencyRates/')),
    url(r'^currencyRates/$', 'currencyRates.views.index'),
    url(r'^currencyRates/update/$', 'currencyRates.views.update'),
    url(r'^currencyRates/loaddata/$', 'currencyRates.views.loaddata'),
    # Examples:
    # url(r'^$', 'ExchangeRates.views.home', name='home'),
    # url(r'^ExchangeRates/', include('ExchangeRates.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
