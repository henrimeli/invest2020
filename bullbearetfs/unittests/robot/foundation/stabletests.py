from datetime import datetime, time
import logging, unittest
import sys,json
import xmlrunner
from django.utils import timezone
from django.test import TestCase

# Import Models
from bullbearetfs.strategy.models import EquityStrategy, AcquisitionPolicy,DispositionPolicy,OrdersManagement,PortfolioProtectionPolicy
from bullbearetfs.robot.models import ETFAndReversePairRobot,TradeDataHolder
from bullbearetfs.robot.symbols.models import RobotEquitySymbols
from bullbearetfs.robot.activitysentiments.models import EquityAndMarketSentiment
from bullbearetfs.robot.budget.models import RobotBudgetManagement
from bullbearetfs.robot.foundation.roundtrip import RoundTrip
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, strToDatetime
logger = logging.getLogger(__name__)

#
# Dummy function needed to force rebuild on change.
#
def test_stable_roundtrip_dummy(request):
  pass

##########################################################################################################
# StableRoundTrips Interface
#
# Tests the functionality around the StableRoundTrips (Interface) Class.
# StableRoundtrips is not a persistable Class. It is an interface to access RoundTrips in a Stable State
# and perform various manipulations. It is a more sophisticated version of the TradeDataHolder class with
# emphasis on data that meet the criteria of RoundTrips.isStable()==True
# StableRoundTrips is a collection of RoundTrips.
# it is used within the ETFAndReversePairRobot class and understand everything about the internals
# of the RoundTrip.
# Functionality in the Roundtrip has been grouped in the following areas:
  # Size of the Set, isEmpty(),isFullyLoaded()
  # Total Cost, Current Value, Performance
  # Highest/Lowest CostBasis, Highest/Lowest Current Value, Highest/Lowest ProfitPotential
  # Oldest/Youngest . Age in comparison to Minimum Hold Time and Maximum Hold Time.
  # Check if current asset price (not yet bought) is within a range of existing values in the Stable
  # This check makes it possible to buy smart.
##############################################################################################################
# Tests the functionality around:
#  Unit Test Organization. Most unittests will be organized in the following classes.
#    A Test Class for the empty set and validations to ensure proper returns, when there is no data.
#    A Test Class with up to 5 Data entries to make sure the functions are called and respond properly.
#    A Test Class with a large number of data (20-50 maybe)
#    A Test Class with combined Robots to ensure that application can function with various Robots.
#    Optionally a Test Class with Risk, Performance, ... etc.
# Tests the functionality around:
#    EmptyStableRoundTripTestCase: This represents an empty StableRoundTrip. We want to make sure all the data i
#
#    AddingUpToFourEntries: Adds up to 4 entries in the StableBox and validate that the calculations match.
#    Status: INCOMPLETE
#
#    AddingUpToFiftyEntries:  Create a Robot and add up to 50 entries to make sure it can take this large number
#    Status: INCOMPLETE
#
#    RoundTripWithRiskExposureCalculationTestCase: INCOMPLETE
#  
#  A Roundtrip has various states. Stable, InTransition and Complete.
#  Stable Roundtrip: 
#  InTransition Roundtrip:
#  Complete Roundtrip:
#####################################################################################################
#
# One Simple Roundtrip . Validate that all basic functions can be reached and executed with correct results.
#
#@unittest.skip("Taking a break now")
class EmptyStableRoundTripTestCase(TestCase):
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
    budget_management = RobotBudgetManagement.objects.create(pair_robot=robot1,use_percentage_or_fixed_value='Number')


  def getTradeInformation(self,index):
    information = dict()
    information[self.bullish]=self.bull_prices[index]
    information[self.bearish]=self.bear_prices[index] 
    information['timestamp'] = self.current_times[index]
    return information 

  #@unittest.skip("Taking a break now")
  def testBasicIndividualInformation(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are Robots 
    stable = robot_0.getStableRoundTrips()
    self.assertEqual(stable.getSize(),0)
    self.assertEqual(stable.getStableSize(),0)
    self.assertEqual(stable.isFullyLoaded(),False) 
    self.assertEqual(stable.isEmpty(),True) 
    self.assertEqual(stable.getTradableAssetsSize(),0) 

    self.assertEqual(stable.getAverageBullCostBasis(),0)
    self.assertEqual(stable.getAverageBearCostBasis(),0)
    self.assertEqual(stable.getLowestBullCostBasis(),None)
    self.assertEqual(stable.getLowestBearCostBasis(),None)
    self.assertEqual(stable.getHighestBullCostBasis(),None)
    self.assertEqual(stable.getHighestBearCostBasis(),None)

    self.assertEqual(stable.getBestPerformingBullInStage(),None)
    self.assertEqual(stable.getBestPerformingBearInStage(),None)
    self.assertEqual(stable.getBestPerformingBullValue(),None)    
    self.assertEqual(stable.getBestPerformingBearValue(),None)     
    self.assertEqual(stable.getTheLeastExpensiveBullEntry(),None)
    self.assertEqual(stable.getTheLeastExpensiveBearEntry(),None) 
    self.assertEqual(stable.getWorstPerformingBearInStage(),None)    
    self.assertEqual(stable.getWorstPerformingBullInStage(),None)    
    self.assertEqual(stable.getTheMostExpensiveBullEntry(),None)
    self.assertEqual(stable.getTheMostExpensiveBearEntry(),None)

    self.assertEqual(stable.getOldestStageRoundtripEntry(),None)
    self.assertEqual(stable.getYoungestStageRoundtripEntry(),None)
    self.assertEqual(stable.getTimeEllapsedSinceOldestAcquisition(),None)
    self.assertEqual(stable.getTimeEllapsedSinceYoungestAcquisition(),None)
    self.assertEqual(stable.getAgeDifferenceBetweenOldestAndYoungestInStage(),None)

  #@unittest.skip("Taking a break now")
  def testBasicGroupInformation(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    stable = robot_0.getStableRoundTrips()
    self.assertEqual(stable.getAllStableEntries(),[])
    self.assertEqual(stable.getAllStableEntriesByAgeOldestFirst(),[])
    self.assertEqual(stable.getAllStableEntriesByAgeYoungestFirst(),[])  
    self.assertEqual(stable.getAllStableEntriesByBullPrice(),[])    
    self.assertEqual(stable.getAllStableEntriesByBearPrice(),[])    
    self.assertEqual(stable.getAllStableEntriesByBearCostBasis(),[])     
    self.assertEqual(stable.getAllStableEntriesByBullCostBasis(),[])    
    self.assertEqual(stable.getAllStableEntriesByBullValue(),[])     
    self.assertEqual(stable.getAllStableEntriesByBearValue(),[])    

  #@unittest.skip("Taking a break now")
  def testBasicFinancialInformation(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    stable = robot_0.getStableRoundTrips()
    self.assertEqual(stable.getAverageBullPrice(),00)
    self.assertEqual(stable.getAverageBearPrice(),00) 
    self.assertEqual(stable.getSpreadBullPrice(),00)
    self.assertEqual(stable.getSpreadBearPrice(),00)
    self.assertEqual(stable.getTotalCostBasis(),00)
    self.assertEqual(stable.getSpreadBearPrice(),00)
    self.assertEqual(round(stable.getTotalBearCostBasis(),2),0)
    self.assertEqual(round(stable.getTotalBullCostBasis(),2),0)
    self.assertEqual(stable.getNumberOfAssetsAcquiredWithinTimeframe(timeframe=15),0) 
    self.assertEqual(stable.isBullToBearCostBasisWithinRatioPercentage(ratio_percent=10), None)

  #@unittest.skip("Taking a break now")
  def testAssetsWithinRangesNumbersRobot(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    stable = robot_0.getStableRoundTrips()
    #type_used,rule_used,number_bull,number_bear
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number',rule_used='bull',number_bull=0.1,number_bear=.51),False)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number',rule_used='bear',number_bull=0.2,number_bear=.45),False)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number',rule_used='both',number_bull=0.3,number_bear=.25),False)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number',rule_used='either',number_bull=0.4,number_bear=.55),False)

    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number_profit',rule_used='bull',number_bull=0.1,number_bear=.51),False)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number_profit',rule_used='bear',number_bull=0.2,number_bear=.45),False)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number_profit',rule_used='both',number_bull=0.3,number_bear=.25),False)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number_profit',rule_used='either',number_bull=0.4,number_bear=.55),False)

  #@unittest.skip("Taking a break now")
  def testAssetsWithinRangesPercentagesRobot(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    stable = robot_0.getStableRoundTrips()
    #type_used,rule_used,number_bull,number_bear
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='percentage_stock',rule_used='bull',number_bull=0.1,number_bear=.51),False)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='percentage_stock',rule_used='bear',number_bull=0.2,number_bear=.45),False)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='percentage_stock',rule_used='both',number_bull=0.3,number_bear=.25),False)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='percentage_stock',rule_used='either',number_bull=0.4,number_bear=.55),False)

    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='percentage_profit',rule_used='bull',number_bull=0.1,number_bear=.51),False)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='percentage_profit',rule_used='bear',number_bull=0.2,number_bear=.45),False)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='percentage_profit',rule_used='both',number_bull=0.3,number_bear=.25),False)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='percentage_profit',rule_used='either',number_bull=0.4,number_bear=.55),False)

  #@unittest.skip("Taking a break now")
  def testAssetsWithinTimeInterval(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    stable = robot_0.getStableRoundTrips()
    self.assertEqual(stable.isAssetToPurchaseWithinTimeRangeByNumber(time_interval=10),False)      


  #@unittest.skip("Taking a break now")
  def testUIReporting(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    stable = robot_0.getStableRoundTrips()
    stable_summary = robot_0.getStableReport()['summary_data']
    stable_content = robot_0.getStableReport()['content_data']
    self.assertEqual(stable_summary['stable_size'],0) 
    self.assertEqual(len(stable_content),0) 
    #self.assertEqual(stable.getStableReport(),False)

  #@unittest.skip("Taking a break now")
  def testCommandLineReporting(self):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    stable = robot_0.getStableRoundTrips()
    #TODO: No data structure for this yet !!!

#####################################################################################################
#
# One StableRoundTrip class . Adding data continously until it reaches max
#@unittest.skip("Taking a break now")
class AddingUpToFourEntries(TestCase):
  base_name = 'testme'
  description = 'description'
  max_roundtrips = 20
  etf = 'QQQ'
  bullish = 'TQQQ'
  bearish = 'SQQQ'
  cost_basis_per_roundtrip = 1500
  initial_budget = 100000
  profit_basis_per_roundtrip = 100
  bull_prices=[124.0,125.0,125.45,126.10,126.12]
  bear_prices=[29.0,28.5,28.00,27.65,27.64]
  current_times=['2020-08-03 04:05:00-04:00','2020-08-03 09:05:00-04:00','2020-08-03 11:15:00-04:00',
                 '2020-08-03 11:45:00-04:00','2020-08-03 11:49:24-04:00']
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
    budget_management = RobotBudgetManagement.objects.create(pair_robot=robot1,max_budget_per_purchase_number=self.cost_basis_per_roundtrip,
                                                             use_percentage_or_fixed_value='Number')



  def getTradeInformation(self,index):
    information = dict()
    information[self.bullish]=self.bull_prices[index]
    information[self.bearish]=self.bear_prices[index] 
    information['timestamp'] = self.current_times[index]
    return information 

  def loadData(self,count):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    index = 0
    for n in self.current_times:
      payload = self.getTradeInformation(index=index)
      self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
      if index < count:
        robot_0.addNewRoundtripEntry()
      index +=1


  #@unittest.skip("Taking a break now")
  def testRoundtripBasicRobot(self):
    self.loadData(count=4)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    index=4
    payload = self.getTradeInformation(index=index)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 

    #robot_0.addNewRoundtripEntry()
    stable = robot_0.getStableRoundTrips()
    self.assertEqual(stable.getSize(),index)
    self.assertEqual(stable.getStableSize(),index)
    self.assertEqual(stable.getTradableAssetsSize(),0) #All assets were added today 
    self.assertEqual(stable.isFullyLoaded(),False)
    self.assertEqual(stable.isEmpty(),False) 

    self.assertEqual(round(stable.getAverageBullCostBasis(),2),750.82)
    self.assertEqual(round(stable.getAverageBearCostBasis(),2),749.39)
    self.assertEqual(stable.getLowestBullCostBasis().getBullBuyPrice(),124)
    self.assertEqual(stable.getLowestBearCostBasis().getBearBuyPrice(),28.5)
    self.assertEqual(stable.getHighestBullCostBasis().getBullBuyPrice(),126.10)
    self.assertEqual(stable.getHighestBearCostBasis().getBearBuyPrice(),28)
    #stable.printEntries()

    self.assertEqual(round(stable.getBestPerformingBullInStage().getStableBullValue(),2),12.72)
    self.assertEqual(round(stable.getBestPerformingBearInStage().getStableBullValue(),2),.12)
    self.assertEqual(round(stable.getBestPerformingBullValue().getStableBullValue(),2),12.72)    
    self.assertEqual(round(stable.getBestPerformingBearValue().getStableBullValue(),2),.12)     
    self.assertEqual(stable.getTheLeastExpensiveBullEntry().getBullBuyPrice(),124)
    self.assertEqual(stable.getTheLeastExpensiveBearEntry().getBearBuyPrice(),27.65) 
    self.assertEqual(round(stable.getWorstPerformingBearInStage().getStableBearValue(),2),-35.36)    
    self.assertEqual(round(stable.getWorstPerformingBullInStage().getStableBullValue(),2),.12)    
    self.assertEqual(round(stable.getTheMostExpensiveBullEntry().getBullBuyPrice(),2),126.1)
    self.assertEqual(round(stable.getTheMostExpensiveBearEntry().getBearBuyPrice(),2),29)

    self.assertEqual(stable.getTimeEllapsedSinceOldestAcquisition().getTimeSincePurchase(),464.4)
    self.assertEqual(stable.getTimeEllapsedSinceYoungestAcquisition().getTimeSincePurchase(),4.4)
    self.assertEqual(stable.getAgeDifferenceBetweenOldestAndYoungestInStage(),460)
    self.assertEqual(stable.getOldestStageRoundtripEntry().getBullBuyDate(),strToDatetime(self.current_times[0]))
    self.assertEqual(stable.getYoungestStageRoundtripEntry().getBullBuyDate(),strToDatetime(self.current_times[index-1]))

  #@unittest.skip("Taking a break now")
  def testBasicFinancialInformation(self):
    self.loadData(count=4)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    payload = self.getTradeInformation(index=4)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[4]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[4]) 

    #robot_0.addNewRoundtripEntry()   
    stable = robot_0.getStableRoundTrips()
    self.assertEqual(stable.getSize(),4)
    self.assertEqual(round(stable.getAverageBullPrice(),2),125.14)
    self.assertEqual(round(stable.getAverageBearPrice(),2),28.29) 

    self.assertEqual(round(stable.getSpreadBullPrice(),2),2.10)
    self.assertEqual(round(stable.getSpreadBearPrice(),2),1.35)
    self.assertEqual(round(stable.getSpreadPercentToMaxBullPrice(),2),1.67)
    self.assertEqual(round(stable.getSpreadPercentToMaxBearPrice(),2),4.66)
    self.assertEqual(round(stable.getSpreadPercentToMinBullPrice(),2),1.69)
    self.assertEqual(round(stable.getSpreadPercentToMinBearPrice(),2),4.88)
    self.assertEqual(round(stable.getSpreadPercentToAverageBearPrice(),2),4.77)
    self.assertEqual(round(stable.getSpreadPercentToAverageBullPrice(),2),1.68)

    self.assertEqual(stable.getTotalCostBasis(),6000.85)
    self.assertEqual(round(stable.getSpreadBearPrice(),2),1.35)
    self.assertEqual(round(stable.getTotalBearCostBasis(),2),2997.55)
    self.assertEqual(round(stable.getTotalBullCostBasis(),2),3003.3)
    self.assertEqual(stable.getNumberOfAssetsAcquiredWithinTimeframe(timeframe=15),1) 
    self.assertEqual(stable.isBullToBearCostBasisWithinRatioPercentage(ratio_percent=1), True)

  #@unittest.skip("Taking a break now")
  def testAssetsWithinRangesNumbersRobot(self):
    self.loadData(count=4)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    payload = self.getTradeInformation(index=4)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[4]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[4]) 

    #robot_0.addNewRoundtripEntry()
    stable = robot_0.getStableRoundTrips()
    self.assertEqual(stable.getSize(),4)
    
    #Bull Price [124.0,125.0,125.45,126.10] Current:[126.12] (.02)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number',rule_used='bull',number_bull=0.01,number_bear=.51),False) #[],
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number',rule_used='bull',number_bull=0.02,number_bear=.51),False) #[],
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number',rule_used='bull',number_bull=0.03,number_bear=.51),True) #[],
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number',rule_used='bull',number_bull=0.20,number_bear=.51),True) #[],

    #Bear Prices=[29.0,28.5,28.00,27.65] Current: [27.64] (.01)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number',rule_used='bear',number_bear=.005,number_bull=0.2),False)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number',rule_used='bear',number_bear=.45,number_bull=0.2),True)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number',rule_used='bear',number_bear=.45,number_bull=0.2),True)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number',rule_used='bear',number_bear=.45,number_bull=0.2),True)

    #See data from both above    
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number',rule_used='both',number_bull=0.01,number_bear=.025),False)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number',rule_used='both',number_bull=0.03,number_bear=.45),True)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number',rule_used='both',number_bull=0.01,number_bear=.45),False)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number',rule_used='both',number_bull=0.3,number_bear=.25),True)

    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number',rule_used='either',number_bull=0.4,number_bear=.55),True)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number',rule_used='either',number_bull=0.01,number_bear=.045),True)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number',rule_used='either',number_bull=0.4,number_bear=.55),True)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number',rule_used='either',number_bull=0.004,number_bear=.0055),False)

  #@unittest.skip("Taking a break now")
  def testWithinNumberOfProfitTarget(self):
    self.loadData(count=4)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    payload = self.getTradeInformation(index=4)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[4]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[4]) 
    
    stable = robot_0.getStableRoundTrips()
    self.assertEqual(stable.getSize(),4)
    #TODO: Fix later
    index = 'TODO'
    if index !='TODO':
      self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number_profit',rule_used='bull',number_bull=0.1,number_bear=.51),False)
      self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number_profit',rule_used='bear',number_bull=0.2,number_bear=.45),False)
      self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number_profit',rule_used='both',number_bull=0.3,number_bear=.25),False)
      self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='number_profit',rule_used='either',number_bull=0.4,number_bear=.55),False)


  #@unittest.skip("Taking a break now")
  def testWithinPercentagesOfStockPrice(self):
    self.loadData(count=4)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    payload = self.getTradeInformation(index=4)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[4]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[4]) 

    stable = robot_0.getStableRoundTrips()
    self.assertEqual(stable.getSize(),4)

    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='percentage_stock',rule_used='bull',number_bull=.016,number_bear=.51),True)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='percentage_stock',rule_used='bull',number_bull=.011,number_bear=.51),False)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='percentage_stock',rule_used='bull',number_bull=.002,number_bear=.51),False)

    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='percentage_stock',rule_used='bear',number_bull=0.2,number_bear=.45),True)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='percentage_stock',rule_used='both',number_bull=0.3,number_bear=.25),True)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='percentage_stock',rule_used='either',number_bull=0.4,number_bear=.55),True)

  #@unittest.skip("Taking a break now")
  def testWithinPercentagesOfProfitPrice(self):
    self.loadData(count=4)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    payload = self.getTradeInformation(index=4)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[4]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[4]) 

    stable = robot_0.getStableRoundTrips()
    self.assertEqual(stable.getSize(),4)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='percentage_profit',rule_used='bull',number_bull=0.1,number_bear=.51),True)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='percentage_profit',rule_used='bear',number_bull=0.2,number_bear=.45),True)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='percentage_profit',rule_used='both',number_bull=0.3,number_bear=.25),True)
    self.assertEqual(stable.isAssetToBuyWithinPriceRange(type_used='percentage_profit',rule_used='either',number_bull=0.4,number_bear=.55),True)

  #@unittest.skip("Taking a break now")
  def testAssetsWithinTimeInterval(self):
    self.loadData(count=4)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    payload = self.getTradeInformation(index=4)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[4]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[4]) 
    stable = robot_0.getStableRoundTrips()
    self.assertEqual(stable.getSize(),4)
    self.assertEqual(stable.isAssetToPurchaseWithinTimeRangeByNumber(time_interval=4),False)      
    self.assertEqual(stable.isAssetToPurchaseWithinTimeRangeByNumber(time_interval=6),True)      
    self.assertEqual(stable.isAssetToPurchaseWithinTimeRangeByNumber(time_interval=7),True)      

  #@unittest.skip("Taking a break now")
  def testUIReporting(self):
    self.loadData(count=4)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=4)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[4]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[4]) 
    stable = robot_0.getStableRoundTrips()
    self.assertEqual(stable.getSize(),4)
    stable_summary = robot_0.getStableReport()['summary_data']
    stable_content = robot_0.getStableReport()['content_data']
    self.assertEqual(stable_summary['stable_size'],4) 
    self.assertEqual(len(stable_content),4) 
    #self.assertEqual(stable.getStableReport(),False)

  #@unittest.skip("Taking a break now")
  def testCommandLineReporting(self):
    self.loadData(count=4)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    payload = self.getTradeInformation(index=4)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[4]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[4]) 
    stable = robot_0.getStableRoundTrips()
    self.assertEqual(stable.getSize(),4)
    #TODO: No data structure for this yet !!!



#####################################################################################################
#
# AddingUpToFiftyEntries: Adding a large number of data and make sure the system can handl it
#
#
#@unittest.skip("Taking a break now")
class AddingUpToFiftyEntries(TestCase):
  base_name = 'testme'
  description = 'description'
  max_roundtrips = 20
  etf = 'OIL'
  bullish = 'SCO'
  bearish = 'UCO'
  cost_basis_per_roundtrip = 1500
  initial_budget = 100000
  profit_basis_per_roundtrip = 50
  bull_prices=[16.29,16.31,16.41,16.34,16.23, 16.18,16.37,16.49,16.55,16.35, 16.29,16.31,16.41,16.34,16.23, 16.18,16.37,16.49,16.55,16.35]
  bear_prices=[31.44,31.40,31.29,31.26,31.19, 31.42,31.20,31.39,31.26,31.09, 31.42,31.45,32.29,33.26,30.19, 31.14,91.40,31.49,31.16,31.10]
  current_times=['2020-08-03 04:05:00-04:00','2020-08-03 09:05:00-04:00','2020-08-03 11:15:00-04:00','2020-08-03 11:16:00-04:00',
                 '2020-08-03 11:45:00-04:00','2020-08-03 11:49:24-04:00','2020-08-03 11:55:00-04:00','2020-08-03 13:15:00-04:00',
                 '2020-08-04 10:45:00-04:00','2020-08-04 10:40:24-04:00','2020-08-04 11:55:00-04:00','2020-08-04 14:15:00-04:00',
                 '2020-08-05 09:45:00-04:00','2020-08-05 11:29:24-04:00','2020-08-05 11:35:03-04:00','2020-08-05 13:15:00-04:00',
                 '2020-08-05 15:55:00-04:00','2020-08-05 15:56:00-04:00','2020-08-05 15:56:30-04:00','2020-08-05 15:57:00-04:00']
  internal_name='foumban'

  @classmethod 
  def setUpTestData(self):
    nasdaq=RobotEquitySymbols.objects.create(name='Nasdaq',symbol=self.etf,bullishSymbol=self.bullish,bearishSymbol=self.bearish)
    robot1=ETFAndReversePairRobot.objects.create(name=self.base_name,description=self.description,
            portfolio=None,strategy=None,symbols=nasdaq,enabled=True,owner=None,visibility=True,
            version='1.0.0', max_hold_time='14',minimum_hold_time='0',hold_time_includes_holiday=True,
            sell_remaining_before_buy=False,liquidate_on_next_opportunity=False,internal_name=self.internal_name,
            max_roundtrips=self.max_roundtrips,cost_basis_per_roundtrip=self.cost_basis_per_roundtrip,
            profit_target_per_roundtrip=self.profit_basis_per_roundtrip)    
    self.robot_0_id =robot1.pk
    sentiment_0 = EquityAndMarketSentiment.objects.create(pair_robot=robot1,influences_acquisition=True,circuit_breaker=False,
                                                          sentiment_feed='Automatic')
 
    self.s0_id = sentiment_0.pk
    budget_management = RobotBudgetManagement.objects.create(pair_robot=robot1,max_budget_per_purchase_number=self.cost_basis_per_roundtrip,
                                                             use_percentage_or_fixed_value='Number')



  def getTradeInformation(self,index):
    information = dict()
    information[self.bullish]=self.bull_prices[index]
    information[self.bearish]=self.bear_prices[index] 
    information['timestamp'] = self.current_times[index]
    return information 

  def loadData(self,count):
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    index = 0
    for n in self.current_times:
      payload = self.getTradeInformation(index=index)
      self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
      if index < count:
        robot_0.addNewRoundtripEntry()
      index +=1


  #@unittest.skip("Taking a break now")
  def testRoundtripBasicRobot(self):
    self.loadData(count=19)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    index=19
    payload = self.getTradeInformation(index=index)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 

    #robot_0.addNewRoundtripEntry()
    stable = robot_0.getStableRoundTrips()
    self.assertEqual(stable.getSize(),19)
    self.assertEqual(stable.getStableSize(),19)
    self.assertEqual(stable.getTradableAssetsSize(),19) 
    self.assertEqual(stable.isFullyLoaded(),False)
    self.assertEqual(stable.isEmpty(),False) 

    self.assertEqual(round(stable.getAverageBullCostBasis(),2),748.72)
    self.assertEqual(round(stable.getAverageBearCostBasis(),2),750.74)
    self.assertEqual(stable.getLowestBullCostBasis().getBullCostBasis(),742.05)
    self.assertEqual(stable.getLowestBearCostBasis().getBearCostBasis(),731.20)
    self.assertEqual(stable.getHighestBullCostBasis().getBullCostBasis(),754.86)
    self.assertEqual(round(stable.getHighestBearCostBasis().getBearCostBasis(),2),764.98)

  #@unittest.skip("Taking a break now")
  def testRoundtripEqualsAndContainedIn(self):
    self.loadData(count=19)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    index=19
    payload = self.getTradeInformation(index=index)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 

    #robot_0.addNewRoundtripEntry()
    stable = robot_0.getStableRoundTrips()
    self.assertEqual(stable.getSize(),19)
    self.assertEqual(stable.getStableSize(),19)
    self.assertEqual(stable.getTradableAssetsSize(),19) 
    self.assertEqual(stable.isFullyLoaded(),False)
    self.assertEqual(stable.isEmpty(),False) 

    youngest = stable.getAllStableEntriesByAgeYoungestFirst()
    youngest0 = youngest[0]

    youngest = stable.getAllStableEntriesByAgeYoungestFirst()
    youngest0 = youngest[0]
    self.assertEqual(youngest[0].equalsRoundtrip(candidate=youngest[0]),True)
    self.assertEqual(youngest[3].equalsRoundtrip(candidate=youngest[3]),True)
    self.assertEqual(youngest[2].equalsRoundtrip(candidate=youngest[2]),True)
    self.assertEqual(youngest[5].equalsRoundtrip(candidate=youngest[5]),True)

    self.assertEqual(youngest[0].equalsRoundtrip(candidate=None),False)
    self.assertEqual(youngest[3].equalsRoundtrip(),False)

    self.assertEqual(youngest[0].equalsRoundtrip(candidate=youngest[1]),False)
    self.assertEqual(youngest[3].equalsRoundtrip(candidate=youngest[2]),False)
    self.assertEqual(youngest[2].equalsRoundtrip(candidate=youngest[4]),False)
    self.assertEqual(youngest[5].equalsRoundtrip(candidate=youngest[6]),False)

    self.assertEqual(youngest[0].containedInRoundtrips(roundtrip_list=youngest[1:10]),False)
    self.assertEqual(youngest[0].containedInRoundtrips(roundtrip_list=youngest[0:10]),True)
    self.assertEqual(youngest[5].containedInRoundtrips(roundtrip_list=youngest[1:10]),True)
    self.assertEqual(youngest[12].containedInRoundtrips(roundtrip_list=youngest[0:10]),False)

    self.assertEqual(youngest[12].containedInRoundtrips(roundtrip_list=None),False)
    self.assertEqual(youngest[12].containedInRoundtrips(),False)
    self.assertEqual(youngest[12].containedInRoundtrips(roundtrip_list=[youngest[12]]),True)

    
  #@unittest.skip("Taking a break now")
  def testRoundtripWinningBullsAndBears(self):
    self.loadData(count=19)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    index=19
    payload = self.getTradeInformation(index=index)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 

    #robot_0.addNewRoundtripEntry()
    stable = robot_0.getStableRoundTrips()
    self.assertEqual(stable.getSize(),19)
    self.assertEqual(stable.getStableSize(),19)
    self.assertEqual(stable.isFullyLoaded(),False)
    self.assertEqual(stable.isEmpty(),False) 

    winning_bulls = stable.getStableWinningBulls()
    self.assertEqual(len(winning_bulls),1)

    winning_bulls_5 = stable.getStableWinningBulls(count=5)
    self.assertEqual(len(winning_bulls_5),5)
    self.assertTrue(winning_bulls_5[0].getStableBullValue()>=winning_bulls_5[1].getStableBullValue())
    self.assertTrue(winning_bulls_5[1].getStableBullValue()>=winning_bulls_5[2].getStableBullValue())
    self.assertTrue(winning_bulls_5[2].getStableBullValue()>=winning_bulls_5[3].getStableBullValue())
    self.assertTrue(winning_bulls_5[3].getStableBullValue()>=winning_bulls_5[4].getStableBullValue())
    
    self.assertFalse(winning_bulls_5[4].getStableBullValue()>=winning_bulls_5[0].getStableBullValue())

    winning_bears_7 = stable.getStableWinningBears(count=7)
    self.assertEqual(len(winning_bears_7),7)
    self.assertTrue(winning_bears_7[0].getStableBearValue()>=winning_bears_7[1].getStableBearValue())
    self.assertTrue(winning_bears_7[1].getStableBearValue()>=winning_bears_7[2].getStableBearValue())
    self.assertTrue(winning_bears_7[2].getStableBearValue()>=winning_bears_7[3].getStableBearValue())
    self.assertTrue(winning_bears_7[3].getStableBearValue()>=winning_bears_7[4].getStableBearValue())

    self.assertFalse(winning_bears_7[4].getStableBearValue()>=winning_bears_7[0].getStableBearValue())


    #Test Reversing the order of the winners. Least performers first
    winning_bulls_best_false = stable.getStableWinningBulls(count=5,best=False)
    self.assertEqual(len(winning_bulls_best_false),5)
    self.assertTrue(winning_bulls_best_false[0].getStableBullValue()<=winning_bulls_best_false[1].getStableBullValue())
    self.assertTrue(winning_bulls_best_false[1].getStableBullValue()<=winning_bulls_best_false[2].getStableBullValue())
    self.assertTrue(winning_bulls_best_false[2].getStableBullValue()<=winning_bulls_best_false[3].getStableBullValue())
    self.assertTrue(winning_bulls_best_false[3].getStableBullValue()<=winning_bulls_best_false[4].getStableBullValue())
    
    self.assertFalse(winning_bulls_best_false[4].getStableBullValue()<=winning_bulls_best_false[0].getStableBullValue())


    winning_bears_best_false = stable.getStableWinningBears(count=7,best=False)
    self.assertEqual(len(winning_bears_best_false),7)
    self.assertTrue(winning_bears_best_false[0].getStableBearValue()<=winning_bears_best_false[1].getStableBearValue())
    self.assertTrue(winning_bears_best_false[1].getStableBearValue()<=winning_bears_best_false[2].getStableBearValue())
    self.assertTrue(winning_bears_best_false[2].getStableBearValue()<=winning_bears_best_false[3].getStableBearValue())
    self.assertTrue(winning_bears_best_false[3].getStableBearValue()<=winning_bears_best_false[4].getStableBearValue())

    self.assertFalse(winning_bears_best_false[4].getStableBearValue()<=winning_bears_best_false[0].getStableBearValue())

    #Test Returning more than contained in the Set (set has 19, requesting 50. Only 19 will be returned).
    winning_bulls_too_many = stable.getStableWinningBulls(count=50,best=False)
    self.assertFalse(len(winning_bulls_too_many)==50)
    self.assertEqual(len(winning_bulls_too_many),19)

    winning_bears_too_many = stable.getStableWinningBears(count=50,best=False)
    self.assertFalse(len(winning_bears_too_many)==50)
    self.assertEqual(len(winning_bears_too_many),19)

    #Test Excluding using exclude_list.    First: Exclude everything from the set.
    winning_bulls_to_exclude1 = stable.getStableWinningBulls(count=50)
    self.assertFalse(len(winning_bulls_to_exclude1)==50)
    self.assertEqual(len(winning_bulls_to_exclude1),19)
    winning_bears_with_exclude1 = stable.getStableWinningBears(count=50,exclude_list=winning_bulls_to_exclude1)
    self.assertTrue(len(winning_bears_with_exclude1)==0)
    #self.assertEqual(len(winning_bears_too_many),19)

    #Test Excluding using exclude_list.    First: Exclude everything from the set.
    winning_bulls_to_exclude2 = stable.getStableWinningBulls(count=10)
    self.assertEqual(len(winning_bulls_to_exclude2),10)

    winning_bears_with_exclude2 = stable.getStableWinningBears(count=10,exclude_list=winning_bulls_to_exclude2)
    self.assertTrue(len(winning_bears_with_exclude2)==9)

    #Validate that NO Roundtrip is in both lists.
    for x in winning_bears_with_exclude2:
      for y in winning_bulls_to_exclude2:
        self.assertEqual(x.equalsRoundtrip(y),False)

if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)
