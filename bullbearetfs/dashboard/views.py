from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from bullbearetfs.forms import contactForm

# Import Views
from django.views.generic import ListView, DetailView,View,TemplateView, FormView
from django.views.generic import CreateView, UpdateView, DeleteView

from .models import Dashboard
from .forms import DashboardInformationForm 

# Updating Dashboard information
def update_dashboard(request,pk):
  return

# Deleting Dashboard information
def delete_dashboard(request,pk):
  return

# Creating a new Dashboard
def create_dashboard(request, pk):
  print("Create the Dashboard for pk= {0} ".format(pk))
  user = request.user.get_username()
  context = { 

    }

  return render(request, 'dashboard/create_dashboard.html', context)



def refresh_dashboard_information(request):
  print("Refresh Dashboard Information for user: {0}  ".format(request.user.get_username()))

  if request.method == 'POST':
  	dashboard_form = DashboardInformationForm(request.POST)
  else:
  	dashboard_form = DashboardInformationForm()

  context = dashboard_form.contextData()

  return render(request, 'dashboard/tabs/information.html', context)



#Shows the index.html
class DashboardPageView (TemplateView):
  model = Dashboard
  template_name='dashboard/home.html'

# TODO: I question the below class !!!
class DashboardDetailsPageView(DetailView):
  model = Dashboard
  template_name='dashboard/home.html'
