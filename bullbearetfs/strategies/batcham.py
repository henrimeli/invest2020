
from bullbearetfs.strategies.strategybase import EggheadBaseStrategy
from bullbearetfs.strategies.strategybase import WORKFLOW_ENTRIES, PAIRS_ENTRIES
from bullbearetfs.robot.foundation.stableroundtrip import StableRoundTrips
from bullbearetfs.robot.foundation.roundtrip import RoundTrip
from bullbearetfs.utilities.core import getTimeZoneInfo, strToDatetime, shouldUsePrint, displayOutput,displayError
#from bullbearetfs.utilities.core import displayReportBasic1,displayReportBasic2,displayReportAdvanced1
from bullbearetfs.utilities.core import shouldUseReportLevel1, shouldUseReportLevel2, shouldUseReportLevel3
import logging 

"""
  TODO: Describe the Module here ...

  List the classes of the module here
"""

logger = logging.getLogger(__name__)


class BatchamCompletionCandidates():
  """
    This class controlls how we select candidates to move from Stable to Completion.
    In this strategy, the inner spread between the bull value and the bear value is calculated.
  """
  def __init__(self,robot):
    self.robot = robot
    min_hold_time = None if (self.robot.getMinHoldTimeInMinutes()==0.0) else self.robot.getMinHoldTimeInMinutes()
    self.candidates_list = self.robot.getStableRoundTrips().getMaxBullBearCurrentValueSpread(minimal_age=min_hold_time)

  def __str__(self):
   return "{0}".format('Hello, these are the Batcham Strategy Completion Candidates') 


  def getReportDataBasic(self):
    """
    """
    if shouldUseReportLevel1():
      return "Level 1"
    elif shouldUseReportLevel2():
      return "Level 2"
    elif shouldUseReportLevel3():
      return "Level 3"
    return "Level 0"


  def getBatchamCompletionCandidatesReport(self):
    if shouldUseReportLevel0():
      return ""

    str1="\n--------------------------- Batcham Strategy Stable to Completion Report Level -------- "
    str2="\nThis report should contain the candidates to be moved from Stable to Completion. "
    str3=self.getReportDataBasic()
    str4="\n--------------------------- --------------------------------- --------------------------------- "
    return str1 + str2 + str3 +str4 


  def isEmpty(self):
    return self.getCompletionSize()==0

  def getCompletionSize(self):
    return len(self.candidates_list)
  #self.robot.getCompletionProfitTarget()
  def getCompletionWinner(self):
    self.candidates_list.sort(key=lambda rt:rt.getBullBearCurrentValueDelta(),reverse=True) 
    if len(self.candidates_list)!=0:
      print("Sorted by Current Value Delta : {}".format(self.candidates_list[0].getBullBearCurrentValueDelta()))
    return None if len(self.candidates_list)==0 else self.candidates_list[0] 

  
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

  def getCompletionCandidateReportData(self):
    summary_data = dict()
    summary_data['entries']=self.getCompletionSize()
      
    content_data = [{'bear_cost_basis':l.getBearCostBasis(),'bull_cost_basis':l.getBullCostBasis(),'bear_current_value':l.getBearCurrentValue(),
                     'bull_current_value':l.getBullCurrentValue(),'bull_performance':round(l.getStableBullValue(),2), 
                     'bear_performance': round(l.getStableBearValue(),2),
                     'combined_performance':round(l.getBullBearCurrentValueDelta(),2),'performance_target':self.robot.getCompletionProfitTarget()}
                              for l in self.candidates_list] 
    response = dict()
    response['summary_data'] = summary_data
    response['content_data'] = content_data
      
    return response      

class BatchamStrategy(EggheadBaseStrategy):
  """
   A BatchamStrategy Class represents an instance of classes that implement the Batcham Investment Strategy.
 
   List all the Methods here:
   __init__():
   isValid():
   buy()
   sell()

  """
  def __init__(self,robot):
    super().__init__(robot,name='Batcham',workflow=WORKFLOW_ENTRIES[0],pair=PAIRS_ENTRIES[0])

  def __str__(self):
    return "{} Strategy Implementation".format(self.name) 

  def isValid(self):
    """ Returns True, if the workflow and the pairs are from the selected options.  """
    return super().isValid() and self.workflow==WORKFLOW_ENTRIES[0] and self.pair==PAIRS_ENTRIES[0]
  
  def moveToCompletion(self,winner):
    self.robot.moveBullAndBearToCompletion(candidate=winner)

  def matchesBatchamCompletionTarget(self,winner):
    if (winner.getBullBearCurrentValueDelta() >= self.robot.getCompletionProfitTarget()):
      return True
    return False 

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
      print("HENRI: Condition to buy is not met")       

  def sell(self): 
    """
      The Batcham Strategy does not have any intermediate steps.
      Therefore assets will be moved from Stable to Completion.

      During the Disposition step, two things are checked.
      0. Generic checks will be done to see if this is a good time to sell. This involves things like:
        A. Market Trading Window is Opened for sale?
        B. Infrastructure condition (enough space on the assembly line in the right section?)
        C. Disposition policy
        D. Catastrophic external Condition.

      
      1. Assets in Stable will be moved to Completion, if they meet the Completion criteria.
    """
    #print("Running Sell on the Batcham Strategy")

    #Is it a good time to sell?
    if not self.dispositionConditionMet():
      return 

    completed = self.robot.getCompletedRoundTrips()
    completed.printCompletionReport()

    #Process Completion Candidates
    completion_candidates = BatchamCompletionCandidates(robot=self.robot)
    if not completion_candidates.isEmpty():
      winner = completion_candidates.getCompletionWinner()
      if self.matchesBatchamCompletionTarget(winner=winner):
        displayOutput(str="Found a winner. {}".format(completion_candidates.getCompletionCandidateReportData()))
        self.moveToCompletion(winner=winner)
      else:
        displayOutput(str="Completion Winner is not yet good enough: {}".format(completion_candidates.getCompletionCandidateReportData()))
    else: 
      displayOutput(str=" The Transition to Completion List is empty. ".format())

