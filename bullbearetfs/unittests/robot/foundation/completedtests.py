from datetime import datetime, time
import logging, unittest
import sys,json,xmlrunner
from django.utils import timezone
from django.test import TestCase

# Import Models
from bullbearetfs.strategy.models import EquityStrategy, AcquisitionPolicy,DispositionPolicy,OrdersManagement,PortfolioProtectionPolicy
from bullbearetfs.robot.models import ETFAndReversePairRobot,TradeDataHolder 
from bullbearetfs.robot.foundation.roundtrip import RoundTrip 
from bullbearetfs.strategies.babadjou import BabadjouWinnerRoundTrip, BabadjouCompletionCandidates
from bullbearetfs.robot.symbols.models import RobotEquitySymbols
from bullbearetfs.robot.activitysentiments.models import EquityAndMarketSentiment
from bullbearetfs.robot.budget.models import RobotBudgetManagement
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, strToDatetime
logger = logging.getLogger(__name__)

"""
  RoundTrip Testing Module

  This class tests the Move from Stable to Transition and Completion (with emphasis on Completion) based on 
  various Completion criteria. Type. Two major classes are used for that purpose:
     BabadjouWinnerRoundTrip and BabadjouCompletionCandidate Interfaces/Classes
 
  Additionally, some functionality around Regression is also tested. Regression focuses on when an asset fails
  to reach the expected profit within the specified Hold time. Some concession needs to be made to allow the
  asset to be sold anyway at discounts.
  The application was intentionally implemented to be flexible when it comes to how to ...
  Because we are investing in leveraged ETFs, it is important not to hold the assets for too long. Turnover of the asset
  is therefore important. 
 
 
  Functionality in the BabadjouWinnerRoundTrip has been grouped in the following areas:
   
    Winner based on various types of criteria: Performance, Buy price, Inner Spread.
    Validate that we recognize reaching Regression Status
    Validate the various levels of Regression: Yellow, Orange, Red
    Validate that we might prevent additional Stable to move to transition because max has been reached.
  
    Construction of "Transition" candidacy (none exist, we building it)
    Construction of "Completion" candidacy (One exists already, is it good enough to be move to completion)
    Selection of the proper bulls and bears to be part of the Group
    Calculation of their performance to Transition, Generation of Data to save the entry into the System.
    Calculation of their performance to completion.
    Usage of min_hold_time to ensure that we can't move entries, unless they have been deemed elligible based on Age.
    Usage of various criteria to move entries. Performance, Buy price, Inner Spread, Assembly Line Spread, Average Costs
 
  Tests the functionality around:
    InvalidDispositionScenarios: Performance Based Winners focus on the move to Transition based on the StableValue().
      By focusing on the StableValue(), we focus only on how Bull/Bear are performing to select entries then move them.
      Number of Test Classes Planned: 5
      Total Number of Test Functions: 5 x 5
      Number of remaining Functions: 0
 
    MiscelleneousStrategyScenarios: Performance Based Winners focus on the move to Transition based on the StableValue().
      By focusing on the StableValue(), we focus only on how Bull/Bear are performing to select entries then move them.
      Number of Test Classes Planned: 5
      Total Number of Test Functions: 5 x 5
      Number of remaining Functions: 0

     LargNumberOfRobots: INCOMPLETE
         Number of Test Classes Planned: 4
         Total Number of Test Functions: many
         Number of remaining Classes: 2 
"""

def test_babadjou_completeness_roundtrip_dummy(request):
  """
    Dummy function needed to force rebuild on change.
  """
  pass

#####################################################################################################
#
#  InvalidDispositionScenarios: Check how to deal with A variety of invalid scenarios.
#   Want to ensure they will be handle gracefully, in case a bad value is entered.
#
#@unittest.skip("Taking a break now")
class InvalidDispositionScenarios(TestCase):
  base_name = 'InvalidDispositionScenarios'
  description = 'Description of Test for the Invalid Disposition Scenarios of Babadjou Winners'
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

  #Invalid Entry Strategy (bestbull_and_bestbear) ==> (bestbest_and_bestbest)
  #completion_profit_policy
  #@unittest.skip("Taking a break now")
  def testInvalidCompletionProfitPolicy(self):
    self.loadData(count=3)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    disposition = DispositionPolicy.objects.get(pk=self.disposition1_id)
    #Update the Disposition to reflect what we want.
    disposition.in_transition_asset_composition='1Bull x 4Bear'
    disposition.save()
    # These are the Basic Initialization Functions of the Class
    index=3
    payload = self.getTradeInformation(index=index)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 

  #Invalid Entry Strategy (bestbull_and_bestbear) ==> (bestbest_and_bestbest)
  #in_transition_profit_policy
  #@unittest.skip("Taking a break now")
  def testInvalidTransitionProfitPolicy(self):
    self.loadData(count=3)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    disposition = DispositionPolicy.objects.get(pk=self.disposition1_id)
    #Update the Disposition to reflect what we want.
    disposition.in_transition_asset_composition='1Bull x 4Bear'
    disposition.save()
    # These are the Basic Initialization Functions of the Class
    index=3
    payload = self.getTradeInformation(index=index)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 

  #Invalid Entry Strategy (bestbull_and_bestbear) ==> (bestbest_and_bestbest)
  #@unittest.skip("Taking a break now")
  def testInvalidEntryStrategy(self):
    self.loadData(count=3)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    disposition = DispositionPolicy.objects.get(pk=self.disposition1_id)
    #Update the Disposition to reflect what we want.
    disposition.in_transition_asset_composition='1Bull x 4Bear'
    disposition.save()
    # These are the Basic Initialization Functions of the Class
    index=3
    payload = self.getTradeInformation(index=index)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 

  #Composition: '1Bull x 4Bear'
  #@unittest.skip("Taking a break now")
  def testInvalidBearInComposition(self):
    self.loadData(count=3)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    disposition = DispositionPolicy.objects.get(pk=self.disposition1_id)
    #Update the Disposition to reflect what we want.
    disposition.in_transition_asset_composition='1Bull x 4Bear'
    disposition.save()
    # These are the Basic Initialization Functions of the Class
    index=3
    payload = self.getTradeInformation(index=index)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 

  #Composition: '0Bull x 1Bear'
  #@unittest.skip("Taking a break now")
  def testInvalidBullInComposition(self):
    self.loadData(count=3)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    disposition = DispositionPolicy.objects.get(pk=self.disposition1_id)
    #Update the Disposition to reflect what we want.
    disposition.in_transition_asset_composition='1Bull x 4Bear'
    disposition.save()
    # These are the Basic Initialization Functions of the Class
    index=3
    payload = self.getTradeInformation(index=index)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 

  #Composition: '1Bull x 1Bear'
  #@unittest.skip("Taking a break now")
  def testComposition1Bull1BearBestAndBest(self):
    self.loadData(count=3)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    disposition = DispositionPolicy.objects.get(pk=self.disposition1_id)

    #Update the Disposition to reflect what we want.
    disposition.in_transition_asset_composition='1Bull x 1Bear'
    disposition.save()

    # These are the Basic Initialization Functions of the Class
    index=3
    payload = self.getTradeInformation(index=index)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bullish) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bearish) 
    self.assertEqual(robot_0.getSymbol(),self.etf) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices[index]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices[index]) 


  #Composition: '3Bull x 3Bear'
  #@unittest.skip("Taking a break now")
  def testComposition3Bull3BearBestAndBest(self):
    self.loadData(count=1)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_0_id)
    disposition = DispositionPolicy.objects.get(pk=self.disposition1_id)

    #Update the Disposition to reflect what we want.
    disposition.in_transition_asset_composition='3Bull x 3Bear'
    disposition.save()

    index=1
    for index in [1,2,3,4,5,6,7,8,9,10]:
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

      if index==1:
        winner_transition = BabadjouWinnerRoundTrip(robot=robot_0)
        self.assertEqual(winner_transition.isValid(),False)
        self.assertEqual(winner_transition.isTransitionalCandidate(),False)
        self.assertEqual(winner_transition.isCompletionCandidate(),False)

      if index==2:
        winner_transition = BabadjouWinnerRoundTrip(robot=robot_0)
        self.assertEqual(winner_transition.isValid(),True)
        self.assertEqual(winner_transition.isTransitionalCandidate(),True)
        self.assertEqual(winner_transition.isCompletionCandidate(),False)

    # These are the Basic Initialization of the Class
     

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


#####################################################################################################
#
# LargNumberOfRobots: Adding a large number of robots
#
#
#@unittest.skip("Taking a break now")
class LargNumberOfRobots(TestCase):
  base_name = ['Dow Jones','Small Cap']
  description = ['Description1','Description2']
  max_roundtrips = [20,20]
  etfs  = ['DIA','PPPP']
  bulls = ['SDOW','TNA']
  bears = ['UDOW','TZA']

  current_times=['2020-08-03 04:05:00-04:00','2020-08-03 09:05:00-04:00','2020-08-03 11:15:00-04:00','2020-08-03 11:16:00-04:00',
                 '2020-08-03 11:45:00-04:00','2020-08-03 11:49:24-04:00','2020-08-03 11:55:00-04:00','2020-08-03 13:15:00-04:00',
                 '2020-08-04 10:45:00-04:00','2020-08-04 10:40:24-04:00','2020-08-04 11:55:00-04:00','2020-08-04 14:15:00-04:00',
                 '2020-08-05 09:45:00-04:00','2020-08-05 11:29:24-04:00','2020-08-05 11:35:03-04:00','2020-08-05 13:15:00-04:00']

  cost_PR = [2000,1000]
  profit_PR = [100,50]
  
  bull_prices_dow = [120.45,122.33,121.67,125.22,124.20, 124.10,130.11,135.23,137.11,140.10,120.45,122.33,121.67,125.22,124.20, 124.10,130.11,135.23,137.11,140.10]
  bear_prices_dow = [29.0,28.5,28.00,27.65,27.64 ,29.0,28.5,28.00,27.65,27.64,29.0,28.5,28.00,27.65,27.64 ,29.0,28.5,28.00,27.65,27.64]
  
  bull_prices_tna = [29.39,29.44,29.57,29.82,29.99, 29.39,29.44,29.57,29.82,29.99, 29.39,29.44,29.57,29.82,29.99,29.82,29.99 ]
  bear_prices_tna = [18.83,18.73,18.47,18.55,18.34, 18.83,18.73,18.47,18.55,18.34, 18.83,18.73,18.47,18.55,18.34,18.55,18.34 ]

  internal_name=['foumban','ngaoundere']

  @classmethod 
  def setUpTestData(self):
#################################DOW JONES ##########
    dow=RobotEquitySymbols.objects.create(name=self.base_name[0],symbol=self.etfs[0],bullishSymbol=self.bulls[0],bearishSymbol=self.bears[0])
    robot_dow=ETFAndReversePairRobot.objects.create(name=self.base_name[0],description=self.description[0],
            portfolio=None,strategy=None,symbols=dow,enabled=True,owner=None,visibility=True,
            version='1.0.0', max_hold_time='14',minimum_hold_time='1',hold_time_includes_holiday=True,
            sell_remaining_before_buy=False,liquidate_on_next_opportunity=False,internal_name=self.internal_name[0],
            max_roundtrips=self.max_roundtrips[0],cost_basis_per_roundtrip=self.cost_PR[0],
            profit_target_per_roundtrip=self.profit_PR[0])    
    self.robot_dow_id =robot_dow.pk
    sentiment_dow = EquityAndMarketSentiment.objects.create(pair_robot=robot_dow,influences_acquisition=True,circuit_breaker=False,
                                                          sentiment_feed='Automatic')
 
    self.s0_id = sentiment_dow.pk
    bm_dow = RobotBudgetManagement.objects.create(pair_robot=robot_dow,use_percentage_or_fixed_value='Number')

# #################################Russell Robot #################
    russel=RobotEquitySymbols.objects.create(name=self.base_name[1],symbol=self.etfs[1],bullishSymbol=self.bulls[1],bearishSymbol=self.bears[1])
    robot_russel=ETFAndReversePairRobot.objects.create(name=self.base_name[1],description=self.description[1],
            portfolio=None,strategy=None,symbols=russel,enabled=True,owner=None,visibility=True,
            version='1.0.0', max_hold_time='14',minimum_hold_time='1',hold_time_includes_holiday=True,
            sell_remaining_before_buy=False,liquidate_on_next_opportunity=False,internal_name=self.internal_name[1],
            max_roundtrips=self.max_roundtrips[1],cost_basis_per_roundtrip=self.cost_PR[1],
            profit_target_per_roundtrip=self.profit_PR[1])    
    self.robot_russel_id =robot_russel.pk
    sentiment_russel = EquityAndMarketSentiment.objects.create(pair_robot=robot_russel,influences_acquisition=True,circuit_breaker=False,
                                                          sentiment_feed='Automatic')
 
    self.s0_id = sentiment_russel.pk
    bm_russel = RobotBudgetManagement.objects.create(pair_robot=robot_russel,use_percentage_or_fixed_value='Number')

  def getTradeInformationRussell(self,index):
    information = dict()
    information[self.bulls[1]]=self.bull_prices_tna[index]
    information[self.bears[1]]=self.bear_prices_tna[index] 
    information['timestamp'] = self.current_times[index]
    #print("\nHENRI: {0}".format(index))
    return information 

  def getTradeInformationDow(self,index):
    information = dict()
    information[self.bulls[0]]=self.bull_prices_dow[index]
    information[self.bears[0]]=self.bear_prices_dow[index] 
    information['timestamp'] = self.current_times[index]
    #print("\nHENRI: {0}".format(index))
    return information 

  def loadData(self,count):
    robot_russell = ETFAndReversePairRobot.objects.get(pk=self.robot_russel_id)
    robot_dow = ETFAndReversePairRobot.objects.get(pk=self.robot_dow_id)
    index = 0
    for n in self.current_times:
      payload_tna = self.getTradeInformationRussell(index=index)
      payload_dow = self.getTradeInformationDow(index=index)
      self.assertEqual(robot_russell.setCurrentValues(current_payload=payload_tna),True)
      self.assertEqual(robot_dow.setCurrentValues(current_payload=payload_dow),True)
      if index < count:
        robot_russell.addNewRoundtripEntry()
        robot_dow.addNewRoundtripEntry()
      index +=1


  #@unittest.skip("Taking a break now")
  def testRoundtripBasicRobotRussell(self):
    self.loadData(count=14)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_russel_id)
    # These are the Basic Initialization Functions of the Class
    index = 15
    payload = self.getTradeInformationRussell(index=index)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bulls[1]) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bears[1]) 
    self.assertEqual(robot_0.getSymbol(),self.etfs[1]) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices_tna[index]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices_tna[index]) 

    #robot_0.addNewRoundtripEntry()
    stable = robot_0.getStableRoundTrips()
    self.assertEqual(stable.getSize(),index-1)
    self.assertEqual(stable.getStableSize(),index-1)
    self.assertEqual(stable.isFullyLoaded(),False)
    self.assertEqual(stable.isEmpty(),False) 

    self.assertEqual(round(stable.getAverageBullCostBasis(),2),1002.7)
    self.assertEqual(round(stable.getAverageBearCostBasis(),2),999.05)
    self.assertEqual(stable.getLowestBullCostBasis().getBullCostBasis(),989.67)
    self.assertEqual(stable.getLowestBearCostBasis().getBearCostBasis(),992.69)
    self.assertEqual(stable.getHighestBullCostBasis().getBullCostBasis(),1013.88)
    self.assertEqual(stable.getHighestBearCostBasis().getBearCostBasis(),1008.7)
    #stable.printEntries()
  #@unittest.skip("Taking a break now")
  def testRoundtripBasicRobotDow(self):
    self.loadData(count=14)
    robot_0 = ETFAndReversePairRobot.objects.get(pk=self.robot_dow_id)
    # These are the Basic Initialization Functions of the Class
    index=15
    payload = self.getTradeInformationDow(index=index)
    self.assertEqual(robot_0.setCurrentValues(current_payload=payload),True)
    self.assertEqual(robot_0.getBullishSymbol(),self.bulls[0]) 
    self.assertEqual(robot_0.getBearishSymbol(),self.bears[0]) 
    self.assertEqual(robot_0.getSymbol(),self.etfs[0]) 
    self.assertEqual(robot_0.getCurrentBullPrice(),self.bull_prices_dow[index]) 
    self.assertEqual(robot_0.getCurrentBearPrice(),self.bear_prices_dow[index]) 

    #robot_0.addNewRoundtripEntry()
    stable = robot_0.getStableRoundTrips()
    self.assertEqual(stable.getSize(),index-1)
    self.assertEqual(stable.getStableSize(),index-1)
    self.assertEqual(stable.isFullyLoaded(),False)
    self.assertEqual(stable.isEmpty(),False) 

    self.assertEqual(round(stable.getAverageBullCostBasis(),2),982.08)
    self.assertEqual(round(stable.getAverageBearCostBasis(),2),996.48)
    self.assertEqual(round(stable.getLowestBullCostBasis().getBullCostBasis(),2),946.61)
    self.assertEqual(stable.getLowestBearCostBasis().getBearCostBasis(),986)
    self.assertEqual(stable.getHighestBullCostBasis().getBullCostBasis(),1040.88)
    self.assertEqual(stable.getHighestBearCostBasis().getBearCostBasis(),1008.0)

if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)
