from django.urls import path
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required, permission_required

from bullbearetfs.strategy.views import StrategiesPageView,StrategyDetailsPageView

from bullbearetfs.strategy.views import create_strategy,update_strategy,delete_strategy
from bullbearetfs.strategy.views import refresh_introduction_tab,refresh_information_tab, refresh_acquisition_tab
from bullbearetfs.strategy.views import refresh_disposition_tab,refresh_orders_tab, refresh_protection_tab, validate_strategy

urlpatterns = [
    
    # This is the Home Page. Home can be reached via 'home' or ''
    url(r'^$',StrategiesPageView.as_view(),name='strategy'),
    url(r'^create_strategy/',create_strategy,name='create_strategy'),

    url(r'^(?P<pk>[0-9]+)/$',StrategyDetailsPageView.as_view(),name='strategydetails'),
    url(r'^strategy',StrategiesPageView.as_view(),name='strategy'),
    url(r'^(?P<pk>[0-9]+)/update_strategy/$',update_strategy,name='update_strategy'),
    url(r'^(?P<pk>[0-9]+)/delete_strategy/$',delete_strategy,name='delete_strategy'),
    url(r'^(?P<pk>[0-9]+)/validate-strategy/$',validate_strategy,name='validate-strategy'),
   # These are the subtabs of the Strategy refresh_strategy_tab
    url(r'^(?P<pk>[0-9]+)/refresh-introduction-tab/$',refresh_introduction_tab,name='refresh-introduction-tab'),
    url(r'^(?P<pk>[0-9]+)/refresh-information-tab/$',refresh_information_tab,name='refresh-information-tab'),
    url(r'^(?P<pk>[0-9]+)/refresh-acquisition-tab/$',refresh_acquisition_tab,name='refresh-acquisition-tab'),
    url(r'^(?P<pk>[0-9]+)/refresh-disposition-tab/$',refresh_disposition_tab,name='refresh-disposition-tab'),
    url(r'^(?P<pk>[0-9]+)/refresh-orders-tab/$',refresh_orders_tab,name='refresh-orders-tab'),
    url(r'^(?P<pk>[0-9]+)/refresh-protection-tab/$',refresh_protection_tab,name='refresh-protection-tab')
]