import datetime, time
import logging, unittest
import sys,json,xmlrunner
from django.utils import timezone
from django.test import TestCase

# Import Models
from bullbearetfs.robot.models import ETFAndReversePairRobot,TradeDataHolder, RoundTrip, StartupStatus
from bullbearetfs.utilities.orders import RobotSellOrderExecutor, RobotBuyOrderExecutor
from bullbearetfs.utilities.alpaca import AlpacaLastTrade
from bullbearetfs.strategy.models import EquityStrategy, AcquisitionPolicy,DispositionPolicy,OrdersManagement,PortfolioProtectionPolicy
from bullbearetfs.brokerages.models import BrokerageInformation
from bullbearetfs.robot.budget.models import Portfolio,RobotBudgetManagement
from bullbearetfs.robot.symbols.models import RobotEquitySymbols, BullBearETFData
from bullbearetfs.robot.activitysentiments.models import EquityAndMarketSentiment,RobotActivityWindow, MarketBusinessHours

logger = logging.getLogger(__name__)

#
# Dummy function needed to force rebuild on change.
#
def test_robots_dummy(request):
  pass

##############################################################################################
# This class tests the functionality of the CORE Robot functions.
#
# Tests the functionality around:
#    Basic Robot Information Page.
#    Ability to navigate the conditionals
#    Several robots running at the same time.
#    Status: Incomplete
#     -BasicRobotWithNoTradeDataTestCase: Basic class with very minimal data
#     -BasicRobotWithOneBuyTestCase: Uses Conditional to determin purchase decision. INCOMPLETE
#     -BasicRobotWithOneBuyOneSaleTestCase: INCOMPLETE
#     -TwoBasicRobotWithNoTradeDataTestCase: INCOMPLETE
#     -MoreThan5TradingRobotsTestCase: INCOMPLETE
#    Number of Test Classes Planned: 5
#    Total Number of Test Functions: 
#    Number of remaining Classes:
##############################################################################################

#
# This test case covers the creation of a new Class Instance of the Robot.
# There is no trading data at this point. Most of the methods should still return valid 
# and expected values
#
#@unittest.skip("Taking a break now")
class BasicRobotWithNoTradeDataTestCase(TestCase):
  base_name = 'testme'
  max_roundtrips = '10'
  etf = 'QQQ'
  bullish = 'TQQQ'
  bearish = 'SQQQ'
  cost_basis_per_roundtrip = 2000
  initial_budget = 100000
  profit_per_roundtrip = 100
  description='This is my description'
  now=datetime.datetime.now(timezone.utc)
  profit_basis_per_roundtrip=10
  internal_name='egghead'
  strategy_name='Batcham Strategy on ETrade'
  strategy_category='Batcham'
  strategy_class = 'Bullish Bearish'
  s_bull_bear_0 = ['3x Bearish','2x Bearish','1x Bearish','3x Bearish']
  s_bull_bear_weight_0 = [100,50,100,100]

  @classmethod 
  def setUpTestData(self):
    alpaca = BrokerageInformation.objects.create(brokerage_type='Alpaca',name='Alpaca Brokerate',website='https://alpaca.markets/')

    eTrade = Portfolio.objects.create(name='ETrade',initial_cash_funds=100000,current_cash_funds=100000,brokerage_id=alpaca.id,
      max_robot_fraction=.10,cash_position_update_policy='immediate',description='ETrade Portfolio description')
    
    babadjou = EquityStrategy.objects.create(strategy_class=self.strategy_class,strategy_category=self.strategy_category,name=self.strategy_name,description='Strategy description here',
                                           visibility=True,automatic_generation_client_order_id=True,
                                            minimum_entries_before_trading=4,trade_only_after_fully_loaded=False,
                                             manual_asset_composition=True)

    acquisition = AcquisitionPolicy.objects.create(acquisition_time_proximity=True,min_time_between_purchases=5,
      acquisition_volume_proximity=False, min_volume_between_purchases=0, volume_fraction_to_average=0,
      acquisition_price_proximity=True,proximity_calculation_automatic=True, simultaneous_bull_bear_acquisitions=True,
      strategy_id=babadjou.id)

    disposition = DispositionPolicy.objects.create(strategy_id=babadjou.id)

    protection = PortfolioProtectionPolicy.objects.create(strategy_id=babadjou.id)

    orders = OrdersManagement.objects.create(strategy_id=babadjou.id)

    nasdaq=RobotEquitySymbols.objects.create(name='Nasdaq',symbol='QQQ',bullishSymbol='TQQQ',bearishSymbol='SQQQ')

    robot1=ETFAndReversePairRobot.objects.create(name=self.base_name,description=self.description,
            portfolio=eTrade,strategy=babadjou,symbols=nasdaq,enabled=True,owner=None,visibility=True,
            version='1.0.0',creation_date=self.now, max_hold_time='14',minimum_hold_time='1',hold_time_includes_holiday=True,
            sell_remaining_before_buy=False,liquidate_on_next_opportunity=False,internal_name=self.internal_name,
            max_roundtrips=self.max_roundtrips,cost_basis_per_roundtrip=self.cost_basis_per_roundtrip,
            profit_target_per_roundtrip=self.profit_basis_per_roundtrip)
    
    self.robot_0_id =robot1.pk


    #TODO: commented out. MarketBusinessHours.updateTodayBusinessHours(isOpen=True)
    #Regular/Typical trading day
    typical_market = RobotActivityWindow.objects.create(trade_before_open=False,trade_after_close=False,trade_during_extended_opening_hours=False,
      offset_after_open='0',offset_before_close='0',blackout_midday_from='0',blackout_midday_time_interval='0',
      pair_robot_id=robot1.id)

    self.win1=typical_market.pk

    sentiment_0 = EquityAndMarketSentiment.objects.create(pair_robot=robot1,influences_acquisition=True,circuit_breaker=False,sentiment_feed='Automatic',
            external_sentiment=self.s_bull_bear_0[0], market_sentiment=self.s_bull_bear_0[1], sector_sentiment=self.s_bull_bear_0[2], equity_sentiment=self.s_bull_bear_0[3],
      external_sentiment_weight=self.s_bull_bear_weight_0[0],market_sentiment_weight=self.s_bull_bear_weight_0[1],sector_sentiment_weight=self.s_bull_bear_weight_0[2],
      equity_sentiment_weight=self.s_bull_bear_weight_0[3])
 
    self.s0_id = sentiment_0.pk

    budget_management = RobotBudgetManagement.objects.create(pair_robot=robot1,use_percentage_or_fixed_value='Number')
     
     #Roundtrip functions
     #Buy & Sell Conditions (that defer to components
  #@unittest.skip("Taking a break now")
  def testEntryPointApplicationOnEmptyRobot(self):
    robot_0 = self.getTradingRobot(name=self.base_name)
    valid_key='{"current_bull_price":120,"current_bear_price":25,"current_timestamp":""}'
    empty_key='{""}'
    invalid_key_missing_bull='{"current_bull_1price":120,"current_bear_price":25,"current_timestamp":""}'
    invalid_key_missing_bear='{"current_bull_price":120,"current_bear1_price":25,"current_timestamp":""}'
    invalid_key_missing_time='{"current_bull_1price":120,"current_bear_price":25,"current_timestamp":""}'

    #Validate that the Robot is Enabled. 
    self.assertEqual(robot_0.isEnabled(),True)
    #Disable it first.
    robot_0.toggleEnabled()
    self.assertEqual(robot_0.prepareTrades(key=valid_key),-1)

    #Enable the Robot.
    robot_0.toggleEnabled()
    self.assertEqual(robot_0.prepareTrades(key=empty_key),-1)

    self.assertEqual(robot_0.prepareTrades(key=invalid_key_missing_bull),-1)
    self.assertEqual(robot_0.prepareTrades(key=invalid_key_missing_bear),-1)
    self.assertEqual(robot_0.prepareTrades(key=invalid_key_missing_time),-1)

  #@unittest.skip("Taking a break now")
  def testEventRecordingOnEmptyRobot(self):
    robot_0 = self.getTradingRobot(name=self.base_name)
    robot_0.toggleEnabled()
    robot_0.toggleEnabled()
    entries = StartupStatus.getNumberOfEvents(robot_id=robot_0.pk)
    self.assertEqual(entries,2)

  #@unittest.skip("Taking a break now")
  def testSymbolsInformationOnEmptyRobot(self):
    robot_0 = self.getTradingRobot(name=self.base_name)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),0) 
    self.assertEqual(robot_0.getCurrentBearPrice(),0) 
    self.assertTrue(robot_0.getCurrentTimestamp()<self.now) 

  #@unittest.skip("Taking a break now")
  def testBasicConfigurationEmptyRobot(self):
    robot_0 = self.getTradingRobot(name=self.base_name)
    self.assertEqual(robot_0.getMaxNumberOfRoundtrips(),int(self.max_roundtrips)) 
    self.assertEqual(robot_0.getMaximumAssetHoldTime(),'14') 
    self.assertEqual(robot_0.getMinimumAssetHoldTime(),'1') 
    self.assertEqual(robot_0.getMinHoldTimeInMinutes(),int('1')*24*60) 
    self.assertEqual(robot_0.getMaxHoldTimeInMinutes(),int('14')*24*60) 
    self.assertEqual(robot_0.shouldRemainingAssetsBeSoldBeforeAnyAcquisition(),False) 
    self.assertEqual(robot_0.shouldLiquidateAssetsAtNextAvailableOpportunity(),False) 
    self.assertEqual(robot_0.getInternalName(),self.internal_name) 
    self.assertEqual(robot_0.isDataSourceLiveFeed(),False) 
    self.assertEqual(robot_0.getRobotSleepTimeBetweenChecks(),'1') 
    self.assertEqual(robot_0.isDataSourceBacktest(),True) 
    self.assertEqual(robot_0.isEnabled(),True) 
    self.assertEqual(robot_0.isVisible(),True) 
    self.assertEqual(robot_0.getRobotVersion(),'1.0.0') 
    self.assertEqual(robot_0.areAllRoundtripsBalanced(),True) 


  #TODO: Improve the result generation
  #@unittest.skip("Taking a break now")
  def testCommandLineReportingOnEmptyRobot(self):
    robot_0 = self.getTradingRobot(name=self.base_name)
    active_costs = robot_0.getAllActiveCosts()
    all_costs = robot_0.getAllCosts()
    self.assertEqual(active_costs['cost_basis'],0)
    self.assertEqual(active_costs['realized'],0)  
    self.assertEqual(active_costs['realized_profits'],0) 
    self.assertEqual(active_costs['unrealized'],0)
    self.assertEqual(all_costs['cost_basis'],0)
    self.assertEqual(all_costs['realized'],0)  
    self.assertEqual(all_costs['realized_profits'],0) 
    self.assertEqual(all_costs['unrealized'],0)


  @unittest.skip("Taking a break now")
  def testUIDataReportingOnEmptyRobot(self):
    robot_0 = self.getTradingRobot(name=self.base_name)
    #print("\nHENRI: {0}".format(robot_0.getStableData()))
    stable_summary = robot_0.getStableReport()['summary_data']
    stable_content = robot_0.getStableReport()['content_data']
    self.assertEqual(stable_summary['stable_size'],0) 
    self.assertEqual(len(stable_content),0) 

    tr_summary = robot_0.getInTransitionReport()['summary_data']
    tr_content = robot_0.getInTransitionReport()['content_data']
    self.assertEqual(tr_summary['intransition_size'],0) 
    self.assertEqual(len(tr_content),0) 

    co_summary = robot_0.getCompletedReport()['summary_data']
    co_content = robot_0.getCompletedReport()['content_data']
    self.assertEqual(co_summary['completed_size'],0) 
    self.assertEqual(len(co_content),0) 

  #@unittest.skip("Taking a break now")
  def testMarketSentimentConfigurationRobot(self):
    robot_0 = self.getTradingRobot(name=self.base_name)
    self.assertEqual(robot_0.getBullishComposition(),30) 
    self.assertEqual(robot_0.getBearishComposition(),70) 
    self.assertEqual(robot_0.getSentimentWindow(),'14') 

  #@unittest.skip("Taking a break now")
  def testBrokerageOrderProcessingFunctionsOnEmptyRobot(self):
    robot_0 = self.getTradingRobot(name=self.base_name)
    self.assertEqual(robot_0.updateOrders(),True)
    #TODO: Add creation of Buy Order
    #TODO: Add creation of Sell Order
    self.assertEqual(robot_0.updateOrders(),True)


  #@unittest.skip("Taking a break now")
  def testStrategyConfigurationOnEmptyRobot(self):
    robot_0 = self.getTradingRobot(name=self.base_name)
    self.assertEqual(robot_0.isBatchamStrategy(),True) 
    self.assertEqual(robot_0.isBabadjouStrategy(),False) 
   
    #TODO: Reorganize these functions.
    #self.assertEqual(robot_0.shouldStartTradeOnlyAfterFullyLoadedStableBox(),False) 
    #self.assertEqual(robot_0.shouldAssetsBeComposedAutomatically(),True) 
    # AcquisitionPolicy, DispositionPolicy, OrdersManagement Protection 
    # RobotCategory

  #@unittest.skip("Taking a break now")
  def testBuyConditionChecksForRobot(self):
    robot_0 = self.getTradingRobot(name=self.base_name)
    #self.assertEqual(robot_0.infrastructureIsReady(),True) 
    self.assertEqual(robot_0.noCatastrophicEventHappening(),True) 
    self.assertEqual(robot_0.acquisitionConditionMet(),True) 
    self.assertEqual(robot_0.noIssuesWithBrokerage(),True) 
    self.assertEqual(robot_0.canTradeNow(current_time=self.now),True) 
    self.assertEqual(robot_0.haveEnoughFundsToPurchase(),True) 


  #@unittest.skip("Taking a break now")
  def testMarketWindowConfigurationRobot(self):
    robot_0 = self.getTradingRobot(name=self.base_name)
    self.assertEqual(robot_0.canTradeNow(current_time=self.now),True) 

  #Portfolio and Budget Management
  #@unittest.skip("Taking a break now")
  def testBudgetConfigurationOnEmptyRobot(self):
    robot_0 = self.getTradingRobot(name=self.base_name)
    self.assertEqual(robot_0.haveEnoughFundsToPurchase(),False) 
    self.assertEqual(robot_0.updateRobotCashPosition(cost_basis=300),0.0) 
    #Portfolio Selection Associated with Data Source
    #Daily Budget Update from the the External Portofolio

  #@unittest.skip("Taking a break now")
  def testRoundtripInterfacesOnEmptyRobot(self):
    robot_0 = self.getTradingRobot(name=self.base_name)
    self.assertEqual(robot_0.getStableRoundTrips().getStableSize(),0) 
    #self.assertEqual(robot_0.getInTransitionRoundTrips().getInTransitionSize(),0) 
    self.assertEqual(robot_0.getCompletedRoundTrips().getCompletedSize(),0) 
    #self.assertEqual(robot_0.getTransitionalCandidateRoundTrips().getTransitionalSize(),0) 
    self.assertEqual(robot_0.getCompletionCandidatesRoundTrips().getCompletionCandidatesSize(),0) 

  def getTradingRobot(self,name):
    robot = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)    
    return robot

#
# We perform a singe purchase operation and make sure all the values are as expected.
@unittest.skip("Taking a break now")
class BasicRobotWithOneBuyTestCase(TestCase):
  base_name = 'testme'
  max_roundtrips = 20
  etf = 'QQQ'
  bullish = 'TQQQ'
  bearish = 'SQQQ'
  cost_basis_per_roundtrip = 2000
  initial_budget = 100000
  profit_per_roundtrip = 100

  @classmethod 
  def setUpTestData(self):
    robot = ETFAndReversePairRobot.objects.create(name=self.base_name,max_roundtrips=self.max_roundtrips,bullish_symbol=self.bullish,
                                                  bearish_symbol=self.bearish,etf_symbol=self.etf,initial_profit=self.profit_per_roundtrip,
                                                  budget=self.initial_budget,cost_basis_per_roundtrip=self.cost_basis_per_roundtrip)


  #@unittest.skip("Taking a break now")
  def testBasicConfigurationEmptyRobot(self):
    robot_0 = self.getTradingRobot(name=self.base_name)


  def testRobotWithOneBuyTradingData(self):
    robot_0 = self.getTradingRobot(name=self.base_name)
    robot_0.addANewRoundtrip()
    robot_0.listAllRountrips()
    # This is a buy order section
    buy_order = robot_0.prepareBuyOrder(bull_share_price=120,bear_share_price=6)
    dual_order = RobotBuyOrderExecutor(buy_order=buy_order)
    order_result = dual_order.executeAndGetResults(use_alpaca=False,use_historical=False)
    print("Order Result = {0} ".format(order_result))
    robot_0.captureBuyOrderCompletion(order=order_result)
    bullish = order_result['bull'] 
    bearish = order_result['bear']
    
    # These are the Basic Initialization Functions of the Class
    self.assertEqual(robot_0.getInitialBudget(),self.initial_budget)  
    self.assertEqual(robot_0.getBullish(),self.bullish) 
    self.assertEqual(robot_0.getBearish(),self.bearish) 
    self.assertNotEqual(robot_0.getAvailableCash(),float(self.initial_budget)) 
    self.assertEqual(robot_0.getProfitTargetPerRoundtrip(),self.profit_per_roundtrip) 
    self.assertEqual(robot_0.getMaxNumberOfRoundtrips(),20) 

    # Validate Transaction operations 
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

    # Validate Shares Quantity operations 
    self.assertEqual(robot_0.getAllBearishSharesAcquired(),bearish['qty'])  
    self.assertEqual(robot_0.getAllBullishSharesAcquired(),bullish['qty'])      
    self.assertEqual(robot_0.getAllSharesAcquired(),bearish['qty']+bullish['qty'])  

    self.assertEqual(robot_0.getAllBullishSharesSold(),0)
    self.assertEqual(robot_0.getAllBearishSharesSold(),0)
    self.assertEqual(robot_0.getAllSharesSold(),0)

    print("HENRI: {0}".format(TradeDataHolder.objects.annotate().order_by('acquistion_date')[0]))
    #self.assertEqual(robot_0.getAllBullishSharesUnrealized(),bullish['qty'])
    #self.assertEqual(robot_0.getAllBearishSharesUnrealized(),bearish['qty']) 
    #self.assertEqual(robot_0.getAllSharesUnrealized(),bearish['qty']+bullish['qty'])

    #self.assertEqual(robot_0.getTimeOfMostRecentBullishPurchase(),0)
    #self.assertEqual(robot_0.getTimeOfMostRecentBearishPurchase(),1) 
    #self.assertEqual(robot_0.getTimeOfMostRecentPurchase(),5)

    self.assertEqual(robot_0.getCostOfAllBearishSharesAcquired(),bearish['qty']*bearish['price'])
    self.assertEqual(robot_0.getCostOfAllBullishSharesAcquired(),bullish['qty']*bullish['price']) 
    total_price =  bearish['qty']*bearish['price'] + bullish['qty']*bullish['price']
    self.assertEqual(robot_0.getCostOfAllSharesAcquired(),total_price)

    self.assertEqual(robot_0.getCostOfAllBearishSharesUnrealized(bear_price_per_share=7),bearish['qty']*bearish['price'])
    self.assertEqual(robot_0.getCostOfAllBullishSharesAcquired(bull_price_per_share=110),bullish['qty']*bullish['price']) 
    total_price =  bearish['qty']*bearish['price'] + bullish['qty']*bullish['price']
    self.assertEqual(robot_0.getCostOfAllBullishSharesUnrealized(bear_price_per_share=7,bull_price_per_share=110),total_price)



    self.assertEqual(robot_0.isAssemblylineFull(),False)

    # Validate Value Operations 
  def getTradingRobot(self,name):
    match=name
    robot = ETFAndReversePairRobot.objects.get(name=match)
    
    return robot


# One acquitions and one sale
#
@unittest.skip("Taking a break now")
class BasicRobotWithOneBuyOneSaleTestCase(TestCase):
  base_name = 'testme'
  max_roundtrips = 20
  etf = 'QQQ'
  bullish = 'TQQQ'
  bearish = 'SQQQ'
  cost_per_roundrip = 2000
  initial_budget = 100000
  profit_per_roundtrip = 100

  @classmethod 
  def setUpTestData(self):
    robot = ETFAndReversePairRobot.objects.create(name=self.base_name,max_roundtrips=self.max_roundtrips,bullish_symbol=self.bullish,
                                                  bearish_symbol=self.bearish,etf_symbol=self.etf,initial_profit=self.profit_per_roundtrip,
                                                  budget=self.initial_budget,cost_basis_per_roundtrip=self.cost_per_roundrip)


  #@unittest.skip("Taking a break now")
  def testBasicConfigurationEmptyRobot(self):
    robot_0 = self.getTradingRobot(name=self.base_name)

  def testRobotWithOneBuyOneSingleSellTradingData(self):
    robot_0 = self.getTradingRobot(name=self.base_name)
    alpaca_trade = AlpacaLastTrade()
    bullish_price = alpaca_trade.getLastTrade(symbol = robot_0.getBullish()).price
    bearish_price = alpaca_trade.getLastTrade(symbol = robot_0.getBearish()).price
    #print("Prices from Alpaca: {0} , {1} \n".format(bullish_price,bearish_price))
    #sys.stdout.flush()
    # This is a buy order section
    buy_order = robot_0.prepareBuyOrder(bull_share_price=bullish_price,bear_share_price=bearish_price)
    dual_order = RobotBuyOrderExecutor(buy_order=buy_order)
    order_result = dual_order.executeAndGetResults(use_alpaca=False,use_historical=False)

    #print("Order Result = {0} ".format(order_result))

    robot_0.captureBuyOrderCompletion(order=order_result)

    #Selling the Bullish Side
    sell_order_bull = robot_0.prepareSellOrder(buy_client_order_id=buy_order['bull_order_id'])
    order_bull = RobotSellOrderExecutor(sell_order=sell_order_bull)
    results_bull = order_bull.executeAndGetResults(use_alpaca=False,use_historical=False,sell_price=bullish_price+5)

    self.assertEqual(robot_0.getTransactions(),3) 
    self.assertEqual(robot_0.getNumberOfBullishBuyTransactions(),1) 
    self.assertEqual(robot_0.getNumberOfBearishBuyTransactions(),1) 
    self.assertEqual(robot_0.isAssemblylineFull(),False)

    #Selling the Bearish Side
    sell_order_bear = robot_0.prepareSellOrder(buy_client_order_id=buy_order['bear_order_id'])
    order_bear = RobotSellOrderExecutor(sell_order=sell_order_bear)
    results_bear = order.executeAndGetResults(use_alpaca=False,use_historical=False,sell_price=bearish_price-0.60)

    self.assertEqual(robot_0.getTransactions(),4) 
    self.assertEqual(robot_0.getNumberOfBullishBuyTransactions(),1) 
    self.assertEqual(robot_0.getNumberOfBearishBuyTransactions(),1) 
    self.assertEqual(robot_0.isAssemblylineFull(),False)


  def getTradingRobot(self,name):
    match=name
    robot = ETFAndReversePairRobot.objects.get(name=match)
    
    return robot

 

#
# This test case covers the creation of a new Class Instance of the Robot.
# There is no trading data at this point. Most of the methods should still return valid 
# and expected values
#
@unittest.skip("Taking a break now")
class TwoBasicRobotWithNoTradeDataTestCase(TestCase):
  base_name = 'testme'
  max_roundtrips = 20
  etf = 'QQQ'
  bullish = 'TQQQ'
  bearish = 'SQQQ'
  cost_per_roundrip = 2000
  initial_budget = 100000
  profit_per_roundtrip = 100
  min_number_of_rountrips_per_day = 5
  time_spacing_between_sales = 15 #minutes

  base_name1 = 'testme1'
  max_roundtrips1 = 20
  etf1 = 'SPY'
  bullish1 = 'TQQQ'
  bearish1 = 'SQQQ'
  cost_per_roundrip1 = 2000
  initial_budget1 = 100000
  profit_per_roundtrip1 = 100

  @classmethod 
  def setUpTestData(self):
    robot_qqq = ETFAndReversePairRobot.objects.create(name=self.base_name,max_roundtrips=self.max_roundtrips,bullish_symbol=self.bullish,
                                                  bearish_symbol=self.bearish,etf_symbol=self.etf,initial_profit=self.profit_per_roundtrip,
                                                  budget=self.initial_budget,cost_basis_per_roundtrip=self.cost_per_roundrip)

    robot_spy = ETFAndReversePairRobot.objects.create(name=self.base_name1,max_roundtrips=self.max_roundtrips1,bullish_symbol=self.bullish1,
                                                  bearish_symbol=self.bearish1,etf_symbol=self.etf1,initial_profit=self.profit_per_roundtrip1,
                                                  budget=self.initial_budget1,cost_basis_per_roundtrip=self.cost_per_roundrip1)

  #@unittest.skip("Taking a break now")
  def testBasicConfigurationEmptyRobot(self):
    robot_qqq = self.getTradingRobot(name=self.base_name)
    robot_spy = self.getTradingRobot(name=self.base_name1)

  def getTradingRobot(self,name):
    match=name
    robot = ETFAndReversePairRobot.objects.get(name=match)
    
    return robot



#
# This test case covers the creation of a new Class Instance of the Robot.
# There is no trading data at this point. Most of the methods should still return valid 
# and expected values
#   # ['SPXU','SPXL','SCO','UCO','TQQQ','SQQQ','SDOW','UDOW','TNA','TZA','FAS','FAZ','LABU','LABD']

@unittest.skip("Taking a break now")
class Roundtrip15RobotsWithLotsofDataTestCase(TestCase):
  base_name = ['Nasdaq','S&P500','Oil Bloomberg','Dow Jones','Small Cap','Financials','Biotech','Technology',
               'Semi Conductors','Russell','Silver','Natural Gas','China']
  description = ['Description1','Description2','Description3','Description4','Description5','Description6','Description7',
                 'Description10','Description11','Description12','Description13','Description14','Description15']
  max_roundtrips = [20,20,10,10,10, 10,10,10,10,10, 10,10,10,10,10]
  etfs  = ['QQQQ','PPPP','AAA','BBBO','CCC', 'UUU','DSFR','EEE0','AAA0','DDDD', 'FFFF','FRRR','AAA','DDDS','UUUU']
  bulls = ['TQQQ','SPXU','SCO','SDOW','TNA', 'FAS','LABU','TECL','NUGT','JNUG', 'SOXL','URTY','AGQ','KOLD','YINN']
  bears = ['SQQQ','SPXL','UCO','UDOW','TZA', 'FAZ','LABD','TECS','DUST','JDST', 'SOXS','SRTY','ZXL','BOIL','YANG']
  cost_PR = [2000,1000,1500,1800,2200, 2500,3000,5000,6000,7000, 7500,8500,10000,12000,15000]
  profit_PR = [100,50,20,25,20, 40,45,55,65,75, 200,250,300,400,500]
  
  bull_prices_nasdaq = [120,122,121,125,124, 124,130,135,137,140]
  bear_prices_nasdaq = []
  
  bull_prices_spy = []
  bear_prices_spy = []

  bull_prices_oil = []
  bear_prices_oil = []

  bull_prices_dow = []
  bear_prices_dow = []

  bull_prices_small_cap = []
  bear_prices_small_cap = []

  current_times = ['']
  @classmethod 
  def setUpTestData(self):
#################################NASDAQ ##########
    nasdaq=RobotEquitySymbols.objects.create(name=self.base_name[0],symbol=self.etfs[0],bullishSymbol=self.bulls[0],bearishSymbol=self.bears[0])
    robot_nasdaq=ETFAndReversePairRobot.objects.create(name=self.base_name[0],description=self.description[0],
            portfolio=None,strategy=None,symbols=nasdaq,enabled=True,owner=None,visibility=True,
            version='1.0.0', max_hold_time='14',minimum_hold_time='1',hold_time_includes_holiday=True,
            sell_remaining_before_buy=False,liquidate_on_next_opportunity=False,internal_name=self.internal_name[0],
            max_roundtrips=self.max_roundtrips[0],cost_basis_per_roundtrip=self.cost_PR[0],
            profit_target_per_roundtrip=self.profit_PR[0])    
    self.robot_nasdaq_id =robot_nasdaq.pk
    sentiment_nasdaq = EquityAndMarketSentiment.objects.create(pair_robot=robot_nasdaq,influences_acquisition=True,circuit_breaker=False,
                                                          sentiment_feed='Automatic')
 
    self.s0_id = sentiment_nasdaq.pk
    bm_nasdaq = RobotBudgetManagement.objects.create(pair_robot=robot_nasdaq,use_percentage_or_fixed_value='Number')

# #################################SPY Robot #################
    spy=RobotEquitySymbols.objects.create(name=self.base_name[1],symbol=self.etfs[1],bullishSymbol=self.bulls[1],bearishSymbol=self.bears[1])
    robot_spy=ETFAndReversePairRobot.objects.create(name=self.base_name[1],description=self.description[1],
            portfolio=None,strategy=None,symbols=nasdaq,enabled=True,owner=None,visibility=True,
            version='1.0.0', max_hold_time='14',minimum_hold_time='1',hold_time_includes_holiday=True,
            sell_remaining_before_buy=False,liquidate_on_next_opportunity=False,internal_name=self.internal_name[1],
            max_roundtrips=self.max_roundtrips[1],cost_basis_per_roundtrip=self.cost_PR[1],
            profit_target_per_roundtrip=self.profit_PR[1])    
    self.robot_spy_id =robot_spy.pk
    sentiment_spy = EquityAndMarketSentiment.objects.create(pair_robot=robot_spy,influences_acquisition=True,circuit_breaker=False,
                                                          sentiment_feed='Automatic')
 
    self.s0_id = sentiment_spy.pk
    bm_spy = RobotBudgetManagement.objects.create(pair_robot=robot_spy,use_percentage_or_fixed_value='Number')

# #################################OIL Robot ################
    oil=RobotEquitySymbols.objects.create(name=self.base_name[2],symbol=self.etfs[2],bullishSymbol=self.bulls[2],bearishSymbol=self.bears[2])
    robot_oil=ETFAndReversePairRobot.objects.create(name=self.base_name[2],description=self.description[2],
            portfolio=None,strategy=None,symbols=oil,enabled=True,owner=None,visibility=True,
            version='1.0.0', max_hold_time='14',minimum_hold_time='1',hold_time_includes_holiday=True,
            sell_remaining_before_buy=False,liquidate_on_next_opportunity=False,internal_name=self.internal_name[2],
            max_roundtrips=self.max_roundtrips[2],cost_basis_per_roundtrip=self.cost_PR[2],
            profit_target_per_roundtrip=self.profit_PR[2])    
    self.robot_oil_id =robot_oil.pk
    sentiment_oil = EquityAndMarketSentiment.objects.create(pair_robot=robot_oil,influences_acquisition=True,circuit_breaker=False,
                                                          sentiment_feed='Automatic')
 
    self.s_oil_id = sentiment_oil.pk
    bm_oil = RobotBudgetManagement.objects.create(pair_robot=robot_oil,use_percentage_or_fixed_value='Number')

# #################################DOW Robot ################
    dow=RobotEquitySymbols.objects.create(name=self.base_name[3],symbol=self.etfs[3],bullishSymbol=self.bulls[3],bearishSymbol=self.bears[3])
    robot_dow=ETFAndReversePairRobot.objects.create(name=self.base_name[3],description=self.description[3],
            portfolio=None,strategy=None,symbols=dow,enabled=True,owner=None,visibility=True,
            version='1.0.0', max_hold_time='14',minimum_hold_time='1',hold_time_includes_holiday=True,
            sell_remaining_before_buy=False,liquidate_on_next_opportunity=False,internal_name=self.internal_name[1],
            max_roundtrips=self.max_roundtrips[3],cost_basis_per_roundtrip=self.cost_PR[3],
            profit_target_per_roundtrip=self.profit_PR[3])    
    self.robot_dow_id =robot_dow.pk
    sentiment_dow = EquityAndMarketSentiment.objects.create(pair_robot=robot_dow,influences_acquisition=True,circuit_breaker=False,
                                                          sentiment_feed='Automatic')
 
    self.s_dow_id = sentiment_dow.pk
    bm_dow = RobotBudgetManagement.objects.create(pair_robot=robot_dow,use_percentage_or_fixed_value='Number')

# #################################DOW Robot ################
    small_cap=RobotEquitySymbols.objects.create(name=self.base_name[4],symbol=self.etfs[4],bullishSymbol=self.bulls[4],bearishSymbol=self.bears[4])
   
# #################################DOW Robot ################
    fin=RobotEquitySymbols.objects.create(name=self.base_name[5],symbol=self.etfs[5],bullishSymbol=self.bulls[5],bearishSymbol=self.bears[5])

# #################################DOW Robot ################
    bio=RobotEquitySymbols.objects.create(name=self.base_name[6],symbol=self.etfs[6],bullishSymbol=self.bulls[6],bearishSymbol=self.bears[6])

# #################################DOW Robot ################
    micro=RobotEquitySymbols.objects.create(name=self.base_name[7],symbol=self.etfs[7],bullishSymbol=self.bulls[7],bearishSymbol=self.bears[7])

# #################################DOW Robot ################
    gold=RobotEquitySymbols.objects.create(name=self.base_name[8],symbol=self.etfs[8],bullishSymbol=self.bulls[8],bearishSymbol=self.bears[8])
    gold_miner=RobotEquitySymbols.objects.create(name=self.base_name[9],symbol=self.etfs[9],bullishSymbol=self.bulls[9],bearishSymbol=self.bears[9])

    semi_conductors=RobotEquitySymbols.objects.create(name=self.base_name[10],symbol=self.etfs[10],bullishSymbol=self.bulls[10],bearishSymbol=self.bears[10])
    russell=RobotEquitySymbols.objects.create(name=self.base_name[11],symbol=self.etfs[11],bullishSymbol=self.bulls[11],bearishSymbol=self.bears[11])
    silver=RobotEquitySymbols.objects.create(name=self.base_name[12],symbol=self.etfs[12],bullishSymbol=self.bulls[12],bearishSymbol=self.bears[12])
    gas=RobotEquitySymbols.objects.create(name=self.base_name[13],symbol=self.etfs[13],bullishSymbol=self.bulls[13],bearishSymbol=self.bears[13])
    china=RobotEquitySymbols.objects.create(name=self.base_name[14],symbol=self.etfs[14],bullishSymbol=self.bulls[14],bearishSymbol=self.bears[14])

  #@unittest.skip("Taking a break now")
  def getTradeInformation(self,index,robot):
    information = dict()
    information['timestamp'] = self.current_times[index]

    information[self.bullish]=self.bull_prices[index]
    information[self.bearish]=self.bear_prices[index] 
    return information 

  #@unittest.skip("Taking a break now")
  def testRoundtripBasicRobot(self):
    robot_nasdaq = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    robot_spy    = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    robot_oil    = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    robot_dow    = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    index = 0
    for n in self.current_times:
      payload_nasdaq = self.getTradeInformation(index=index,robot=robot_nasdaq)
      payload_spy = self.getTradeInformation(index=index,robot=robot_spy)
      payload_oil = self.getTradeInformation(index=index,robot=robot_oil)
      payload_dow = self.getTradeInformation(index=index,robot=robot_dow)

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

if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)
