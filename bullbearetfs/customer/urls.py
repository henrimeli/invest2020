from django.urls import path
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required, permission_required

from .views import ProfilePageView, SettingsPageView, NotificationsPageView, ThankYouPageView, ContactPageView

from .views import create_profile


urlpatterns = [
    
    # This is the Home Page. Home can be reached via 'home' or ''
    url(r'^$',ProfilePageView.as_view(),name='profile'),
    url(r'^create_profile/',create_profile,name='create_profile'),

        # Customer Communication
    url(r'^contact/',ContactPageView.as_view(),name='contact'),
    url(r'^thankyou/',ThankYouPageView.as_view(),name='thankyou'),   

    #Customer Management
    url(r'^profile/',login_required(ProfilePageView.as_view()),name='profile'),
    url(r'^settings/',login_required(SettingsPageView.as_view()),name='settings'),
    url(r'^notifications/',login_required(NotificationsPageView.as_view()),name='notifications'),


]