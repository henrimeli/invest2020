import datetime, time,logging, unittest
from django.test import TestCase
import dateutil.parser, xmlrunner
from bullbearetfs.brokerages.models import BrokerageInformation
from bullbearetfs.strategy.models import EquityStrategy, AcquisitionPolicy, DispositionPolicy
from bullbearetfs.robot.activitysentiments.models import EquityAndMarketSentiment,RobotActivityWindow
from bullbearetfs.robot.budget.models import RobotBudgetManagement,  Portfolio
from bullbearetfs.robot.symbols.models import  RobotEquitySymbols
from bullbearetfs.robot.models import  ETFAndReversePairRobot
from bullbearetfs.strategies.babadjou import BabadjouStrategy
from bullbearetfs.strategies.batcham import BatchamStrategy

#from bullbearetfs.strategies.balatchi import BalatchiStrategy
#from bullbearetfs.strategies.bangang import BangangStrategy
#from bullbearetfs.strategies.bamendjinda import BamendjindaStrategy
#, BalachiStrategyReference, BangangStrategyReference

from bullbearetfs.strategies.strategyreferences import BabadjouStrategy, BatchamStrategy, BalachiStrategyReference, BangangStrategyReference
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, strToDatetime, shouldUsePrint, displayOutput,displayError
from bullbearetfs.executionengine.models import ETFPairRobotExecution , ETFPairBackTestRobotExecutionEngine

from bullbearetfs.datasources.datasources import  BackTestArrayInfrastructure,BackTestFileInfrastructure, DownloadableETFBullBear
from bullbearetfs.datasources.datasources import DelayedLiveInfrastructure, BackTestInfrastructure, BackTestDatabaseInfrastructure

"""
  The purpose of this class is to create and validate strategy implementations.
  The basestrategy class is the skeleton (abstract base class for all strategies to be implemented on the egghead platform).

  All strategies of the Egghead platform must subclass the basestrategy abstract class and implement the remaining functions
  Additional help classes and/or functions might be needed to complete the implementation.
"""

logger = logging.getLogger(__name__)

def test_reference_strategies(request):
  logger.info("This is just a dummy function ")


######################################################################################################################
# Reference Stratregies Functionality:
#
# This represent the validation of various reference Strategies
#
#
@unittest.skip("TODO: Not yet implemented.")
class TestBabadjouStrategy(TestCase):
  testname ='TestBabadjouStrategy'
  base_name='Robot for Babadjou Strategy'
  description='This is a test description of the robot for the Babadjou Strategy '
  max_roundtrips=20
  internal_name='bamboutos'
  cost_basis_per_roundtrip=1000
  profit_basis_per_roundtrip=25
  etf='QQQ'
  bullish='TQQQ'
  bearish='SQQQ'

  bulls_prices = [120.0,121.00,122.0,123.0,122.5,122,122.75,124,127,130]
  bear_prices  = [25.00, 24.75,24.50,24.25,24.25,24.50,24.33,24,23,22.50]
  etf_prices   = [250,252,252,253,253,256,266,277,254,245]
  timestamps   = ['2020-08-03 8:15:00-04:00','2020-08-03 8:45:00-04:00','2020-08-03 9:05:00-04:00','2020-08-03 9:45:00-04:00',
                  '2020-08-03 10:16:00-04:00','2020-08-03 11:05:00-04:00','2020-08-03 11:35:00-04:00','2020-08-03 12:45:00-04:00',
                  '2020-08-04 8:45:00-04:00','2020-08-04 9:45:00-04:00','2020-08-04 10:45:00-04:00','2020-08-04 11:45:00-04:00',
                  '2020-08-04 2:45:00-04:00']

  @classmethod 
  def setUpTestData(self):
    displayOutput(str="Setting up {0}".format(self.testname))
    alpacaBrokerage = BrokerageInformation.objects.create(brokerage_type='Alpaca',name='Alpaca Brokerage',website='https://alpaca.markets/')

    alpacaPortfolio = Portfolio.objects.create(name='Alpaca Portfolio',initial_cash_funds=100000,current_cash_funds=100000,brokerage_id=alpacaBrokerage.id,
      max_robot_fraction=.10,cash_position_update_policy='immediate',description='Alpaca Portfolio description')

    nasdaq=RobotEquitySymbols.objects.create(name='Nasdaq',symbol=self.etf,bullishSymbol=self.bullish,bearishSymbol=self.bearish)
    now=datetime.datetime.now(getTimeZoneInfo())
    
    strategy = EquityStrategy.objects.create(name='My Best Equity Strategy So Far',description='This is just a test',creation_date=now,
      modify_date=now,strategy_class='Bullish Bearish Pair',strategy_category='Babadjou',visibility=False,
      minimum_entries_before_trading=2, trade_only_after_fully_loaded=False,manual_asset_composition_policy=True,
      automatic_generation_client_order_id=True)
    self.entry_id = strategy.pk 

    acquisition = AcquisitionPolicy.objects.create(strategy=strategy,acquisition_time_proximity=False,min_time_between_purchases=60,and_or_1='AND',
      acquisition_volume_proximity=False,min_volume_between_purchases='15M',volume_fraction_to_average=3,and_or_2='AND',
      acquisition_price_proximity=True,acquisition_price_factor='Bull',bear_acquisition_volatility_factor='.01',number_or_percentage='Stock Price by Number',
      proximity_calculation_automatic=True,bull_acquisition_volatility_factor='.10',simultaneous_bull_bear_acquisitions=True)
    self.acq_entry = acquisition.pk 

    disposition = DispositionPolicy.objects.create(strategy=strategy,in_transition_profit_policy=True,in_transition_profit_target_ratio='.15',
      completion_profit_policy=True,completion_complete_target_ratio='.40',
      in_transition_asset_composition='2Bull x 1Bear',in_transition_entry_strategy='bestbull_and_worstbear')
    self.disposition_id = disposition.pk 


    robot=ETFAndReversePairRobot.objects.create(name=self.base_name,description=self.description,
            portfolio=alpacaPortfolio,strategy=strategy,symbols=nasdaq,enabled=True,owner=None,visibility=True,
            version='1.0.0', max_hold_time='14',minimum_hold_time='1',hold_time_includes_holiday=True,
            sell_remaining_before_buy=False,liquidate_on_next_opportunity=False,internal_name=self.internal_name,
            max_roundtrips=self.max_roundtrips,cost_basis_per_roundtrip=self.cost_basis_per_roundtrip,
            profit_target_per_roundtrip=self.profit_basis_per_roundtrip)    
    self.robot_id =robot.pk

    sentiment = EquityAndMarketSentiment.objects.create(pair_robot=robot,influences_acquisition=True,circuit_breaker=False,
                                                          sentiment_feed='Automatic')
 
    self.sentiment_id = sentiment.pk
    self.budget_management = RobotBudgetManagement.objects.create(pair_robot=robot,max_budget_per_purchase_number=self.cost_basis_per_roundtrip,
                                                             use_percentage_or_fixed_value='Number')
 
    activities = RobotActivityWindow.objects.create(pair_robot=robot,trade_before_open=True,trade_after_close=False,
      trade_during_extended_opening_hours=False, offset_after_open='0',offset_before_close='0',
      blackout_midday_from='10:00am',blackout_midday_time_interval='0')

  @unittest.skip("Taking a break now")
  def testBabadjouStrategyCreation(self):
    #Find the Robot to carry the Execution
    displayOutput(str="Testing the Babadjou Strategy Scenario")
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_id)
    strategy_instance = EquityStrategy.objects.get(pk=self.entry_id)

    strategy_imple = BabadjouStrategy(robot=robot_0)

    self.assertEqual(strategy_imple.isValid(),True)
    self.assertEqual(strategy_imple.isBabadjouStrategy(),True)

    self.assertEqual(strategy_imple.isBatchamStrategy(),False) 
    self.assertEqual(strategy_imple.isBalatchiStrategy(),False)

    self.assertEqual(strategy_imple.hasTransitionStep(),True) 
    self.assertEqual(strategy_imple.hasBalancedTransition(),True) 

    self.assertEqual(strategy_instance.isBabadjouStrategy(),True) 

  #
  #
  #
  #@unittest.skip("Taking a break now")
  def testBasicEndToEndBabadjouStrategyWithArrayInfra(self):
    """
      This is an end to end test that demonstrates the Babadjou Strategy
    """
    array_feed_infra = BackTestArrayInfrastructure(bull_feed=self.bulls_prices,bear_feed=self.bear_prices,
                                                   etf_feed=self.etf_prices,time_feed=self.timestamps,bull_symbol=self.bullish,
                                                   bear_symbol=self.bearish,etf_symbol=self.etf)

    #Find the Robot to carry the Execution
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_id)

    #Create and Save a new ETFPairRobotExecution Instance
    executor = ETFPairRobotExecution.createRobotExecution(exec_start_date=None,exec_end_date=None,robot=robot_0)

    #Create a new RobotExecutionEngine
    exec1=ETFPairBackTestRobotExecutionEngine(robot=robot_0,executor_id=executor.id,request=None,
                                             datasource=array_feed_infra)

    #Perform the Backtest. There might be a delay in completing the execution.
    results = exec1.executeBackTest()

    #Retrieve the Financial Results
    financial_results = exec1.getExecEngineFinancialReport()
    financial_summary = financial_results['summary']
    financial_entries = financial_results['entries']

    print("{}".format(financial_summary))
    self.assertTrue(int(financial_summary['transactions'])>0)
    self.assertTrue(len(financial_entries)>0)

    #Replay the execution
    replay_results = exec1.getExecEngineReplayReport()
    #print (" {}".format(replay_results))
    replay_summary = replay_results['summary']
    replay_entries = replay_results['entries']
    self.assertTrue(int(replay_summary['transactions'])>0)
    self.assertTrue(len(replay_entries)>0)




#class BatchamCompletionCandidates():

#@unittest.skip(" ")
class TestBatchamStrategy(TestCase):
  testname ='TestBatchamStrategy'
  base_name='Robot for Batcham Strategy'
  description='This is a test description of the robot for the Batcham Strategy '
  max_roundtrips=20
  internal_name='bamboutos'
  cost_basis_per_roundtrip=1000
  profit_basis_per_roundtrip=25
  etf='QQQ'
  bullish='TQQQ'
  bearish='SQQQ'

  bulls_prices = [120.0,121.00,122.0,123.0,122.5,122,122.75,124,127,130]
  bear_prices  = [25.00, 24.75,24.50,24.25,24.25,24.50,24.33,24,23,22.50]
  etf_prices   = [250,252,252,253,253,256,266,277,254,245]
  timestamps   = ['2020-08-03 8:15:00-04:00','2020-08-03 8:45:00-04:00','2020-08-03 9:05:00-04:00','2020-08-03 9:45:00-04:00',
                  '2020-08-03 10:16:00-04:00','2020-08-03 11:05:00-04:00','2020-08-03 11:35:00-04:00','2020-08-03 12:45:00-04:00',
                  '2020-08-04 8:45:00-04:00','2020-08-04 9:45:00-04:00','2020-08-04 10:45:00-04:00','2020-08-04 11:45:00-04:00',
                  '2020-08-04 2:45:00-04:00']

  @classmethod 
  def setUpTestData(self):
    displayOutput(str="Setting up {0}".format(self.testname))
    alpacaBrokerage = BrokerageInformation.objects.create(brokerage_type='Alpaca',name='Alpaca Brokerage',website='https://alpaca.markets/')

    alpacaPortfolio = Portfolio.objects.create(name='Alpaca Portfolio',initial_cash_funds=100000,current_cash_funds=100000,brokerage_id=alpacaBrokerage.id,
      max_robot_fraction=.10,cash_position_update_policy='immediate',description='Alpaca Portfolio description')

    nasdaq=RobotEquitySymbols.objects.create(name='Nasdaq',symbol=self.etf,bullishSymbol=self.bullish,bearishSymbol=self.bearish)
    now=datetime.datetime.now(getTimeZoneInfo())
    
    strategy = EquityStrategy.objects.create(name='My Best Equity Strategy So Far',description='This is just a test',creation_date=now,
      modify_date=now,strategy_class='Bullish Bearish Pair',strategy_category='Batcham',visibility=False,
      minimum_entries_before_trading=2, trade_only_after_fully_loaded=False,manual_asset_composition_policy=True,
      automatic_generation_client_order_id=True)
    self.entry_id = strategy.pk 

    acquisition = AcquisitionPolicy.objects.create(strategy=strategy,acquisition_time_proximity=False,min_time_between_purchases=60,and_or_1='AND',
      acquisition_volume_proximity=False,min_volume_between_purchases='15M',volume_fraction_to_average=3,and_or_2='AND',
      acquisition_price_proximity=True,acquisition_price_factor='Bull',bear_acquisition_volatility_factor='.01',number_or_percentage='Stock Price by Number',
      proximity_calculation_automatic=True,bull_acquisition_volatility_factor='.10',simultaneous_bull_bear_acquisitions=True)
    self.acq_entry = acquisition.pk 

    disposition = DispositionPolicy.objects.create(strategy=strategy,in_transition_profit_policy=True,in_transition_profit_target_ratio='.15',
      completion_profit_policy=True,completion_complete_target_ratio='.40',
      in_transition_asset_composition='2Bull x 1Bear',in_transition_entry_strategy='bestbull_and_worstbear')
    self.disposition_id = disposition.pk 


    robot=ETFAndReversePairRobot.objects.create(name=self.base_name,description=self.description,
            portfolio=alpacaPortfolio,strategy=strategy,symbols=nasdaq,enabled=True,owner=None,visibility=True,
            version='1.0.0', max_hold_time='14',minimum_hold_time='1',hold_time_includes_holiday=True,
            sell_remaining_before_buy=False,liquidate_on_next_opportunity=False,internal_name=self.internal_name,
            max_roundtrips=self.max_roundtrips,cost_basis_per_roundtrip=self.cost_basis_per_roundtrip,
            profit_target_per_roundtrip=self.profit_basis_per_roundtrip)    
    self.robot_id =robot.pk

    sentiment = EquityAndMarketSentiment.objects.create(pair_robot=robot,influences_acquisition=True,circuit_breaker=False,
                                                          sentiment_feed='Automatic')
 
    self.sentiment_id = sentiment.pk
    self.budget_management = RobotBudgetManagement.objects.create(pair_robot=robot,max_budget_per_purchase_number=self.cost_basis_per_roundtrip,
                                                             use_percentage_or_fixed_value='Number')
 
    activities = RobotActivityWindow.objects.create(pair_robot=robot,trade_before_open=True,trade_after_close=False,
      trade_during_extended_opening_hours=False, offset_after_open='0',offset_before_close='0',
      blackout_midday_from='10:00am',blackout_midday_time_interval='0')
 
  def testStrategyCreation(self):
    displayOutput(str="Testing the Basic Strategy Scenario")
    #robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_id)
    #strategy = BatchamStrategyReference(robot=robot_0)
    #Find the Robot to carry the Execution
    #displayOutput(str="Testing the Babadjou Strategy Scenario")
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_id)
    strategy_instance = EquityStrategy.objects.get(pk=self.entry_id)

    strategy_imple = BatchamStrategy(robot=robot_0)

    self.assertEqual(strategy_imple.isValid(),True)
    self.assertEqual(strategy_imple.isBabadjouStrategy(),False)

    self.assertEqual(strategy_imple.isBatchamStrategy(),True) 
    self.assertEqual(strategy_imple.isBalatchiStrategy(),False)

    self.assertEqual(strategy_imple.hasTransitionStep(),False) 
    self.assertEqual(strategy_imple.hasBalancedTransition(),False) 

    self.assertEqual(strategy_instance.isBatchamStrategy(),True) 
 
  #
  #
  #
  #@unittest.skip("Taking a break now")
  def testBasicEndToEndBatchamStrategyWithArrayInfra(self):
    """
      This is an end to end test that demonstrates the Batcham Strategy
    """
    array_feed_infra = BackTestArrayInfrastructure(bull_feed=self.bulls_prices,bear_feed=self.bear_prices,
                                                   etf_feed=self.etf_prices,time_feed=self.timestamps,bull_symbol=self.bullish,
                                                   bear_symbol=self.bearish,etf_symbol=self.etf)

    #Find the Robot to carry the Execution
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_id)

    #Create and Save a new ETFPairRobotExecution Instance
    executor = ETFPairRobotExecution.createRobotExecution(exec_start_date=None,exec_end_date=None,robot=robot_0)

    #Create a new RobotExecutionEngine
    exec1=ETFPairBackTestRobotExecutionEngine(robot=robot_0,executor_id=executor.id,request=None,
                                             datasource=array_feed_infra)

    #Perform the Backtest. There might be a delay in completing the execution.
    results = exec1.executeBackTest()

    #Retrieve the Financial Results
    financial_results = exec1.getExecEngineFinancialReport()
    financial_summary = financial_results['summary']
    financial_entries = financial_results['entries']

    print("{}".format(financial_summary))
    self.assertTrue(int(financial_summary['transactions'])>0)
    self.assertTrue(len(financial_entries)>0)

    #Replay the execution
    replay_results = exec1.getExecEngineReplayReport()
    #print (" {}".format(replay_results))
    replay_summary = replay_results['summary']
    replay_entries = replay_results['entries']
    self.assertTrue(int(replay_summary['transactions'])>0)
    self.assertTrue(len(replay_entries)>0)

#
@unittest.skip("TODO: Not yet implemented.")
class TestBanganStrategy(TestCase):
  testname ='TestBanganStrategy'

  @classmethod 
  def setUpTestData(self):
    print("Setting up {0}".format(self.testname))
 
  def testStrategyCreation(self):
    print("Testing the Basic Strategy Scenario")
    self.assertEqual(True,True)

#
@unittest.skip("TODO: Not yet implemented.")
class TestBalachiStrategy(TestCase):
  testname ='TestBalachiStrategy'

  @classmethod 
  def setUpTestData(self):
    print("Setting up {0}".format(self.testname))
 
  def testStrategyCreation(self):
    print("Testing the Basic Strategy Scenario")
    self.assertEqual(True,True)

if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)
