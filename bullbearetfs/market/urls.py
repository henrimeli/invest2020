from django.urls import path
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required, permission_required

from .views import MarketPageView, MarketDetailsPageView
from .views import create_market, update_market, delete_market
from .views import refresh_market_providers, refresh_market_information, refresh_market_symbols, refresh_market_intelligence

urlpatterns = [
    
    # This is the Home Page for Market Data
    url(r'^$',MarketPageView.as_view(),name='market'),
  
    url(r'^create_market/',create_market,name='create_market'),
    url(r'^(?P<pk>[0-9]+)/$',MarketDetailsPageView.as_view(),name='marketdetails'),
    url(r'^market',MarketPageView.as_view(),name='market'),
    url(r'^(?P<pk>[0-9]+)/update/$',update_market,name='update'),
    url(r'^(?P<pk>[0-9]+)/delete/$',delete_market,name='delete'),

   # These are the subtabs of the Market providers
   #url(r'^(?P<pk>[0-9]+)/refresh-market-providers/$',refresh_market_providers,name='refresh-market-providers'),
   url(r'^refresh-market-providers/$',refresh_market_providers,name='refresh-market-providers'),
   url(r'^refresh-market-symbols/$',refresh_market_symbols,name='refresh-market-symbols'),
   url(r'^refresh-market-information/$',refresh_market_information,name='refresh-market-information'),
   url(r'^refresh-market-intelligence/$',refresh_market_intelligence,name='refresh-market-intelligence')

]