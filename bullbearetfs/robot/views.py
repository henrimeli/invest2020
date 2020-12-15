import datetime
import logging
from django.utils import timezone

from googlefinance import getQuotes

from django.shortcuts import render, redirect
from django.urls import reverse,reverse_lazy


# Create your views here.
from django.http import HttpResponse
from bullbearetfs.forms import contactForm

# Import Views
from django.views.generic import ListView, DetailView,View,TemplateView, FormView
from django.views.generic import CreateView, UpdateView,DeleteView

# Import Models.
from bullbearetfs.customer.models import CustomerBasic
from bullbearetfs.robot.symbols.models import RobotEquitySymbols, BullBearETFData
from bullbearetfs.robot.activitysentiments.models import RobotActivityWindow, EquityAndMarketSentiment
from bullbearetfs.models import EquityTradingRobot, Customer
from bullbearetfs.robot.budget.models import RobotBudgetManagement, Portfolio
from bullbearetfs.executionengine.models import ETFPairBackTestRobotExecutionEngine
from bullbearetfs.models import EquityTradingData
from bullbearetfs.strategy.models import OrdersManagement
# Import Forms
from .forms import EquityTradingRobotForm, RobotInformationForm, RobotActivityWindowForm, RobotBudgetManagementForm,RobotEquitySymbolsForm
from .forms import EquityAndMarketSentimentForm, RobotNotificationForm, RobotTradingSecurityForm
from bullbearetfs.strategy.forms import  OrdersManagementForm
from bullbearetfs.robot.forms import ETFAndReversePairRobotCreationForm, ETFAndReversePairRobotInformationForm
from bullbearetfs.robot.forms import InTransitionRoundTripForm, StableRoundTripForm, CompletedRoundTripForm,RobotExecutionCreationForm

from bullbearetfs.robot.models import ETFAndReversePairRobot
# Get a logger instance
logger = logging.getLogger(__name__)

############################Creating entries in other tables to match the Robot Creation
#
# When a new Robot is created, other entries need to be added to other tables.
# This function ensures that other entries are created.
# When adding new entries, want to have some default values added.
#
def add_other_entries(request, robot):
  instance = robot
  session_username = request.user.get_username()

  #print ("Primary Key= {0}.  Strategy Name= {1}. Session User= {1} ".format(instance.id,instance.name, session_username))

  #I.e. Add an entry into the tables
  #modifier = CustomerBasic.objects.get(username=session_username)

   #ActivityWindow
  activity = RobotActivityWindow( robot=robot)
  activity.save()

  #Budget Management Policy
  budget = RobotBudgetManagement(robot=robot)
  budget.save()

  #EquitySentimentScale
  #esentiment=EquitySentimentScale(robot=robot)
  #esentiment.save()

  #Equity & Market Sentiment
  sentiment = EquityAndMarketSentiment(robot=robot)
  sentiment.save()

  #symbols = RobotEquitySymbols(robot=robot)
  #symbols.save()

  return


############################Robots Creation/Listing/Update and Delete ################
#
# Creating a new Robot.
#
def create_robot_works(request):
  print("Creating a new Robot ")

  # Coming from the Form (meaning editing). 
  # For Posts Requests only. (we are coming from the Create New Strategy)
  if request.method == 'POST':

    robot_form = EquityTradingRobotForm(request.POST)

    print("DEBUG: Validate robot form: {0}  ".format(robot_form.is_valid()))
    print("DEBUG: Display robot form errors. {0} ".format(robot_form.errors.as_data()))

    if(robot_form.is_valid()):

      robot_saved = robot_form.save()

      print("Robot form was saved. {0}".format(robot_saved.name))

      add_other_entries(request=request,robot=robot_saved)

    else: 
      print('Forms are not valid. Exiting safely. TODO: Improve Errors')

    return redirect(reverse('thankyou'))

  else:
  # This is the scenario where this is completely new. We are building a new form here.
    #
    robot_form = EquityTradingRobotForm(initial={'visibility':'True'})

  context = { 
      'robot_form':robot_form 
   }

  return render(request, 'robot/create_robot.html', context)

def delete_robot_works(request, pk):
  print("Deleting the Robot for pk= {0} ".format(pk))
  user = request.user.get_username()

  context = { 
    #'formset':units_config_formset, 
    #'offering_form':offering_form 
  }

  return render(request, 'robot/delete_robot.html', context)


############################Robot Creation/Listing/Update and Delete ################
# update_robot():
# 
def update_robot_works(request, pk):
  print("Updating the Strategy for pk= {0} ".format(pk))
  user = request.user.get_username()
  #Create a new Units Configuration formset. One extra will be displayed. 
  strategy_form = EquityRobotForm(instance=robot_instance)

  context = { 
    'robot_form':robot_form 
  }

  return render(request, 'robot/update_robot.html', context)

############################Refresh Robot Functions ################
# refresh_robot_introduction(): DELETE ME. NOT USED.
#
def refresh_robot_introduction(request):

  print("Robot Introduction ")

  info_data_form = RobotInformationForm()

  context = {
    'information_form':information_form
  }

  return render(request,'robot/tabs/information.html',context)

# Refresh Robot Information 
def refresh_robot_information_works(request,pk):
  logger.debug("Robot Information {0}".format(pk))
  user = request.user.get_username()
  basic = EquityTradingRobot.objects.get(pk=pk)

  robot_notication_form = RobotNotificationForm()
  trading_security_form = RobotTradingSecurityForm()
  #TODO: Add functionality for Update the Form Data.
  #Only process in case of a POST ( request comes from the FORM, Submit Button).
  if request.method == 'POST': 
    logger.debug('Submit was  a POST.')
    action_selected = request.POST.get('ACTION')

    if action_selected == 'SAVE':
      information_form = EquityTradingRobotForm(request.POST or None, request.FILES or None,instance=basic) 

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
      information_form = EquityTradingRobotForm(instance=basic)
      context = {
         "information_form":information_form
      }
      return render(request,'robot/tabs/information.html',context)
  else:
    logger.debug('Submit is NOT a post.')
    information_form = EquityTradingRobotForm(instance=basic)

  context = {
    'information_form':information_form
  }

  return render(request,'robot/tabs/information.html',context)

############################################################
# Refresh Robot Activity 
# Load and Update Robot Activity information into the UI
#
def refresh_robot_activity(request,pk):
  print("Robot Activity Window Form {0}".format(pk))
 
  #Get the Trading Robot matching Object
  robot = ETFAndReversePairRobot.objects.get(pk=pk)
  print("Found a match?: {0}".format(robot.name))
  
  activity = RobotActivityWindow.objects.get(pair_robot_id=robot.id)
  sentiment = EquityAndMarketSentiment.objects.get(pair_robot_id=robot.id)

  sentiment_window = dict()
  sentiment_window['label']='Sentiment Duration Window:'
  sentiment_window['max_hold_time']= robot.max_hold_time
  activity_dates = dict()
  activity_dates['date_today_label']='Today is:'
  activity_dates['date_today']=datetime.datetime.now()
  activity_dates['market_open_label']='Market opens Today(TODO):'
  activity_dates['market_open']='9:30AM'
  activity_dates['market_close_label']='Market closes Today(TODO):'
  activity_dates['market_close']='4:00PM'
  activity_dates['market_timezone_label']=' Timezone Information:'
  activity_dates['market_timezone']='US NY Timezone'
    
  if request.method == 'POST': 
    print ('Submit was  a POST.')
    action_selected = request.POST.get('ACTION')

    if action_selected == 'SAVE':
      activity_form = RobotActivityWindowForm(request.POST or None, request.FILES or None,instance=activity) 
      sentiment_form = EquityAndMarketSentimentForm(request.POST or None, request.FILES or None,instance=sentiment) 

      if activity_form.is_valid() and sentiment_form.is_valid():
        saved_activity = activity_form.save(commit=False)
        saved_sentiment = sentiment_form.save(commit=False)
        saved_activity.modified_date= datetime.datetime.now()
        saved_sentiment.modified_date= datetime.datetime.now()
        saved_activity.save()   
        saved_sentiment.save()   
        print ('Activity & Sentiments were saved.')
      else:
        print("Activity Form and/or Sentiment Form was(were) invalid. Nothing will be saved.")
      
      return redirect(reverse('thankyou')) 
    else:
      print ('Action Selected is NOT save.')
      activity_form = RobotActivityWindowForm(instance=activity)
      sentiment_form = EquityAndMarketSentimentForm(instance=sentiment)
      context = {
         "activity_form":activity_form,
         "sentiment_form":sentiment_form,
         "sentiment_window":sentiment_window,
         "activity_dates":activity_dates
      }
      return render(request,'robot/tabs/activity.html',context)
  else:
    print('Submit is NOT a post.')
    activity_form = RobotActivityWindowForm(instance=activity)

  context = {
    "activity_form":activity_form,
    "sentiment_form":sentiment_form,
    "sentiment_window":sentiment_window,
    "activity_dates":activity_dates
  }
  return render(request,'robot/tabs/activity.html',context)

#
# Refresh Robot Budget
#
def refresh_robot_budget(request,pk):
  logger.debug("Robot Budget Management {0}".format(pk))

  user = request.user.get_username()
  robot = ETFAndReversePairRobot.objects.get(pk=pk)

  budget = RobotBudgetManagement.objects.get(pair_robot_id=robot.id)
  portfolio = robot.portfolio

  #logger.info("Portfolio Name: {0} {1} {2} {3}".format(portfolio.name,portfolio.initial_cash_funds,
  #                                         portfolio.current_cash_funds,portfolio.max_robot_fraction))
  #porfolio_cash=robot.getCurrentPortfolioCashPosition()
  #logger.info("Calculated from Robot: Initial Budget: {0}".format(robot.getInitialBudget()))
  #basic = get_object_or_404(ETFAndReversePairRobot,pk=pk)
  #budget.portfolio_initial_budget = robot.getInitialRobotBudget()
  #budget.current_cash_position = robot.getCurrentRobotCashPosition()

  if request.method == 'POST': 
    logger.debug('Submit was  a POST.')
    action_selected = request.POST.get('ACTION')

    if action_selected == 'SAVE':
      budget_form = RobotBudgetManagementForm(request.POST or None, request.FILES or None,instance=budget) 

      if budget_form.is_valid():
        saved_budget = budget_form.save(commit=False)
        saved_budget.modified_date= datetime.datetime.now()
        saved_budget.save()   
        logger.debug('Budget was saved.')
      else:
        logger.error("Budget Form was invalid. Nothing will be saved.")
      
      return redirect(reverse('thankyou')) 
    else:
      logger.debug('Action Selected is NOT save.')
      budget_form = RobotBudgetManagementForm(instance=budget)
      context = {
         "budget_form":budget_form
      }
      return render(request,'robot/tabs/budget.html',context)
  else:
    logger.debug('Submit is NOT a post.')
    budget_form = RobotBudgetManagementForm(instance=budget)

  context = {
    'budget_form':budget_form
  }
  return render(request,'robot/tabs/budget.html',context)

#
#
# 
def refresh_robot_sentiments(request,pk):
  logger.debug("Robot Sentiments {0}".format(pk))

  user = request.user.get_username()
  robot = ETFAndReversePairRobot.objects.get(pk=pk)

  sentiment = EquityAndMarketSentiment.objects.get(pair_robot_id=robot.id)

  logger.debug("Market Sentiments found? Market Name={0} ".format(sentiment.name))
  if request.method == 'POST': 
    logger.debug('Submit was  a POST.')
    action_selected = request.POST.get('ACTION')

    if action_selected == 'SAVE':
      sentiment_form = EquityAndMarketSentimentForm(request.POST or None, request.FILES or None,instance=sentiment) 
      #e_sentiment_form = EquitySentimentScaleForm(request.POST or None, request.FILES or None,instance=e_sentiment) 

      if sentiment_form.is_valid():
        saved = sentiment_form.save(commit=False)
        saved.modified_date = datetime.datetime.now()
        saved.save()
        logger.debug("Market & Equity Sentiments were saved. Sentiment Name={0}".format(saved.name))
      else:
        logger.error("Market & Equity Sentiment Form were invalid. Nothing will be saved.")
      
      return redirect(reverse('thankyou')) 
    else:
      logger.debug('Action Selected is NOT save.')
      sentiment_form = EquityAndMarketSentimentForm(instance=sentiment)
      context = {
         "sentiment_form":sentiment_form,
      }
      return render(request,'robot/tabs/sentiments.html',context)
  else:
    logger.debug('Submit is NOT a post.')
    sentiment_form = EquityAndMarketSentimentForm(instance=m_sentiment)

  context = {
    'sentiment_form':sentiment_form,
    #'equity_sentiment_form':e_sentiment_form
  }
  return render(request,'robot/tabs/sentiments.html',context)

#
#  Robot Symbols from Stable, InTransaction and Completed
# 
def refresh_robot_symbols(request,pk): 
  logger.debug("Robot Equity Symbols {0}".format(pk))

  user = request.user.get_username()
  robot = ETFAndReversePairRobot.objects.get(pk=pk)
  symbols = robot.symbols
  #print("symbols {0}".format(symbols.getBullishSymbol()))
  pair = dict()
  pair['bull_symbol']=symbols.getBullishSymbol()
  pair['bear_symbol']=symbols.getBearishSymbol()
  pair['etf_symbol']=symbols.getSymbol()

  hour_data = RobotEquitySymbols.getHourlyEquitiesData(pair=pair)
  today_data = RobotEquitySymbols.getTodayEquitiesData(pair=pair)
  week_data = RobotEquitySymbols.getWeekEquitiesData(pair=pair)
  two_weeks_data = RobotEquitySymbols.getTwoWeeksEquitiesData(pair=pair)
  three_weeks_data = RobotEquitySymbols.getThreeWeeksEquitiesData(pair=pair)
  four_weeks_data = RobotEquitySymbols.getFourWeeksEquitiesData(pair=pair)
  
  symbol_form = RobotEquitySymbolsForm(user_name=user)

  context = {
    'all_symbols':pair,
    'hour_data':hour_data,
    'today_data':today_data,
    'week_data':week_data,
    'two_weeks_data':two_weeks_data,
    'three_weeks_data':three_weeks_data,
    'four_weeks_data':four_weeks_data

  }
  return render(request,'robot/tabs/equities.html',context)

#
#  Robot Transactions from Stable, InTransaction and Completed
# 
def refresh_robot_transactions(request,pk):
  print("Robot Transactions ")
  user = request.user.get_username()
  robot = ETFAndReversePairRobot.objects.get(pk=pk)

  completed_data = robot.getCompletedReport()
  completed_form = CompletedRoundTripForm(roundtrip_data=completed_data,user_name=user)

  in_transition_data = robot.getInTransitionReport()
  in_transition_form = InTransitionRoundTripForm(roundtrip_data=in_transition_data,user_name=user)

  stable_data = robot.getStableReport()
  stable_form = StableRoundTripForm(roundtrip_data=stable_data,user_name=user)
  
  context_completed = completed_form.contextData()
  context_stable = stable_form.contextData()
  context_in_transition = in_transition_form.contextData()

  context = {
    'stable_form':context_stable,
    'in_transition_form':context_in_transition,
    'completed_form':context_completed
  }
  #print("\n\nHENRI: {0}".format(context))
  return render(request,'robot/tabs/transactions.html',context)

#
#
#
#
def run_robot_execution(robot,form_data,request):
  return True 


#
#  Robot Projections from the various
# 
def refresh_robot_projections(request,pk):
  print("Robot Backtest Execution ... ")

  logger.debug("Robot Backtest Execution {0} method = {1}".format(pk,request.method))

  user = request.user.get_username()
  robot = ETFAndReversePairRobot.objects.get(pk=pk)

  if request.method == 'POST': 
    logger.info('HENRI: Submit was  a POST.')
    action_selected = request.POST.get('ACTION')
    logger.info("HENRI: Submit was  a POST.  {}".format(action_selected))
    if action_selected == 'RUN':
      logger.info(" RUN was selected.".format())
      execution_form = RobotExecutionCreationForm(request.POST or None, request.FILES or None) 
      print("DEBUG: Validate Robot Backtest Execution form: {0}  ".format(execution_form.is_valid()))
      print("DEBUG: Display Robot Backtest Execution form errors. {0} ".format(execution_form.errors.as_data()))

      if execution_form.is_valid():
        saved = execution_form.save(commit=False)
        saved.save()
        logger.debug("Execution Form Executed ={0}".format(saved.execution_name))
        engine = ETFPairBackTestRobotExecutionEngine(robot=robot,request=request,backtest_input_data=saved)
        result = engine.executeBackTest() #run_robot_execution(form_data=saved,robot=robot,request=request)
      else:
        logger.error("Execution Form invalid. Nothing will be saved.")
      
      return redirect(reverse('thankyou')) 
    else:
      execution_form = RobotExecutionCreationForm()
      logger.info("Action Selected is NOT save. ")
      context = {
         'execution_form':execution_form
      }
      return  render(request,'robot/tabs/projections.html',context)
  else:
    logger.debug('Submit is NOT a post.')
    execution_form = RobotExecutionCreationForm()

  context = {
         'execution_form':execution_form
  }
  return render(request,'robot/tabs/projections.html',context)


def refresh_robot_strategy(request,pk):
  print("Robot Strategy Form ")
  robot = RobotEquitySymbols.objects.filter(pk=pk)
  #strategy_form = RobotStrategySelectionForm(instance=robot)
  information_form = ETFAndReversePairRobot(instance=robot)


  context = {
    'symbols_form':symbols_form,
    'all_symbols_lists':all_symbols_lists
  }
  return render(request,'robot/tabs/strategy.html',context)

def refresh_robot_activate(request,pk):
  print("Refresh Robot Activigy: Modifying {0}".format(pk))
  robot = ETFAndReversePairRobot.objects.get(pk=pk)
  robot.toggleActive()

  all_robots_list=ETFAndReversePairRobot.objects.filter() 
  context = {
    'all_robots_list':all_robots_list
  }
  return render(request,'robot/home.html',context)


##############################################################
# Details for all Robots. 
# 
class OldRobotsDetailsPageView(DetailView):
  model = EquityTradingRobot
  template_name = 'robot/details.html'
  success_url = reverse_lazy('home') 

  def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name
        return context


class OldRobotsPageView(ListView):
  model = EquityTradingRobot
  context_object_name = 'all_robots_list'
  template_name = 'robot/home.html'
  paginate_by = 10

  def get_queryset(self):
    session_username = self.request.user.get_username()
    print('EquityTradingRobot: username from session ='+session_username)
    #person = Customer.objects.get(username=session_username)
    # customer={2}".format(dashboard.id,
    #basic = CustomerBasic.objects.get(username=session_username)
    #person = Customer.objects.get(id=basic.id)
    #print("EquityTradingRobot: {0} {1} {2}".format( basic.id,basic.first_name, person.id))
    #person = basic.basic_information.id

    #portfolio = Portfolio.objects.get(owner_id=person.id)
    #print("Portfolio: {0} ".format( portfolio.name))

    return EquityTradingRobot.objects.filter() 

def delete_robot(request, pk):
  logger.info("Deleting the Robot for pk= {0} ".format(pk))
  user = request.user.get_username()

  context = { 
  }
  return render(request, 'robot/delete_robot.html', context)

# Refresh Robot Information 
def refresh_robot_information(request,pk):
  logger.debug("ETFAndReversePairRobot Information {0}".format(pk))
  user = request.user.get_username()
  basic = ETFAndReversePairRobot.objects.get(pk=pk)

  #Only process in case of a POST ( request comes from the FORM, Submit Button).
  if request.method == 'POST': 
    logger.debug('Submit was  a POST.')
    action_selected = request.POST.get('ACTION')

    if action_selected == 'SAVE':
      information_form = ETFAndReversePairRobotInformationForm(request.POST or None, request.FILES or None,instance=basic) 
      print("DEBUG: Validate robot form: {0}  ".format(information_form.is_valid()))
      print("DEBUG: Display robot form errors. {0} ".format(information_form.errors.as_data()))
      #Validate the Symbols and the Strategies?
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
      information_form = ETFAndReversePairRobotInformationForm(instance=basic)
      context = {
         "information_form":information_form
      }
      return render(request,'robot/tabs/information.html',context)
  else:
    logger.debug('Submit is NOT a post.')
    information_form = ETFAndReversePairRobotInformationForm(instance=basic)

  context = {
    'information_form':information_form
  }

  return render(request,'robot/tabs/information.html',context)

############################Robot Creation/Listing/Update and Delete ################
# update_robot():
# 
def update_robot(request, pk):
  logger.info("Updating the Strategy for pk= {0} ".format(pk))
  user = request.user.get_username()
  robot_form = ETFAndReversePairRobot(instance=robot_instance)

  context = { 
    'robot_form':robot_form 
  }

############################Creating entries in other tables to match the Robot Creation
#
# When a new Robot is created, other entries need to be added to other tables.
# This function ensures that other entries are created.
# When adding new entries, want to have some default values added.
#
def pair_add_other_entries(request, robot):
  instance = robot
  session_username = request.user.get_username()

  print ("Primary Key= {0}.  Strategy Name= {1}. Session User= {1} ".format(instance.id,instance.strategy.name, session_username))

  #I.e. Add an entry into the tables
  #modifier = CustomerBasic.objects.get(username=session_username)

   #ActivityWindow
  activity = RobotActivityWindow( pair_robot=robot)
  activity.save()

  #Budget Management Policy
  budget = RobotBudgetManagement(pair_robot=robot)
  budget.save()

  #EquitySentimentScale
  #esentiment=EquitySentimentScale(robot=robot)
  #esentiment.save()

  #Equity & Market Sentiment
  sentiment = EquityAndMarketSentiment(pair_robot=robot)
  sentiment.save()

  #symbols = RobotEquitySymbols(robot=robot)
  #symbols.save()
  #pair_robot
  return

##############################################################
# Details for all Robots. 
# 
class RobotsDetailsPageView(DetailView):
  model = ETFAndReversePairRobot
  template_name = 'robot/details.html'
  success_url = reverse_lazy('home') 

  def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name
        return context

class RobotsPageView(ListView):
  model = ETFAndReversePairRobot
  context_object_name = 'all_robots_list'
  template_name = 'robot/home.html'
  paginate_by = 10

  def get_queryset(self):
    session_username = self.request.user.get_username()
    print('ETFAndReversePairRobot: username from session ='+session_username)
    #person = Customer.objects.get(username=session_username)
    # customer={2}".format(dashboard.id,
    #basic = CustomerBasic.objects.get(username=session_username)
    #person = Customer.objects.get(id=basic.id)
    #print("EquityTradingRobot: {0} {1} {2}".format( basic.id,basic.first_name, person.id))
    #person = basic.basic_information.id

    #portfolio = Portfolio.objects.get(owner_id=person.id)
    #print("Portfolio: {0} ".format( portfolio.name))

    return ETFAndReversePairRobot.objects.filter() 


############################Robots Creation/Listing/Update and Delete ################
#
# Creating a new Robot.
#
def create_robot(request):
  logger.info("Creating a new Robot ")

  # Coming from the Form (meaning editing). 
  if request.method == 'POST':

    robot_form = ETFAndReversePairRobotCreationForm(request.POST)

    print("DEBUG: Validate robot form: {0}  ".format(robot_form.is_valid()))
    print("DEBUG: Display robot form errors. {0} ".format(robot_form.errors.as_data()))

    if(robot_form.is_valid()):

      robot_saved = robot_form.save()

      print("Robot form was saved. {0}".format(robot_saved.name))

      pair_add_other_entries(request=request,robot=robot_saved)

    else: 
      print('Forms are not valid. Exiting safely. TODO: Improve Errors')

    return redirect(reverse('thankyou'))

  else:
    robot_form = ETFAndReversePairRobotCreationForm()

  context = { 
      'robot_form':robot_form 
   }

  return render(request, 'robot/create_pair_robot.html', context)

