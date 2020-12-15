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

"""
  TODO: Describe the Module here ...

  List the classes of the module here
"""
logger = logging.getLogger(__name__)


class BusinessIntelligence(models.Model):
  """
    This class leverages data to help make better acquisition decisions
  """
  name = models.CharField(max_length=20,default='')
  value = models.IntegerField(default=0)

  def __str__(self):
    return "{0} {1} ".format(self.name, self.value)
