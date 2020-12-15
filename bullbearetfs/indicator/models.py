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

CHOICES_INDICATOR_CLASS=(('Manual Indicator','Manual Indicator'),('Technical Indicator','Technical Indicator'),\
                         ('Volume Indicator','Volume Indicator'),('Time Indicator','Time Indicator'),\
                         ('Profit Indicator','Profit Indicator'),('Circuit Breaker','Circuit Breaker'),\
                         ('Immediate Indicator','Immediate Indicator'))

CHOICES_INDICATOR_FAMILY = (('SMA','Simple Moving Average'),('EMA','Exponential Moving Average'),('OSC','Oscillator'),\
                            ('RSA','Relative Strength Index'),('Fibonacci','Fibonacci'),('STD','Standard Deviation'),
                            ('Triggers','Triggers'))
CHOICES_TRESHOLD_TO_MARKET_OPEN = (('5','5'),('15','15'),('30','30'),('45','45'),('60','60'))
CHOICES_TRESHOLD_TO_VOLUME_ON_OPEN = (('1 Million','1 Million'),('2 Millions','2 Millions'))
CHOICES_TIME_INTERVAL = (('30','30'),('45','45'),('60','60'),('90','90'),('120','120'))
CHOICES_VOLUME_INTERVAL = (('10% Average Volume','10% Average Volume'),('15% Average Volume','15% Average Volume'),('20% Average Volume','20% Average Volume'),('25% Average Volume','25% Average Volume'))

class EquityIndicator(models.Model):
  """
    TODO: Equity Indicator class is used to ...
  """
  name = models.CharField(max_length=50,default='')
  description = models.CharField(max_length=100,default='')
  indicator_class =  models.CharField(max_length=25,choices=CHOICES_INDICATOR_CLASS, default='Time Indicator')
  indicator_family= models.CharField(max_length=25,choices=CHOICES_INDICATOR_FAMILY, default='Triggers')

  creation_date = models.DateTimeField('date created',default=timezone.now)
  modify_date = models.DateTimeField('date created',default=timezone.now)
  modified_by = models.ForeignKey('CustomerBasic',on_delete=models.PROTECT, blank=True,null=True)
  owner = models.ForeignKey('Customer',on_delete=models.PROTECT, blank=True,null=True)
  visibility = models.BooleanField(default=True)

  treshold_to_market_open = models.CharField(max_length=25,choices=CHOICES_TRESHOLD_TO_MARKET_OPEN, default='15')
  treshold_to_volume_open =models.CharField(max_length=25,choices=CHOICES_TRESHOLD_TO_VOLUME_ON_OPEN, default='1 Million')
  volume_interval = models.CharField(max_length=25,choices=CHOICES_VOLUME_INTERVAL, default='10% Average Volume')
  time_interval = models.CharField(max_length=25,choices=CHOICES_TIME_INTERVAL, default='60')

  reset_on_start = models.BooleanField(default=True)
  reset_daily = models.BooleanField(default=True)
  use_robot_symbol = models.BooleanField(default=True)
      
  def __str__(self):
    return "{0} ".format(self.name)

#returns True, if the Indicator has been triggered based on the parameters passed.
#If a timeIndicator, isTriggered (param1=lastsuccessful_time,param2=now)
#if a VolumeIndicator, isTriggered(param1=, param2=current volume)
#if a manual indicator isTriggerred(): returns True, if the checkBox is checked.
#if a technical Indicator, isTriggerred(): returns True, if
#if a circuit Breaker Indicator, isTriggerred(): 
#I need to pass the robotID, so that I know which robot is calling.
  def isTriggered(self,**kwargs):
    isTriggered = False
    if not self.isValid():
      return False

    if self.indicator_class == 'Manual Indicator':
      if 'manual_check' in kwargs:
        manual_check = kwargs['manual_check']
        if manual_check == True:  
          isTriggered = True

    # 5 variables:  self.treshold_to_volume (self.lowest_volume), self.volume_interval
    #last_successful, current_volume, average_volume
    elif self.indicator_class == 'Volume Indicator':
      if 'last_successful' in kwargs and 'current_volume' in kwargs and 'average_volume' in kwargs:
        last_successful = kwargs['last_successful']
        current_volume = kwargs['current_volume']
        average_volume = kwargs['average_volume']
        if current_volume < self.getLowestVolume():
          isTriggered = False
        else:
          interval = self.getVolumeInterval(average_volume=average_volume)  
          if current_volume - last_successful >= interval:
            isTriggered = True
    # Making the assumption that. I'm within market trading hours and outside blackout times
    # specified in the RobotWindowTime Management. The Robot is responsible for that.
    elif self.indicator_class == 'Time Indicator':
      if 'last_successful' in kwargs and 'current_time' in kwargs:
        last_successful = kwargs['last_successful']
        current_time = kwargs['current_time']
        interval = current_time - last_successful
        #now_time = current_time

        actual_interval = datetime.timedelta(minutes=self.time_interval)

        #self.time_interval
        #Know market opening time.
        #Know my own blackout time
        if interval >  actual_interval:
          isTriggered = False;
        else:
          #TODO:Henri now_time - last_successful >= self.time_interval:
          isTriggered = True

    elif self.indicator_class == 'Circuit Breaker':
      if 'circuit_breaker_check' in kwargs:
        circuit_breaker = kwargs['circuit_breaker_check']
        if circuit_breaker:
          isTriggered = True
    elif self.indicator_class == 'Immediate Indicator':
      if 'immediate_check' in kwargs:
        immediate_check = kwargs['immediate_check']
        if immediate_check:
          isTriggered = True
   #2 scenarios TQQQ + SQQQ.
   # 1. First Sale: Profit_exit (TQQQ or SQQQ)
   # 2. Second Sale Exit_to_close()
    elif self.indicator_class == 'Profit Indicator':
      if 'current_stock_price' in kwargs and 'acquisition_stock_price' in kwargs \
        and 'number_of_shares' in kwargs and 'minimum_profit' in kwargs:
        current_stock_price = kwargs['current_stock_price']
        acquisition_stock_price = kwargs['acquisition_stock_price']
        number_of_shares = kwargs['number_of_shares']
        minimum_profit = kwargs['minimum_profit']

        if (current_stock_price - acquisition_stock_price)*number_of_shares > minimum_profit:
          isTriggered = True

    elif self.indicator_class == 'Technical Indicator':
      if 'indicator' in kwargs:
        indicator = kwargs['indicator']
        if indicator == 'macd' and 'volume' in kwargs and 'timeframe' in kwargs:
          algo = 'macd'
          volume = kwargs['volume']
          timeframe = kwargs['timeframe']
          isTriggered = True


    return isTriggered

  #
  # Calculate the Lowest Volume by converting human readable to number
  # TODO: Add Unit Tests
  def getLowestVolume(self):
    if self.treshold_to_volume_open == '1 Million':
      return 1000000
    elif self.treshold_to_volume_open == '2 Millions':
      return 2000000
    else:
      return 2000000

  #
  # Calculate the Average Volume Fonction
  # TODO: Add Unit Tests
  def getVolumeInterval(self,average_volume):
    average_volume = average_volume or None 
    if self.volume_interval == '10% Average Volume':
      return average_volume * .1
    elif self.volume_interval == '15% Average Volume':
      return average_volume * .15
    else:
      return average_volume
#
# isValid() checks to see if an Indicator is valid or not
#
  def isValid(self):
    isValid = False;

    if (self.indicator_class == 'Manual Indicator' or self.indicator_class == 'Profit Indicator' or \
      self.indicator_class == 'Volume Indicator' or self.indicator_class == 'Time Indicator' or \
      self.indicator_class == 'Circuit Breaker' or self.indicator_class == 'As Soon as Possible') or \
      self.indicator_class == 'Immediate Indicator':
      if self.indicator_family == 'Triggers':
        isValid = True
    elif self.indicator_class == 'Technical Indicator':
      if not (self.indicator_family == 'Triggers'):
        isValid = True

    return isValid


# ######################## Dashboard #############

class IndicatorDummy(models.Model):
  subject = models.CharField(max_length=50,default='')
  email = models.EmailField()
  comment = models.TextField()

  def __str__(self):
    return "{0} {1} ".format(self.email,self.subject)
