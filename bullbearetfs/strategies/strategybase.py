from abc import ABC, abstractmethod 
from bullbearetfs.errors.customerrors import NotImplementedError
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, strToDatetime, shouldUsePrint, displayOutput,displayError
from bullbearetfs.robot.foundation.stableroundtrip import StableRoundTrips
import logging

"""
  Module Name: strategybasepy

  The Egghead Platform provides an infrastructure to build, test and deploy investment strategies.
  All investment strategies on the platform are based around two main attributes:
    1. Leveraged and non-leveraged stock market index pairs.
    2. Acquisition to Disposition workflow
  
  All investment strategies are built around the equity pair types and acquisition to disposition workflow.
  Pair types speak to wether the pair is balanced or unbalanced. A balanced pair is equally leveraged
  on the bullish and the bearish side.
  The strategy workflow represents the acquisition to disposition workflow.
  All investment strategies on the platform must follow a strict programmatic contract outlined in the 
  EggheadBaseStrategy abstract class. All Egghead Strategies must inherit from the EggheadBaseStrategy

  This module contains reference implementations of the EggheadBaseStrategy class that support the
  currently supported strategies.
  This module shows (demonstrates) how to implement an example of a strategy in the Egghead platform.
 
  What is a Strategy Equity Pair type: Speaks to the type of Bull/Bear pairs. There are several types.
    Balanced Bullish Bearish Pair: TQQQ/SQQQ(3x,-3x), UCO/SCO(2x,-2x)
    UnBalanced Bullish Bearish leveraged Pair: 
    Bearish & ETF Pair: SQQQ/QQQ (-3x,x) (Leveraged/non-Leveraged asset)
    Bullish & ETF Pair: TQQQ/QQQ (3x ,x) (Leveraged/non-Leveraged asset)

  What is a Strategy Workflow type: Represents the Acquisition to Disposition workflow.
    Acquisition to Balanced Transition to Disposition.
    Acquisition to Unbalanced Transition to Disposition.
    Acquisition to Balanced Transition ( via ETF Protection ) to Disposition.
    Acquisition to Disposition.

  By combining the Strategy Equity Pair Type and the Strategy Workflow type, we get a large number of investment
  possibilities. 16 to be exact. There are 16 chefferies in the Bamboutos Division. 
  Below are some that have been tested and implemented.

  Acquisition Conditions:
    Two main conditions are provided. Time Proximity, Price Proximity.
    The platform can be configured to use or a combination of these options.

  Disposition Conditions:
    Disposition follows the workflow through a transition phase. During this phase, one of the Bull/Bear
    of a given RoundTrip is sold. The RoundTrip is said to be 'In Transition'.
    At a later time, when conditions are met, the other side of the RoundTrip is sold.

  List the implementation classes of the module here:
  ---------------------------------------------------
  BabadjouStrategy
  The Babadjou Strategy is a reference implementation of a Balanced Bullish/Bearish Pair combined with the
  Acquisition to Balanced Transition to Disposition workflow. 
 
  BatchamStrategy
  The Batcham Strategy is a reference implementation of a Balanced Bullish/Bearish Pair combined with the
  Acquisition to Disposition workflow. 

  BalachiStrategy
  The Balachi Strategy is a reference implementation of an Unbalanced Bullish/Bearish Pair combined with the
  Acquisition to Disposition workflow. 

  BangangStrategy
  The Bangang Strategy is a reference implementation of an Unbalanced Bullish/Bearish Pair combined with the
  Acquisition to Disposition workflow. 


  ...etc
  List additional strategies classes here:
  1. BabadjouStrategy()
  2. BangangStrategy()
  3. BatchamStrategy()
  4. BabeteStrategy()
  5. BamendjindaStrategy()
  6. BamessoStrategy()
  7. BafoundaStrategy()
  8. BamessingueStrategy()
  9. BamendouStrategy()
  10. BamendjingStrategy()
  11. BalatchiStrategy()
  12. BamenkomboStrategy()
  13. BamendjoStrategy()
  14. BalengStrategy()
  15. BamougoumStrategy()
  16. GalimStrategy()
"""
logger = logging.getLogger(__name__)

#There are 4 Workflow Types.
#Acquisition to Disposition. (AcqToDis)
#Acquisition to Balanced Transition to Disposition.(AcqToBalTraToDis)
#Acquisition to Unbalanced Transition to Disposition.(AcqToUnBalTraToDis)
#Acquisition to Balanced Transition ( via ETF Protection ) to Disposition. (AcqToETFTraToDis)
WORKFLOW_ENTRIES=['AcqToDis','AcqToBalTraToDis','AcqToUnBalTraToDis','AcqToETFTraToDis']
PAIRS_ENTRIES=['BalancedBullBear','UnbalancedBullBear','BearishAndETF','BullishAndETF']

WORKFLOW_TYPES=(('AcqToDis','AcqToDis'),('AcqToBalTraToDis','AcqToBalTraToDis'),
                ('AcqToUnBalTraToDis','AcqToUnBalTraToDis'),('AcqToETFTraToDis','AcqToETFTraToDis'))

EQUITY_PAIR_TYPES=(('BalancedBullBear','BalancedBullBear'),('UnbalancedBullBear','UnbalancedBullBear'),
                   ('BearishAndETF','BearishAndETF'),('BullishAndETF','BullishAndETF'))


class EggheadBaseStrategy(ABC): 
  """
    This class represents the Abstract Base Class for all the Egghead Strategies.

    Each Egghead Strategy must implement the buy() and sell() functions, that dictates the behavior.
    Addditionally, if transition elements are needed, they will need to be implemented to go along ...
  """

  def __init__(self,robot,name,workflow,pair):
    """
      TODO:
    """
    self.robot = robot
    self.name  = name
    self.workflow=workflow
    self.pair  = pair

  def __str__(self):
    return "{} {} {}".format(self.name, self.workflow, self.pair)

  def isValid(self):
    """  Returns True, if the workflow and the pairs are from the allowed options."""
    #print (" Robot={}".format(type(self.robot)))
    if self.robot==None:
    # or not isinstance(self.robot,ETFAndReversePairRobot):
      return False

    workflow_valid = self.workflow in WORKFLOW_ENTRIES
    pair_valid = self.pair in PAIRS_ENTRIES
    return workflow_valid and pair_valid


  def isBabadjouStrategy(self):
    """ Returns True is self has a workflow that is from Acquisition To Balanced Transition to Disposition AND Balanced Bull Bear Pairs."""
    #print("workflow={} pair={} workflow_o={} pair_o={}".format(self.workflow,self.pair,WORKFLOW_ENTRIES[1],PAIRS_ENTRIES[0]))
    return self.isValid() and (self.workflow==WORKFLOW_ENTRIES[1]) and (self.pair==PAIRS_ENTRIES[0])

  def isBatchamStrategy(self):
    """ Returns True is self has a workflow that is from Acquisition to Disposition AND Balanced Bull Bear Pairs."""    
    return self.isValid() and (self.workflow==WORKFLOW_ENTRIES[0]) and (self.pair==PAIRS_ENTRIES[0])

  def isBalatchiStrategy(self):
    """ Returns True is self has a workflow that is from Acquisition to Disposition AND Bullish And ETF Pairs."""    
    return self.isValid() and (self.workflow==WORKFLOW_ENTRIES[0]) and (self.pair==PAIRS_ENTRIES[3])

  def hasTransitionStep(self):
    return self.isValid() and self.workflow != WORKFLOW_ENTRIES[0]

  def hasBalancedTransition(self):
    return self.isValid() and self.hasTransitionStep() and (self.workflow==WORKFLOW_ENTRIES[1] or self.workflow==WORKFLOW_ENTRIES[2])

  def setupStrategy(self):
    """ Perform any action, prior to executing a buy/sell operation. I.e: update orders from the brokerage """
    logger.info("Entering setupStrategy() {}".format(self.name))
    response = self.isValid() and self.robot.updateOrders() 
    logger.info("Exiting setupStrategy(). Response={} ".format(response))
    return response

  def canTradeNow(self):
    """ Returns True if Market Trading Window and own trading window conditions are met """    
    logger.info("Entering canTradeNow() {}".format(self.name))
    response = self.isValid() and self.robot.canTradeNow(current_time=self.robot.getCurrentTimestamp()) 
    logger.info("Exiting canTradeNow(). Response={} ".format(response))
    return response
 
  def haveEnoughFundsToPurchase(self):
    """ Returns True if there is enough funds in the Budget to purchase asset """    
    logger.info("Entering haveEnoughFundsToPurchase() {}".format(self.name))
    response = self.robot.haveEnoughFundsToPurchase() 
    logger.info("Exiting haveEnoughFundsToPurchase(). Response={0} ".format(response))
    return response

  def infraIsReadyForAssetAcquisition(self):
    """ Returns True if the Infrastructure is ready. I.e.: Do we have space on the Assembly Line? """    
    logger.info("Entering infraIsReadyForAssetAcquisition() {}".format(self.name))
    response = self.robot.infraIsReadyForAssetAcquisition()     
    logger.info("Exiting infraIsReadyForAssetAcquisition(). Response={0} ".format(response))
    return response

  def infraIsReadyForAssetDisposition(self):
    """ Returns True if we are ready to start selling. """
    logger.info("Entering infraIsReadyForAssetDisposition() {}".format(self.name))
    response = self.robot.infraIsReadyForAssetDisposition() 
    logger.info("Exiting infraIsReadyForAssetDisposition(). Response={0}".format(response))
    return response

  def noIssuesWithBrokerage(self):
    """ Returns True if there are no issues with the Brokerage. Sometimes, there might be issues between the Brokerage and the account """
    logger.info("Entering noIssuesWithBrokerage() {}".format(self.name))
    response = self.robot.noIssuesWithBrokerage() 
    logger.info("Exiting noIssuesWithBrokerage(). Response={0} ".format(response))
    return response

  def noCatastrophicEventHappening(self):
    """ Returns True if there are no catastrophic events happening. Do Conditions in the Market require a pause?"""
    logger.info("Entering noCatastrophicEventHappening() {}".format(self.name))
    response = self.robot.noCatastrophicEventHappening() 
    logger.info("Exiting noCatastrophicEventHappening(). Response = {0} ".format(response))
    return response

  
  def acquisitionConditionMet(self):
    """ 
      Returns True if all strategy based acquisition conditions are met.
      acquisitionConditionMet() checks to see if all strategy based acquisition conditions are met. 
      Strategy will work with the StableBox to see if Strategy Conditions are met
      if time condition policy is enabled ... see if current time & time conditions are met
      if proximity conditin policy is enabled. see if
      Will return True, if those conditions are met.
    """

    logger.info("Entering acquisitionConditionMet() {}".format(self.name))
    
    market_window_condition = self.robot.canTradeNow(current_time=self.robot.getCurrentTimestamp())        
    budget_condition = self.robot.haveEnoughFundsToPurchase()
    infrastructure_condition = self.robot.infraIsReadyForAssetAcquisition()
    no_catastrophic_condition =  self.robot.noCatastrophicEventHappening()
    no_brokerage_condition =  self.robot.noIssuesWithBrokerage() 
    strategy_condition = self.robot.acquisitionConditionMet()

    displayOutput(str="Acquisition Conditions: Market Hours={}. Budget={}. Infra Ready={}. Catastrophic={}. Brokerage={}. Strategy={}.".format(market_window_condition,budget_condition, infrastructure_condition,
      no_catastrophic_condition, no_brokerage_condition,strategy_condition ))

    response= market_window_condition and budget_condition and \
              infrastructure_condition and strategy_condition and \
              ( no_brokerage_condition ) and ( no_catastrophic_condition )

    logger.info("Exiting acquisitionConditionMet(). Response={0}".format(response))
    return response

  def dispositionConditionMet(self):
    """ 
      Returns True if all strategy based disposition conditions are met.
      dispositionConditionMet() checks to see if all strategy based disposition conditions are met. 
      Is the tradingmarketwindow() open for trading?

      Will return True, if those conditions are met.
    """
    logger.info("Entering dispositionConditionMet() {}".format(self.name))
    
    market_window_condition = self.robot.canTradeNow(current_time=self.robot.getCurrentTimestamp())        
    infrastructure_condition = self.robot.infraIsReadyForAssetAcquisition()
    catastrophic_condition = self.robot.noCatastrophicEventHappening()
    brokerage_condition = self.robot.noIssuesWithBrokerage() 

    displayOutput(str="Disposition Conditions: Market={}. Infra={}. Catastrophic={}. Brokerage={}.".format(market_window_condition,infrastructure_condition,
          catastrophic_condition, brokerage_condition))

    response = (market_window_condition and brokerage_condition and \
       infrastructure_condition and catastrophic_condition)

    #logger.info("Exiting acquisitionConditionMet(). Response={0}".format(response))

    return response 


  def transitionConditionMet(self):
    """ 
      Returns True if all strategy specific transition conditions are met.
      transitionConditionMet() checks to see if all strategy based transition conditions are met. 
      Not all strategies require a transition step. 
    """

    if not self.hasTransitionStep():
      return False

    #Enough space on the bandwagon? Others?
    stable_box = StableRoundTrips(robot=self.robot)    
    if stable_box.getStableSize() < self.robot.getMinimumEntriesForStrategy(): 
      return False 
    
    return True 


  @abstractmethod
  def buy(self): 
    """
      TODO: Abstract method that must be implemented by the instance
      The buy() method checks if all the conditions are met to perform the acquisition.
      Acquisition is determined by a set of conditions that have to be met. 
      These conditions are organized  and delegated as follow:
      1. Market Trading Window Conditions
      2. Budget Conditions
      3. Infrastructure-based Conditions (i.e: enough space on the assembly line?)
      4. Strategy Acquisition policy and conditions
      5. Catastrophic external Condition. (market conditions or intentional stops)
   
      There is no particular order. All 5 conditions must be met for an acquistion to take place.
      Once an acquisition conditions are met, other parameters can now be calculated.
      Type of order to place, how many shares for each, orderclientID, other things
    """
    raise NotImplementedError
    pass
  
  @abstractmethod
  def sell(self):
    """
      TODO: Abstract method that must be implemented by the instance
    """
    raise NotImplementedError
    pass
