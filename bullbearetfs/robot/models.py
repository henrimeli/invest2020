from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import datetime
from django.utils import timezone
from django.contrib.auth.models import  User
import logging, json, time, pytz, asyncio, re
from datetime import timedelta
from os import environ 
#import dateutil.parser
import logging
#import holidays
from bullbearetfs.customer.models import Customer
from bullbearetfs.strategy.models import EquityStrategy
from bullbearetfs.customer.models import Customer
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple,displayOutput,displayError,strToDatetime
#from bullbearetfs.brokerages.alpaca import AlpacaAPIBase, AlpacaPolygon, AlpacaMarketClock

logger = logging.getLogger(__name__)


##############################
CHOICES_ACCOUNT_TYPES = (('Free','Free'),('Paid','Paid'),('Trial','Trial'))
CHOICES_MARKET_TIMEZONE = (('EST','EST'),('EURO','EURO'),('24_7','24_7'))
CHOICES_CASH_POSITION_UPDATE_POLICY = ((24,'1 day'),(1,'hourly'),(0,'immediate'),(48,'2 days'),(72,'3 days'))
CHOICES_DATA_FEED_FREQUENCY = (('minute','minute'),('hour','hour'),('day','day'))
ASSET_HOLD_TIME = (('1','1'),('5','5'),('14','14'),('21','21'),('30','30'))
CHOICES_ROBOT_FRACTIONS = ((0.10,'10%'),(0.20,'20%'),(0.25,'25%'),(0.30,'30%'))



CHOICES_LIVE_DATA_FEED=(('Polygon','Polygon'),('Not Yet Implemented','Not Yet Implemented'))
CHOICES_BLACKOUT_WINDOW=(('0','0'),('15','15'),('30','30'),('45','45'),('60','60'))
CHOICES_MIDDAY_BLACKOUT_START=(('0','0'),('10','10:00am'),('11','11:00am'),('12','12:00pm'),('13','13:00pm'),('14','2:00pm'),('15','3:00pm'))
CHOICES_VOLATILITY_SCALE=(('High','High'),('Medium','Medium'),('Low','Low'),('None','None'),('Not Available','Not Available'))
CHOICES_SENTIMENTS_SCALE=((-3,'3x Bearish'),(-2,'2x Bearish'),(-1,'1x Bearish'),(0,'Neutral'),
                          (1,'1x Bullish'),(2,'2x Bullish'),(3,'3x Bullish'))
CHOICES_SENTIMENTS_WEIGHT_SCALE=((100,'100'),(50,'50'),(0,'0'))
CHOICES_SENTIMENTS_FEED  = (('Automatic','Automatic'),('Manual','Manual'))

CHOICES_USE_CASH_OR_NUMBER= (('Number','Number'),('Percent','Percent'))
CHOICES_MAX_BUDGET_PER_ACQUISITION_PERCENT = (('10','10'),('15','15'),('20','20'),('25','25'),('30','30'))
CHOICES_MAX_BUDGET_PER_ACQUISITION_NUMBER = (('500','500'),('250','250'),('1000','1000'),('1500','1500'),('2000','2000'),('2500','2500'))

CHOICES_TAX_RATE = (('0','0'),('5','5'))
CHOICES_COMMISSION_PER_TRADE = (('0','0'),('1','1'),('5','5'))
CHOICES_OTHER_COSTS = (('0','0'),('5','5'))

CHOICES_BROKERAGE_PAPER = (('Local Account','Local Account'),('eTrade Regular','eTrade Regular'),('eTrade Retirement','eTrade Retirement'),('Alpaca','Alpaca'),('Ameritrade','Ameritrade'))
CHOICES_BROKERAGE_LIVE = (('Local Account','Local Account'),('eTrade Regular','eTrade Regular'),('eTrade Retirement','eTrade Retirement'),('Alpaca','Alpaca'),('Ameritrade','Ameritrade'))

MASTER_BULLS = ['TQQQ','UDOW','LABU','SPXU','UPRO','UCO','TNA','FAS','TECL','NUGT','JNUG','SOXL','URTY','GUSH','ERX','AGQ','KOLD','YINN']
MASTER_BEARS = ['SQQQ','SDOW','LABD','SPXS','SPXL','SCO','TZA','FAZ','TECS','DUST','JDST','SOXS','SRTY','DRIP','ERY','ZSL','BOIL','YANG']
MASTER_ETFS  = ['QQQ' ,'DIA' ,'XBI' ,'SPY', 'SPY' ,'DBO','IJR','XFN','PHLX','MSCI','RING' ,'DIA' ,'DIA' , 'DIA','DIA','DIA','CHIN','BBB']

MASTER_NAMES = ['Nasdaq100','Dow Jones Industrial','Biotech','S&P500','S&P500','Bloomberg Crude Oil',
                'Small Cap','Financials','Technology','Gold Miners','Junior Gold Miners','Semi Conductors',
                'Russell 2000','S&P Oil & Gas Exploration','Energy','Silver','Something','China']
MASTER_LEVERAGE = ['3x','3x','3x','3x','3x','2x','3x','3x','3x','3x','3x','3x','3x','3x','3x','3x','3x','3x']
MASTER_OWNERS = ['Proshares','Proshares','Direxion','Direxion','Proshares','Proshares','Direxion TNA','Direction FAS',
                 'Direxion','Direxion','Direxion','Direxion','Proshares','Direxion','Direxion','Direxion','Direxion','Direxion']

MASTER_DESC = ['Nasdaq100','ProShares UltraPro DJIA 3x ETF','','','','','','','','','','','','','','','','','','','','']
MASTER_TOP15 = ['AMZN,AAPL,MSFT,IBM','AAA,BBB,CCC','YYY,III,PPP','','','','','','','','','','','','','','','','','','']


##############################
#
# Startup Status
# time, action, robot, comment
CHOICES_STARTUP_ACTIONS = (('start','start'),('stop','stop'))
class StartupStatus(models.Model):
  log_time = models.DateTimeField('date created',default=timezone.now)
  comment = models.CharField(max_length=50,default='',blank=True,null=True)
  action = models.CharField(max_length=10, choices = CHOICES_STARTUP_ACTIONS,default='start')
  object_type = models.CharField(max_length=10, choices = CHOICES_STARTUP_ACTIONS,default='start')
  object_identifier = models.IntegerField(default=0,blank=True,null=True)
  modified_by = models.ForeignKey('Customer',on_delete=models.PROTECT, blank=True,null=True)

  def __str__(self):
    return "Startup-time-{0} ".format(self.log_time )


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


#Markets: Symbols information, symbols groups (nasdaq 3x, dow jones 2x, ),
# business hours, brokerage, volatility,
# Keeps track of Market specific data.
# Ideally, we would like to get this from an API

class BrokerageInformation(models.Model):
  name = models.CharField(default='',max_length=20)
  website = models.CharField(default='',max_length=20)
  connection_type = models.CharField(default='',max_length=20)
  connection_API_Key = models.CharField(default='',max_length=20)
  brokerage_type = models.CharField(max_length=20, choices = CHOICES_BROKERAGE_PAPER,default='Alpaca',)

  def __str__(self):
    return "{0} ".format(self.name)

# ######################## Portfolio Information ##################
# 
# This is the Portfolio related Information:
# It captures information about the portfolio at the brokerage.
# How much cash is available, and various portolio policies such
# as margin trading requirements, ...
# Choices are expressed in percentage
# max_robot_fraction specifies how much a robot can invest in total.
# NOTE: Do not confuse with BudgetManagement From each Robot
class Portfolio(models.Model):
  name = models.CharField(max_length=50,default='')
  description = models.CharField(max_length=150,default='')
  owner = models.ForeignKey('Customer', on_delete=models.PROTECT,blank=True,null=True)
  brokerage = models.ForeignKey(BrokerageInformation,on_delete=models.PROTECT,blank=True,null=True)
  initial_cash_funds = models.FloatField(default=0) #Updated every 24 hours
  current_cash_funds = models.FloatField(default=0)
  max_robot_fraction = models.CharField(max_length=25, choices = CHOICES_ROBOT_FRACTIONS,default='10')
  cash_position_update_policy = models.CharField(max_length=15,choices=CHOICES_CASH_POSITION_UPDATE_POLICY,default='daily')

  def __str__(self):
    return "Portfolio - {}.".format(self.name)


# Managing the money used to acquire shares
# The goal here is to determine where the Robot should get funds for trading.
# Robot gets assigned initial funds from Portfolio.
# If Robot generates money, Robot should be able to use have more money to trade with
# If Robot loses money, Robot should have less money to trade, unless portfolio gives him money
# Portfolio management is shared between Robot and Portfolio management.
# Robot's share is always a percentage of Portfolio, up to a certain extend.
class RobotBudgetManagement(models.Model):
  #Initial Value. Should be updated every day. Value should come from the Portfolio via the Robot.
  #Remove them from the Model and keep them as class variables only
  portfolio_initial_budget = models.FloatField(default=0.0, blank=True, null=True)

  # Usage per Acquisition
  use_percentage_or_fixed_value = models.CharField(max_length=15,choices=CHOICES_USE_CASH_OR_NUMBER,default='Number')

  # Current Cash Position
  current_cash_position = models.FloatField(default=0.0)
  cash_position_update_policy = models.CharField(max_length=15,choices=CHOICES_CASH_POSITION_UPDATE_POLICY,default='daily')

  add_taxes = models.BooleanField(default=False)
  add_commission = models.BooleanField(default=False)
  add_other_costs = models.BooleanField(default=False)

  taxes_rate = models.CharField(max_length=5,choices=CHOICES_TAX_RATE,default='0')
  commission_per_trade = models.CharField(max_length=5,choices=CHOICES_COMMISSION_PER_TRADE,default='0')
  other_costs = models.CharField(max_length=5,choices=CHOICES_OTHER_COSTS,default='0')

  #Budget per equity acquisition
  max_budget_per_purchase_percent = models.CharField(max_length=15,choices=CHOICES_MAX_BUDGET_PER_ACQUISITION_PERCENT, default='15')
  max_budget_per_purchase_number = models.CharField(max_length=15,choices=CHOICES_MAX_BUDGET_PER_ACQUISITION_NUMBER, default='2000')

  pair_robot = models.ForeignKey('ETFAndReversePairRobot',on_delete=models.PROTECT, blank=True,null=True)


  def __str__(self):
    return "Budget Management - {0}.".format(self.id)

  # Is called Once per day from the main robot to provide budget updates from the Portfolio
  # Is called after the Synchronization with the Brokerage Portfolio has already been run
  # This will only replicate the data from the Portfolio here once per day. All daily transactions
  # will be updated from this interface.
  def setInitialDailyBudget(self,robot):
    self.portfolio_initial_budget = robot.portfolio.getInitialRobotBudget()
    self.current_cash_position = self.portfolio_initial_budget
    self.save()

  def updateBudgetAfterAcquisition(self,amount):
    self.current_cash_position = self.current_cash_position - amount
    self.save()
    return self.current_cash_position

  def updateBudgetAfterDisposition(self,amount):
    self.current_cash_position = self.current_cash_position + amount
    self.save()
    return self.current_cash_position

  def haveEnoughFundsToPurchase(self):
    return self.current_cash_position >= self.getCostBasisPerRoundtrip()

  def getCostBasisPerRoundtrip(self):
    if self.use_percentage_or_fixed_value == 'Number':
      return float(self.max_budget_per_purchase_number)
    else:
      return float(self.max_budget_per_purchase_percent) * self.current_cash_position *.01

  def getAvailableTotalCash(self):

    return self.current_cash_position


# Robot's activity window
# This should go hand in hand with the MarketInformation Tabls.
# Parameters: {'now':<date>} .
# Returns: if now is outside the Set Window,
class RobotActivityWindow(models.Model):
  trade_before_open = models.BooleanField(default=False)
  trade_after_close = models.BooleanField(default=False)
  trade_during_extended_opening_hours = models.BooleanField(default=False)

  offset_after_open = models.CharField(max_length=15,choices=CHOICES_BLACKOUT_WINDOW, default='0')
  offset_before_close = models.CharField(max_length=15,choices=CHOICES_BLACKOUT_WINDOW, default='0')
  blackout_midday_from = models.CharField(max_length=15,choices=CHOICES_MIDDAY_BLACKOUT_START, default='0')
  blackout_midday_time_interval = models.CharField(max_length=15,choices=CHOICES_BLACKOUT_WINDOW, default='0')

  live_data_feed = models.CharField(max_length=25,choices=CHOICES_LIVE_DATA_FEED, default='Polygon')
  pair_robot = models.ForeignKey('ETFAndReversePairRobot',on_delete=models.PROTECT, blank=True,null=True)

  def __str__(self):
    return "Activity Window - {0}.".format(self.pk)

  def getTodayMiddayBlackoutStart(self,hour_of_day,current_time):
    ct = current_time
    if hour_of_day=='10:00am':
      return datetime(year=ct.year,month=ct.month,day=ct.day,hour=10,minute=0,tzinfo=getTimeZoneInfo())
    elif hour_of_day=='11:00am':
      return datetime(year=ct.year,month=ct.month,day=ct.day,hour=11,minute=0,tzinfo=getTimeZoneInfo())
    elif hour_of_day=='12:00pm':
      return datetime(year=ct.year,month=ct.month,day=ct.day,hour=12,minute=0,tzinfo=getTimeZoneInfo())
    elif hour_of_day=='13:00pm':
      return datetime(year=ct.year,month=ct.month,day=ct.day,hour=13,minute=0,tzinfo=getTimeZoneInfo())
    elif hour_of_day=='14:00pm':
      return datetime(year=ct.year,month=ct.month,day=ct.day,hour=14,minute=0,tzinfo=getTimeZoneInfo())
    elif hour_of_day=='15:00pm':
      return datetime(year=ct.year,month=ct.month,day=ct.day,hour=15,minute=0,tzinfo=getTimeZoneInfo())
    elif hour_of_day=='0':
      return datetime(year=ct.year,month=ct.month,day=ct.day,hour=10,minute=0,tzinfo=getTimeZoneInfo())
    return datetime(year=ct.year,month=ct.month,day=ct.day,hour=10,minute=0,tzinfo=getTimeZoneInfo())

  #
  #Blackout windows allows us to create intervals, during which we don't want to trade.
  #
  def isWithinBlackoutWindow(self,current_time):
    ct = current_time

    minutes_offset_after_open = int(self.offset_after_open)
    blackout_opening_left_side  = datetime(year=ct.year,month=ct.month,day=ct.day,hour=9,minute=30,second=0,tzinfo=getTimeZoneInfo())
    blackout_opening_right_side = blackout_opening_left_side + timedelta(minutes=minutes_offset_after_open)

    blackout_midday_left_side = self.getTodayMiddayBlackoutStart(hour_of_day=self.blackout_midday_from,current_time=current_time)
    blackout_midday_right_side = blackout_midday_left_side + timedelta(minutes=int(self.blackout_midday_time_interval))

    minutes_offset_before_close = int(self.offset_before_close)
    blackout_end_of_day_left_side = datetime(year=ct.year,month=ct.month,day=ct.day,hour=16,minute=00,second=0,tzinfo=getTimeZoneInfo()) + timedelta(minutes=-minutes_offset_before_close)
    blackout_end_of_day_right_side = datetime(year=ct.year,month=ct.month,day=ct.day,hour=16,minute=0,second=0,tzinfo=getTimeZoneInfo())

    answer = (blackout_opening_left_side < current_time < blackout_opening_right_side) \
          or (blackout_midday_left_side < current_time < blackout_midday_right_side) \
          or (blackout_end_of_day_left_side < current_time < blackout_end_of_day_right_side)

    return answer

  #
  # Before placing a trade, we must know if the conditions to place a trade are met.
  # By default we can trade during Opened Market hours.
  # Trading in other timeframe needs to be allowed through a flag.
  #
  def canTradeNow(self,current_time):
    if (MarketBusinessHours.isWithinMarketHours(current_time=current_time)):
      if self.isWithinBlackoutWindow(current_time=current_time):
        return False
      return True

    if self.trade_before_open and \
        (MarketBusinessHours.isWithinPreMarketHours(current_time=current_time)):
      return True

    if self.trade_after_close and \
        (MarketBusinessHours.isWithinAfterMarketHours(current_time=current_time)):
      return True

    if self.trade_during_extended_opening_hours and \
        (MarketBusinessHours.isWithinExtendedPreMarketHours(current_time=current_time)):
      return True
    return False


#
# The purpose of this is to keep track of the stock market business hours.
# To prevent constant calls to external websites, we provide our own
# limited set of functionality to keep track and report on time
# We use the 'pip install holidays' to upload the holidays. We use weekday() to determin the weekdays and holidays.
# See Link here: https://towardsdatascience.com/5-minute-guide-to-detecting-holidays-in-python-c270f8479387
# The Stock Market should be opened every business day. Closed on Holidays and on Weekends.
# The functionality hear reflects that.
# Checking is we are withing PreMarket, Business, PostMarket and Extended Premarket
#
class MarketBusinessHours(models.Model):
  name = models.CharField(max_length=20,default='',blank=True)
  time_zone = models.CharField(max_length=10, choices = CHOICES_MARKET_TIMEZONE,default='EST')
  opening_time = models.DateTimeField('date created',default=timezone.now)
  closing_time = models.DateTimeField('date created',default=timezone.now)

  def __str__(self):
    return "Opens={1}. Day:{2}.".format(self.marketisOpenToday, self.name)


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



#
# Symbol(s) associated with given Robot
#
class RobotEquitySymbols(models.Model):
  name = models.CharField(max_length=25,default='')
  description = models.CharField(max_length=100,default='')
  symbol = models.CharField(max_length=6,default='')
  owners = models.CharField(max_length=25,default='')
  leverage = models.CharField(max_length=5,default='')
  bullishSymbol = models.CharField(max_length=6,default='')
  bearishSymbol = models.CharField(max_length=6,default='')
  top_15_stocks = models.CharField(max_length=250,default='')

  def __str__(self):
    return "{0} {1} {2} Bull, Bear, Etf".format(self.owners, self.name, self.leverage)

  def getBasicInformation(self):
    return "{} {} {} {} {} {}".format(self.owners,self.name,self.leverage,self.bullishSymbol,self.bearishSymbol,self.symbol)


  @staticmethod
  def getMasterEntriesAsJSON():
    pairs = RobotEquitySymbols.objects.filter()
    entry = [{'etf':pair.symbol,'bull':pair.bullishSymbol,'bear':pair.bearishSymbol} for pair in pairs]
    entries = dict()
    entries['entries'] = entry
    return entries

  @staticmethod
  def printAllMasterEquities():
    entries = RobotEquitySymbols.objects.filter().all()
    for x in entries:
      print("\n {}".format(x.getBasicInformation()))

  #
  # Returns the number of Master Equity Entries
  #
  @staticmethod
  def getTotalMaster():
    entries = RobotEquitySymbols.objects.filter().all()
    return len(entries)


#
  # Static Method used to load the topETFs that we will be following and tracking.
  #
  @staticmethod
  def isValidPair(bull,bear,etf=None):
    count = RobotEquitySymbols.objects.filter(bullishSymbol=bull).filter(bearishSymbol=bear).count()
    return (count==1)

  #
  # Purge All Equities will delete all entries
  #
  @staticmethod
  def purgeAllEquities():
    RobotEquitySymbols.objects.all().delete()
    return True
  #
  # Static Method used to load the topETFs that we will be following and tracking.
  # TODO: Complete the lists , Update the ETFs, Add some test cases such as:
  #   Move some of this to a different file for better documentation?
  #
  @staticmethod
  def insertMasterEquities(count=1):
    index = 0
    total = count if (count<len(MASTER_BULLS)) else len(MASTER_BULLS)
    while index < total:
      bull = MASTER_BULLS[index]
      bear = MASTER_BEARS[index]
      etf  = MASTER_ETFS[index]
      leverage  = MASTER_LEVERAGE[index]
      owners = MASTER_OWNERS[index]
      name = MASTER_NAMES[index]
      top_15=MASTER_TOP15[index]

      #Check if a bull/bear pair has already been uploaded.
      entry = RobotEquitySymbols.objects.filter(bullishSymbol=bull).filter(bearishSymbol=bear).filter(symbol=etf)

      if (entry == None) or (len(entry)==0):
        entry = RobotEquitySymbols.objects.create(name=name,bullishSymbol=bull,bearishSymbol=bear,symbol=etf,
                                        owners=owners,top_15_stocks=top_15,leverage=leverage)
      else:
        displayOutput(str="Nothing was inserted because entry was already present. Bull={} Bear={}".format(bull, bear))
      index = index+1

    return True

  def getTop15Stocks(self):
    return self.top_15_stocks

  def getBullishSymbol(self):
    return self.bullishSymbol

  def getBearishSymbol(self):
    return self.bearishSymbol

  def getSymbol(self):
    return self.symbol

  def getSymbolsPairAsPayload(self):
    payload = dict()
    payload['bull_symbol']=self.getBullishSymbol()
    payload['bear_symbol']=self.getBearishSymbol()
    payload['etf_symbol']=self.getSymbol()

    return payload

  #
  # Retrieve the most recent entry for the last hour (technically 4 hours)
  #
  @staticmethod
  def getHourlyEquitiesData(pair):
    end_date = BullBearETFData.getMostRecentEntry(pair)
    four_hours = end_date + timedelta(hours=-4)
    today = BullBearETFData.getTodayData(pair=pair,start_date=four_hours,end_date=end_date)
    return today

  @staticmethod
  def getTodayEquitiesData(pair):
    end_date = BullBearETFData.getMostRecentEntry(pair)
    start_date = end_date + timedelta(hours=-24)
    today = BullBearETFData.getTodayData(pair=pair,start_date=start_date,end_date=end_date)
    return today

  @staticmethod
  def getWeekEquitiesData(pair):
    end_date = BullBearETFData.getMostRecentEntry(pair)
    start_date = end_date + timedelta(weeks=-1)
    week = BullBearETFData.getTodayData(pair=pair,start_date=start_date,end_date=end_date)
    return week

  @staticmethod
  def getTwoWeeksEquitiesData(pair):
    end_date = BullBearETFData.getMostRecentEntry(pair)
    start_date = end_date + timedelta(weeks=-2)
    two_weeks = BullBearETFData.getTodayData(pair=pair,start_date=start_date,end_date=end_date)
    return two_weeks

  @staticmethod
  def getThreeWeeksEquitiesData(pair):
    end_date = BullBearETFData.getMostRecentEntry(pair)
    start_date = end_date + timedelta(weeks=-3)
    two_weeks = BullBearETFData.getTodayData(pair=pair,start_date=start_date,end_date=end_date)
    return two_weeks

  @staticmethod
  def getFourWeeksEquitiesData(pair):
    end_date = BullBearETFData.getMostRecentEntry(pair)
    start_date = end_date + timedelta(weeks=-4)
    two_weeks = BullBearETFData.getTodayData(pair=pair,start_date=start_date,end_date=end_date)
    return two_weeks


#
# Keeps track of all ETF Pairs and their main Index they are tracking.
#
class BullBearETFData(models.Model):
  timestamp = models.DateTimeField('date created',default=timezone.now)
  bull_price = models.FloatField(default=0)
  bear_price = models.FloatField(default=0)
  etf_price  = models.FloatField(default=0)
  bull_symbol = models.CharField(max_length=10,default='')
  bear_symbol = models.CharField(max_length=10,default='')
  etf_symbol = models.CharField(max_length=10,default='')

  def __str__(self):
    bull_entry="{0}:{1}".format(self.bull_symbol,self.bull_price)
    bear_entry="{0}:{1}".format(self.bear_symbol,self.bear_price)
    etf_entry ="{0}:{1}".format(self.etf_symbol,self.etf_price)
    return "{0} {1} {2} {3}".format(self.timestamp, bull_entry, bear_entry, etf_entry)

  def getBasicInformation(self):
    information = dict()
    information[self.bull_symbol] = self.bull_price
    information[self.bear_symbol] = self.bear_price
    information[self.etf_symbol]  = self.etf_price
    information['timestamp']      = self.timestamp.isoformat().replace('T',' ')
    return information

  ######################## Methods for Creating, Updating and Deleting Entries into the Table ###############
  @staticmethod
  def getMostRecentEntry(pair):
    end_date = datetime.now(getTimeZoneInfo()).isoformat()
    start_date = datetime.now(getTimeZoneInfo()) + timedelta(days=-30)

    pairs_query = BullBearETFData.objects.filter(bull_symbol=pair['bull_symbol'],bear_symbol=pair['bear_symbol'],etf_symbol=pair['etf_symbol'])
    time_bound = pairs_query.filter(timestamp__lte=end_date,timestamp__gte=start_date)
    most_recent = time_bound.aggregate(Max('timestamp'))['timestamp__max']
    return most_recent

  @staticmethod
  def getTodayData(pair,start_date,end_date):
    today = dict()
    pairs_query = BullBearETFData.objects.filter(bull_symbol=pair['bull_symbol'],bear_symbol=pair['bear_symbol'],etf_symbol=pair['etf_symbol'])
    time_bound = pairs_query.filter(timestamp__lte=end_date,timestamp__gte=start_date)

    today['bull_h'] = round(float(time_bound.aggregate(Max('bull_price'))['bull_price__max']),2)
    today['bull_l'] = round(float(time_bound.aggregate(Min('bull_price'))['bull_price__min']),2)
    today['bull_a'] = round(float(time_bound.aggregate(Avg('bull_price'))['bull_price__avg']),2)
    today['bull_s'] = round(abs(today['bull_h'] - today['bull_l']),2)
    today['bear_h'] = round(float(time_bound.aggregate(Max('bear_price'))['bear_price__max']),2)
    today['bear_l'] = round(float(time_bound.aggregate(Min('bear_price'))['bear_price__min']),2)
    today['bear_a'] = round(float(time_bound.aggregate(Avg('bear_price'))['bear_price__avg']),2)
    today['bear_s'] = round(abs(today['bear_h'] - today['bear_l']),2)
    today['etf_h']  = round(float(time_bound.aggregate(Max('etf_price'))['etf_price__max']),2)
    today['etf_l']  = round(float(time_bound.aggregate(Min('etf_price'))['etf_price__min']),2)
    today['etf_a']  = round(float(time_bound.aggregate(Avg('etf_price'))['etf_price__avg']),2)
    today['etf_s']  = round(abs(today['etf_h'] - today['etf_l']),2)

    return today

  ######################## Methods for Creating, Updating and Deleting Entries into the Table ###############
  @staticmethod
  def dailyDataExists(pair,start_date,end_date):
    pairs_query = BullBearETFData.objects.filter(bull_symbol=pair['bull_symbol'],bear_symbol=pair['bear_symbol'],etf_symbol=pair['etf_symbol'])
    count = pairs_query.filter(timestamp__lte=end_date,timestamp__gte=start_date).count()
    return (count>0)

  @staticmethod
  def insertTradingData(payload):
    entry = BullBearETFData.objects.create(timestamp=payload['timestamp'],bull_price=payload['bull_price'],
                                bear_price=payload['bear_price'],etf_price=payload['etf_price'], bull_symbol=payload['bull_symbol'],
                                bear_symbol=payload['bear_symbol'],etf_symbol=payload['etf_symbol'])

  @staticmethod
  def updateTradingData(payload):
    entry = BullBearETFData.objects.filter(bull_price=payload['bull_price'],bear_price=payload['bear_price'],
                                           timestamp=payload['timestamp'],bull_symbol=payload['bull_symbol'],
                                           bear_symbol=payload['bear_symbol'],etf_symbol=payload['etf_symbol'])
    if entry == None or len(entry)==0:
      BullBearETFData.objects.create(timestamp=payload['timestamp'],bull_price=payload['bull_price'],
                                     bear_price=payload['bear_price'],etf_price=payload['etf_price'], bull_symbol=payload['bull_symbol'],
                                     bear_symbol=payload['bear_symbol'],etf_symbol=payload['etf_symbol'])

    elif len(entry)==1:
      entry[0].bull_price= payload['bull_price']
      entry[0].bear_price= payload['bear_price']
      entry[0].etf_price = payload['etf_price']
      entry[0].save()
    elif len(entry)>=1:
      displayError(str="Why is the size bigger than 1? {}".format(len(entry)))

  @staticmethod
  def getDataFeed(pair,resolution='hour',start_date=None,end_date=None,use_market=True,use_pre_market=False,use_post_market=False,use_ext_pre_market=False): 
    pairs_query = BullBearETFData.objects.filter(bull_symbol=pair['bull_symbol'],bear_symbol=pair['bear_symbol'],etf_symbol=pair['etf_symbol'])
    if use_market:
      pairs_query = pairs_query.filter(timestamp__hour__gte=9).filter(timestamp__hour__lte=16)

    if resolution=='hour':
      pairs_query = pairs_query.filter(timestamp__minute=5)
    elif resolution=='day': #TODO: Implement me
      pairs_query = pairs_query.filter(timestamp__minute=5)
    elif resolution=='05min': #TODO: Implement me
      pairs_query = pairs_query.filter(timestamp__minute=5)

    if use_pre_market:
      pairs_query = pairs_query.filter(timestamp__hour__gte=7).filter(timestamp__hour__lte=9)

    if use_post_market:
      pairs_query = pairs_query.filter(timestamp__hour__gte=16).filter(timestamp__hour__lte=19)

    if use_ext_pre_market:
      pairs_query = pairs_query.filter(timestamp__hour__gte=4).filter(timestamp__hour__lte=7)

    if start_date==None and end_date==None:
      results = pairs_query.filter().order_by('timestamp')
    elif start_date==None and (not end_date==None):
      results = pairs_query.filter(timestamp__lte=end_date).order_by('timestamp')
    elif not (start_date==None) and ( end_date==None):
      results = pairs_query.filter(timestamp__gte=start_date).order_by('timestamp')
    else:
      results = pairs_query.filter(timestamp__lte=end_date,timestamp__gte=start_date).order_by('timestamp')
    return results

  @staticmethod
  def purgeIntervalEntry(start_date,end_date,pair):
    pairs_query = BullBearETFData.objects.filter(bull_symbol=pair['bull_symbol'],bear_symbol=pair['bear_symbol'],etf_symbol=pair['etf_symbol'])
    pairs_query.filter(timestamp__lte=end_date,timestamp__gte=start_date).delete()

  @staticmethod
  def purgePairEntry(pair):
    pairs_query = BullBearETFData.objects.filter(bull_symbol=pair['bull_symbol'],bear_symbol=pair['bear_symbol'],etf_symbol=pair['etf_symbol'])
    pairs_query.filter().delete()

  @staticmethod
  def purgeDatabase():
    BullBearETFData.objects.filter().delete()


# Market Sentiment and Volatility Scale .
# Helps determine the External Sentiment, Market Sentiment, Sector Sentiment, Equity Sentiment
# All functions are self contained and don't require external passing of Arguments.
# An extreme scenario is if the Circuit Breaker has been set. I.e: Dow Jone drops by %5 within # Time
# 50-50 is the basis.
# Highest value is 80-20 [or 75-25]
class EquityAndMarketSentiment(models.Model):
  external_sentiment = models.CharField(max_length=15,choices=CHOICES_SENTIMENTS_SCALE, default='Neutral')
  market_sentiment = models.CharField(max_length=15,choices=CHOICES_SENTIMENTS_SCALE, default='Neutral')
  sector_sentiment = models.CharField(max_length=15,choices=CHOICES_SENTIMENTS_SCALE, default='Neutral')
  equity_sentiment = models.CharField(max_length=15,choices=CHOICES_SENTIMENTS_SCALE, default='Neutral')

  #Sentiment influences acquisition? Boolean
  influences_acquisition = models.BooleanField(default=False)
  external_sentiment_weight = models.CharField(max_length=15,choices=CHOICES_SENTIMENTS_WEIGHT_SCALE, default='50')
  market_sentiment_weight = models.CharField(max_length=15,choices=CHOICES_SENTIMENTS_WEIGHT_SCALE, default='50')
  sector_sentiment_weight = models.CharField(max_length=15,choices=CHOICES_SENTIMENTS_WEIGHT_SCALE, default='50')
  equity_sentiment_weight = models.CharField(max_length=15,choices=CHOICES_SENTIMENTS_WEIGHT_SCALE, default='50')

  sentiment_feed = models.CharField(max_length=15,choices=CHOICES_SENTIMENTS_FEED, default='Manual')
  circuit_breaker = models.BooleanField(default=False,blank=True)

  pair_robot = models.ForeignKey('ETFAndReversePairRobot',on_delete=models.PROTECT, blank=True,null=True)

  def __str__(self):
    return "Sentiments: Ext={0} Market={1} Sector={2} Equity={3}. ID={4}".format(self.external_sentiment,self.market_sentiment,self.sector_sentiment,self.equity_sentiment,self.pk)

  def isValid(self):

    return True

  #All Sentiments are 3x bearish is crashing when all the indexes are negative and Bearish
  def isMarketCrashing(self):
    crashing = (self.external_sentiment == '3x Bearish') and (self.external_sentiment == '3x Bearish') and \
               (self.sector_sentiment == '3x Bearish') and (self.equity_sentiment == '3x Bearish')

    return crashing

  #Returns True, if the Circuit Breaker has been set.
  def isCircuitBreakerEnabled(self):
    return self.circuit_breaker

  def calculateValues(self):
    #Reverse the tuple (1,'key') ==> ('key',1) to simplify indexed access.
    if not self.influences_acquisition:
      return 0

    R_SENTIMENTS_SCALE = getReversedTuple(tuple_data=CHOICES_SENTIMENTS_SCALE)
    R_SENTIMENTS_WEIGHT_SCALE = getReversedTuple(tuple_data=CHOICES_SENTIMENTS_WEIGHT_SCALE)

    value = R_SENTIMENTS_SCALE[self.external_sentiment] * R_SENTIMENTS_WEIGHT_SCALE[self.external_sentiment_weight] + \
            R_SENTIMENTS_SCALE[self.market_sentiment] * R_SENTIMENTS_WEIGHT_SCALE[self.market_sentiment_weight]     + \
            R_SENTIMENTS_SCALE[self.sector_sentiment] * R_SENTIMENTS_WEIGHT_SCALE[self.sector_sentiment_weight]     + \
            R_SENTIMENTS_SCALE[self.equity_sentiment] * R_SENTIMENTS_WEIGHT_SCALE[self.equity_sentiment_weight]

    return value

  def getBullishComposition(self):
    #[-1200, +1200] 80/20[-1200,-1000], 75/25[-1000,-800] 70/30[-800,-600] 60/40[-600,-150], 50/50[-150,150],
                  #[40/60[150-600], 30/70[600,800], 25/75[800,1000], 20/80[1000,1200]
    value_range = [-1200, -1000, -800, -600, -300, 300, 600, 800, 1000, 1200]
    value = self.calculateValues()
    if  (value_range[0] <= value < value_range[1]):
      bullish_composition = 20
    elif (value_range[1] <= value < value_range[2]):
      bullish_composition = 25
    elif (value_range[2] <= value < value_range[3]):
      bullish_composition = 30
    elif (value_range[3] <= value < value_range[4]):
      bullish_composition = 40
    elif (value_range[4] <= value < value_range[5]):
      bullish_composition = 50
    elif (value_range[5] <= value < value_range[6]):
      bullish_composition = 60
    elif (value_range[6] <= value < value_range[7]):
      bullish_composition = 70
    elif (value_range[7] <= value < value_range[8]):
      bullish_composition = 75
    elif (value_range[8] <= value <= value_range[9]):
      bullish_composition = 80

    return bullish_composition

  def getBearishComposition(self):
    return 100 - self.getBullishComposition()

