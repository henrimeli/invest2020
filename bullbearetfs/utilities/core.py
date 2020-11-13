from django.utils import timezone
import os , sys
from os import environ
import logging, json, time, pytz, asyncio
from datetime import datetime

#
# Single location to setup the Timezone information.
#
def getTimeZoneInfo():
  return timezone.utc

def getCurrentTimeZonInfo():
  return timezone.get_current_timezone()

#
# Reverses the content of a tuple. 
# I.e.: (1,'some data') ==> ('some data',1)
# This makes it possible to access the tuple via key.
# NOTE: The reason the original tuple needs to be (1,'value') is because of the display on the UI
#
def getReversedTuple(tuple_data):
  #logger.info(" Reversed Tuple ... ")
  reversed = {y: x for x, y in tuple_data}
  return reversed 
  
########################################Can we Delete this ##################
def fixupMyDateTime(self,candidate):
  candidate=candidate
  return datetime.now(timezone.utc)

def strToDatetime(business_day):
  dt_object = datetime.strptime(business_day,"%Y-%m-%d %H:%M:%S%z")
  return dt_object

def makeAware(date_str):
  date_object.replace(tzinfo=timezone.get_current_timezone())
  return me

def timezoneAwareDate(business_day):
  h1 = isinstance(business_day, datetime)  
  h2 = isinstance(business_day, str)

  displayOutput(str="Henri ---> TYPE: {0} {1} {2}".format(type(business_day),h1,h2))
  if isinstance(business_day,datetime):
    return business_day

  dt_object = datetime.strptime(business_day,"%Y-%m-%d %H:%M:%S%z")
  return dt_object

def displayError(str=None):
  if shouldUsePrint():
    print(str)
  elif shouldUseLogger():
    logger.error(str)

def displayOutput(str=None):
  if shouldUsePrint():
    print(str)
  elif shouldUseLogger():
    logger.info(str)

def shouldUsePrint():
  return True if (environ.get('PRINT_VAR') is not None) else False

def shouldUseLogger():
  return True if (environ.get('LOGGER_VAR') is not None) else False

