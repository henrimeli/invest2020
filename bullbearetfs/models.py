from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import datetime
from django.utils import timezone
from django.contrib.auth.models import  User
import logging, json, time, pytz, asyncio, re
from datetime import timedelta
from os import environ 
from django.db.models import Sum,Avg,Max,Min

# Import Models
from bullbearetfs.utilities.core import getTimeZoneInfo, shouldUsePrint, strToDatetime
from bullbearetfs.utilities.errors import InvalidTradeDataHolderException
from bullbearetfs.executionengine.models import ETFPairRobotExecutionData
from bullbearetfs.robot.models import RobotEquitySymbols, Portfolio, EquityAndMarketSentiment, RobotBudgetManagement
from bullbearetfs.customer.models import Customer
from bullbearetfs.strategy.models import EquityStrategy

from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers import serialize

logger = logging.getLogger(__name__)

CHOICES_ROBOT_SLEEP_TIME_BETWEEN_TRADES = (('1','1'),('2','2'),('5','5'),('10','10'))
CHOICES_MAX_HOLD_DAYS = (('5','5'),('14','14'),('21','21'),('30','30'),('No Max','No Max'))
CHOICES_REGRESSION_FACTOR = (('100,50,33','100,50,33'),('50,33,25','50,33,25'),('30,20,10','30,20,10'))
CHOICES_MIN_HOLD_DAYS = (('0','0'),('0.5','0.5'),('1','1'),('1.5','1.5'),('2','2'),('3','3'),('4','4'),('5','5'),('7','7')) # trading sessions
CHOICES_DATA_SOURCE =(('live','live'),('backtest','backtest'),('paper','paper'))
CHOICES_ROUNDTRIPS =(('4','4'),('8','8'),('10','10'),('12','12'))
CHOICES_ROUNDTRIPS_COST_BASIS = (('500','500'),('1,000','1,000'),('1,500','1,500'),('2,500','2,500'),('4,000','4,000'),('5,000','5,000'))
CHOICES_ROUNDTRIPS_PROFIT_TARGETS = (('.05','.05'),('.075','.075'),('.1','.1'),('.15','.15'))
CHOICES_VERSION_INFORMATION = (('1.0.0','1.0.0'),('2.0.0','2.0.0'))
CHOICES_MAX_TRANSACTIONS_PER_DAY=(('1','1'),('2','2'),('unlimited','unlimited'))

class NotificationType(models.Model):
  name = models.CharField(max_length=20,default='')
  value = models.IntegerField(default=0)
  aalue = models.IntegerField(default=0)

  def __str__(self):
    return "{0} {1} ".format(self.name, self.value)

# A Roundtrip is an abstraction of the concept of a simulteneaous Bull and a Bear entry
# Given a Robot and a root_id, the RoundTrip can retrieve both the bull and the bear and manage various aspects of it 
# elegantly (in an Object Oriented way) and with programmatic clarity via a single Interface/Namespace/Class.
# In the Egghead Project, Bulls and Bears are always acquired in Pairs. They don't have to be disposed of in Pairs. 
# The main role of the RounTrip Class is to fully manage that abstraction and provide programmatic/algorithmic clarity
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

  def __str__(self):
    str_data = ''
    if self.isCompleted():
      bull="\nCompleted: Bull:{0:4} {1:4} {2:6} {3} {4}".format(self.getBullSymbol(),self.getBullQuantity(),self.getBullBuyPrice(),self.getBullBuyDate(),self.getBullSellDate())
      bear="\n           Bear:{0:4} {1:4} {2:6} {3} {4}".format(self.getBearSymbol(),self.getBearQuantity(),self.getBearBuyPrice(),self.getBearBuyDate(),self.getBearSellDate())
    elif self.isStable():
      name_id=self.getRootOrderClientIDNoInternal()
      bull="\nStable: Bull:{0:4} {1:4} {2:6} {3} {4}".format(self.getBullSymbol(),self.getBullQuantity(),self.getBullBuyPrice(),self.getBullBuyDate(),name_id)
      bear="\n        Bear:{0:4} {1:4} {2:6} {3} {4}".format(self.getBearSymbol(),self.getBearQuantity(),self.getBearBuyPrice(),self.getBearBuyDate(),name_id)
    elif self.isInTransition():
      bull="\nTransition: Bull:{0:4} {1:4} {2:6} {3} {4}".format(self.getBullSymbol(),self.getBullQuantity(),self.getBullBuyPrice(),self.getBullBuyDate(),self.getBullSellDate())
      bear="\n            Bear:{0:4} {1:4} {2:4} {3:6} {4}".format(self.getBearSymbol(),self.getBearQuantity(),self.getBearBuyPrice(),self.getBearBuyDate(),self.getBearSellDate())
    return bull + bear

  def getDetailedInformation(self,bull_info='',bear_info=''):
      name_id=self.getRootOrderClientIDNoInternal()
      bull="\nStable: Bull:{0} {1} {2} {3} {4} {5}".format(self.getBullSymbol(),self.getBullQuantity(),self.getBullBuyPrice(),self.getBullBuyDate(),name_id,bull_info)
      bear="\n        Bear:{0} {1} {2} {3} {4} {5}".format(self.getBearSymbol(),self.getBearQuantity(),self.getBearBuyPrice(),self.getBearBuyDate(),name_id,bear_info)
      return bull+bear

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


##########################################################################################
#
#  Root Client ID Information
#
  def getRootOrderClientID(self):
        return self.root_order_client_id

  #TODO: NO UNITTEST FOR THIS
  def getWinningOrderClientIDRoot(self):
    if not (self.getTheBull().winning_order_client_id == None):
      return self.getTheBull().winning_order_client_id
    if not (self.getTheBear().winning_order_client_id == None):
      return self.getTheBear().winning_order_client_id
    return None

  def getRootOrderClientIDNoInternal(self):
        return self.root_order_client_id.replace(self.robot.getInternalName()+'_','')

  def getBullBuyOrderClientID(self):
        return self.getRootOrderClientID() + "_buy_" + self.getBullSymbol()

  def getBearBuyOrderClientID(self):
        return self.getRootOrderClientID() + "_buy_" + self.getBearSymbol  ()

  def getBullSellOrderClientID(self):
        return self.getRootOrderClientID() + "_sell_" + self.getBullSymbol()

  def getBearSellOrderClientID(self):
        return self.getRootOrderClientID() + "_sell_" + self.getBearSymbol()

###########################################################################################
#
#  Bull / Bear Ratio
#
  #Of all the money spent to acquire Bull + Bear, what percentage went to Bull?
  #Ideally, we should be close to 50%
  def getCostBasisBullRatio(self):
    total_cost_basis = self.getRoundtripCostBasis()
    bull_cost_basis = self.getBullCostBasis()
    return 100 * (bull_cost_basis/total_cost_basis)

  #Of all the money speant to acquire Bull + Bear, what percentage went to Bear?
  #Ideally, we should be close to 50%
  def getCostBasisBearRatio(self):
    total_cost_basis = self.getRoundtripCostBasis()
    bear_cost_basis = self.getBearCostBasis()
    return 100 * (bear_cost_basis/total_cost_basis)

  #Of the total value of the asset, what percentage does the Bull contribute
  def getCurrentValueBasedBearRatio(self):
    total_current_value = self.getRoundtripUnrealizedValue()
    bear_current_value = self.getBearCurrentValue()
    return 100 * (bear_current_value/total_current_value)

  #Of the total value of the asset, what percentage does the Bear contribute
  def getCurrentValueBasedBullRatio(self):
    total_current_value = self.getRoundtripUnrealizedValue()
    bull_current_value = self.getBullCurrentValue()
    return 100 * (bull_current_value/total_current_value)

  # Change in Ratio from the time of purchase to today
  def getBullCostBasisRatioDelta(self):
    return self.getCostBasisBullRatio() - self.getCurrentValueBasedBullRatio()

  # Change in Ratio from the time of purchase to today
  def getBearCostBasisRatioDelta(self):
    return self.getCostBasisBearRatio() - self.getCurrentValueBasedBearRatio()


  def getStringForRatio(self):
    cb_bull_ratio = self.getCostBasisBullRatio()
    cb_bear_ratio = self.getCostBasisBearRatio()
    cv_bull_ratio = self.getCurrentValueBasedBullRatio()
    cv_bear_ratio = self.getCurrentValueBasedBearRatio()
    bull_cb_delta = self.getBullCostBasisRatioDelta()
    bear_cb_delta = self.getBearCostBasisRatioDelta()

    return "Cost Basis - Bull: {0:,.2f}. Bear: {1:,.2f}. Current Value - Bull:{2:,.2f}. Bear: {3:,.2f}.  Deltas - Bull: {4:,.2f}  Bear: {5:,.2f}".format(cb_bull_ratio,\
          cb_bear_ratio, cv_bull_ratio, cv_bear_ratio, bull_cb_delta, bear_cb_delta )



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

########## Time/Age and State functions #############
  #By default, the minimumHoldTime is 0.
  def isPastMinimumHoldTime(self):
    if shouldUsePrint():
      print("Minimum Hold time: {} Time Since Purchase: {} ".format(self.robot.getMinHoldTimeInMinutes(),self.getTimeSincePurchase()))
    return self.getTimeSincePurchase() > self.robot.getMinHoldTimeInMinutes()

  #By default, the maximumHoldTime is 14.
  def isPastMaximumHoldTime(self):
    if shouldUsePrint():
      print("Maximum Hold time: {} Time Since Purchase: {} ".format(self.robot.getMaxHoldTimeInMinutes(),self.getTimeSincePurchase()))
    return self.getTimeSincePurchase() > self.robot.getMaxHoldTimeInMinutes()

  #Between MinHoldTime and MaxHoldTime
  def isAvailableForTrading(self):
    return self.isPastMinimumHoldTime() and (not self.isPastMaximumHoldTime())

  #duration:
  def isInRegression(self):
    regression_start = self.robot.getRegressionStartDayInMinutes()
    max_hold_time = self.robot.getMaxHoldTimeInMinutes()
    if shouldUsePrint():
      print("Regression Start:{}".format(regression_start))
    return regression_start < self.getTimeSincePurchase() < max_hold_time

  def isInRegressionLevelYellow(self):
    regression_start = self.robot.getRegressionStartDayInMinutes()
    max_hold_time = self.robot.getMaxHoldTimeInMinutes()
    diff_regression = (max_hold_time - regression_start)/3
    return (regression_start) < self.getTimeSincePurchase() < (regression_start+diff_regression)

  def isInRegressionLevelOrange(self):
    regression_start = self.robot.getRegressionStartDayInMinutes()
    max_hold_time = self.robot.getMaxHoldTimeInMinutes()
    diff_regression = 2*((max_hold_time - regression_start)/3)
    return (regression_start+diff_regression) < self.getTimeSincePurchase() < (regression_start+ 2*(diff_regression))

  def isInRegressionLevelRed(self):
    regression_start = self.robot.getRegressionStartDayInMinutes()
    max_hold_time = self.robot.getMaxHoldTimeInMinutes()
    diff_regression = 2*((max_hold_time - regression_start)/3)
    return (regression_start+ 2*(diff_regression)) < self.getTimeSincePurchase() < max_hold_time

#####################################################################################################
#
#  Single Equality / List of Possible Matches
#  Two Roundtrip are equals, if they have the same rootorderclientID
#
#  containedInRoundtrips(roundtrip_list): returns True if self is contained in the roundtrip_list
#
  def equalsRoundtrip(self,candidate=None):
    return False if (candidate==None) else (candidate.getRootOrderClientID()==self.getRootOrderClientID())

  def containedInRoundtrips(self,roundtrip_list=None):
    if roundtrip_list==None:
      return False
    candidates = [c for c in roundtrip_list if c.equalsRoundtrip(candidate=self) ]

    return False if len(candidates)==0 else True


##################################################################################
#
#  Stages Transition Filters : TODO.
# This needs to be properly designed to take various compositions into account.
# Intentionally defer the Bull/Bear Ratio aspect to the caller
#
  def getProfitTargetPerRoundtrip(self):
    return self.robot.getProfitTargetPerRoundtrip()

  def getBullTransitionProfitTarget(self):
    return self.robot.getBullTransitionProfitTarget()

  def getBearTransitionProfitTarget(self):
    return self.robot.getBearTransitionProfitTarget()

  def getCompletionProfitTarget(self):
        return self.robot.getCompletionProfitTarget()

  def isBullTransitionalCandidate(self):
        return (self.isStable() and (self.getStableBullValue()>self.getBullTransitionProfitTarget()))

  def isBearTransitionalCandidate(self):
        return (self.isStable() and (self.getStableBearValue()>self.getBearTransitionProfitTarget()))

  def isTransitionalCandidate(self):
        return self.isBullTransitionalCandidate() or self.isBearTransitionalCandidate()

  def isCompletionCandidate(self):
    return self.isInTransition() and ( self.getTransitionalDeltaValue() > (self.getCompletionProfitTarget()))

###########################################################
#
#  Ages and Durations . Focus is on the time between
#  acquisition and completion (active period)

  # How long has this been since it was purchased (bought). The response is in minutes.
  def getTimeSincePurchase(self):
    return round((self.getCurrentTimestamp() - self.getBullBuyDate()).total_seconds()/60,2)

  def getTimeSinceCompletion(self):
        if self.isCompleted():
          return round((self.getCurrentTimestamp() - self.getDateCompleted()).total_seconds()/60,2)
        return None

  def completedToday(self):
        if self.isCompleted():
          co_day = self.getDateCompleted().day
          co_month=self.getDateCompleted().month
          co_year =self.getDateCompleted().year
          cu_day = self.getCurrentTimestamp().day
          cu_month = self.getCurrentTimestamp().month
          cu_year = self.getCurrentTimestamp().year
          return (co_day==cu_day) and (co_month==cu_month) and (co_year==cu_year)
        return None

  def completedLast24Hours(self):
    if self.isCompleted():
      lapsed_minutes = round((self.getCurrentTimestamp() - self.getDateCompleted()).total_seconds()/60,2)
      return (lapsed_minutes <= 24*60)
    return None

  # The day when it was bought.
  def getInStableDate(self):
        return self.getAcquisitionDate()

 #The day when it as moved to InTransition Stage
  def getInTransitionDate(self):
    if self.isInBearishTransition():
      return self.getBullSellDate()
    elif self.isInBullishTransition():
      return self.getBearSellDate()
    elif self.isCompleted():
      if (self.getCompletionDate() == self.getBearSellDate()):
        return self.getBullSellDate()
      else:
        return self.getBearSellDate()
    return None

  #The day when it as moved to Completion Stage
  def getCompletionDate(self):
    if self.isCompleted():
      if self.getBullSellDate() > self.getBearSellDate():
        return self.getBullSellDate()
      else:
        return self.getBearSellDate()
    return None

  #How long (duration) was the asset in Stable. It is no longer in Stable
  def getTimeSpentInStable(self):
    if self.isInTransition() or self.isCompleted():
      return round((self.getInTransitionDate() - self.getInStableDate()).total_seconds()/60,2)
    return None

  #How long (duration) was the asset in Transition. It is no longer in Transition
  def getTimeSpentInTransition(self):
    if self.isCompleted():
      return round((self.getCompletionDate() - self.getInTransitionDate()).total_seconds()/60,2)
    return None

  def getTimeSpentActive(self):
    if self.isCompleted():
      return round((self.getCompletionDate() - self.getAcquisitionDate()).total_seconds()/60,2)
    return None

 # How long has this Roundtrip been in Transition Stage
  # Current State is still in-transition.
  def getDurationInTransition(self):
    if self.isInBearishTransition():
      return  round(((self.getCurrentTimestamp() - self.getBullSellDate()).total_seconds() / 60),2)
    elif self.isInBullishTransition():
      return  round(((self.getCurrentTimestamp() - self.getBearSellDate()).total_seconds() / 60),2)
    return None

  # How long has this Roundtrip been in Transition Stage
  # Current State is still in-transition.
  def getDurationInStable(self):
    if self.isStable():
      return round((self.getCurrentTimestamp() - self.getBullBuyDate()).total_seconds()/60,2)
    return None

 # It has been completed, how long did it take to complete?
  def getRoundtripAge(self):
        return self.getTimeSpentActive()
#############################################################################################################
#
#  Financial Data focused on Costbasis, Realized, Unrealized in absolute (not to confused with profits,losses)
#
  def getBullCostBasis(self):
        return self.getBullBuyPrice() * self.getBullQuantity()

  def getBearCostBasis(self):
        return self.getBearBuyPrice() * self.getBearQuantity()

  def getBullCurrentValue(self):
        return self.getTheBull().getUnRealizedValue(current_price=self.getBullCurrentPrice())

  def getBearCurrentValue(self):
        return self.getTheBear().getUnRealizedValue(current_price=self.getBearCurrentPrice())

  def getRoundtripCostBasis(self,non_digits=True):
        return self.getBullCostBasis() + self.getBearCostBasis()

  def getBullBearCostBasisDelta(self):
    return abs(self.getBullCostBasis() - self.getBearCostBasis())

  def getBullBearCurrentValueDelta(self):
    return abs(self.getBearCurrentValue() - self.getBullCurrentValue())

  def getBullRealizedValue(self,non_digits=True):
    if self.getTheBull().isRealized():
          return self.getBullSellPrice() * self.getBullQuantity()
    return None if non_digits else 0

  def getBearRealizedValue(self,non_digits=True):
    if self.getTheBear().isRealized():
      return self.getBearSellPrice() * self.getBearQuantity()
    return None if non_digits else 0

  def getTransitionalRealized(self,non_digits=True):
    if self.getTheBull().isRealized():
      return self.getTheBull().getRealizedValue()
    elif self.getTheBear().isRealized():
      return self.getTheBear().getRealizedValue()
    return None if non_digits else 0

  def getTransitionalUnRealized(self,non_digits=True):
    if self.isInBullishTransition():
      return self.getBullCurrentValue()
    elif self.isInBearishTransition():
      return self.getBearCurrentValue()
    return None if non_digits else 0

  #Calculates what has been sold either way and at any stage.
  def getRoundtripRealizedValue(self,non_digits=True):
    if self.isStable():
      return None if non_digits else 0
    elif self.isInTransition():
      return self.getTransitionalRealized()
    return self.getBullRealizedValue() + self.getBearRealizedValue()

  def getRoundtripUnrealizedValue(self,non_digits=True):
    if self.isStable():
      return self.getBullCurrentValue() + self.getBearCurrentValue()
    elif self.isInTransition():
      return self.getTransitionalUnRealized()
    return None if non_digits else 0

  # When in Transition, it means one side has sold.
  # How much money (PROFIT) did we cash in for that sale?
  def getRoundtripInTransitionRealizedProfit(self,non_digits=True):
    if self.isInBullishTransition():
      return self.getBearRealizedValue() - self.getBearCostBasis()
    elif self.isInBearishTransition():
      return self.getBullRealizedValue() - self.getBullCostBasis()
    return None if non_digits else 0

  def getRoundtripRealizedProfit(self,non_digits=True):
    if self.isCompleted():
          return self.getRoundtripRealizedValue() - self.getRoundtripCostBasis()
    elif self.isInTransition():
          return self.getRoundtripInTransitionRealizedProfit()
    return None if non_digits else 0

  def getRealizedAndSettled(self,non_digits=True):
    if self.isCompleted():
      bull_amount =self.getBullRealizedValue()
      bull_duration = self.getDurationSinceBullSold()
      bear_amount =self.getBearRealizedValue()
      bear_duration =self.getDurationSinceBearSold()
      settled_bull = self.robot.portfolio.getAvailableCashFollowingSale(duration=bull_duration,amount=bull_amount)
      settled_bear = self.robot.portfolio.getAvailableCashFollowingSale(duration=bear_duration,amount=bear_amount)
      return settled_bear + settled_bull
    elif self.isInBullishTransition():
      bear_amount = self.getBearRealizedValue()
      bear_duration = self.getDurationSinceBearSold()
      return self.robot.portfolio.getAvailableCashFollowingSale(duration=bear_duration,amount=bear_amount)
    elif self.isInBearishTransition():
      bull_amount = self.getBullRealizedValue()
      bull_duration = self.getDurationSinceBullSold()
      return self.robot.portfolio.getAvailableCashFollowingSale(duration=bull_duration,amount=bull_amount)
    return None if non_digits else 0

  def getDurationSinceBullSold(self,non_digits=True):
    if self.getTheBull().isRealized():
      return round(((self.getCurrentTimestamp() - self.getBullSellDate()).total_seconds() / 60),2)
    return None if non_digits else 0

  def getDurationSinceBearSold(self,non_digits=True):
    if self.getTheBear().isRealized():
      return round(((self.getCurrentTimestamp() - self.getBearSellDate()).total_seconds() / 60),2)
    return None if non_digits else 0

#############################################################################################################
#
#  Financial Data focused on potential Profits, losses, deltas, ... (not to confuse with absolute values)
#
  #The price spread is the difference between the purchase price and the current average price on the Assembly Line.
  def getBullPriceSpread(self,average=None):
    return abs(self.getBullBuyPrice() - average)

  #The price spread is the difference between the purchase price and the current average price on the Assembly Line.
  def getBearPriceSpread(self,average=None):
    return abs(self.getBearBuyPrice() - average)

  #The inner spread represents the differennce within the Roundtrip of the Bull vs Bear value based on current price
  #Shouldn't be large if the Asset Composition is around 50% for each side. But will get higher within the Batcham
  #Strategy. Or if we decide to to use Asset Composition different for example 60/40.
  #(if market has a bullish or bearish bias based on sentiment)
  # (Bull Current Price - Bull Cost Basis) + ( Bear Current Price - Bear Cost Basis)
  def getAbsoluteBullBearCurrentValueSpread(self):
    if self.isStable():
      return abs(self.getStableTotalValue())
    return None

  #Same calculation as above, but doesn't calculate use Absolute Value. Can be Negative.
  def getBullBearCurrentValueSpread(self):
    if self.isStable():
      return self.getStableTotalValue()
    return None


  #The spread represents the differennce within the Roundtrip of the Bull vs Bear value based on cost basis
  #Shouldn't be large if Asset Composition is around 50%. But could get higher is there is a composition discrepency.
  def getBullBearCostBasisSpread(self):
    if self.isStable():
      return abs(self.getBullBearCostBasisDelta())
    return None

  def getStableBullValue(self):
    if self.isStable():
      return self.getBullCurrentValue() - self.getBullCostBasis()
    return None

  def getStableBearValue(self):
    if self.isStable():
      return self.getBearCurrentValue() - self.getBearCostBasis()
    return None

  def getStableTotalValue(self):
    if self.isStable():
     return self.getStableBearValue() + self.getStableBullValue()
    return None

  def getTransitionalDeltaValue(self):
    if self.isInTransition():
      return self.getTransitionalTotalValue() - self.getRoundtripCostBasis()
    return None

  def getTransitionalTotalValue(self):
    if self.isInTransition():
      return self.getTransitionalRealized() + self.getTransitionalUnRealized()
    return None

#  def getRoundtripRealizedProfit(self):
#    if self.isCompleted():
#      return self.getRoundtripRealizedValue() - self.getRoundtripCostBasis()
#    return None

  def getProfitPercentage(self):
    if self.isCompleted():
      return 100*(self.getRoundtripRealizedProfit()/self.getRoundtripCostBasis())
    return None

  def getAnnualizedProfitPercentage(self):
    profit = self.getProfitPercentage()
    active = self.getTimeSpentActive()
    return None if (profit == None) or (active == None) else 100*(profit/active)

  def isRoundtripProfitPositive(self):
    if self.isCompleted() and (self.getRoundtripRealizedProfit() > 0):
      return True
    elif self.isCompleted() and (self.getRoundtripRealizedProfit() < 0):
      return False
    return  None

  def isRoundtripProfitNegative(self):
    if self.isCompleted() and (self.getRoundtripRealizedProfit() < 0):
      return True
    elif self.isCompleted() and (self.getRoundtripRealizedProfit() > 0):
      return False
    return None

  def isRoundtripProfitAboveExpectations(self):
    if self.isCompleted() and (self.getRoundtripRealizedProfit() > self.robot.getCostBasisPerRoundtrip()):
      return True
    elif self.isCompleted() and (self.getRoundtripRealizedProfit() < self.robot.getCostBasisPerRoundtrip()):
      return False
    return None

  def isRoundtriProfitBelowExpectations(self):
    if self.isCompleted() and (self.getRoundtripRealizedProfit() < self.robot.getCostBasisPerRoundtrip()):
      return True
    elif self.isCompleted() and (self.getRoundtripRealizedProfit() > self.robot.getCostBasisPerRoundtrip()):
      return False
    return None

#############################################################################################################
#
#  Financial Data focused on Acquisition Constraints (Price Proximity by Number, Profit,
#   Composition of Bull/Bear Ratio, Breakeven Prices)
#
  def isBearWithinSharePriceByNumber(self,number):
    price_delta = abs(self.getBearCurrentPrice() - self.getBearBuyPrice())
    return True if (price_delta <= number) else False

  def isBearWithinSharePriceByPercentage(self,percentage):
    price_delta_percent = 100 * abs((self.getBearCurrentPrice() - self.getBearBuyPrice())/self.getBearCurrentPrice())
    return True if (price_delta_percent <= percentage) else False

  def isBearWithinCostBasisByTotalProfit(self):
    profit = self.getBearQuantity() * abs((self.getBearCurrentPrice() - self.getBearBuyPrice()))
    profit_target = self.getProfitTargetPerRoundtrip()
    return True if (profit <= self.getProfitTargetPerRoundtrip()) else False

  def isBearWithinCostBasisByWeightedTotalProfit(self):
    profit = self.getBearQuantity() * abs((self.getBearCurrentPrice() - self.getBearBuyPrice()))
    return True if (profit <= self.robot.getBearWeightedProfitTargetPerRoundtrip()) else False
  #isBearWithinSharePriceByPercentageOfProfit
  def isBearWithinCostBasisByPercentageOfTotalProfit(self):
    percentage = self.getProfitTargetPerRoundtrip()/self.getRoundtripCostBasis()
    price_delta_percent = abs((self.getBearCurrentPrice() - self.getBearBuyPrice())/self.getBearBuyPrice())
    return True if (price_delta_percent <= percentage) else False

  def isBearWithinCostBasisByWeightedTotalPercentageOfProfit(self):
    percentage = self.robot.getBearWeightedProfitTargetPerRoundtrip()/self.getRoundtripCostBasis()
    price_delta_percent = abs((self.getBearCurrentPrice() - self.getBearBuyPrice())/self.getBearCurrentPrice())
    return True if (price_delta_percent <= percentage) else False

  def isBearWithinPriceRangeByPercentageOfProfitRatio(self,profit_percent):
    profit =  self.getBearQuantity() * abs((self.getBearCurrentPrice() - self.getBearBuyPrice()))
    profit_target = profit_percent * self.getProfitTargetPerRoundtrip()
    return True if (profit <= profit_target) else False

  def isBearPriceAboveBreakevenByTotalProfit(self):
    breakeven = self.getBearBreakevenPriceByTotalProfit()
    return True if (self.getBearCurrentPrice() >= breakeven) else False

  def isBearPriceAboveBreakevenByComponentProfitRatio(self,component_percent):
    breakeven = self.getBearBreakevenPriceByComponentProfitRatio(component_percent=component_percent)
    return True if (self.getBearCurrentPrice() >= breakeven ) else False

  def getBearBreakevenPriceByTotalProfit(self):
    breakeven_price = abs(self.getProfitTargetPerRoundtrip() + (self.getBearBuyPrice() * self.getBearQuantity() )) / self.getBearQuantity()
    return breakeven_price

  def getBearBreakevenPriceByComponentProfitRatio(self,component_percent):
    breakeven_price = abs(component_percent * self.getProfitTargetPerRoundtrip() + (self.getBearBuyPrice() * self.getBearQuantity() )) / self.getBearQuantity()
    return breakeven_price

  def getBearBreakevenPricePercentByTotalProfit(self):
    breakeven_price = abs(self.getProfitTargetPerRoundtrip() + (self.getBearBuyPrice() * self.getBearQuantity() )) / self.getBearQuantity()
    return 100 *( abs(breakeven_price - self.getBearBuyPrice())/self.getBearBuyPrice())

  def getBearBreakevenPricePercentByComponentProfitRatio(self,component_percent):
    breakeven_price = abs(component_percent * self.getProfitTargetPerRoundtrip() + (self.getBearBuyPrice() * self.getBearQuantity() )) / self.getBearQuantity()
    return 100 * ( abs(breakeven_price - self.getBearBuyPrice()) / self.getBearBuyPrice() )

###################################Bull Equivalents##########
  # buy_price = $120, current_price = $122 ==> price_delta = $2
  # if number == 1, return False. if number == 3, return True
  def isBullWithinSharePriceByNumber(self,number):
    price_delta = abs(self.getBullCurrentPrice() - self.getBullBuyPrice())
    return True if (price_delta <= number) else False

  # buy_price = $100, current_price = $102 ==> price_delta_percent = 2% = 2/100
  # if percent == 1%, return False. if percent == 3%, return True
  def isBullWithinSharePriceByPercentage(self,percentage):
    price_delta_percent = 100 * abs((self.getBullCurrentPrice() - self.getBullBuyPrice())/self.getBullCurrentPrice())
    return True if (price_delta_percent <= percentage) else False

  # buy_price = $100, quantity=10. Bull ONLY Cost Basis = $1,000. current_price = $102 ==> unrealized_profit = $20 = $1,020 - $1,000
  # if profit_target_per_roundtrip == $15, return False [$15 < $20 ].
  # if profit_target_per_roundtrip == $30, return True  [$30 > $20]
  def isBullWithinCostBasisByTotalProfit(self):
    unrealized_profit = self.getBullQuantity() * abs((self.getBullCurrentPrice() - self.getBullBuyPrice()))
    return True if (unrealized_profit <= self.getProfitTargetPerRoundtrip()) else False

  # buy_price = $100, quantity=10. Cost Basis = $1,000. Bull Composition = 50%
  # current_price = $101 ==> unrealized_profit = $10 = $1,020 - $1,000
  # if profit_target_per_roundtrip == $10, weighted profit target = $10 * 50% = $7.5 return False [$7.5 < $10 ].
  # if profit_target_per_roundtrip == $30, weighted profit target = $30 * 50% = $15 return True   [$15 > $10]
  def isBullWithinCostBasisByWeightedTotalProfit(self):
    profit = self.getBullQuantity() * abs((self.getBullCurrentPrice() - self.getBullBuyPrice()))
    return True if (profit <= self.robot.getBullWeightedProfitTargetPerRoundtrip()) else False

  # buy_price = $100, quantity=10. Bull ONLY Cost Basis = $1,000.
  # current_price = $102 ==> unrealized_profit = $20 of 1,000 invested = 2/100 = 2%
  # if profit_target_per_roundtrip == $10 or 10/1000 = 1% of investment., return False [1% < 2% ].
  # if profit_target_per_roundtrip == $30 or 30/1000 = 3% of investment.., return True [3% > 2%]
  def isBullWithinCostBasisByPercentageOfTotalProfit(self):
    percentage = self.getProfitTargetPerRoundtrip()/self.getRoundtripCostBasis()
    price_delta_percent = abs((self.getBullCurrentPrice() - self.getBullBuyPrice())/self.getBullBuyPrice())
    return True if (price_delta_percent <= percentage) else False
 #Same as above, except I use the weightedProfitTargetperroundtrip()
  # BullComposition() is important.
  def isBullWithinCostBasisByWeightedTotalPercentageOfProfit(self):
    percentage = self.robot.getBullWeightedProfitTargetPerRoundtrip()/self.getRoundtripCostBasis()
    price_delta_percent = abs((self.getBullCurrentPrice() - self.getBullBuyPrice())/self.getBullCurrentPrice())
    return True if (price_delta_percent <= percentage) else False

  #To be used with inTranstionTargetRatio() and CompletionTargetRatio()
  def isBullWithinPriceRangeByPercentageOfProfitRatio(self,profit_percent):
    profit =  self.getBullQuantity() * abs((self.getBullCurrentPrice() - self.getBullBuyPrice()))
    profit_target = profit_percent * self.getProfitTargetPerRoundtrip()
    return True if (profit <= profit_target) else False

  def isBullPriceAboveBreakevenByTotalProfit(self):
    breakeven = self.getBullBreakevenPriceByTotalProfit()
    return True if (self.getBullCurrentPrice() >= breakeven) else False

  def isBullPriceAboveBreakevenByComponentProfitRatio(self,component_percent):
    breakeven = self.getBullBreakevenPriceByComponentProfitRatio(component_percent=component_percent)
    return True if (self.getBullCurrentPrice() >= breakeven ) else False

  def getBullBreakevenPriceByTotalProfit(self):
    breakeven_price = abs(self.getProfitTargetPerRoundtrip() + (self.getBullBuyPrice() * self.getBullQuantity() )) / self.getBullQuantity()
    return breakeven_price

  def getBullBreakevenPriceByComponentProfitRatio(self,component_percent):
    breakeven_price = abs(component_percent * self.getProfitTargetPerRoundtrip() + (self.getBullBuyPrice() * self.getBullQuantity() )) / self.getBullQuantity()
    return breakeven_price

  def getBullBreakevenPricePercentByTotalProfit(self):
    breakeven_price = abs(self.getProfitTargetPerRoundtrip() + (self.getBullBuyPrice() * self.getBullQuantity() )) / self.getBullQuantity()
    return 100 *( abs(breakeven_price - self.getBullBuyPrice())/self.getBullBuyPrice())

  def getBullBreakevenPricePercentByComponentProfitRatio(self,component_percent):
    breakeven_price = abs(component_percent * self.getProfitTargetPerRoundtrip() + (self.getBullBuyPrice() * self.getBullQuantity() )) / self.getBullQuantity()
    return 100 * ( abs(breakeven_price - self.getBullBuyPrice()) / self.getBullBuyPrice() )

  def isWithinTimeRangeByNumber(self, time_interval=0):
    time_delta = self.getTimeSincePurchase() - time_interval
    return True if (time_delta <= 0) else False

#  ========================== ================ ====================== =================
  #
  #  Need to be careful.
  #  Need to generate the sell order and send it to broker. For that, i need a sell_order_client_id
  #  Need the buy_order_id to update the database. Maybe getBull() and getBear() can do the trick for me.
  #
  def sellTheBear(self,transition_root_id=None):
    bear_sale_order = dict()
    bear_sale_order['sell_order_client_id']= self.getBearSellOrderClientID()
    bear_sale_order['buy_order_client_id']= self.getBearBuyOrderClientID()
    bear_sale_order['sell_date'] = self.current_timestamp
    bear_sale_order['sell_price'] = self.current_bear_price
        # Capture the Executed Sell Order in the Database.
    #self.captureSaleOrderCompletion(order=bear_sale_order)
    TradeDataHolder.recordDispositionTransaction(robot=self.robot,order=bear_sale_order,transition_root_id=transition_root_id)
    #bear_data = TradeDataHolder.recordDispositionTransaction(robot=None,order=sale_order)



  def sellTheBull(self,transition_root_id=None):
        # TODO: Execute the Sell order on the Brokerage.
    bull_sale_order = dict()
    bull_sale_order['sell_order_client_id']= self.getBullSellOrderClientID()
    bull_sale_order['buy_order_client_id']= self.getBullBuyOrderClientID()
    bull_sale_order['sell_date'] = self.current_timestamp
    bull_sale_order['sell_price'] = self.current_bull_price

        # Capture the Executed Sell Order in the Database.
    #self.captureSaleOrderCompletion(order=bull_sale_order)
    TradeDataHolder.recordDispositionTransaction(robot=self.robot,order=bull_sale_order,transition_root_id=transition_root_id)

 
  def sellTheUnrealized(self):
    if self.getTheBull().isUnRealized():
      self.sellTheBull()
      if shouldUsePrint():
        print("Roundtrip Completed. Bull was sold. {0}".format(self.printProfitAndLosses()))
    else:
      self.sellTheBear()
      if shouldUsePrint():
            print("Roundtrip Completed. Bear was sold. {0}".format(self.printProfitAndLosses()))


  def printProfitAndLosses(self):
    cost_basis = self.getTheBull().getCostBasis() + self.getTheBear().getCostBasis()
    realized = self.getTheBull().getRealizedValue() + self.getTheBear().getRealizedValue()
    profit = realized - cost_basis
    profit_per = round(profit /cost_basis,2)
    return ("Cost Basis= {0}. Realized {1}. Profit($)= {2}. Profit(%)= {3}.".format(cost_basis,realized,profit,profit_per))




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

  def getTradableAssetsSize(self):
    tradable = [ c for c in self.stable_list if (c.isPastMinimumHoldTime())]
    return len(tradable)

###Returns List in either increasing or decreasing (reverse=True or False ) Order ###################
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

  def getAllStableEntriesByBearPrice(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBearBuyPrice(),reverse=True)
    return candidates

  def getAllStableEntriesByBearCostBasis(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBearCostBasis(),reverse=True)
    return candidates

  def getAllStableEntriesByBullCostBasis(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBullCostBasis(),reverse=True)
    return candidates

  def getAllStableEntriesByBullValue(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getStableBullValue(),reverse=True)
    return candidates

  def getAllStableEntriesByBearValue(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getStableBearValue(),reverse=True)
    return candidates
 
#############################################################################
  #Percentage of price increase/decrease based on the given number of entries. 
  #TODO: The next two functions are work in progress
  def getBullPriceTrend(self,entries=None):
    candidates = self.stable_list
    if len(candidates) == 0:
      return 0 

    if len(candidates) == 1:
      return 0 

    all_entries = len(candidates) if entries==None else entries
    candidates.sort(key=lambda rt:rt.getStableBearValue(),reverse=True)
    return 0 

  #Percentage of price increase/decrease based on the given number of entries. 
  def getAverageBullPriceTrend(self,entries=None):
    candidates = self.stable_list
    if len(candidates) == 0:
      return 0 

    return 0 
 
#################################################################################
  def getCurrentBullCompositionRatio(self):
    bull_current_value_list = [c.getBullCurrentValue() for c in self.stable_list  ]
    bear_current_value_list = [c.getBearCurrentValue() for c in self.stable_list  ]
    total_value = sum(bull_current_value_list) + sum(bear_current_value_list)
    return 0 if len(self.stable_list) == 0 else 100 * (sum(bull_current_value_list)/total_value)

  def getCurrentBearCompositionRatio(self):
    bull_current_value_list = [c.getBullCurrentValue() for c in self.stable_list  ]
    bear_current_value_list = [c.getBearCurrentValue() for c in self.stable_list  ]
    total_value = sum(bull_current_value_list) + sum(bear_current_value_list)
    return 0 if len(self.stable_list) == 0 else 100 * (sum(bear_current_value_list)/total_value)

  def getTotalCurrentStableSpread(self):
    price_spread = [c.getBullBearCurrentValueSpread() for c in self.stable_list]
    return sum(price_spread)

  def getNegativeBullPriceSpread(self):
    price_spread = [c.getBullBearCurrentValueSpread() for c in self.stable_list]
    return sum(price_spread)

  #1. What's the price spread on Stable?
  #2. How many negative spread attributed to Bulls?
  #3. How many negative spread attributed to Bears?
  def getCurrentTrend(self):
    stable_portfolio_trend = dict()
    stable_portfolio_trend['type'] = 'stable_value_spread'
    stable_portfolio_trend['spread_total_value'] = self.getTotalCurrentStableSpread()
    stable_portfolio_trend['stable_size'] = self.getStableSize()
    stable_portfolio_trend['current_bull_composition'] = self.getCurrentBullCompositionRatio()
    stable_portfolio_trend['current_bear_composition'] = self.getCurrentBearCompositionRatio()
    stable_portfolio_trend['negatives_bull_spread'] = 5
    stable_portfolio_trend['negatives_bear_spread'] = 2
    
    return stable_portfolio_trend

# ------------------Spread based on ONLY ELLIGIBLE Average on Assembly line Price ---------------------------------
  def getMaxBearSpreadToAverageElligiblePrice(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    if len(candidates) == 0:
      return candidates

    #Calculate the Average based on buyPrice() for Elligible ONLY
    avg = sum([c.getBearBuyPrice() for c in candidates]) / len(candidates)

    #Sort by the criteria given bearPriceSpread(bearbuyprice - avg)
    candidates.sort(key=lambda rt:rt.getBearPriceSpread(average=avg),reverse=True)
    return candidates     

  def getMaxBullSpreadToAverageElligiblePrice(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    if len(candidates) == 0:
      return candidates

    #Calculate the Average based on buyPrice() for Elligible ONLY
    avg = sum([c.getBullBuyPrice() for c in candidates]) / len(candidates)

    #Sort by the criteria given bearPriceSpread(bearbuyprice - avg)
    candidates.sort(key=lambda rt:rt.getBullPriceSpread(average=avg),reverse=True)
    return candidates     

  def getMinBearSpreadToAverageElligiblePrice(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    if len(candidates) == 0:
      return candidates

    #Calculate the Average based on buyPrice() for Elligible ONLY
    avg = sum([c.getBearBuyPrice() for c in candidates]) / len(candidates)

    #Sort by the criteria given bearPriceSpread(bearbuyprice - avg)
    candidates.sort(key=lambda rt:rt.getBearPriceSpread(average=avg),reverse=False)
    return candidates     

  def getMinBullSpreadToAverageElligiblePrice(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    if len(candidates) == 0:
      return candidates

    #Calculate the Average based on buyPrice() for Elligible ONLY
    avg = sum([c.getBullBuyPrice() for c in candidates]) / len(candidates)

    #Sort by the criteria given bearPriceSpread(bearbuyprice - avg)
    candidates.sort(key=lambda rt:rt.getBullPriceSpread(average=avg),reverse=False)
    return candidates     


# ------------------Spread based on Average Assembly line Price ---------------------------------
  def getMaxBearSpreadToAveragePrice(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    if len(candidates) == 0:
      return candidates

    #Calculate the Average based on buyPrice() for ALL
    avg = sum([c.getBearBuyPrice() for c in self.stable_list]) / len(self.stable_list)
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBearPriceSpread(average=avg),reverse=True)
    return candidates     

  def getMaxBullSpreadToAveragePrice(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    if len(candidates) == 0:
      return candidates

    #Calculate the Average based on buyPrice() for ALL
    avg = sum([c.getBullBuyPrice() for c in self.stable_list]) / len(self.stable_list)
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBullPriceSpread(average=avg),reverse=True)
    return candidates     

  def getMinBearSpreadToAveragePrice(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    if len(candidates) == 0:
      return candidates

    #Calculate the Average based on buyPrice() for ALL
    avg = sum([c.getBearBuyPrice() for c in self.stable_list]) / len(self.stable_list)
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBearPriceSpread(average=avg),reverse=False)
    return candidates     

  def getMinBullSpreadToAveragePrice(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    if len(candidates) == 0:
      return candidates

    #Calculate the Average based on buyPrice() for ALL
    avg = sum([c.getBullBuyPrice() for c in self.stable_list]) / len(self.stable_list)
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBullPriceSpread(average=avg),reverse=False)
    return candidates     


# ------------------Roundtrip Inner Spread based on own Price Only (Current Value -  CostBasis ) ---------------------------------
  def getMaxBullBearCostBasisSpread(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBullBearCostBasisDelta(),reverse=True)

    return candidates     

  def getMaxBullBearCurrentValueSpread(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBullBearCurrentValueDelta(),reverse=True)

    return candidates     

  def getMinBullBearCostBasisSpread(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBullBearCostBasisDelta(),reverse=False)
    return candidates     

  def getMinBullBearCurrentValueSpread(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBullBearCurrentValueDelta(),reverse=False)
    return candidates     

# ------------------Asset Acquisition Price Based ---------------------------------------------------
  def getMostExpensiveBearCandidates(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBearBuyPrice(),reverse=True)
    return candidates 

  def getMostExpensiveBullCandidates(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBullBuyPrice(),reverse=True)
    return candidates 

  def getLeastExpensiveBearCandidates(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBearBuyPrice(),reverse=False)
    return candidates 

  def getLeastExpensiveBullCandidates(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBullBuyPrice(),reverse=False)
    return candidates 

# ------------------Asset Performance Based (Current Value - Cost Basis) ---------------------------------
  def getBestBearCandidates(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getStableBearValue(),reverse=True)
    return candidates 

  def getBestBullCandidates(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    candidates.sort(key=lambda rt:rt.getStableBullValue(),reverse=True)
    return candidates 

  def getWorstBearCandidates(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getStableBearValue(),reverse=False)
    return candidates 

  def getWorstBullCandidates(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getStableBullValue(),reverse=False)
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

  def getTheMostExpensiveBullEntry(self):
    candidates = self.getAllStableEntriesByBullPrice()
    return None if len(candidates) == 0 else candidates[0]

  def getTheMostExpensiveBearEntry(self):
    candidates = self.getAllStableEntriesByBearPrice()
    return None if len(candidates) == 0 else candidates[0]

  def getTheLeastExpensiveBullEntry(self):
    candidates = self.getAllStableEntriesByBullPrice()
    return None if len(candidates) == 0 else candidates[-1]

  def getTheLeastExpensiveBearEntry(self):
    candidates = self.getAllStableEntriesByBearPrice()
    return None if len(candidates) == 0 else candidates[-1]

  def getWorstPerformingBearInStage(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getStableBearValue(),reverse=False)
    return None if len(candidates) == 0 else candidates[0]

  def getWorstPerformingBullInStage(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getStableBullValue(),reverse=False)
    return None if len(candidates) == 0 else candidates[0]

  def getBestPerformingBearInStage(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getStableBearValue(),reverse=True)
    return None if len(candidates) == 0 else candidates[0]

  def getBestPerformingBullInStage(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getStableBullValue(),reverse=True)
    return None if len(candidates) == 0 else candidates[0]

  def getAverageBullCostBasis(self):
    candidates = [c.getBullCostBasis() for c in self.stable_list  ]
    return 0 if len(candidates) == 0 else (sum(candidates)/len(candidates))

  def getAverageBearCostBasis(self):
    candidates = [c.getBearCostBasis() for c in self.stable_list  ]
    return 0 if len(candidates) == 0 else (sum(candidates)/len(candidates))

  def getAverageBullPrice(self):
    vals = [c.getBullBuyPrice() for c in self.stable_list  ]
    return 0 if len(vals) == 0 else (sum(vals)/len(vals))

  def getAverageBearPrice(self):
    vals = [c.getBearBuyPrice() for c in self.stable_list  ]
    return 0 if len(vals) == 0 else (sum(vals)/len(vals))

  def getSpreadBullPrice(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBullBuyPrice(),reverse=True)
    return 0 if len(candidates) == 0 else (candidates[0].getBullBuyPrice() - candidates[-1].getBullBuyPrice())

  def getSpreadBearPrice(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBearBuyPrice(),reverse=True)
    return 0 if len(candidates) == 0 else (candidates[0].getBearBuyPrice() - candidates[-1].getBearBuyPrice())

  def getSpreadPercentToMaxBullPrice(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBullBuyPrice(),reverse=True)
    return 0 if len(candidates) == 0 else 100*((candidates[0].getBullBuyPrice() - candidates[-1].getBullBuyPrice())/candidates[0].getBullBuyPrice())

  def getSpreadPercentToMaxBearPrice(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBearBuyPrice(),reverse=True)
    return 0 if len(candidates) == 0 else 100*((candidates[0].getBearBuyPrice() - candidates[-1].getBearBuyPrice())/candidates[0].getBearBuyPrice())

  def getSpreadPercentToMinBullPrice(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBullBuyPrice(),reverse=True)
    return 0 if len(candidates) == 0 else 100*((candidates[0].getBullBuyPrice() - candidates[-1].getBullBuyPrice())/candidates[-1].getBullBuyPrice())

  def getSpreadPercentToMinBearPrice(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBearBuyPrice(),reverse=True)
    return 0 if len(candidates) == 0 else 100*((candidates[0].getBearBuyPrice() - candidates[-1].getBearBuyPrice())/candidates[-1].getBearBuyPrice())

  def getSpreadPercentToAverageBearPrice(self):
    bear_avg_price = self.getAverageBearPrice()
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBearBuyPrice(),reverse=True)
    return 0 if len(candidates) == 0 else 100*((candidates[0].getBearBuyPrice() - candidates[-1].getBearBuyPrice())/bear_avg_price)

  def getSpreadPercentToAverageBullPrice(self):
    bull_avg_price = self.getAverageBullPrice()
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBullBuyPrice(),reverse=True)
    return 0 if len(candidates) == 0 else 100*((candidates[0].getBullBuyPrice() - candidates[-1].getBullBuyPrice())/bull_avg_price)




  def getLowestBullCostBasis(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBullCostBasis(),reverse=False)
    return None if len(candidates) == 0 else candidates[0]
    
  def getHighestBullCostBasis(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBullCostBasis(),reverse=True)
    return None if len(candidates) == 0 else candidates[0]
    
  def getHighestBearCostBasis(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBearCostBasis(),reverse=True)
    return None if len(candidates) == 0 else candidates[0]

  def getLowestBearCostBasis(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBearCostBasis(),reverse=False)
    return None if len(candidates) == 0 else candidates[0]
 
  def getTotalBearCostBasis(self):
    vals = [c.getBearCostBasis() for c in self.stable_list  ]
    sum_bears = sum(vals)
    return  sum_bears
    
  def getTotalBullCostBasis(self):
    vals = [c.getBullCostBasis() for c in self.stable_list  ]
    sum_bulls = sum(vals)
    return  sum_bulls

  def getTotalCostBasis(self):
    return self.getTotalBullCostBasis() + self.getTotalBearCostBasis()

  def getOldestStageRoundtripEntry(self):
    candidates = self.getAllStableEntriesByAgeOldestFirst()
    return None if len(candidates) == 0 else candidates[0]
      
  def getYoungestStageRoundtripEntry(self):
    candidates = self.getAllStableEntriesByAgeYoungestFirst()
    return None if len(candidates) == 0 else candidates[0]

  def getTimeEllapsedSinceYoungestAcquisition(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getTimeSincePurchase(),reverse=False)
    return None if len(candidates) == 0 else candidates[0]

  def getTimeEllapsedSinceOldestAcquisition(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getTimeSincePurchase(),reverse=True)
    return None if len(candidates) == 0 else candidates[0]

  def getAgeDifferenceBetweenOldestAndYoungestInStage(self):
    ellapsed_old = self.getTimeEllapsedSinceOldestAcquisition()
    ellapsed_yng = self.getTimeEllapsedSinceYoungestAcquisition()
    if not (ellapsed_old == None) and not (ellapsed_yng==None):
      return ellapsed_old.getTimeSincePurchase() - ellapsed_yng.getTimeSincePurchase()
    
    return None 

  def getNumberOfAssetsAcquiredWithinTimeframe(self,timeframe=60):
    candidates = [c for c in self.stable_list if (c.getTimeSincePurchase()<=timeframe) ]
    return len(candidates) 

  #If price proximity is set. current_bull_price, current_bear_price are already passed. 
  def isAssetToBuyWithinPriceRange(self,type_used,rule_used,number_bull,number_bear):
    logger.info("Type_used={0}. rule_used={1}. number_bear={2}. number_bull={3}.".format(type_used,rule_used,number_bear,number_bull))
    if len(self.stable_list) == 0:
      return False 

    if   rule_used.lower() == 'bull' and (type_used.lower() == 'number' or type_used.lower() == 'number_stock'):
      candidates = [c for c in self.stable_list if c.isBullWithinSharePriceByNumber(number=number_bull) ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bull' and type_used.lower() == 'percentage_stock':
      candidates = [c for c in self.stable_list if c.isBullWithinSharePriceByPercentage(percentage=number_bull) ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bull' and type_used.lower() == 'percentage_profit':
      candidates = [c for c in self.stable_list if c.isBullWithinCostBasisByPercentageOfTotalProfit() ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bull' and type_used.lower() == 'number_profit':
      candidates = [c for c in self.stable_list if c.isBullWithinCostBasisByTotalProfit() ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bull' and type_used.lower() == 'weighted_percent_profit':
      candidates = [c for c in self.stable_list if c.isBullWithinCostBasisByWeightedTotalPercentageOfProfit() ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bull' and type_used.lower() == 'weighted_number_profit':
      candidates = [c for c in self.stable_list if c.isBullWithinCostBasisByWeightedTotalProfit() ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bull' and (type_used.lower() == 't_percent_profit' or type_used.lower() == 'c_percent_profit'):
      profit_target = self.robot.getInTransitionProfitTargetRatio() if (type_used.lower() == 't_percent_profit') else self.robot.getCompletionProfitTargetRatio()
      candidates = [c for c in self.stable_list if c.isBullWithinPriceRangeByPercentageOfProfitRatio(profit_percent=profit_target) ]
      return True if (len(candidates) > 0) else False

    elif rule_used.lower() == 'bear' and (type_used.lower() == 'number' or type_used.lower() == 'number_stock'):
      candidates = [c for c in self.stable_list if c.isBearWithinSharePriceByNumber(number=number_bear) ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bear' and type_used.lower() == 'percentage_stock':
      candidates = [c for c in self.stable_list if c.isBearWithinSharePriceByPercentage(percentage=number_bear) ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bear' and type_used.lower() == 'percentage_profit':
      candidates = [c for c in self.stable_list if c.isBearWithinCostBasisByPercentageOfTotalProfit() ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bear' and type_used.lower() == 'number_profit':
      candidates = [c for c in self.stable_list if c.isBearWithinCostBasisByTotalProfit() ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bear' and type_used.lower() == 'weighted_percent_profit': 
      candidates = [c for c in self.stable_list if c.isBearWithinCostBasisByWeightedTotalPercentageOfProfit() ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bear' and type_used.lower() == 'weighted_number_profit':
      candidates = [c for c in self.stable_list if c.isBearWithinCostBasisByWeightedTotalProfit() ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bear' and (type_used.lower() == 't_percent_profit' or type_used.lower() == 'c_percent_profit'):
      profit_target = self.robot.getInTransitionProfitTargetRatio() if (type_used.lower() == 't_percent_profit') else self.robot.getCompletionProfitTargetRatio()
      candidates = [c for c in self.stable_list if c.isBearWithinPriceRangeByPercentageOfProfitRatio(profit_percent=profit_target) ]
      return True if (len(candidates) > 0) else False

    elif rule_used.lower() == 'both' and (type_used.lower() == 'number' or type_used.lower() == 'number_stock'):
      candidates_bull = [c for c in self.stable_list if c.isBullWithinSharePriceByNumber(number=number_bull) ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinSharePriceByNumber(number=number_bear) ]
      return True if (len(candidates_bear) > 0) and (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'both' and type_used.lower() == 'percentage_stock':
      candidates_bull = [c for c in self.stable_list if c.isBullWithinSharePriceByPercentage(percentage=number_bull) ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinSharePriceByPercentage(percentage=number_bear) ]
      return True if (len(candidates_bear) > 0) and (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'both' and type_used.lower() == 'percentage_profit':
      candidates_bull = [c for c in self.stable_list if c.isBullWithinCostBasisByPercentageOfTotalProfit() ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinCostBasisByPercentageOfTotalProfit() ]
      return True if (len(candidates_bear) > 0) and (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'both' and type_used.lower() == 'number_profit':
      candidates_bull = [c for c in self.stable_list if c.isBullWithinCostBasisByTotalProfit() ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinCostBasisByTotalProfit() ] 
      return True if (len(candidates_bear) > 0) and (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'both' and type_used.lower() == 'weighted_percent_profit':
      candidates_bull = [c for c in self.stable_list if c.isBullWithinCostBasisByWeightedTotalPercentageOfProfit() ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinCostBasisByWeightedTotalPercentageOfProfit() ]
      return True if (len(candidates_bear) > 0) and (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'both' and type_used.lower() == 'weighted_number_profit':
      candidates_bull = [c for c in self.stable_list if c.isBullWithinCostBasisByWeightedTotalProfit() ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinCostBasisByWeightedTotalProfit() ]
      return True if (len(candidates_bear) > 0) and (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'both' and (type_used.lower() == 't_percent_profit' or type_used.lower() == 'c_percent_profit'):
      profit_target = self.robot.getInTransitionProfitTargetRatio() if (type_used.lower() == 't_percent_profit') else self.robot.getCompletionProfitTargetRatio()
      candidates_bull = [c for c in self.stable_list if c.isBullWithinPriceRangeByPercentageOfProfitRatio(profit_percent=profit_target) ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinPriceRangeByPercentageOfProfitRatio(profit_percent=profit_target) ]
      return True if (len(candidates_bear) > 0) and (len(candidates_bull) > 0) else False

    elif rule_used.lower() == 'either' and (type_used.lower() == 'number' or type_used.lower() == 'number_stock'):
      candidates_bull = [c for c in self.stable_list if c.isBullWithinSharePriceByNumber(number=number_bull) ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinSharePriceByNumber(number=number_bear) ]
      return True if (len(candidates_bear) > 0) or (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'either' and type_used.lower() == 'percentage_stock':
      candidates_bull = [c for c in self.stable_list if c.isBullWithinSharePriceByPercentage(percentage=number_bull) ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinSharePriceByPercentage(percentage=number_bear) ]
      return True if (len(candidates_bear) > 0) or (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'either' and type_used.lower() == 'percentage_profit':
      candidates_bull = [c for c in self.stable_list if c.isBullWithinCostBasisByPercentageOfTotalProfit() ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinCostBasisByPercentageOfTotalProfit() ]
      return True if (len(candidates_bear) > 0) or (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'either' and type_used.lower() == 'number_profit':
      candidates_bull = [c for c in self.stable_list if c.isBullWithinCostBasisByTotalProfit() ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinCostBasisByTotalProfit() ] 
      return True if (len(candidates_bear) > 0) or (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'either' and type_used.lower() == 'weighted_percent_profit':
      candidates_bull = [c for c in self.stable_list if c.isBullWithinCostBasisByWeightedTotalPercentageOfProfit() ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinCostBasisByWeightedTotalPercentageOfProfit() ]
      return True if (len(candidates_bear) > 0) or (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'either' and type_used.lower() == 'weighted_number_profit':
      candidates_bull = [c for c in self.stable_list if c.isBullWithinCostBasisByWeightedTotalProfit() ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinCostBasisByWeightedTotalProfit() ]
      return True if (len(candidates_bear) > 0) or (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'either' and (type_used.lower() == 't_percent_profit' or type_used.lower() == 'c_percent_profit'):
      profit_target = self.robot.getInTransitionProfitTargetRatio() if (type_used.lower() == 't_percent_profit') else self.robot.getCompletionProfitTargetRatio()
      candidates_bull = [c for c in self.stable_list if c.isBullWithinPriceRangeByPercentageOfProfitRatio(profit_percent=profit_target) ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinPriceRangeByPercentageOfProfitRatio(profit_percent=profit_target) ]
      return True if (len(candidates_bear) > 0) or (len(candidates_bull) > 0) else False
    return False 

  #If relative time proximity is set
  def isAssetToPurchaseWithinTimeRangeByNumber(self,time_interval):
    candidates = [c for c in self.stable_list if c.isWithinTimeRangeByNumber(time_interval=time_interval) ]
    return True if len(candidates) > 0  else False

  def isBullToBearCostBasisWithinRatioPercentage(self,ratio_percent=10):
    total_cost = self.getTotalCostBasis()
    cost_delta = abs(self.getTotalBullCostBasis() - self.getTotalBearCostBasis())
    return None if (cost_delta==0 or cost_delta==None or (total_cost==0) or (total_cost==None)) else ((100*(cost_delta / total_cost))<ratio_percent)

  #
  # Retrieve all the Roundtrips, where the Bull matches the winning criteria.
  # All the ones on the exclusive_list will be removed. 
  # count: Number of entries to return. exclude_list: 
  # list of Roundtrips to exclude from the list.
  # best: Winners could be Best Performers(True) or Worst Performers (False)
  # 
  def getStableWinningBulls(self,count=1,exclude_list=None, best=True):
    candidates = []
    strategy_type = self.robot.getTransitionStrategyType()
    min_hold_time = None if (self.robot.getMinHoldTimeInMinutes()==0.0) else self.robot.getMinHoldTimeInMinutes()

    if (strategy_type == None) or (strategy_type=='performance'):
      candidates = self.getBestBullCandidates(minimal_age=min_hold_time) if (best==True) else self.getWorstBullCandidates(minimal_age=min_hold_time)
    elif strategy_type == 'asset_price':
      candidates = self.getMostExpensiveBullCandidates(minimal_age=min_hold_time) if (best==True) else self.getLeastExpensiveBullCandidates(minimal_age=min_hold_time)
    elif strategy_type == 'price_inner_spread':
      candidates = self.getMaxBullBearCurrentValueSpread(minimal_age=min_hold_time) if (best==True) else self.getMinBullBearCurrentValueSpread(minimal_age=min_hold_time)
    elif strategy_type == 'price_average_spread':
      candidates = self.getMaxBullSpreadToAveragePrice(minimal_age=min_hold_time) if (best==True) else self.getMinBullSpreadToAveragePrice(minimal_age=min_hold_time)
    elif strategy_type == 'price_average_spread_elligible_only':
      candidates = self.getMaxBullSpreadToAverageElligiblePrice(minimal_age=min_hold_time) if (best==True) else self.getMinBullSpreadToAverageElligiblePrice(minimal_age=min_hold_time)
    
    if candidates == None or len(candidates) == 0: 
      return None 

    if exclude_list == None:
      return candidates[0:count]

    final_candidates = [c for c in candidates if not(c.containedInRoundtrips(roundtrip_list=exclude_list))]
    return final_candidates[0:count]


  def getStableWinningBears(self,count=1,exclude_list=None,best=True):
    candidates = []
    strategy_type = self.robot.getTransitionStrategyType()
    min_hold_time = None if (self.robot.getMinHoldTimeInMinutes()==0.0) else self.robot.getMinHoldTimeInMinutes()

    if (strategy_type == None) or (strategy_type=='performance'):
      candidates = self.getBestBearCandidates(minimal_age=min_hold_time) if (best==True) else self.getWorstBearCandidates(minimal_age=min_hold_time)
    elif strategy_type == 'asset_price':
      candidates = self.getMostExpensiveBearCandidates(minimal_age=min_hold_time) if (best==True) else self.getLeastExpensiveBearCandidates(minimal_age=min_hold_time)
    elif strategy_type == 'price_inner_spread':
      candidates = self.getMaxBullBearCostBasisSpread(minimal_age=min_hold_time) if (best==True) else self.getMinBullBearCostBasisSpread(minimal_age=min_hold_time)
    elif strategy_type == 'price_average_spread':
      candidates = self.getMaxBearSpreadToAveragePrice(minimal_age=min_hold_time) if (best==True) else self.getMinBearSpreadToAveragePrice(minimal_age=min_hold_time)
    elif strategy_type == 'price_average_spread_elligible_only':
      candidates = self.getMaxBearSpreadToAverageElligiblePrice(minimal_age=min_hold_time) if (best==True) else self.getMinBearSpreadToAverageElligiblePrice(minimal_age=min_hold_time)

    if candidates == None or len(candidates) == 0:
      return None 

    if exclude_list == None:
      return candidates[0:count]

    final_candidates = [c for c in candidates if not(c.containedInRoundtrips(roundtrip_list=exclude_list))]
    return final_candidates[0:count]


  def getStableReport(self):
    bull_cheapest  = self.getTheLeastExpensiveBullEntry()
    bear_cheapest  = self.getTheLeastExpensiveBearEntry()
    bull_expensive = self.getTheMostExpensiveBullEntry()
    bear_expensive = self.getTheMostExpensiveBearEntry()
    bull_avg_price = self.getAverageBullPrice()
    bear_avg_price = self.getAverageBearPrice()
    bull_price_spread = self.getSpreadBullPrice()
    bear_price_spread = self.getSpreadBearPrice()
    bull_oldest = self.getOldestStageRoundtripEntry()
    bear_oldest = self.getOldestStageRoundtripEntry()
    bull_youngest= self.getYoungestStageRoundtripEntry()
    bear_youngest= self.getYoungestStageRoundtripEntry()
    age_youngest = self.getTimeEllapsedSinceYoungestAcquisition()
    age_oldest = self.getTimeEllapsedSinceOldestAcquisition()
    age_spread = self.getAgeDifferenceBetweenOldestAndYoungestInStage()

    summary_data = {'stable_size':len(self.stable_list),'bull_cheapest':bull_cheapest,'bear_cheapest':bear_cheapest,
                  'bull_expensive':bull_expensive,'bear_expensive':bear_expensive,'bull_avg_price':bull_avg_price,
                  'bear_avg_price':bear_avg_price,'bull_price_spread':bull_price_spread,'bull_oldest':bull_oldest,
                  'bear_oldest':bear_oldest,'bull_youngest':bull_youngest,'bear_youngest':bear_youngest,
                  'age_oldest':age_oldest,'age_spread':age_spread} 

    #TODO: reconcile with below data
    five_youngest = self.stable_list
    five_youngest.sort(key=lambda rt:rt.getStableBullValue(),reverse=False)
    
    five_most_recent_data = [{'delta':l.getTransitionalDeltaValue(), 'buy_date': l.getAcquisitionDate(),
                              'profit':l.getTransitionalTotalValue(),'duration':l.getDurationInTransition()}
                              for l in five_youngest] 
    stable_data = dict()
    stable_data['summary_data'] = summary_data
    stable_data['content_data'] = five_most_recent_data

    return stable_data 

  def printStableReport(self):
    #TODO: reconcile with above data
    best_bears = self.getAllStableEntriesByBearValue()
    best_bulls = self.getAllStableEntriesByBullValue()    
    bull_p = self.robot.getCurrentBullPrice()
    bear_p = self.robot.getCurrentBearPrice()
    print(" ------------ StableRoundTrips Report at {0} {1} {2}----------".format(self.robot.getCurrentTimestamp(),bull_p,bear_p))
    for n in best_bulls:
      bull = round(n.getStableBullValue(),2)
      bear = round(n.getStableBearValue(),2)
      total = round(n.getStableTotalValue(),2)
      bp = round(n.getBullBuyPrice(),2)
      ep = round(n.getBearBuyPrice(),2)
      cost_basis = round(n.getRoundtripCostBasis())

      print("Bull: {0:04,.2f} ({3:04,.2f}) CB={5}. Bear: {1:,.2f} ({4}). Delta: {2:,.2f} ".format(bull, bear, total,bp,ep,cost_basis))
      print("\n Ratio: {0}".format(n.getStringForRatio()))
    print("\n")
    print(" --------------------------- --------------------------------- --------------------------------- ")




#
#
#
#
class InTransitionRoundTrips():

  def __init__(self,robot):
    self.robot = robot
    self.max_size =self.robot.getMaxNumberOfRoundtrips()
    self.in_transition_list = []

    entries = robot.getAllBullishRoundtrips()
    for entry in entries:
      rt = RoundTrip(robot=self.robot,root_id=entry.getOrderClientIDRoot())
      if rt.isInTransition():
        self.in_transition_list.append(rt)
  
  def __str__(self):
    return "{0}".format('Hello, this is the Transition Roundtrip') 

  def getInTransitionSize(self):
    return len(self.in_transition_list)

  def isFullyLoaded(self):
    return (self.getInTransitionSize() == self.max_size ) #TODO: Externalize me and make me dynamic

  def setInTransitionSize(self,size=5):
    self.max_size = size 

  def isEmpty(self):
    return self.getInTransitionSize() == 0

  def isFull(self):
    return self.getInTransitionSize() == self.max_size

  def getNumberOfBullsInTransition(self):
    in_transition = [ candidate for candidate in self.in_transition_list if candidate.isInBullishTransition()]
    return len(in_transition) 

  def getNumberOfBearsInTransition(self):
    in_transition = [ candidate for candidate in self.in_transition_list if candidate.isInBearishTransition()]
    return len(in_transition) 

  def getTotalNumberInTransition(self):
    return self.getInTransitionSize()

  def getBestCandidateInValue(self): 
    candidates = self.in_transition_list
    candidates.sort(key=lambda rt:rt.getTransitionalDeltaValue(),reverse=True)
    return None if len(candidates) == 0 else candidates[0]

  def getBestCandidateInAge(self): 
    candidates = self.in_transition_list
    candidates.sort(key=lambda rt:rt.getTimeSpentInTransition(),reverse=True)
    return None if len(candidates) == 0 else candidates[0]

  def getBestPerformingBull(self):
    candidates = [ candidate for candidate in self.in_transition_list if candidate.isInBullishTransition()]
    candidates.sort(key=lambda rt:rt.getTransitionalDeltaValue(),reverse=True)
    return None if len(candidates) == 0 else candidates[0]

  def getBestPerformingBear(self):
    candidates = [ candidate for candidate in self.in_transition_list if candidate.isInBearishTransition()]
    candidates.sort(key=lambda rt:rt.getTransitionalDeltaValue(),reverse=True)
    return None if len(candidates) == 0 else candidates[0]

  def getAllInTransitionEntries(self):
    return self.in_transition_list

  def getCashGeneratedAfterSettlement(self):
    all_settled_profits = [ c.getRealizedAndSettled() for c in self.in_transition_list ]
    return sum(all_settled_profits)

  def getInTransitionReport(self):
    best_bear = None if (self.getBestPerformingBear() == None) else self.getBestPerformingBear().getTransitionalDeltaValue()
    best_bull = None if (self.getBestPerformingBull() == None) else self.getBestPerformingBull().getTransitionalDeltaValue()
    summary_data = {'intransition_size':len(self.in_transition_list),'best_bear':best_bear,
                    'best_bull':best_bull,
                    'youngest':(None if self.getBestCandidateInAge() is None else self.getBestCandidateInAge().getTimeSpentInTransition()),
                    'best_value':(None if self.getBestCandidateInValue() is None else self.getBestCandidateInValue().getTransitionalDeltaValue())} 

    five_youngest = self.in_transition_list
    five_youngest.sort(key=lambda rt:rt.getTimeSpentInTransition(),reverse=False)
    
    five_most_recent_data = [{'delta':l.getTransitionalDeltaValue(), 'sell_date': l.getCompletionDate(),
                              'profit':l.getTransitionalTotalValue(),'duration':l.getDurationInTransition()}
                              for l in five_youngest[:5]] 

    in_transition_data = dict()
    in_transition_data['summary_data']=summary_data
    in_transition_data['content_data'] = five_most_recent_data

    return in_transition_data 

  def printInTransitionReport(self):
    best_bears = self.getAllInTransitionEntries()
    best_bulls = self.getAllInTransitionEntries()    
    total_t=0
    print(" --------------------------- InTransitionRoundTrips Report at {0}".format(self.robot.getCurrentTimestamp()))
    for n in best_bulls:
      total =  round(n.getTransitionalTotalValue(),2)
      delta =  round(n.getTransitionalDeltaValue(),2)
      total_t+= delta
      age = n.getDurationInTransition()
      print("Delta:{0}. Age: {1}".format(delta,age))
    print("Total:{0:,.2f}. ".format(total_t))
    print(" --------------------------- --------------------------------- --------------------------------- \n")


#
# This is the encapsulation of the Completed Elements.
#
class CompletedRoundTrips():

  def __init__(self,robot):
    self.robot = robot
    self.completed_list = []
    entries = self.robot.getAllBullishRoundtrips()
    for entry in entries:
      rt = RoundTrip(robot=self.robot,root_id=entry.getOrderClientIDRoot())
      if rt.isCompleted():
        self.completed_list.append(rt)

  def __str__(self):
   return "{0}".format('Hello, this is the Completed Roundtrip') 

  def getAllCompletedEntries(self):
    return self.completed_list

  def getTodayMaxTransactionsSize(self):
    all_results = [c for c in self.completed_list if c.completedToday()]
    if shouldUsePrint():
      print("CompletedRoundTrips: getTodayMaxTransactionsSize: {}".format(len(all_results)))
    return len(all_results)

  def getCompletedSize(self):
    return len(self.completed_list)

  #def hasCompletedToday(self):
  #  return 
  def getAgeOfFirstCompletion(self):
    all_ages = self.completed_list 
    all_ages.sort(key=lambda rt:rt.getAcquisitionDate(),reverse=True)
    return all_ages[0]

  def getAgeOfMostRecentCompletion(self):
    current_timestamp = self.robot.getCurrentTimestamp()
    return current_timestamp

  def getNumberAboveExpectations(self):
    all_results = [c for c in self.completed_list if c.isRoundtripProfitAboveExpectations()]
    return len(all_results)

  def getNumberBelowExpectations(self):
    all_results = [c for c in self.completed_list if c.isRoundTriProfitBelowExpectations()]
    return len(all_results)

  def getNumberOfSuccessful(self):
    all_results = [c for c in self.completed_list if c.isRoundtripProfitPositive()]
    return len(all_results)

  def getNumberOfUnSuccessful(self):
    all_results = [c for c in self.completed_list if c.isRoundtripProfitNegative()]
    return len(all_results)

  def getNumberOfCompleted(self):
    all_successful = self.completed_list
    return len(self.completed_list)

  def getTotalProfitGenerated(self):
    all_profits = [c.getRoundtripRealizedProfit() for c in self.completed_list ]
    return sum(all_profits)

  def getAverageAgeOfCompletion(self):
    all_results = [c.getTimeSpentActive() for c in self.completed_list ]
    return 0 if len(all_results) == 0 else sum(all_results)/len(all_results)

  def getAverageProfitPerCompletion(self):
    if self.getNumberOfCompleted() == 0:
      return 0.0
    return self.getTotalProfitGenerated() / self.getNumberOfCompleted()

  def getCashGeneratedAfterSettlement(self):
    all_settled_profits = [ c.getRealizedAndSettled() for c in self.completed_list ]
    return sum(all_settled_profits)

  def getCompletedReport(self):
    summary_data = {'completed_size':self.getNumberOfCompleted(),'successful':self.getNumberOfSuccessful(),
                    'unsuccessful':self.getNumberOfUnSuccessful(),'average_profit':self.getAverageProfitPerCompletion(),
                    'average_age':self.getAverageAgeOfCompletion()} 

    five_youngest = self.completed_list
    five_youngest.sort(key=lambda rt:rt.getTimeSpentActive(),reverse=False)
    
    five_most_recent_data = [{'buy_date':l.getAcquisitionDate(), 'sell_date': l.getCompletionDate(),
                              'transition_time':l.getTimeSpentInTransition(),'profit':l.getRoundtripRealizedProfit(),\
                              'stable_time':l.getTimeSpentInStable(),'cost_basis':l.getRoundtripCostBasis()}
                              for l in five_youngest] 
    completed_data = dict()
    completed_data['summary_data'] = summary_data
    completed_data['content_data'] = five_most_recent_data

    return completed_data 

  def printCompletionReport(self):
    nc = self.getNumberOfCompleted()
    ns = self.getNumberOfSuccessful()    
    nl = self.getNumberOfUnSuccessful()
    avg = self.getAverageProfitPerCompletion()
    avg_age = self.getAverageAgeOfCompletion()
    print("\n--------------------------- CompletedRoundTrips Report at {0} -------------------------------- ".format(self.robot.getCurrentTimestamp()))
    print("Completions={0}. Successful={1}. Loss={2}. Profit per Compl.={3:,.2f} Average Age={4}".format(nc,\
          ns,nl,avg,avg_age))
    print(" --------------------------- --------------------------------- --------------------------------- ")







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
  version=models.CharField(max_length=10,choices=CHOICES_VERSION_INFORMATION, default='1.0.0')
  creation_date = models.DateTimeField('date created',default=timezone.now)
  modify_date = models.DateTimeField('date modified',default=timezone.now)

  max_hold_time = models.CharField(max_length=10,choices=CHOICES_MAX_HOLD_DAYS, default='5')
  minimum_hold_time = models.CharField(max_length=5,choices=CHOICES_MIN_HOLD_DAYS, default='1')
  hold_time_includes_holiday = models.BooleanField(default=False)
  #If set, do not buy anymore ... but sell
  sell_remaining_before_buy = models.BooleanField(default=False)
  # If set, liquidate holdings as soon as possible.
  liquidate_on_next_opportunity = models.BooleanField(default=False)
  #To be used with client order id generation
  internal_name = models.CharField(max_length=10,default='egghead',blank=True)
  # check system every 60 seconds. Sleep pattern within the robot
  live_data_check_interval = models.CharField(max_length=10,choices=CHOICES_ROBOT_SLEEP_TIME_BETWEEN_TRADES, default='1')
  #Testing, Live, ...etc
  data_source_choice = models.CharField(max_length=10,choices=CHOICES_DATA_SOURCE, default='backtest')

  max_sell_transactions_per_day =models.CharField(max_length=10,choices=CHOICES_MAX_TRANSACTIONS_PER_DAY, default='unlimited')
  ################## Roundtrip concept: Transactions #####################################################
  # We want to recycle StableBox 3 times within a trading week = 3x20 acquisitions, 3x20 sales = 120 transactions.
  # at 2500 * .005 = $12.5 per exit (sale) transaction, we should be at $750 per week.
  # If the size of Stable is 10. We invest $2500 per Roundtrip. Total investment is $2500 each time we are full.
  max_roundtrips = models.CharField(max_length=10,choices=CHOICES_ROUNDTRIPS, default='10')
  cost_basis_per_roundtrip = models.CharField(max_length=10,choices=CHOICES_ROUNDTRIPS_COST_BASIS, default='10')
  profit_target_per_roundtrip = models.CharField(max_length=10,choices=CHOICES_ROUNDTRIPS_PROFIT_TARGETS, default='.05')

  #Ownership Management
  owner = models.ForeignKey(Customer, on_delete=models.PROTECT,blank=True,null=True)
  #Portfolion Management
  portfolio = models.ForeignKey(Portfolio, on_delete=models.PROTECT,blank=True,null=True)
  #Strategy Management
  strategy = models.ForeignKey(EquityStrategy,on_delete=models.PROTECT,blank=True,null=True)
  #Equities Management
  symbols = models.ForeignKey(RobotEquitySymbols,on_delete=models.PROTECT,blank=True,null=True)

  # These variables should change with every new tick.
  #
  current_bull_price= 0
  current_bear_price= 0
  current_timestamp = datetime.now(getTimeZoneInfo())
  execution_engine = None
  last_daily_update = None

  def __str__(self):
        return " {0} {1}".format(self.name, self.pk)

  ##########################################################################
  #     Robot Basic Information Getters ...
  #
  # Switch from Enable to Disable safely
  #
  def toggleEnabled(self):
    self.disconnectSafely() if self.enabled else self.connectSafely()
    self.save()

  def disconnectSafely(self):
    self.enabled = False
    self.recordDisconnectionTransaction()

  def connectSafely(self):
    self.enabled = True
    self.recordConnectionTransaction()

  def isEnabled(self):
    return self.enabled

  def isVisible(self):
    return self.visibility

  def getCurrentBullPrice(self):
        return self.current_bull_price

  def getCurrentBearPrice(self):
        return self.current_bear_price

  def getCurrentTimestamp(self):
        return self.current_timestamp

  def getBullishSymbol(self):
    return self.symbols.bullishSymbol

  def getBearishSymbol(self):
    return self.symbols.bearishSymbol

  def getSymbol(self):
        return self.symbols.symbol

  def getRobotVersion(self):
        return self.version

#
  # Variables below come from the Robot directly
  #
  def getMaxNumberOfRoundtrips(self):
    return int(self.max_roundtrips)

  def getMaximumAssetHoldTime(self):
    return self.max_hold_time

  def getMaxHoldTimeInMinutes(self):
    return float(self.max_hold_time) * 24 * 60

  def getMinimumAssetHoldTime(self):
    return self.minimum_hold_time

  def getMinHoldTimeInMinutes(self):
    return float(self.minimum_hold_time) * 24 * 60

  def getProfitTargetPerRoundtrip(self):
    return float(self.profit_target_per_roundtrip )

  def getBullTransitionProfitTarget(self):
    return self.getInTransitionProfitTarget()

  def getBearTransitionProfitTarget(self):
    return self.getInTransitionProfitTarget()

  def getBullWeightedProfitTargetPerRoundtrip(self):
    return self.getProfitTargetPerRoundtrip() * self.getBullishComposition() * 0.01

  def getBearWeightedProfitTargetPerRoundtrip(self):
    return self.getProfitTargetPerRoundtrip() * self.getBearishComposition() * 0.01

  def getInTransitionProfitTarget(self):
    return self.getProfitTargetPerRoundtrip() * self.getInTransitionProfitTargetRatio()

  def getCompletionProfitTarget(self):
    return self.getProfitTargetPerRoundtrip() * self.getCompletionProfitTargetRatio()

  def shouldRemainingAssetsBeSoldBeforeAnyAcquisition(self):
    return self.sell_remaining_before_buy

  def shouldLiquidateAssetsAtNextAvailableOpportunity(self):
    return self.liquidate_on_next_opportunity

  def getInternalName(self):
    return self.internal_name

  #Production
  def isDataSourceLiveFeed(self):
    return self.data_source_choice == 'live'

  #UAT
  def isDataSourcePaperAccount(self):
    return self.data_source_choice == 'paper'

  #SIT
  def isDataSourceBacktest(self):
    return self.data_source_choice == 'backtest'

  #SIT
  def isDataSourceLocal(self):
    return self.isDataSourceBacktest()

  def getRobotSleepTimeBetweenChecks(self):
    return self.live_data_check_interval

  #Sets the Execution. Clear Any Data that might have been present before
  def setExecutionEngine(self,execution_engine=None,purge_previous=True):
    self.execution_engine = execution_engine
    if purge_previous:
      TradeDataHolder.deleteExecutionEngineEntries(robot=self)

  # #######################################################################################
  #  Robot Symbols functionality is presented here.
  #  Dereferrencing functions implemented at the RobotSymbol level.
  #
  def getSymbolsPairAsPayload(self):
    return self.symbols.getSymbolsPairAsPayload()


  # #######################################################################################
  #  Robot Market Sentiment influences Asset Composition.
  #  Asset Composition depends on two places. Market Activity (Automatic) or Strategy (Manual).
  #  Must figure out how to synchronize both all the time. Via Javascript would be best.
  #  When one side it saved, it should adjust the other side.

  def getSentimentWindow(self):
    return self.getMaximumAssetHoldTime()

  def assetCompositionIsManual(self):
    return False if self.strategy==None else self.strategy.manual_asset_composition_policy

  def assetCompositionIsAutomatic(self):
    return not self.assetCompositionIsManual()

  def getBullishComposition(self):
    if self.assetCompositionIsAutomatic():
      sentiment = EquityAndMarketSentiment.objects.get(pair_robot_id=self.pk)
      bullishRatio = sentiment.getBullishComposition()
    else:
      bullishRatio = self.strategy.getBullishCompositionOnAcquisition()

    return bullishRatio

  def getBearishComposition(self):
    if self.assetCompositionIsAutomatic():
      sentiment = EquityAndMarketSentiment.objects.get(pair_robot_id=self.pk)
      bearishRatio = sentiment.getBearishComposition()
    else:
      bearishRatio = self.strategy.getBearishCompositionOnAcquisition()

    return bearishRatio

  def hasReachedMaxSellTransactionsPerDay(self):
    if shouldUsePrint():
      print("Maximum Number of Sales: {}".format(self.max_sell_transactions_per_day))
    if self.max_sell_transactions_per_day == 'unlimited':
      return False
    completed = self.getCompletedRoundTrips()
    return completed.getTodayMaxTransactionsSize() >= int(self.max_sell_transactions_per_day)

  # #######################################################################################
  #     Market Trading Window  ...
  #  How and where is data added to capture the trading window?
  #  Only question it needs to answer is: Can I trade now?
  #

  def canTradeNow(self,current_time):
    activity_window = RobotActivityWindow.objects.get(pk=self.pk)
    return activity_window.canTradeNow(current_time=current_time)

  # ##########################################################################
  #            Portfolio & Budgets ...
  def updateBudgetAfterPurchase(self,amount=0):
    logger.info("Updating Robot Cash Position following Purchase. {0}".format(amount))
    budget = RobotBudgetManagement.objects.get(pair_robot_id=self.pk)
    return budget.updateBudgetAfterAcquisition(amount=amount)

  def updateBudgetAfterDisposition(self,amount=0):
    logger.info("Updating Robot Cash Position following Disposition. {0}".format(amount))
    budget = RobotBudgetManagement.objects.get(pair_robot_id=self.pk)
    return budget.updateBudgetAfterDisposition(amount=amount)

  def haveEnoughFundsToPurchase(self):
    budget = RobotBudgetManagement.objects.get(pair_robot_id=self.pk)
    return  budget.haveEnoughFundsToPurchase()

  def getCostBasisPerRoundtrip(self):
    budget = RobotBudgetManagement.objects.get(pair_robot_id=self.pk)
    return  budget.getCostBasisPerRoundtrip()


  # ##########################################################################
  #   Events such as CatastrMarket events
  def noCatastrophicEventHappening(self):
    sentiment = EquityAndMarketSentiment.objects.get(pair_robot_id=self.pk)
    return not sentiment.isMarketCrashing()

  # ##########################################################################
  #   Events such as CatastrMarket events
  #

  def noIssuesWithBrokerage(self):
        #TODO: How about day trading rules? We need to keep track, so that we don't break it.
        return True

# ############################################################################################
  #  InfraIsReadyForAssetAcquisition:
  #  Infrastructural Event are event that can't be classified in any of the other event groups.
  #  One of the events could be that we have reached the limit of entries on the Assembly Line.
  def infraIsReadyForAssetAcquisition(self):
        return  True

  # ##########################################################################
  # InfraIsReadyForAssetDisposition:
  # Infrastructural Event are event that can't be classified in any of the other event groups.
  # One could be that we haven't reached the minimum as specified by the Strategy.
  def infraIsReadyForAssetDisposition(self):
        return  True

  # ##########################################################################
  #    EquityStrategy Model Information
  #   These functions get their data from the EquityStrategy Model.
  #
  def isBatchamStrategy(self):
    return self.strategy.isBatchamStrategy()

  def isBabadjouStrategy(self):
    return self.strategy.isBabadjouStrategy()


  # ##########################################################################
  #  Acquisition, Disposition Policies ...
  #
  def acquisitionConditionMet(self):
        return False if self.strategy==None else self.strategy.acquisitionConditionMet(robot=self)

  def dispositionConditionMet(self):
        return False if self.strategy==None else self.strategy.dispositionConditionMet(robot=self)

  def getCompletionProfitTargetRatio(self):
        return 0.5 if self.strategy==None else self.strategy.getCompletionProfitTargetRatio()

  def getInTransitionProfitTargetRatio(self):
        return 0.5 if self.strategy==None else self.strategy.getInTransitionProfitTargetRatio()

  def getBestOrWorstBullInTransitionStrategy(self):
    return True if self.strategy==None else self.strategy.getBestOrWorstBullInTransitionStrategy()

  def getBestOrWorstBearInTransitionStrategy(self):
    return True if self.strategy==None else self.strategy.getBestOrWorstBearInTransitionStrategy()

  def getNumberOfBullsInTransitionComposition(self):
    return 1 if self.strategy==None else self.strategy.getNumberOfBullsInTransitionComposition()

  def getNumberOfBearsInTransitionComposition(self):
    return 1 if self.strategy==None else self.strategy.getNumberOfBearsInTransitionComposition()

  def getTransitionStrategyType(self):
        return None if self.strategy==None else self.strategy.getTransitionStrategyType()

  def getTransitionLoadFactor(self):
        return 0.5 if self.strategy==None else self.strategy.getTransitionLoadFactor()

  def getMinimumEntriesForStrategy(self):
        return 2
  #def getRegressionTime(self):
  #  return 0 if self.strategy==None else self.strategy.getRegressionStartDayInMinutes()

  def getRegressionStartDayInMinutes(self):
    return 0 if self.strategy==None else self.strategy.getRegressionStartDayInMinutes()

  # ##########################################################################
  #            Order Management, Portfolio Protection Strategy
  #
  # TODO: Based on various criteria, determine if I should use:
  #   -Market Order (liquid asset, business hours)
  #   -Limit Order  ( extended trading hours, ... etc.)
  def getAcquisitionOrderType(self):
    return self.strategy.getAcquisitionOrderType()

  def getInTransitionSellOrderType(self):
    return self.strategy.getInTransitionSellOrderType()

  def getCompletionSellOrderType(self):
    return self.strategy.getCompletionSellOrderType()

  def getAssetProtectionStrategy(self):
        return self.strategy.retrieveAssetProtectionStrategy()

 # ################# ASSEMBLY LINE ELEMENTS FUNCTIONS ##############################
  #
  # Returns the various interfaces to the different stages within our application.
  #
  def getStableRoundTrips(self):
    stable_box = StableRoundTrips(robot=self)
    return stable_box

  def getInTransitionRoundTrips(self):
    in_transition = InTransitionRoundTrips(robot=self)
    return in_transition

  def getTransitionalCandidateRoundTrips(self):
    transitional = TransitionalCandidateRoundTrips(robot=self)
    return transitional

  def getCompletionCandidatesRoundTrips(self):
        completion = CompletionCandidateRoundtrips(robot=self)
        return completion

  def getCompletedRoundTrips(self):
    completed = CompletedRoundTrips(robot=self)
    return completed


  # ################# EVENT RECORDING FUNCTIONS ################################################
  #
  # Recording of various events in the system
  #
  def recordTradeData(self):
        EquityTradingData.objects.create(symbol=self.getBullishSymbol(),trade_datetime=self.current_timestamp,volume=0,price=self.getCurrentBullPrice())
        EquityTradingData.objects.create(symbol=self.getBearishSymbol(),trade_datetime=self.current_timestamp,volume=0,price=self.getCurrentBearPrice())
        EquityTradingData.objects.create(symbol=self.getSymbol(),trade_datetime=self.current_timestamp,volume=0,price=self.getCurrentBullPrice())

  def recordDisconnectionTransaction(self):
    log_time = self.getCurrentTimestamp()
    action = 'Disconnect'
    object_type = 'Robot'
    object_id = self.pk
    modified_by = None #TODO: FixME
    comment = 'Disconnecting for no reason '
    StartupStatus.recordTransaction(log_time=log_time,action=action,object_type=object_type,
                                    object_id=object_id, modified_by=modified_by,comment=comment)

  def recordConnectionTransaction(self):
    log_time = self.getCurrentTimestamp()
    action = 'Connect'
    object_type = 'Robot'
    object_id = self.pk
    modified_by = None #TODO: FixME
    comment = 'Connect for no reason '
    StartupStatus.recordTransaction(log_time=log_time,action=action,object_type=object_type,
                                    object_id=object_id, modified_by=modified_by,comment=comment)

  #
  # On regular intervall, the Robot Portfolio needs to be synchronized with the
  #
  def synchronizeBudgetWithBrokerage(self):
    if self.isAlpacaPaperAccount() and self.isAlpacaPortfolioAccount():
      brokerage = AlpacaPaperAccount()
    elif self.isAlpacaLiveAccount():
      brokerage = AlpacaPaperAccount()
    elif self.isLocalAccount() and self.isLocalPortfolioAccount():
      brokerage = LocalAccount()

    self.portfolio.synchronizeBudgetWithBrokerage()

  # ################# USER INTERFACE DATA FUNCTIONS / UI REPORTING DATA ########################
  #
  # Returns Data for the Forms ... to be displaed on the UI
  #
  def getCompletedReport(self):
    return self.getCompletedRoundTrips().getCompletedReport()

  def getInTransitionReport(self):
    return self.getInTransitionRoundTrips().getInTransitionReport()

  def getStableReport(self):
    return self.getStableRoundTrips().getStableReport()

 # ################# ENTRY POINT OF APPLICATION - DAILY MARKET DATA  ################################################
  #
  # This is the entry point from the various external sources to start trading for the Robot.
  #
  def setCurrentValues(self,current_payload):
    try:
      self.current_bull_price = current_payload[self.getBullishSymbol()]
      self.current_bear_price = current_payload[self.getBearishSymbol()]
      self.current_timestamp  = strToDatetime(business_day=current_payload['timestamp'])
    except Exception as e:
      print("The matching Bull and/or Bear symbol are missing from the current values paylod. {0}.".format(e))
      return False
    return True


  #
  #
  #
  def TwentyFourHourUpdate(self):
    #print("24 Hour update TimeStamp: {}".format(self.current_timestamp))
    #round((self.getCurrentTimestamp() - self.getBullBuyDate()).total_seconds()/60,2)

    if self.last_daily_update==None:
      self.portfolio.synchronizeBudgetWithBrokerage()
      self.last_daily_update = self.current_timestamp
    elif round((self.last_daily_update - self.current_timestamp).total_seconds()/60,2) > (24 * 60):
      self.portfolio.synchronizeBudgetWithBrokerage()
      self.last_daily_update = self.current_timestamp  #

    bud_mgmt =   RobotBudgetManagement.objects.get(pk=self.pk)
    bud_mgmt.setInitialDailyBudget(robot=self)

#
  # This is the main entry point to start trading with a Robot.
  # All ETFRobotBackTestExecution() and ETFRobotLiveExecution() enter through this.
  #
  def prepareTrades(self,key=None):
    if not self.isEnabled():
      logger.error("Robot has not yet been enabled. Please enable {0} before starting the trade. Exiting...".format(self.name,key))
      return -1

    logger.info("\n\nRobot'{0}' Data:{1}' launched.".format(self.name,key))

    if key == None:
      logger.error("The key passed doesn't contain any values. Make sure there are values in the Key parameter. ")
      return -1

    if not self.setCurrentValues(current_payload=key):
      return -1

    #Record the actual Share Price into the Data Table.
    self.recordTradeData()

    #Udpdate Records based on Orders execution.
    self.updateOrders()

    #24 Hour Update: Things that need to be updated every 24 hours.
    self.TwentyFourHourUpdate()

 #Invoke Strategies and let them do the rest
    if self.isBabadjouStrategy():
      babadjou = BabadjouStrategy(robot=self)
      babadjou.setupStrategy()
      babadjou.buy()
      babadjou.sell()
    elif self.isBatchamStrategy():
      batcham = BatchamStrategy(robot=self)
      batcham.setupStrategy()
      batcham.buy()
      batcham.sell()
    elif self.isBamendjindaStrategy():
      bamendjinda = BamendjindaStrategy(robot=self)
      bamendjinda.setupStrategy()
      bamendjinda.buy()
      bamendjinda.sell()
    else:
      print("Strategy doesn't have an implementation yet. {0}.".format(strategy))
      raise Exception(" You must provide a valid strategy. ")

    self.updatePortfolioValue()

########################################Roundtrip Report Functions. ##################
  #TODO: Make sure to understand this logic
  def isAssemblyLineEmpty(self):
        return 0 == self.getNumberOfActives()

  def getAllBullishRoundtrips(self):
    ex_eng_id = None if self.execution_engine == None else self.execution_engine.id
    entries = TradeDataHolder.objects.filter(robot_id=self.pk).filter(execution_id=ex_eng_id).filter(buy_order_client_id__endswith='_buy_'+self.getBullishSymbol()).order_by('buy_date')
    return entries

  def getAllBearishRoundtrips(self):
    ex_eng_id = None if self.execution_engine == None else self.execution_engine.id
    entries = TradeDataHolder.objects.filter(robot_id=self.pk).filter(execution_id=ex_eng_id).filter(buy_order_client_id__endswith='_buy_'+self.getBearishSymbol()).order_by('buy_date')
    return entries

  def getTotalBothSidesEntries(self):
    ex_eng_id = None if self.execution_engine == None else self.execution_engine.id
    entries = TradeDataHolder.objects.filter(robot_id=self.pk).filter(execution_id=ex_eng_id).filter(buy_order_client_id__icontains='_buy_').order_by('buy_date')
    return entries

  #TODO: All Active Roundtrips for this Robot and this Execution Engine.
  def getAllActiveRoundtrips(self):
    ex_eng_id = None if self.execution_engine == None else self.execution_engine.id
    entries = TradeDataHolder.objects.filter(robot_id=self.pk).filter(execution_id=ex_eng_id).filter(buy_order_client_id__endswith='_buy_'+self.getBullishSymbol()).filter(sell_order_client_id__isnull=True).order_by('buy_date')
    return entries

  #Returns all, include the ones that have completed. Only includes on side (bear or bulls, not both)
  def getAllSize(self):
        return self.getAllBullishRoundtrips().count()

  #
  # All Roundtrips should be exactly half the total. As the number of bullish and number of bearish must
  # be identical
  #
  def areAllRoundtripsBalanced(self):
        balanced = False
        all_bullish_roundtrips = self.getAllBullishRoundtrips().count()
        all_bearish_roundtrips = self.getAllBearishRoundtrips().count()
        all_roundtrips = self.getTotalBothSidesEntries().count()/2
        if (all_roundtrips == all_bearish_roundtrips) and (all_roundtrips == all_bullish_roundtrips):
          return True
        return False

#TODO: Please fix me. Only returns active (Not yet Completed.)
  def getSize(self):
        return self.getAllActiveRoundtrips().count()

  def isFullOfActiveEntries(self):
        actives = self.getStableRoundTrips().getStableSize() + self.getInTransitionRoundTrips().getInTransitionSize()
        return (actives >= self.max_roundtrips)

  def isFullyLoaded(self):
        return (self.getNumberOfRoundtrips() >= self.getMaxNumberOfRoundtrips())

  def getNumberOfRoundtrips(self):
    if self.areAllRoundtripsBalanced():
      return self.getTotalBothSidesEntries().count()/2
    return -1

  # ################# REPORTING FUNCTIONS #################################################################
  # This is the financial Reporting for Command Line. There is a version that runs on the UI.
  #
  def getAllActiveCosts(self):
    result = dict()
    all_candidates = self.getInTransitionRoundTrips().getAllInTransitionEntries() + \
                     self.getStableRoundTrips().getAllStableEntries()


    cost_basis_list       = [ c.getRoundtripCostBasis(non_digits=False) for c in all_candidates]
    bull_cost_basis_list  = [ c.getBullCostBasis() for c in all_candidates]
    bear_cost_basis_list  = [ c.getBearCostBasis() for c in all_candidates]
    bull_current_value_list  = [ c.getBullCurrentValue() for c in all_candidates]
    bear_current_value_list  = [ c.getBearCurrentValue() for c in all_candidates]
    realized_list         = [ c.getRoundtripRealizedValue(non_digits=False) for c in all_candidates]
    unrealized_list       = [ c.getRoundtripUnrealizedValue(non_digits=False) for c in all_candidates]
    realized_profits_list = [ c.getRoundtripRealizedProfit(non_digits=False) for c in all_candidates]

    result['cost_basis'] = sum(cost_basis_list)
    result['bull_cost_basis'] = sum(bull_cost_basis_list)
    result['bear_cost_basis'] = sum(bear_cost_basis_list)
    result['bull_current_value'] = sum(bull_current_value_list)
    result['bear_current_value'] = sum(bear_current_value_list)
    result['realized'] = sum(realized_list)
    result['unrealized'] = sum(unrealized_list)
    result['realized_profits'] = sum(realized_profits_list)

    return result


  def getAllCosts(self):
    result = dict()
    all_candidates = self.getInTransitionRoundTrips().getAllInTransitionEntries() + \
                     self.getStableRoundTrips().getAllStableEntries() + \
                     self.getCompletedRoundTrips().getAllCompletedEntries()

    cost_basis_list       = [ c.getRoundtripCostBasis(non_digits=False) for c in all_candidates]
    bull_cost_basis_list  = [ c.getBullCostBasis() for c in all_candidates]
    bear_cost_basis_list  = [ c.getBearCostBasis() for c in all_candidates]
    realized_list         = [ c.getRoundtripRealizedValue(non_digits=False)  for c in all_candidates]
    unrealized_list       = [ c.getRoundtripUnrealizedValue(non_digits=False) for c in all_candidates]
    realized_profits_list = [ c.getRoundtripRealizedProfit(non_digits=False) for c in all_candidates]

    result['cost_basis'] = sum(cost_basis_list)
    result['bull_cost_basis'] = sum(bull_cost_basis_list)
    result['bear_cost_basis'] = sum(bear_cost_basis_list)
    result['realized'] =  sum(realized_list)
    result['unrealized'] =  sum(unrealized_list)
    result['realized_profits'] =  sum(realized_profits_list)

    return result

  def updatePortfolioValue(self):
    in_t_size = self.getInTransitionRoundTrips().getInTransitionSize()
    st_size = self.getStableRoundTrips().getStableSize()
    com_size = self.getCompletedRoundTrips().getCompletedSize()
    c_ts = self.current_timestamp
    bull_p = self.current_bull_price
    bear_p = self.current_bear_price
    print("\n\n-----------------Portfolio Summary Information at {0} ---Bull[{1:,.2f}]---Bear[{2:,.2f}]------------------------------".format(c_ts,bull_p,bear_p))
    print("InTransition={0}. Stable={1}. Active[Stable+Transition]={2}. Completed={3}. Total Entries={4}.".format( \
                     in_t_size, st_size,st_size + in_t_size,com_size,self.getAllSize()))

    results = self.getAllCosts()
    cb = round(results['cost_basis'],2)
    bull_cb = 0 if cb==0 else round(100 * results['bull_cost_basis']/results['cost_basis'],2)
    bear_cb = 0 if cb==0 else round(100 * results['bear_cost_basis']/results['cost_basis'],2)
    re = round(results['realized'],2)
    un = round(results['unrealized'],2)
    rp = round(results['realized_profits'],2)
    pv = round(re + un,2)
    profit = round(pv - cb ,2)
    realized_profit = round(rp,2)

    a_results = self.getAllActiveCosts()
    a_cb = round(a_results['cost_basis'],2)
    a_bull_cb = 0 if a_cb==0 else round(100 * a_results['bull_cost_basis']/results['cost_basis'],2)
    a_bear_cb = 0 if a_cb==0 else round(100 * a_results['bear_cost_basis']/results['cost_basis'],2)
    a_re = round(a_results['realized'],2)
    a_un = round(a_results['unrealized'],2)
    a_rp = round(a_results['realized_profits'],2)
    a_pv = round(a_re + a_un,2)
    a_profit = round(a_pv - a_cb ,2)
    a_realized_profit = round(a_rp,2)

    stable_candidates= self.getStableRoundTrips().getAllStableEntries()
    bull_prices = [round(c.getBullBuyPrice(),2) for c in stable_candidates]
    bear_prices = [round(c.getBearBuyPrice(),2) for c in stable_candidates]
    price_spread = [round(c.getAbsoluteBullBearCurrentValueSpread(),2) for c in stable_candidates]

    print("Total :C. Basis={0:,.2f}[Bull/Bear(%)={6:,.2f}/{7:,.2f}]. Profit={5:,.2f} Realized={1:,.2f}. Unrealized={2:,.2f}. Port. Value={3:,.2f}. Net win/loss={4:,.2f}.".format(cb,re,un,pv,profit,realized_profit,bull_cb,bear_cb))
    print("Active:C. Basis={0:,.2f}[Bull/Bear(%)={6:,.2f}/{7:,.2f}]. Profit={5:,.2f} Realized={1:,.2f}. Unrealized={2:,.2f}. Port. Value={3:,.2f}. Net win/loss={4:,.2f}.".format(a_cb,a_re,a_un,a_pv,a_profit,a_realized_profit,a_bull_cb,a_bear_cb))
    print("Bulls       : {} ".format(bull_prices))
    print("Bears       : {} ".format(bear_prices))
    print("Price Spread: {} ".format(price_spread))
    print("                              ---------------------------------------                      ")


# ################# BROKERAGE FUNCTIONS #################################################################
  # These are function that interact with the Brokerage.
  # 0. The first set of functions determines the type of Brokerage (etrade, alpaca, ameritrade, Local)
  #    and the type of data feed (live, paper, local). Not all combinations are valid combinations.
  #    Here are the only valid combinations: (eTrade, Alpaca, Ameritrade) + (live, paper), (local) + (local)
  # 1. Buy Orders: Simulteneous
  # 2. Sell Orders: Sell one side (Transition Sale Order)
  #
  def isLocalBacktestAccount(self):
    return self.portfolio.isLocal() and self.isDataSourceLocal()

  def isAlpacaLiveAccount(self):
    return self.portfolio.isAlpaca() and self.isDataSourceLiveFeed()

  def isAlpacaPaperAccount(self):
    return self.portfolio.isAlpaca() and self.isDataSourcePaperAccount()

  def isEtradeRegularPaperAccount(self):
    return self.portfolio.isETradeRegular() and self.isDataSourcePaperAccount()

  def isEtradeRetirementPaperAccount(self):
    return self.portfolio.isETradeRetirement() and self.isDataSourcePaperAccount()

  def updateOrders(self):
    logger.info("TODO: Brokerage Function. Updating orders from the Brokerage ... ")
    logger.info("TODO: self.updateRobotCashPosition(): Make sure to run this following the update of the Database. ")
    if self.isAlpacaPaperAccount() and self.isAlpacaPortfolioAccount():
      brokerage = AlpacaPaperAccount()
      closed_orders = brokerage.getClosedOrders()
    elif self.isAlpacaLiveAccount():
      print(" hello")

    time.sleep(int(self.getRobotSleepTimeBetweenChecks()))
    return True

  def moveToCompletion(self,candidate):
    if shouldUsePrint():
      print("Moving to Completion (Sell the unrealized). ")
    if candidate.isInTransition():
      candidate.sellTheUnrealized()

  def moveToBearishTransition(self,candidate):
        candidate.sellTheBull()

  def moveToBullishTransition(self,candidate):
        candidate.sellTheBear()

  #
  # A new Roundtrip entry will be created and added to the Assembly line.
  # TODO: This is where we place an Order with the Brokerage
  #
  def addNewRoundtripEntry(self,business_day=None):
    current_time = self.getCurrentTimestamp() if (business_day==None) else timezoneAwareDate(business_day=business_day)
    bullish = dict()
    bearish = dict()
    bullish['symbol'] = self.getBullishSymbol()
    bearish['symbol'] = self.getBearishSymbol()
    bullish['price'] = self.getCurrentBullPrice()
    bearish['price'] = self.getCurrentBearPrice()
    order_ids = TradeDataHolder.generateBuyOrderClientIDs(r_id=self.pk,bear_symbol=self.getBearishSymbol(),bull_symbol=self.getBullishSymbol(),project_root=self.getInternalName())
    bullish['bull_buy_order_client_id']= order_ids['bull_buy_order_client_id']
    bearish['bear_buy_order_client_id']= order_ids['bear_buy_order_client_id']
    bears_ratio = self.getBearishComposition() * .01
    bulls_ratio = self.getBullishComposition() * .01
    if shouldUsePrint():
      print("Composition: {0} {1} {2}".format(bears_ratio,bulls_ratio,self.getCostBasisPerRoundtrip()))
    bullish['qty']= round((self.getCostBasisPerRoundtrip() * bulls_ratio)/bullish['price'])
    bearish['qty']= round((self.getCostBasisPerRoundtrip() * bears_ratio)/bearish['price'])
    bullish['date'] = current_time
    bearish['date'] = current_time
    logger.info("Cost Basis: {}".format(self.getCostBasisPerRoundtrip()))
    logger.info("Order has been sent to the Brokerage. Record Transaction ... \nBullish={}\nBearish={}\n".format(bullish,bearish))
    TradeDataHolder.recordAcquisitionTransaction(robot=self,bullish=bullish,bearish=bearish)

    return order_ids

######################## ###################################
#
# Transactions: Must stay here because I need both the symbol and the robot_id
# This section, we retrieve all the transaction related data
#
  def getRobotExecutionParams(self):
    return 'exect_params'

  def getBullishFilter(self):
    ex_eng_id = None if self.execution_engine == None else self.execution_engine.id
    return TradeDataHolder.objects.filter(robot_id=self.pk).filter(execution_id=ex_eng_id).filter(symbol=self.getBullishSymbol())

  def getBearishFilter(self):
    ex_eng_id = None if self.execution_engine == None else self.execution_engine.id
    return TradeDataHolder.objects.filter(robot_id=self.pk).filter(execution_id=ex_eng_id).filter(symbol=self.getBearishSymbol())

  def getAllBullishPurchaseTransactions(self):
   return self.getBullishFilter().count()

  def getAllBearishPurchaseTransactions(self):
    return self.getBearishFilter().count()

  def getAllPurchaseTransactions(self):
    return self.getAllBullishPurchaseTransactions() + self.getAllBearishPurchaseTransactions()

  def getAllBullishSaleTransactions(self):
    return self.getBullishFilter().filter(sell_order_client_id__isnull=False).count()

  def getAllBearishSaleTransactions(self):
    return self.getBearishFilter().filter(sell_order_client_id__isnull=False).count()

  def getAllSaleTransactions(self):
    return self.getAllBullishSaleTransactions() + self.getAllBearishSaleTransactions()

  def getAllTransactions(self):
    return self.getAllPurchaseTransactions() + self.getAllSaleTransactions()

  def getAllBullishUnrealizedTransactions(self):
    return self.getBullishFilter().filter(sell_order_client_id__isnull=True).count()

  def getAllBearishUnrealizedTransactions(self):
    return self.getBearishFilter().filter(sell_order_client_id__isnull=True).count()

  def getAllUnRealizedTransactions(self):
    return self.getAllBullishUnrealizedTransactions() + self.getAllBullishUnrealizedTransactions()

###################################################
#
# Shares Quantity (How many shares, ...) ...
  def getAllBearishSharesAcquired(self):
    number = self.getBearishFilter().filter(buy_order_client_id__isnull=False).aggregate(total_shares=Sum('quantity'))
    return 0 if number['total_shares'] == None else number['total_shares']

  def getAllBullishSharesAcquired(self):
    number = self.getBullishFilter().filter(buy_order_client_id__isnull=False).aggregate(total_shares=Sum('quantity'))
    return 0 if number['total_shares'] == None else number['total_shares']

  def getAllSharesAcquired(self):
    return self.getAllBearishSharesAcquired() + self.getAllBullishSharesAcquired()

  def getAllBearishSharesSold(self):
    number = self.getBearishFilter().filter(sell_order_client_id__isnull=False).aggregate(total_shares=Sum('quantity'))
    return 0 if number['total_shares'] == None else number['total_shares']

  def getAllBullishSharesSold(self):
    number = self.getBullishFilter().filter(sell_order_client_id__isnull=False).aggregate(total_shares=Sum('quantity'))
    return 0 if number['total_shares'] == None else number['total_shares']

  def getAllSharesSold(self):
    return self.getAllBullishSharesSold() + self.getAllBearishSharesSold()

  def getAllBearishSharesUnrealized(self):
    number = self.getBearishFilter().filter(sell_order_client_id__isnull=True).aggregate(total_shares=Sum('quantity'))
    return 0 if number['total_shares'] == None else number['total_shares']

  def getAllBullishSharesUnrealized(self):
    number = self.getBullishFilter().filter(sell_order_client_id__isnull=True).aggregate(total_shares=Sum('quantity'))
    return 0 if number['total_shares'] == None else number['total_shares']

  def getAllSharesUnrealized(self):
    return self.getAllBearishSharesUnrealized() + self.getAllBullishSharesUnrealized()

######################################################
#
# Financial Value
# Shares Quantity (How many shares, ...) ...
  def getCostOfAllBearishSharesAcquired(self):
    number = self.getBearishFilter().filter(buy_order_client_id__isnull=False).aggregate(total_costs=Sum(F('buy_price') * F('quantity'), output_field=FloatField()))
    return 0 if number['total_costs'] == None else number['total_costs']

  def getCostOfAllBullishSharesAcquired(self):
    number = self.getBullishFilter().filter(buy_order_client_id__isnull=False).aggregate(total_costs=Sum(F('buy_price') * F('quantity'), output_field=FloatField()))
    return 0 if number['total_costs'] == None else number['total_costs']

  def getCostOfAllSharesAcquired(self):
    return self.getCostOfAllBullishSharesAcquired() + self.getCostOfAllBearishSharesAcquired()

  def getProfitOfAllBearishSharesSold(self):
        #TODO: Please add filder .filter(robot_id=self.pk).filter(execution_id=self.execution_engine.id)
    entries = TradeDataHolder.objects.filter().filter(robot_id=self.pk).count()
    return entries

  def getProfitOfAllBullishSharesSold(self):
    entries = TradeDataHolder.objects.filter().filter(robot_id=self.pk).count()
    return entries

  def getProfitOfAllSharesSold(self):
    entries = TradeDataHolder.objects.filter().filter(robot_id=self.pk).count()
    return entries

  def getCostOfAllBearishSharesUnrealized(self, bear_price_per_share):
    number = self.getBearishFilter().filter(buy_order_client_id__isnull=False).aggregate(total_costs=Sum(bear_price_per_share * F('quantity'), output_field=FloatField()))
    return 0 if number['total_costs'] == None else number['total_costs']

  def getCostOfAllBullishSharesUnrealized(self, bull_price_per_share):
    number = self.getBullishFilter().filter(buy_order_client_id__isnull=False).aggregate(total_costs=Sum(bull_price_per_share * F('quantity'), output_field=FloatField()))
    return 0 if number['total_costs'] == None else number['total_costs']

  def getCostOfAllSharesUnrealized(self,bear_price_per_share,bull_price_per_share):
    return self.getCostOfAllBullishSharesUnrealized(bull_price_per_share=bull_price_per_share) + self.getCostOfAllBearishSharesUnrealized(bear_price_per_share=bear_price_per_share)

  def getEntryBasedOnOrderClientID(self,exec_engine_order_client_id):
    entry = TradeDataHolder.getEntryBasedOnOrderClientID(exec_engine_order_client_id=exec_engine_order_client_id)
    return entry

#
  # Serializing the Robot Instance.
  # TODO: Implement it to call other classes serializers
  #
  def getSerializedRobotObject(self):
    entry = [self]
    data_robot = serialize('json', entry, cls=ETFPairsRobotEncoder)

    activity_window = RobotActivityWindow.objects.get(pk=self.pk)
    activity_data = '' if activity_window==None else serialize('json', [activity_window], cls=ETFPairsRobotEncoder)

    sentiment_window = EquityAndMarketSentiment.objects.get(pk=self.pk)
    sentiment_data = '' if sentiment_window==None else serialize('json', [sentiment_window], cls=ETFPairsRobotEncoder)

    budget_window = RobotBudgetManagement.objects.get(pk=self.pk)
    budget_data = '' if budget_window==None else serialize('json', [budget_window], cls=ETFPairsRobotEncoder)

    data_strategy = '' if self.strategy==None else serialize('json', [self.strategy], cls=ETFPairsRobotEncoder)
    data_symbols = '' if self.symbols==None else serialize('json', [self.symbols], cls=ETFPairsRobotEncoder)
    data_portfolio = '' if self.portfolio==None else serialize('json', [self.portfolio], cls=ETFPairsRobotEncoder)
    data = data_robot + data_strategy + data_symbols + data_portfolio + activity_data + sentiment_data
    #print("Serialized: {}".format())
    return data

  def deserializedRobotObject(self):
    entry = [self]
    data_robot = serialize('json', entry, cls=ETFPairsRobotEncoder)
    data_strategy = serialize('json', [self.strategy], cls=ETFPairsRobotEncoder)
    data = data_robot + data_strategy
    return data


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
  execution =   models.ForeignKey('ETFPairRobotExecution',on_delete=models.PROTECT,blank=True,null=True)
 
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
    if not self.symbol or (not self.buy_price)\
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

    #Account for None cases
    execution_engine = None if robot==None else robot.execution_engine
    execution_params = None if robot==None else robot.getRobotExecutionParams()

    #Record a Disposition Purchase transaction with the Execution Engine:
    ETFPairRobotExecutionData.recordDispositionExecution(executor=execution_engine,exec_time=sell_order['sell_date'],
                                   order_client_id=sell_order['sell_order_client_id'],exec_params=execution_params,income=0)

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

    #Account for None cases
    execution_engine = None if robot==None else robot.execution_engine
    execution_params = None if robot==None else robot.getRobotExecutionParams()

    bull_entry=TradeDataHolder.objects.create(robot=robot, symbol=bullish['symbol'], buy_price=bullish['price'],
                             buy_order_client_id=bullish['bull_buy_order_client_id'],buy_date=bullish['date'],
                             quantity=bullish['qty'],execution=execution_engine )

    bear_entry=TradeDataHolder.objects.create(robot=robot, symbol=bearish['symbol'], buy_price=bearish['price'],
                             buy_order_client_id=bearish['bear_buy_order_client_id'],buy_date=bearish['date'],
                             quantity=bearish['qty'],execution=execution_engine)

    #Record the Bull Purchase transaction with the Execution Engine:
    ETFPairRobotExecutionData.recordAcquisitionExecution(executor=execution_engine,exec_time=bullish['date'],
                                   order_client_id=bullish['bull_buy_order_client_id'],exec_params=execution_params,cost=0)

    #Record the Bear Purchase transaction with the Execution Engine:
    ETFPairRobotExecutionData.recordAcquisitionExecution(executor=execution_engine,exec_time=bearish['date'],
                                   order_client_id=bearish['bear_buy_order_client_id'],exec_params=execution_params,cost=0)

    robot_id = None if robot==None else robot.id
    exec_engine_id = None if (execution_engine==None) or (robot.execution_engine==None) else robot.execution_engine.id
    bull_info =bull_entry.getBasicBuyInformation()
    bear_info = bear_entry.getBasicBuyInformation()
    if shouldUsePrint():
      print("\nNew Entry added: Bull={0}. Bear={1}. Robot={2} Exec_Engine={3} ".format(bull_info,bear_info,robot_id,exec_engine_id,))


  @staticmethod
  def deleteExecutionEngineEntries(robot):
        TradeDataHolder.objects.filter(robot=robot).filter(execution=robot.execution_engine).delete()

  @staticmethod
  def generateInTransitionRootOrderClientID(project_root,bulls_count,bears_count,r_id=None):
    project_root = project_root
    current_time = datetime.now(getTimeZoneInfo())
    root_order_client_id = current_time.strftime("{0}_{1}_{2}_{3}_%Y%m%d-%H-%M-%S.%f".format(project_root,r_id,bulls_count,bears_count))
    return root_order_client_id

  @staticmethod
  def generateRootOrderClientId(project_root,r_id=None):
    project_root = project_root
    current_time = datetime.now(getTimeZoneInfo())
    root_order_client_id = current_time.strftime("{0}_{1}_%Y%m%d-%H-%M-%S.%f".format(project_root,r_id))
    return root_order_client_id

  @staticmethod
  def generateBuyOrderClientIDs(project_root,bull_symbol,bear_symbol,r_id=None):
    root_order_client_id = TradeDataHolder.generateRootOrderClientId(project_root=project_root,r_id=r_id)
    order_ids = dict()
    order_ids['bull_buy_order_client_id'] = root_order_client_id + "_buy_" + bull_symbol
    order_ids['bear_buy_order_client_id'] = root_order_client_id + "_buy_" + bear_symbol
    return order_ids

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

#
# This serializer is used to serialize entries for the Robot.
#   Customer
class ETFPairsRobotEncoder(DjangoJSONEncoder):
  def default(self, obj):
    if isinstance(obj, ETFAndReversePairRobot) or isinstance(obj,Portfolio):
      return str(obj)
    elif isinstance(obj, EquityStrategy) or isinstance(obj,RobotEquitySymbols):
      return str(obj)
    elif isinstance(obj,RobotActivityWindow) or isinstance(obj,EquityAndMarketSentiment):
      return str(obj)
    elif isinstance(obj,RobotBudgetManagement):
      return str(obj)
    return super().default(obj)




   