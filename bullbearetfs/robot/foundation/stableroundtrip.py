import logging
from bullbearetfs.robot.foundation.roundtrip import RoundTrip


"""
  TODO: Describe the Module here ...

  List the classes of the module here
"""

logger = logging.getLogger(__name__)


###########################################################################################################
# StableRoundTrips: This is not really a persistable Class. It is an interface to roundtrip data that are 
# in a particular state. The Stable State.
#  RoundTrips.isStable() returns True ... are all the entries in this class.
#
# StableRoundTrirps: This is the encapsulation of the Assets in a Stable State
#
class StableRoundTrips():

  def __init__(self,robot):
    self.robot = robot
    self.stable_list = []
    entries = robot.getAllBullishRoundtrips()
    for entry in entries:
      rt = RoundTrip(robot=self.robot,root_id=entry.getOrderClientIDRoot())
      if rt.isStable():
        self.stable_list.append(rt)

  def __str__(self):
   return "{0}".format('Hello, this is the StableRoundtrip Class') 

  def getStableRoundtripDataBasic(self):
    pass 
 
  def getStableRoundTripDataBasic2(self):
    pass 

  def printEntries(self):
    print("\n")
    for c in self.stable_list:
      print("{0}".format(c))

  def getSize(self):
    return self.getStableSize()

  def getStableSize(self):
    return len(self.stable_list)

  def isFullyLoaded(self):
    return (len(self.stable_list) >= self.robot.getMaxNumberOfRoundtrips()) 
  
  def isEmpty(self):
    return (self.getSize() == 0)

  def getTradableAssetsSize(self):
    tradable = [ c for c in self.stable_list if (c.isPastMinimumHoldTime())]
    return len(tradable)

###Returns List in either increasing or decreasing (reverse=True or False ) Order ###################
  def getAllStableEntries(self):
    return self.stable_list

  def getAllStableEntriesByAgeYoungestFirst(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBullBuyDate(),reverse=True)
    return candidates 
  
  def getAllStableEntriesByAgeOldestFirst(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBullBuyDate(),reverse=False)
    return candidates 

  def getAllStableEntriesByBullPrice(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBullBuyPrice(),reverse=True)
    return candidates

  def getAllStableEntriesByBearPrice(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBearBuyPrice(),reverse=True)
    return candidates

  def getAllStableEntriesByBearCostBasis(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBearCostBasis(),reverse=True)
    return candidates

  def getAllStableEntriesByBullCostBasis(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBullCostBasis(),reverse=True)
    return candidates

  def getAllStableEntriesByBullValue(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getStableBullValue(),reverse=True)
    return candidates

  def getAllStableEntriesByBearValue(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getStableBearValue(),reverse=True)
    return candidates
 

   # total_spread = round(sum(price_spread),2)

    #bull_current_value_list  = [ c.getBullCurrentValue() for c in all_candidates]
    #bear_current_value_list  = [ c.getBearCurrentValue() for c in all_candidates]


   # pass 
# ------------------Portfolio Trend + Market Trend --------------------------------------------------------------------------
# The purpose of these functions is to provide a right picture of the portfolio in comparison to 
# where the market is trending overall. The main goal is to avoid having a portfolio that trends sharply in one 
# direction or another. If the portfolio can be maintained within a given window 
# A very important aspect in investing is the ability to keep the Porfolio trending up regardless
# of the direction of the market. Aggressively trending up (or down) has lots of risks.
# Our goal is to generate steady revenue and avoid excessive risks. Therefore, trending too far up 
# or trending too far down is not a good approach. Our approach will be to remain within a given comfort window.
# This is best achieved,
# If the portfolio value is maintained WITHIN a given window of for example [-10% , 0 , +20%]. At the current point, 
# the 20% range is just a random number.
# Whenever our portfolio value goes above +20%, we perform actions to reign it back in.
# Whenever our portfolio value goes below -20%, we perform actions to reign it back in.
# This way, we try as hard as possible to keep the portfolio value balanced, so that we can cash is small and steady profits.
# In order to achieve that, it is important to :
#  -Clearly define our tolerance window. It will be determined through tests. It will also depend on the asset.
#    But the concept will remain the same to achieve this goal.
#  -Measure Market trends accurately (price difference between several acquisition over periods of time)
#  -Measure Portfolio trends accurately (portfolio value change, as the market moves)
#  -Adjust acquisitions, so that the portfolio always stays within the right value range.
# Because we buy both sides of the market, we can continue buying regardless of the direction of the market.
# The main difference is the weight of the Bull, the weight of the Bear.
# Let's say we have performed 5 straight Bull/Bear (80/20) acquisitions. And the market keeps trending up and we have to buy.
# We can place a buy order, but we will buy 20/80 (instead of 80/20).
# We are simply buying more bears and less bulls.
# Adjusting the portfolio on every acquisition is not always the best thing. Therefore, it is important
# to have portfolio adjustment times in place.
# 
# Certain formulas must be defined to clearly underrstand the calculations.
# Step 1: Eliminate the 50/50 bull/bear composition. Because it brings no value. If the market goes up by 10% or down 10%
#         Nothing happens. Therefore, we must always operate from an non - 50/50 composition.
#
# Step 2: Let's assume a 80/20 bull/bear composition. And a budget of $1,500 for both. 
# That's .8 * 1500 = 1,200 for the Bull. At the price of $120 for the Bull, the bear would cost ...
# The Current Bull/Bear Spread is:
# Now, let's assume the Bull price goes up by 1%, the Bear price will go down by 1% as well. 
#
  #Percentage of price increase/decrease based on the given number of entries. 
  def getBullPriceTrend(self,entries=None):
    candidates = self.stable_list
    if len(candidates) == 0:
      return 0 

    if len(candidates) == 1:
      return 0 

    all_entries = len(candidates) if entries==None else entries
    candidates.sort(key=lambda rt:rt.getStableBearValue(),reverse=True)
    return 0 

  #Percentage of price increase/decrease based on the given number of entries. 
  def getAverageBullPriceTrend(self,entries=None):
    candidates = self.stable_list
    if len(candidates) == 0:
      return 0 

    return 0 
 
#  def getPortfolioValueTrend(self,entries=None):
#    pass 

  def getCurrentBullCompositionRatio(self):
    bull_current_value_list = [c.getBullCurrentValue() for c in self.stable_list  ]
    bear_current_value_list = [c.getBearCurrentValue() for c in self.stable_list  ]
    total_value = sum(bull_current_value_list) + sum(bear_current_value_list)
    return 0 if len(self.stable_list) == 0 else 100 * (sum(bull_current_value_list)/total_value)

  def getCurrentBearCompositionRatio(self):
    bull_current_value_list = [c.getBullCurrentValue() for c in self.stable_list  ]
    bear_current_value_list = [c.getBearCurrentValue() for c in self.stable_list  ]
    total_value = sum(bull_current_value_list) + sum(bear_current_value_list)
    return 0 if len(self.stable_list) == 0 else 100 * (sum(bear_current_value_list)/total_value)

  def getTotalCurrentStableSpread(self):
    price_spread = [c.getBullBearCurrentValueSpread() for c in self.stable_list]
    return sum(price_spread)

  def getNegativeBullPriceSpread(self):
    price_spread = [c.getBullBearCurrentValueSpread() for c in self.stable_list]
    return sum(price_spread)

  #1. What's the price spread on Stable?
  #2. How many negative spread attributed to Bulls?
  #3. How many negative spread attributed to Bears?
  def getCurrentTrend(self):
    stable_portfolio_trend = dict()
    stable_portfolio_trend['type'] = 'stable_value_spread'
    stable_portfolio_trend['spread_total_value'] = self.getTotalCurrentStableSpread()
    stable_portfolio_trend['stable_size'] = self.getStableSize()
    stable_portfolio_trend['current_bull_composition'] = self.getCurrentBullCompositionRatio()
    stable_portfolio_trend['current_bear_composition'] = self.getCurrentBearCompositionRatio()
    stable_portfolio_trend['negatives_bull_spread'] = 5
    stable_portfolio_trend['negatives_bear_spread'] = 2
    
    return stable_portfolio_trend

# ------------------Spread based on ONLY ELLIGIBLE Average on Assembly line Price ---------------------------------
  def getMaxBearSpreadToAverageElligiblePrice(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    if len(candidates) == 0:
      return candidates

    #Calculate the Average based on buyPrice() for Elligible ONLY
    avg = sum([c.getBearBuyPrice() for c in candidates]) / len(candidates)

    #Sort by the criteria given bearPriceSpread(bearbuyprice - avg)
    candidates.sort(key=lambda rt:rt.getBearPriceSpread(average=avg),reverse=True)
    return candidates     

  def getMaxBullSpreadToAverageElligiblePrice(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    if len(candidates) == 0:
      return candidates

    #Calculate the Average based on buyPrice() for Elligible ONLY
    avg = sum([c.getBullBuyPrice() for c in candidates]) / len(candidates)

    #Sort by the criteria given bearPriceSpread(bearbuyprice - avg)
    candidates.sort(key=lambda rt:rt.getBullPriceSpread(average=avg),reverse=True)
    return candidates     

  def getMinBearSpreadToAverageElligiblePrice(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    if len(candidates) == 0:
      return candidates

    #Calculate the Average based on buyPrice() for Elligible ONLY
    avg = sum([c.getBearBuyPrice() for c in candidates]) / len(candidates)

    #Sort by the criteria given bearPriceSpread(bearbuyprice - avg)
    candidates.sort(key=lambda rt:rt.getBearPriceSpread(average=avg),reverse=False)
    return candidates     

  def getMinBullSpreadToAverageElligiblePrice(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    if len(candidates) == 0:
      return candidates

    #Calculate the Average based on buyPrice() for Elligible ONLY
    avg = sum([c.getBullBuyPrice() for c in candidates]) / len(candidates)

    #Sort by the criteria given bearPriceSpread(bearbuyprice - avg)
    candidates.sort(key=lambda rt:rt.getBullPriceSpread(average=avg),reverse=False)
    return candidates     


# ------------------Spread based on Average Assembly line Price ---------------------------------
  def getMaxBearSpreadToAveragePrice(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    if len(candidates) == 0:
      return candidates

    #Calculate the Average based on buyPrice() for ALL
    avg = sum([c.getBearBuyPrice() for c in self.stable_list]) / len(self.stable_list)
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBearPriceSpread(average=avg),reverse=True)
    return candidates     

  def getMaxBullSpreadToAveragePrice(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    if len(candidates) == 0:
      return candidates

    #Calculate the Average based on buyPrice() for ALL
    avg = sum([c.getBullBuyPrice() for c in self.stable_list]) / len(self.stable_list)
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBullPriceSpread(average=avg),reverse=True)
    return candidates     

  def getMinBearSpreadToAveragePrice(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    if len(candidates) == 0:
      return candidates

    #Calculate the Average based on buyPrice() for ALL
    avg = sum([c.getBearBuyPrice() for c in self.stable_list]) / len(self.stable_list)
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBearPriceSpread(average=avg),reverse=False)
    return candidates     

  def getMinBullSpreadToAveragePrice(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    if len(candidates) == 0:
      return candidates

    #Calculate the Average based on buyPrice() for ALL
    avg = sum([c.getBullBuyPrice() for c in self.stable_list]) / len(self.stable_list)
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBullPriceSpread(average=avg),reverse=False)
    return candidates     


# ------------------Roundtrip Inner Spread based on own Price Only (Current Value -  CostBasis ) ---------------------------------
  def getMaxBullBearCostBasisSpread(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBullBearCostBasisDelta(),reverse=True)

    return candidates     

  def getMaxBullBearCurrentValueSpread(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBullBearCurrentValueDelta(),reverse=True)

    return candidates     

  def getMinBullBearCostBasisSpread(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBullBearCostBasisDelta(),reverse=False)
    return candidates     

  def getMinBullBearCurrentValueSpread(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBullBearCurrentValueDelta(),reverse=False)
    return candidates     

# ------------------Asset Acquisition Price Based ---------------------------------------------------
  def getMostExpensiveBearCandidates(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBearBuyPrice(),reverse=True)
    return candidates 

  def getMostExpensiveBullCandidates(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBullBuyPrice(),reverse=True)
    return candidates 

  def getLeastExpensiveBearCandidates(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBearBuyPrice(),reverse=False)
    return candidates 

  def getLeastExpensiveBullCandidates(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getBullBuyPrice(),reverse=False)
    return candidates 

# ------------------Asset Performance Based (Current Value - Cost Basis) ---------------------------------
  def getBestBearCandidates(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getStableBearValue(),reverse=True)
    return candidates 

  def getBestBullCandidates(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    candidates.sort(key=lambda rt:rt.getStableBullValue(),reverse=True)
    return candidates 

  def getWorstBearCandidates(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getStableBearValue(),reverse=False)
    return candidates 

  def getWorstBullCandidates(self,minimal_age=None):
    #Make sure to select elligible entries. 
    candidates = self.stable_list if (minimal_age==None) else [ c for c in self.stable_list if (c.getTimeSincePurchase()>=minimal_age)]
    #Sort by the criteria given
    candidates.sort(key=lambda rt:rt.getStableBullValue(),reverse=False)
    return candidates 

####################Return single Entity #################################
  def getBestPerformingBearValue(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getStableBearValue(),reverse=True)
    return None if len(candidates) == 0 else candidates[0]

  def getBestPerformingBullValue(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getStableBullValue(),reverse=True)
    return None if len(candidates) == 0 else candidates[0]

  def getTheMostExpensiveBullEntry(self):
    candidates = self.getAllStableEntriesByBullPrice()
    return None if len(candidates) == 0 else candidates[0]

  def getTheMostExpensiveBearEntry(self):
    candidates = self.getAllStableEntriesByBearPrice()
    return None if len(candidates) == 0 else candidates[0]

  def getTheLeastExpensiveBullEntry(self):
    candidates = self.getAllStableEntriesByBullPrice()
    return None if len(candidates) == 0 else candidates[-1]

  def getTheLeastExpensiveBearEntry(self):
    candidates = self.getAllStableEntriesByBearPrice()
    return None if len(candidates) == 0 else candidates[-1]

  def getWorstPerformingBearInStage(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getStableBearValue(),reverse=False)
    return None if len(candidates) == 0 else candidates[0]

  def getWorstPerformingBullInStage(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getStableBullValue(),reverse=False)
    return None if len(candidates) == 0 else candidates[0]

  def getBestPerformingBearInStage(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getStableBearValue(),reverse=True)
    return None if len(candidates) == 0 else candidates[0]

  def getBestPerformingBullInStage(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getStableBullValue(),reverse=True)
    return None if len(candidates) == 0 else candidates[0]

  def getAverageBullCostBasis(self):
    candidates = [c.getBullCostBasis() for c in self.stable_list  ]
    return 0 if len(candidates) == 0 else (sum(candidates)/len(candidates))

  def getAverageBearCostBasis(self):
    candidates = [c.getBearCostBasis() for c in self.stable_list  ]
    return 0 if len(candidates) == 0 else (sum(candidates)/len(candidates))

  def getAverageBullPrice(self):
    vals = [c.getBullBuyPrice() for c in self.stable_list  ]
    return 0 if len(vals) == 0 else (sum(vals)/len(vals))

  def getAverageBearPrice(self):
    vals = [c.getBearBuyPrice() for c in self.stable_list  ]
    return 0 if len(vals) == 0 else (sum(vals)/len(vals))

  def getSpreadBullPrice(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBullBuyPrice(),reverse=True)
    return 0 if len(candidates) == 0 else (candidates[0].getBullBuyPrice() - candidates[-1].getBullBuyPrice())

  def getSpreadBearPrice(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBearBuyPrice(),reverse=True)
    return 0 if len(candidates) == 0 else (candidates[0].getBearBuyPrice() - candidates[-1].getBearBuyPrice())

  def getSpreadPercentToMaxBullPrice(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBullBuyPrice(),reverse=True)
    return 0 if len(candidates) == 0 else 100*((candidates[0].getBullBuyPrice() - candidates[-1].getBullBuyPrice())/candidates[0].getBullBuyPrice())

  def getSpreadPercentToMaxBearPrice(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBearBuyPrice(),reverse=True)
    return 0 if len(candidates) == 0 else 100*((candidates[0].getBearBuyPrice() - candidates[-1].getBearBuyPrice())/candidates[0].getBearBuyPrice())

  def getSpreadPercentToMinBullPrice(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBullBuyPrice(),reverse=True)
    return 0 if len(candidates) == 0 else 100*((candidates[0].getBullBuyPrice() - candidates[-1].getBullBuyPrice())/candidates[-1].getBullBuyPrice())

  def getSpreadPercentToMinBearPrice(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBearBuyPrice(),reverse=True)
    return 0 if len(candidates) == 0 else 100*((candidates[0].getBearBuyPrice() - candidates[-1].getBearBuyPrice())/candidates[-1].getBearBuyPrice())

  def getSpreadPercentToAverageBearPrice(self):
    bear_avg_price = self.getAverageBearPrice()
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBearBuyPrice(),reverse=True)
    return 0 if len(candidates) == 0 else 100*((candidates[0].getBearBuyPrice() - candidates[-1].getBearBuyPrice())/bear_avg_price)

  def getSpreadPercentToAverageBullPrice(self):
    bull_avg_price = self.getAverageBullPrice()
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBullBuyPrice(),reverse=True)
    return 0 if len(candidates) == 0 else 100*((candidates[0].getBullBuyPrice() - candidates[-1].getBullBuyPrice())/bull_avg_price)




  def getLowestBullCostBasis(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBullCostBasis(),reverse=False)
    return None if len(candidates) == 0 else candidates[0]
    
  def getHighestBullCostBasis(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBullCostBasis(),reverse=True)
    return None if len(candidates) == 0 else candidates[0]
    
  def getHighestBearCostBasis(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBearCostBasis(),reverse=True)
    return None if len(candidates) == 0 else candidates[0]

  def getLowestBearCostBasis(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getBearCostBasis(),reverse=False)
    return None if len(candidates) == 0 else candidates[0]
 
  def getTotalBearCostBasis(self):
    vals = [c.getBearCostBasis() for c in self.stable_list  ]
    sum_bears = sum(vals)
    return  sum_bears
    
  def getTotalBullCostBasis(self):
    vals = [c.getBullCostBasis() for c in self.stable_list  ]
    sum_bulls = sum(vals)
    return  sum_bulls

  def getTotalCostBasis(self):
    return self.getTotalBullCostBasis() + self.getTotalBearCostBasis()

  def getOldestStageRoundtripEntry(self):
    candidates = self.getAllStableEntriesByAgeOldestFirst()
    return None if len(candidates) == 0 else candidates[0]
      
  def getYoungestStageRoundtripEntry(self):
    candidates = self.getAllStableEntriesByAgeYoungestFirst()
    return None if len(candidates) == 0 else candidates[0]

  def getTimeEllapsedSinceYoungestAcquisition(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getTimeSincePurchase(),reverse=False)
    return None if len(candidates) == 0 else candidates[0]

  def getTimeEllapsedSinceOldestAcquisition(self):
    candidates = self.stable_list
    candidates.sort(key=lambda rt:rt.getTimeSincePurchase(),reverse=True)
    return None if len(candidates) == 0 else candidates[0]

  def getAgeDifferenceBetweenOldestAndYoungestInStage(self):
    ellapsed_old = self.getTimeEllapsedSinceOldestAcquisition()
    ellapsed_yng = self.getTimeEllapsedSinceYoungestAcquisition()
    if not (ellapsed_old == None) and not (ellapsed_yng==None):
      return ellapsed_old.getTimeSincePurchase() - ellapsed_yng.getTimeSincePurchase()
    
    return None 

  def getNumberOfAssetsAcquiredWithinTimeframe(self,timeframe=60):
    candidates = [c for c in self.stable_list if (c.getTimeSincePurchase()<=timeframe) ]
    return len(candidates) 

  #If price proximity is set. current_bull_price, current_bear_price are already passed. 
  def isAssetToBuyWithinPriceRange(self,type_used,rule_used,number_bull,number_bear):
    logger.info("Type_used={0}. rule_used={1}. number_bear={2}. number_bull={3}.".format(type_used,rule_used,number_bear,number_bull))
    if len(self.stable_list) == 0:
      return False 

    if   rule_used.lower() == 'bull' and (type_used.lower() == 'number' or type_used.lower() == 'number_stock'):
      candidates = [c for c in self.stable_list if c.isBullWithinSharePriceByNumber(number=number_bull) ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bull' and type_used.lower() == 'percentage_stock':
      candidates = [c for c in self.stable_list if c.isBullWithinSharePriceByPercentage(percentage=number_bull) ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bull' and type_used.lower() == 'percentage_profit':
      candidates = [c for c in self.stable_list if c.isBullWithinCostBasisByPercentageOfTotalProfit() ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bull' and type_used.lower() == 'number_profit':
      candidates = [c for c in self.stable_list if c.isBullWithinCostBasisByTotalProfit() ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bull' and type_used.lower() == 'weighted_percent_profit':
      candidates = [c for c in self.stable_list if c.isBullWithinCostBasisByWeightedTotalPercentageOfProfit() ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bull' and type_used.lower() == 'weighted_number_profit':
      candidates = [c for c in self.stable_list if c.isBullWithinCostBasisByWeightedTotalProfit() ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bull' and (type_used.lower() == 't_percent_profit' or type_used.lower() == 'c_percent_profit'):
      profit_target = self.robot.getInTransitionProfitTargetRatio() if (type_used.lower() == 't_percent_profit') else self.robot.getCompletionProfitTargetRatio()
      candidates = [c for c in self.stable_list if c.isBullWithinPriceRangeByPercentageOfProfitRatio(profit_percent=profit_target) ]
      return True if (len(candidates) > 0) else False

    elif rule_used.lower() == 'bear' and (type_used.lower() == 'number' or type_used.lower() == 'number_stock'):
      candidates = [c for c in self.stable_list if c.isBearWithinSharePriceByNumber(number=number_bear) ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bear' and type_used.lower() == 'percentage_stock':
      candidates = [c for c in self.stable_list if c.isBearWithinSharePriceByPercentage(percentage=number_bear) ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bear' and type_used.lower() == 'percentage_profit':
      candidates = [c for c in self.stable_list if c.isBearWithinCostBasisByPercentageOfTotalProfit() ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bear' and type_used.lower() == 'number_profit':
      candidates = [c for c in self.stable_list if c.isBearWithinCostBasisByTotalProfit() ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bear' and type_used.lower() == 'weighted_percent_profit': 
      candidates = [c for c in self.stable_list if c.isBearWithinCostBasisByWeightedTotalPercentageOfProfit() ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bear' and type_used.lower() == 'weighted_number_profit':
      candidates = [c for c in self.stable_list if c.isBearWithinCostBasisByWeightedTotalProfit() ]
      return True if (len(candidates) > 0) else False
    elif rule_used.lower() == 'bear' and (type_used.lower() == 't_percent_profit' or type_used.lower() == 'c_percent_profit'):
      profit_target = self.robot.getInTransitionProfitTargetRatio() if (type_used.lower() == 't_percent_profit') else self.robot.getCompletionProfitTargetRatio()
      candidates = [c for c in self.stable_list if c.isBearWithinPriceRangeByPercentageOfProfitRatio(profit_percent=profit_target) ]
      return True if (len(candidates) > 0) else False

    elif rule_used.lower() == 'both' and (type_used.lower() == 'number' or type_used.lower() == 'number_stock'):
      candidates_bull = [c for c in self.stable_list if c.isBullWithinSharePriceByNumber(number=number_bull) ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinSharePriceByNumber(number=number_bear) ]
      return True if (len(candidates_bear) > 0) and (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'both' and type_used.lower() == 'percentage_stock':
      candidates_bull = [c for c in self.stable_list if c.isBullWithinSharePriceByPercentage(percentage=number_bull) ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinSharePriceByPercentage(percentage=number_bear) ]
      return True if (len(candidates_bear) > 0) and (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'both' and type_used.lower() == 'percentage_profit':
      candidates_bull = [c for c in self.stable_list if c.isBullWithinCostBasisByPercentageOfTotalProfit() ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinCostBasisByPercentageOfTotalProfit() ]
      return True if (len(candidates_bear) > 0) and (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'both' and type_used.lower() == 'number_profit':
      candidates_bull = [c for c in self.stable_list if c.isBullWithinCostBasisByTotalProfit() ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinCostBasisByTotalProfit() ] 
      return True if (len(candidates_bear) > 0) and (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'both' and type_used.lower() == 'weighted_percent_profit':
      candidates_bull = [c for c in self.stable_list if c.isBullWithinCostBasisByWeightedTotalPercentageOfProfit() ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinCostBasisByWeightedTotalPercentageOfProfit() ]
      return True if (len(candidates_bear) > 0) and (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'both' and type_used.lower() == 'weighted_number_profit':
      candidates_bull = [c for c in self.stable_list if c.isBullWithinCostBasisByWeightedTotalProfit() ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinCostBasisByWeightedTotalProfit() ]
      return True if (len(candidates_bear) > 0) and (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'both' and (type_used.lower() == 't_percent_profit' or type_used.lower() == 'c_percent_profit'):
      profit_target = self.robot.getInTransitionProfitTargetRatio() if (type_used.lower() == 't_percent_profit') else self.robot.getCompletionProfitTargetRatio()
      candidates_bull = [c for c in self.stable_list if c.isBullWithinPriceRangeByPercentageOfProfitRatio(profit_percent=profit_target) ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinPriceRangeByPercentageOfProfitRatio(profit_percent=profit_target) ]
      return True if (len(candidates_bear) > 0) and (len(candidates_bull) > 0) else False

    elif rule_used.lower() == 'either' and (type_used.lower() == 'number' or type_used.lower() == 'number_stock'):
      candidates_bull = [c for c in self.stable_list if c.isBullWithinSharePriceByNumber(number=number_bull) ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinSharePriceByNumber(number=number_bear) ]
      return True if (len(candidates_bear) > 0) or (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'either' and type_used.lower() == 'percentage_stock':
      candidates_bull = [c for c in self.stable_list if c.isBullWithinSharePriceByPercentage(percentage=number_bull) ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinSharePriceByPercentage(percentage=number_bear) ]
      return True if (len(candidates_bear) > 0) or (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'either' and type_used.lower() == 'percentage_profit':
      candidates_bull = [c for c in self.stable_list if c.isBullWithinCostBasisByPercentageOfTotalProfit() ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinCostBasisByPercentageOfTotalProfit() ]
      return True if (len(candidates_bear) > 0) or (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'either' and type_used.lower() == 'number_profit':
      candidates_bull = [c for c in self.stable_list if c.isBullWithinCostBasisByTotalProfit() ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinCostBasisByTotalProfit() ] 
      return True if (len(candidates_bear) > 0) or (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'either' and type_used.lower() == 'weighted_percent_profit':
      candidates_bull = [c for c in self.stable_list if c.isBullWithinCostBasisByWeightedTotalPercentageOfProfit() ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinCostBasisByWeightedTotalPercentageOfProfit() ]
      return True if (len(candidates_bear) > 0) or (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'either' and type_used.lower() == 'weighted_number_profit':
      candidates_bull = [c for c in self.stable_list if c.isBullWithinCostBasisByWeightedTotalProfit() ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinCostBasisByWeightedTotalProfit() ]
      return True if (len(candidates_bear) > 0) or (len(candidates_bull) > 0) else False
    elif rule_used.lower() == 'either' and (type_used.lower() == 't_percent_profit' or type_used.lower() == 'c_percent_profit'):
      profit_target = self.robot.getInTransitionProfitTargetRatio() if (type_used.lower() == 't_percent_profit') else self.robot.getCompletionProfitTargetRatio()
      candidates_bull = [c for c in self.stable_list if c.isBullWithinPriceRangeByPercentageOfProfitRatio(profit_percent=profit_target) ]
      candidates_bear = [c for c in self.stable_list if c.isBearWithinPriceRangeByPercentageOfProfitRatio(profit_percent=profit_target) ]
      return True if (len(candidates_bear) > 0) or (len(candidates_bull) > 0) else False
    return False 

  #If relative time proximity is set
  def isAssetToPurchaseWithinTimeRangeByNumber(self,time_interval):
    candidates = [c for c in self.stable_list if c.isWithinTimeRangeByNumber(time_interval=time_interval) ]
    return True if len(candidates) > 0  else False

  def isBullToBearCostBasisWithinRatioPercentage(self,ratio_percent=10):
    total_cost = self.getTotalCostBasis()
    cost_delta = abs(self.getTotalBullCostBasis() - self.getTotalBearCostBasis())
    return None if (cost_delta==0 or cost_delta==None or (total_cost==0) or (total_cost==None)) else ((100*(cost_delta / total_cost))<ratio_percent)

  #
  # Retrieve all the Roundtrips, where the Bull matches the winning criteria.
  # All the ones on the exclusive_list will be removed. 
  # count: Number of entries to return. exclude_list: 
  # list of Roundtrips to exclude from the list.
  # best: Winners could be Best Performers(True) or Worst Performers (False)
  # 
  def getStableWinningBulls(self,count=1,exclude_list=None, best=True):
    candidates = []
    strategy_type = self.robot.getTransitionStrategyType()
    min_hold_time = None if (self.robot.getMinHoldTimeInMinutes()==0.0) else self.robot.getMinHoldTimeInMinutes()

    if (strategy_type == None) or (strategy_type=='performance'):
      candidates = self.getBestBullCandidates(minimal_age=min_hold_time) if (best==True) else self.getWorstBullCandidates(minimal_age=min_hold_time)
    elif strategy_type == 'asset_price':
      candidates = self.getMostExpensiveBullCandidates(minimal_age=min_hold_time) if (best==True) else self.getLeastExpensiveBullCandidates(minimal_age=min_hold_time)
    elif strategy_type == 'price_inner_spread':
      candidates = self.getMaxBullBearCurrentValueSpread(minimal_age=min_hold_time) if (best==True) else self.getMinBullBearCurrentValueSpread(minimal_age=min_hold_time)
    elif strategy_type == 'price_average_spread':
      candidates = self.getMaxBullSpreadToAveragePrice(minimal_age=min_hold_time) if (best==True) else self.getMinBullSpreadToAveragePrice(minimal_age=min_hold_time)
    elif strategy_type == 'price_average_spread_elligible_only':
      candidates = self.getMaxBullSpreadToAverageElligiblePrice(minimal_age=min_hold_time) if (best==True) else self.getMinBullSpreadToAverageElligiblePrice(minimal_age=min_hold_time)
    
    if candidates == None or len(candidates) == 0: 
      return None 

    if exclude_list == None:
      return candidates[0:count]

    final_candidates = [c for c in candidates if not(c.containedInRoundtrips(roundtrip_list=exclude_list))]
    return final_candidates[0:count]


  def getStableWinningBears(self,count=1,exclude_list=None,best=True):
    candidates = []
    strategy_type = self.robot.getTransitionStrategyType()
    min_hold_time = None if (self.robot.getMinHoldTimeInMinutes()==0.0) else self.robot.getMinHoldTimeInMinutes()

    if (strategy_type == None) or (strategy_type=='performance'):
      candidates = self.getBestBearCandidates(minimal_age=min_hold_time) if (best==True) else self.getWorstBearCandidates(minimal_age=min_hold_time)
    elif strategy_type == 'asset_price':
      candidates = self.getMostExpensiveBearCandidates(minimal_age=min_hold_time) if (best==True) else self.getLeastExpensiveBearCandidates(minimal_age=min_hold_time)
    elif strategy_type == 'price_inner_spread':
      candidates = self.getMaxBullBearCostBasisSpread(minimal_age=min_hold_time) if (best==True) else self.getMinBullBearCostBasisSpread(minimal_age=min_hold_time)
    elif strategy_type == 'price_average_spread':
      candidates = self.getMaxBearSpreadToAveragePrice(minimal_age=min_hold_time) if (best==True) else self.getMinBearSpreadToAveragePrice(minimal_age=min_hold_time)
    elif strategy_type == 'price_average_spread_elligible_only':
      candidates = self.getMaxBearSpreadToAverageElligiblePrice(minimal_age=min_hold_time) if (best==True) else self.getMinBearSpreadToAverageElligiblePrice(minimal_age=min_hold_time)

    if candidates == None or len(candidates) == 0:
      return None 

    if exclude_list == None:
      return candidates[0:count]

    final_candidates = [c for c in candidates if not(c.containedInRoundtrips(roundtrip_list=exclude_list))]
    return final_candidates[0:count]


  def getStableReport(self):
    bull_cheapest  = self.getTheLeastExpensiveBullEntry()
    bear_cheapest  = self.getTheLeastExpensiveBearEntry()
    bull_expensive = self.getTheMostExpensiveBullEntry()
    bear_expensive = self.getTheMostExpensiveBearEntry()
    bull_avg_price = self.getAverageBullPrice()
    bear_avg_price = self.getAverageBearPrice()
    bull_price_spread = self.getSpreadBullPrice()
    bear_price_spread = self.getSpreadBearPrice()
    bull_oldest = self.getOldestStageRoundtripEntry()
    bear_oldest = self.getOldestStageRoundtripEntry()
    bull_youngest= self.getYoungestStageRoundtripEntry()
    bear_youngest= self.getYoungestStageRoundtripEntry()
    age_youngest = self.getTimeEllapsedSinceYoungestAcquisition()
    age_oldest = self.getTimeEllapsedSinceOldestAcquisition()
    age_spread = self.getAgeDifferenceBetweenOldestAndYoungestInStage()

    summary_data = {'stable_size':len(self.stable_list),'bull_cheapest':bull_cheapest,'bear_cheapest':bear_cheapest,
                  'bull_expensive':bull_expensive,'bear_expensive':bear_expensive,'bull_avg_price':bull_avg_price,
                  'bear_avg_price':bear_avg_price,'bull_price_spread':bull_price_spread,'bull_oldest':bull_oldest,
                  'bear_oldest':bear_oldest,'bull_youngest':bull_youngest,'bear_youngest':bear_youngest,
                  'age_oldest':age_oldest,'age_spread':age_spread} 

    #TODO: reconcile with below data
    five_youngest = self.stable_list
    five_youngest.sort(key=lambda rt:rt.getStableBullValue(),reverse=False)
    
    five_most_recent_data = [{'delta':l.getTransitionalDeltaValue(), 'buy_date': l.getAcquisitionDate(),
                              'profit':l.getTransitionalTotalValue(),'duration':l.getDurationInTransition()}
                              for l in five_youngest] 
    stable_data = dict()
    stable_data['summary_data'] = summary_data
    stable_data['content_data'] = five_most_recent_data

    return stable_data 

  def printStableReport(self):
    #TODO: reconcile with above data
    best_bears = self.getAllStableEntriesByBearValue()
    best_bulls = self.getAllStableEntriesByBullValue()    
    bull_p = self.robot.getCurrentBullPrice()
    bear_p = self.robot.getCurrentBearPrice()
    print(" ------------ StableRoundTrips Report at {0} {1} {2}----------".format(self.robot.getCurrentTimestamp(),bull_p,bear_p))
    for n in best_bulls:
      bull = round(n.getStableBullValue(),2)
      bear = round(n.getStableBearValue(),2)
      total = round(n.getStableTotalValue(),2)
      bp = round(n.getBullBuyPrice(),2)
      ep = round(n.getBearBuyPrice(),2)
      cost_basis = round(n.getRoundtripCostBasis())

      print("Bull: {0:04,.2f} ({3:04,.2f}) CB={5}. Bear: {1:,.2f} ({4}). Delta: {2:,.2f} ".format(bull, bear, total,bp,ep,cost_basis))
      print("\n Ratio: {0}".format(n.getStringForRatio()))
    print("\n")
    print(" --------------------------- --------------------------------- --------------------------------- ")
