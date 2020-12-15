from django import forms
from django.forms import ModelForm
from django.forms.formsets import BaseFormSet

from bullbearetfs.robot.activitysentiments.models import MarketBusinessHours
from bullbearetfs.brokerages.models import BrokerageInformation
from bullbearetfs.market.models import MajorIndexSymbol, IndexTrackerIssuer, IndexTrackerETFSymbol
from bullbearetfs.market.models import MarketDataProvider,MarketInformation
from bullbearetfs.customer.models import CustomerBasic, Customer

# This is the form for creating and editing new Market Information. 
# A ModelForm is created. 
class MarketInformationForm(ModelForm):
  class Meta:
    model = MarketInformation
    fields = ['name','market_type','market_business_times']
    labels = {'name':'Market Name','market_type':'Market Type Owner'}
    help_texts = {'name':'Enter a valid name'}

class MarketBusinessHoursForm(ModelForm):
  class Meta:
    model = MarketBusinessHours
    fields = ['time_zone','opening_time','closing_time']
    labels = {'time_zone':'Time Zone','opening_time':'Opening Time','closing_time':'Market Type Owner'}
    help_texts = {'time_zone':'Enter a Time Zone'}

##############Providers ################
class BrokerageInformationForm(ModelForm):
  class Meta:
    model = BrokerageInformation
    fields = ['name','website','connection_type','connection_API_Key']
    labels = {'name':'Brokerage Name','Connection type':'Connection API Key'}
    help_texts = {'name':'Enter a valid name'}

class MarketDataProviderForm(ModelForm):
  class Meta:
    model = MarketDataProvider
    fields = ['name','website','connection_type','connection_API_Key']
    labels = {'name':'Market Data Provider','Connection type':'Connection API Key'}
    help_texts = {'name':'Enter a valid name'}


################## Symbols And Groups ######################
class MajorIndexSymbolForm(ModelForm):
  class Meta:
    model = MajorIndexSymbol
    fields = ['name','short_name','description','symbol']
    labels = {'name':'Symbol Name','short_name':'Short Name','description':'Description ','symbol':' Symbol'}
    help_texts = {'name':'Enter a valid name'}

class IndexTrackerIssuerForm(ModelForm):
  class Meta:
    model = IndexTrackerIssuer
    fields = ['name','website','short_name','description']
    labels = {'name':'Issuer Name','website':'Issuer Website','short_name':'Short Name','description':'Description'}
    help_texts = {'name':'Enter a valid name'}

class IndexTrackerETFSymbolForm(ModelForm):
  class Meta:
    model = IndexTrackerETFSymbol
    fields = ['symbol','is_leveraged','leveraged_coef','average_volume','name','etf_issuer','followed_index']
    labels = {'name':'Name','symbol':'Symbol','is_leveraged':'Is leveraged?','leveraged_coef':'Leverage Coefficient',
    'average_volume':'Average Volume','etf_issuer':'Issuer','followed_index':'Index Following'}
    help_texts = {'symbol':'Enter a valid Symbol'}

################### Market Intelligence ####################
#class EquityVolatilityForm(ModelForm):
#  class Meta:
#    model = EquityVolatility
#    fields = ['symbol','datetime','daily_volatility','five_days_volatility']
#    labels = {'symbol':'Brokerage Name','datetime':'Connection API Key','daily_volatility':'',
#              'five_days_volatility':'Five Day Volatility'}
#    help_texts = {'symbol':'Enter a valid Symbol'}