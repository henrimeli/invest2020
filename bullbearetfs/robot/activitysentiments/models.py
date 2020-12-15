from django.db import models
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
from random import uniform


"""
TODO: Describe the Module here. 

List all classes here

"""


logger = logging.getLogger(__name__)


CHOICES_MARKET_TIMEZONE = (('EST','EST'),('EURO','EURO'),('24_7','24_7'))

CHOICES_BLACKOUT_WINDOW=(('0','0'),('15','15'),('30','30'),('45','45'),('60','60'))
CHOICES_MIDDAY_BLACKOUT_START=(('0','0'),('10','10:00am'),('11','11:00am'),('12','12:00pm'),('13','13:00pm'),('14','2:00pm'),('15','3:00pm'))
CHOICES_VOLATILITY_SCALE=(('High','High'),('Medium','Medium'),('Low','Low'),('None','None'),('Not Available','Not Available'))
CHOICES_SENTIMENTS_SCALE=((-3,'3x Bearish'),(-2,'2x Bearish'),(-1,'1x Bearish'),(0,'Neutral'),
                          (1,'1x Bullish'),(2,'2x Bullish'),(3,'3x Bullish'))
CHOICES_SENTIMENTS_WEIGHT_SCALE=((100,'100'),(50,'50'),(0,'0'))
CHOICES_SENTIMENTS_FEED  = (('Automatic','Automatic'),('Manual','Manual'),('Defer to Strategy','Defer to Strategy'))
CHOICES_COMPOSITION_CALCULATION  = (('Random','Random'),('A1','A1'),('A2','A2'),('A3','A3'),('A4','A4'),('A5','A5'),('A6','A6'))
CHOICES_LIVE_DATA_FEED=(('Polygon','Polygon'),('Not Yet Implemented','Not Yet Implemented'))


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
  """
    Describe the class here
  """
  name = models.CharField(max_length=20,default='',blank=True)
  time_zone = models.CharField(max_length=10, choices = CHOICES_MARKET_TIMEZONE,default='EST')
  opening_time = models.DateTimeField('date created',default=timezone.now) 
  closing_time = models.DateTimeField('date created',default=timezone.now)

  def __str__(self):
    return "Opens={1}. Day:{2}.".format(self.marketisOpenToday, self.name)

    
  @staticmethod
  def isWithinPreMarketHours(current_time=None):
    """TODO: Describe the method here """
    now = datetime.now(getTimeZoneInfo()) if (current_time==None) else current_time  
    date_only = now.date()

    if not MarketBusinessHours.isOpen(current_date=date_only):
      return False
    
    o_premkt = datetime(date_only.year,date_only.month,date_only.day,7,00,00,tzinfo=getTimeZoneInfo())
    c_premkt = datetime(date_only.year,date_only.month,date_only.day,9,30,00,tzinfo=getTimeZoneInfo())

    answer = o_premkt <= current_time <= c_premkt
    return answer

  @staticmethod
  def isWithinExtendedPreMarketHours(current_time=None):
    """TODO: Describe the method here """
    now = datetime.now(getTimeZoneInfo()) if (current_time==None) else current_time  
    date_only = now.date()

    if not MarketBusinessHours.isOpen(current_date=date_only):
      return False
    
    o_ext_premkt = datetime(date_only.year,date_only.month,date_only.day,4,00,00,tzinfo=getTimeZoneInfo())
    c_ext_premkt = datetime(date_only.year,date_only.month,date_only.day,7,00,00,tzinfo=getTimeZoneInfo())

    answer = o_ext_premkt <= current_time <= c_ext_premkt
    return answer

  @staticmethod
  def isWithinMarketHours(current_time=None):
    """TODO: Describe the method here """
    now = datetime.now(getTimeZoneInfo()) if (current_time==None) else current_time  
    date_only = now.date()

    if not MarketBusinessHours.isOpen(current_date=date_only):
      return False
    
    o_mkt = datetime(date_only.year,date_only.month,date_only.day,9,30,00,tzinfo=getTimeZoneInfo())
    c_mkt = datetime(date_only.year,date_only.month,date_only.day,16,00,00,tzinfo=getTimeZoneInfo())

    answer = o_mkt <= current_time <= c_mkt
    return answer

  @staticmethod
  def isWithinAfterMarketHours(current_time=None):
    """TODO: Describe the method here """
    now = datetime.now(getTimeZoneInfo()) if (current_time==None) else current_time  
    date_only = now.date()

    if not MarketBusinessHours.isOpen(current_date=date_only):
      return False
    
    o_post_mkt = datetime(date_only.year,date_only.month,date_only.day,16,00,00,tzinfo=getTimeZoneInfo())
    c_post_mkt = datetime(date_only.year,date_only.month,date_only.day,19,00,00,tzinfo=getTimeZoneInfo())

    answer = o_post_mkt <= current_time <= c_post_mkt
    return answer


  @staticmethod
  def isMarketOpenToday(self):
    """TODO: Describe the method here """
    today = date.today()
    return MarketBusinessHours.isOpen(start_date=today)

  #
  #
  @staticmethod
  def isOpen(current_date=None):
    """TODO: Describe the method here """
    now = date.today() if (current_date==None) else date(current_date.year,  current_date.month,current_date.day)
    if now.weekday()==5 or now.weekday()==6:
      return False

    holidays_of_year = holidays.UnitedStates(years=now.year).items()
    for year in holidays_of_year:
      if now == year[0]:
        return False

    return True

# Robot's activity window
# This should go hand in hand with the MarketInformation Tabls.
# Parameters: {'now':<date>} .
# Returns: if now is outside the Set Window,
class RobotActivityWindow(models.Model):
  """
    Describe the class here
  """
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
    """TODO: Describe the method here """
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
    """TODO: Describe the method here """
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
    """TODO: Describe the method here """
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


# Market Sentiment and Volatility Scale .
# Helps determine the External Sentiment, Market Sentiment, Sector Sentiment, Equity Sentiment
# All functions are self contained and don't require external passing of Arguments.
# An extreme scenario is if the Circuit Breaker has been set. I.e: Dow Jone drops by %5 within # Time
# 50-50 is the basis. 
# Highest value is 80-20 [or 75-25]
#CHOICES_COMPOSITION_CALCULATION
class EquityAndMarketSentiment(models.Model):
  """
    Describe the class here
  """
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

  sentiment_feed = models.CharField(max_length=20,choices=CHOICES_SENTIMENTS_FEED, default='Manual')
  composition_calc = models.CharField(max_length=25,choices=CHOICES_COMPOSITION_CALCULATION, default='Random')
  circuit_breaker = models.BooleanField(default=False,blank=True)
  ignore_neutral_outcome = models.BooleanField(default=True)

  pair_robot = models.ForeignKey('ETFAndReversePairRobot',on_delete=models.PROTECT, blank=True,null=True)
  
  value_range = [-1200, -1000, -800, -600, -300, 300, 600, 800, 1000, 1200]
  
  new_value_range = [-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7]

  last_saved_direction = 0

  current_trend = None 

  def __str__(self):
    return "Sentiments: Ext={0} Market={1} Sector={2} Equity={3}. ID={4}".format(self.external_sentiment,self.market_sentiment,self.sector_sentiment,self.equity_sentiment,self.pk)

  def isValid(self):

    return True

  #All Sentiments are 3x bearish is crashing when all the indexes are negative and Bearish
  def isMarketCrashing(self):
    """TODO: Describe the method here """
    crashing = (self.external_sentiment == '3x Bearish') and (self.external_sentiment == '3x Bearish') and \
               (self.sector_sentiment == '3x Bearish') and (self.equity_sentiment == '3x Bearish')

    return crashing

  #Returns True, if the Circuit Breaker has been set.
  def isCircuitBreakerEnabled(self):  
    """TODO: Describe the method here """
    return self.circuit_breaker

  #
  #  Allows to calculate based on some knowledge based values
  #
  def calculateKnowledgeBasedValue(self):
    """TODO: Describe the method here """
    #print("Calculate based on knowledge Base. Current Trend = {}".format(self.current_trend))
    if self.current_trend is not None and self.current_trend['type']=='stable_value_spread':

      if self.current_trend['spread_total_value'] < 0 :   # Our Spread it outside our comfort zone
        if self.current_trend['current_bull_composition'] >= self.current_trend['current_bear_composition']:
          value = self.calculateAnyRandomValue(left_side=-1200,right_side=-600)
          #print("Currently Negative. Higher Bull Composition ... we need more Bears {}".format(value))
        else:
          value = self.calculateAnyRandomValue(left_side=600,right_side=1200)
          #print("Currently Negative. Higher Bear Composition ... we need more Bulls{}".format(value))

      else:   # Our Spread is within out comfort zone
        if self.current_trend['current_bull_composition'] >= self.current_trend['current_bear_composition']:
          value = self.calculateAnyRandomValue(left_side=600,right_side=1200)
          #print("Currently Positive. Higher Bull Composition ... we need more Bears{}".format(value))
        else:
          value = self.calculateAnyRandomValue(left_side=-1200,right_side=-600)
          #print("Higher Bear Composition ... we need more Bulls{}".format(value))

    return value

  #
  #  Calculate the Weighted Moving Average.
  #  The data used to calculate is in the self.current_trend
  #
  def eggheadWeightedMovingAverage(self):
    """TODO: Describe the method here """
    return None if self.pair_robot==None else self.pair_robot.calculateEMA(use_transition=False)

  #
  #  Calculate the Exponential Moving Average.
  #  The data used to calculate is in the self.current_trend
  #
  def eggheadExponentialMovingAverage(self):
    """TODO: Describe the method here """
    return None if self.pair_robot==None else self.pair_robot.calculateEMA(use_transition=False)
    

  #
  #  Calculate the Simple Moving Average.
  #  The data used to calculate is in the self.current_trend
  #
  def eggheadWeightedSimpleAverage(self,ignore_previous=False):
    """TODO: Describe the method here """
    return None if self.pair_robot==None else self.pair_robot.calculateSMA(use_transition=False)

  #
  # Pick any random number between [-1200 , +1200]
  # Numbers must alternate between positive and negative values
  #
  def calculateAlternateRandomValue(self):
    """TODO: Describe the method here """
    #[-1200, +1200] Total Range:
    #[80/20[-1200,-1000], 75/25[-1000,-800] 70/30[-800,-600] 60/40[-600,-150], 50/50[-150,150], 
    #[40/60[150-600],     30/70[600,800],   25/75[800,1000], 20/80[1000,1200]
    if self.last_saved_direction == 0:
      value = self.calculateAnyRandomValue(left_side=-1200,right_side=1200)
    elif self.last_saved_direction > 0:
      value = self.calculateAnyRandomValue(left_side=-1200,right_side=0)
    elif self.last_saved_direction <0 :
      value = self.calculateAnyRandomValue(left_side=0,right_side=1200)

    self.last_saved_direction = 1 if (value > 0) else -1
    return value

  #
  # Pick any random number between [-1200 , +1200]
  #
  def calculateAnyRandomValue(self,left_side=-1200,right_side=1200):
    """TODO: Describe the method here """
    #[-1200, +1200] Total Range:
    #[80/20[-1200,-1000], 75/25[-1000,-800] 70/30[-800,-600] 60/40[-600,-150], 50/50[-150,150], 
    #[40/60[150-600],     30/70[600,800],   25/75[800,1000], 20/80[1000,1200]
    value = uniform(left_side,right_side)
    if not self.ignore_neutral_outcome:
      return value

    if not self.isNeutral(value=value):
      return value 
    
    while self.isNeutral(value=value):
      value = uniform(left_side,right_side)

    return value

  #
  # Sometimes, we don't want 50/50 propositions
  #
  def isNeutral(self,value):
    """TODO: Describe the method here """
    if (self.value_range[4] <= value < self.value_range[5]):
      return True
    return False 

  #
  #
  #
  #
  #Reverse the tuple (1,'key') ==> ('key',1) to simplify indexed access.
  #CHOICES_COMPOSITION_CALCULATION  = (('Random','Random'),('A1','A1'),('A2','A2'),('A3','A3'),('A4','A4'),('A5','A5'),('A6','A6'))
  def calculateValues(self):
    """TODO: Describe the method here """
    if not self.influences_acquisition:
      return 0 

    if self.sentiment_feed == 'Manual':
      R_SENTIMENTS_SCALE = getReversedTuple(tuple_data=CHOICES_SENTIMENTS_SCALE)
      R_SENTIMENTS_WEIGHT_SCALE = getReversedTuple(tuple_data=CHOICES_SENTIMENTS_WEIGHT_SCALE)

      value = R_SENTIMENTS_SCALE[self.external_sentiment] * R_SENTIMENTS_WEIGHT_SCALE[self.external_sentiment_weight] + \
              R_SENTIMENTS_SCALE[self.market_sentiment] * R_SENTIMENTS_WEIGHT_SCALE[self.market_sentiment_weight]     + \
              R_SENTIMENTS_SCALE[self.sector_sentiment] * R_SENTIMENTS_WEIGHT_SCALE[self.sector_sentiment_weight]     + \
              R_SENTIMENTS_SCALE[self.equity_sentiment] * R_SENTIMENTS_WEIGHT_SCALE[self.equity_sentiment_weight]     
      return value 

    elif self.sentiment_feed == 'Automatic': 
      if self.composition_calc == 'Random':
        return self.calculateAnyRandomValue()
      elif self.composition_calc == 'A1':
        return 0 if self.pair_robot==None else self.pair_robot.calculateSMA(use_transition=False)
      elif self.composition_calc == 'A2':
        return 0 if self.pair_robot==None else self.pair_robot.calculateEMA(use_transition=False)
      elif self.composition_calc == 'A3':
        return self.calculateAlternateRandomValue()
      elif self.composition_calc == 'A4':
        return self.calculateKnowledgeBasedValue()

    return 0  

  def getBullishComposition(self):
    """TODO: Describe the method here """
    #[-1200, +1200] 80/20[-1200,-1000], 75/25[-1000,-800] 70/30[-800,-600] 60/40[-600,-150], 50/50[-150,150], 
                  #[40/60[150-600], 30/70[600,800], 25/75[800,1000], 20/80[1000,1200]
    #value_range = [-1200, -1000, -800, -600, -300, 300, 600, 800, 1000, 1200]
    value = self.calculateValues()
    if  (self.value_range[0] <= value < self.value_range[1]):
      b_c = 20
    elif (self.value_range[1] <= value < self.value_range[2]):
      b_c = 25
    elif (self.value_range[2] <= value < self.value_range[3]):
      b_c = 30
    elif (self.value_range[3] <= value < self.value_range[4]):
      b_c = 40
    elif (self.value_range[4] <= value < self.value_range[5]):
      b_c = 50
    elif (self.value_range[5] <= value < self.value_range[6]):
      b_c = 60
    elif (self.value_range[6] <= value < self.value_range[7]):
      b_c = 70
    elif (self.value_range[7] <= value < self.value_range[8]):
      b_c = 75 
    elif (self.value_range[8] <= value <= self.value_range[9]):
      b_c = 80
    
    return b_c

  def getBalancedAssetComposition(self):
    """
    Returns a 50/50 asset composition.
    """
    composition = dict()
    composition['bull'] = 50
    composition['bear'] = 100 - composition['bull']
    return composition

  #def getBearishComposition(self):
  #  return 100 - self.getBullishComposition()

  def getAssetComposition(self,current_trend=None):
    """TODO: Describe the method here """
    if current_trend != None :
      self.current_trend = current_trend

    composition = dict()
    composition['bull'] = self.getBullishComposition()
    composition['bear'] = 100 - composition['bull']

    self.current_trend = None 
    return composition
