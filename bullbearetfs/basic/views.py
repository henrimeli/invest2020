from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from bullbearetfs.forms import contactForm

# Import Views
from django.views.generic import ListView, DetailView,View,TemplateView, FormView
from django.views.generic import CreateView, UpdateView,DeleteView


class HelpPageView(TemplateView):
  """
      This class is responsible for the Help View
  """
  template_name = 'basic/help.html'

class EducationPageView(TemplateView):
  """
      This class is responsible for the Education View
  """
  template_name = 'basic/education.html'

class FAQPageView(TemplateView):
  """
      This class is responsible for the FAQ View
  """
  template_name = 'basic/faq.html'

class AboutPageView(TemplateView):
  """
      This class is responsible for the About View
  """
  template_name = 'basic/about.html'
