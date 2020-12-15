from django.urls import path
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required, permission_required

from .views import AboutPageView, EducationPageView, HelpPageView, FAQPageView



urlpatterns = [
    #Foundation Pages. Basic and Non-Dynamic Content
    url(r'^about/',AboutPageView.as_view(),name='about'),
    url(r'^education/',EducationPageView.as_view(),name='education'),
    url(r'^help/',HelpPageView.as_view(),name='help'),   
    url(r'^faq/',FAQPageView.as_view(),name='faq'),   
]