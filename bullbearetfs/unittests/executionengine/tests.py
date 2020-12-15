import datetime, time, pytz, logging, unittest , sys,json
import pandas as pd
from django.utils import timezone
from django.test import TestCase
import dateutil.parser,xmlrunner
from django.core import serializers
from bullbearetfs.strategy.models import EquityStrategy, AcquisitionPolicy, DispositionPolicy
from bullbearetfs.strategy.models import OrdersManagement,PortfolioProtectionPolicy
from bullbearetfs.robot.models import  ETFAndReversePairRobot
from bullbearetfs.robot.symbols.models import RobotEquitySymbols
from bullbearetfs.brokerages.models import BrokerageInformation
from bullbearetfs.robot.budget.models import RobotBudgetManagement,  Portfolio
from bullbearetfs.robot.activitysentiments.models import EquityAndMarketSentiment
from bullbearetfs.robot.budget.models import RobotBudgetManagement
from bullbearetfs.utilities.core import strToDatetime 
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, shouldUsePrint
from bullbearetfs.executionengine.models import ETFPairRobotExecution , ETFPairBackTestRobotExecutionEngine
from bullbearetfs.robot.models import  ETFAndReversePairRobot
from bullbearetfs.robot.foundation.roundtrip import RoundTrip
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, strToDatetime, shouldUsePrint, displayOutput,displayError
from bullbearetfs.datasources.datasources import  BackTestArrayInfrastructure,BackTestFileInfrastructure, DownloadableETFBullBear
from bullbearetfs.datasources.datasources import DelayedLiveInfrastructure, BackTestInfrastructure, BackTestDatabaseInfrastructure
from bullbearetfs.robot.activitysentiments.models import EquityAndMarketSentiment,RobotActivityWindow

"""
  Tests the functionality around the ExecutionEngine Classes.
  This consists of the following classes:
  1. ETFPairBackTestRobotExecutionEngine : This is a wrapper class for the functionality of the 2 classes below
  2. ETFPairRobotExecutionData: This class is used to keep track of step by step data of a particular execution
  3. ETFPairRobotExecution: This class consists of the individual execution launched, when a new execution is started.

"""

logger = logging.getLogger(__name__)


def test_robot_feed_dummy(request):
  logger.info(" This is just a dummy function ")


#     
#@unittest.skip("Taking a break now")
class ExecutionEngineBasicFeeds(TestCase):
  """
    ExecutionEngineBasicFeeds: We are validating that we can launch Execution Engines with a variety of feeds.
    The purpose of these classes is to make all execution very simple
  """
  base_name='Base Name'
  description = 'This is the Description'
  testname ='ExecutionEngineBasicFeeds'
  max_roundtrips=8
  etf = 'QQQ'
  bullish = 'TQQQ'
  bearish = 'SQQQ'
  internal_name='foumban'
  cost_basis_per_roundtrip = 1500
  profit_basis_per_roundtrip = 10

  bulls_prices = [120.0,121.00,122.0,123.0,122.5,122,122.75,124,127,130]
  bear_prices  = [25.00, 24.75,24.50,24.25,24.25,24.50,24.33,24,23,22.50]
  etf_prices   = [250,252,252,253,253,256,266,277,254,245]
  timestamps   = ['2020-08-03 8:15:00-04:00','2020-08-03 8:45:00-04:00','2020-08-03 9:05:00-04:00','2020-08-03 9:45:00-04:00',
                  '2020-08-03 10:16:00-04:00','2020-08-03 11:05:00-04:00','2020-08-03 11:35:00-04:00','2020-08-03 12:45:00-04:00',
                  '2020-08-04 8:45:00-04:00','2020-08-04 9:45:00-04:00','2020-08-04 10:45:00-04:00','2020-08-04 11:45:00-04:00',
                  '2020-08-04 2:45:00-04:00']

  @classmethod 
  def setUpTestData(self):
    if shouldUsePrint():
      print("Setting up {0}".format(self.testname))

    #Build the Robot
    now=datetime.datetime.now(getTimeZoneInfo())
    alpacaBrokerage = BrokerageInformation.objects.create(brokerage_type='Alpaca',name='Alpaca',website='alpaca.markets/')

    alpacaPortfolio = Portfolio.objects.create(name='Alpaca Portfolio',initial_cash_funds=100000,current_cash_funds=100000,brokerage_id=alpacaBrokerage.id,
      max_robot_fraction=.10,cash_position_update_policy='immediate',description='Alpaca Portfolio description')

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

    ############################ Robot ##############################
    nasdaq=RobotEquitySymbols.objects.create(name='Nasdaq',symbol=self.etf,bullishSymbol=self.bullish,bearishSymbol=self.bearish)
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


  #Creates a new RobotExecution
  #Creates a new Robot
  #Feeds data from an Array Datasource
  #Validate that we can create reports for this execution. 
  #A Financial report and a Replay Report.
  #@unittest.skip("Taking a break now")
  def testCreateAndRunANewExecutionBasedonArrayFeed(self):
    #Define the Feed Type: We will feed from an Array
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
    self.assertTrue(int(financial_summary['transactions'])>0)
    self.assertTrue(len(financial_entries)>0)

    #Replay the execution
    replay_results = exec1.getExecEngineReplayReport()
    #print (" {}".format(replay_results))
    replay_summary = replay_results['summary']
    replay_entries = replay_results['entries']
    self.assertTrue(int(replay_summary['transactions'])>0)
    self.assertTrue(len(replay_entries)>0)

    #Delete this Execution
    exec1.clearBackTestData()

    #Try to regenerate the reports and validate that they are no reports, because the data has been deleted.
    replay_results = exec1.getExecEngineReplayReport()

    #Retrieve the Financial Results: Validate there is no data, because the data has been deleted.
    financial_results = exec1.getExecEngineFinancialReport()
    replay_summary = replay_results['summary']
    replay_entries = replay_results['entries']
    self.assertTrue(int(replay_summary['transactions'])>0)
    self.assertTrue(len(replay_entries)>0)

  #Create 2 Feeds Infrastructures (File, Array, ...)
  # Create a new Robot.
  # Creates one new RobotExecution per Feed. Make sure to update the Robot with various feeds.
  # Validate that we can create a Financial Report, a Replay Report for these executions. 
  # Between 2 runs, we modify the Robot.max_rountrips from 8 to 4.
  # We are saving the configuration information.
  # Make sure that upon completion, we can retrieve and compare the configuration parameters.
  #@unittest.skip("Taking a break now")
  def testSeveralExecutionsVariousDataSources(self):
    #Define the Feed Type: We will feed from an Array
    file_feed_infra = BackTestFileInfrastructure(testname='testSeveralExecutionsVariousDataSources',bull_symbol=self.bullish,
                                                bear_symbol=self.bearish,etf_symbol=self.etf)

    #Define the Feed Type: We will feed from an Array
    array_feed_infra = BackTestArrayInfrastructure(bull_feed=self.bulls_prices,bear_feed=self.bear_prices,
                                                etf_feed=self.etf_prices,time_feed=self.timestamps,bull_symbol=self.bullish,
                                                bear_symbol=self.bearish,etf_symbol=self.etf)
    
    #Find the Robot to carry the Execution
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_id)

    #Create and Save a new ETFPairRobotExecution Instance
    executor_array = ETFPairRobotExecution.createRobotExecution(exec_start_date=None,exec_end_date=None,robot=robot_0)

    #Create a new RobotExecutionEngine
    exec_engine_array=ETFPairBackTestRobotExecutionEngine(robot=robot_0,executor_id=executor_array.id,request=None, 
                                             datasource=array_feed_infra)

    #Perform the Backtest. There might be a delay in completing the execution. 
    results_array = exec_engine_array.executeBackTest()

    #robot_1 and robot_0 are the same. Modify the Robot max_roundtrips (8,4). Run it against Files Feed.
    robot_1 = ETFAndReversePairRobot.objects.get(pk=self.robot_id)
    robot_1.max_roundtrips=4
    robot_1.save()

    #Create and Save a new ETFPairRobotExecution Instance
    executor_file = ETFPairRobotExecution.createRobotExecution(exec_start_date=None,exec_end_date=None,robot=robot_1)

    #Create a new RobotExecutionEngine
    exec_engine_file=ETFPairBackTestRobotExecutionEngine(robot=robot_1,executor_id=executor_file.id,request=None, 
                                             datasource=file_feed_infra)

    #Perform the Backtest. There might be a delay in completing the execution. 
    results_file = exec_engine_file.executeBackTest()

    #Check the Financial Report from the File Execution (robot_0)
    f_results_file = exec_engine_file.getExecEngineFinancialReport()
    f_finance_summary = f_results_file['summary']
    f_finance_entries = f_results_file['entries']

    self.assertEqual(int(f_finance_summary['transactions']),2*int(robot_1.max_roundtrips))
    self.assertEqual(len(f_finance_entries),2*int(robot_1.max_roundtrips))


    #Check the Financial Report from the Array Execution (robot_1)
    f_results_array = exec_engine_array.getExecEngineFinancialReport()
    a_finance_summary = f_results_array['summary']
    a_finance_entries = f_results_array['entries']

    self.assertEqual(int(a_finance_summary['transactions']),2*int(robot_0.max_roundtrips))
    self.assertEqual(len(a_finance_entries),2*int(robot_0.max_roundtrips))

    #TODO: Make sure you can list executions that belong to the Robot (robot_0 and robot_1 are the same)
    exec_all_files = exec_engine_file.listAllExecutions()
    exec_all_arrays = exec_engine_array.listAllExecutions()
    self.assertEqual(len(exec_all_files),2)
    self.assertEqual(len(exec_all_arrays),2)
    
    #The result below is in form of an array [ '+4',' ','-8','']
    found_4 = False
    found_8 = False 
    config_diff = exec_engine_array.compareExecutionResults(candidate=executor_file)
    for x in config_diff:
      if '4' in x:
        found_4 = True
      if '8' in x:
        found_8 = True 

    self.assertEqual(found_4,True)
    self.assertEqual(found_8,True)


  # This will test the ExecutionEngine. The only different with the two other
  # tests is the Execution Engine will be fed from the Database entries
  # This adds the complexity of start/end times.
  #
  #@unittest.skip("Taking a break now")
  def testExecutionEngineViaDatabaseEntriesFeed(self):
    #Set up the Data to feed the Robot.
    number_entries = 1 #Nasdaq100 Only (TQQQ, SQQQ, QQQ)
    RobotEquitySymbols.insertMasterEquities(count=number_entries)
    #Start Date on October 01
    start_date = datetime.datetime(2020,10,1,tzinfo=timezone.utc).isoformat()
    backtesting = BackTestInfrastructure(action='download',useMasterTable=True)
    response = backtesting.processTradeData(start_date=start_date)
    response0 = backtesting.downloadAndStore(target='both',update=False)
    #Data has loaded completely.

    db_infrastructure = BackTestDatabaseInfrastructure(bull_symbol=self.bullish,bear_symbol=self.bearish,etf_symbol=self.etf)
    #Find the Robot to carry the Execution
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_id)

    #Create and Save a new ETFPairRobotExecution Instance
    start_date_s = datetime.datetime(2020,10,1,tzinfo=timezone.utc).isoformat()
    end_date_s = datetime.datetime(2020,10,28,tzinfo=timezone.utc).isoformat()

    executor = ETFPairRobotExecution.createRobotExecution(exec_start_date=start_date_s,exec_end_date=end_date_s,robot=robot_0)

    #Create a new RobotExecutionEngine
    exec1=ETFPairBackTestRobotExecutionEngine(robot=robot_0,executor_id=executor.id,request=None, 
                                             datasource=db_infrastructure)

    #Perform the Backtest. There might be a delay in completing the execution. 
    results = exec1.executeBackTest()

    #Retrieve the Financial Results
    financial_results = exec1.getExecEngineFinancialReport()
    #print (" {}".format(financial_results))
    financial_summary = financial_results['summary']
    financial_entries = financial_results['entries']
    self.assertTrue(int(financial_summary['transactions'])>0)
    self.assertTrue(len(financial_entries)>0)

    #Replay the execution
    replay_results = exec1.getExecEngineReplayReport()
    replay_summary = replay_results['summary']
    replay_entries = replay_results['entries']
    self.assertTrue(int(replay_summary['transactions'])>0)
    self.assertTrue(len(replay_entries)>0)

  #
  # DelayedLiveInfrastructure: The feed comes from the Live Data
  #
  @unittest.skip("Taking a break now")  
  def testSerializingRobot(self):
    print("Serialization ...")

   #Find the Robot to carry the Execution
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_id)
    #data = serializers.serialize("json", [robot_0])
    data = robot_0.getSerializedRobotObject()
    print(" {}".format(data))

    #Launch a few more robots on each robot.
    #TODO: Make sure you can Delete ONE and validate
    #exec_engine_file.printExecutorData()
    #exec_engine_array.printExecutorData()
    #TODO: Rerun with different parameters?
    #This meaans: Delete the content, but not the execution.

    #TODO: Do we want to do Compare?
    #f_replay_summary = f_results_file['summary']
    #f_replay_entries = f_results_file['entries']

    #self.assertTrue(int(f_replay_summary['transactions'])>0)
    #self.assertTrue(len(f_replay_entries)>0)

    #print("\n\n FILE: {}".format(f_results_file))
    #print("ARRAY: {}".format(f_results_array))

  @unittest.skip("Taking a break now")
  def testBasicExecution(self):
    #Define the Feed  Type
    #Define the Robot 
    #Define the Parameters for the ExecutionEngine
    exec1=ETFPairBackTestRobotExecutionEngine(robot=robot0,backtest_input_data=self.backtest1,request=None, datasource=None)
    exec1.executeBackTest()
    exec1.displayResults()


  #
  # DelayedLiveInfrastructure: The feed comes from the Live Data
  #
  @unittest.skip("Taking a break now")  
  def testRobotFeedFromDelayedLive(self):
    live_infra = DelayedLiveInfrastructure(bull_symbol=self.bullish,bear_symbol=self.bearish,etf_symbol=self.etf,sleep_time=1)
    
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_id)

    count = 5
    sleep_time = 1
    for i in range(count):
      feed = live_infra.getTradingInformation() 
      #print("Data: = {}".format(data))
      robot_0.setCurrentValues(current_payload=feed)
      response = robot_0.acquisitionConditionMet() 
      if response:
        robot_0.addNewRoundtripEntry()

    size =robot_0.getStableRoundTrips().getStableSize()
    self.assertTrue(size>=1)

if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)
