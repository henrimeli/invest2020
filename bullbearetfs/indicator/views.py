import datetime
import logging

from django.shortcuts import render, redirect
from django.urls import reverse,reverse_lazy

# Create your views here.
from django.http import HttpResponse, JsonResponse
from bullbearetfs.forms import contactForm

# Import Views
from django.views.generic import ListView, DetailView,View,TemplateView, FormView
from django.views.generic import CreateView, UpdateView,DeleteView

# Import Models
#from bullbearetfs.models import CustomerBasic, Portfolio, Customer
from bullbearetfs.indicator.models import EquityIndicator
# Import Forms
from .forms import EquityIndicatorInformationForm

# Get a logger instance
logger = logging.getLogger(__name__)


# Functions
def create_indicator(request):
  logger.debug("Creating a new Indicator ")

  # Coming from the Form (meaning editing). 
  # For Posts Requests only. (we are coming from the Create New Indicator)
  if request.method == 'POST':

    indicator_form = EquityIndicatorInformationForm(request.POST)

    logger.debug("Validate indicator form: {0}  ".format(indicator_form.is_valid()))
    logger.debug("Display indicator form errors. {0} ".format(indicator_form.errors.as_data()))

    if(indicator_form.is_valid()):

      indicator_saved = indicator_form.save()
      logger.debug("Indicator form was saved. {0}".format(indicator_saved.name))
      #add_other_entries(request=request,indicator=indicator_saved)

    else: 
      logger.debug('Forms are not valid. Exiting safely. TODO: Improve Errors')

    return redirect(reverse('thankyou'))

  else:
  # This is the scenario where this is completely new. We are building a new form here.
    #
    indicator_form = EquityIndicatorInformationForm(initial={'visibility':'True'})

  context = { 
      'indicator_form':indicator_form 
    }

  return render(request, 'indicator/create_indicator.html', context)


def update_indicator(request, pk):
  logger.debug("Updating the Indicator for pk= {0} ".format(pk))
  user = request.user.get_username()
  context = { 

    }

  return render(request, 'indicator/update_indicator.html', context)

#
# Deleting the given Indicator
#
def delete_indicator(request, pk):
  logger.debug("Deleting the Indicator for pk= {0} ".format(pk))
  user = request.user.get_username()
  indicator = EquityIndicator.objects.get(pk=pk)
  logger.debug("Found a match?: '{0}'".format(indicator.name))
  indicator.delete()
  
  return redirect(reverse('thankyou')) 

################################AJAX Asynchronous Functions #####################
#
# This is the Introduction Tab
#
def refresh_introduction_tab(request,pk):

  logger.debug("Indicator Introduction Tab clicked: {0}".format(pk))


  context = {

  } 

  return render(request,'indicator/tabs/introduction.html',context)

#
# This is the Information Tab
#
def refresh_indicator_information(request,pk):
  logger.debug("Indicator Information Tab Clicked for {0}".format(pk))
  user = request.user.get_username()
  indicator = EquityIndicator.objects.get(pk=pk)

  #TODO: Add functionality for Update the Form Data.
  #Only process in case of a POST ( request comes from the FORM, Submit Button).
  if request.method == 'POST': 
    logger.debug('Submit was  a POST.')
    action_selected = request.POST.get('ACTION')

    if action_selected == 'SAVE':
      information_form = EquityIndicatorInformationForm(request.POST or None, request.FILES or None,instance=indicator) 

      if information_form.is_valid():
        saved_information = information_form.save(commit=False)
        saved_information.modified_date= datetime.datetime.now()
        saved_information.save()   
        logger.debug('Information was saved.')
      else:
        logger.debug("Form was invalid. Nothing will be saved.")
      
      return redirect(reverse('thankyou')) 
    else:
      logger.debug('Action Selected is NOT save.')
      information_form = EquityIndicatorInformationForm(instance=indicator)
      context = {
         "indicator_form":information_form
      }
      return render(request,'indicator/tabs/information.html',context)
  else:
    logger.debug('Submit is NOT a post.')
    information_form = EquityIndicatorInformationForm(instance=indicator)


  context = {
    'indicator_form':information_form
  }

  return render(request,'indicator/tabs/information.html',context)

#
# This is the Validation of the Indicator
#
def validate_indicator(request,pk):
  logger.debug("Indicator Validation Clicked for {0}".format(pk))
  user = request.user.get_username()
  indicator = EquityIndicator.objects.get(pk=pk)

  valid = True
  reason = ""

  if not indicator.isValid():
    valid = False
    reason = "Unknown"
    logger.debug("Indicator isValid() returned False")
  else:
    logger.debug("Indicator isValid() returned True")

  if not indicator.isTriggered(manual_check=True):
    valid = False
    reason = "Unknown"
    logger.debug("Indicator isTriggered(manual_check) returned False")
  else:
    logger.debug("Indicator isTriggered(manual_check) returned True")

  validity = "Successful"
  
  if not valid:
    validity = " Failed "

  data = dict()
  data['title']="Validator for indicator"
  data['dialog_text']="Indicator '{0}' validity check was '{1}'.".format(indicator.name,validity)

  #logger.info("Run Validation on Indicator '{0}'. The result is {1}.".format(indicator.name, valid))
  #data1 = {
  #         'title': 'Validator for Indicator',
  #          'location': 'India',
  #          'is_active': False,
  #          'modal': True,
  #          'dialog_text':'This is the dialog text'
  #      }
  return JsonResponse(data)
  

##############################################################
# Details for all Robots. 
# 
class IndicatorDetailsPageView(DetailView):
  model = EquityIndicator
  template_name = 'indicator/details.html'
  success_url = reverse_lazy('home') 

  def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name
        return context


class IndicatorPageView(ListView):
  model = EquityIndicator
  context_object_name = 'all_indicators_list'
  template_name = 'indicator/home.html'
  paginate_by = 5

  def get_queryset(self):
    session_username = self.request.user.get_username()
    logger.debug('EquityIndicator: username from session ='+session_username)
    #person = Customer.objects.get(username=session_username)
    # customer={2}".format(dashboard.id,
    #basic = CustomerBasic.objects.get(username=session_username)
    #person = Customer.objects.get(id=basic.id)
    #print("EquityTradingRobot: {0} {1} {2}".format( basic.id,basic.first_name, person.id))
    #person = basic.basic_information.id

    #portfolio = Portfolio.objects.get(owner_id=person.id)
    #print("Portfolio: {0} ".format( portfolio.name))

    return EquityIndicator.objects.filter() 

