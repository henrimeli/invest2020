from bullbearetfs.strategy.strategybase import EggheadBaseStrategy

"""
  TODO: Describe the Module here ...

  List the classes of the module here
"""

logger = logging.getLogger(__name__)

class BamendjinStrategy(EggheadBaseStrategy):
  def __init__(self,robot):
    self.robot = robot

  def __str__(self):
   return "{0}".format('Hello, this is the Bamendjin Strategy') 

  #
  # The purpose of this section is to capture any information that might need to be updated to make 
  # buy or sell decision with the most accurate data.
  # updating Orders from the Brokerate happen here.
  # Recording of Market activities?
  def setupStrategy(self):
   #Goes to Alpaca to find if there are updates to Orders. Place them in the database.          self.sell_bamendjinda() 
    self.robot.updateOrders() 

  #
  # This area manipulates the sell of securities on the assembly line.
  # The assembly line consists of the following parts:
  # StableRoundTrips:: Hold all RoundTrips that are currently stable.
  # TransitionalCandidatesRoundTrips: Holds roundstrips that are about to be moved to Transitions
  # InTransitionRoundTrips : holds roundtrips that are about to be moved to
  # CompletedRoundTrips: These are completed Roundtrips.
  # 
  def sell(self):
    entries = self.getAllBullishRoundtrips()
    bull_candidates = []
    bear_candidates = []
    completion_candidates = []
    in_transition = []
    
    for x in entries:
      rt = RoundTrip(robot=self,root_id=x.getOrderClientIDRoot())
      if rt.isBullTransitionalCandidate():
      	bull_candidates.append(rt)
      if rt.isBearTransitionalCandidate():
      	bear_candidates.append(rt)      
      if rt.isCompletionCandidate(regression_factor=1):
      	age = rt.getTimeSpentInTransition()
      	print("Completion Candidates Found: {0}  Age={1}".format(rt,age))
      	completion_candidates.append(rt)

    print ("Candidates: To Bulls: {0}. To Bears:{1}. To Completion: {2}".format(len(bull_candidates),len(bear_candidates),len(completion_candidates)))

    #
    # Only perform one single operation at a time.
    #
    if len(completion_candidates) >=1:
      print("There are {0} candidates for completion .... processing.".format(len(completion_candidates)))
      completion_candidates.sort(key=lambda rt:rt.getTransitionalDeltaValue(),reverse=True)
      best_candidate = completion_candidates[0]
      self.moveToCompletion(candidate=best_candidate)
    elif (self.getNumberOfBearsInTransition() + self.getNumberOfBullsInTransition()) >= 5:
      print ("we have reached the max number of items in Transition. Store this time and place an emergency sale strategy rule in place")
  

      #TODO: Replace with below if needed. def getAllInTransition(self):
      #return self.getInTransitionRoundTrips().getAllInTransitionEntries()
      completion_candidates = self.getAllInTransition()
      completion_candidates.sort(key=lambda rt:rt.getTransitionalDeltaValue(),reverse=True)
      candidate = completion_candidates[0]
      age_candidates = self.getAllInTransition()
      age_candidates.sort(key=lambda rt:rt.getTimeSpentInTransition(),reverse=False)
      age_candidate = age_candidates[0]
      print("Best Candidate: {0} Age of Blockage: {1}".format(candidate.getTransitionalDeltaValue(),age_candidate.getTimeSpentInTransition()))
      if (age_candidate.getTimeSpentInTransition() > 180) and \
         (candidate.getAgeSincePurchase() > 24*60) and \
         (candidate.getTransitionalDeltaValue()>0):
      	self.moveToCompletion(candidate)
      elif self.ageSinceLastPositiveDeltaValue()>180:
        self.moveToCompletion(candidate)
    elif abs(self.getNumberOfBearsInTransition()-self.getNumberOfBullsInTransition()) > 3:   #TODO: Externalize 3
      print("There is an inbalance in the Assembly line. Recreate parity by selling at loss.")
      if (self.getNumberOfBullsInTransition() > self.getNumberOfBearsInTransition()):
      	candidate_bear = self.getTheBestStableBearByValue()
      	print("The best bear was found: {0}".format(candidate_bear))
      	self.moveToBearishTransition(candidate_bear)
      else:
      	candidate_bull = self.getTheBestStableBullByValue()
      	print("The best bull was found: {0}".format(candidate_bull))
      	self.moveToBullishTransition(candidate_bull)
    elif len(bear_candidates) >=1:
      print("There are candidates for Bearish processing ....")
      bear_candidates.sort(key=lambda rt:rt.getRoundtripUnrealizedValue(),reverse=True)
      self.moveToBullishTransition(candidate=bear_candidates[0])
    elif len(bull_candidates) >=1:
      print("There are candidates for Bullish processing ...")
      bull_candidates.sort(key=lambda rt:rt.getRoundtripUnrealizedValue(),reverse=True)
      self.moveToBearishTransition(candidate=bull_candidates[0])
"""

    completed = CompletedRoundTrips(robot=self)
    completed.printCompletionReport()

    transitions = InTransitionRoundTrips(robot=self)
    self.setMinimumEntriesForStrategy(value=5)

    bulls_ratio = 3
    bears_ratio = 1

    if not transitions.isEmpty():
      completion_c = CompletionCandidateRoundtrips(robot=self)
      print("Looking for winner for completion")
      rationed_winner = completion_c.getRationedInTransitionWinners(bulls=bulls_ratio, bears =bears_ratio)

      if rationed_winner.matchesRationedCompletionTarget():
        print("Found a winner in Transition. ")
        for x in rationed_winner.winning_bears:
          self.moveToCompletion(x)

        for y in rationed_winner.winning_bulls:
          self.moveToCompletion(y)

      else:
        print("Winner is not good enough. {0:,.2f}".format(rationed_winner.getRationedPerformance()))

    #There is a mimimum of entries required before we start trading.
    stable_box = StableRoundTrips(robot=self)
    if stable_box.getStableSize() < self.getMinimumEntriesForStrategy():
      return 

    if transitions.getInTransitionSize() > 0:
      transitions.printInTransitionReport()

    total_ratio = bulls_ratio + bears_ratio

    if not transitions.isFull():
      print("Finding best candidate inTransition")
      transitional = TransitionalCandidateRoundTrips(robot=self)
      rationed_winner = transitional.getRationedWinningStable(bulls=(total_ratio - bulls_ratio), bears=(total_ratio - bears_ratio))
      if rationed_winner.matchesRationedInTransitionTarget():
        print("Found a winner in Stable. winning Bears = {0}. Winning Bulls = {1}".format(len(rationed_winner.winning_bears),len(rationed_winner.winning_bulls)))
        for x in rationed_winner.winning_bears:
          self.moveToBearishTransition(x)

        for y in rationed_winner.winning_bulls:
          self.moveToBullishTransition(y)        
        #self.moveToBullishTransition(winner.winning_bull)
        #self.moveToBearishTransition(winner.winning_bear)
"""