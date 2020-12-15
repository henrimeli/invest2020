import datetime
import logging

from django.shortcuts import render, redirect
from django.urls import reverse,reverse_lazy

# Create your views here.
from django.http import HttpResponse
from bullbearetfs.forms import contactForm

# Import Views
from django.views.generic import ListView, DetailView,View,TemplateView, FormView
from django.views.generic import CreateView, UpdateView,DeleteView

# Import Models
from bullbearetfs.customer.models import CustomerBasic,Customer
#from bullbearetfs.models import BrokerageInformation, MarketBusinessHours, Portfolio
from bullbearetfs.market.models import MarketInformation, MajorIndexSymbol,  IndexTrackerIssuer, IndexTrackerETFSymbol
# Import Forms
from .forms import MarketInformationForm, MarketDataProviderForm, BrokerageInformationForm
from .forms import MajorIndexSymbolForm, IndexTrackerIssuerForm, IndexTrackerETFSymbolForm
from .forms import MarketBusinessHoursForm

# Get a logger instance
logger = logging.getLogger(__name__)

# Functions
def create_market(request):
  print("Creating a new Market ")

  market_form = MarketDataForm(initial={'visibility':'True'})

  context = { 
      'market_form':market_form 
    }



  return render(request, 'market/create_market.html', context)

def update_market(request, pk):
  print("Updating the Market for pk= {0} ".format(pk))
  user = request.user.get_username()
  context = { 

    }

  return render(request, 'market/update_market.html', context)

def delete_market(request, pk):
  print("Deleting the Market Data for pk= {0} ".format(pk))
  user = request.user.get_username()
  context = { 

    }

  return render(request, 'market/delete_market.html', context)

################################AJAX Asynchronous Functions #####################
#
# This is the Market Providers Tab
#
def refresh_market_providers(request):

  print("Market Provider Tab: ")

  broker_form =BrokerageInformationForm()
  market_data_form = MarketDataProviderForm()

  context = {
    'broker_form':broker_form,
    'market_data_form':market_data_form
  }

  return render(request,'market/tabs/providers.html',context)


#
# Shows all the important market information
#
def refresh_market_symbols(request):

  logger.debug("Market Symbols Tab: ")
  all_major_symbols = MajorIndexSymbol.objects.filter()
  all_major_etfs = IndexTrackerETFSymbol.objects.filter()
  index_symbols_form =MajorIndexSymbolForm()
  index_issuers_form = IndexTrackerIssuerForm()
  index_trackers_form=IndexTrackerETFSymbolForm()

  context = {
    'all_major_symbols':all_major_symbols,
    'all_major_etfs':all_major_etfs,
    'index_symbols_form':index_symbols_form,
    'index_issuers_form':index_issuers_form,
    'index_trackers_form':index_trackers_form,    
  }

  return render(request,'market/tabs/symbols.html',context)

def refresh_market_intelligence(request):

  print("Market intelligence Tab: ")

  volatility_form =EquityVolatilityForm()

  context = {
    'volatility_form':volatility_form
  }

  return render(request,'market/tabs/intelligence.html',context)

def refresh_market_information(request):

  print("Market Information Tab: ")

  hours_form =MarketBusinessHoursForm()
  info_data_form = MarketInformationForm()

  context = {
    'hours_form':hours_form,
    'info_data_form':info_data_form
  }

  return render(request,'market/tabs/information.html',context)

##############################################################
# Details for all Robots. 
# 
class MarketDetailsPageView(DetailView):
  model = MarketInformation
  template_name = 'market/details.html'
  success_url = reverse_lazy('home') 

  def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name
        return context


class MarketPageView(ListView):
  model = MarketInformation
  context_object_name = 'all_markets_list'
  template_name = 'market/home.html'
  paginate_by = 5

  def get_queryset(self):
    session_username = self.request.user.get_username()
    print('Market: username from session ='+session_username)
    #person = Customer.objects.get(username=session_username)
    # customer={2}".format(dashboard.id,
    #basic = CustomerBasic.objects.get(username=session_username)
    #person = Customer.objects.get(id=basic.id)
    #print("EquityTradingRobot: {0} {1} {2}".format( basic.id,basic.first_name, person.id))
    #person = basic.basic_information.id

    #portfolio = Portfolio.objects.get(owner_id=person.id)
    #print("Portfolio: {0} ".format( portfolio.name))

    return MarketInformation.objects.filter() 

