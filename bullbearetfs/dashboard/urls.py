from django.urls import path
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required, permission_required

from .views import DashboardPageView, DashboardDetailsPageView

from .views import create_dashboard, update_dashboard, delete_dashboard, refresh_dashboard_information

urlpatterns = [
    
    # This is the Home Page. Home can be reached via 'home' or ''
    url(r'^$',DashboardPageView.as_view(),name='dashboard'),

    url(r'^(?P<pk>[0-9]+)/$',DashboardDetailsPageView.as_view(),name='dashboarddetails'),
    url(r'^dashboard',DashboardPageView.as_view(),name='dashboard'),
    url(r'^(?P<pk>[0-9]+)/update/$',update_dashboard,name='update'),
    url(r'^(?P<pk>[0-9]+)/delete/$',delete_dashboard,name='delete'),

    # These are the subtabs of the Market providers
    url(r'^refresh-dashboard-information/$',refresh_dashboard_information,name='refresh-dashboard-information'),
   #url(r'^refresh-dashboard-symbols/$',refresh_market_symbols,name='refresh-market-symbols'),

]