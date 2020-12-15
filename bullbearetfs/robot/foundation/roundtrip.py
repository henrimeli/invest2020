import logging
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, shouldUsePrint, fixupMyDateTime, timezoneAwareDate,strToDatetime

"""
  This Module represents a class that encapsulated the concept of a Bull and a Bear bought at the same time.
  A Roundtrip is an abstraction of the concept of a Bull and a Bear entry
  Acquisition of Market assets is done via Roundtrips.
  Each Roundtrip consists of 2 assets. One Bear and One Bull.
  At Acquisition time, the Bear and the Bull have the same monetar.
  Through its lifetime, the Roundtrip goes through stages.
  1. Stable Stage: A pair was just acquired and its combined value is close to zero, regardless of market conditions
  2. Transition Stage: One side of the Pair has been sold. As the market moves, the value of the other side moves.
  The goal is to wait until an asset in transition reaches the optimal value, so it can be moved to Completion phase
  3. Completion Stage: The completion phase is when the other side of the asset is sold for maximum profit.
  The RounTrip Class: contains functions to drive the processes described above. 

  This module has only one class: RoundTrip class.
  This class has a very large number of methods organized as follow:

"""

logger = logging.getLogger(__name__)

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
  
  def getBullPrint1Data(self):
    data = "{0:5}{1:3} {2:6}".format(self.getBullBuyPrice(),self.getBullQuantity(),round(self.getBullCostBasis(),2))
    return data

  def getBearPrint1Data(self):
    data = "{0:5}{1:3} {2:6}".format(self.getBearBuyPrice(),self.getBearQuantity(),round(self.getBearCostBasis(),2))
    return data

  def getBullPrint2Data(self):
    data = "{0:5} {1:6} {2:6}".format(round(self.getBullBuyPrice(),2),round(self.getBullCostBasis(),2),round(self.getStableBullValue(),2))
    return data

  def getBearPrint2Data(self):
    data = "{0:5} {1:6} {2:6}".format(round(self.getBearBuyPrice(),2),round(self.getBearCostBasis(),2),round(self.getStableBearValue(),2))
    return data


  def getDetailedInformation(self,bull_info='',bear_info=''):
      name_id=self.getRootOrderClientIDNoInternal()
      bull="\nStable: Bull:{0} {1} {2} {3} {4} {5}".format(self.getBullSymbol(),self.getBullQuantity(),self.getBullBuyPrice(),self.getBullBuyDate(),name_id,bull_info)
      bear="\n        Bear:{0} {1} {2} {3} {4} {5}".format(self.getBearSymbol(),self.getBearQuantity(),self.getBearBuyPrice(),self.getBearBuyDate(),name_id,bear_info) 
      return bull+bear
##########################################################################################
#
#  Print Methods.
#

##########################################################################################
#
#  Reports Data Methods
#

  # Return data without sale data.
  def getBasicReportData1(self):
    bull_data = dict()
    bear_data = dict()
    bull_data['buy_price']=self.getBullBuyPrice()
    bull_data['symbol']=self.getBullSymbol()
    bull_data['quantity']=self.getBullBuyPrice()
    bull_data['buy_date']=self.getBullSymbol()

    bear_data['buy_price']=self.getBearBuyPrice()
    bear_data['symbol']=self.getBearSymbol()
    bear_data['quantity']=self.getBearBuyPrice()
    bear_data['buy_date']=self.getBearSymbol()

    data = dict()
    data['bull_data'] = bull_data
    data['bear_data'] = bear_data
    data['root_client_order_id'] = self.getRootOrderClientIDNoInternal()

    return data 

  def getBasicReportData2(self):
    result = self.getBasicReportData1()
    #TODO: Read Basic Data1 and append Sell Data.
    pass 


##########################################################################################
#
#  Getters and Setters Methods.
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

  def getBullQuantity(self):
    return self.getTheBull().quantity

  def getBearQuantity(self):
    return self.getTheBear().quantity

  def getBullCurrentPrice(self):
    return self.current_bull_price

  def getBearCurrentPrice(self):
    return self.current_bear_price

  def getCurrentTimestamp(self):
    return self.current_timestamp

  def getTheBull(self):
    return self.robot.getTheBull(buy_order_client_id=self.getBullBuyOrderClientID())

  def getTheBear(self):
    return self.robot.getTheBear(buy_order_client_id=self.getBearBuyOrderClientID())
    #return TradeDataHolder.objects.get(buy_order_client_id=self.getBearBuyOrderClientID())    

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

  # 
  def getRoundtripDataRatio(self):
    data = dict()
    data['bull_ratio_cost_basis'] = self.getCostBasisBullRatio()
    data['bear_ratio_cost_basis'] = self.getCostBasisBearRatio()
    data['bull_ratio_current_val'] = self.getCurrentValueBasedBullRatio()
    data['bear_ratio_current_val'] = self.getCurrentValueBasedBearRatio()
    data['bull_ratio_delta'] = self.getBullCostBasisRatioDelta()
    data['bear_ratio_delta'] = self.getBearCostBasisRatioDelta()

    return data

###########################################################################################
#
#  Validation and Final Stages Check (Stable, Transition, Completed)
#
  #Ensure there is exactly 2 entries in the table with the same order_client_ID_Root
  def hasExactlyTwoEntries(self):
    entries=self.robot.hasExactlyTwoEntries(root_id=self.getRootOrderClientID())
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
    elif self.isInBearishTransition():
      return "Bearish"
    return "Invalid"

  ########## Two functions below are only used for Babadjou Strategy #############
  def isInBullishWinningTransition(self,transition_id):
    return self.isInBullishTransition() and (self.getWinningOrderClientIDRoot()==transition_id)

  def isInBearishWinningTransition(self,transition_id):
    return self.isInBearishTransition() and (self.getWinningOrderClientIDRoot()==transition_id)


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

  #Calculates what has been sold either way and at any stage. getCompletionCandidatesData
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
    self.robot.recordDispositionTransaction(order=bear_sale_order,transition_root_id=transition_root_id)
    #TradeDataHolder.recordDispositionTransaction(robot=self.robot,order=bear_sale_order,transition_root_id=transition_root_id)
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
    self.robot.recordDispositionTransaction(order=bull_sale_order,transition_root_id=transition_root_id)
    #TradeDataHolder.recordDispositionTransaction(robot=self.robot,order=bull_sale_order,transition_root_id=transition_root_id)

  
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
