import asyncio
from django.db import models
from django.db.models import Count, F, Value
from django.db.models import FloatField
from django.db.models import Sum,Avg,Max,Min
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import datetime
from datetime import date
from django.utils import timezone
from django.contrib.auth.models import  User
import logging
import holidays
from bullbearetfs.strategy.models import EquityStrategy
from bullbearetfs.customer.models import Customer 
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple,displayOutput,displayError,strToDatetime
from bullbearetfs.brokerages.alpaca import AlpacaAPIBase, AlpacaPolygon, AlpacaMarketClock
from random import uniform

logger = logging.getLogger(__name__)


CHOICES_ACCOUNT_TYPES = (('Free','Free'),('Paid','Paid'),('Trial','Trial'))
CHOICES_DATA_FEED_FREQUENCY = (('minute','minute'),('hour','hour'),('day','day'))
ASSET_HOLD_TIME = (('1','1'),('5','5'),('14','14'),('21','21'),('30','30'))

###### TO BE DELETED?
CHOICES_PORTFOLIO_INBALANCE = (('20','20'),('25','25'),('30','30'),('15','15'))
CHOICES_MAX_CONSECUTIVE_BUYS = (('1','1'),('5','5'))
CHOICES_BUY_SIGNALS_TO_SKIP = (('1','1'),('5','5'))
CHOICES_ACTIONS_ON_PORTFOLIO_INBALANCE = (('sell','sell'),('warning','warning'))



# Type of Notification such as:
# 1. doc shared notification
# 2. message notification
class NotificationType(models.Model):
  name = models.CharField(max_length=20,default='')
  value = models.IntegerField(default=0)

  def __str__(self):
    return "{0} {1} ".format(self.name, self.value)
 
# All notification placed in this table.
# i.e.: User A has shared a deal you
# User A has added you to their team
# User A has uploaded a Deal Analysis
# User A has sent you a message
#  TODO: Re-examine the need for this class
class Notifications(models.Model):
  notifications_name = models.CharField(max_length=20,default='')
  from_user = models.IntegerField(default=0)
  to_user = models.IntegerField(default=0)
  share_date = models.DateTimeField(auto_now_add=True)
  read_date = models.DateTimeField(auto_now_add=True)
  notification_type = models.ForeignKey(NotificationType,on_delete=models.PROTECT,blank=True,null=True)

  def __str__(self):
    return "{0} ".format(self.notifications_name)


#
# Manage versions.
# 
class RobotVersions(models.Model):
  name = models.CharField(max_length=10,default='', blank=True)
  major = models.IntegerField(default=0,blank=True)
  minor = models.IntegerField(default=0,blank = True)
  release = models.IntegerField(default=0, blank=True)
  changes = models.CharField(max_length=250,default='', blank=True)

  def __str__(self):
    return "{0} {1} {2} {3} ".format(self.name,self.major,self.minor,self.release)      



# ######################## Equity Trading Robot Components ######
# Keeps track of trading data every 5 minutes for a given symbol. Will keep data for 90 days running.
# Might be able to get this from another source. Also keep track of pre-market and post market data 
class EquityTradingData(models.Model):
  symbol =  models.CharField(max_length=10,default='')
  trade_datetime = models.DateTimeField('date created',default=timezone.now) #TODO: Configure me
  volume = models.FloatField(default=0)
  price = models.FloatField(default=0)

  def __str__(self):
    return "{0} {1} {2}".format(self.symbol, self.price, self.volume)

  @staticmethod
  def updateTradingData(symbol,price,volume,trade_datetime): 
    EquityTradingData.objects.create(symbol=symbol,price=price,volume=volume,trade_datetime=trade_datetime)

  @staticmethod
  def getPrice(symbol): 
    now=datetime.now(getTimeZoneInfo()) 
    data_q = EquityTradingData.objects.filter(symbol=symbol)
    daily_most_recent = data_q.filter(trade_datetime__date=date(now.year,now.month,now.day)).order_by('-trade_datetime')
    return daily_most_recent[0].price

  @staticmethod
  def getDailyHigh(symbol): 
    now=datetime.now(getTimeZoneInfo()) 
    data_q = EquityTradingData.objects.filter(symbol=symbol)
    daily_high = data_q.filter(trade_datetime__date=date(now.year,now.month,now.day)).aggregate(greatest=Max('price'))
    return 0 if daily_high['greatest'] == None else daily_high['greatest']

  @staticmethod
  def getDailyLow(symbol):
    now=datetime.now(getTimeZoneInfo()) 
    data_q = EquityTradingData.objects.filter(symbol=symbol)
    daily_low = data_q.filter(trade_datetime__date=date(now.year,now.month,now.day)).aggregate(lowest=Min('price'))
    return 0 if daily_low['lowest'] == None else daily_low['lowest']
  
  @staticmethod
  def getDailyAverage(symbol): 
    now=datetime.now(getTimeZoneInfo()) 
    data_q = EquityTradingData.objects.filter(symbol=symbol)    
    daily_average = data_q.filter(trade_datetime__date=date(now.year,now.month,now.day)).aggregate(average=Avg('price'))
    return 0 if daily_average['average'] == None else daily_average['average']
 
  @staticmethod
  def getDaysHigh(symbol,days=7):
    data_q = EquityTradingData.objects.filter(symbol=symbol)    
    end_date = datetime.now(tz=getTimeZoneInfo())
    date_diff = timedelta(days=-days)
    start_date = end_date + date_diff  
    d_h_7 = data_q.filter(trade_datetime__lte=end_date, trade_datetime__gte=start_date).aggregate(greatest=Max('price'))
    return 0 if d_h_7['greatest'] == None else d_h_7['greatest']

  @staticmethod
  def getDaysLow(symbol,days=7):
    data_q = EquityTradingData.objects.filter(symbol=symbol)    
    end_date = datetime.now(tz=getTimeZoneInfo())
    date_diff = timedelta(days=-days)
    start_date = end_date + date_diff  
    d_l_7 = data_q.filter(trade_datetime__lte=end_date, trade_datetime__gte=start_date).aggregate(lowest=Min('price'))
    return 0 if d_l_7['lowest'] == None else d_l_7['lowest']

  @staticmethod
  def getDaysAverage(symbol,days=7):
    data_q = EquityTradingData.objects.filter(symbol=symbol)    
    end_date = datetime.now(tz=getTimeZoneInfo())
    date_diff = timedelta(days=-days)
    start_date = end_date + date_diff  
    d_a_7 = data_q.filter(trade_datetime__lte=end_date, trade_datetime__gte=start_date).aggregate(average=Avg('price'))
    return 0 if d_a_7['average'] == None else d_a_7['average']

  #How often was the stock price above the average  
  @staticmethod
  def getDailyAboveAverage(symbol):
    EquityTradingData.objects.filter().aggregate(average=Avg(''))
    return 0 if daily_average['average'] == None else daily_average['average']

  #How often was the stock price below the average  
  @staticmethod
  def getDailyBelowAverage(symbol):
    EquityTradingData.objects.filter().aggregate(average=Avg(''))
    pass 

  #Daily Spread devided by the average price  
  @staticmethod
  def getDailyPriceFluctuationInPercentage(symbol):
    EquityTradingData.objects.filter().aggregate(average=Avg(''))
    pass 


 
 
#Components
# A TradingRobot (EA) is an automated and Autonoumous Runner, that processes Stock Market Events to decide when to
# Acquire and Dispose of Assets. This particular Robot focuses solely on Stock Market Equities. 
# At this time, it is designed and implemented to focus only on the acquisition and disposition of Bull/Bear ETF Pairs.
# as Stocks, ETFs, Mutual Funds. Later, we will add Forex Trading Robots, Futures Trading Robots, 
# Commodity Trading Robots, Crypto Trading Robots, ...etc
# A trading Robot is created and configured once then deployed. From here, it is expected to runs automatically 
# and makes decisions based on its configuration and strategies. There should be as little intervention as 
# possible during its run. It should be capable of running successful on its own and produce results that 
# beat the major indexes over the short and the long term (after exclusing comissions and taxes).
# At first, we will focus on mostly short term Equity trading strategies 
# It monitors the performance of assets it owns, until these assets have reached the level of profit defined. Then the Robot
# will dispose of the asset.
# Components of an Equity Trading Robot:
# Each Trading Robot is designed to be as flexible and configurable as possible. Therefore it provides lots of options. 
# It consists of an Acquisition Policy, a Disposition Policy, a Portfolio Protection Policy, 
# An Orders Management Policy, Transaction Data
# Acquisition Policy: Determines at when Assets should be purchased. It uses Entry Indicators to determine
# the most appropriate time to enter a market position, which asset to purchase and how much to spend.
# Disposition Policy: Determines at what time Assets should be disposed of. It uses Exit Indicators to determine
# the most appropriate time to dispose of an Asset.
# Portfolio Protection Policy: Once an asset has been purchased, it determines the how to protect the asset.
# Order Management Policy: It determines which Order Types should be used when acquiring/disposing of an asset.
# Transaction Data: This is where Transaction Data are kept. 
# Profit Targets: Projection / targets are used to follow the evolution of unrealized gains through the lifetime of
# ownership of assets. Profit target projections are used to determin exit points.
class EquityTradingRobot(models.Model):
  name = models.CharField(max_length=50,default='')
  description = models.CharField(max_length=100,default='')
  creation_date = models.DateTimeField('date created',default=timezone.now)
  modify_date = models.DateTimeField('date modified',default=timezone.now)
  #modified_by = models.ForeignKey(Customer,on_delete=models.PROTECT, default=1)
  internal_name = models.CharField(max_length=10,default='',blank=True)
  #If set, do not buy anymore ... but sale
  sell_remaining_before_buy = models.BooleanField(default=False) 
  # If set, liquidate holdings
  liquidate_on_next_opportunity = models.BooleanField(default=False) 

  visibility = models.BooleanField(default=False)
  active = models.BooleanField(default=False)
  deployed = models.BooleanField(default=False)
  version = models.CharField(max_length=10,default='')

  #Strategy
  max_asset_hold_time = models.CharField(max_length=5,choices=ASSET_HOLD_TIME, default='1')
  hold_time_includes_holiday = models.BooleanField(default=False)

  # check system every 60 seconds. Sleep pattern within the robot
  live_data_check_interval = models.IntegerField(default=60)
  data_feed_frequency = models.CharField(max_length=10,choices=CHOICES_DATA_FEED_FREQUENCY, default='day')

  # Orders Management
  orders = models.ForeignKey('OrdersManagement', on_delete=models.PROTECT,blank=True,null=True)
  
  #Portfolion Management
  portfolio = models.ForeignKey('Portfolio', on_delete=models.PROTECT,blank=True,null=True)
  
  #Ownership Management
  owner = models.ForeignKey('Customer', on_delete=models.PROTECT,blank=True,null=True)
  
  #Strategy Management
  strategy = models.ForeignKey(EquityStrategy,on_delete=models.PROTECT,blank=True,null=True)
  
  #Equities Management
  symbols = models.ForeignKey('RobotEquitySymbols',on_delete=models.PROTECT,blank=True,null=True)

  # 
  def __str__(self):
    return "{0} {1} ".format(self.name,self.active)

  #
  #This method is call so that trading can continue
  #
  async def prepareTrades(self):
    logger.info("     Robot '{0}'' is trading now ...".format(self.name))

    await asyncio.sleep(1)
    return
