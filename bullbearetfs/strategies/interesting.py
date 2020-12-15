from bullbearetfs.strategy.strategybase import EggheadBaseStrategy

"""
  TODO: Describe the Module here ...

  List the classes of the module here
"""

logger = logging.getLogger(__name__)

class InterestingStrategy(EggheadBaseStrategy):
  def __init__(self,robot):
    self.robot = robot

  def __str__(self):
   return "{0}".format('Hello, this is the Bangang Strategy') 


  def buy():
  	print ("Buying the InterestingStrategy")

  def sell(self): 

    completed = CompletedRoundTrips(robot=self)
    completed.printCompletionReport()

    transitions = InTransitionRoundTrips(robot=self)
    #First deal with clear cut completion candidates. If there are any, then move them along.
    # We could make several tries by using various Rules. Basic, Regression, then lastly Emergency
    if not transitions.isEmpty():
      completion_c = CompletionCandidateRoundtrips(robot=self)
      completion_c.setActiveRule(rule=completion_c.basicCompletionCandidateRule)
      result = completion_c.applyRule()
      if result == None: 
        print("There are no candidates to move to completion based on CompletionCandidateRoundtrips Basic Rules.")
        if completion_c.isAdvancedCompletionCandateRuleTriggered():
          completion_c.setActiveRule(rule=completion_c.advancedCompletionCandidateRule)
          advanced_result = completion_c.applyRule()
          if advanced_result == None:
            print("There are no candidates to move to Completion based on the AdvancedCompletionCandidateRule Rules.")
            fully_loaded=transitions.isFullyLoaded()
            if completion_c.isEmergencyCompletionCandidateRuleTriggered(fully_loaded=fully_loaded):
              completion_c.setActiveRule(rule=completion_c.emergencyCompletionCandidateRule)
              e_candidate = completion_c.applyRule()
              print("Emergency Rules MUST return a Single candidate. They cannot return None. Following the emergency rule, a Candidate was found. {0}.".format(e_candidate))
              self.moveToCompletion(e_candidate)
            else:
              print("The Emergency Rule has not been triggered... No Action.")
          else:
            print("Advanced Rule applied. There was at least one candidate returned. {0}".format(advanced_result))
            self.moveToCompletion(advanced_result)
        else:
          print("The Advanced Rule has not been triggered. No Action.")
      else:
        print("A Candidate was found after running the Basic Rule. Move it along. {0}".format(result))
        self.moveToCompletion(result)

    #First we need to deal with issues that could prevent the InTransitionRoundTrips to be effective.
    #We must make sure it has space to accept new incoming candidates. It it is full, how can we free more space?
    #We must make sure it is well balanced and the type of candidates it accepts reflects what we want.
    #The appropriate Ratio of Bullish vs Bearish is critical for the ability to generate movement.
    #If all the content is the same, we won't be able to move them along without losing lots of money.
    #Therefore, the content must be varied enough for us to have the right mixture.
    #Additionally, we need a system that gives us enough configuration flexibility without the need to
    #Edit, modify and rewrite the code.
    # We could make sevaeral tries by using various Rules. Basic, Regression, then lastly Emergency

    transitions = InTransitionRoundTrips(robot=self)
    if transitions.getInTransitionSize() > 0:
      transitions.printInTransitionReport()

    #If we are fully loaded, we will try applying a variety of rules to see if we can free some space.
    if transitions.isFullyLoaded() and False:
      print("In Transition is Fully Loaded. Triggering the rules ...")
      full_t = TransitionalCandidateRoundTrips(robot=self)
      full_t.setActiveRule(rule=full_t.fullyLoadedInTransitionBasicRule)
      result_basic = full_t.applyRule()
      if (result_basic == None):
        if full_t.isFullyLoadedInTransitionAdvancedRuleTriggered():
          full_t.setActiveRule(rule=full_t.fullyLoadedInTransitionAdvancedRule)
          result_adv = full_t.applyRule()
          if (result_adv == None):
            if full_t.isFullyLoadedInTransitionEmergencyRuleTriggered():
              full_t.setActiveRule(rule=full_t.fullyLoadedInTransitionEmergencyRule)
              result_e = full_t.applyRule()
              print("Emergency Rule was applied to free up space. Candidate = {0}".format(result_e))
              self.moveToCompletion(result_e)
            else:
      	      print("No Emergency Rule Activated. ")
          else:
      	    print(" Advanced Rule yielded some result. {0}".format(result_adv))
      	    self.moveToCompletion(result_adv)
        else:
          print(" Fully Loaded Advanced Rule Not triggered ...")
      else:
        print("Basic Rule yielded a result. ")
        self.moveToCompletion(result_basic)
    else:
      print("The InTransitionRoundTrips is NOT full. {0}".format(transitions.getInTransitionSize()))
      bull_bear_ratio = transitions.getCurrentBullToBearRatio()
      print("Bull Bear Ratio: {0}  Balanced? {1}".format(bull_bear_ratio,transitions.isBullToBearSpreadBalanced()))

      #If the next entry will create an inbalance, then force the next entry to meet certain criterias.
      #if not transitions.isBullToBearSpreadBalanced(): 
      if transitions.isBullToBearSpreadBalanced(): 
        print("Spread is balanced. towards Bulls?{0}".format(transitions.isUnbalancedTowardsBulls()))
        if transitions.isUnbalancedTowardsBulls():
          print("The InTransitions content is tilted towards Bulls. I need more Bears.")
          transitional = TransitionalCandidateRoundTrips(robot=self)
          candidate_bear = transitional.getTheBestStableBearByValue()
          candidate_bull = transitional.getTheBestStableBullByValue()
          self.moveToBearishTransition(candidate_bear)
          self.moveToBullishTransition(candidate_bull)
        elif transitions.isUnbalancedTowardsBears():
          print("The InTransitions content is tilted towards Bears. I need more Bulls.")
          transitional = TransitionalCandidateRoundTrips(robot=self)
          candidate_bull = transitional.getTheBestStableBullByValue()
          candidate_bear = transitional.getTheBestStableBearByValue()
          self.moveToBearishTransition(candidate_bear)
          self.moveToBullishTransition(candidate_bull)
      else:
        print("The InTransitions is currently balanced. I can add the best candidate, regardless ... ")
        balanced = TransitionalCandidateRoundTrips(robot=self)
        balanced.setActiveRule(rule=balanced.balancedBasicRule)
        result = balanced.applyRule()
        if (result == None):
          if balanced.isBalancedAdvancedRuleTriggered():
            balanced.setActiveRule(rule=balanced.balancedAdvancedRule)
            result = balanced.applyRule()
            if (result == None): 
              if balanced.isBalancedEmergencyRuleTriggered():
                balanced.setActiveRule(rule=balanced.balancedEmergencyRule)
                result = balanced.applyRule()
                self.moveToBullishTransition(candidate=result)
              else:
                print("No TransitionalCandidateRoundTrips.Balanced Emergency Rule. No Action ...")
            else:
              print("The TransitionalCandidateRoundTrips.balancedAdvancedRule triggered some result. ")
              self.moveToBearishTransition(candidate=result)
          else:
            print("No Advanced Rule has been triggered ...")
        else:
          print("The TransitionalCandidateRoundTrips.basicRule yielded some result. Selling the Bull.")
          self.moveToBullishTransition(candidate=result)

