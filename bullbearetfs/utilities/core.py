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

  if isinstance(business_day,datetime):
    return business_day

  displayOutput(str="business_day is a string type. Convert to datetime {0} {1} {2}".format(type(business_day),h1,h2))
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
    if loggerLevelIsInfo():
      logger.info(str)
    elif loggerLevelIsDebug():
      logger.debug(str)
    elif loggerLevelIsTrace():
      logger.trace(str)
    elif loggerLevelIsWarning():
      logger.warn(str)
    elif loggerLevelIsError():
      logger.error(str)
    elif loggerLevelIsOFF():
      pass
    elif loggerLevelIsFatal():
      logger.fatal(str)


def shouldUseReportLevel3():
  report_level=environ.get('REPORT_LEVEL')
  return True if ( report_level is not None) and (report_level.upper()=='LEVEL_3' or report_level.upper()=='LEVEL3' ) else False

def shouldUseReportLevel2():
  report_level=environ.get('REPORT_LEVEL')
  return True if ( report_level is not None) and (report_level.upper()=='LEVEL_2' or report_level.upper()=='LEVEL2') else False

def shouldUseReportLevel1():
  report_level=environ.get('REPORT_LEVEL')
  return True if ( report_level is not None) and (report_level.upper()=='LEVEL_1' or report_level.upper()=='LEVEL1') else False

def shouldUseReportLevel0():
  report_level=environ.get('REPORT_LEVEL')
  return True if ( report_level is not None) and (report_level.upper()=='LEVEL_0' or report_level.upper()=='LEVEL0') else False

def shouldUseReportLevelOFF():
  return shouldUseReportLevel0()


def shouldUsePrint():
  return True if (environ.get('PRINT_VAR') is not None) else False

def shouldUseLogger():
  return True if (environ.get('LOGGER_VAR') is not None) else False

def loggerLevelIsInfo():
  logger_level=environ.get('LOGGER_LEVEL')  
  return True if (logger_level is not None) and (logger_level.upper() == 'INFO') else False

def loggerLevelIsDebug():
  logger_level=environ.get('LOGGER_LEVEL')  
  return True if (logger_level is not None) and (logger_level.upper() == 'DEBUG') else False

def loggerLevelIsTrace():
  logger_level=environ.get('LOGGER_LEVEL')  
  return True if (logger_level is not None) and (logger_level.upper() == 'TRACE') else False

def loggerLevelIsWarning():
  logger_level=environ.get('LOGGER_LEVEL')  
  return True if (logger_level is not None) and (logger_level.upper() == 'WARN') else False

def loggerLevelIsError():
  logger_level=environ.get('LOGGER_LEVEL')  
  return True if (logger_level is not None) and (logger_level.upper()=='ERROR') else False

def loggerLevelIsOFF():
  logger_level=environ.get('LOGGER_LEVEL')  
  return True if (logger_level is not None) and (logger_level.upper()=='OFF') else False

