from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import datetime
from django.utils import timezone
from django.contrib.auth.models import  User
import logging 

"""
  TODO: Describe the Module here ...

  List the classes of the module here
"""

logger = logging.getLogger(__name__)


# Keeps track of Markets and its specific characteristics
CHOICES_MARKET_TYPE = (('Equity','Equity'),('Forex','Forex'),('Crypto','Crypto'),('Futures','Futures'),('Commodity','Commodity'))
CHOICES_ROBOT_FRACTIONS = (('10','10%'),('20','20%'),('30','30%'))

# ######################## Dashboard #############

# ######################## Foundation Package #############
# Consists of the static section of the website such as
# Home Page, About Page, Help Page, FAQ Page, Blogs Page
# Education Page, Contact Page (non static)
class WebsiteContactPage(models.Model):
  subject = models.CharField(max_length=50,default='')
  email = models.EmailField()
  comment = models.TextField()
  john = 1

  def __str__(self):
    return "{0} {1} {2} ".format(self.email,self.subject,self.john)

  def getSubject(self):
    return self.subject

  def setComment(self, value):
    self.comment = value

  def run(self):
    print("Running ")
    self.changeJohn(value=10)

  def getComments(self):
    return self.comment

#Markets: Symbols information, symbols groups (nasdaq 3x, dow jones 2x, ), 
# business hours, brokerage, volatility, 
# Keeps track of Market specific data.
# Ideally, we would like to get this from an API
#TODO: Configure Property. Real Time Data is provided by seperate company
class MarketDataProvider(models.Model):
  name = models.CharField(default='',max_length=20)
  website = models.CharField(default='',max_length=20)
  connection_type = models.CharField(default='',max_length=20)
  connection_API_Key = models.CharField(default='',max_length=20)


  def __str__(self):
    return "{0} ".format(self.name)


# ######################## Markets Information ##################
#  
# This is the Markets Type Information: Equity, Forex, Futures
# Each Market has its specificities such as:
# opening/closing times
# Holidays
# Restrictions, rules and regulations, ...
# Robots must have inherent behaviors based on Market Type
# 
class MarketInformation(models.Model):
  name = models.CharField(max_length=50,default='')
  description = models.CharField(max_length=150,default='')
  market_top_news = models.CharField(max_length=150,default='')
  market_reference_links =  models.CharField(max_length=150,default='')
  symbol = models.CharField(max_length=10,default='')
  market_type = models.CharField(max_length=25, choices = CHOICES_MARKET_TYPE,default='Equity')
  market_business_times = models.ForeignKey('MarketBusinessHours', on_delete=models.PROTECT)
  
  def __str__(self):
    return "{0} {1} ".format(self.name, self.symbol)

# Market Data Information about Major Indexes
# such as the Dow, Russell, Nasdaq, S&P
#TODO: Link with 
class MajorIndexSymbol(models.Model):
  name = models.CharField(max_length=50,default='')
  short_name = models.CharField(max_length=20,default='')
  description = models.CharField(max_length=150,default='')
  symbol = models.CharField(max_length=50,default='')
  website = models.CharField(max_length=50,default='')

  def __str__(self):
    return "{0} {1} ".format(self.name, self.symbol)

# There are various ETF Trackers from various companies
# Bloomberg, iShares, Direxion
class IndexTrackerIssuer(models.Model):
  name = models.CharField(max_length=50,default='')
  short_name = models.CharField(max_length=20,default='')
  description = models.CharField(max_length=150,default='')
  website = models.CharField(max_length=50,default='')
  #symbol = models.CharField(max_length=50)
  
  def __str__(self):
    return "{0} {1} ".format(self.name, self.short_name)

# ETF Symbols
class IndexTrackerETFSymbol(models.Model):
  name = models.CharField(max_length=50,default='')
  followed_index = models.ForeignKey(MajorIndexSymbol, on_delete=models.PROTECT)
  etf_issuer = models.ForeignKey(IndexTrackerIssuer, on_delete=models.PROTECT)
  symbol = models.CharField(max_length=10,default='')
  is_leveraged = models.BooleanField(default=True)
  leveraged_coef = models.IntegerField(default=1)
  average_volume = models.IntegerField(default=0)
  average_daily_volatility = models.CharField(max_length=25, choices = CHOICES_ROBOT_FRACTIONS,default='Investor')

  def __str__(self):
    return "{0} ".format(self.name)

# ######################## Dashboard #############

class MarketDummy(models.Model):
  subject = models.CharField(max_length=50,default='')
  email = models.EmailField()
  comment = models.TextField()

  def __str__(self):
    return "{0} {1} ".format(self.email,self.subject)
