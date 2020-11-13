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