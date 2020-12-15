import logging
from bullbearetfs.strategies.strategybase import EggheadBaseStrategy
from bullbearetfs.strategies.strategybase import WORKFLOW_ENTRIES, PAIRS_ENTRIES
from bullbearetfs.robot.foundation.stableroundtrip import StableRoundTrips
from bullbearetfs.robot.foundation.roundtrip import RoundTrip
from bullbearetfs.utilities.core import getTimeZoneInfo, strToDatetime, shouldUsePrint, displayOutput,displayError

"""
  This module contains the implementation required in order for the 
  Babadjou Strategy to run successfully on the Egghead platform.
  
  The Babadjou Strategy belongs to the ... Class of Strategies and the ... Family of Strategies.
  Reminder: 
  The Babadjou Strategy follows the approach of all Base Strategies on the Egghead platform.
  All Strategies on the Egghead Platform operate on the same concept of simulteneous Bull / Bear Acquisition.
  
  Acquisition Conditions:
    Three main conditions are provided. Time Proximity, Price Proximity and Volume Proximity.
    The platform can be configured to use or a combination of these options.

  Disposition Conditions:
    Disposition in the Babadjou strategy goes through a transition phase. During this phase, one of the Bull/Bear
    of a given RoundTrip is sold. The RoundTrip is said to be 'In Transition'.
    At a later time, when conditions are met, the other side of the RoundTrip is sold.

  List the classes of the module here:
  BabadjouStrategy(EggheadBaseStrategy)
  What is the Babadjou Investment Strategy on the Egghead Platform?

  BabadjouWinnerRoundTrip:
  A BabadjouWinnerRoundTrip is created, when a combination has been met the expected conditions.

  BabadjouCompletionCandidates:
  This represents a list of potential candidates taken from the BabadjouWinnerRoundTrip. 

"""

logger = logging.getLogger(__name__)


class BabadjouWinnerRoundTrip():
  """
   A BabadjouWinnerRoundTrip Class represents an instance of classes that implement the Babadjou Investment Strategy.
   A BabadjouCompletionCandidate represents an instance of classes that captures lists of candidates to be moved
   to Completion via the Strategy.
 
    List all the Methods here:
  """
  def __init__(self,robot,transition_root_id=None):
    self.robot = robot
    
    if transition_root_id == None:
      self.candidacy='Transition'
      stable = robot.getStableRoundTrips()
      bulls_direction = robot.getBestOrWorstBullInTransitionStrategy()
      bears_direction = robot.getBestOrWorstBearInTransitionStrategy()
      self.bulls_count     = robot.getNumberOfBullsInTransitionComposition()
      self.bears_count     = robot.getNumberOfBearsInTransitionComposition()
      self.target     = robot.getInTransitionProfitTarget() 
      self.winning_bulls=stable.getStableWinningBulls(count=self.bulls_count,exclude_list=None, best=bulls_direction)
      self.winning_bears=stable.getStableWinningBears(count=self.bears_count,exclude_list=self.winning_bulls, best=bears_direction)
    else:
      self.winning_bulls=[]
      self.winning_bears=[]
      self.candidacy ='Completion'
      self.transition_root_id = transition_root_id
      self.target     = robot.getCompletionProfitTarget() 
      entries = robot.getAllBullishRoundtrips()
      for entry in entries:
        rt = RoundTrip(robot=self.robot,root_id=entry.getOrderClientIDRoot())
        if rt.isInBullishWinningTransition(transition_id=transition_root_id): 
      	  self.winning_bulls.append(rt)
        elif rt.isInBearishWinningTransition(transition_id=transition_root_id):
          self.winning_bears.append(rt)

  def __str__(self):
    return "{}".format(self.getTransitionCandidateReportData())

  def isValid(self):
    return self.isCompletionCandidate() or self.isTransitionalCandidate()

  def isCompletionCandidate(self):
    if self.winning_bulls == None or self.winning_bears == None:
      return False
    return self.candidacy=='Completion' and \
           (len(self.winning_bulls)>0) and (len(self.winning_bears)>0)

  def isTransitionalCandidate(self):
    if self.winning_bulls == None or self.winning_bears == None:
      return False
    return self.candidacy=='Transition' and \
           (self.bulls_count == len(self.winning_bulls)) and \
           (self.bears_count == len(self.winning_bears))

  def printTransitionalCandidateOutput(self):
   if self.isValid():
     if self.isTransitionalCandidate():
       data = self.getTransitionCandidateReportData()
     else:
       data = self.getCompletionCandidateReportData()
     str1= "\nWinning Bulls: Len=[{0}] Perf=[${1:,.2f}] IDs=[ {2}]".format(data['bulls_length'], data['bulls_performance'],data['bulls_ids']) 
     str2= "\nWinning Bears: Len=[{0}] Perf=[${1:,.2f}] IDs=[ {2}]".format(data['bears_length'], data['bears_performance'],data['bears_ids'])  
     str3= "\nPerformance  : Actual[${0:,.2f}] Tgt=[${1:,.2f} ] Matches Tgt? {2}".format(data['total_performance'],data['performance_target'],data['performance_match'])
     return str1 + str2 + str3
   return None 

  def printCompletionCandidateOutput(self):   
   data = self.getCompletionCandidateReportData()
   str1= "\nWinning Bulls: Len=[{0}] Perf=[${1:,.2f}] IDs=[ {2}]".format(data['bulls_length'], data['bulls_performance'],data['bulls_ids']) 
   str2= "\nWinning Bears: Len=[{0}] Perf=[${1:,.2f}] IDs=[ {2}]".format(data['bears_length'], data['bears_performance'],data['bears_ids'])  
   str3= "\nPerformance  : Actual[${0:,.2f}] Tgt=[${1:,.2f} ] Matches Tgt? {2}".format(data['total_performance'],data['performance_target'],data['performance_match'])
   return str1 + str2 + str3

  def getRootOrderClientID(self): 
    if self.isValid():
      if self.isTransitionalCandidate(): 
        p_root=self.robot.getInternalName()
        r_id=self.robot.pk
        bulls_size = len(self.winning_bulls)
        bears_size = len(self.winning_bears)
        transition_root_id = self.robot.generateInTransitionRootOrderClientID(bulls_count=bulls_size,bears_count=bears_size,project_root=p_root,r_id=r_id)
        return transition_root_id
      return self.transitional_root_id
    return None

  def moveToCompletion(self):
    if self.isValid():
      if self.isCompletionCandidate():
        for x in self.winning_bulls:  
          self.robot.moveToCompletion(candidate=x)
        for y in self.winning_bears:
          self.robot.moveToCompletion(candidate=y)
  
  def moveToTransition(self):
    if self.isTransitionalCandidate():
      transition_root_order_client_id = self.getRootOrderClientID() 
      for x in self.winning_bulls:
        x.sellTheBull(transition_root_id=transition_root_order_client_id)
      for x in self.winning_bears:
        x.sellTheBear(transition_root_id=transition_root_order_client_id)

  def getBullsRootIDs(self):
    ids =''
    for x in self.winning_bulls:
      ids += x.getRootOrderClientIDNoInternal() + ' '
    return ids

  def getBearsRootIDs(self):
    ids =''
    for x in self.winning_bears:
      ids += x.getRootOrderClientIDNoInternal() + ' '
    return ids

  def getTotalRoundTripsPerWinner(self):
    if self.isValid():
      return len(self.winning_bulls) + len(self.winning_bears)
    return None 

  def getBullsInTransitionPerformance(self):
    if self.isTransitionalCandidate():
      bulls_stable_values = [ c.getStableBullValue() for c in self.winning_bulls] 
      bulls_total = round(sum(bulls_stable_values),2)
      return bulls_total 
    return None

  def getBearsInTransitionPerformance(self):
    if self.isTransitionalCandidate():
      bears_stable_values = [ c.getStableBearValue() for c in self.winning_bears]  
      bears_total = round(sum(bears_stable_values),2)
      return bears_total 
    return None	

  def getBabadjouTransitionPerformance(self):
    if self.isTransitionalCandidate():
      return round(self.getBullsInTransitionPerformance() + self.getBearsInTransitionPerformance(),2)
    return None 

  def matchesBabadjouTransitionTarget(self):
    if self.isTransitionalCandidate():
      profit = self.getBabadjouTransitionPerformance()
      return profit >= self.target
    return None


  def getBullishBearish(self): 
    b1 = [ c.getIsBullishOrBearishTransition() for c in self.winning_bears] 
    b3 = [ c.getIsBullishOrBearishTransition() for c in self.winning_bulls] 
    print(" Winning bears: Bear is UNREALIZED={}. Winning bulls: Bull is UNREALIZED b3={}.  ".format(b1,b3))


  #
  # Buy Prices Candidate Logic
  #
  def getBullsCurrentValue(self):
    bulls_cb = [ c.getBullCurrentValue() for c in self.winning_bulls] 
    bulls_avg = round(sum(bulls_cb)/len(self.winning_bulls),2)
    return bulls_avg 

  #
  # BuyCandidate Logic
  #
  def getBearsCurrentValue(self):
    bears_cb = [ c.getBearCurrentValue() for c in self.winning_bears] 
    bears_avg = round(sum(bears_cb)/len(self.winning_bears),2)
    return bears_avg 

  #
  # Buy Prices Candidate Logic
  #
  def getBullsCostBasis(self):
    bulls_cb = [ c.getBullCostBasis() for c in self.winning_bulls] 
    bulls_avg = round(sum(bulls_cb)/len(self.winning_bulls),2)
    return bulls_avg 

  #
  # BuyCandidate Logic
  #
  def getBearsCostBasis(self):
    bears_cb = [ c.getBearCostBasis() for c in self.winning_bears] 
    bears_avg = round(sum(bears_cb)/len(self.winning_bears),2)
    return bears_avg 

  #
  # Buy Prices Candidate Logic
  #
  def getBullsBuyPriceAverage(self):
    bulls_prices = [ c.getBullBuyPrice() for c in self.winning_bulls] 
    bulls_total = round(sum(bulls_prices)/len(self.winning_bulls),2)
    return bulls_total 

  #
  # BuyCandidate Logic
  #
  def getBearsBuyPriceAverage(self):
    bears_prices = [ c.getBearBuyPrice() for c in self.winning_bears] 
    bears_total = round(sum(bears_prices)/len(self.winning_bears),2)
    return bears_total 

  #
  # Completion Candidate Logic
  #
  def getBullsCompletionPerformance(self):
    bulls_deltas = [ c.getTransitionalDeltaValue() for c in self.winning_bulls] 
    bulls_total = round(sum(bulls_deltas),2)
    return bulls_total 

  def getBearsCompletionPerformance(self):
    bears_deltas= [ c.getTransitionalDeltaValue() for c in self.winning_bears]  
    bears_total = round(sum(bears_deltas),2)
    return bears_total 
     	
  def getBabadjouCompletionPerformance(self):
    #self.getBullishBearish()
    return round(self.getBullsCompletionPerformance() + self.getBearsCompletionPerformance(),2)

  def matchesBabadjouCompletionTarget(self):
    profit = self.getBabadjouCompletionPerformance()
    return profit >= self.target
  
  def getCompletionCandidateReportData(self):
    response = dict()
    response['bulls_length']=len(self.winning_bulls)
    response['bears_length']=len(self.winning_bears)
    response['bulls_cost_basis']=self.getBullsCostBasis()
    response['bears_cost_basis']=self.getBearsCostBasis()
    response['bulls_current_val']=self.getBullsCurrentValue()
    response['bears_current_val']=self.getBearsCurrentValue()
    response['bulls_ids']=self.getBullsRootIDs()
    response['bears_ids']=self.getBearsRootIDs()
    response['bulls_performance']=self.getBullsCompletionPerformance()
    response['bears_performance']=self.getBearsCompletionPerformance()
    response['total_performance']=self.getBabadjouCompletionPerformance()
    response['performance_target']=self.target
    response['performance_match']=self.matchesBabadjouCompletionTarget()
    return response

  def getTransitionCandidateReportData(self):
    if self.isTransitionalCandidate():
      response = dict()
      response['bulls_length']=len(self.winning_bulls)
      response['bears_length']=len(self.winning_bears)
      response['bulls_ids']=self.getBullsRootIDs()
      response['bears_ids']=self.getBearsRootIDs()
      response['bulls_performance']=self.getBullsInTransitionPerformance()
      response['bears_performance']=self.getBearsInTransitionPerformance()
      response['total_performance']=self.getBabadjouTransitionPerformance()
      response['performance_target']=self.target
      response['performance_match']=self.matchesBabadjouTransitionTarget()
      return response
    return None 

#
# This entity controls how we select candidates to sell and move to Completion.
#
class BabadjouCompletionCandidates():
  def __init__(self,robot):
    self.robot = robot
    self.candidates_list = []
    entries = robot.getBabadjouCompletionCandidates()
    for entry in entries:
      wt = BabadjouWinnerRoundTrip(robot=self.robot,transition_root_id=entry.getWinningOrderClientIDRoot())
      if wt.isCompletionCandidate():
      	self.candidates_list.append(wt)

  def __str__(self):
   return "{0}".format('Hello, these are the Babadjou Strategy Completion Candidates') 

  def printBabadjouTransitionReport(self):
    print("\n--------------------------- Babadjou Strategy Transition to Completion Report----------------- ")
    print("This report should contain the candidates to be moved from Transition to Completion. ")
    print(" --------------------------- --------------------------------- --------------------------------- ")

  def getCompletionCandidatesOutput(self):
  	return None 

  def isEmpty(self):
    return self.getCompletionSize()==0

  def getCompletionSize(self):
  	return len(self.candidates_list)

  def getMaximumSize(self):
    if len(self.candidates_list) == 0:
      return None
    max_entries = self.robot.getMaxNumberOfRoundtrips() / self.candidates_list[0].getTotalRoundTripsPerWinner()
    return int(self.robot.getTransitionLoadFactor() * max_entries)

  def getCompletionWinner(self):
    self.candidates_list.sort(key=lambda wt:wt.getBabadjouCompletionPerformance(),reverse=True) 
    print("Candidates Transition to Completion: {}".format(self.getCompletionCandidatesData()))
    return None if len(self.candidates_list)==0 else self.candidates_list[0] 

  def isFull(self):
    if len(self.candidates_list) == 0:
      return False
    return (self.getCompletionSize() >= (self.getMaximumSize()))

  def getBabadjouTotalPerformance(self):
    total_performance = sum([ c.getBabadjouCompletionPerformance() for c in self.candidates_list])
    return total_performance

  def getBabadjouTotalBullsValue(self):
    total_performance = sum([ c.getBullsCurrentValue() for c in self.candidates_list])
    return total_performance

  def getBabadjouTotalBearsValue(self):
    total_performance = sum([ c.getBearsCurrentValue() for c in self.candidates_list])
    return total_performance

  def getCompletionSummaryDataBasic(self):
    c_list=self.candidates_list
    bulls_avg_buy_price = 0 if len(c_list)==0 else sum([ c.getBullsBuyPriceAverage() for c in c_list])/len(c_list)
    bears_avg_buy_price = 0 if len(c_list)==0 else sum([ c.getBearsBuyPriceAverage() for c in c_list])/len(c_list)
    bulls_current_value = sum([ c.getBullsCurrentValue() for c in c_list])
    bears_current_value = sum([ c.getBearsCurrentValue() for c in c_list])
    bulls_value_ratio = 100 * (bulls_current_value/(bulls_current_value+bears_current_value))
    bears_value_ratio = 100 * (bears_current_value/(bulls_current_value+bears_current_value))

    summary = dict()
    summary['entries']=self.getCompletionSize()
    summary['all_entries_performance']= round(self.getBabadjouTotalPerformance(),2)
    summary['bulls_avg_buy_price']= round(bulls_avg_buy_price,2)
    summary['bears_avg_buy_price']= round(bears_avg_buy_price,2)
    summary['bulls_current_value']= round(bulls_current_value,2)
    summary['bears_current_value']= round(bears_current_value,2)
    summary['bulls_value_ratio']= round(bulls_value_ratio,2)
    summary['bears_value_ratio']= round(bears_value_ratio,2)

    return summary 

  def getCompletionSummaryDataAdvanced(self):
    summary = dict()

  def getCompletionCandidatesData(self):
    #trans_avg_bull_price = 0 if len(self.candidates_list)==0 else sum([ c.getBullsBuyPriceAverage() for c in self.candidates_list])/len(self.candidates_list)
    #trans_avg_bear_price = 0 if len(self.candidates_list)==0 else sum([ c.getBearsBuyPriceAverage() for c in self.candidates_list])/len(self.candidates_list)
    #summary_data = dict()
    #summary_data['entries']=self.getCompletionSize()
    #summary_data['babadjou_avg_bull_price']= round(trans_avg_bull_price,2)
    #summary_data['babadjou_avg_bear_price']= round(trans_avg_bear_price,2)
    #summary_data['all_entries_performance']= round(self.getBabadjouTotalPerformance(),2)
    #summary_data['all_bulls_value']= round(self.getBabadjouTotalBullsValue(),2)
    #summary_data['all_bears_value']= round(self.getBabadjouTotalBearsValue(),2)
    #summary_data['all_bulls_ratio']= round(100 * self.getBabadjouTotalBullsValue()/(self.getBabadjouTotalBullsValue()+self.getBabadjouTotalBearsValue()),2)
    #summary_data['all_bears_ratio']= round(100 * self.getBabadjouTotalBearsValue()/(self.getBabadjouTotalBullsValue()+self.getBabadjouTotalBearsValue()),2)
    #summary_data['bullish_bearish']=self.getBullishBearish()
      
    content_data = [{'bears_cost_basis':l.getBearsCostBasis(),'bulls_cost_basis':l.getBullsCostBasis(),'bears_avg_price':l.getBearsBuyPriceAverage(),
                     'bulls_avg_price':l.getBullsBuyPriceAverage(),'bulls_performance':round(l.getBullsCompletionPerformance(),2), 'bears_performance': round(l.getBearsCompletionPerformance(),2),
                     'combined_performance':round(l.getBabadjouCompletionPerformance(),2),'performance_target':l.target}
                              for l in self.candidates_list] 
    response = dict()
    #response['summary_data'] = summary_data
    response['content_data'] = content_data
      
    return response      

  # The Babadjou Strategy: This strategy is based on the acquisition of both a bull and bear.
  # Each acquisition is called a RoundTrip.  Bull and Bear buys occur simulteneaously. 
  # A small delay is possible, depending on configuration.
  # There is price spacing between acquisitions. The spacing Condition can be set on the Bull, the Bear or Both
  # connected with an AND or OR. Price spacing can also be placed depending on the Profit goal. 
  # Price Spacing (Proximity) means that no two assets can be active at the same time within a certain amount of 
  # money from one another at the same time.
  # Time spacing and volume spacing are optional. 
  #
  # The assets are held until exit conditions are met.
  # The exit happens in two stages.
  #   1. First a transition stage: This is where one side of the Roundtrip is sold (either the Bull or the Bear). 
  #      RoundTrips are not sold on their own, but in combination with others to keep the portfolio balanced and avoid runaways. 
  #      Which side of the Roundtrip is sold and/or how many are sold is the key to the strategy.
  #      For Example: we could chose to sell ONE Bull, ONE Bear and only sell the best performers or the best and worst performers of each.
  #      A target price is set and if the target is met, then the combined assets are sold.
  #      The ratio of Bulls and Bears to be moved to Transition is dictated. Only specific ratios are allowed.
  #   2. From Transition fo Completion. This is where the remaining side of the Roundtrip is sold, when specific price criteria are met.
  #      The only factor that dictates this sale is if the target price has been reached.
  # function below works like a charm. It is designed as follow.
  # Acquisition Criteria: 50/50 (bull, bear). 
  # Transition Criteria:  Sell the best Bull and sell the best Bear at the same time, when inTransition target is met.
  #   The InTransition Target is fixed.
  # Completion Criteria:  Exit, when profit target is met.
  # 
  # There are a few variants to this Strategy. The variants are based on which other entry gets sold.
  # Here are some combinations: 
  # Strategy Type: Performance Based, Acquisition Price Based, Comparison Price, Spread
  #   Asset Performance: The best performers based on stable value of bull and bears 
  #   Acquisition Price-based: least expensive Bull, Least Expensive Bear. Most expensive Bull, most expensive Bear.
  #   Comparision-based: The difference between the best performers and the worst performers on the Stable Box hits
  #   a certain number.
  #   Random Pairs Based: Pick any bull and any bear ...
  #   Age Based: Pick the oldest Bull, Youngest bear or vice versa.
  #   Sell the Best Bull and one of the worst performing bears, who is not part of the Bull.
  #   Sell a Bull in the first half, and a Bear in the negative half. I.e.: [0-5] Best - Bull, [9-10] - Bear

class BabadjouStrategy(EggheadBaseStrategy):
  """
   A BabadjouStrategy Class represents an instance of classes that implement the Babadjou Investment Strategy.
 
   List all the Methods here:
  """
  def __init__(self,robot):
    super().__init__(robot,name='Babadjou',workflow=WORKFLOW_ENTRIES[1],pair=PAIRS_ENTRIES[0])

  def __str__(self):
    return "{} Strategy Implementation".format(self.name) 

  def isValid(self):
    """ Returns True, if the workflow and the pairs are from the selected options.  """
    return super().isValid() and self.workflow==WORKFLOW_ENTRIES[1] and self.pair==PAIRS_ENTRIES[0]
  
  def buy(self):
    """
      TODO:
    """

    if self.acquisitionConditionMet():
      order_ids = self.robot.addNewRoundtripEntry(business_day=self.robot.current_timestamp)
      root_id = order_ids['bull_buy_order_client_id'].replace('_buy_'+self.robot.getBullishSymbol(),'')
      rt = RoundTrip(robot=self.robot,root_id=root_id)
      self.robot.updateBudgetAfterPurchase(amount=rt.getBullCostBasis())
      self.robot.updateBudgetAfterPurchase(amount=rt.getBearCostBasis())
    else:
      displayOutput(str="Acquisition Condition is not met")       


  #
  #
  #
  def sell(self):
    """
      TODO: The Babadjou Strategy has an intermediate step that moves the assets from Stable to InTransition.
      Then the assets will be moved from Transition to Completion.

      During the Disposition step, two things are checked.
      0. Generic checks will be done to see if this is a good time to sell. This involves things like:
        A. Market Trading Window is Opened for sale?
        B. Infrastructure condition (enough space on the assembly line in the right section?)
        C. Disposition policy
        D. Catastrophic external Condition.

      1. First the assets already in Transition will be moved to Completion, if they meet the requirements set.
      This first step frees places on the Transition assembly line.
      
      2. Assets in Stable will be moved to Transition, if they meet the criteria.
    """

    #Is it a good time to sell?
    if not self.dispositionConditionMet():
      return 

    completed = self.robot.getCompletedRoundTrips()
    completed.printCompletionReport()

    #Process Completion Candidates
    completion_candidates = BabadjouCompletionCandidates(robot=self.robot)
    completion_candidates.printBabadjouTransitionReport()

    if not completion_candidates.isEmpty():
      winner = completion_candidates.getCompletionWinner()
      if winner.matchesBabadjouCompletionTarget():
        displayOutput(str="Found a winner in Transition. {}".format(winner.getCompletionCandidateReportData()))
        winner.moveToCompletion()
      else:
        displayOutput(str="Completion Winner is not yet good enough: {}".format(winner.getCompletionCandidateReportData()))
    else: 
      displayOutput(str=" The Transition to Completion List is empty. ".format())

    # Check if Transition Bandwagon exists and has enough space on it. 
    if not self.transitionConditionMet() or completion_candidates.isFull():
      return 
    
    #Process Completion Candidates
    transition = BabadjouWinnerRoundTrip(robot=self.robot)
    displayOutput(str="\nBest Transition Candidate:\n {}".format(transition.printTransitionalCandidateOutput()))
    if transition.isTransitionalCandidate():
      displayOutput(str="\nTransitional Candidate Found. {}".format(transition.getTransitionCandidateReportData()))
      if transition.matchesBabadjouTransitionTarget():
        displayOutput(str="Transitional Candidate: We have a winner. ")
        transition.moveToTransition()
    else:
      print ("No transitional candidate found.")
