from django.db import models
from django.utils import timezone
from django.utils.timezone import datetime
from django.utils import timezone
from django.contrib.auth.models import  User
import logging, json, time, pytz, asyncio, re
from datetime import timedelta
import dateutil.parser
from django.db.models import Sum,Avg,Max,Min
from bullbearetfs.utilities.core import getTimeZoneInfo, displayOutput, shouldUsePrint, fixupMyDateTime, timezoneAwareDate,strToDatetime

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

logger = logging.getLogger(__name__)

"""
  TODO: Describe the Module here ...

  List the classes of the module here
"""



#
# Keeps track of the top 15 stocks of a given ETF
# Build Sentiment knowledge about them
#
class Top15Data(models.Model):
  """
  TODO: Describe the Class here ...

  List the classes of the methods of the class here
  """
  timestamp = models.DateTimeField('date created',default=timezone.now) #TODO: Configure me
  price = models.FloatField(default=0)
  symbol = models.CharField(max_length=10,default='')

  def __str__(self):
    return "{0} {1} {2}".format(self.timestamp, self.symbol,self.price)
  

#
# Keeps track of all ETF Pairs and their main Index they are tracking.
#
class BullBearETFData(models.Model):
  """
  TODO: Describe the Class here ...

  List the classes of the methods of the class here
  """
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
    """ TODO: describe the method here """
    information = dict()
    information[self.bull_symbol] = self.bull_price
    information[self.bear_symbol] = self.bear_price
    information[self.etf_symbol]  = self.etf_price   
    information['timestamp']      = self.timestamp.isoformat().replace('T',' ')
    return information

  ######################## Methods for Creating, Updating and Deleting Entries into the Table ###############
  @staticmethod
  def getMostRecentEntry(pair):
    """ TODO: describe the method here """
    end_date = datetime.now(getTimeZoneInfo()).isoformat()
    start_date = datetime.now(getTimeZoneInfo()) + timedelta(days=-30)
    
    pairs_query = BullBearETFData.objects.filter(bull_symbol=pair['bull_symbol'],bear_symbol=pair['bear_symbol'],etf_symbol=pair['etf_symbol'])
    time_bound = pairs_query.filter(timestamp__lte=end_date,timestamp__gte=start_date)
    most_recent = time_bound.aggregate(Max('timestamp'))['timestamp__max']
    return most_recent

  @staticmethod
  def getTodayData(pair,start_date,end_date):
    """ TODO: describe the method here """
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
    """ TODO: describe the method here """
    pairs_query = BullBearETFData.objects.filter(bull_symbol=pair['bull_symbol'],bear_symbol=pair['bear_symbol'],etf_symbol=pair['etf_symbol'])
    count = pairs_query.filter(timestamp__lte=end_date,timestamp__gte=start_date).count()
    return (count>0) 

  @staticmethod
  def insertTradingData(payload): 
    """ TODO: describe the method here """
    entry = BullBearETFData.objects.create(timestamp=payload['timestamp'],bull_price=payload['bull_price'],
                                bear_price=payload['bear_price'],etf_price=payload['etf_price'], bull_symbol=payload['bull_symbol'],
                                bear_symbol=payload['bear_symbol'],etf_symbol=payload['etf_symbol'])

  @staticmethod
  def updateTradingData(payload): 
    """ TODO: describe the method here """
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
    """ TODO: describe the method here """
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
    """ TODO: describe the method here """
    pairs_query = BullBearETFData.objects.filter(bull_symbol=pair['bull_symbol'],bear_symbol=pair['bear_symbol'],etf_symbol=pair['etf_symbol'])
    pairs_query.filter(timestamp__lte=end_date,timestamp__gte=start_date).delete()

  @staticmethod
  def purgePairEntry(pair):
    """ TODO: describe the method here """
    pairs_query = BullBearETFData.objects.filter(bull_symbol=pair['bull_symbol'],bear_symbol=pair['bear_symbol'],etf_symbol=pair['etf_symbol'])
    pairs_query.filter().delete()

  @staticmethod
  def purgeDatabase():
    """ TODO: describe the method here """
    BullBearETFData.objects.filter().delete()


#
# Symbol(s) associated with given Robot
# 
class RobotEquitySymbols(models.Model):
  """
  TODO: Describe the Class here ...

  List the classes of the methods of the class here
  """
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
    """ TODO: describe the method here """
    pairs = RobotEquitySymbols.objects.filter()
    entry = [{'etf':pair.symbol,'bull':pair.bullishSymbol,'bear':pair.bearishSymbol} for pair in pairs]
    entries = dict()
    entries['entries'] = entry
    return entries 

  @staticmethod 
  def printAllMasterEquities():
    """ TODO: describe the method here """
    entries = RobotEquitySymbols.objects.filter().all()
    for x in entries:
      print("\n {}".format(x.getBasicInformation()))

  #
  # Returns the number of Master Equity Entries
  #
  @staticmethod
  def getTotalMaster():
    """ TODO: describe the method here """
    entries = RobotEquitySymbols.objects.filter().all()
    return len(entries)
  #
  # Static Method used to load the topETFs that we will be following and tracking.
  #
  @staticmethod
  def isValidPair(bull,bear,etf=None):
    """ TODO: describe the method here """
    count = RobotEquitySymbols.objects.filter(bullishSymbol=bull).filter(bearishSymbol=bear).count()
    return (count==1)

  #
  # Purge All Equities will delete all entries
  #
  @staticmethod
  def purgeAllEquities():
    """ TODO: describe the method here """
    RobotEquitySymbols.objects.all().delete()
    return True 
  #
  # Static Method used to load the topETFs that we will be following and tracking.
  # TODO: Complete the lists , Update the ETFs, Add some test cases such as:
  #   Move some of this to a different file for better documentation?
  #
  @staticmethod
  def insertMasterEquities(count=1):
    """ TODO: describe the method here """
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
    """ TODO: describe the method here """
    return self.top_15_stocks

  def getBullishSymbol(self):
    """ TODO: describe the method here """
    return self.bullishSymbol

  def getBearishSymbol(self):
    """ TODO: describe the method here """
    return self.bearishSymbol

  def getSymbol(self):
    """ TODO: describe the method here """
    return self.symbol

  def getSymbolsPairAsPayload(self):
    """ TODO: describe the method here """
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
    """ TODO: describe the method here """
    end_date = BullBearETFData.getMostRecentEntry(pair)
    four_hours = end_date + timedelta(hours=-4)
    today = BullBearETFData.getTodayData(pair=pair,start_date=four_hours,end_date=end_date)
    return today

  @staticmethod
  def getTodayEquitiesData(pair):
    """ TODO: describe the method here """
    end_date = BullBearETFData.getMostRecentEntry(pair)
    start_date = end_date + timedelta(hours=-24)
    today = BullBearETFData.getTodayData(pair=pair,start_date=start_date,end_date=end_date)
    return today

  @staticmethod
  def getWeekEquitiesData(pair):
    """ TODO: describe the method here """
    end_date = BullBearETFData.getMostRecentEntry(pair)
    start_date = end_date + timedelta(weeks=-1)
    week = BullBearETFData.getTodayData(pair=pair,start_date=start_date,end_date=end_date)
    return week

  @staticmethod
  def getTwoWeeksEquitiesData(pair):
    """ TODO: describe the method here """
    end_date = BullBearETFData.getMostRecentEntry(pair)
    start_date = end_date + timedelta(weeks=-2)
    two_weeks = BullBearETFData.getTodayData(pair=pair,start_date=start_date,end_date=end_date)
    return two_weeks

  @staticmethod
  def getThreeWeeksEquitiesData(pair):
    """ TODO: describe the method here """
    end_date = BullBearETFData.getMostRecentEntry(pair)
    start_date = end_date + timedelta(weeks=-3)
    two_weeks = BullBearETFData.getTodayData(pair=pair,start_date=start_date,end_date=end_date)
    return two_weeks

  @staticmethod
  def getFourWeeksEquitiesData(pair):
    """ TODO: describe the method here """
    end_date = BullBearETFData.getMostRecentEntry(pair)
    start_date = end_date + timedelta(weeks=-4)
    two_weeks = BullBearETFData.getTodayData(pair=pair,start_date=start_date,end_date=end_date)
    return two_weeks
