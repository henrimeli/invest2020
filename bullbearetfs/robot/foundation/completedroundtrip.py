import logging 
from bullbearetfs.robot.foundation.roundtrip import RoundTrip
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, strToDatetime, shouldUsePrint, displayOutput,displayError




"""
  TODO: Describe the Module here ...

  List the classes of the module here
"""

logger = logging.getLogger(__name__)

#
# This is the encapsulation of the Completed Elements.
#
class CompletedRoundTrips():

  def __init__(self,robot):
    self.robot = robot
    self.completed_list = []
    entries = self.robot.getAllBullishRoundtrips()
    for entry in entries:
      rt = RoundTrip(robot=self.robot,root_id=entry.getOrderClientIDRoot())
      if rt.isCompleted():
        self.completed_list.append(rt)

  def __str__(self):
   return "{0}".format('Hello, this is the Completed Roundtrip') 

  def getAllCompletedEntries(self):
    return self.completed_list

  def getTodayMaxTransactionsSize(self):
    all_results = [c for c in self.completed_list if c.completedToday()]
    if shouldUsePrint():
      print("CompletedRoundTrips: getTodayMaxTransactionsSize: {}".format(len(all_results)))
    return len(all_results)

  def getCompletedSize(self):
    return len(self.completed_list)

  #def hasCompletedToday(self):
  #  return 
  def getAgeOfFirstCompletion(self):
    all_ages = self.completed_list 
    all_ages.sort(key=lambda rt:rt.getAcquisitionDate(),reverse=True)
    return all_ages[0]

  def getAgeOfMostRecentCompletion(self):
    current_timestamp = self.robot.getCurrentTimestamp()
    return current_timestamp

  def getNumberAboveExpectations(self):
    all_results = [c for c in self.completed_list if c.isRoundtripProfitAboveExpectations()]
    return len(all_results)

  def getNumberBelowExpectations(self):
    all_results = [c for c in self.completed_list if c.isRoundTriProfitBelowExpectations()]
    return len(all_results)

  def getNumberOfSuccessful(self):
    all_results = [c for c in self.completed_list if c.isRoundtripProfitPositive()]
    return len(all_results)

  def getNumberOfUnSuccessful(self):
    all_results = [c for c in self.completed_list if c.isRoundtripProfitNegative()]
    return len(all_results)

  def getNumberOfCompleted(self):
    all_successful = self.completed_list
    return len(self.completed_list)

  def getTotalProfitGenerated(self):
    all_profits = [c.getRoundtripRealizedProfit() for c in self.completed_list ]
    return sum(all_profits)

  def getAverageAgeOfCompletion(self):
    all_results = [c.getTimeSpentActive() for c in self.completed_list ]
    return 0 if len(all_results) == 0 else sum(all_results)/len(all_results)

  def getAverageProfitPerCompletion(self):
    if self.getNumberOfCompleted() == 0:
      return 0.0
    return self.getTotalProfitGenerated() / self.getNumberOfCompleted()

  def getCashGeneratedAfterSettlement(self):
    all_settled_profits = [ c.getRealizedAndSettled() for c in self.completed_list ]
    return sum(all_settled_profits)

  def getCompletedReport(self):
    summary_data = {'completed_size':self.getNumberOfCompleted(),'successful':self.getNumberOfSuccessful(),
                    'unsuccessful':self.getNumberOfUnSuccessful(),'average_profit':self.getAverageProfitPerCompletion(),
                    'average_age':self.getAverageAgeOfCompletion()} 

    five_youngest = self.completed_list
    five_youngest.sort(key=lambda rt:rt.getTimeSpentActive(),reverse=False)
    
    five_most_recent_data = [{'buy_date':l.getAcquisitionDate(), 'sell_date': l.getCompletionDate(),
                              'transition_time':l.getTimeSpentInTransition(),'profit':l.getRoundtripRealizedProfit(),\
                              'stable_time':l.getTimeSpentInStable(),'cost_basis':l.getRoundtripCostBasis()}
                              for l in five_youngest] 
    completed_data = dict()
    completed_data['summary_data'] = summary_data
    completed_data['content_data'] = five_most_recent_data

    return completed_data 

  def printCompletionReport(self):
    nc = self.getNumberOfCompleted()
    ns = self.getNumberOfSuccessful()    
    nl = self.getNumberOfUnSuccessful()
    avg = self.getAverageProfitPerCompletion()
    avg_age = self.getAverageAgeOfCompletion()
    print("\n--------------------------- CompletedRoundTrips Report at {0} -------------------------------- ".format(self.robot.getCurrentTimestamp()))
    print("Completions={0}. Successful={1}. Loss={2}. Profit per Compl.={3:,.2f} Average Age={4}".format(nc,\
          ns,nl,avg,avg_age))
    print(" --------------------------- --------------------------------- --------------------------------- ")

