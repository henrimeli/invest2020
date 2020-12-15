from datetime import datetime, time
import logging, unittest, sys,json, xmlrunner
from django.utils import timezone
from django.test import TestCase

# Import Models
from bullbearetfs.strategy.models import EquityStrategy, AcquisitionPolicy,DispositionPolicy,OrdersManagement,PortfolioProtectionPolicy
from bullbearetfs.robot.models import ETFAndReversePairRobot,TradeDataHolder, RoundTrip, BabadjouWinnerRoundTrip
from bullbearetfs.models import RobotEquitySymbols,EquityAndMarketSentiment, RobotBudgetManagement
from bullbearetfs.robot.models import BabadjouCompletionCandidates
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, strToDatetime
logger = logging.getLogger(__name__)

#
# Dummy function needed to force rebuild on change.
#
def test_babadjou_winners_roundtrips_dummy(request):
  pass

###############################################################################################################
# This class tests the Move from Stable to Transition and Completion based on the Transition Strategy Type.
# Two major classes are used for that purpose:
#    BabadjouWinnerRoundTrip and BabadjouCompletionCandidate Interfaces/Classes
#
# Tests the functionality around the BabadjouWinnerRoundTrip (Interface) Class.
# BabadjouWinnerRoundTrip is not a persistable Class. It is an interface to access RoundTrips we want to move
# to Transition then to Completion. We choose to move one or more Roundtrips to Transition, Completion when they
# meet certain criteria.
#
# BabadjouWinnerRoundTrip: Focuses on the encapsulation of potential winners based on various performance criteria.
# BabadjouCompletionCandidate: Focuses on collecting BabadjouWinnerRoundTrips and finding best performers to move to 
# Completion 
# Functionality in the BabadjouWinnerRoundTrip has been grouped in the following areas:
#   Winner based on various types of criteria: Performance, Buy price, Inner Spread, Average-Based Assembly Line Spread
#   Construction of "Transition" candidacy (none exist, we building it)
#   Construction of "Completion" candidacy (One exists already, is it good enough to be move to completion)
#   Selection of the proper bulls and bears to be part of the Group
#   Calculation of their performance to Transition, Generation of Data to save the entry into the System.
#   Calculation of their performance to completion.
#   Usage of min_hold_time to ensure that we can't move entries, unless they have been deemed elligible based on Age.
#   Usage of various criteria to move entries. Performance, Buy price, Inner Spread, Assembly Line Spread, Average Costs
#
##############################################################################################################
# Tests the functionality around:
#   PerformanceBasedWinners: Performance Based Winners focus on the move to Transition based on the StableValue().
#     By focusing on the StableValue(), we focus only on how Bull/Bear are performing to select entries then move them.
#     Number of Test Classes Planned: 5
#     Total Number of Test Functions: 5 x 5
#     Number of remaining Functions: 0
#
#   AssetAcquisitionPriceBasedWinners: Focuses on the move to transition based on the acquisition Price of assets.
#     By focusing on the Acquisition Price, we focus only on how much we pay for Bull/Bear to select entries to move them.
#     We believe we will achieve different results than above. 
#     It is important to note that the main criteria for qualifying is still the performance. Acquisition price is only
#     the criteria for selection of the asset combination (Bull/Bear).
#     Number of Test Classes Planned: 1
#     Total Number of Test Functions: 5
#     Number of remaining Functions: 0
#     Status: COMPLETE
#
#   InnerPriceSpreadBasedWinners: Focuses on the move to transition based on the inner spread.
#     By selecting the Inner Spread (which is the cost difference between bull/bear of the same Roundtrip), we 
#     Number of Test Classes Planned: 1
#     Total Number of Test Functions: 5
#     Number of remaining Functions: 0
#     Status: COMPLETE
#  
#   AveragePriceSpreadBasedWinners: Focuses on the move to transition based on the price spread on the Assembly Line.
#     Here we calculate the Spread based on all entries, regardless whether they are elligible to be sold or not.
#     Number of Test Classes Planned: 1
#     Total Number of Test Functions: 5
#     Number of remaining Functions: 0
#     Status: COMPLETE
#
#   AveragePriceSpreadTwoBasedWinners: Focuses on the move to transition based on the price spread on the Assembly Line. 
#      Here we calculate the spread based only on elligible entries.
#     Number of Test Classes Planned: 1
#     Total Number of Test Functions: 5
#     Number of remaining Functions: 0
#     Status: COMPLETE
#
#####################################################################################################
#
#  PerformanceBasedWinners: Items are selected based on their individual performances.
#
#
#@unittest.skip("Taking a break now")
class PerformanceBasedWinners(TestCase):
  base_name = 'PerformanceBasedWinners'
  description = 'Description of Test for the PerformanceBasedWinners Babadjou Winners'
  max_roundtrips = 20
  etf = 'OIL'
  bullish = 'SCO'
  bearish = 'UCO'
  cost_basis_per_roundtrip = 1500
  initial_budget = 100000
  profit_basis_per_roundtrip = 50
  bull_prices=[16.29,16.31,16.41,16.34,16.23, 16.18,16.37,16.49,16.95,16.35, 16.29,16.31,16.41,16.34,16.23, 16.18,16.37,16.49,16.55,16.35]
  bear_prices=[31.44,31.40,31.29,31.26,31.19, 31.42,31.20,31.39,31.26,31.09, 31.42,31.45,32.29,33.26,30.19, 31.14,91.40,31.49,31.16,31.10]
  current_times=['2020-08-03 04:05:00-04:00','2020-08-03 09:05:00-04:00','2020-08-03 11:15:00-04:00','2020-08-03 11:16:00-04:00',
                 '2020-08-03 11:45:00-04:00','2020-08-03 11:49:24-04:00','2020-08-03 11:55:00-04:00','2020-08-03 13:15:00-04:00',
                 '2020-08-04 10:45:00-04:00','2020-08-04 10:40:24-04:00','2020-08-04 11:55:00-04:00','2020-08-04 14:15:00-04:00',
                 '2020-08-05 09:45:00-04:00','2020-08-05 11:29:24-04:00','2020-08-05 11:35:03-04:00','2020-08-05 13:15:00-04:00',
                 '2020-08-05 15:55:00-04:00','2020-08-05 15:56:00-04:00','2020-08-05 15:56:30-04:00','2020-08-05 15:57:00-04:00']
  internal_name='foumban'

  @classmethod 
  def setUpTestData(self):

    strategy1 = EquityStrategy.objects.create(name='My valid Equity Strategy',description='This is just a test',
        strategy_class='Bullish Bearish',strategy_category='Babadjou',visibility=False,
      minimum_entries_before_trading=4, trade_only_after_fully_loaded=False,manual_asset_composition=True,
      automatic_generation_client_order_id=True)

    self.entry1_id = strategy1.pk 

    disposition1 = DispositionPolicy.objects.create(in_transition_profit_policy=True,in_transition_profit_target_ratio='.25',
      completion_profit_policy=True,completion_complete_target_ratio='.40', strategy=strategy1,in_transition_strategy_type='Asset Performance',
      in_transition_asset_composition='1Bull x 2Bear',in_transition_entry_strategy='bestbull_and_bestbear',
      in_transition_load_factor='50')
    self.disposition1_id = disposition1.pk 

    nasdaq=RobotEquitySymbols.objects.create(name='Nasdaq',symbol=self.etf,bullishSymbol=self.bullish,bearishSymbol=self.bearish)
    robot1=ETFAndReversePairRobot.objects.create(name=self.base_name,description=self.description,
            portfolio=None,strategy=strategy1,symbols=nasdaq,enabled=True,owner=None,visibility=True,
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
  def testNoEntriesInStable(self):
    self.loadData(count=0)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    index=0
    payload = self.getTradeInformation(index=index)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 

    stable = robot_0.getStableRoundTrips()
    self.assertEqual(stable.getSize(),0)
    self.assertEqual(stable.getStableSize(),0)
    self.assertEqual(stable.isFullyLoaded(),False)
    self.assertEqual(stable.isEmpty(),True) 

    winner_transition = BabadjouWinnerRoundTrip(robot=robot_0)
    self.assertEqual(winner_transition.isValid(),False)
    self.assertEqual(winner_transition.isTransitionalCandidate(),False)
    self.assertEqual(winner_transition.isCompletionCandidate(),False)
    self.assertEqual(winner_transition.getCandidateOutput(),None)
    self.assertEqual(winner_transition.matchesBabadjouTransitionTarget(),None)
    self.assertEqual(winner_transition.getTransitionCandidateReportData(),None)


  #@unittest.skip("Taking a break now")
  def testFewerEntriesInStableThanNeededForStrategy(self):
    self.loadData(count=1) #At least 3 are needed
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    index=1
    payload = self.getTradeInformation(index=index)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 

    stable = robot_0.getStableRoundTrips()
    self.assertEqual(stable.getSize(),1)
    self.assertEqual(stable.getStableSize(),1)
    self.assertEqual(stable.isFullyLoaded(),False)
    self.assertEqual(stable.isEmpty(),False) 

    winner_transition = BabadjouWinnerRoundTrip(robot=robot_0)
    self.assertEqual(winner_transition.isValid(),False)
    self.assertEqual(winner_transition.isTransitionalCandidate(),False)
    self.assertEqual(winner_transition.isCompletionCandidate(),False)
    self.assertEqual(winner_transition.getCandidateOutput(),None)
    self.assertEqual(winner_transition.matchesBabadjouTransitionTarget(),None)
    self.assertEqual(winner_transition.getTransitionCandidateReportData(),None)

  #@unittest.skip("Taking a break now")
  def testExactlyAsManyAsNeededRoundtrips(self):
    self.loadData(count=3)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    index=3
    payload = self.getTradeInformation(index=index)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 

    stable = robot_0.getStableRoundTrips()
    self.assertEqual(stable.getSize(),3)
    self.assertEqual(stable.getStableSize(),3)
    self.assertEqual(stable.isFullyLoaded(),False)
    self.assertEqual(stable.isEmpty(),False) 

    winner_transition = BabadjouWinnerRoundTrip(robot=robot_0)
    self.assertEqual(winner_transition.isValid(),True)
    self.assertEqual(winner_transition.isTransitionalCandidate(),True)
    self.assertEqual(winner_transition.isCompletionCandidate(),False)
    report_data = winner_transition.getTransitionCandidateReportData()
    self.assertEqual(report_data['bulls_length'],1)  
    self.assertEqual(float(report_data['performance_target']),12.5) 
    self.assertEqual(round(float(report_data['total_performance']),2),-1.78) 
    self.assertEqual(winner_transition.matchesBabadjouTransitionTarget(),False)

  #By changing minimum_hold_time some bulls/bear can't yet be sold.
  #@unittest.skip("Taking a break now")
  def tesAsManyAsNeededWithMinimumHoldTime(self):
    self.loadData(count=3)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # Here, we modify the minimum hold time
    index=3
    robot_0.minimum_hold_time='1'
    robot_0.save()

    payload = self.getTradeInformation(index=index)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 

    stable = robot_0.getStableRoundTrips()
    self.assertEqual(stable.getSize(),3)
    self.assertEqual(stable.getStableSize(),3)
    self.assertEqual(stable.isFullyLoaded(),False)
    self.assertEqual(stable.isEmpty(),False) 

    #Because of the 1 day Hold time, we can't find enough entries to sell.
    winner_transition = BabadjouWinnerRoundTrip(robot=robot_0)
    self.assertEqual(winner_transition.isValid(),False)
    self.assertEqual(winner_transition.isTransitionalCandidate(),False)
    self.assertEqual(winner_transition.isCompletionCandidate(),False)

    #By moving the Index, we also move the Current_Time to one day ahead
    # The new current_time will make it possible to
    # '2020-08-04 11:55:00-04:00'
    index = 12
    payload = self.getTradeInformation(index=index)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    winner_transition = BabadjouWinnerRoundTrip(robot=robot_0)
    self.assertEqual(winner_transition.isValid(),True)
    self.assertEqual(winner_transition.isTransitionalCandidate(),True)
    self.assertEqual(winner_transition.isCompletionCandidate(),False)
    report_data = winner_transition.getTransitionCandidateReportData()
    self.assertEqual(report_data['bulls_length'],1)  
    self.assertEqual(float(report_data['performance_target']),12.5) 
    self.assertEqual(round(float(report_data['total_performance']),2),50.88) 
    self.assertEqual(winner_transition.matchesBabadjouTransitionTarget(),True)

  #@unittest.skip("Taking a break now")
  def testBabadjouCompletionCandidates(self):
    self.loadData(count=3)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    index=3
    for index in [3,4,8]:
      payload = self.getTradeInformation(index=index)
      self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
      self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
      self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
      self.assertEqual(robot_0.getSymbol(),self.etf) 
      self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
      self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 

      stable = robot_0.getStableRoundTrips()
      self.assertEqual(stable.getSize(),3)
      self.assertEqual(stable.getStableSize(),3)
      self.assertEqual(stable.isFullyLoaded(),False)
      self.assertEqual(stable.isEmpty(),False) 

      if index==3:
        winner_transition = BabadjouWinnerRoundTrip(robot=robot_0)
        self.assertEqual(winner_transition.isValid(),True)
        self.assertEqual(winner_transition.isTransitionalCandidate(),True)
        self.assertEqual(winner_transition.isCompletionCandidate(),False)
        report_data = winner_transition.getTransitionCandidateReportData()
        self.assertEqual(report_data['bulls_length'],1)  
        self.assertEqual(float(report_data['performance_target']),12.5) 
        self.assertEqual(round(float(report_data['total_performance']),2),-1.78) 
        self.assertEqual(winner_transition.matchesBabadjouTransitionTarget(),False)

      if index==4:
        winner_transition = BabadjouWinnerRoundTrip(robot=robot_0)
        self.assertEqual(winner_transition.isValid(),True)
        self.assertEqual(winner_transition.isTransitionalCandidate(),True)
        self.assertEqual(winner_transition.isCompletionCandidate(),False)
        report_data = winner_transition.getTransitionCandidateReportData()
        self.assertEqual(report_data['bulls_length'],1)  
        self.assertEqual(float(report_data['performance_target']),12.5) 
        self.assertEqual(round(float(report_data['total_performance']),2),-10.2) 
        self.assertEqual(winner_transition.matchesBabadjouTransitionTarget(),False)
        completions = BabadjouCompletionCandidates(robot=robot_0)
        self.assertEqual(completions.isFull(),False)
        self.assertEqual(completions.getCompletionSize(),0)
        self.assertEqual(completions.isEmpty(),True)
        self.assertEqual(completions.getMaximumSize(),None)
        self.assertEqual(completions.getCompletionWinner(),None)
        completions_data = completions.getCompletionCandidatesData()
        self.assertEqual(completions_data['summary_data']['entries'],0)
        self.assertEqual(completions_data['content_data'],[])

      if index==8:
        winner_transition = BabadjouWinnerRoundTrip(robot=robot_0)
        self.assertEqual(winner_transition.isValid(),True)
        self.assertEqual(winner_transition.isTransitionalCandidate(),True)
        self.assertEqual(winner_transition.isCompletionCandidate(),False)
        report_data = winner_transition.getTransitionCandidateReportData()
        self.assertEqual(report_data['bulls_length'],1)  
        self.assertEqual(float(report_data['performance_target']),12.5) 
        self.assertEqual(round(float(report_data['total_performance']),2),26.28) 
        self.assertEqual(winner_transition.matchesBabadjouTransitionTarget(),True)
        winner_transition.moveToTransition()
        stable1 = robot_0.getStableRoundTrips()
        self.assertEqual(stable1.getSize(),0)
        self.assertEqual(stable1.getStableSize(),0)
        self.assertEqual(stable1.isFullyLoaded(),False)
        self.assertEqual(stable1.isEmpty(),True) 
        winner2_transition = BabadjouWinnerRoundTrip(robot=robot_0)
        self.assertEqual(winner2_transition.isValid(),False)
        self.assertEqual(winner2_transition.isTransitionalCandidate(),False)
        self.assertEqual(winner2_transition.isCompletionCandidate(),False)
        completions = BabadjouCompletionCandidates(robot=robot_0)
        self.assertEqual(completions.getCompletionSize(),1)
        self.assertEqual(completions.getMaximumSize(),3) 
        self.assertEqual(completions.isFull(),False)
        self.assertEqual(completions.isEmpty(),False)
        completions_data = completions.getCompletionCandidatesData()
        self.assertEqual(completions_data['summary_data']['entries'],1)
        self.assertEqual(len(completions_data['content_data']),1)
        completion_winner_1 = completions.getCompletionWinner()

        self.assertEqual(completion_winner_1.isValid(),True)
        self.assertEqual(completion_winner_1.isTransitionalCandidate(),False)
        self.assertEqual(completion_winner_1.isCompletionCandidate(),True)

        #Move to Completion ...
        completion_winner_1.moveToCompletion()
        
        completions_after = BabadjouCompletionCandidates(robot=robot_0)
        self.assertEqual(completions_after.isFull(),False)
        self.assertEqual(completions_after.getCompletionSize(),0)
        self.assertEqual(completions_after.isEmpty(),True)
        self.assertEqual(completions_after.getMaximumSize(),None) 
        self.assertEqual(completions_after.getCompletionWinner(),None) 
        self.assertEqual(completions_after.getCompletionCandidatesData()['content_data'],[])    
        self.assertEqual(completions_after.getMaximumSize(),None) 
    
##############################################################################################################
#
#  AssetPriceBasedWinners: Adding random entries into the system. Then using transition_type
#  based on 'Asset Acquisition Price' to complete the work. Additionally, another part of this test will
#  use minmum hold time to make sure we can have assets not sell earlier than the minimal hold time specified. 
#
#@unittest.skip("Taking a break now")
class AssetAcquisitionPriceBasedWinners(TestCase):
  base_name = 'Test Babadjou Asset Acquisition Price Winners'
  description = 'Description of Test for the Babadjou Asset Acquisition Price Winners'
  max_roundtrips = 20
  etf = 'NAT'
  bullish = 'DGAZ'
  bearish = 'DAS'
  cost_basis_per_roundtrip = 1500
  initial_budget = 100000
  profit_basis_per_roundtrip = 50
  bull_prices=[16.29,16.31,16.41,16.34,16.23, 16.18,16.37,16.49,16.95,16.35, 16.29,16.31,16.41,16.34,16.23, 16.18,16.37,16.49,16.55,16.35]
  bear_prices=[31.44,31.40,31.29,31.26,31.19, 31.42,31.20,31.39,31.26,31.09, 31.42,31.45,32.29,33.26,30.19, 31.14,91.40,31.49,31.16,31.10]
  current_times=['2020-08-03 04:05:00-04:00','2020-08-03 09:05:00-04:00','2020-08-03 11:15:00-04:00','2020-08-03 11:16:00-04:00',
                 '2020-08-03 11:45:00-04:00','2020-08-03 11:49:24-04:00','2020-08-03 11:55:00-04:00','2020-08-03 13:15:00-04:00',
                 '2020-08-04 10:45:00-04:00','2020-08-04 10:40:24-04:00','2020-08-04 11:55:00-04:00','2020-08-04 14:15:00-04:00',
                 '2020-08-05 09:45:00-04:00','2020-08-05 11:29:24-04:00','2020-08-05 11:35:03-04:00','2020-08-05 13:15:00-04:00',
                 '2020-08-05 15:55:00-04:00','2020-08-05 15:56:00-04:00','2020-08-05 15:56:30-04:00','2020-08-05 15:57:00-04:00']
  internal_name='foumban'

  @classmethod 
  def setUpTestData(self):

    strategy1 = EquityStrategy.objects.create(name='My valid Equity Strategy',description='This is just a test',
        strategy_class='Bullish Bearish',strategy_category='Babadjou',visibility=False,
      minimum_entries_before_trading=4, trade_only_after_fully_loaded=False,manual_asset_composition=True,
      automatic_generation_client_order_id=True)

    self.entry1_id = strategy1.pk 

    disposition1 = DispositionPolicy.objects.create(in_transition_profit_policy=True,in_transition_profit_target_ratio='.25',
      completion_profit_policy=True,completion_complete_target_ratio='.40', strategy=strategy1,in_transition_strategy_type='Asset Acquisition Price',
      in_transition_asset_composition='1Bull x 2Bear',in_transition_entry_strategy='bestbull_and_bestbear',
      in_transition_load_factor='50')
    self.disposition1_id = disposition1.pk 

    nasdaq=RobotEquitySymbols.objects.create(name='Nasdaq',symbol=self.etf,bullishSymbol=self.bullish,bearishSymbol=self.bearish)
    robot1=ETFAndReversePairRobot.objects.create(name=self.base_name,description=self.description,
            portfolio=None,strategy=strategy1,symbols=nasdaq,enabled=True,owner=None,visibility=True,
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
  def testBabadjouPriceBasedWinningRoundtrips(self):
    self.loadData(count=3)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    index=3
    for index in [3,4,8]:
      payload = self.getTradeInformation(index=index)
      self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
      self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
      self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
      self.assertEqual(robot_0.getSymbol(),self.etf) 
      self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
      self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 

      stable = robot_0.getStableRoundTrips()
      self.assertEqual(stable.getSize(),3)
      self.assertEqual(stable.getStableSize(),3)
      self.assertEqual(stable.isFullyLoaded(),False)
      self.assertEqual(stable.isEmpty(),False) 

      if index==3:
        winner_transition = BabadjouWinnerRoundTrip(robot=robot_0)
        self.assertEqual(winner_transition.isValid(),True)
        self.assertEqual(winner_transition.isTransitionalCandidate(),True)
        self.assertEqual(winner_transition.isCompletionCandidate(),False)
        report_data = winner_transition.getTransitionCandidateReportData()
        self.assertEqual(report_data['bulls_length'],1)  
        self.assertEqual(float(report_data['performance_target']),12.5) 
        self.assertEqual(round(float(report_data['total_performance']),2),-10.9) 
        self.assertEqual(winner_transition.matchesBabadjouTransitionTarget(),False)

      if index==4:
        winner_transition = BabadjouWinnerRoundTrip(robot=robot_0)
        self.assertEqual(winner_transition.isValid(),True)
        self.assertEqual(winner_transition.isTransitionalCandidate(),True)
        self.assertEqual(winner_transition.isCompletionCandidate(),False)
        report_data = winner_transition.getTransitionCandidateReportData()
        self.assertEqual(report_data['bulls_length'],1)  
        self.assertEqual(float(report_data['performance_target']),12.5) 
        self.assertEqual(round(float(report_data['total_performance']),2),-19.32) 
        self.assertEqual(winner_transition.matchesBabadjouTransitionTarget(),False)
        completions = BabadjouCompletionCandidates(robot=robot_0)
        self.assertEqual(completions.isFull(),False)
        self.assertEqual(completions.getCompletionSize(),0)
        self.assertEqual(completions.isEmpty(),True)
        self.assertEqual(completions.getMaximumSize(),None)
        self.assertEqual(completions.getCompletionWinner(),None)
        completions_data = completions.getCompletionCandidatesData()
        self.assertEqual(completions_data['summary_data']['entries'],0)
        self.assertEqual(completions_data['content_data'],[])

      if index==8:
        winner_transition = BabadjouWinnerRoundTrip(robot=robot_0)
        self.assertEqual(winner_transition.isValid(),True)
        self.assertEqual(winner_transition.isTransitionalCandidate(),True)
        self.assertEqual(winner_transition.isCompletionCandidate(),False)
        report_data = winner_transition.getTransitionCandidateReportData()
        self.assertEqual(report_data['bulls_length'],1)  
        self.assertEqual(float(report_data['performance_target']),12.5) 
        self.assertEqual(round(float(report_data['total_performance']),2),17.16) 
        self.assertEqual(winner_transition.matchesBabadjouTransitionTarget(),True)
        winner_transition.moveToTransition()
        stable1 = robot_0.getStableRoundTrips()
        self.assertEqual(stable1.getSize(),0)
        self.assertEqual(stable1.getStableSize(),0)
        self.assertEqual(stable1.isFullyLoaded(),False)
        self.assertEqual(stable1.isEmpty(),True) 
        winner2_transition = BabadjouWinnerRoundTrip(robot=robot_0)
        self.assertEqual(winner2_transition.isValid(),False)
        self.assertEqual(winner2_transition.isTransitionalCandidate(),False)
        self.assertEqual(winner2_transition.isCompletionCandidate(),False)
        completions = BabadjouCompletionCandidates(robot=robot_0)
        self.assertEqual(completions.isFull(),False)
        self.assertEqual(completions.getCompletionSize(),1)
        self.assertEqual(completions.getMaximumSize(),3) 
        self.assertEqual(completions.isEmpty(),False)
        completions_data = completions.getCompletionCandidatesData()
        self.assertEqual(completions_data['summary_data']['entries'],1)
        self.assertEqual(len(completions_data['content_data']),1)
        completion_winner_1 = completions.getCompletionWinner()

        self.assertEqual(completion_winner_1.isValid(),True)
        self.assertEqual(completion_winner_1.isTransitionalCandidate(),False)
        self.assertEqual(completion_winner_1.isCompletionCandidate(),True)

        #Move to Completion ...
        completion_winner_1.moveToCompletion()
        
        completions_after = BabadjouCompletionCandidates(robot=robot_0)
        self.assertEqual(completions_after.isFull(),False)
        self.assertEqual(completions_after.getCompletionSize(),0)
        self.assertEqual(completions_after.isEmpty(),True)
        self.assertEqual(completions_after.getMaximumSize(),None) 
        self.assertEqual(completions_after.getCompletionWinner(),None) 
        self.assertEqual(completions_after.getCompletionCandidatesData()['content_data'],[])    
        self.assertEqual(completions_after.getMaximumSize(),None) 


##############################################################################################################
#
#  InnerPriceSpreadBasedWinners: Adding random entries into the system. Then using transition_type
#  based on 'Internal Price Spread' to select Bulls and Bears to move items. Additionally, another part of this test will
#  use minmum hold time to make sure we can have assets not sell earlier than the minimal hold time specified. 
#
#@unittest.skip("Taking a break now")
class InnerPriceSpreadBasedWinners(TestCase):
  base_name = 'Test Babadjou Strategy based on Internal Price Spread'
  description = 'Description of Test for the InnerPriceSpreadBasedWinners'
  max_roundtrips = 20
  etf = 'RUS'
  bullish = 'TZA'
  bearish = 'TNA'
  cost_basis_per_roundtrip = 1500
  initial_budget = 100000
  profit_basis_per_roundtrip = 30
  bull_prices=[16.29,16.31,16.41,16.34,16.23, 16.18,16.37,16.49,16.95,16.35, 16.29,16.31,16.41,16.34,16.23, 16.18,16.37,16.49,16.55,16.35]
  bear_prices=[31.44,31.40,31.29,31.26,31.19, 31.42,31.20,30.39,31.26,31.09, 31.42,31.45,32.29,33.26,30.19, 31.14,91.40,31.49,31.16,31.10]
  current_times=['2020-08-03 04:05:00-04:00','2020-08-03 09:05:00-04:00','2020-08-03 11:15:00-04:00','2020-08-03 11:16:00-04:00',
                 '2020-08-03 11:45:00-04:00','2020-08-03 11:49:24-04:00','2020-08-03 11:55:00-04:00','2020-08-03 13:15:00-04:00',
                 '2020-08-04 10:45:00-04:00','2020-08-04 10:40:24-04:00','2020-08-04 11:55:00-04:00','2020-08-04 14:15:00-04:00',
                 '2020-08-05 09:45:00-04:00','2020-08-05 11:29:24-04:00','2020-08-05 11:35:03-04:00','2020-08-05 13:15:00-04:00',
                 '2020-08-05 15:55:00-04:00','2020-08-05 15:56:00-04:00','2020-08-05 15:56:30-04:00','2020-08-05 15:57:00-04:00']
  internal_name='bangante'

  @classmethod 
  def setUpTestData(self):

    strategy1 = EquityStrategy.objects.create(name='My valid Equity Strategy',description='This is just a test',
        strategy_class='Bullish Bearish',strategy_category='Babadjou',visibility=False,
      minimum_entries_before_trading=4, trade_only_after_fully_loaded=False,manual_asset_composition=True,
      automatic_generation_client_order_id=True)

    self.entry1_id = strategy1.pk 

    disposition1 = DispositionPolicy.objects.create(in_transition_profit_policy=True,in_transition_profit_target_ratio='.25',
      completion_profit_policy=True,completion_complete_target_ratio='.40', strategy=strategy1,in_transition_strategy_type='Price Based Inner Spread',
      in_transition_asset_composition='1Bull x 2Bear',in_transition_entry_strategy='bestbull_and_bestbear',
      in_transition_load_factor='50')
    self.disposition1_id = disposition1.pk 

    nasdaq=RobotEquitySymbols.objects.create(name='Nasdaq',symbol=self.etf,bullishSymbol=self.bullish,bearishSymbol=self.bearish)
    robot1=ETFAndReversePairRobot.objects.create(name=self.base_name,description=self.description,
            portfolio=None,strategy=strategy1,symbols=nasdaq,enabled=True,owner=None,visibility=True,
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
  def testBabadjouPriceBasedWinningRoundtrips(self):
    self.loadData(count=8)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    index=3
    for index in [9,10,11]:
      payload = self.getTradeInformation(index=index)
      self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
      self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
      self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
      self.assertEqual(robot_0.getSymbol(),self.etf) 
      self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
      self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 

      stable = robot_0.getStableRoundTrips()
      self.assertEqual(stable.getSize(),8)
      self.assertEqual(stable.getStableSize(),8)
      self.assertEqual(stable.isFullyLoaded(),False)
      self.assertEqual(stable.isEmpty(),False) 

      if index==9:
        winner_transition = BabadjouWinnerRoundTrip(robot=robot_0)
        self.assertEqual(winner_transition.isValid(),True)
        self.assertEqual(winner_transition.isTransitionalCandidate(),True)
        self.assertEqual(winner_transition.isCompletionCandidate(),False)
        report_data = winner_transition.getTransitionCandidateReportData()
        self.assertEqual(report_data['bulls_length'],1)  
        self.assertEqual(float(report_data['performance_target']),7.5) 
        self.assertEqual(round(float(report_data['total_performance']),2),-22.62) 
        self.assertEqual(winner_transition.matchesBabadjouTransitionTarget(),False)

      if index==10:
        winner_transition = BabadjouWinnerRoundTrip(robot=robot_0)
        self.assertEqual(winner_transition.isValid(),True)
        self.assertEqual(winner_transition.isTransitionalCandidate(),True)
        self.assertEqual(winner_transition.isCompletionCandidate(),False)
        report_data = winner_transition.getTransitionCandidateReportData()
        self.assertEqual(report_data['bulls_length'],1)  
        self.assertEqual(float(report_data['performance_target']),7.5) 
        self.assertEqual(round(float(report_data['total_performance']),2),-9.48) 
        self.assertEqual(winner_transition.matchesBabadjouTransitionTarget(),False)
        completions = BabadjouCompletionCandidates(robot=robot_0)
        self.assertEqual(completions.isFull(),False)
        self.assertEqual(completions.getCompletionSize(),0)
        self.assertEqual(completions.isEmpty(),True)
        self.assertEqual(completions.getMaximumSize(),None)
        self.assertEqual(completions.getCompletionWinner(),None)
        completions_data = completions.getCompletionCandidatesData()
        self.assertEqual(completions_data['summary_data']['entries'],0)
        self.assertEqual(completions_data['content_data'],[])

      if index==11:
        winner_transition = BabadjouWinnerRoundTrip(robot=robot_0)
        self.assertEqual(robot_0.getStableRoundTrips().getSize(),8)
        self.assertEqual(winner_transition.isValid(),True)
        self.assertEqual(winner_transition.isTransitionalCandidate(),True)
        self.assertEqual(winner_transition.isCompletionCandidate(),False)
        report_data = winner_transition.getTransitionCandidateReportData()
        self.assertEqual(report_data['bulls_length'],1)  
        self.assertEqual(float(report_data['performance_target']),7.5) 
        self.assertEqual(round(float(report_data['total_performance']),2),-7.14) 
        self.assertEqual(winner_transition.matchesBabadjouTransitionTarget(),False)

        #Intentionally move to Transition, although not meeting the criterias.
        winner_transition.moveToTransition()
        stable1 = robot_0.getStableRoundTrips()
        self.assertEqual(stable1.getSize(),5)
        self.assertEqual(stable1.getStableSize(),5)
        self.assertEqual(stable1.isFullyLoaded(),False)
        self.assertEqual(stable1.isEmpty(),False) 
        winner2_transition = BabadjouWinnerRoundTrip(robot=robot_0)
        self.assertEqual(winner2_transition.isValid(),True)
        self.assertEqual(winner2_transition.isTransitionalCandidate(),True)
        self.assertEqual(winner2_transition.isCompletionCandidate(),False)

        report2_data = winner2_transition.getTransitionCandidateReportData()
        self.assertEqual(report2_data['bulls_length'],1)  
        self.assertEqual(float(report2_data['performance_target']),7.5) 
        self.assertEqual(round(float(report2_data['total_performance']),2),9.84) 
        self.assertEqual(winner2_transition.matchesBabadjouTransitionTarget(),True)

        winner2_transition.moveToTransition()
        completions = BabadjouCompletionCandidates(robot=robot_0)
        self.assertEqual(completions.isFull(),False)
        self.assertEqual(completions.getCompletionSize(),2)
        self.assertEqual(completions.getMaximumSize(),3) 
        self.assertEqual(completions.isEmpty(),False)
        completions_data = completions.getCompletionCandidatesData()
        self.assertEqual(completions_data['summary_data']['entries'],2)
        self.assertEqual(len(completions_data['content_data']),2)
        completion_winner_1 = completions.getCompletionWinner()

        self.assertEqual(completion_winner_1.isValid(),True)
        self.assertEqual(completion_winner_1.isTransitionalCandidate(),False)
        self.assertEqual(completion_winner_1.isCompletionCandidate(),True)
        self.assertEqual(round(completion_winner_1.getBearsCompletionPerformance(),2),18.40)
        self.assertEqual(round(completion_winner_1.getBullsCompletionPerformance(),2),7.86)
        self.assertEqual(round(completion_winner_1.getBabadjouCompletionPerformance(),2),round(18.40+7.86,2))
        #Move to Completion ...
        completion_winner_1.moveToCompletion()
        
        completions_after = BabadjouCompletionCandidates(robot=robot_0)
        self.assertEqual(completions_after.isFull(),False)
        self.assertEqual(completions_after.getCompletionSize(),1)
        self.assertEqual(completions_after.isEmpty(),False)
        self.assertEqual(completions_after.getMaximumSize(),3) 

        completions2 = BabadjouCompletionCandidates(robot=robot_0)
        self.assertEqual(completions2.isFull(),False)
        self.assertEqual(completions2.getCompletionSize(),1)
        self.assertEqual(completions2.getMaximumSize(),3) 
        self.assertEqual(completions2.isEmpty(),False)
        completion_winner_2 = completions2.getCompletionWinner()
        self.assertEqual(completion_winner_2.isValid(),True)
        self.assertEqual(completion_winner_2.isTransitionalCandidate(),False)
        self.assertEqual(completion_winner_2.isCompletionCandidate(),True)

        self.assertEqual(round(completion_winner_2.getBearsCompletionPerformance(),2),1.2)
        self.assertEqual(round(completion_winner_2.getBullsCompletionPerformance(),2),2.48)
        self.assertEqual(round(completion_winner_2.getBabadjouCompletionPerformance(),2),round(1.2+2.48,2))
        self.assertEqual(completion_winner_2.matchesBabadjouCompletionTarget(),False)




##############################################################################################################
#
#  AveragePriceSpreadBasedWinners: Adding random entries into the system. Then using transition_type
#  based on 'Average Price Spread on the Assembly Line' to select Bulls and Bears to move items. 
#  Additionally, another part of this test will
#  use minmum hold time to make sure we can have assets not sell earlier than the minimal hold time specified. 
#
#@unittest.skip("Taking a break now")
class AveragePriceSpreadBasedWinners(TestCase):
  base_name = 'Test Babadjou Strategy based on the Average Price Spread on the Assembly Line'
  description = 'Description of Test for the AveragePriceSpreadBasedWinners'
  max_roundtrips = 20
  etf = 'LABB'
  bullish = 'LABU'
  bearish = 'LABD'
  cost_basis_per_roundtrip = 1500
  initial_budget = 100000
  profit_basis_per_roundtrip = 30
  bull_prices=[16.29,16.31,16.41,16.34,16.23, 16.18,16.37,16.49,16.95,16.35, 16.29,16.31,16.41,16.34,16.23, 16.18,16.37,16.49,16.55,16.35]
  bear_prices=[31.44,31.40,31.29,31.26,31.19, 31.42,31.20,31.39,31.26,31.09, 31.42,31.45,32.29,33.26,30.19, 31.14,91.40,31.49,31.16,31.10]
  current_times=['2020-08-03 04:05:00-04:00','2020-08-03 09:05:00-04:00','2020-08-03 11:15:00-04:00','2020-08-03 11:16:00-04:00',
                 '2020-08-03 11:45:00-04:00','2020-08-03 11:49:24-04:00','2020-08-03 11:55:00-04:00','2020-08-03 13:15:00-04:00',
                 '2020-08-04 10:45:00-04:00','2020-08-04 10:40:24-04:00','2020-08-04 11:55:00-04:00','2020-08-04 14:15:00-04:00',
                 '2020-08-05 09:45:00-04:00','2020-08-05 11:29:24-04:00','2020-08-05 11:35:03-04:00','2020-08-05 13:15:00-04:00',
                 '2020-08-05 15:55:00-04:00','2020-08-05 15:56:00-04:00','2020-08-05 15:56:30-04:00','2020-08-05 15:57:00-04:00']
  internal_name='dschang'

  @classmethod 
  def setUpTestData(self):

    strategy1 = EquityStrategy.objects.create(name='My valid Equity Strategy',description='This is just a test',
        strategy_class='Bullish Bearish',strategy_category='Babadjou',visibility=False,
      minimum_entries_before_trading=4, trade_only_after_fully_loaded=False,manual_asset_composition=True,
      automatic_generation_client_order_id=True)

    self.entry1_id = strategy1.pk 

    disposition1 = DispositionPolicy.objects.create(in_transition_profit_policy=True,in_transition_profit_target_ratio='.25',
      completion_profit_policy=True,completion_complete_target_ratio='.40', strategy=strategy1,in_transition_strategy_type='Price Based Average Spread',
      in_transition_asset_composition='1Bull x 2Bear',in_transition_entry_strategy='bestbull_and_bestbear',
      in_transition_load_factor='50')
    self.disposition1_id = disposition1.pk 

    nasdaq=RobotEquitySymbols.objects.create(name='Nasdaq',symbol=self.etf,bullishSymbol=self.bullish,bearishSymbol=self.bearish)
    robot1=ETFAndReversePairRobot.objects.create(name=self.base_name,description=self.description,
            portfolio=None,strategy=strategy1,symbols=nasdaq,enabled=True,owner=None,visibility=True,
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
  def testBabadjouPriceBasedWinningRoundtrips(self):
    self.loadData(count=3)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    index=3
    for index in [3,4,8]:
      payload = self.getTradeInformation(index=index)
      self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
      self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
      self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
      self.assertEqual(robot_0.getSymbol(),self.etf) 
      self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
      self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 

      stable = robot_0.getStableRoundTrips()
      self.assertEqual(stable.getSize(),3)
      self.assertEqual(stable.getStableSize(),3)
      self.assertEqual(stable.isFullyLoaded(),False)
      self.assertEqual(stable.isEmpty(),False) 

      if index==3:
        winner_transition = BabadjouWinnerRoundTrip(robot=robot_0)
        self.assertEqual(winner_transition.isValid(),True)
        self.assertEqual(winner_transition.isTransitionalCandidate(),True)
        self.assertEqual(winner_transition.isCompletionCandidate(),False)
        report_data = winner_transition.getTransitionCandidateReportData()
        self.assertEqual(report_data['bulls_length'],1)  
        self.assertEqual(float(report_data['performance_target']),7.5) 
        self.assertEqual(round(float(report_data['total_performance']),2),-10.9) 
        self.assertEqual(winner_transition.matchesBabadjouTransitionTarget(),False)

      if index==4:
        winner_transition = BabadjouWinnerRoundTrip(robot=robot_0)
        self.assertEqual(winner_transition.isValid(),True)
        self.assertEqual(winner_transition.isTransitionalCandidate(),True)
        self.assertEqual(winner_transition.isCompletionCandidate(),False)
        report_data = winner_transition.getTransitionCandidateReportData()
        self.assertEqual(report_data['bulls_length'],1)  
        self.assertEqual(float(report_data['performance_target']),7.5) 
        self.assertEqual(round(float(report_data['total_performance']),2),-19.32) 
        self.assertEqual(winner_transition.matchesBabadjouTransitionTarget(),False)
        completions = BabadjouCompletionCandidates(robot=robot_0)
        self.assertEqual(completions.isFull(),False)
        self.assertEqual(completions.getCompletionSize(),0)
        self.assertEqual(completions.isEmpty(),True)
        self.assertEqual(completions.getMaximumSize(),None)
        self.assertEqual(completions.getCompletionWinner(),None)
        completions_data = completions.getCompletionCandidatesData()
        self.assertEqual(completions_data['summary_data']['entries'],0)
        self.assertEqual(completions_data['content_data'],[])

      if index==8:
        winner_transition = BabadjouWinnerRoundTrip(robot=robot_0)
        self.assertEqual(winner_transition.isValid(),True)
        self.assertEqual(winner_transition.isTransitionalCandidate(),True)
        self.assertEqual(winner_transition.isCompletionCandidate(),False)
        report_data = winner_transition.getTransitionCandidateReportData()
        self.assertEqual(report_data['bulls_length'],1)  
        self.assertEqual(float(report_data['performance_target']),7.5) 
        self.assertEqual(round(float(report_data['total_performance']),2),17.16) 
        self.assertEqual(winner_transition.matchesBabadjouTransitionTarget(),True)
        winner_transition.moveToTransition()
        stable1 = robot_0.getStableRoundTrips()
        self.assertEqual(stable1.getSize(),0)
        self.assertEqual(stable1.getStableSize(),0)
        self.assertEqual(stable1.isFullyLoaded(),False)
        self.assertEqual(stable1.isEmpty(),True) 
        winner2_transition = BabadjouWinnerRoundTrip(robot=robot_0)
        self.assertEqual(winner2_transition.isValid(),False)
        self.assertEqual(winner2_transition.isTransitionalCandidate(),False)
        self.assertEqual(winner2_transition.isCompletionCandidate(),False)
        completions = BabadjouCompletionCandidates(robot=robot_0)
        self.assertEqual(completions.isFull(),False)
        self.assertEqual(completions.getCompletionSize(),1)
        self.assertEqual(completions.getMaximumSize(),3) 
        self.assertEqual(completions.isEmpty(),False)
        completions_data = completions.getCompletionCandidatesData()
        self.assertEqual(completions_data['summary_data']['entries'],1)
        self.assertEqual(len(completions_data['content_data']),1)
        completion_winner_1 = completions.getCompletionWinner()

        self.assertEqual(completion_winner_1.isValid(),True)
        self.assertEqual(completion_winner_1.isTransitionalCandidate(),False)
        self.assertEqual(completion_winner_1.isCompletionCandidate(),True)

        #Move to Completion ...
        completion_winner_1.moveToCompletion()
        
        completions_after = BabadjouCompletionCandidates(robot=robot_0)
        self.assertEqual(completions_after.isFull(),False)
        self.assertEqual(completions_after.getCompletionSize(),0)
        self.assertEqual(completions_after.isEmpty(),True)
        self.assertEqual(completions_after.getMaximumSize(),None) 
        self.assertEqual(completions_after.getCompletionWinner(),None) 
        self.assertEqual(completions_after.getCompletionCandidatesData()['content_data'],[])    
        self.assertEqual(completions_after.getMaximumSize(),None) 


##############################################################################################################
#
#  AveragePriceSpreadTwoBasedWinners: Adding random entries into the system. Then using transition_type
#  based on 'Average Price Spread on the Assembly Line'. We only focus on the elligible entries to calculate the average
#  to select Bulls and Bears to move items. Additionally, another part of this test will
#  use minmum hold time to make sure we can have assets not sell earlier than the minimal hold time specified. 
#
#@unittest.skip("Taking a break now")
class AveragePriceSpreadTwoBasedWinners(TestCase):
  base_name = 'Test Babadjou Strategy based on the Average Price Spread on the Assembly Line'
  description = 'Description of Test for the AveragePriceSpreadBasedWinners'
  max_roundtrips = 20
  etf = 'HEY'
  bullish = 'REDX'
  bearish = 'XDER'
  cost_basis_per_roundtrip = 1500
  initial_budget = 100000
  profit_basis_per_roundtrip = 30
  bull_prices=[16.29,16.31,16.41,16.34,16.23, 16.18,16.37,16.49,16.95,16.35, 16.29,16.31,16.41,16.34,16.23, 16.18,16.37,16.49,16.55,16.35]
  bear_prices=[31.44,31.40,31.29,31.26,31.19, 31.42,31.20,31.39,31.26,31.09, 31.42,31.45,32.29,33.26,30.19, 31.14,91.40,31.49,31.16,31.10]
  current_times=['2020-08-03 04:05:00-04:00','2020-08-03 09:05:00-04:00','2020-08-03 11:15:00-04:00','2020-08-03 11:16:00-04:00',
                 '2020-08-03 11:45:00-04:00','2020-08-03 11:49:24-04:00','2020-08-03 11:55:00-04:00','2020-08-03 13:15:00-04:00',
                 '2020-08-04 10:45:00-04:00','2020-08-04 10:40:24-04:00','2020-08-04 11:55:00-04:00','2020-08-04 14:15:00-04:00',
                 '2020-08-05 09:45:00-04:00','2020-08-05 11:29:24-04:00','2020-08-05 11:35:03-04:00','2020-08-05 13:15:00-04:00',
                 '2020-08-05 15:55:00-04:00','2020-08-05 15:56:00-04:00','2020-08-05 15:56:30-04:00','2020-08-05 15:57:00-04:00']
  internal_name='bafang'

  @classmethod 
  def setUpTestData(self):

    strategy1 = EquityStrategy.objects.create(name='My valid Equity Strategy',description='This is just a test',
        strategy_class='Bullish Bearish',strategy_category='Babadjou',visibility=False,
      minimum_entries_before_trading=4, trade_only_after_fully_loaded=False,manual_asset_composition=True,
      automatic_generation_client_order_id=True)

    self.entry1_id = strategy1.pk 

    disposition1 = DispositionPolicy.objects.create(in_transition_profit_policy=True,in_transition_profit_target_ratio='.25',
      completion_profit_policy=True,completion_complete_target_ratio='.40', strategy=strategy1,in_transition_strategy_type='Price Based Average Spread 2',
      in_transition_asset_composition='1Bull x 1Bear',in_transition_entry_strategy='bestbull_and_bestbear',
      in_transition_load_factor='50')
    self.disposition1_id = disposition1.pk 

    nasdaq=RobotEquitySymbols.objects.create(name='Nasdaq',symbol=self.etf,bullishSymbol=self.bullish,bearishSymbol=self.bearish)
    robot1=ETFAndReversePairRobot.objects.create(name=self.base_name,description=self.description,
            portfolio=None,strategy=strategy1,symbols=nasdaq,enabled=True,owner=None,visibility=True,
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
  def testBabadjouPriceBasedWinningRoundtrips(self):
    self.loadData(count=10)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    # These are the Basic Initialization Functions of the Class
    index=10
    for index in [10,11,12]:
      payload = self.getTradeInformation(index=index)
      self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
      self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
      self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
      self.assertEqual(robot_0.getSymbol(),self.etf) 
      self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
      self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 

      stable = robot_0.getStableRoundTrips()
      self.assertEqual(stable.getSize(),10)
      self.assertEqual(stable.getStableSize(),10)
      self.assertEqual(stable.isFullyLoaded(),False)
      self.assertEqual(stable.isEmpty(),False) 

      if index==10:
        winner_transition = BabadjouWinnerRoundTrip(robot=robot_0)
        self.assertEqual(winner_transition.isValid(),True)
        self.assertEqual(winner_transition.isTransitionalCandidate(),True)
        self.assertEqual(winner_transition.isCompletionCandidate(),False)
        report_data = winner_transition.getTransitionCandidateReportData()
        self.assertEqual(report_data['bulls_length'],1)  
        self.assertEqual(float(report_data['performance_target']),7.5) 
        self.assertEqual(round(float(report_data['total_performance']),2),4.58) 
        self.assertEqual(winner_transition.matchesBabadjouTransitionTarget(),False)

      if index==11:
        winner_transition = BabadjouWinnerRoundTrip(robot=robot_0)
        self.assertEqual(winner_transition.isValid(),True)
        self.assertEqual(winner_transition.isTransitionalCandidate(),True)
        self.assertEqual(winner_transition.isCompletionCandidate(),False)
        report_data = winner_transition.getTransitionCandidateReportData()
        self.assertEqual(report_data['bulls_length'],1)  
        self.assertEqual(float(report_data['performance_target']),7.5) 
        self.assertEqual(round(float(report_data['total_performance']),2),-1.86) 
        self.assertEqual(winner_transition.matchesBabadjouTransitionTarget(),False)
        completions = BabadjouCompletionCandidates(robot=robot_0)
        self.assertEqual(completions.isFull(),False)
        self.assertEqual(completions.getCompletionSize(),0)
        self.assertEqual(completions.isEmpty(),True)
        self.assertEqual(completions.getMaximumSize(),None)
        self.assertEqual(completions.getCompletionWinner(),None)
        completions_data = completions.getCompletionCandidatesData()
        self.assertEqual(completions_data['summary_data']['entries'],0)
        self.assertEqual(completions_data['content_data'],[])

      if index==12:
        winner_transition = BabadjouWinnerRoundTrip(robot=robot_0)
        self.assertEqual(winner_transition.isValid(),True)
        self.assertEqual(winner_transition.isTransitionalCandidate(),True)
        self.assertEqual(winner_transition.isCompletionCandidate(),False)
        report_data = winner_transition.getTransitionCandidateReportData()
        self.assertEqual(report_data['bulls_length'],1)  
        self.assertEqual(float(report_data['performance_target']),7.5) 
        self.assertEqual(round(float(report_data['total_performance']),2),22.8) 
        self.assertEqual(winner_transition.matchesBabadjouTransitionTarget(),True)
        winner_transition.moveToTransition()
        stable1 = robot_0.getStableRoundTrips()
        self.assertEqual(stable1.getSize(),8)
        self.assertEqual(stable1.getStableSize(),8)
        self.assertEqual(stable1.isFullyLoaded(),False)
        self.assertEqual(stable1.isEmpty(),False) 
        winner2_transition = BabadjouWinnerRoundTrip(robot=robot_0)
        self.assertEqual(winner2_transition.isValid(),True)
        self.assertEqual(winner2_transition.isTransitionalCandidate(),True)
        self.assertEqual(winner2_transition.isCompletionCandidate(),False)
        completions = BabadjouCompletionCandidates(robot=robot_0)
        self.assertEqual(completions.isFull(),False)
        self.assertEqual(completions.getCompletionSize(),1)
        self.assertEqual(completions.getMaximumSize(),5) 
        self.assertEqual(completions.isEmpty(),False)
        completions_data = completions.getCompletionCandidatesData()
        self.assertEqual(completions_data['summary_data']['entries'],1)
        self.assertEqual(len(completions_data['content_data']),1)
        completion_winner_1 = completions.getCompletionWinner()

        self.assertEqual(completion_winner_1.isValid(),True)
        self.assertEqual(completion_winner_1.isTransitionalCandidate(),False)
        self.assertEqual(completion_winner_1.isCompletionCandidate(),True)

        #Move to Completion ...
        completion_winner_1.moveToCompletion()
        
        completions_after = BabadjouCompletionCandidates(robot=robot_0)
        self.assertEqual(completions_after.isFull(),False)
        self.assertEqual(completions_after.getCompletionSize(),0)
        self.assertEqual(completions_after.isEmpty(),True)
        self.assertEqual(completions_after.getMaximumSize(),None) 
        self.assertEqual(completions_after.getCompletionWinner(),None) 
        self.assertEqual(completions_after.getCompletionCandidatesData()['content_data'],[])    
        self.assertEqual(completions_after.getMaximumSize(),None) 


if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)
