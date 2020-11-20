from datetime import datetime, time
import logging, unittest
import sys,json
from django.utils import timezone
from django.test import TestCase

# Import Models, Functions
#from bullbearetfs.models import strToDatetime, getTimeZoneInfo, InvalidTradeDataHolderException
#from bullbearetfs.models import ETFAndReversePairRobot, TradeDataHolder, RoundTrip

# Import Models
from bullbearetfs.utilities.core import getTimeZoneInfo, shouldUsePrint, strToDatetime
from bullbearetfs.models import TradeDataHolder, ETFAndReversePairRobot, RoundTrip
#from bullbearetfs.utilities.core  import  getTimeZoneInfo,shouldUsePrint
from bullbearetfs.utilities.errors  import   InvalidTradeDataHolderException
from bullbearetfs.robot.models import RobotEquitySymbols ,Portfolio, RobotBudgetManagement, EquityAndMarketSentiment
from bullbearetfs.executionengine.models import ETFPairRobotExecution


logger = logging.getLogger(__name__)

#
# Dummy function needed to force rebuild on change.
#
def test_roundtrip_dummy(request):
  pass

##############################################################################################
# RoundTrip Interface TestCases
#
# Tests the functionality around the Roundtrip (Interface) Class.
# Roundtrip is not a model class. It is an interface to access TradeDataHolder Class instances
# check their states and perform various manipulations. It is a more sophisticated wrapper of the 
# TradeDataHolder class
# RoundTrip is used within the ETFAndReversePairRobot class and understand everything about the internals of
# TradeDataHolder class and provides functions to calculate values, represent the states of Objects.
# Functionality in the RoundTrip has been grouped in the following areas:
# -Basic functions: Similar to getters and Setters in OO Programming. Retrieves the basic information of the class 
#                   such as symbol, price, dates, order_client_id,...
#
# -Composition and Ratios: Focuses on the composition of each side. What percentage is the Bull? What Percentage is the Bear?
#  If we sell all Bull/or Bear, how far should the Bear/Bull go to get us into trouble?
# 
# -ClientOrderID manipulation: Information needed to keep each RoundTrip Specific and UNIQUE 
#
# -Transitional Stages(states): isStable, isInBullishTransition, isInBearishTransition, isComplete, isActive represent
#       the transitional stages/states of a RoundTrip Object. 
#
# -Duration and Age: Focuses on the age of an asset as well as its duration in a particular stage.
#
# -Financial (Absolute): Combined Costs/Realized, Unrealized: Financial aspect of the Roundtrip.
#
# -Profitability: Financial Exit criterias , Deltas and differences as the stock price moves up and down.
#
# -Performance Statistics: How was/is the performance of a Roundtrip based on benchmarks?
#
# -Time & Price proximity: How close are we to hitting a given price? Time difference in acquisition.
#
# -Shares Quantity via the TradeHolder Class:
#
# -Data Preparation for various Reports:
#
# -Risk Exposure after divesting one side. To be implemented as version 2.0 . Tolerance zones, Tolerance Factors
# Each Test of the Roundtrip should have sections that focus on each of the areas above to ensure full coverage
# of the functionalities.
##############################################################################################################
# Tests the functionality around:
#  Unit Test Organization. Most unittests will be organized in the following classes.
#    A Test Class for the empty set and validations to ensure proper returns, when there is no data.
#    A Test Class with up to 5 Data entries to make sure the functions are called and respond properly.
#    A Test Class with a large number of data (20-50 maybe)
#    A Test Class with combined Robots to ensure that application can function with various Robots.
#    Optionally a Test Class with Risk, Performance, ... etc.
#    
#    RoundtripBasicOneBuyTestCase : Create a Robot and execute a single Buy Operation
#    Status: Complete
#
#    RoundtripThreeEntriesMovingDatesTestCase:  Create a Robot and add 1 entry, then move the 'currenttime' several times
#                                     just like a typical day in the Market would look like. 
#    Status: Complete
#
#    RoundtripFiveEntriesAddedTestCase: Uses Conditional to determin purchase decision. INCOMPLETE
#    Status: Complete
#
#    RoundtripWithOneBuyOneSaleTestCase: 
#    Status: Complete 
#
#    RoundTripWithRiskExposureCalculationTestCase: INCOMPLETE
#    Roundtrip15RobotsWithLotsofDataTestCase: INCOMPLETE
#        Number of Test Classes Planned: 6
#        Total Number of Test Functions: many
#        Number of remaining Classes: 2
#  
#####################################################################################################
#
# One Simple Roundtrip . Validate that all basic functions can be reached and executed with correct results.
#
#@unittest.skip("Taking a break now")
class RoundtripBasicOneBuyTestCase(TestCase):
  base_name = 'testme'
  description = 'description'
  max_roundtrips = 20
  etf = 'QQQ'
  bullish = 'TQQQ'
  bearish = 'SQQQ'
  cost_basis_per_roundtrip = 1500
  initial_budget = 100000
  profit_basis_per_roundtrip = 100
  bull_prices=[123.32,124.35,124.45]
  bear_prices=[28.95,28.5,28.00]
  current_times=['2020-08-03 04:05:00-04:00','2020-08-03 09:05:00-04:00','2020-08-03 06:05:00-04:00']
  internal_name='bamboutos'

  @classmethod 
  def setUpTestData(self):
    nasdaq=RobotEquitySymbols.objects.create(name='Nasdaq',symbol='QQQ',bullishSymbol=self.bullish,bearishSymbol=self.bearish)
    robot1=ETFAndReversePairRobot.objects.create(name=self.base_name,description=self.description,
            portfolio=None,strategy=None,symbols=nasdaq,enabled=True,owner=None,visibility=True,
            version='1.0.0', max_hold_time='14',minimum_hold_time='1',hold_time_includes_holiday=True,
            sell_remaining_before_buy=False,liquidate_on_next_opportunity=False,internal_name=self.internal_name,
            max_roundtrips=self.max_roundtrips,cost_basis_per_roundtrip=self.cost_basis_per_roundtrip,
            profit_target_per_roundtrip=self.profit_basis_per_roundtrip)    
    self.robot_0_id =robot1.pk
    sentiment_0 = EquityAndMarketSentiment.objects.create(pair_robot=robot1,influences_acquisition=True,circuit_breaker=False,
                                                          sentiment_feed='Automatic')
 
    self.s0_id = sentiment_0.pk
    budget_management = RobotBudgetManagement.objects.create(pair_robot=robot1,use_percentage_or_fixed_value='Number',
        max_budget_per_purchase_number='1500')


  def getTradeInformation(self,index):
    information = dict()
    information[self.bullish]=self.bull_prices[index]
    information[self.bearish]=self.bear_prices[index] 
    information['timestamp'] = self.current_times[index]
    return information 

  #@unittest.skip("Taking a break now")
  def testRoundtripBasicRobot(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(len(entries),1)
    rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot())
    self.assertEqual(rt.getBullSymbol(),self.bullish) 
    self.assertEqual(rt.getBearSymbol(),self.bearish)
    self.assertEqual(rt.getBullBuyPrice(),self.bull_prices[0])
    self.assertEqual(rt.getBearBuyPrice(),self.bear_prices[0])
    self.assertEqual(rt.getBullSellPrice(),None)
    self.assertEqual(rt.getBearSellPrice(),None)
    self.assertEqual(rt.getBullSellDate(),None)
    self.assertEqual(rt.getBearSellDate(),None)
    self.assertEqual(rt.getBullQuantity(),6)
    self.assertEqual(rt.getBearQuantity(),26)
    self.assertEqual(rt.getBullCurrentPrice(),123.32) 
    self.assertEqual(rt.getBearCurrentPrice(),28.95) 
    self.assertEqual( type(rt.getTheBull()),TradeDataHolder)
    self.assertEqual( type(rt.getTheBear()),TradeDataHolder) 
    self.assertEqual(rt.getCurrentTimestamp(),strToDatetime(self.current_times[0]) )

  #@unittest.skip("Taking a break now")
  def testBullBearCompositionAndRatios(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(len(entries),1)
    rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot())
    #Ratios between Bulls and Bears
    self.assertTrue(48<rt.getCostBasisBullRatio()<51) 
    self.assertTrue(48<rt.getCostBasisBearRatio()<51)
    self.assertTrue(48<rt.getCurrentValueBasedBullRatio()<51) 
    self.assertTrue(48<rt.getCurrentValueBasedBearRatio()<51)  
    self.assertEqual(rt.getBullCostBasisRatioDelta(),0) 
    self.assertEqual(rt.getBearCostBasisRatioDelta(),0) 


  #@unittest.skip("Taking a break now")
  def testClientOrderIDsStagesRobot(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(len(entries),1)
    rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot())
    self.assertEqual(rt.getRootOrderClientID().split('_')[0],self.internal_name) 
    self.assertEqual(int(rt.getRootOrderClientID().split('_')[1]),robot_0.pk) 
    self.assertEqual(rt.getBullBuyOrderClientID().split('_')[0],self.internal_name) 
    self.assertEqual(int(rt.getBullBuyOrderClientID().split('_')[1]),robot_0.pk) 
    self.assertEqual(rt.getBullBuyOrderClientID().split('_')[3],'buy') 
    self.assertEqual(rt.getBullBuyOrderClientID().split('_')[4],self.bullish) 
    self.assertEqual(rt.getBearBuyOrderClientID().split('_')[0],self.internal_name) 
    self.assertEqual(int(rt.getBearBuyOrderClientID().split('_')[1]),robot_0.pk) 
    self.assertEqual(rt.getBearBuyOrderClientID().split('_')[3],'buy') 
    self.assertEqual(rt.getBearBuyOrderClientID().split('_')[4],self.bearish) 
    self.assertEqual(rt.getBullSellOrderClientID().split('_')[0],self.internal_name) 
    self.assertEqual(int(rt.getBullSellOrderClientID().split('_')[1]),robot_0.pk) 
    self.assertEqual(rt.getBullSellOrderClientID().split('_')[3],'sell') 
    self.assertEqual(rt.getBullSellOrderClientID().split('_')[4],self.bullish) 
    self.assertEqual(rt.getBearSellOrderClientID().split('_')[0],self.internal_name) 
    self.assertEqual(int(rt.getBearSellOrderClientID().split('_')[1]),robot_0.pk) 
    self.assertEqual(rt.getBearSellOrderClientID().split('_')[3],'sell') 
    self.assertEqual(rt.getBearSellOrderClientID().split('_')[4],self.bearish) 

  #@unittest.skip("Taking a break now")
  def testValidationAndTransitionalStages(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(len(entries),1)
    rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot())
    #Stage Completion Functions.
    self.assertEqual(rt.hasExactlyTwoEntries(),True) 
    self.assertEqual(rt.isValid(),True) 
    self.assertEqual(rt.isStable(),True) 
    self.assertEqual(rt.isInBullishTransition(),False) 
    self.assertEqual(rt.isInTransition(),False) 
    self.assertEqual(rt.isActive(),True) 
    self.assertEqual(rt.isCompleted(),False) 
    self.assertEqual(rt.getIsBullishOrBearishTransition(),"Invalid") 
    self.assertEqual(rt.isInBearishTransition(),False) 

  #unittest.skip("These functions shouldn't be here.")
  def testTransitionalFilteringRobot(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(len(entries),1)
    rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot())
    self.assertEqual(rt.isBullTransitionalCandidate(),False) 
    self.assertEqual(rt.isBearTransitionalCandidate(),False) 
    self.assertEqual(rt.isCompletionCandidate(),False) 

  #@unittest.skip("Taking a break now")
  def testTimeAndAgeAndDurationRobot(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(len(entries),1)
    rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot())  
    ###TIME Functions
    self.assertEqual(rt.getAcquisitionDate(),strToDatetime(self.current_times[0]))
    self.assertEqual(rt.getBullBuyDate(),strToDatetime(self.current_times[0]))
    self.assertEqual(rt.getBearBuyDate(),strToDatetime(self.current_times[0]))
    self.assertEqual(rt.getTimeSincePurchase(),0.0)
    self.assertEqual(rt.getTimeSinceCompletion(),None)
    self.assertEqual(rt.getInStableDate(),strToDatetime(self.current_times[0])) 
    self.assertEqual(rt.getInTransitionDate(),None)
    self.assertEqual(rt.getCompletionDate(),None)
    self.assertEqual(rt.getTimeSpentInStable(),None)  
    self.assertEqual(rt.getDurationInStable(),0.0)
    self.assertEqual(rt.getTimeSpentInTransition(),None)
    self.assertEqual(rt.getTimeSpentActive(),None)
    self.assertEqual(rt.getDurationInTransition(),None)  
    self.assertEqual(rt.getRoundtripAge(),None)
    self.assertEqual(rt.getDurationSinceBullSold(),None)
    self.assertEqual(rt.getDurationSinceBearSold(),None) 
    self.assertEqual(rt.completedToday(),None)
    self.assertEqual(rt.completedLast24Hours(),None) 

  # Regression Functions helps understand how our exit criteria changes as we get close to the
  # deadline dates that we set for ourselves. 
  # The deadline is purely arbitrary, we want to make sure the tool is available, in case we need to use it
  # we want to make sure it has been tested and works as expected.
  #@unittest.skip("Taking a break now")
  def testBasicAgeDurationRegressionFunctions(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(len(entries),1)
    rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot())  
    self.assertEqual(rt.isPastMinimumHoldTime(),False) 
    self.assertEqual(rt.isPastMaximumHoldTime(),False) 
    self.assertEqual(rt.isAvailableForTrading(),False) 
    self.assertEqual(rt.isInRegression(),False)     
    self.assertEqual(rt.isInRegressionLevelYellow(),False)    
    self.assertEqual(rt.isInRegressionLevelOrange(),False)   
    self.assertEqual(rt.isInRegressionLevelRed(),False)    

  #Spread represents the difference between two types of prices.
  #Generally between short position and long position in the Market.
  #@unittest.skip("Taking a break now")
  def testSpreadAndRiskFunctions(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(len(entries),1)
    rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot())  
    self.assertEqual(rt.getBullBearCurrentValueSpread(),0.0)    
    self.assertEqual(round(rt.getBullBearCostBasisSpread(),2),12.780)    
    self.assertEqual(rt.getBullPriceSpread(average=rt.getBullBuyPrice()),0) 
    self.assertEqual(rt.getBearPriceSpread(average=rt.getBearBuyPrice()),0) 


  #@unittest.skip("Taking a break now")
  def testCombinedCostsAndValueAtVariousStages(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 

    self.assertEqual(robot_0.getBearishComposition(),50) 
    self.assertEqual(robot_0.getBullishComposition(),50) 
    self.assertEqual(robot_0.getCostBasisPerRoundtrip(),1500) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(len(entries),1)
    rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot()) 
    self.assertEqual(round(rt.getBullCostBasis(),2),739.92) 
    self.assertEqual(round(rt.getBearCostBasis(),2),752.70)
    self.assertEqual(round(rt.getBullCurrentValue(),2),739.92) 
    self.assertEqual(round(rt.getBearCurrentValue(),2),752.70)
    self.assertEqual(round(rt.getRoundtripCostBasis(),2),1492.62)  
    self.assertEqual(round(rt.getBullBearCostBasisDelta(),2),12.78)
    self.assertEqual(round(rt.getBullBearCurrentValueDelta(),2),12.78)
    self.assertEqual(rt.getBullRealizedValue(),None) 
    self.assertEqual(rt.getBearRealizedValue(),None)
    self.assertEqual(rt.getTransitionalRealized(),None) 
    self.assertEqual(rt.getRoundtripRealizedValue(),None)
    self.assertEqual(rt.getRoundtripUnrealizedValue(),1492.62) 
    self.assertEqual(rt.getTransitionalUnRealized(),None) 
    self.assertEqual(rt.getRoundtripInTransitionRealizedProfit(),None)
    self.assertEqual(rt.getRoundtripRealizedProfit(),None)  
    self.assertEqual(rt.getRealizedAndSettled(),None)
    self.assertEqual(rt.getRealizedAndSettled(),None)

  #@unittest.skip("Taking a break now")
  def testProfitabilityRobot(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(len(entries),1)
    rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot()) 
    self.assertEqual(round(rt.getStableBullValue(),2),0.0) 
    self.assertEqual(round(rt.getStableBearValue(),2),0.0) 
    self.assertEqual(round(rt.getStableTotalValue(),2),0.0) 
    self.assertEqual(rt.getTransitionalDeltaValue(),None) 
    self.assertEqual(rt.getTransitionalTotalValue(),None) 
    self.assertEqual(rt.getRoundtripRealizedProfit(),None) 

  #@unittest.skip("Taking a break now")
  def testPerformanceStatistics(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(len(entries),1)
    rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot()) 
    self.assertEqual(rt.isRoundtripProfitNegative(),None) 
    self.assertEqual(rt.isRoundtripProfitPositive(),None) 
    self.assertEqual(rt.isRoundtripProfitAboveExpectations(),None) 
    self.assertEqual(rt.isRoundtriProfitBelowExpectations(),None)  
    self.assertEqual(rt.getProfitPercentage(),None) 
    self.assertEqual(rt.getAnnualizedProfitPercentage(),None) 
  

  #@unittest.skip("Taking a break now")
  def testTimeAndPriceProximityRobot(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(len(entries),1)
    rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot()) 
    self.assertEqual(rt.isBearWithinSharePriceByNumber(number=1),True) 
    self.assertEqual(rt.isBullWithinSharePriceByNumber(number=1),True) 
    self.assertEqual(rt.isBearWithinCostBasisByTotalProfit(),True) 
    self.assertEqual(rt.isBullWithinCostBasisByTotalProfit(),True) 
    self.assertEqual(rt.isBearWithinSharePriceByPercentage(percentage=1),True) 
    self.assertEqual(rt.isBullWithinSharePriceByPercentage(percentage=1),True) 
    self.assertEqual(rt.isWithinTimeRangeByNumber(),True) 

  # Validate number of Transactions 
  def testTransactions1(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(robot_0.getAllBullishPurchaseTransactions(),1)  
    self.assertEqual(robot_0.getAllBearishPurchaseTransactions(),1)      
    self.assertEqual(robot_0.getAllPurchaseTransactions(),2)  
    self.assertEqual(robot_0.getAllBullishSaleTransactions(),0)  
    self.assertEqual(robot_0.getAllBearishSaleTransactions(),0)
    self.assertEqual(robot_0.getAllSaleTransactions(),0)  
    self.assertEqual(robot_0.getAllBullishUnrealizedTransactions(),1)
    self.assertEqual(robot_0.getAllBearishUnrealizedTransactions(),1) 
    self.assertEqual(robot_0.getAllUnRealizedTransactions(),2)
    self.assertEqual(robot_0.getAllTransactions(),2)  

  # Validate Share Quantity Operations 
  def testShareQuantityOnRobot(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(robot_0.getAllBullishSharesAcquired(),6)
    self.assertEqual(robot_0.getAllBearishSharesAcquired(),26)
    self.assertEqual(robot_0.getAllSharesAcquired(),32)
    self.assertEqual(robot_0.getAllBullishSharesSold(),0)
    self.assertEqual(robot_0.getAllBearishSharesSold(),0)
    self.assertEqual(robot_0.getAllSharesSold(),0)
    self.assertEqual(robot_0.getAllBullishSharesUnrealized(),6)
    self.assertEqual(robot_0.getAllBearishSharesUnrealized(),26) 
    self.assertEqual(robot_0.getAllSharesUnrealized(),32)


#####################################################################################################
#
# One Roundtrip with moving dates (current time) . 
# Validate that all basic functions can be reached and executed with correct results.
#
#@unittest.skip("Taking a break now")
class RoundtripThreeEntriesMovingDatesTestCase(TestCase):
  base_name = 'testme'
  description = 'description'
  max_roundtrips = 20
  etf = 'QQQ'
  bullish = 'TQQQ'
  bearish = 'SQQQ'
  cost_basis_per_roundtrip = 1500
  initial_budget = 100000
  profit_basis_per_roundtrip = 100
  bull_prices=[123.32,124.35,124.45]
  bear_prices=[28.95,28.5,28.00]
  current_times=['2020-08-03 04:05:00-04:00','2020-08-03 05:05:00-04:00','2020-08-03 06:05:00-04:00']
  internal_name='bamboutos'

  @classmethod 
  def setUpTestData(self):
    nasdaq=RobotEquitySymbols.objects.create(name='Nasdaq',symbol='QQQ',bullishSymbol=self.bullish,bearishSymbol=self.bearish)

    robot1=ETFAndReversePairRobot.objects.create(name=self.base_name,description=self.description,
            portfolio=None,strategy=None,symbols=nasdaq,enabled=True,owner=None,visibility=True,
            version='1.0.0', max_hold_time='14',minimum_hold_time='1',hold_time_includes_holiday=True,
            sell_remaining_before_buy=False,liquidate_on_next_opportunity=False,internal_name=self.internal_name,
            max_roundtrips=self.max_roundtrips,cost_basis_per_roundtrip=self.cost_basis_per_roundtrip,
            profit_target_per_roundtrip=self.profit_basis_per_roundtrip)
    
    self.robot_0_id =robot1.pk

    sentiment_0 = EquityAndMarketSentiment.objects.create(pair_robot=robot1,influences_acquisition=True,circuit_breaker=False,
                                                          sentiment_feed='Automatic')
 
    self.s0_id = sentiment_0.pk
    budget_management = RobotBudgetManagement.objects.create(pair_robot=robot1,use_percentage_or_fixed_value='Number',
        max_budget_per_purchase_number='1500')


  def getTradeInformation(self,index):
    information = dict()
    information[self.bullish]=self.bull_prices[index]
    information[self.bearish]=self.bear_prices[index] 
    information['timestamp'] = self.current_times[index]
    return information 

  #@unittest.skip("Taking a break now")
  def testRoundtripBasicRobot(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    index = 0
    for n in self.current_times:
      payload = self.getTradeInformation(index)
      self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
      self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
      self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
      self.assertEqual(robot_0.getSymbol(),self.etf) 
      self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
      self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 
      self.assertEqual(robot_0.getCurrentTimestamp(),strToDatetime(self.current_times[index]))
      self.assertEqual(robot_0.getBearishComposition(),50) 
      self.assertEqual(robot_0.getBullishComposition(),50) 
      self.assertEqual(robot_0.getCostBasisPerRoundtrip(),1500) 

      if index == 0:
        robot_0.addNewRoundtripEntry()
      
      entries = robot_0.getAllBullishRoundtrips()
      self.assertEqual(len(entries),1)
      rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot())
      self.assertEqual(rt.getBullSymbol(),self.bullish) 
      self.assertEqual(rt.getBearSymbol(),self.bearish)
      self.assertEqual(rt.getBullBuyPrice(),self.bull_prices[0])
      self.assertEqual(rt.getBearBuyPrice(),self.bear_prices[0])
      self.assertEqual(rt.getBullSellPrice(),None)
      self.assertEqual(rt.getBearSellPrice(),None)
      self.assertEqual(rt.getBullSellDate(),None)
      self.assertEqual(rt.getBearSellDate(),None)
      self.assertEqual(rt.getBullQuantity(),6)
      self.assertEqual(rt.getBearQuantity(),26)
      self.assertEqual(rt.getBullCurrentPrice(),self.bull_prices[index]) 
      self.assertEqual(rt.getBearCurrentPrice(),self.bear_prices[index]) 
      self.assertEqual( type(rt.getTheBull()),TradeDataHolder)
      self.assertEqual( type(rt.getTheBear()),TradeDataHolder) 
      index = index+1

  #@unittest.skip("Taking a break now")
  def testTimeAndAgeAndDurationRobot(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    index = 0
    for n in self.current_times:
      payload = self.getTradeInformation(index)
      self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
      self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
      self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
      self.assertEqual(robot_0.getSymbol(),self.etf) 
      self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
      self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 
      self.assertEqual(robot_0.getCurrentTimestamp(),strToDatetime(self.current_times[index]))
      if index == 0:
        robot_0.addNewRoundtripEntry()
      
      entries = robot_0.getAllBullishRoundtrips()
      self.assertEqual(len(entries),1)
      rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot())
      
      if index == 1:
      ###TIME Functions
        self.assertEqual(rt.getAcquisitionDate(),strToDatetime(self.current_times[0]))
        self.assertEqual(rt.getBullBuyDate(),strToDatetime(self.current_times[0]))
        self.assertEqual(rt.getBearBuyDate(),strToDatetime(self.current_times[0]))
        self.assertEqual(rt.getTimeSincePurchase(),60)
        self.assertEqual(rt.getTimeSinceCompletion(),None)
        self.assertEqual(rt.getInStableDate(),strToDatetime(self.current_times[0])) 
        self.assertEqual(rt.getInTransitionDate(),None)
        self.assertEqual(rt.getCompletionDate(),None)
        self.assertEqual(rt.getTimeSpentInStable(),None)  
        self.assertEqual(rt.getDurationInStable(),60)
        self.assertEqual(rt.getTimeSpentInTransition(),None)
        self.assertEqual(rt.getTimeSpentActive(),None)
        self.assertEqual(rt.getDurationInTransition(),None)  
        self.assertEqual(rt.getRoundtripAge(),None)
        self.assertEqual(rt.getDurationSinceBullSold(),None)
        self.assertEqual(rt.getDurationSinceBearSold(),None)
        self.assertEqual(rt.isWithinTimeRangeByNumber(time_interval=180),True) 

      index = index + 1 


  #@unittest.skip("Taking a break now")
  def testWithinPriceRangeByProfitRobot(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    index = 0
    for n in self.current_times:
      payload = self.getTradeInformation(index=index)
      self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
      self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
      self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
      self.assertEqual(robot_0.getSymbol(),self.etf) 
      self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
      self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 
      self.assertEqual(robot_0.getCurrentTimestamp(),strToDatetime(self.current_times[index]))
      self.assertEqual(robot_0.getBearishComposition(),50) 
      self.assertEqual(robot_0.getBullishComposition(),50) 
      self.assertEqual(robot_0.getCostBasisPerRoundtrip(),1500) 

      if index == 0:
        robot_0.addNewRoundtripEntry()

      if index == 1:
        self.assertEqual(rt.isBearWithinSharePriceByNumber(number=1),True)  #bear = 28.95, 28.5
        self.assertEqual(rt.isBearWithinPriceRangeByComponentProfitRatio(component_percent=.10),True) #10% of $100 
        self.assertEqual(True,False)

        self.assertEqual(round(rt.getBearBreakevenPriceByTotalProfit(),2),32.80) # $32.80 is breakeven price
        self.assertEqual(round(rt.getBearBreakevenPriceByComponentProfitRatio(component_percent=.50),2),30.87) # $30.87 50% of $100
        self.assertEqual(rt.isBearPriceAboveBreakevenByTotalProfit(),False) #50% of $100
        self.assertEqual(rt.isBearPriceAboveBreakevenByComponentProfitRatio(component_percent=.50),False) #50% of $100
        self.assertEqual(round(rt.getBearBreakevenPricePercentByTotalProfit(),2),13.29) # $(32.80 - 28) / 28 = 13% 
        self.assertEqual(round(rt.getBearBreakevenPricePercentByComponentProfitRatio(component_percent=.50),2),6.64) # $30.87 50% of $100
        self.assertEqual(rt.isBullWithinPriceRangeByComponentProfitRatio(component_percent=.10),True) #10% of $100 
        self.assertEqual(round(rt.getBullBreakevenPriceByTotalProfit(),2),139.99) # $139.99 is breakeven price
        self.assertEqual(round(rt.getBullBreakevenPriceByComponentProfitRatio(component_percent=.10),2),124.99) # $124.99. 10% of $100
        self.assertEqual(rt.isBullPriceAboveBreakevenByTotalProfit(),False) #50% of $100
        self.assertEqual(rt.isBullPriceAboveBreakevenByComponentProfitRatio(component_percent=.50),False) #50% of $100
        self.assertEqual(round(rt.getBullBreakevenPricePercentByTotalProfit(),2),13.51) # $(123.32 - 139.99) / 123.32 = 13% 
        self.assertEqual(round(rt.getBullBreakevenPricePercentByComponentProfitRatio(component_percent=.50),2),6.76) # $30.87 50% of $100


  #@unittest.skip("Taking a break now")
  def testTimeAndPriceProximityRobot(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    index = 0
    for n in self.current_times:
      payload = self.getTradeInformation(index=index)
      self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
      self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
      self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
      self.assertEqual(robot_0.getSymbol(),self.etf) 
      self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
      self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 
      self.assertEqual(robot_0.getCurrentTimestamp(),strToDatetime(self.current_times[index]))
      if index == 0:
        robot_0.addNewRoundtripEntry()
      
      entries = robot_0.getAllBullishRoundtrips()
      self.assertEqual(len(entries),1)
      rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot())
      
      if index == 1:
        self.assertEqual(rt.isBearWithinSharePriceByNumber(number=1),True)  #bear = 28.95, 28.5
        self.assertEqual(rt.isBearWithinSharePriceByNumber(number=.44),False)  #bear = 28.95
        self.assertEqual(rt.isBearWithinSharePriceByNumber(number=.45),True)  #bear = 28.95
        self.assertEqual(rt.isBearWithinSharePriceByNumber(number=.40),False)  #bear = 28.95
        self.assertEqual(rt.isBearWithinSharePriceByNumber(number=.50),True)  #bear = 28.95
        self.assertEqual(rt.isBearWithinSharePriceByPercentage(percentage=1),False) #1% (28.95-28.5)/28.95 = 1.57%
        self.assertEqual(rt.isBearWithinSharePriceByPercentage(percentage=1.60),True) #1% (28.95-28.5)/28.95 = 1.57%
        self.assertEqual(rt.isBearWithinCostBasisByTotalProfit(),True) #$100 total profit

        self.assertEqual(rt.isBullWithinSharePriceByNumber(number=1),False)  #bull = 123.32, 124.35
        self.assertEqual(rt.isBullWithinSharePriceByNumber(number=1.44),True)  #bull = 123.32, 124.35
        self.assertEqual(rt.isBullWithinSharePriceByNumber(number=.45),False)  #bull = 123.32, 124.35
        self.assertEqual(rt.isBullWithinSharePriceByNumber(number=1.03),False)  #bull = 123.32, 124.35
        self.assertEqual(rt.isBullWithinSharePriceByNumber(number=1.01),False)  #bull = 123.32, 124.35
        self.assertEqual(rt.isBullWithinSharePriceByPercentage(percentage=1),True) #1% (123.32 - 124.35)/123.32 = .82%
        self.assertEqual(rt.isBullWithinSharePriceByPercentage(percentage=0.80),False) #1% (28.95-28.5)/28.95 = 1.57%
        self.assertEqual(rt.isBullWithinCostBasisByTotalProfit(),True) #$100 total profit

        self.assertEqual(rt.isWithinTimeRangeByNumber(time_interval=29),False) 
        self.assertEqual(rt.isWithinTimeRangeByNumber(time_interval=31),False) 
        self.assertEqual(rt.isWithinTimeRangeByNumber(time_interval=60),True) 


      if index == 2:
        self.assertEqual(rt.isBearWithinSharePriceByNumber(number=1),True) 
        self.assertEqual(rt.isRoundtripProfitNegative(),None) 
        self.assertEqual(rt.isRoundtripProfitPositive(),None) 
        self.assertEqual(rt.isRoundtripProfitAboveExpectations(),None) 
        self.assertEqual(rt.isRoundtriProfitBelowExpectations(),None)  
        self.assertEqual(rt.getProfitPercentage(),None) 
        self.assertEqual(rt.getAnnualizedProfitPercentage(),None) 
        self.assertEqual(rt.isBullTransitionalCandidate(),False) 
        self.assertEqual(rt.isBearTransitionalCandidate(),False)   
        self.assertEqual(rt.isCompletionCandidate(),False)   
        self.assertEqual(rt.getBullTransitionProfitTarget(),self.profit_basis_per_roundtrip/2) 
        self.assertEqual(rt.getBearTransitionProfitTarget(),self.profit_basis_per_roundtrip/2)  
        self.assertEqual(rt.getCompletionProfitTarget(),self.profit_basis_per_roundtrip/2) 
        self.assertEqual(rt.isTransitionalCandidate(),False) 
        self.assertEqual(rt.isCompletionCandidate(),False)  


      if index == 3:
        self.assertEqual(rt.isBearWithinSharePriceByNumber(number=1),True) 
        self.assertEqual(rt.isBullTransitionalCandidate(),False) 
        self.assertEqual(rt.isBearTransitionalCandidate(),False)   
        self.assertEqual(rt.isCompletionCandidate(),False)   
        self.assertEqual(rt.getBullTransitionProfitTarget(),self.profit_basis_per_roundtrip/2) 
        self.assertEqual(rt.getBearTransitionProfitTarget(),self.profit_basis_per_roundtrip/2)  
        self.assertEqual(rt.getCompletionProfitTarget(),self.profit_basis_per_roundtrip/2)  
        self.assertEqual(rt.isTransitionalCandidate(),False) 
        self.assertEqual(rt.isCompletionCandidate(),False) 

        
      index = index + 1

#####################################################################################################
#
# Five Roundtrips with moving dates are added to the Stable . 
# Validate that all basic functions can be reached and executed with correct results.
#
#@unittest.skip("Taking a break now")
class RoundtripFiveEntriesAddedTestCase(TestCase):
  base_name = 'testme'
  description = 'description'
  max_roundtrips = 20
  etf = 'DIA'
  bullish = 'UDOW'
  bearish = 'SDOW'
  cost_basis_per_roundtrip = 5000
  initial_budget = 100000
  profit_basis_per_roundtrip = 10
  bull_prices=[123.32,124.35,124.45,124.89,125.0]
  bear_prices=[28.95,28.5,28.00,27.83,27.69]
  current_times=['2020-08-03 04:05:00-04:00','2020-08-04 05:05:00-04:00','2020-08-05 06:05:00-04:00',
                 '2020-08-08 07:05:00-04:00','2020-08-09 07:35:00-04:00']
  internal_name='bafoussam'

  @classmethod 
  def setUpTestData(self):
    nasdaq=RobotEquitySymbols.objects.create(name='Nasdaq',symbol=self.etf,bullishSymbol=self.bullish,bearishSymbol=self.bearish)

    robot1=ETFAndReversePairRobot.objects.create(name=self.base_name,description=self.description,
            portfolio=None,strategy=None,symbols=nasdaq,enabled=True,owner=None,visibility=True,
            version='1.0.0', max_hold_time='14',minimum_hold_time='1',hold_time_includes_holiday=True,
            sell_remaining_before_buy=False,liquidate_on_next_opportunity=False,internal_name=self.internal_name,
            max_roundtrips=self.max_roundtrips,cost_basis_per_roundtrip=self.cost_basis_per_roundtrip,
            profit_target_per_roundtrip=self.profit_basis_per_roundtrip)
    
    self.robot_0_id =robot1.pk

    sentiment_0 = EquityAndMarketSentiment.objects.create(pair_robot=robot1,influences_acquisition=True,circuit_breaker=False,
                                                          sentiment_feed='Automatic')
 
    self.s0_id = sentiment_0.pk
    budget_management = RobotBudgetManagement.objects.create(pair_robot=robot1,use_percentage_or_fixed_value='Number',
        max_budget_per_purchase_number='1500')


  def getTradeInformation(self,index):
    information = dict()
    information[self.bullish]=self.bull_prices[index]
    information[self.bearish]=self.bear_prices[index] 
    information['timestamp'] = self.current_times[index]
    return information 

  #@unittest.skip("Taking a break now")
  def testRoundtripBasicRobot(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    index = 0
    for n in self.current_times:
      payload = self.getTradeInformation(index)
      self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
      self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
      self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
      self.assertEqual(robot_0.getSymbol(),self.etf) 
      self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
      self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 
      self.assertEqual(robot_0.getBearishComposition(),50) 
      self.assertEqual(robot_0.getBullishComposition(),50) 
      self.assertEqual(robot_0.getCostBasisPerRoundtrip(),1500) 
      self.assertEqual(robot_0.getProfitTargetPerRoundtrip(),10) 
      self.assertEqual(robot_0.getBullWeightedProfitTargetPerRoundtrip(),5.0) 
      self.assertEqual(robot_0.getBearWeightedProfitTargetPerRoundtrip(),5.0) 


      self.assertEqual(robot_0.getCurrentTimestamp(),strToDatetime(self.current_times[index]))
      if (index == 0) or (index == 1) or (index == 2) or (index == 3) or (index == 4):
        robot_0.addNewRoundtripEntry()
      
      entries = robot_0.getAllBullishRoundtrips()
      if index == 0:
        self.assertEqual(len(entries),1)
        rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot())
        self.assertEqual(rt.getBullSymbol(),self.bullish) 
        self.assertEqual(rt.getBearSymbol(),self.bearish)
        self.assertEqual(rt.getBullBuyPrice(),self.bull_prices[0])
        self.assertEqual(rt.getBearBuyPrice(),self.bear_prices[0])
        self.assertEqual(rt.getBullSellPrice(),None)
        self.assertEqual(rt.getBearSellPrice(),None)
        self.assertEqual(rt.getBullSellDate(),None)
        self.assertEqual(rt.getBearSellDate(),None)
        self.assertEqual(rt.getBullQuantity(),6)
        self.assertEqual(rt.getBearQuantity(),26)
        self.assertEqual(rt.getBullCurrentPrice(),self.bull_prices[index]) 
        self.assertEqual(rt.getBearCurrentPrice(),self.bear_prices[index]) 
        self.assertEqual( type(rt.getTheBull()),TradeDataHolder)
        self.assertEqual( type(rt.getTheBear()),TradeDataHolder) 

      if index == 1:
        self.assertEqual(len(entries),2)
        rt = RoundTrip(robot=robot_0,root_id=entries[1].getOrderClientIDRoot())
        self.assertEqual(rt.getBullSymbol(),self.bullish) 
        self.assertEqual(rt.getBearSymbol(),self.bearish)
        self.assertEqual(rt.getBullBuyPrice(),self.bull_prices[1])
        self.assertEqual(rt.getBearBuyPrice(),self.bear_prices[1])
        self.assertEqual(rt.getBullSellPrice(),None)
        self.assertEqual(rt.getBearSellPrice(),None)
        self.assertEqual(rt.getBullSellDate(),None)
        self.assertEqual(rt.getBearSellDate(),None)
        self.assertEqual(rt.getBullQuantity(),6)
        self.assertEqual(rt.getBearQuantity(),26)
        self.assertEqual(rt.getBullCurrentPrice(),self.bull_prices[index]) 
        self.assertEqual(rt.getBearCurrentPrice(),self.bear_prices[index]) 
        self.assertEqual( type(rt.getTheBull()),TradeDataHolder)
        self.assertEqual( type(rt.getTheBear()),TradeDataHolder) 


      if index == 2:
        self.assertEqual(len(entries),3)
        rt = RoundTrip(robot=robot_0,root_id=entries[1].getOrderClientIDRoot())
        self.assertEqual(rt.getBullSymbol(),self.bullish) 
        self.assertEqual(rt.isBearWithinSharePriceByNumber(number=1),True) 
        self.assertEqual(rt.isRoundtripProfitNegative(),None) 
        self.assertEqual(rt.isRoundtripProfitPositive(),None) 
        self.assertEqual(rt.isRoundtripProfitAboveExpectations(),None) 
        self.assertEqual(rt.isRoundtriProfitBelowExpectations(),None)  
        self.assertEqual(rt.getProfitPercentage(),None) 
        self.assertEqual(rt.getAnnualizedProfitPercentage(),None) 
        self.assertEqual(rt.isBullTransitionalCandidate(),False) 
        self.assertEqual(rt.isBearTransitionalCandidate(),False)   
        self.assertEqual(rt.isCompletionCandidate(),False)   
        self.assertEqual(rt.getBullTransitionProfitTarget(),self.profit_basis_per_roundtrip/2) 
        self.assertEqual(rt.getBearTransitionProfitTarget(),self.profit_basis_per_roundtrip/2)  
        self.assertEqual(rt.getCompletionProfitTarget(),self.profit_basis_per_roundtrip/2) 
        self.assertEqual(rt.isTransitionalCandidate(),False) 
        self.assertEqual(rt.isCompletionCandidate(),False)  


      if index == 3:
        self.assertEqual(len(entries),4)
        rt = RoundTrip(robot=robot_0,root_id=entries[1].getOrderClientIDRoot())
        self.assertEqual(rt.getBullSymbol(),self.bullish) 
        self.assertEqual(rt.isBearWithinSharePriceByNumber(number=1),True) 
        self.assertEqual(rt.isBullTransitionalCandidate(),False) 
        self.assertEqual(rt.isBearTransitionalCandidate(),False)   
        self.assertEqual(rt.isCompletionCandidate(),False)   
        self.assertEqual(rt.getBullTransitionProfitTarget(),self.profit_basis_per_roundtrip/2) 
        self.assertEqual(rt.getBearTransitionProfitTarget(),self.profit_basis_per_roundtrip/2)  
        self.assertEqual(rt.getCompletionProfitTarget(),self.profit_basis_per_roundtrip/2)  
        self.assertEqual(rt.isTransitionalCandidate(),False) 
        self.assertEqual(rt.isCompletionCandidate(),False) 


      if index == 4:
        self.assertEqual(len(entries),5)
        rt = RoundTrip(robot=robot_0,root_id=entries[1].getOrderClientIDRoot())
        self.assertEqual(rt.getBullSymbol(),self.bullish) 


      index = index+1


##############################################################################################
# Roundtrip Interface
#
# Tests the functionality around the Roundtrip (Interface) Class.
# Roundtrip is not a real class. It is an interface to access TradeDataHolder Class
# and perform various manipulations. It is a more sophisticated version of the TradeDataHolder class
# RoundTrip is used within the ETFAndReversePairRobot class and understand everything about the concepts. 
# Tests the functionality around:
#    BasicRobotWithOneBuyOneSaleTestCase : 
#      Buy several (up to 4), 
#      SellTheBull(): validate inTransitionFunctions() 
#      SellTheBear(): validate inTransitionFunctions()
#####################################################################################################
#
# One Roundtrip . Validate that all basic functions can be reached and executed with correct results.
#@unittest.skip("Taking a break now")
class RoundtripWithOneBuyOneSaleTestCase(TestCase):
  base_name = 'testme'
  description = 'description'
  max_roundtrips = 20
  etf = 'TTT'
  bullish = 'TZA'
  bearish = 'TNA'
  cost_basis_per_roundtrip = 2500
  initial_budget = 100000
  profit_basis_per_roundtrip = 50
  bull_prices=[18.50,18.56,18.71,17.61,16.91,16.88] 
  bear_prices=[30.10,30.02,29.99,28.00,30.85,31.58]
  current_times=['2020-08-03 08:00:00-04:00','2020-08-03 08:40:00-04:00','2020-08-03 09:05:00-04:00',
                 '2020-08-04 15:50:00-04:00', '2020-08-04 09:05:00-04:00', '2020-08-05 09:05:00-04:00']
  internal_name='ningun'

  @classmethod 
  def setUpTestData(self):
    nasdaq=RobotEquitySymbols.objects.create(name='Nasdaq',symbol=self.etf,bullishSymbol=self.bullish,bearishSymbol=self.bearish)

    robot1=ETFAndReversePairRobot.objects.create(name=self.base_name,description=self.description,
            portfolio=None,strategy=None,symbols=nasdaq,enabled=True,owner=None,visibility=True,
            version='1.0.0', max_hold_time='14',minimum_hold_time='1',hold_time_includes_holiday=True,
            sell_remaining_before_buy=False,liquidate_on_next_opportunity=False,internal_name=self.internal_name,
            max_roundtrips=self.max_roundtrips,cost_basis_per_roundtrip=self.cost_basis_per_roundtrip,
            profit_target_per_roundtrip=self.profit_basis_per_roundtrip)
    
    self.robot_0_id =robot1.pk

    sentiment_0 = EquityAndMarketSentiment.objects.create(pair_robot=robot1,influences_acquisition=True,circuit_breaker=False,
                                                          sentiment_feed='Automatic')
 
    self.s0_id = sentiment_0.pk
    budget_management = RobotBudgetManagement.objects.create(pair_robot=robot1,use_percentage_or_fixed_value='Number',
        max_budget_per_purchase_number='1500')


  def getTradeInformation(self,index):
    information = dict()
    information[self.bullish]=self.bull_prices[index]
    information[self.bearish]=self.bear_prices[index] 
    information['timestamp'] = self.current_times[index]
    return information 

  #@unittest.skip("Taking a break now")
  def testRoundtripBasicRobot(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    index = 0
    for n in self.current_times:
      payload = self.getTradeInformation(index)
      self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
      self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
      self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
      self.assertEqual(robot_0.getSymbol(),self.etf) 
      self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
      self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 
      self.assertEqual(robot_0.getCurrentTimestamp(),strToDatetime(self.current_times[index]))
      if (index == 0) or (index == 1) or (index == 2) or (index == 3) or (index == 4):
        robot_0.addNewRoundtripEntry()
      
      entries = robot_0.getAllBullishRoundtrips()
      if index == 0:
        self.assertEqual(len(entries),1)
        rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot())
        self.assertEqual(rt.getBullSymbol(),self.bullish) 
        self.assertEqual(rt.getBearSymbol(),self.bearish)
        self.assertEqual(rt.getBullBuyPrice(),self.bull_prices[0])
        self.assertEqual(rt.getBearBuyPrice(),self.bear_prices[0])
        self.assertEqual(rt.getBullSellPrice(),None)
        self.assertEqual(rt.getBearSellPrice(),None)
        self.assertEqual(rt.getBullSellDate(),None)
        self.assertEqual(rt.getBearSellDate(),None)
        self.assertEqual(rt.getBullQuantity(),41)
        self.assertEqual(rt.getBearQuantity(),25)
        self.assertEqual(rt.getBullCurrentPrice(),self.bull_prices[index]) 
        self.assertEqual(rt.getBearCurrentPrice(),self.bear_prices[index]) 
        self.assertEqual( type(rt.getTheBull()),TradeDataHolder)
        self.assertEqual( type(rt.getTheBear()),TradeDataHolder) 

      if index == 1:
        self.assertEqual(len(entries),2)
        rt = RoundTrip(robot=robot_0,root_id=entries[1].getOrderClientIDRoot())
        self.assertEqual(rt.getBullSymbol(),self.bullish) 
        self.assertEqual(rt.getBearSymbol(),self.bearish)
        self.assertEqual(rt.getBullBuyPrice(),self.bull_prices[1])
        self.assertEqual(rt.getBearBuyPrice(),self.bear_prices[1])
        self.assertEqual(rt.getBullSellPrice(),None)
        self.assertEqual(rt.getBearSellPrice(),None)
        self.assertEqual(rt.getBullSellDate(),None)
        self.assertEqual(rt.getBearSellDate(),None)
        self.assertEqual(rt.getBullQuantity(),40)
        self.assertEqual(rt.getBearQuantity(),25)
        self.assertEqual(rt.getBullCurrentPrice(),self.bull_prices[index]) 
        self.assertEqual(rt.getBearCurrentPrice(),self.bear_prices[index]) 
        self.assertEqual( type(rt.getTheBull()),TradeDataHolder)
        self.assertEqual( type(rt.getTheBear()),TradeDataHolder) 

      if index == 2:
        self.assertEqual(len(entries),3)
        rt = RoundTrip(robot=robot_0,root_id=entries[1].getOrderClientIDRoot())
        self.assertEqual(rt.getBullSymbol(),self.bullish) 

        # Move to Transition
        rt.sellTheBear()
        self.assertEqual(rt.isInBullishTransition(),True) 
        self.assertEqual(rt.isStable(),False) 
        self.assertEqual(rt.isCompleted(),False) 
        self.assertEqual(rt.isActive(),True) 

        self.assertEqual(rt.getBullSellPrice(),None)
        self.assertEqual(rt.getBearSellPrice(),29.99)
        self.assertEqual(rt.getBullSellDate(),None)
        self.assertEqual(rt.getBearSellDate(),strToDatetime(self.current_times[index]))
        self.assertEqual(rt.getBullQuantity(),40)
        self.assertEqual(rt.getBearQuantity(),25)

        self.assertEqual(rt.getInTransitionDate(),strToDatetime(self.current_times[index]))
        self.assertEqual(rt.getCompletionDate(),None)
        self.assertEqual(rt.getTimeSpentInStable(),25.0)  
        self.assertEqual(rt.getDurationInStable(),None)
        self.assertEqual(rt.getTimeSpentInTransition(),None)
        self.assertEqual(rt.getTimeSpentActive(),None)
        self.assertEqual(rt.getDurationInTransition(),0.0)  
        self.assertEqual(rt.getRoundtripAge(),None)
        self.assertEqual(rt.getDurationSinceBullSold(),None)
        self.assertEqual(rt.getDurationSinceBearSold(),0.0)
        self.assertEqual(rt.getStableBullValue(),None) 
        self.assertEqual(rt.getStableBearValue(),None) 
        self.assertEqual(rt.getStableTotalValue(),None) 
        self.assertEqual(rt.getTransitionalDeltaValue(),5.25) 
        self.assertEqual(rt.getTransitionalTotalValue(),1498.15) 
        self.assertEqual(rt.getRoundtripRealizedProfit(),-0.75) 

      if index == 3:
        self.assertEqual(len(entries),4)
        rt = RoundTrip(robot=robot_0,root_id=entries[2].getOrderClientIDRoot())
        self.assertEqual(rt.getBullSymbol(),self.bullish) 
        # Move to Transition
        rt.sellTheBull()
        self.assertEqual(rt.isInBearishTransition(),True) 
        self.assertEqual(rt.isStable(),False) 
        self.assertEqual(rt.isCompleted(),False) 
        self.assertEqual(rt.isActive(),True) 
        self.assertEqual(rt.getBullSellPrice(),17.61)
        self.assertEqual(rt.getBearSellPrice(),None)
        self.assertEqual(rt.getBearSellDate(),None)
        self.assertEqual(rt.getBullSellDate(),strToDatetime(self.current_times[index]))
        self.assertEqual(rt.getBullQuantity(),40)
        self.assertEqual(rt.getBearQuantity(),25)

        self.assertEqual(rt.getInTransitionDate(),strToDatetime(self.current_times[index]))
        self.assertEqual(rt.getCompletionDate(),None)
        self.assertEqual(rt.getTimeSpentInStable(),1845.0)  
        self.assertEqual(rt.getDurationInStable(),None)
        self.assertEqual(rt.getTimeSpentInTransition(),None)
        self.assertEqual(rt.getTimeSpentActive(),None)
        self.assertEqual(rt.getDurationInTransition(),0.0)  
        self.assertEqual(rt.getRoundtripAge(),None)
        self.assertEqual(rt.getDurationSinceBullSold(),0.0)
        self.assertEqual(rt.getDurationSinceBearSold(),None)
        self.assertEqual(rt.getStableBullValue(),None) 
        self.assertEqual(rt.getStableBearValue(),None) 
        self.assertEqual(rt.getStableTotalValue(),None) 
        self.assertEqual(rt.getTransitionalDeltaValue(),-93.75) 
        self.assertEqual(rt.getTransitionalTotalValue(),1404.4) 
        self.assertEqual(round(rt.getRoundtripRealizedProfit(),2),-44.00) 

      if index == 4:
        self.assertEqual(len(entries),5)
        rt = RoundTrip(robot=robot_0,root_id=entries[4].getOrderClientIDRoot())
        self.assertEqual(rt.getBullSymbol(),self.bullish) 
        self.assertEqual(rt.isStable(),True) 
        self.assertEqual(rt.isCompleted(),False) 
        self.assertEqual(rt.isActive(),True) 
        self.assertEqual(rt.getBullQuantity(),43)
        self.assertEqual(rt.getBearQuantity(),27)
        rt.sellTheBull()
        rt.sellTheBear()
        self.assertEqual(rt.isStable(),False) 
        self.assertEqual(rt.isCompleted(),True) 
        self.assertEqual(rt.isActive(),False) 
        self.assertEqual(rt.getBullSellPrice(),16.91)
        self.assertEqual(rt.getBearSellPrice(),30.85)
        self.assertEqual(rt.getBearSellDate(),strToDatetime(self.current_times[index]))
        self.assertEqual(rt.getBullSellDate(),strToDatetime(self.current_times[index]))
        self.assertEqual(rt.getBullQuantity(),43)
        self.assertEqual(rt.getBearQuantity(),27)

        self.assertEqual(rt.getInTransitionDate(),strToDatetime(self.current_times[index]))
        self.assertEqual(rt.getCompletionDate(),strToDatetime(self.current_times[index]))
        self.assertEqual(rt.getDurationInStable(),None)
        self.assertEqual(rt.getTimeSpentInTransition(),0.0)
        self.assertEqual(rt.getDurationInTransition(),None)  

        self.assertEqual(rt.getDurationSinceBullSold(),0.0)
        self.assertEqual(rt.getDurationSinceBearSold(),0.0)
        self.assertEqual(rt.getStableBullValue(),None) 
        self.assertEqual(rt.getStableBearValue(),None) 
        self.assertEqual(rt.getStableTotalValue(),None) 
        self.assertEqual(rt.getTransitionalDeltaValue(),None) 
        self.assertEqual(rt.getTransitionalTotalValue(),None) 
        self.assertEqual(round(rt.getRoundtripRealizedProfit(),2),46.85) 

        #TODO: Douala Team to Complete this work
        #self.assertEqual(rt.getRoundtripAge(),0.0)
        #self.assertEqual(rt.getTimeSpentActive(),0.0)
        #self.assertEqual(rt.getTimeSpentInStable(),0.0)  

      index = index+1



  #@unittest.skip("Taking a break now")
  def testBullBearCompositionAndRatios(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(len(entries),1)
    rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot())
    #Ratios between Bulls and Bears
    self.assertTrue(48<rt.getCostBasisBullRatio()<51) 
    self.assertTrue(48<rt.getCostBasisBearRatio()<51)
    self.assertTrue(48<rt.getCurrentValueBasedBullRatio()<51) 
    self.assertTrue(48<rt.getCurrentValueBasedBearRatio()<51)  
    self.assertEqual(rt.getBullCostBasisRatioDelta(),0) 
    self.assertEqual(rt.getBearCostBasisRatioDelta(),0) 


  #@unittest.skip("Taking a break now")
  def testClientOrderIDsStagesRobot(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(len(entries),1)
    rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot())
    self.assertEqual(rt.getRootOrderClientID().split('_')[0],self.internal_name) 
    self.assertEqual(int(rt.getRootOrderClientID().split('_')[1]),robot_0.pk) 
    self.assertEqual(rt.getBullBuyOrderClientID().split('_')[0],self.internal_name) 
    self.assertEqual(int(rt.getBullBuyOrderClientID().split('_')[1]),robot_0.pk) 
    self.assertEqual(rt.getBullBuyOrderClientID().split('_')[3],'buy') 
    self.assertEqual(rt.getBullBuyOrderClientID().split('_')[4],self.bullish) 
    self.assertEqual(rt.getBearBuyOrderClientID().split('_')[0],self.internal_name) 
    self.assertEqual(int(rt.getBearBuyOrderClientID().split('_')[1]),robot_0.pk) 
    self.assertEqual(rt.getBearBuyOrderClientID().split('_')[3],'buy') 
    self.assertEqual(rt.getBearBuyOrderClientID().split('_')[4],self.bearish) 
    self.assertEqual(rt.getBullSellOrderClientID().split('_')[0],self.internal_name) 
    self.assertEqual(int(rt.getBullSellOrderClientID().split('_')[1]),robot_0.pk) 
    self.assertEqual(rt.getBullSellOrderClientID().split('_')[3],'sell') 
    self.assertEqual(rt.getBullSellOrderClientID().split('_')[4],self.bullish) 
    self.assertEqual(rt.getBearSellOrderClientID().split('_')[0],self.internal_name) 
    self.assertEqual(int(rt.getBearSellOrderClientID().split('_')[1]),robot_0.pk) 
    self.assertEqual(rt.getBearSellOrderClientID().split('_')[3],'sell') 
    self.assertEqual(rt.getBearSellOrderClientID().split('_')[4],self.bearish) 

  #@unittest.skip("Taking a break now")
  def testValidationAndTransitionalStages(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(len(entries),1)
    rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot())
    #Stage Completion Functions.
    self.assertEqual(rt.hasExactlyTwoEntries(),True) 
    self.assertEqual(rt.isValid(),True) 
    self.assertEqual(rt.isStable(),True) 
    self.assertEqual(rt.isInBullishTransition(),False) 
    self.assertEqual(rt.isInTransition(),False) 
    self.assertEqual(rt.isActive(),True) 
    self.assertEqual(rt.isCompleted(),False) 
    self.assertEqual(rt.getIsBullishOrBearishTransition(),"Invalid") 
    self.assertEqual(rt.isInBearishTransition(),False) 

  #@unittest.skip("These functions shouldn't be here.")
  def testTransitionalFilteringRobot(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(len(entries),1)
    rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot())
    #TODO: MUST BE REMOVED
    self.assertEqual(rt.isBullTransitionalCandidate(),False) 
    self.assertEqual(rt.isBearTransitionalCandidate(),False) 
    self.assertEqual(rt.isCompletionCandidate(),False) 

  #@unittest.skip("Taking a break now")
  def testTimeAndAgeAndDurationRobot(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(len(entries),1)
    rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot())  
    ###TIME Functions
    self.assertEqual(rt.getAcquisitionDate(),strToDatetime(self.current_times[0]))
    self.assertEqual(rt.getBullBuyDate(),strToDatetime(self.current_times[0]))
    self.assertEqual(rt.getBearBuyDate(),strToDatetime(self.current_times[0]))
    self.assertEqual(rt.getTimeSincePurchase(),0.0)
    self.assertEqual(rt.getTimeSinceCompletion(),None)
    self.assertEqual(rt.getInStableDate(),strToDatetime(self.current_times[0])) 
    self.assertEqual(rt.getInTransitionDate(),None)
    self.assertEqual(rt.getCompletionDate(),None)
    self.assertEqual(rt.getTimeSpentInStable(),None)  
    self.assertEqual(rt.getDurationInStable(),0.0)
    self.assertEqual(rt.getTimeSpentInTransition(),None)
    self.assertEqual(rt.getTimeSpentActive(),None)
    self.assertEqual(rt.getDurationInTransition(),None)  
    self.assertEqual(rt.getRoundtripAge(),None)
    self.assertEqual(rt.getDurationSinceBullSold(),None)
    self.assertEqual(rt.getDurationSinceBearSold(),None)

  #@unittest.skip("Taking a break now")
  def testCombinedCostsAndValueAtVariousStages(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(len(entries),1)
    rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot()) 
    self.assertEqual(round(rt.getBullCostBasis(),2),758.5) 
    self.assertEqual(round(rt.getBearCostBasis(),2),752.50)
    self.assertEqual(round(rt.getBullCurrentValue(),2),758.50) 
    self.assertEqual(round(rt.getBearCostBasis(),2),752.50)
    self.assertEqual(round(rt.getRoundtripCostBasis(),2),1511.0)  
    self.assertEqual(round(rt.getBullBearCostBasisDelta(),2),6.0)
    self.assertEqual(round(rt.getBullBearCurrentValueDelta(),2),6.0)
    self.assertEqual(rt.getBullRealizedValue(),None) 
    self.assertEqual(rt.getBearRealizedValue(),None)
    self.assertEqual(rt.getTransitionalRealized(),None) 
    self.assertEqual(rt.getRoundtripRealizedValue(),None)
    self.assertEqual(rt.getRoundtripUnrealizedValue(),1511.0) 
    self.assertEqual(rt.getTransitionalUnRealized(),None) 
    self.assertEqual(rt.getRoundtripInTransitionRealizedProfit(),None)
    self.assertEqual(rt.getRoundtripRealizedProfit(),None)  
    self.assertEqual(rt.getRealizedAndSettled(),None)
    self.assertEqual(rt.getRealizedAndSettled(),None)

  #@unittest.skip("Taking a break now")
  def testProfitabilityRobot(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(len(entries),1)
    rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot()) 
    self.assertEqual(round(rt.getStableBullValue(),2),0.0) 
    self.assertEqual(round(rt.getStableBearValue(),2),0.0) 
    self.assertEqual(round(rt.getStableTotalValue(),2),0.0) 
    self.assertEqual(rt.getTransitionalDeltaValue(),None) 
    self.assertEqual(rt.getTransitionalTotalValue(),None) 
    self.assertEqual(rt.getRoundtripRealizedProfit(),None) 

  #@unittest.skip("Taking a break now")
  def testPerformanceStatistics(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(len(entries),1)
    rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot()) 
    self.assertEqual(rt.isRoundtripProfitNegative(),None) 
    self.assertEqual(rt.isRoundtripProfitPositive(),None) 
    self.assertEqual(rt.isRoundtripProfitAboveExpectations(),None) 
    self.assertEqual(rt.isRoundtriProfitBelowExpectations(),None) 
    #TODO: 
    #self.assertEqual(rt.getProfitPercentage(),None) 
    #self.assertEqual(rt.getAnnualizedProfitPercentage(),None) 
  

  #@unittest.skip("Taking a break now")
  def testTimeAndPriceProximityRobot(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(len(entries),1)
    rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot()) 
    self.assertEqual(rt.isBearWithinSharePriceByNumber(number=1),True) 
    self.assertEqual(rt.isBullWithinSharePriceByNumber(number=1),True) 

    self.assertEqual(rt.isBullWithinSharePriceByPercentage(percentage=1),True) 
    self.assertEqual(rt.isBearWithinSharePriceByPercentage(percentage=1),True) 

    self.assertEqual(rt.isBearWithinCostBasisByTotalProfit(),True) 
    self.assertEqual(rt.isBullWithinCostBasisByTotalProfit(),True) 

    self.assertEqual(rt.isBearWithinCostBasisByPercentageOfTotalProfit(),True) 
    self.assertEqual(rt.isBullWithinCostBasisByPercentageOfTotalProfit(),True) 


    self.assertEqual(rt.isWithinTimeRangeByNumber(),True) 

  # Validate number of Transactions 
  def testTradeDataHoldersViaRobot(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()

    self.assertEqual(robot_0.getAllBullishPurchaseTransactions(),1)  
    self.assertEqual(robot_0.getAllBearishPurchaseTransactions(),1)      
    self.assertEqual(robot_0.getAllPurchaseTransactions(),2)  

    self.assertEqual(robot_0.getAllBullishSaleTransactions(),0)  
    self.assertEqual(robot_0.getAllBearishSaleTransactions(),0)
    self.assertEqual(robot_0.getAllSaleTransactions(),0)  

    self.assertEqual(robot_0.getAllBullishUnrealizedTransactions(),1)
    self.assertEqual(robot_0.getAllBearishUnrealizedTransactions(),1) 
    self.assertEqual(robot_0.getAllUnRealizedTransactions(),2)
    self.assertEqual(robot_0.getAllTransactions(),2)  

  # Validate Share Quantity Operations 
  def testTradeDataHoldersViaRobot2(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=0)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[0]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[0]) 
    robot_0.addNewRoundtripEntry()
    entries = robot_0.getAllBullishRoundtrips()
    self.assertEqual(robot_0.getAllBullishSharesAcquired(),41)
    self.assertEqual(robot_0.getAllBearishSharesAcquired(),25)
    self.assertEqual(robot_0.getAllSharesAcquired(),66)

    self.assertEqual(robot_0.getAllBullishSharesSold(),0)
    self.assertEqual(robot_0.getAllBearishSharesSold(),0)
    self.assertEqual(robot_0.getAllSharesSold(),0)

    self.assertEqual(robot_0.getAllBullishSharesUnrealized(),41)
    self.assertEqual(robot_0.getAllBearishSharesUnrealized(),25) 
    self.assertEqual(robot_0.getAllSharesUnrealized(),66)

 

#################################################################################################################
# RoundTripWithRiskExposureCalculationTestCase: When acquiring Bulls/Bears with compositions different than 50/50
# there is a certain exposure to risk that should be calculated.
# These test should make sure we have a good understanding of the infrastructure we have put in place to calculate risks.
# One Roundtrip with moving dates (current time) and moving Prices with various Bull/Bear Compositions. 
# Validate that all basic functions can be reached and executed with correct results.
# Additionall, get a avery good understanding on how we are exposing ourselves to risks and 
# add additional functions to understand risks better.
# TODO: This function will be implemented as version 2.0.
#   It will require some additional work to be done with the Douala/Yaounde Teams.
@unittest.skip("Taking a break now")
class RoundTripWithRiskExposureCalculationTestCase(TestCase):
  base_name = 'testme'
  description = 'description'
  max_roundtrips = 20
  etf = 'QQQ'
  bullish = 'TQQQ'
  bearish = 'SQQQ'
  cost_basis_per_roundtrip = 2000
  initial_budget = 100000
  profit_basis_per_roundtrip = 100
  bull_prices=[123.32,124.35,124.45]
  bear_prices=[28.95,28.5,28.00]
  current_times=['2020-08-03 04:05:00-04:00','2020-08-03 05:05:00-04:00','2020-08-03 06:05:00-04:00']
  internal_name='bamboutos'

  @classmethod 
  def setUpTestData(self):
    nasdaq=RobotEquitySymbols.objects.create(name='Nasdaq',symbol='QQQ',bullishSymbol=self.bullish,bearishSymbol=self.bearish)

    strategy = EquityStrategy.objects.create(name='My Best Equity Strategy So Far',description='This is just a test',creation_date=now,
      modify_date=now,strategy_class='Bullish Bearish Pair',strategy_category='Batcham',visibility=False,
      minimum_entries_before_trading=2, trade_only_after_fully_loaded=False,manual_asset_composition=True,
      automatic_generation_client_order_id=True)

    robot1=ETFAndReversePairRobot.objects.create(name=self.base_name,description=self.description,
            portfolio=None,strategy=strategy,symbols=nasdaq,enabled=True,owner=None,visibility=True,
            version='1.0.0', max_hold_time='14',minimum_hold_time='1',hold_time_includes_holiday=True,
            sell_remaining_before_buy=False,liquidate_on_next_opportunity=False,internal_name=self.internal_name,
            max_roundtrips=self.max_roundtrips,cost_basis_per_roundtrip=self.cost_basis_per_roundtrip,
            profit_target_per_roundtrip=self.profit_basis_per_roundtrip)
    
    self.robot_0_id =robot1.pk

    sentiment_0 = EquityAndMarketSentiment.objects.create(pair_robot=robot1,influences_acquisition=True,circuit_breaker=False,
                                                          sentiment_feed='Automatic')
 
    self.s0_id = sentiment_0.pk
    budget_management = RobotBudgetManagement.objects.create(pair_robot=robot1,use_percentage_or_fixed_value='Number')


  def getTradeInformation(self,index):
    information = dict()
    information[self.bullish]=self.bull_prices[index]
    information[self.bearish]=self.bear_prices[index] 
    information['timestamp'] = self.current_times[index]
    return information 

  #@unittest.skip("Taking a break now")
  def testRoundtripBasicRobot(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    index = 0
    for n in self.current_times:
      payload = self.getTradeInformation(index=index)
      self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
      self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
      self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
      self.assertEqual(robot_0.getSymbol(),self.etf) 
      self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
      self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 
      self.assertEqual(robot_0.getCurrentTimestamp(),strToDatetime(self.current_times[index]))
      if index == 0:
        robot_0.addNewRoundtripEntry()
      
      entries = robot_0.getAllBullishRoundtrips()
      self.assertEqual(len(entries),1)
      rt = RoundTrip(robot=robot_0,root_id=entries[0].getOrderClientIDRoot())
      self.assertEqual(rt.getBullSymbol(),self.bullish) 
      self.assertEqual(rt.getBearSymbol(),self.bearish)
      self.assertEqual(rt.getBullBuyPrice(),self.bull_prices[0])
      self.assertEqual(rt.getBearBuyPrice(),self.bear_prices[0])
      self.assertEqual(rt.getBullSellPrice(),None)
      self.assertEqual(rt.getBearSellPrice(),None)
      self.assertEqual(rt.getBullSellDate(),None)
      self.assertEqual(rt.getBearSellDate(),None)
      self.assertEqual(rt.getBullQuantity(),6)
      self.assertEqual(rt.getBearQuantity(),26)
      self.assertEqual(rt.getBullCurrentPrice(),self.bull_prices[index]) 
      self.assertEqual(rt.getBearCurrentPrice(),self.bear_prices[index]) 
      self.assertEqual( type(rt.getTheBull()),TradeDataHolder)
      self.assertEqual( type(rt.getTheBear()),TradeDataHolder) 
      index = index+1

