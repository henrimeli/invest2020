import datetime
import logging
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, get_list_or_404
from django.urls import reverse,reverse_lazy
# Create your views here.
from django.http import HttpResponse, JsonResponse
from bullbearetfs.forms import contactForm
from django.forms.formsets import formset_factory
from django.forms import modelformset_factory
from django.db.models import Q

# Import Generic Views
from django.views.generic import ListView, DetailView,View,TemplateView, FormView
from django.views.generic import CreateView, UpdateView,DeleteView


# Import Package Models
from bullbearetfs.strategy.models import EquityStrategy, AcquisitionPolicy, DispositionPolicy, OrdersManagement, PortfolioProtectionPolicy
from bullbearetfs.customer.models import CustomerBasic, Customer
from bullbearetfs.indicator.models import EquityIndicator
#from bullbearetfs.models import 

#Import the Forms
from bullbearetfs.strategy.forms import EquityStrategyForm, PortfolioProtectionForm, AcquisitionPolicyForm, DispositionPolicyForm, OrdersManagementForm
from bullbearetfs.strategy.forms import AcquisitionIndicatorsForm, BaseIndicatorConfigFormSet, StrategyBasicInformationForm

# Get a logger instance
logger = logging.getLogger(__name__)

############################Creating entries in other tables to match the Strategy Creation
#
# When a new Strategy is created, other entries need to be added to other tables.
# This function ensures that other entries are created.
# When adding new entries, want to have some default values added.
#
def add_other_entries(request, strategy):
  instance = strategy
  session_username = request.user.get_username()
  logger.debug("Primary Key= {0}.  Strategy Name= {1}. Session User= {1} ".format(instance.id,instance.name, session_username))

  #I.e. Add an entry into the tables
  #modifier = CustomerBasic.objects.get(username=session_username)

  #Acquisition Policy
  acquisition = AcquisitionPolicy(strategy=instance)
  acquisition.save()

  #Disposition Policy
  disposition = DispositionPolicy(strategy=instance)
  disposition.save()

  #Order Management Policy
  orders = OrdersManagement(strategy=instance)
  orders.save()

  #Protection Policy
  protection = PortfolioProtectionPolicy(strategy=instance)
  protection.save()

  return


############################Strategy Creation/Listing/Update and Delete ################
# delete_strategy():
# 
def delete_strategy(request, pk):
  print("Deleting the Strategy for pk= {0} ".format(pk))
  user = request.user.get_username()
  #offering = Offering.objects.get(pk=pk)
  #Get the Basic Strategy Information
  strategy = EquityStrategy.objects.get(pk=pk)
  logger.debug("Found a match?: {0}".format(strategy.name))
  #basic = get_object_or_404(EquityStrategy,pk=pk)

  # Delete references to Foreign Keys into this Strategy.
  # There should be 4 entries: Acquisition, Disposition, Orders, Portfolion
  acquisition_exists = AcquisitionPolicy.objects.filter(strategy_id = pk).exists()
  disposition_exists = DispositionPolicy.objects.filter(strategy_id = pk).exists()
  orders_exists =  OrdersManagement.objects.filter(strategy_id = pk).exists()
  p_protection_exists = PortfolioProtectionPolicy.objects.filter(strategy_id = pk).exists()

  logger.info("")
  logger.info("User: {0}  is deleting Strategy: {1} ".format(user,strategy.name))
  # Remove the Units Configuration.
  #units_config.delete()
  # Remove the Other entries: Location, ...
  #user = request.user.get_username()
  if acquisition_exists:
    AcquisitionPolicy.objects.filter(strategy_id = pk).delete()
  
  if disposition_exists:
    DispositionPolicy.objects.filter(strategy_id = pk).delete()
  
  if orders_exists:
    OrdersManagement.objects.filter(strategy_id = pk).delete()
  
  if p_protection_exists:
    PortfolioProtectionPolicy.objects.filter(strategy_id = pk).delete()
  
  #Finally Delete the Strategy
  strategy.delete()

  return redirect(reverse('thankyou'))
  #return render(request, 'strategy/delete_strategy.html', context)



############################Strategy Creation/Listing/Update and Delete ################
# update_strategy():
# 
def update_strategy(request, pk):
  print("Updating the Strategy for pk= {0} ".format(pk))
  user = request.user.get_username()
  #Create a new Units Configuration formset. One extra will be displayed. 
  strategy_instance = get_object_or_404(EquityStrategy,pk=pk)

  # After the update has been done, the User Saves the Data. 
  # Posting the Data 
  if request.method == 'POST':
    print("DEBUG: Updates have completed, saving the data for pk: {0}".format(pk))
    strategy_form = StrategyBasicInformationForm(request.POST or None, request.FILES or None, instance=strategy_instance) 
    if(strategy_form.is_valid()):
      print ( 'TODO: Clean the data before saving.:')
      strategy_instance = strategy_form.save()

    else:
      print("DEBUG: Forms Validation failed.. Strategy Form: {0} ".format(strategy_form.errors.as_data()))

    return redirect(reverse('thankyou'))

  # Coming from the "update Strategy" menu on the ListView. 
  strategy_form = StrategyBasicInformationForm(instance=strategy_instance)

  context = { 
    'strategy_form':strategy_form 
  }

  return render(request, 'strategy/update_strategy.html', context)


################################AJAX Asynchronous Functions #####################
#
# This is the Introduction Tab
#
def refresh_introduction_tab(request,pk):

  print("Introduction Tab clicked: {0}".format(pk))


  context = {

  }

  return render(request,'strategy/tabs/introduction.html',context)


# This is the Basic Information Tab
#
def refresh_information_tab(request,pk):
  logger.debug("Basic Information Tab Clicked: {0}".format(pk))
 
  #Get the Basic Strategy Information
  basic = EquityStrategy.objects.get(pk=pk)
  logger.debug("Found a match?: {0}".format(basic.name))
  #basic = get_object_or_404(EquityStrategy,pk=pk)
  
  if request.method == 'POST': 
    logger.debug ('Submit was  a POST.')
    action_selected = request.POST.get('ACTION')

    if action_selected == 'SAVE':
      information_form = StrategyBasicInformationForm(request.POST or None, request.FILES or None,instance=basic) 
      print("DEBUG: Validate form: {0} ".format(information_form.is_valid()))
      print("DEBUG: Display  form errors. {0} ".format(information_form.errors.as_data()))
      if information_form.is_valid():
        saved_information = information_form.save(commit=False)
        saved_information.modified_date= datetime.datetime.now()
        saved_information.save()   
        logger.debug ('Information was saved.')
      else:
        logger.error("Form was invalid. Nothing will be saved.")
      
      return redirect(reverse('thankyou')) 
    else:
      logger.debug ('Action Selected is NOT save.')
      information_form = StrategyBasicInformationForm(instance=basic)
      context = {
         "strategy_form":information_form
      }
      return render(request, 'strategy/tabs/information.html', context)
  else:
    logger.debug('Submit is NOT a post.')
    information_form = StrategyBasicInformationForm(instance=basic)

  context = {
    'strategy_form':information_form 
  }

  return render(request,'strategy/tabs/information.html',context)



#
# This is the Acquisition Tab
#
def refresh_acquisition_tab(request,pk):

  logger.info("Acquisition Policy Tab was clicked for {0}".format(pk))
 
  strategy = EquityStrategy.objects.get(pk=pk)
  logger.debug("Found a match?: {0}".format(strategy.name))

  acquisition = AcquisitionPolicy.objects.get(strategy_id=strategy.id)
  logger.debug("Found Acquisition Policy Match: name={0}".format(acquisition.pk))
  #acquisition = get_object_or_404(AcquisitionPolicy,pk=pk)


  if request.method == 'POST': 
    logger.debug ('Submit was  a POST.')
    action_selected = request.POST.get('ACTION')

    if action_selected == 'SAVE':
      acquisition_form = AcquisitionPolicyForm(request.POST or None, request.FILES or None,instance=acquisition) 

      if acquisition_form.is_valid():
        saved_a = acquisition_form.save(commit=False)
        saved_a.modified_date= datetime.datetime.now()
        saved_a.save()   
        logger.debug ('Acquisition Policy was saved.')
      else:
        logger.error("Acquisition Form was invalid. Nothing will be saved.")
      
      return redirect(reverse('thankyou')) 
    else:
      logger.debug ('Action Selected is not SAVE.')
      acquisition_form = AcquisitionPolicyForm(instance=acquisition)
      context = {
         'acquisition_form':acquisition_form
      }
      return render(request,'strategy/tabs/acquisition.html',context)
  else:
    logger.debug('Submit is NOT a post.')
    acquisition_form = AcquisitionPolicyForm(instance=acquisition)

  context = {
    'acquisition_form':acquisition_form
  }
  return render(request,'strategy/tabs/acquisition.html',context)

#
# This is the Disposition Tab
#
def refresh_disposition_tab(request,pk):
  logger.debug("Disposition Policy Tab was clicked for {0}".format(pk))
 
  strategy = EquityStrategy.objects.get(pk=pk)
  logger.debug("Found a match?: {0}".format(strategy.name))

  disposition = DispositionPolicy.objects.get(strategy_id=strategy.id)
  logger.debug("Found Disposition Policy Match: name={0}".format(disposition))
  #acquisition = get_object_or_404(AcquisitionPolicy,pk=pk)
  
  if request.method == 'POST': 
    logger.debug ('Submit was  a POST.')
    action_selected = request.POST.get('ACTION')

    if action_selected == 'SAVE':
      disposition_form = DispositionPolicyForm(request.POST or None, request.FILES or None,instance=disposition) 

      if disposition_form.is_valid():
        saved_a = disposition_form.save(commit=False)
        saved_a.modified_date= datetime.datetime.now()
        saved_a.save()   
        logger.debug ('Disposition Policy was saved.')
      else:
        logger.error("Disposition Form was invalid. Nothing will be saved.")
      
      return redirect(reverse('thankyou')) 
    else:
      logger.debug ('Action Selected is not SAVE.')
      disposition_form = DispositionPolicyForm(instance=disposition)
      context = {
         "disposition_form":disposition_form
      }
      return render(request,'strategy/tabs/disposition.html',context)
  else:
    logger.debug('Submit is NOT a post.')
    disposition_form = DispositionPolicyForm(instance=disposition)

  context = {
    'disposition_form':disposition_form
  }
 
  return render(request,'strategy/tabs/disposition.html',context)

# This is the Orders Management Tab
#
def refresh_orders_tab(request,pk):
  #print("Orders Management Policy  Tab Clicked: {0}".format(pk))
  logger.debug("Order Management Policy Tab was clicked for {0}".format(pk))
 
  strategy = EquityStrategy.objects.get(pk=pk)
  logger.debug("Found a match?: {0}".format(strategy.name))

  orders = DispositionPolicy.objects.get(strategy_id=strategy.id)
  logger.debug("Found Orders Management Policy Match: name={0}".format(orders))
  #acquisition = get_object_or_404(AcquisitionPolicy,pk=pk)
  
  if request.method == 'POST': 
    logger.debug ('Submit was  a POST.')
    action_selected = request.POST.get('ACTION')

    if action_selected == 'SAVE':
      strategy_form = OrdersManagementForm(request.POST or None, request.FILES or None,instance=orders) 

      if strategy_form.is_valid():
        saved_a = strategy_form.save(commit=False)
        saved_a.modified_date= datetime.datetime.now()
        saved_a.save()   
        logger.debug ('Orders Policy was saved.')
      else:
        logger.error("Orders Form was invalid. Nothing will be saved.")
      
      return redirect(reverse('thankyou')) 
    else:
      logger.debug ('Action Selected is not SAVE.')
      strategy_form = OrdersManagementForm(instance=orders)
      context = {
         "strategy_form":strategy_form
      }
      return render(request,'strategy/tabs/orders.html',context)
  else:
    logger.debug('Submit is NOT a post.')
    strategy_form = OrdersManagementForm(instance=orders)

  context = {
    'strategy_form':strategy_form
  }
  return render(request,'strategy/tabs/orders.html',context)

# This is the Portfolio Protection Tab
#
def refresh_protection_tab(request,pk):
  logger.debug("Portfolio Protection Policy Tab was clicked for {0}".format(pk))
 
  strategy = EquityStrategy.objects.get(pk=pk)
  logger.debug("Found a match?: {0}".format(strategy.name))

  p_protection = PortfolioProtectionPolicy.objects.get(strategy_id=strategy.id)
  logger.debug("Found Porfolio Protection Policy Match: name={0}".format(p_protection))
  #acquisition = get_object_or_404(AcquisitionPolicy,pk=pk)
  
  if request.method == 'POST': 
    logger.debug ('Submit was  a POST.')
    action_selected = request.POST.get('ACTION')

    if action_selected == 'SAVE':
      protection_form = PortfolioProtectionForm(request.POST or None, request.FILES or None,instance=p_protection) 

      if protection_form.is_valid():
        saved_a = protection_form.save(commit=False)
        saved_a.modified_date= datetime.datetime.now()
        saved_a.save()   
        logger.debug ('Portfolio Protection Policy was saved.')
      else:
        logger.error("Portfolio Protection Form was invalid. Nothing will be saved.")
      
      return redirect(reverse('thankyou')) 
    else:
      logger.debug ('Action Selected is not SAVE.')
      protection_form = PortfolioProtectionForm(instance=p_protection)
      context = {
         "protection_form":protection_form
      }
      return render(request,'strategy/tabs/protection.html',context)
  else:
    logger.debug('Submit is NOT a post.')
    protection_form = PortfolioProtectionForm(instance=p_protection)

  context = {
    'protection_form':protection_form
  }
  return render(request,'strategy/tabs/protection.html',context)


# Functions
def create_strategy(request):
  logger.debug("Create a new Strategy ")
  user = request.user.get_username()

  # Coming from the Form (meaning editing). 
  # For Posts Requests only. (we are coming from the Create New Strategy)
  if request.method == 'POST':

    strategy_form = EquityStrategyForm(request.POST)

    logger.debug("Validate strategy form: {0}  ".format(strategy_form.is_valid()))
    logger.debug("Display strategy form errors, if any. {0} ".format(strategy_form.errors.as_data()))

    if(strategy_form.is_valid()):
      strategy_saved = strategy_form.save()
      logger.debug("Strategy form was saved. {0}".format(strategy_saved.name))
      add_other_entries(request=request,strategy=strategy_saved)
    else: 
      logger.debug('Strategy Forms is not valid. Exiting safely. TODO: Improve Errors')

    return redirect(reverse('thankyou'))

  else:
  # This is the scenario where this is completely new. We are building a new form here.
    #
    strategy_form = EquityStrategyForm(initial={'visibility':'True'})

  context = { 
      'strategy_form':strategy_form 
    }

  return render(request, 'strategy/create_strategy.html', context)


#
# This is the Validation of the Strategy
#
def validate_strategy(request,pk):
  logger.debug("Strategy Validation Clicked for {0}".format(pk))
  user = request.user.get_username()
  strategy = EquityStrategy.objects.get(pk=pk)
  valid = True
  reason = ""
  if strategy.owner == None:
    valid=False
    reason="Strategy Owner is not set."

  validity = "Successful"
  
  if not valid:
    validity = " Failed "

  data = dict()
  data['title']="Validator for strategy"
  data['dialog_text']="Strategy '{0}' validity check was '{1}'.".format(strategy.name,validity)

  return JsonResponse(data)


##############################################################
# Detailing all Strategy. 
# 
class StrategyDetailsPageView(DetailView):
  model = EquityStrategy
  template_name = 'strategy/details.html'
  success_url = reverse_lazy('home') 

  def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name
        return context

##############################################################
# List all Strategies. 
# 
class  StrategiesPageView(ListView):
  model = EquityStrategy
  context_object_name = 'all_strategies_list'
  template_name = 'strategy/home.html'
  paginate_by = 5

  def get_queryset(self):
    session_username = self.request.user.get_username()
    print('InvestmentStrategy: username from session ='+session_username)
    #person = Customer.objects.get(username=session_username)
    #person = CustomerBasic.objects.get(username=session_username)

    return EquityStrategy.objects.filter() 
