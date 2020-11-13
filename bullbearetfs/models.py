from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import datetime
from django.utils import timezone
from django.contrib.auth.models import  User
import logging, json, time, pytz, asyncio, re
from datetime import timedelta
from os import environ 

# Import Models
from bullbearetfs.utilities.core import getTimeZoneInfo, shouldUsePrint, strToDatetime
from bullbearetfs.utilities.errors import InvalidTradeDataHolderException


class NotificationType(models.Model):
  name = models.CharField(max_length=20,default='')
  value = models.IntegerField(default=0)

  def __str__(self):
    return "{0} {1} ".format(self.name, self.value)

# A Roundtrip is an abstraction of the concept of a simulteneous Bull and a Bear entry
# Given a Robot and a root_id, the RoundTrip can retrieve both the bull and the bear and manage various aspects of it 
# elegantly (in an Object Oriented way) and with programmatic clarity via a single Interface/Namespace/Class.
# In the Egghead Project, Bulls and Bears are always acquired in Pairs. They don't have to be disposed of in Pairs. 
# The main role of the Rountrip Class is to fully manage that abstraction and provide programmatic/algorithmic clarity
# as well as facilitate the access/manipulation/modification of the data.
#
# RoundTrip Classes are NOT model classes. They are therefore not persisted. Instead, they are built on the fly to serve
# a very clear instantaneous purpose and dismissed once that purpose has been achieved.
# In O/O they would be tantamount to Interfaces. 
# RoundTrip classes are also provided en-lieu of adding too much program logic inside of a Model class.
# RoundTrip classes can also be seen as providing a namespace for very specific type of functionality. 
#
# The Roundtrip Class is a Foundational Class of the Egghead Project, meaning it provides functionality that is expected
# to be reused by various other classes. It is therefore critical that it be well designed, implemented, 
# completely and very accurately tested. Future changes to this class must be done very carefully.
#  
# There are various methods provided in the Rountrip Class with the purpose of managing the following aspects:
#
# - Bull/Bear Access Management: All Inquiries, Accesses to Bull/Bear Data MUST go through a method/function provided by the Roundtrip class.
# - Object States Management: Each Roundtrip goes through a lifecycle: Acquisition, Partial Disposition, and Complete Disposition. 
#                      See below about the discussion on the different states of the RoundTrip Class.
# - Age, Duration Management: Each assets has a lifespann determined by how long it has been held.
# - Individual and combined Value Management: Each Bull/Bear has a value at acquisition and through its lifecycle.
#     The Roundtrip is capable of determining the value of the individual and combined assets at any given time.
# - Performance Managament: The financial performance of an asset helps determine quickly determine the fate of an asset.
# - Composition Management: How much each asset (Bull/Bear) contributes to the combined value of the investment is critical.
# 
# At Acquisition time, the Bear and the Bull have a monetary value determined based on their composition. Their composition might defer.
# Through its lifetime, the Roundtrip goes through various states, depending on the Strategy Class Selected.
# 1. Stable State: [Roundtrip.isStable() == True] A pair was just acquired and its combined value is close to zero, regardless of market conditions
# 2. Transition Stage: [Roundtrip.isInTransition() == True] One side of the Pair has been sold. As the market moves, the value of the other side moves.
# The goal is to wait until an asset in transition reaches the optimal value, so it can be moved to Completion phase
# 3. Completion Stage: [Roundtrip.isComplete() == True] The completion stage is reached when the other side of the asset is sold as well.
# 4. Active State: [Roundtrip.isStable() == True or [Roundtrip.isInTransition() == True]]
#
class RoundTrip():
  def __init__(self,robot,root_id):
    self.robot = robot
    self.root_order_client_id = root_id
    self.bull_symbol = robot.getBullishSymbol()
    self.bear_symbol = robot.getBearishSymbol()
    self.profit_basis_per_roundtrip = robot.getProfitTargetPerRoundtrip()
    self.current_bull_price = robot.getCurrentBullPrice()
    self.current_bear_price = robot.getCurrentBearPrice()
    self.current_timestamp = robot.getCurrentTimestamp()


###################################################################################
#  Basic Getters and Setters: Inquieries and Access Management
#
  def getBullSymbol(self):
    return self.bull_symbol

  def getBearSymbol(self):
    return self.bear_symbol

  def getAcquisitionDate(self):
    return self.getBullBuyDate()

  def getBullBuyDate(self):
    return self.getTheBull().buy_date

  def getBearBuyDate(self):
    return self.getTheBear().buy_date

  def getBullBuyPrice(self):
    return self.getTheBull().buy_price

  def getBearBuyPrice(self):
    return self.getTheBear().buy_price

  def getBullSellPrice(self):
    if self.getTheBull().isRealized():
      return self.getTheBull().sell_price
    return None

  def getBearSellPrice(self):
    if self.getTheBear().isRealized():
      return self.getTheBear().sell_price
    return None

  def getBullSellDate(self):
    if self.getTheBull().isRealized():
      return self.getTheBull().sell_date
    return None

  def getBearSellDate(self):
    if self.getTheBear().isRealized():
      return self.getTheBear().sell_date
    return None

  def getBullCurrentPrice(self):
    return self.current_bull_price

  def getBullQuantity(self):
    return self.getTheBull().quantity

  def getBearQuantity(self):
    return self.getTheBear().quantity

  def getBearCurrentPrice(self):
    return self.current_bear_price

  def getCurrentTimestamp(self):
    return self.current_timestamp

  def getTheBull(self):
    return TradeDataHolder.objects.get(buy_order_client_id=self.getBullBuyOrderClientID())

  def getTheBear(self):
    return TradeDataHolder.objects.get(buy_order_client_id=self.getBearBuyOrderClientID())

###########################################################################################
#
#  Validation and Roundtrip States Check (Stable, Transition, Completed)
#
  #Ensure there is exactly 2 entries in the table with the same order_client_ID_Root
  def hasExactlyTwoEntries(self):
    entries=TradeDataHolder.objects.filter(buy_order_client_id__startswith=self.getRootOrderClientID()).count()
    return entries==2

  # This definition is wrong. Don't use it.
  def isValid(self):
        return self.hasExactlyTwoEntries() and self.getTheBull().isValid() and self.getTheBear().isValid()

  def isStable(self):
        return self.getTheBull().isUnRealized() and self.getTheBear().isUnRealized()

  def isInBullishTransition(self):
        return self.getTheBull().isUnRealized() and self.getTheBear().isRealized()

  def isInBearishTransition(self):
    return self.getTheBull().isRealized() and self.getTheBear().isUnRealized()

  def isInTransition(self):
    return self.isInBullishTransition() or self.isInBearishTransition()

  def isActive(self):
        return self.isStable() or self.isInTransition()

  def isCompleted(self):
        return self.getTheBear().isRealized() and self.getTheBull().isRealized()

  def getIsBullishOrBearishTransition(self):
    if self.isInBullishTransition():
      return "Bullish"
    elif self.isInBullishTransition():
          return "Bearish"
    return "Invalid"

#####################################################################################################################
# StableRoundTrips: Similar to the Roundtrip, this is not a persistable Class. 
# It is an interface to collection of Roundtrip data that are in a particular state at a given time. The Stable State.
# For All the entries in the StableRoundTrips(): RoundTrips.isStable() returns True 
#
# StableRoundTrirps: This is the encapsulation of ALL Assets in a Stable State
#
# Organizing all entries at the ... allows us to create some powerful functions to access, manipulate and 
# all entries. 
# 
class StableRoundTrips():

  def __init__(self,robot):
    self.robot = robot
    self.stable_list = []
    entries = robot.getAllBullishRoundtrips()
    for entry in entries:
      rt = RoundTrip(robot=self.robot,root_id=entry.getOrderClientIDRoot())
      if rt.isStable():
        self.stable_list.append(rt)

  def __str__(self):
   return "{0}".format('This is the StableRoundtrips Class')

  def printEntries(self):
    print("\n")
    for c in self.stable_list:
      print("{0}".format(c))

  def getSize(self):
    return self.getStableSize()

  def getStableSize(self):
    return len(self.stable_list)

  def isFullyLoaded(self):
    return (len(self.stable_list) >= self.robot.getMaxNumberOfRoundtrips())

  def isEmpty(self):
    return (self.getSize() == 0)

###Returns List in either increasing or decreasing (reverse=True or False ) Order ###################
#
#
  def getAllStableEntries(self):
    return self.stable_list

  def getAllStableEntriesByAgeYoungestFirst(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBullBuyDate(),reverse=True)
    return candidates

  def getAllStableEntriesByAgeOldestFirst(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBullBuyDate(),reverse=False)
    return candidates

  def getAllStableEntriesByBullPrice(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBullBuyPrice(),reverse=True)
    return candidates

####################Return single Entity #################################
  def getBestPerformingBearValue(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getStableBearValue(),reverse=True)
    return None if len(candidates) == 0 else candidates[0]

  def getBestPerformingBullValue(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getStableBullValue(),reverse=True)
    return None if len(candidates) == 0 else candidates[0]



# An ETFAndReversePairRobot (ETF-EA) is an automated and autonoumous Runner, that processes Stock Market Events 
# to decide when to Acquire and Dispose of Assets. This Class of Equity Trading Robot focuses solely on Stock Market 
# Equities Based on Leveraged ETFs acquired in Pairs. One side is Bullish and the other side is Bearish.
# Both are following the exact same index.
# For example, the Robot can be configured to trade the Bullish/Bearish pairs of the Nasdaq 100 (TQQQ/SQQQ) or
# the Bullish/Bearish pairs of the DOW Jones Industrial (SDOW/UDOW). 
# Each Robot can only deal with a single Bull/Bear pair at a time.   
# An ETFAndReversePairRobot is created, configured then deployed. From here, it is expected to runs automatically
# and makes decisions based on its configuration and strategies. There should be as little manual intervention as
# possible during its run. 
# 
# Components of an Equity Trading Robot:
# Each Trading Robot is designed to be as flexible and configurable as possible. Therefore it provides lots of options.
# During the configuration, the user should be able to select:
#   -Equity Symbols: The acceptable pairs have already been pre-selected and stored as Master Pairs. The User can only select
#    from those pre-selected pairs. 
#   -Budget Management: The user should be able to select how much money they want to spend per acquisition, as well as their overall budget.
#    Budget data is synchronized based on the Brokerage Policy
#   -Strategy Class and Strategy: A certain number of strategies have been developed and implemented.  During the configuration
#    the user should be able to select which Strategy to chose from. 
#    All Strategies will use Cameroonian-based names. Especially names of villages in the Bamboutos Division. 
# It consists of an Acquisition Policy, a Disposition Policy, a Portfolio Protection Policy,
# An Orders Management Policy, Transaction Data
# Acquisition Policy: Determines at when Assets should be purchased. It uses Entry Indicators to determine
# the most appropriate time to enter a market position, which asset to purchase and how much to spend.
# Disposition Policy: Determines at what time Assets should be disposed of. It uses Exit Indicators to determine
# the most appropriate time to dispose of an Asset.
# Portfolio Protection Policy: Once an asset has been purchased, it determines the how to protect the asset.
# Order Management Policy: It determines which Order Types should be used when acquiring/disposing of an asset.
# Transaction Data: This is where Transaction Data are kept.
# Profit Targets: Projection / targets are used to follow the evolution of unrealized gains through the lifetime of  #################################################################################
class ETFAndReversePairRobot(models.Model):
  name = models.CharField(max_length=50,default='')
  description = models.CharField(max_length=50,default='')
  enabled = models.BooleanField(default=False) #Running?
  visibility = models.BooleanField(default=False) #Should be made visible?
  creation_date = models.DateTimeField('date created',default=timezone.now)
  modify_date = models.DateTimeField('date modified',default=timezone.now)

#
  # These variables should change with every new tick.
  #
  current_bull_price= 0
  current_bear_price= 0
  current_timestamp = datetime.now(getTimeZoneInfo())


##############################################################################
#
# TradeDataHolder is the Infrastructure that contains all the transactions.
# It is organized in such a way that it allows for us to easily
# keep tract of acquisition and sell transactions.
# buy_order_client_id and sell_order_client_id are very important
#
class TradeDataHolder(models.Model):
  symbol =   models.CharField(max_length=10,default='')
  quantity = models.IntegerField(blank=True,null=True)
  buy_date = models.DateTimeField(timezone.now,default=timezone.now)
  buy_price = models.FloatField(default=0.0)
  buy_order_client_id =   models.CharField(max_length=100,default='')
  sell_order_client_id =   models.CharField(max_length=100,blank=True,null=True)
  sell_price = models.FloatField(blank=True,null=True)
  sell_date = models.DateTimeField(timezone.now,blank=True,null=True)
  winning_order_client_id = models.CharField(max_length=100,blank=True,null=True)
  robot = models.ForeignKey(ETFAndReversePairRobot,on_delete=models.PROTECT,blank=True,null=True)

  #execution =   models.ForeignKey('ETFPairRobotExecution',on_delete=models.PROTECT,blank=True,null=True)
 
  def __str__(self):
    return "{0} {1} {2} {3} {4} {5} {6}".format(self.symbol,self.quantity,self.buy_price,datetime.strftime(self.buy_date,"%y/%m/%d"),self.sell_price,self.buy_order_client_id,self.sell_order_client_id)

  def getBasicBuyInformation(self):
    return "[S={0}. Q={1}. P={2}]".format(self.symbol,self.quantity,self.buy_price)

  def getAdvancedBuyInformation(self):
    date_time=datetime.strftime(self.buy_date,"%y/%m/%d")
    root_id = self.getOrderClientIDRoot()
    return "[S={0}. Q={1}. P={2}. D={3} R={4}]".format(self.symbol,self.quantity,self.buy_price,date_time,root_id)

  #############################################################################
  # Data Sanity. We want to make sure we are
  # only working with good Data from the beginning.
  #
  def isValidAfterBuy(self):
    return self.isValid()

  def isValidAfterSale(self):
    return self.isValid(after_sale=True)

  ############################################################################
  # This function checks the data integrity of our system.
  # By default, we check this after a Buy Operation (after_sale=False)
  # After a sale, we also want to make sure the data remain as expected.
  # Only check after a Buy Operation
  # Should the cost_basis be considered? Could play a role in the future.

  def isValid(self,after_sale=False):
    if not self.symbol or (not self.buy_price) \
      or (not self.buy_date) or (not self.buy_order_client_id):
      return False

    if (self.buy_price <= 0) or (self.quantity <= 0) or (self.symbol == ''):
      return False

    #Fields expected to be NULL should also be null. Only true after acquisition. After sale, this is no longer valid
    if after_sale == False:
      if (not self.sell_price is None) or (not self.sell_date is None) or (not self.sell_order_client_id is None):
        return False
    else:
      if (self.sell_price <=0) or (self.sell_date == None) or (self.sell_order_client_id is None):
        logger.error("Either the sale price, the sell date or the sell client ID are wrong. ")
        return False

    #Guarantee the buy_order_client_id ends with '_buy_symbol'. Only true for AfterBuy status for buy_order_client_id
    ending = '_buy_'+self.symbol
    if not self.buy_order_client_id.endswith(ending):
      return False

    #Ensure that the sell_client_order_id was set properly
    if after_sale == True:
      ending_sell = '_sell_'+self.symbol
      if not self.sell_order_client_id.endswith(ending_sell):
        logger.error("Issue with Order_Client_ID")
        return False
    return True

##################################################################################
  ### Place the Order here. buy_order should have all the pieces needed.
  ###
  @staticmethod
  def recordDispositionTransaction(robot,order,transition_root_id=None):
    sell_order = order
    entry = TradeDataHolder.objects.get(buy_order_client_id=sell_order['buy_order_client_id'])

    if entry == None:
      raise InvalidTradeDataHolderException("Unable to locate entry based on order_client_id {0}.".format(sell_order['buy_order_client_id']))

    entry.sell_price = sell_order['sell_price']
    entry.sell_order_client_id = sell_order['sell_order_client_id']
    entry.sell_date = sell_order['sell_date']
    if not (transition_root_id==None):
      entry.winning_order_client_id = transition_root_id
    entry.save()


    return entry


  ##################################################################################
  ### Place the Order here. buy_order should have all the pieces needed.
  ###
  @staticmethod
  def recordAcquisitionTransaction(robot,bullish,bearish):
    if bullish['symbol'] == '' or bearish['symbol'] == '':
          raise InvalidTradeDataHolderException("Invalid Bullish {0} or Bearish {1} symbol.".format(bullish['symbol'],bearish['symbol']))
    if bullish['price'] <= 0 or bearish['price'] <= 0:
          raise InvalidTradeDataHolderException("Invalid Bullish {0} or Bearish {1} price.".format(bullish['price'],bearish['price']))
    if bullish['qty'] <= 0 or bearish['qty'] <= 0:
          raise InvalidTradeDataHolderException("Invalid Bullish {0} or Bearish {1} Quantity".format(bullish['qty'],bearish['qty']))
    if not (bullish['bull_buy_order_client_id'].replace('_buy_','').replace(bullish['symbol'],'') == \
                    bearish['bear_buy_order_client_id'].replace('_buy_','').replace(bearish['symbol'],'')):
          raise InvalidTradeDataHolderException("Invalid Order Client ID for Bull {0} and Bear {0}. ".format(bullish['bull_buy_order_client_id'],bearish['bear_buy_order_client_id']))

    bull_entry=TradeDataHolder.objects.create(robot=robot, symbol=bullish['symbol'], buy_price=bullish['price'],
                             buy_order_client_id=bullish['bull_buy_order_client_id'],buy_date=bullish['date'],
                             quantity=bullish['qty'])

    bear_entry=TradeDataHolder.objects.create(robot=robot, symbol=bearish['symbol'], buy_price=bearish['price'],
                             buy_order_client_id=bearish['bear_buy_order_client_id'],buy_date=bearish['date'],
                             quantity=bearish['qty'])


    bull_info =bull_entry.getBasicBuyInformation()
    bear_info = bear_entry.getBasicBuyInformation()
    if shouldUsePrint():
      print("\nNew Entry added: Bull={0}. Bear={1}. ".format(bull_info,bear_info))


  @staticmethod
  def deleteExecutionEngineEntries(robot):
        TradeDataHolder.objects.filter(robot=robot)

  @staticmethod
  def generateInTransitionRootOrderClientID(project_root,bulls_count,bears_count,r_id=None):
    project_root = project_root
    current_time = datetime.now(getTimeZoneInfo())
    root_order_client_id = current_time.strftime("{0}_{1}_{2}_{3}_%Y%m%d-%H-%M-%S.%f".format(project_root,r_id,bulls_count,bears_count))
    return root_order_client_id

  @staticmethod
  def generateBuyOrderClientIDs(project_root,bull_symbol,bear_symbol,r_id=None):
    root_order_client_id = TradeDataHolder.generateRootOrderClientId(project_root=project_root,r_id=r_id)
    order_ids = dict()
    order_ids['bull_buy_order_client_id'] = root_order_client_id + "_buy_" + bull_symbol
    order_ids['bear_buy_order_client_id'] = root_order_client_id + "_buy_" + bear_symbol
    return order_ids

  @staticmethod
  def generateRootOrderClientId(project_root,r_id=None):
    project_root = project_root
    current_time = datetime.now(getTimeZoneInfo())
    root_order_client_id = current_time.strftime("{0}_{1}_%Y%m%d-%H-%M-%S.%f".format(project_root,r_id))
    return root_order_client_id

  #@staticmethod
  #def generateBuyOrderClientIDs(project_root,bull_symbol,bear_symbol,r_id=None):

  @staticmethod
  def generateSellOrderClientIDs(project_root,bull_symbol,bear_symbol,r_id=None):
    root_order_client_id = TradeDataHolder.generateRootOrderClientId(project_root=project_root,r_id=r_id)
    order_ids = dict()
    order_ids['bull_sell_order_client_id'] = root_order_client_id + "_sell_" + bull_symbol
    order_ids['bear_sell_order_client_id'] = root_order_client_id + "_sell_" + bear_symbol
    return order_ids

  @staticmethod
  def getEntryBasedOnOrderClientID(exec_engine_order_client_id):
    data = dict()
    if '_buy_' in exec_engine_order_client_id:
      entry = TradeDataHolder.objects.get(buy_order_client_id=exec_engine_order_client_id)
      data['action']='buy'
      data['quantity']=entry.quantity
      data['symbol']= entry.symbol
      data['price'] = entry.buy_price
      data['cost']= round(entry.getCostBasis() * (-1),2)
      data['buy_date']=entry.buy_date.isoformat().replace('T','')
    elif '_sell_' in exec_engine_order_client_id:
      entry = TradeDataHolder.objects.get(sell_order_client_id=exec_engine_order_client_id)
      data['action']='sell'
      data['quantity']=entry.quantity
      data['symbol']= entry.symbol
      data['price'] = entry.sell_price
      data['cost']=round(entry.getRealizedValue(),2)
      data['buy_date']=entry.sell_date.isoformat().replace('T','')
    return data

  def getSellClientOrderID(self):
    return self.getOrderClientIDRoot() + "_sell_" + self.symbol

  def getBuyClientOrderID(self):
    return self.getOrderClientIDRoot() + "_buy_" + self.symbol

  def getOrderClientIDRoot(self):
    order_client_id_root = self.buy_order_client_id.replace('_buy_','').replace(self.symbol,'')
    return order_client_id_root

  def getWinningOrderClientIDRoot(self):
    return self.winning_order_client_id

  #TODO: please review IsValid()
  def isUnRealized(self):
    return ((self.sell_price is None) and (self.sell_date is None) and (self.sell_order_client_id is None))

  #TODO: please review IsValid()
  def isRealized(self):
    return  (not ( self.sell_price is None) and (not (self.sell_date is None)) and (not (self.sell_order_client_id is None)) )

  def hasPeerEntry(self):
    r_c_id = self.getOrderClientIDRoot()
    count = TradeDataHolder.objects.filter(buy_order_client_id__startswith=r_c_id).exclude(buy_order_client_id=self.buy_order_client_id).count()
    return (count == 1)

  def getCostBasis(self):
        return self.buy_price * self.quantity

  def getCurrentValue(self, current_price):
        return self.quantity * current_price

  def getCurrentProfit(self, current_price):
   return self.getCurrentValue(current_price=current_price) - self.getCostBasis()

  def getUnRealizedValue(self,current_price):
    if self.isUnRealized():
      return (current_price ) *self.quantity
    return 0

  def getRealizedValue(self):
    if self.isUnRealized():
      return 0
    return self.quantity * self.sell_price

   