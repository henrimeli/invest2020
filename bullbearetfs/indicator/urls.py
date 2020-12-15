from django.urls import path
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required, permission_required

from .views import IndicatorPageView, IndicatorDetailsPageView
from .views import create_indicator, update_indicator, delete_indicator, refresh_introduction_tab 
from .views import validate_indicator, refresh_indicator_information

urlpatterns = [    
    # This is the Home Page for Indicators
    url(r'^$',IndicatorPageView.as_view(),name='indicator'),
  
    url(r'^create_indicator/',create_indicator,name='create_indicator'),
    url(r'^indicator',IndicatorPageView.as_view(),name='indicator'),
    url(r'^(?P<pk>[0-9]+)/$',IndicatorDetailsPageView.as_view(),name='indicatordetails'),
    url(r'^(?P<pk>[0-9]+)/update-indicator/$',update_indicator,name='update-indicator'),
    url(r'^(?P<pk>[0-9]+)/delete-indicator/$',delete_indicator,name='delete-indicator'),
    url(r'^(?P<pk>[0-9]+)/validate-indicator/$',validate_indicator,name='validate-indicator'),

   # These are the subtabs of the Strategy refresh_indicator_tab
   url(r'^(?P<pk>[0-9]+)/refresh-introduction-tab/$',refresh_introduction_tab,name='refresh-introduction-tab'),
   url(r'^(?P<pk>[0-9]+)/refresh-indicator-information/$',refresh_indicator_information,name='refresh-indicator-information'),

]