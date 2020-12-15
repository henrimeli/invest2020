from django.db import models
from django.urls import reverse
from django.utils import timezone
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, strToDatetime, shouldUsePrint, displayOutput,displayError

CHOICES_BROKERAGE_PAPER = (('Local Account','Local Account'),('eTrade Regular','eTrade Regular'),('eTrade Retirement','eTrade Retirement'),('Alpaca','Alpaca'),('Ameritrade','Ameritrade'))
CHOICES_BROKERAGE_LIVE = (('Local Account','Local Account'),('eTrade Regular','eTrade Regular'),('eTrade Retirement','eTrade Retirement'),('Alpaca','Alpaca'),('Ameritrade','Ameritrade'))

"""
  TODO: Describe the Module here ...

  List the classes of the module here
"""

#Markets: Symbols information, symbols groups (nasdaq 3x, dow jones 2x, ), 
# business hours, brokerage, volatility, 
# Keeps track of Market specific data.
# Ideally, we would like to get this from an API
class BrokerageInformation(models.Model):
  """
    TODO: Describe the purpose of the class here

    List all methods of the class here
  """
  name = models.CharField(default='',max_length=20)
  website = models.CharField(default='',max_length=20)
  connection_type = models.CharField(default='',max_length=20)
  connection_API_Key = models.CharField(default='',max_length=20)
  brokerage_type = models.CharField(max_length=20, choices = CHOICES_BROKERAGE_PAPER,default='Alpaca',)

  def __str__(self):
    return "{0} ".format(self.name)

  def isETradeRegular(self):
    R_CHOICES_BROKERAGE_PAPER = getReversedTuple(tuple_data=CHOICES_BROKERAGE_PAPER)
    value = R_CHOICES_BROKERAGE_PAPER[self.brokerage_type]
    return value == 'eTrade Regular' 

  def isAlpaca(self):
    R_CHOICES_BROKERAGE_PAPER = getReversedTuple(tuple_data=CHOICES_BROKERAGE_PAPER)
    value = R_CHOICES_BROKERAGE_PAPER[self.brokerage_type]
    return value == 'Alpaca' 

  def isAmeritrade(self):
    R_CHOICES_BROKERAGE_PAPER = getReversedTuple(tuple_data=CHOICES_BROKERAGE_PAPER)
    value = R_CHOICES_BROKERAGE_PAPER[self.brokerage_type]
    return value == 'Ameritrade' 

  def isETradeRetirement(self):
    R_CHOICES_BROKERAGE_PAPER = getReversedTuple(tuple_data=CHOICES_BROKERAGE_PAPER)
    value = R_CHOICES_BROKERAGE_PAPER[self.brokerage_type]
    return value == 'eTrade Retirement' 

  def isLocal(self):
    R_CHOICES_BROKERAGE_PAPER = getReversedTuple(tuple_data=CHOICES_BROKERAGE_PAPER)
    value = R_CHOICES_BROKERAGE_PAPER[self.brokerage_type]
    return value == 'Local Account' 

