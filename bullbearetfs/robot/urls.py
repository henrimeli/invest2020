from django.urls import path
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required, permission_required

from .views import RobotsPageView, RobotsDetailsPageView
from .views import create_robot, update_robot, delete_robot,refresh_robot_activate
from .views import refresh_robot_information, refresh_robot_introduction,refresh_robot_activity,refresh_robot_budget,refresh_robot_projections
from .views import refresh_robot_strategy, refresh_robot_sentiments,refresh_robot_symbols,refresh_robot_transactions

urlpatterns = [
    
    # This is the Home Page for Robots
    url(r'^$',RobotsPageView.as_view(),name='robot'),
  
    url(r'^create_robot/',create_robot,name='create_robot'),

    url(r'^(?P<pk>[0-9]+)/$',RobotsDetailsPageView.as_view(),name='robotdetails'),
    url(r'^robot',RobotsPageView.as_view(),name='robot'),
    url(r'^(?P<pk>[0-9]+)/update/$',update_robot,name='update'),
    url(r'^(?P<pk>[0-9]+)/delete/$',delete_robot,name='delete'),

   # These are the subtabs of the Robot refresh_introduction_tab
    url(r'^(?P<pk>[0-9]+)/refresh-robot-introduction/$',refresh_robot_introduction,name='refresh-robot-introduction'),
    url(r'^(?P<pk>[0-9]+)/refresh-robot-information/$',refresh_robot_information,name='refresh-robot-information'),
    url(r'^(?P<pk>[0-9]+)/refresh-robot-activity/$',refresh_robot_activity,name='refresh-robot-activity'),
    url(r'^(?P<pk>[0-9]+)/refresh-robot-budget/$',refresh_robot_budget,name='refresh-robot-budget'),    
    url(r'^(?P<pk>[0-9]+)/refresh-robot-strategy/$',refresh_robot_strategy,name='refresh-robot-strategy'),    
    url(r'^(?P<pk>[0-9]+)/refresh-robot-sentiments/$',refresh_robot_sentiments,name='refresh-robot-sentiments'),    
    url(r'^(?P<pk>[0-9]+)/refresh-robot-symbols/$',refresh_robot_symbols,name='refresh-robot-symbols'),
    url(r'^(?P<pk>[0-9]+)/refresh-robot-transactions/$',refresh_robot_transactions,name='refresh-robot-transactions'),
    url(r'^(?P<pk>[0-9]+)/refresh-robot-projections/$',refresh_robot_projections,name='refresh-robot-projections'),    
    url(r'^(?P<pk>[0-9]+)/refresh-robot-activate/$',refresh_robot_activate,name='refresh-robot-activate'),
    #url(r'^(?P<pk>[0-9]+)/refresh-acquisition-tab/$',refresh_acquisition_tab,name='refresh-acquisition-tab'),
    #url(r'^(?P<pk>[0-9]+)/refresh-disposition-tab/$',refresh_disposition_tab,name='refresh-disposition-tab'),
    #url(r'^(?P<pk>[0-9]+)/refresh-orders-tab/$',refresh_orders_tab,name='refresh-orders-tab'),
    #url(r'^(?P<pk>[0-9]+)/refresh-protection-tab/$',refresh_protection_tab,name='refresh-protection-tab')
]