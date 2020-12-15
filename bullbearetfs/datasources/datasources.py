from django.utils import timezone
from django.apps import apps
import os
from os import environ
import logging, json, time, pytz, asyncio
from datetime import datetime
from datetime import date
import datetime, time,pytz
import logging, unittest,sys,json
import pandas as pd
from django.utils import timezone
from django.test import TestCase
import dateutil.parser
# Import Models
from bullbearetfs.robot.activitysentiments.models import MarketBusinessHours, RobotActivityWindow, EquityAndMarketSentiment
from bullbearetfs.robot.symbols.models import BullBearETFData, RobotEquitySymbols
from bullbearetfs.strategy.models import EquityStrategy,PortfolioProtectionPolicy
from bullbearetfs.brokerages.alpaca import AlpacaAPIBase, AlpacaLastTrade, AlpacaPolygon, AlpacaMarketClock
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, shouldUsePrint,displayOutput,displayError,strToDatetime
#from bullbearetfs.utilities.orders import RobotSellOrderExecutor, RobotBuyOrderExecutor
#from bullbearetfs.models import CHOICES_SENTIMENTS_SCALE, CHOICES_SENTIMENTS_WEIGHT_SCALE, CHOICES_SENTIMENTS_FEED

logger = logging.getLogger(__name__)

    #############################################################################################################
    # Specify the Trading window
    # DO NOT DELETE: How to convert time back and forth: MUST
    #  How to pull quotes by the minutes and millisecond based on Alpaca API
    # This is critical to save you millions of hours ... dealing with time and timezones in messy. Very messy
    # https://github.com/alpacahq/alpaca-trade-api-python
    # I need a function to manupulate this easily for me.
    # Here is a greate referene documentation for Pandas:
    # https://www.datacamp.com/community/tutorials/pandas-tutorial-dataframe-python
    # PLEASE ALWAYS USE BOTH REFERENCES.
    #############################################################################################################

##############################################################################################################
# The purpose of the Backtest Infrastructure is to play automate the process of getting the data needed for:
# -Local BackTesting (downloadAndStore)
# -Clear the Basic Tables
# -Repopulate the Basic Tables 
# -Feed the robot and the various tests with Data needed for simulation.
#  Some of the tasks can be configured to run on various schedules to validate a variety of things ...
# 
# This class will be invoked via an interface coming from the command line.
# application_config.sh: This file contains environment variables for the system. Such as Location of tests, location of config
# config_egghead.json {'entries':'2','data':[{'bull':'',bear:,etf:'',start_date:'',end_date:'',},{},{},{},{}]}
# Download the data for the given time window, symbols and interval and store it onto the filesystem
# Use the data to populate some tables in the sytem (EquityTradingData)
# Use the data to feed a robot to run some validation and spit out the result.
# Clean up the Tables on the System and reload new sets of data
# Expand this concept to deal with Paper Data
# Ideally, we would like to download the data every week (Sunday or Saturday).
# Replace the weekly data automatically
# Keep the Data for the last 28 days (4 weeks) as fresh as possible.
# Some functions to have: 
#   DownloadAndStore()[config file with list of things to download]
#   Clear the Basic Tables [ knows already which ones are the basic tables ]
#   Populate the Basic Tables [ knows already which ones are the basic tables ]
#   Feed the Robot [ provide me the bull, bear, current time ]
class DownloadableETFBullBear():
  def __init__(self,payload=None):
    self.payload = payload
    self.valid=False

  #
  # Download and save the data into the right folder.
  #
  def isValid(self):
    return self.valid

  def getNextTradingWindow(self,count=1, resolution='minutes', trading_unit=1):
    count = count
    trading_unit = trading_unit
    resolution = resolution
    unit = 1
    if resolution == 'minutes':
      unit = 1
    elif resolution == 'hours':
      unit = 60
    return count + (unit * trading_unit) 

  def getTradingInformation(self,index):
    information = dict()
    information['etf_symbol']= self.payload['etf']
    information['bear_symbol']=self.payload['bear']
    information['bull_symbol']=self.payload['bull']   
    information['etf_price']= self.getETFStockQuote(index=index)
    information['bear_price']=self.getBearStockQuote(index=index)
    information['bull_price']=self.getBullStockQuote(index=index)   
    information['timestamp'] =self.getTimestamp(index=index)
    return information 

  def continueTrading(self,count):
    if (self.getBearStockQuote(count) == -1) or (self.getBullStockQuote(count) == -1):
      return False 
    return True

  def getETFStockQuote(self,index):
    return 1.0

  def getBullStockQuote(self,index):
    try:
      value = self.bull_df.at[index-1,'open']
    except KeyError:
      value = -1
      if index>1:
        displayOutput(str="Accessing Bull Panda data has reached end of file. Index={0}".format(index-1))
      else:
        displayError(str="There was an error accessing Bull Panda data. Index={0}".format(index-1))
    return value
 
  def getBearStockQuote(self,index):
    try:
      value = self.bear_df.at[index-1,'open']
    except KeyError:
      value = -1
      if index>1:
        displayOutput(str="Accessing Bear Panda data has reached end of file. Index={0}".format(index-1))
      else:
        displayError(str="There was an error accessing Bear Panda data. Index={0}".format(index-1))
    return value

  def getTimestamp(self,index):
    try:
      value = self.bear_df.at[index-1,'timestamp']
      parsed = dateutil.parser.parse(value)
      #strToDatetime
      return parsed
    except KeyError:
      value = -1
      if index>1:
        displayOutput(str="Accessing Timestamp Panda data has reached end of file. Index={0}".format(index-1))
      else:
        displayError(str="There was an error accessing Bear Panda data. Index={0}".format(index-1))
    return value


  #
  # Download the entries to A Database near you!!!.
  #
  def downloadAndSaveToDatabase(self,update=False):
    self.bull_df = pd.read_csv(self.generateFileName(source='bull'))
    self.bear_df = pd.read_csv(self.generateFileName(source='bear'))
    self.etf_df = pd.read_csv(self.generateFileName(source='etf'))

    # By default(update=False), we want to make sure we don't add duplicates.
    # If something is already present, we don't add it again.
    # Therefore, we always need to check if data for a given date already exists.    
    pair = dict()
    pair['bull_symbol']=self.payload['bull']
    pair['bear_symbol']=self.payload['bear']
    pair['etf_symbol'] = self.payload['etf']
    #We move the end_date out by 24 hours to get around comparing datetime with dates.
    start_date = datetime.datetime.fromisoformat(self.payload['start_date']).replace(tzinfo=timezone.utc)
    end_date = start_date + datetime.timedelta(days=+1)

    #print("Payload: {}  Start={}    End={}".format(pair,start_date,end_date))
    exists = BullBearETFData.dailyDataExists(pair=pair,start_date=start_date,end_date=end_date)
    
    #print ("update = {}. Exists {}".format(update,exists))
    if exists and not update:
      #print("Exists, shouldn't update. Return")
      return True
    elif exists and update:
      #print("Exists and should update. Delete entry")
      BullBearETFData.purgeIntervalEntry(start_date=start_date,end_date=end_date,pair=pair)

    #if update:
    #  if exists:

    #The lines below will add entries one row at a time. 
    count = 1
    while self.continueTrading(count=count):
      trading_info = self.getTradingInformation(index=count)
      BullBearETFData.insertTradingData(payload=trading_info)
      count = self.getNextTradingWindow(count=count,resolution=self.payload['resolution'])
    
    return True
  #
  # Download the entries to file.
  #
  def downloadAndSaveToFile(self):    
    self.downloadBullToFile()
    self.downloadBearToFile()
    self.downloadETFToFile()
    self.downloadTop15ToFile()
    return self.valid
  
  def generateFileName(self,source=None):
    if source == 'etf':
      trading_unit = self.payload['trading_unit_etf']
    else:
      trading_unit = self.payload['trading_unit']

    file_name =  self.payload['data_folder_root'] + self.payload[source] + '_' + self.payload['start_date'] + '_' \
              +  self.payload['end_date'] + '_per_'+ str(trading_unit)+'_'+self.payload['resolution']+'.csv'

    return  file_name


  #
  # Download and save the data into the right folder.
  #
  def downloadBearToFile(self):
    #Download the Bear
    payload_data = self.payload
    symbol = payload_data['bear']
    force = payload_data['force']
    data_root_folder = payload_data['data_folder_root']
    #print("Downloading this content: {} ".format(payload_data))

    file_name = self.generateFileName(source='bear')
 
    if (force==True) or (not os.path.exists(file_name)):
      alpaca = AlpacaPolygon(payload=payload_data)
      bear_data_frame = alpaca.quotesToSave(symbol=symbol)
      time.sleep(5)
      print("The output goes here {}".format(file_name))
      bear_data_frame.to_csv(file_name)           
    else:
      displayOutput(str="Bear File already exist. No need to recreate it.")

  #
  # Download and save the data into the right folder.
  #
  def downloadBullToFile(self):
    #Download the Bull
    payload_data = self.payload
    symbol = payload_data['bull']
    force = payload_data['force']
    data_root_folder = payload_data['data_folder_root']

    file_name = self.generateFileName(source='bull')

    if (force==True) or (not os.path.exists(file_name)):
      alpaca = AlpacaPolygon(payload=payload_data)
      bull_data_frame = alpaca.quotesToSave(symbol=symbol)
      time.sleep(5)
      #print("The output goes here {}".format(file_name))
      bull_data_frame.to_csv(file_name)           
    else:
      displayOutput(str="Bull File already exist. No need to recreate it.")

  #
  # Download and save the data into the right folder.
  #
  def downloadETFToFile(self):
    #Download the Bull
    payload_data = self.payload
    symbol = payload_data['etf']
    force = payload_data['force']
    data_root_folder = payload_data['data_folder_root']

    file_name = self.generateFileName(source='etf')

    if (force==True) or (not os.path.exists(file_name)):
      alpaca = AlpacaPolygon(payload=payload_data)
      etf_data_frame = alpaca.quotesToSave(symbol=symbol,trading_unit=str(payload_data['trading_unit_etf']))
      time.sleep(5)
      #print("The output goes here {}".format(file_name))
      etf_data_frame.to_csv(file_name)           
    else:
      displayOutput(str="ETF File already exist. No need to recreate it.")
    
  #
  # Download and save the data into the right folder.
  # The Top15 are the top15 stocks that make up an index.
  # 
  def downloadTop15ToFile(self):
    displayOutput(str="Not yet implemented.")

    
#
# The BacktestInfrastructure is used to populate tables with trading data from various ETFs and
# date intervals. 
# The data can be populate from a variety of sources:
#  From a  File: The default filename is config_egghead.json
#  From entries in a MasterTable (Preferred)
#  From JSON/Dict file format.
#
class BackTestInfrastructure():
  def __init__(self,config_file=None,config_file_folder=None,start_date=None,action=None,useMasterTable=False):
    #Not used.
    #self.tests_root_folder_key='EGGHEAD_TESTS_FOLDER'
    self.config_folder_key='EGGHEAD_CONFIG_FOLDER'
    self.config_file_key='EGGHEAD_CONFIG_FILE'
    self.data_folder_root_key='EGGHEAD_DATA_FOLDER'
    self.default_config_file='config_egghead.json'
    # Keys
    self.bullish_key = 'bull'
    self.bearish_key = 'bear'
    self.etf_key = 'etf'
    self.entries_key = 'entries'

    self.valid=True
    self.config = None
    #datetime.datetime(2020,10,1,tzinfo=timezone.utc).isoformat()
    self.default_start_date = (date.today() + datetime.timedelta(days=-1)).isoformat()
    self.default_end_date = (date.today() + datetime.timedelta(days=-1)).isoformat()

    if (useMasterTable):
      displayOutput(str="Loading all ETFs from Master File")
      entries = dict()
      self.config = RobotEquitySymbols.getMasterEntriesAsJSON()
    elif (action=='download' or (action==None)):
      self.config_file=config_file
      self.config_file_folder = config_file_folder
      self.processConfigEntries()

    self.default_trading_unit = 5 #5 minutes interval of data
    self.default_trading_unit_etf = 60 #For ETFs, we use 60 minutes intervals
    self.default_resolution = 'minute' # We use Minute units

  def isValid(self):
    return self.valid

  #
  # Validate the JSON file and make sure the required Keys (bull, bear, etf) are provided.
  #
  def validateConfig(self):
    entries = self.config['entries']
    for x in entries:
      if not self.bullish_key in x:
        displayOutput(str="ERROR: Invalid Config File Entry. Missing Required Bull Symbol in entry. {}".format(x))
        self.valid=False
      elif not self.bearish_key in x:
        displayOutput(str="ERROR: Invalid Config File Entry. Missing Required Bear Symbol in entry. {}".format(x))
        self.valid=False
      elif not self.etf_key in x:
        displayOutput(str="ERROR: Invalid Config File Entry. Missing Required ETF Symbol in entry. {}".format(x))
        self.valid=False

      if not self.valid:
        break

  #
  # Validate the JSON file and make sure we are only working with Symbols that have been 
  # pre-selected and approved.
  #
  def matchWithAllowedSymbols(self):
    entries = self.config['entries']
    for x in entries:
      valid_pair = RobotEquitySymbols.isValidPair(bull=x['bull'],bear=x['bear'],etf=x['etf'])
      if not valid_pair:
        data = "Data: Bull={} Bear={} Etf={}".format(x['bull'],x['bear'],x['etf'])
        displayOutput(str="ERROR: Invalid Config File Entry. Bull/Bear entry is not in list of approved Bull/Bear ETFs. {}".format(data))
        self.valid=False
        break
    return 

  #
  # We are reading from a File. First, we must process the file successfully.
  # Processes the Config File, so that we can download all the data we need.
  #  
  def processConfigEntries(self):

    if self.config_file_folder==None:
      if not self.config_folder_key in os.environ:
        displayOutput(str="No Folder provided and No Default folder specified. {}".format(self.config_folder_key))
        self.valid = False
        return
      else:
        displayOutput(str="No Parent folder provided. Using default Folder {}".format(os.environ[self.config_folder_key]))
        self.config_file_folder = os.environ[self.config_folder_key]

    if self.config_file==None:
      if not self.config_file_key in os.environ:
        displayOutput(str="No file specified and no CONFIG_FILE specified. {0}. Will try default config file {0}".format(self.default_config_file))
        self.config_file = self.default_config_file
      else:
        self.config_file = os.environ[self.config_file_key]

    #Add trailing '/', if none exist
    temp_folder=self.config_file_folder 
    self.config_file_folder = temp_folder if temp_folder.endswith('/') else temp_folder + '/'

    #Remove leading '/' from the filename, if one exists
    temp_file=self.config_file 
    self.config_file = temp_file if not temp_file.startswith('/') else temp_file.strip('/') 

    file_path = self.config_file_folder + self.config_file 
    if not os.path.isfile(file_path):
      displayOutput(str="ERROR: Folder+File does not exist. {}".format(file_path))
      self.valid=False      
      return 

    #Load the Config File
    with open(file_path) as file:
      try:
        self.config = json.load(file)
      except:
        self.valid=False 
        displayOutput(str="Error Reading JSON File.  {0}.".format(file_path))
      file.close()

    if not self.valid:
      return

    self.valid = False if self.entries_key not in self.config else True     
    if not self.valid:
      displayOutput(str="Invalid Config File. Missing key {}".format(self.entries_key))
      return 
    
    self.validateConfig()
    if not self.valid:
      displayOutput(str="Invalid Config File. {}".format(file_path))
      return 

    self.matchWithAllowedSymbols()
    if not self.valid:  
      displayOutput("Invalid Bull/Bear/ETF Symbols. Some symbol(s) aren't allowed. Please review your config file. {}".format(file_path))
    

    return 
  
  #
  # Pairs Data
  #
  def getNumberOfBullBearPairs(self):
    if not self.isValid():
      return None
    entries = self.config[self.entries_key]
    return len(entries)

  #
  # Process the Entries from the Pairs list. The format of the Pairs is key.
  # Pairs are retrieved from the Master Table: RobotEquitySymbols using the function getMasterEntriesAsJSON
  # The Trading Calendar is retrieved from Alpaca.
  #
  def processTradeData(self,start_date=None,end_date=None,pairs=None):
    if not self.isValid():
      return False

    if shouldUsePrint():
      print(self.config)

    default_start_date = datetime.datetime(2020,10,1,tzinfo=timezone.utc).isoformat()
    default_end_date = default_start_date
    default_pairs = self.config[self.entries_key]
    self.start_date = start_date if not (start_date==None) else default_start_date
    self.end_date = end_date if not (end_date==None) else default_end_date
    self.pairs = pairs if not (pairs==None) else default_pairs

    alpaca = AlpacaMarketClock()
    trading_dates = alpaca.getTradingCalendar(start_date=self.start_date,end_date=end_date)
    
    entries = []
    for pair in self.pairs:
      displayOutput(str="Pair={}".format(pair))
      #for day in trading_dates:
      config_dict=dict()
      entry = [{'bull':pair['bull'],'bear':pair['bear'],'etf':pair['etf'],'start_date':day['start_date'],
                  'end_date':day['start_date']} for day in trading_dates]
      config_dict['entries']=entry
      entries.append(config_dict.copy())

    self.config=entries
    return entries

  #
  # Pairs Data
  #
  def getNumberOfBullBearPairs(self):
    if not self.isValid():
      return None
    entries = self.config[self.entries_key]
    return len(entries)

  #
  # Download and store data into the database. This function has some complexity because
  # Files will be moved the File first, then moved to the Database.
  # TODO: I hope there are better ways to do it.
  #
  def downloadAndStore(self,target=None,update=False):
    if not self.isValid():
      return False

    if shouldUsePrint():
      print(self.config)

    #Store the downloaded files from the location of the 
    if self.data_folder_root_key in os.environ:
      temp_data_folder = os.environ[self.data_folder_root_key]
    else:
      temp_data_folder = self.config_file_folder + 'data'
    
    #Add trailing '/', if none exist
    data_root_folder = temp_data_folder if temp_data_folder.endswith('/') else temp_data_folder + '/'

    # Check if the folder exists. If not, then create one ...
    if not os.path.exists(data_root_folder):
      os.mkdir(data_root_folder)

    # At this point, the data is as follow:
    # config = [ {'entries':[ {'bull':'TQQQ','bear':'SQQQ','etf':'QQQ','start_date':'2020-10-01','end_date':'2020-10-01'}]},
    #            {'entries':[ {'bull':'LABD','bear':'LABU'} ]},
    #            {'entries':[ {'bull':'UDOW','bear':'SDOW'} ] }]
    #print("HENRI: CONFIG {}".format(self.config[0]['entries']))
    for data_entry in self.config:
    #Set the default values first. Make sure to calculate the dates properly
      start_date_hl = data_entry['start_date'] if ('start_date' in data_entry) else self.default_start_date
      end_date_hl = data_entry['end_date'] if ('end_date' in data_entry) else self.default_end_date
      trading_unit_hl = data_entry['trading_unit'] if ('trading_unit' in data_entry) else self.default_trading_unit
      trading_unit_etf_hl = data_entry['trading_unit_etf'] if ('trading_unit_etf' in data_entry) else self.default_trading_unit_etf
      resolution_hl = data_entry['resolution'] if ('resolution' in data_entry) else self.default_resolution

      payload_data = [{'bull':x[self.bullish_key],'bear':x[self.bearish_key],'etf':x[self.etf_key],
                    'start_date':x['start_date'] if ('start_date' in x) else start_date_hl,
                    'end_date': x['end_date'] if ('end_date' in x ) else end_date_hl,
                    'resolution': x['resolution'] if ('resolution' in x) else resolution_hl,
                    'data_folder_root':data_root_folder,'force':False,
                    'trading_unit':x['trading_unit'] if ('trading_unit' in x) else trading_unit_hl,
                    'trading_unit_etf':x['trading_unit_etf'] if ('trading_unit_etf' in x) else trading_unit_etf_hl} 
                    for x in data_entry[self.entries_key]]
      
      payload = dict()
      payload['data'] = payload_data
      for x in payload_data:
        downloadable = DownloadableETFBullBear(payload=x)
        if target=='both':
          success = downloadable.downloadAndSaveToFile()
          success = downloadable.downloadAndSaveToDatabase(update=update)
        if target == None or target=='file':
          success = downloadable.downloadAndSaveToFile()
        elif target == 'database':
          success = downloadable.downloadAndSaveToDatabase(update=update)
    return self.isValid()

  #
  #  Provides the option to clear all the entries in the Table
  #  prior to reloading all the data again.
  #
  @staticmethod
  def purgeSymbolsAndData(clear_and_reload=False):
    if clear_and_reload:
      #RobotEquitySymbols.purgeAllEquities()
      BullBearETFData.purgeAllEntries()

    return True 

#
# TODO: The function below was NOT tested after we added the ability to 
# Update the Data from the MasterEntries.  
# Therefore ... use with caution
#
class BacktestInfrastructureFromJSON():
  def __init__(self,config_file=None,config_file_folder=None,json=None,action=None):
    self.config_folder_key='EGGHEAD_CONFIG_FOLDER'
    self.config_file_key='EGGHEAD_CONFIG_FILE'
    self.tests_root_folder_key='EGGHEAD_TESTS_FOLDER'
    self.data_folder_root_key='EGGHEAD_DATA_FOLDER'
    self.default_config_file='config_egghead.json'
    self.default_trading_unit = 5
    self.default_trading_unit_etf = 60
    self.default_resolution = 'minute'
    self.default_start_date = (date.today() + datetime.timedelta(days=-1)).isoformat()
    self.default_end_date = (date.today() + datetime.timedelta(days=-1)).isoformat()
    self.entries_key = 'entries'
    self.bullish_key = 'bull'
    self.bearish_key = 'bear'
    self.etf_key = 'etf'
    self.config = None
    self.valid=True

    if (action=='download' or (action==None)) and (json==None):
      self.config_file=config_file
      self.config_file_folder = config_file_folder
      self.processConfigEntries()
    elif (action=='download' or (action==None)) and not (json==None):
      self.json_content=json
      self.processJSONEntry()
    elif action == 'feed':
      self.valid =self.prepareFeed()
    elif action == 'populate':
      self.valid = self.preparePopulate()
    else:
      self.valid = False

  def isValid(self):
    return self.valid
  #
  # Validate the JSON file and make sure the required Keys (bull, bear, etf) are provided.
  #
  def validateConfig(self):
    entries = self.config['entries']
    for x in entries:
      if not self.bullish_key in x:
        displayOutput(str="ERROR: Invalid Config File Entry. Missing Required Bull Symbol in entry. {}".format(x))
        self.valid=False
      elif not self.bearish_key in x:
        displayOutput(str="ERROR: Invalid Config File Entry. Missing Required Bear Symbol in entry. {}".format(x))
        self.valid=False
      elif not self.etf_key in x:
        displayOutput(str="ERROR: Invalid Config File Entry. Missing Required ETF Symbol in entry. {}".format(x))
        self.valid=False

      if not self.valid:
        break

  #
  # Validate the JSON file and make sure we are only working with Symbols that have been 
  # pre-selected and approved.
  #
  def matchWithAllowedSymbols(self):
    entries = self.config['entries']
    for x in entries:
      if not x['bull'] in master_bulls:
        displayOutput(str="ERROR: Invalid Config File Entry. Bull entry is not in list of approved Bull ETFs. {}".format(x['bull']))
        self.valid=False
      elif not x['bear'] in master_bears:
        displayOutput(str="ERROR: Invalid Config File Entry. Bear entry is not in list of approved Bear ETFs. {}".format(x['bear']))
        self.valid=False
      elif not x['etf'] in master_etfs:
        displayOutput(str="ERROR: Invalid Config File Entry. ETF entry is not in list of approved ETFs. {}".format(x['etf']))
        self.valid=False

      if not self.valid:
        break
    return 

  #
  # Processes the JSON Entry passed on the ...
  # 
  def processJSONEntry(self):
    displayOutput("Processing Entry from DICT File. {}".format(self.json_content))
    try:
      self.config = json.loads(self.json_content)
    except:
      displayOutput(str="ERROR: There was an error reading the JSON File content. {}".format(''))
      self.valid=False
      return 

    self.valid = False if self.entries_key not in self.config else True     
    if not self.valid:
      displayOutput(str="Invalid Config File. Missing key {}".format(self.entries_key))
      return 
    
    self.validateConfig()
    if not self.valid:
      displayOutput(str="Invalid JSON Entry. {}".format(self.json_content))
      return 

    self.matchWithAllowedSymbols()
    if not self.valid:  
      displayOutput("Invalid Bull/Bear/ETF Symbols. Some symbol(s) aren't allowed. Please review your config file. {}".format(self.json_content))
    
    return 
  
    self.valid=True
  	

  #
  # Processes the Config File, so that we can download all the data we need.
  #  
  def processConfigEntries(self):

    if self.config_file_folder==None:
      if not self.config_folder_key in os.environ:
        displayOutput(str="No Folder provided and No Default folder specified. {}".format(self.config_folder_key))
        self.valid = False
        return
      else:
        displayOutput(str="No Parent folder provided. Using default Folder {}".format(os.environ[self.config_folder_key]))
        self.config_file_folder = os.environ[self.config_folder_key]

    if self.config_file==None:
      if not self.config_file_key in os.environ:
        displayOutput(str="No file specified and no CONFIG_FILE specified. {0}. Will try default config file {0}".format(self.default_config_file))
        self.config_file = self.default_config_file
      else:
        self.config_file = os.environ[self.config_file_key]

    #Add trailing '/', if none exist
    temp_folder=self.config_file_folder 
    self.config_file_folder = temp_folder if temp_folder.endswith('/') else temp_folder + '/'

    #Remove leading '/' from the filename, if one exists
    temp_file=self.config_file 
    self.config_file = temp_file if not temp_file.startswith('/') else temp_file.strip('/') 

    file_path = self.config_file_folder + self.config_file 
    if not os.path.isfile(file_path):
      displayOutput(str="ERROR: Folder+File does not exist. {}".format(file_path))
      self.valid=False      
      return 

    #Load the Config File
    with open(file_path) as file:
      try:
        self.config = json.load(file)
      except:
        self.valid=False 
        displayOutput(str="Error Reading JSON File.  {0}.".format(file_path))
      file.close()

    if not self.valid:
      return

    self.valid = False if self.entries_key not in self.config else True     
    if not self.valid:
      displayOutput(str="Invalid Config File. Missing key {}".format(self.entries_key))
      return 
    
    self.validateConfig()
    if not self.valid:
      displayOutput(str="Invalid Config File. {}".format(file_path))
      return 

    self.matchWithAllowedSymbols()
    if not self.valid:  
      displayOutput("Invalid Bull/Bear/ETF Symbols. Some symbol(s) aren't allowed. Please review your config file. {}".format(file_path))
    
    return 
  
  #
  # Pairs Data
  #
  def getNumberOfBullBearPairs(self):
    if not self.isValid():
      return None
    entries = self.config[self.entries_key]
    return len(entries)

  #
  # Download and store data into the database.
  #
  def downloadAndStore(self,target=None,update=False):
    if not self.isValid():
      return False

    if shouldUsePrint():
      print(self.config)

    #Store the downloaded files from the location of the 
    if self.data_folder_root_key in os.environ:
      temp_data_folder = os.environ[self.data_folder_root_key]
    else:
      temp_data_folder = self.config_file_folder + 'data'
    
    #Add trailing '/', if none exist
    data_root_folder = temp_data_folder if temp_data_folder.endswith('/') else temp_data_folder + '/'

    # Check if the folder exists. If not, then create one ...
    if not os.path.exists(data_root_folder):
      os.mkdir(data_root_folder)

    #Set the default values first. Make sure to calculate the dates properly
    start_date_hl = self.config['start_date'] if ('start_date' in self.config) else self.default_start_date
    end_date_hl = self.config['end_date'] if ('end_date' in self.config) else self.default_end_date
    trading_unit_hl = self.config['trading_unit'] if ('trading_unit' in self.config) else self.default_trading_unit
    trading_unit_etf_hl = self.config['trading_unit_etf'] if ('trading_unit_etf' in self.config) else self.default_trading_unit_etf
    resolution_hl = self.config['resolution'] if ('resolution' in self.config) else self.default_resolution

    payload_data = [{'bull':x[self.bullish_key],'bear':x[self.bearish_key],'etf':x[self.etf_key],
                    'start_date':x['start_date'] if ('start_date' in x) else start_date_hl,
                    'end_date': x['end_date'] if ('end_date' in x ) else end_date_hl,
                    'resolution': x['resolution'] if ('resolution' in x) else resolution_hl,
                    'data_folder_root':data_root_folder,'force':False,
                    'trading_unit':x['trading_unit'] if ('trading_unit' in x) else trading_unit_hl,
                    'trading_unit_etf':x['trading_unit_etf'] if ('trading_unit_etf' in x) else trading_unit_etf_hl} 
                    for x in self.config[self.entries_key]]
      
    payload = dict()
    payload['data'] = payload_data
    for x in payload_data:
      downloadable = DownloadableETFBullBear(payload=x)
      if target=='both':
        success = downloadable.downloadAndSaveToFile()
        success = downloadable.downloadAndSaveToDatabase(update=update)
      if target == None or target=='file':
        success = downloadable.downloadAndSaveToFile()
      elif target == 'database':
        success = downloadable.downloadAndSaveToDatabase(update=update)

    return True 

#
# Sets up the Infrastructure to stream Quotefeed from Database directly
# It is provided mostly for convenience and consistency
#
class BackTestDatabaseInfrastructure():

  def __init__(self,bull_symbol,bear_symbol,etf_symbol):
    self.payload = dict()
    self.payload['bull_symbol']=bull_symbol
    self.payload['bear_symbol']=bear_symbol
    self.payload['etf_symbol']=etf_symbol


  def getFeedData(self,start_date,end_date):
    #This type of feed has start/end date specification capabilities.
    backtest_data = BullBearETFData.getDataFeed(pair=self.payload,start_date=start_date,end_date=end_date)
    return backtest_data

#
# Sets up the Infrastructure to stream files from an array.
#  This infrastructure should be used for very small subsets of tests
# where we want to directly modify the feed data.
#
class BackTestArrayInfrastructure():

  def __init__(self,bull_feed,bear_feed,etf_feed,time_feed,bull_symbol,bear_symbol,etf_symbol):
    self.bull_prices =  bull_feed
    self.bear_prices = bear_feed
    self.etf_prices = etf_feed
    self.timestamps = time_feed
    self.bull_symbol = bull_symbol
    self.bear_symbol = bear_symbol
    self.etf_symbol = etf_symbol
    self.timestamp = 'timestamp'

  def getFeedData(self):
    x = min(len(self.bear_prices),min(len(self.timestamps),min(len(self.bull_prices),len(self.etf_prices))))
    self.item = [{self.timestamp:self.timestamps[count],self.bull_symbol:self.bull_prices[count],self.bear_symbol:self.bear_prices[count],
                  self.etf_symbol:self.etf_prices[count]} for count in range(x)]

    return self.item
  

#
# Sets up Infrastructure to stream data from various Files 
# into Data Frames
#
class BackTestFileInfrastructure():

  def __init__(self,testname,bull_symbol,bear_symbol,etf_symbol):
    self.testname = testname
    self.bull_symbol = bull_symbol
    self.bear_symbol = bear_symbol
    self.etf_symbol = etf_symbol
    default_file_root = '/Users/henrimeli/Desktop/stocks/stocks_data/tests/'
    self.tests_root_folder_key='EGGHEAD_TESTS_FOLDER'
    self.timestamp = 'timestamp'
    self.calculateFileRoot()
  
  #
  # Calculate the value of the File Root.
  #
  def calculateFileRoot(self):
    if not self.tests_root_folder_key in os.environ:
      self.file_root = self.default_config_file
    else:
      self.file_root = os.environ[self.tests_root_folder_key]

    #Add trailing '/', if none exist
    temp_folder=self.file_root 
    self.file_root = temp_folder if temp_folder.endswith('/') else temp_folder + '/'

    bull_file_path = self.file_root + 'bull_' + self.testname + '.csv'  
    bear_file_path = self.file_root + 'bear_' + self.testname + '.csv' 
    try:
      self.bull_df = pd.read_csv(bull_file_path)
      self.bear_df = pd.read_csv(bear_file_path)
    except:
      displayError(str="Error opening file:\n {}  or \n {} ".format(bull_file_path,bear_file_path))
    
  #
  #
  #  
  def getFeedData(self):
    x = min(self.bull_df['open'].count(),self.bear_df['open'].count())
    self.item = [{self.timestamp:self.bear_df.at[count,'timestamp'],self.bull_symbol:self.bull_df.at[count,'open'],
                  self.bear_symbol:self.bear_df.at[count,'open'], self.etf_symbol:self.bull_df.at[count,'open']} for count in range(x)]

    return self.item

#
# Sets up Infrastructure to stream data from Delayed Live Action
# The data is coming from the Alpaca API and is NOT live.
# Need to check how delayed it is.
#
class DelayedLiveInfrastructure():

  def __init__(self,bull_symbol,bear_symbol,etf_symbol,sleep_time=1):
    self.bull_symbol = bull_symbol
    self.bear_symbol = bear_symbol
    self.etf_symbol = etf_symbol
    self.sleep_time=sleep_time
    self.alpaca = AlpacaLastTrade()
  
  def getTradingInformation(self):
    information = dict()
    symbols = [self.bull_symbol,self.bear_symbol,self.etf_symbol]
    for s in symbols:
      last_trade = self.alpaca.getLastTrade(symbol=s)
      information[s] = last_trade.price
      timestamp_number = last_trade.timestamp
      timestampe=pd.to_datetime(timestamp_number).replace(microsecond=0)
    information['timestamp']=timestampe.isoformat().replace('T',' ')
    time.sleep(self.sleep_time)
    return information 
