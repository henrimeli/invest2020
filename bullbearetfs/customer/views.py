from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from bullbearetfs.forms import contactForm

# Import Views
from django.views.generic import ListView, DetailView,View,TemplateView, FormView
from django.views.generic import CreateView, UpdateView,DeleteView

#TODO: Move me later
from bullbearetfs.market.models import WebsiteContactPage
from bullbearetfs.customer.models import CustomerProfile
from bullbearetfs.models import Notifications
from bullbearetfs.basic.models import Settings
from bullbearetfs.forms import ContactForm 

#Shows the User Profile Information on a Template Form
class ProfilePageView (TemplateView):
  model = CustomerProfile
  template_name='index.html'

#Shows the index.html
class SettingsPageView (TemplateView):
  model = Settings
  template_name='index.html'

#Shows the index.html
class NotificationsPageView (TemplateView):
  model = Notifications
  template_name='index.html'

#The Thank You page
class ThankYouPageView(TemplateView):
  template_name = 'basic/thankyou.html'

#Contact Page View
# https://docs.djangoproject.com/en/2.1/topics/forms/
class ContactPageView(TemplateView):
  form_class=ContactForm
  template_name = 'basic/contact.html'
  model = WebsiteContactPage

  def get_success_url (self):
    return reverse('thankyou')

# TODO: Remove me
def create_profile(request):
    return HttpResponse('Hello, World! This is the Stock Market Application for siriusinnovate.com team. ')
