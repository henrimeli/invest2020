
from bullbearetfs.strategy.strategybase import EggheadBaseStrategy

"""
  TODO: Describe the Module here ...

  List the classes of the module here
"""

logger = logging.getLogger(__name__)


#
#
#
#
class InTransitionRoundTrips():

  def __init__(self,robot):
    self.robot = robot
    self.max_size =self.robot.getMaxNumberOfRoundtrips()
    self.in_transition_list = []

    entries = robot.getAllBullishRoundtrips()
    for entry in entries:
      rt = RoundTrip(robot=self.robot,root_id=entry.getOrderClientIDRoot())
      if rt.isInTransition():
      	self.in_transition_list.append(rt)
  
  def __str__(self):
    return "{0}".format('Hello, this is the Transition Roundtrip') 

  def getInTransitionSize(self):
    return len(self.in_transition_list)

  def isFullyLoaded(self):
    return (self.getInTransitionSize() == self.max_size ) #TODO: Externalize me and make me dynamic

  def setInTransitionSize(self,size=5):
    self.max_size = size 

  def isEmpty(self):
    return self.getInTransitionSize() == 0

  def isFull(self):
    return self.getInTransitionSize() == self.max_size

  def getNumberOfBullsInTransition(self):
    in_transition = [ candidate for candidate in self.in_transition_list if candidate.isInBullishTransition()]
    return len(in_transition) 

  def getNumberOfBearsInTransition(self):
    in_transition = [ candidate for candidate in self.in_transition_list if candidate.isInBearishTransition()]
    return len(in_transition) 

  def getTotalNumberInTransition(self):
    return self.getInTransitionSize()

  def getBestCandidateInValue(self): 
    candidates = self.in_transition_list
    candidates.sort(key=lambda rt:rt.getTransitionalDeltaValue(),reverse=True)
    return None if len(candidates) == 0 else candidates[0]

  def getBestCandidateInAge(self): 
    candidates = self.in_transition_list
    candidates.sort(key=lambda rt:rt.getTimeSpentInTransition(),reverse=True)
    return None if len(candidates) == 0 else candidates[0]

  def getBestPerformingBull(self):
    candidates = [ candidate for candidate in self.in_transition_list if candidate.isInBullishTransition()]
    candidates.sort(key=lambda rt:rt.getTransitionalDeltaValue(),reverse=True)
    return None if len(candidates) == 0 else candidates[0]

  def getBestPerformingBear(self):
    candidates = [ candidate for candidate in self.in_transition_list if candidate.isInBearishTransition()]
    candidates.sort(key=lambda rt:rt.getTransitionalDeltaValue(),reverse=True)
    return None if len(candidates) == 0 else candidates[0]

  def getAllInTransitionEntries(self):
    return self.in_transition_list

  def getCashGeneratedAfterSettlement(self):
    all_settled_profits = [ c.getRealizedAndSettled() for c in self.in_transition_list ]
    return sum(all_settled_profits)

  def getInTransitionReport(self):
    best_bear = None if (self.getBestPerformingBear() == None) else self.getBestPerformingBear().getTransitionalDeltaValue()
    best_bull = None if (self.getBestPerformingBull() == None) else self.getBestPerformingBull().getTransitionalDeltaValue()
    summary_data = {'intransition_size':len(self.in_transition_list),'best_bear':best_bear,
                    'best_bull':best_bull,
                    'youngest':(None if self.getBestCandidateInAge() is None else self.getBestCandidateInAge().getTimeSpentInTransition()),
                    'best_value':(None if self.getBestCandidateInValue() is None else self.getBestCandidateInValue().getTransitionalDeltaValue())} 

    five_youngest = self.in_transition_list
    five_youngest.sort(key=lambda rt:rt.getTimeSpentInTransition(),reverse=False)
    
    five_most_recent_data = [{'delta':l.getTransitionalDeltaValue(), 'sell_date': l.getCompletionDate(),
                              'profit':l.getTransitionalTotalValue(),'duration':l.getDurationInTransition()}
                              for l in five_youngest[:5]] 

    in_transition_data = dict()
    in_transition_data['summary_data']=summary_data
    in_transition_data['content_data'] = five_most_recent_data

    return in_transition_data 

  def printInTransitionReport(self):
    best_bears = self.getAllInTransitionEntries()
    best_bulls = self.getAllInTransitionEntries()    
    total_t=0
    print(" --------------------------- InTransitionRoundTrips Report at {0}".format(self.robot.getCurrentTimestamp()))
    for n in best_bulls:
      total =  round(n.getTransitionalTotalValue(),2)
      delta =  round(n.getTransitionalDeltaValue(),2)
      total_t+= delta
      age = n.getDurationInTransition()
      print("Delta:{0}. Age: {1}".format(delta,age))
    print("Total:{0:,.2f}. ".format(total_t))
    print(" --------------------------- --------------------------------- --------------------------------- \n")



class BangangStrategy(EggheadBaseStrategy):

  def __init__(self,robot):
    self.robot = robot
