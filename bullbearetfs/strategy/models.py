from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import datetime
from django.utils import timezone
from django.contrib.auth.models import  User
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple
import datetime, time, pytz, logging, unittest , sys,json
import pandas as pd
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned

#CHOICES_ACQUISITION_TIMEFRAME   = (('simulteaneous','simulteaneous'),('delayed seconds','delayed seconds'),('deferred policy','deferred policy'))
CHOICES_STRATEGY_CLASS=(('Bullish Bearish Pair','Bullish Bearish Pair'),('Equity Bullish Bearish','Equity Bullish Bearish'))
CHOICES_MINIMUM_BEFORE_TRADING   = (('2','2'),('4','4'),('6','6'))
CHOICES_STRATEGY_CATEGORY=(('Babadjou','Babadjou'),('Batcham','Batcham'))
CHOICES_ASSET_COMPOSITION = (('20-80','20-80'),('25-75','25-75'),('30-70','30-70'),('40-60','40-60'),('50-50','50-50'),('60-40','60-40'),('70-30','70-30'),('75-25','75-25'),('80-20','80-20'))
CHOICES_MINIMUM_TIME_BEFORE_PURCHASES   = (('15','15'),('30','30'),('60','60'))
CHOICES_MINIMUM_VOLUME_BETWEEN_PURCHASES   = (('15M','15M'),('30M','30M'),('60M','60M'))
CHOICES_ACQUISITION_PRICE_FACTORS   = (('Bull','Bull'),('Bear','Bear'),('Bull and Bear','Bull and Bear'),('Bull or Bear','Bull or Bear'))
CHOICES_ACQUISITION_VOLATILITY_FACTORS =(('.10','.10'),('.15','.15'),('.20','.20'),('.25','.25'),('.30','.30'))
CHOICES_IN_TRANSITION_ENTER_STRATEGY = (('worstbull_and_worstbear','worstbull_and_worstbear'),('bestbull_and_bestbear','bestbull_and_bestbear'),
	                                    ('bestbull_and_worstbear','bestbull_and_worstbear'),('worstbull_and_bestbear','worstbull_and_bestbear'))
CHOICES_IN_TRANSITION_PROFIT_RATIO = ((-0.25,'-.25'),(-0.15,'-.15'),(-0.10,'-.10'),(0.0,'0.0'),(0.10,'.10'),(0.15,'.15'),(0.25,'.25'),(0.35,'.35'),(0.45,'.45'),(0.50,'.50') )
CHOICES_COMPLETION_PROFIT_RATIO = ((.40,'.40'),(.50,'.50'),(.75,'.75'),(1,'1'),(1.25,'1.25'),(1.50,'1.50'),(1.75,'1.75'),(2,'2'),(2.5,'2.50') )
CHOICES_ACQUISITION_ORDER_TYPE   = (('market','market'),('limit','limit'))
CHOICES_ACQUISITION_TIME_IN_FORCE   = (('day','day'),('gtc','gtc'))
CHOICES_IN_TRANSITION_STRATEGY_TYPE=(('Asset Performance','Asset Performance'),('Asset Acquisition Price','Asset Acquisition Price'),
                                     ('Price Based Inner Spread','Price Based Inner Spread'),('Price Based Average Spread','Price Based Average Spread'),
                                     ('Price Based Average Spread 2','Price Based Average Spread 2'))
CHOICES_STRATEGY_COMPOSITION = (('1Bull x 1Bear','1Bull x 1Bear'),('2Bull x 1Bear','2Bull x 1Bear'),('3Bull x 1Bear','3Bull x 1Bear'),
                                ('1Bull x 2Bear','1Bull x 2Bear'),('1Bull x 3Bear','1Bull x 3Bear'),('2Bull x 2Bear','2Bull x 2Bear'))
CHOICES_IN_TRANSITION_LOAD_FACTOR =  (('25','25'),('50','50'),('75','75'))
CHOICES_COMPLETION_REGRESSION_POLICY   =  (('NO Policy','NO Policy'),('Manual','Manual'),('Automatic','Automatic'))
CHOICES_COMPLETION_REGRESSION_DURATION =  (('-5','-5'),('-3','-3'),('-2','-2'),('-1','-1'))
CHOICES_COMPLETION_REGRESSION_FACTOR   =  (('20','20'),('25','25'),('33','33'))

####Acquisition
CHOICES_TIME_DIFFERENCE_ACQUISITION = (('1','1'),('2','2'),('3','3'),('4','4'),('5','5'))
CHOICES_AND_OR = (('AND','AND'),('OR','OR')) 
CHOICES_NUMBER_OR_PERCENTAGE=(('Stock Price by Number','Stock Price by Number'),('Stock Price by Percentage','Stock Price by Percentage'),
                              ('Profit Target by Number','Profit Target by Number'),('Profit Target by Percentage','Profit Target by Percentage'),
                              ('Weighted Profit by Number','Weighted Profit by Number'),('Weighted Profit by Percentage','Weighted Profit by Percentage'),
                              ('Transition Profit Tgt Percent','Transition Profit Tgt Percent'),('Completion Profit Tgt Percent','Completion Profit Tgt Percent'))



logger = logging.getLogger(__name__)


# Equity Strategy.
# Equity Strategy Class: a set of rules that determine:
# 1. When to initiate the purchase of an equity (AcquisitionPolicy)
# 2. When to dispose of an equity (DispositionPolicy)
# 3. How to protect an asset, once acquired (if needed)
# 4. Which Order types should be used to acquire/dispose of assets
# Each Strategy belongs to a Strategy Class and a Strategy Category. 
# Strategy Class: determines mostly how many symbols will be needed to implement the strategy from begining to end.
# Strategy Category: focuses on the techniques to move the asset from Acquisition to Disposition via
# intermediary stable states. This helps determine the behavior better. Strategy Categy uses the exact same programming
# Paradign.
# Strategy is an abstract concept and shouldn't know about the resources (Symbols) it
# is to be run against. 
# Some strategies work on two assets (Bullish, Bearish ETF), other strategies work with 3 asset pairs (Bullish, Bearish and the
# Etf Symbol (QQQ, TQQQ, SQQQ)
class EquityStrategy(models.Model):
  name = models.CharField(max_length=50,default='')
  description = models.CharField(max_length=150,default='')
  creation_date = models.DateTimeField('date created',default=timezone.now)
  modify_date = models.DateTimeField('date modified',default=timezone.now)
  modified_by = models.ForeignKey('Customer',on_delete=models.PROTECT, blank=True,null=True)
  owner = models.ForeignKey('CustomerBasic',on_delete=models.PROTECT, blank=True,null=True)
  strategy_class=  models.CharField(max_length=25,choices=CHOICES_STRATEGY_CLASS, default='Bullish Bearish Pair')
  strategy_category = models.CharField(max_length=25,choices=CHOICES_STRATEGY_CATEGORY, default='Babadjou')
  visibility = models.BooleanField(default=True)

  #Sell Function will be skipped, if fewer entries are present
  minimum_entries_before_trading = models.CharField(max_length=25,choices=CHOICES_MINIMUM_BEFORE_TRADING, default=2)

  #When loading the first time, wait at a minimum this number of entries:
  #TODO: Rename to start_trade_only_after_fully_loaded. default to False
  trade_only_after_fully_loaded = models.BooleanField(default=True) 

  #Asset Composition on Acquisition (Bulls vs Bear can be set)
  manual_asset_composition_policy =  models.BooleanField(default=True) 
  manual_asset_composition = models.CharField(max_length=25,choices=CHOICES_ASSET_COMPOSITION, default='50-50')
  
  #Client Order ID is used to keep track of orders placed on the server.
  automatic_generation_client_order_id = models.BooleanField(default=True)
  
  def __str__(self):
    return "{0} ".format(self.name)
       
  #
  # Check if the combination of Strategy Class and Strategy Category matches.
  # TODO: Javascript can fix this problem later.
  #
  def isValid(self):
    if (self.strategy_class=='Equity Bullish Bearish') and \
       (self.strategy_category=='Babadjou' or self.strategy_category == 'Batcham'):
      return False 
    return True 
      
  def isBabadjouStrategy(self):
    #R_CHOICES_STRATEGY_CATEGORY = getReversedTuple(tuple_data=CHOICES_STRATEGY_CATEGORY)
    #value = R_CHOICES_STRATEGY_CATEGORY[self.strategy_category]
    return self.strategy_category == 'Babadjou'

  def isBatchamStrategy(self):
    #R_CHOICES_STRATEGY_CATEGORY = getReversedTuple(tuple_data=CHOICES_STRATEGY_CATEGORY)
    #value = R_CHOICES_STRATEGY_CATEGORY[self.strategy_category]
    return self.strategy_category == 'Batcham'
  
  def getCompositionOnAcquisition(self):
    composition = dict()
    composition['bull']=self.getBullishCompositionOnAcquisition()
    composition['bear']=self.getBearishCompositionOnAcquisition()
    return composition

  def getBullishCompositionOnAcquisition(self): 
    if not self.manual_asset_composition_policy:
      return None
    entries = self.manual_asset_composition.split("-")
    if (len(entries)!=2) or ((int(entries[0])+int(entries[1]))!=100):
      return 50
    if not (20 <= int(entries[0]) <= 80):
      return 50
    return int(entries[0])

  def getBearishCompositionOnAcquisition(self): 
    if not self.manual_asset_composition_policy:
      return None
    entries = self.manual_asset_composition.split("-")
    if (len(entries)!=2) or ((int(entries[0])+int(entries[1]))!=100):
      return 50
    if not (20 <= int(entries[1]) <= 80):
      return 50
    return int(entries[1])
  
  #
  # Check if all conditions are met for us to acquire new assets
  # based on our EquityStrategy
  #
  def acquisitionConditionMet(self,robot):
    acquisition = self.getAcquisitionPolicy()
    if (robot == None) or (acquisition == None) or (not self.isValid()) or (not acquisition.isValid()):
      return None 

    #Enough Space on the Stable Box?
    stable_box = robot.getStableRoundTrips()
    maximum_entries = robot.getMaxNumberOfRoundtrips()
    current_entries = stable_box.getStableSize()
    if current_entries >= maximum_entries:
      return False 

    if acquisition.priceProximityOnly():
      return acquisition.applyPriceAcquisitionRule(robot=robot)
    elif acquisition.timeProximityOnly():
      return acquisition.applyTimeAcquisitionRule(robot=robot)
    elif acquisition.priceAndTimeProximity():
      return acquisition.applyTimeAcquisitionRule(robot=robot) and acquisition.applyPriceAcquisitionRule(robot=robot)
    elif acquisition.priceOrTimeProximity():
      return acquisition.applyPriceAcquisitionRule(robot=robot) or acquisition.applyTimeAcquisitionRule(robot=robot)
    elif acquisition.neitherPriceNorTime():
      return False
    return False 


  ############################################################################################################
  # The functions below come from the DispositionPolicy
  # There must be EXACTLY ONE dispositionPolicy associated with each EquityStrategy Policy.
  # Having more than ONE or NONE is a critical error. But must be handled gracefully as possible.
  #
  def getDispositionPolicy(self):
    try:
      disposition = DispositionPolicy.objects.get(strategy_id=self.pk)
      return disposition
    except ObjectDoesNotExist as ex:
      logger.error("ERROR in EquityStrategy.getDispositionPolicy(): ObjectDoesNotExist ".format(ex))
      return None
    except MultipleObjectsReturned as ex:
      logger.error("ERROR: in EquityStrategy.getDispositionPolicy(): MultipleObjectsReturned ".format(ex))
      return None 
    return None 
 
  #
  # Checks if all the conditions are met for the Disposition to be Called properly.
  # This function is not as powerful as the one with Acquisition as the main condition for exit is profit.
  #
  def dispositionConditionMet(self,robot): 
    disposition = self.getDispositionPolicy()
    if (robot == None) or (disposition == None) or (not self.isValid() or (not disposition.isValid())):
      return None 

    #High priority Options:
    if robot.liquidate_on_next_opportunity or robot.sell_remaining_before_buy:
      return True

    #TODO: How to restrict max number of sell transactions per day
    if robot.hasReachedMaxSellTransactionsPerDay():
      return False

    stable_box = robot.getStableRoundTrips()

    #TODO: Challenge: Only focus on assets that can be sold? 
    #Question Should we use  stable_box.getTradableAssetsSize() instead ?
    #Answer: NO. Implementing functions should only select the ones that matter.
    current_entries = stable_box.getStableSize()

    if current_entries < int(self.minimum_entries_before_trading):
      return False 
   
    return True 
  
  def getTransitionLoadFactor(self):
    disposition = self.getDispositionPolicy()    
    is_invalid = (disposition==None or (not self.isValid()) or (not disposition.isValid()) )
    return None if is_invalid else float(disposition.in_transition_load_factor) * .01

  def getRegressionStartDayInMinutes(self,robot):
    disposition = self.getDispositionPolicy()  
    is_invalid = (disposition==None or (not self.isValid()) or (not disposition.isValid()) or robot==None )
    return None if is_invalid else robot.getMaxHoldTimeInMinutes() + int(disposition.completion_regression_duration)*24*60  

  def getCompletionProfitTargetRatio(self,phase=None):
    disposition = self.getDispositionPolicy()
    is_invalid = (disposition==None or (not self.isValid()) or (not disposition.isValid()) )
    return None if is_invalid else disposition.getCompletionProfitTargetRatio(phase=phase)

  def getInTransitionProfitTargetRatio(self):
    disposition = self.getDispositionPolicy()
    is_invalid = (disposition==None or (not self.isValid()) or (not disposition.isValid()) )
    return None if is_invalid else float(disposition.in_transition_profit_target_ratio)

  def getNumberOfBullsInTransitionComposition(self):
    disposition = self.getDispositionPolicy()    
    is_invalid = (disposition==None or (not self.isValid()) or (not disposition.isValid()) )
    return None if is_invalid else disposition.getNumberOfBullsInTransitionComposition()
    
  def getNumberOfBearsInTransitionComposition(self):
    disposition = self.getDispositionPolicy()    
    is_invalid = (disposition==None or (not self.isValid()) or (not disposition.isValid()) )
    return None if is_invalid else disposition.getNumberOfBearsInTransitionComposition()

  def getBestOrWorstBullInTransitionStrategy(self):
    disposition = self.getDispositionPolicy()    
    is_invalid = (disposition==None or (not self.isValid()) or (not disposition.isValid()) )
    return None if is_invalid else disposition.getBestOrWorstBullInTransitionStrategy()

  def getBestOrWorstBearInTransitionStrategy(self):
    disposition = self.getDispositionPolicy()    
    is_invalid = (disposition==None or (not self.isValid()) or (not disposition.isValid()) )
    return None if is_invalid else disposition.getBestOrWorstBearInTransitionStrategy()

  def getTransitionStrategyType(self):
    disposition = self.getDispositionPolicy()    
    is_invalid = (disposition==None or (not self.isValid()) or (not disposition.isValid()) )
    return None if is_invalid else disposition.getTransitionStrategyType()

  #
  # The functions below come from the AcquisitionPolicy
  # 
  def getAcquisitionPolicy(self):
    try:
      acquisition = AcquisitionPolicy.objects.get(strategy_id=self.pk)
      return acquisition
    except ObjectDoesNotExist as ex:
      logger.error("ERROR in EquityStrategy. getAcquisitionPolicy(): ObjectDoesNotExist ".format(ex))
      return None
    except MultipleObjectsReturned as ex:
      logger.error("ERROR: in EquityStrategy.getAcquisitionPolicy(): MultipleObjectsReturned ".format(ex))
      return None 
    return None 

  def getSimultaneousBullBearPurchase(self):
    acquisition = self.getAcquisitionPolicy()
    is_invalid = (acquisition==None or (not self.isValid()) or (not acquisition.isValid()) )
    return None if is_invalid else acquisition.simultaneous_bull_bear_acquisitions

  #
  # The functions below come from the PortfolioProtectionPolicy
  #
  def getAssetProtectionPolicy(self):
    try:
      protection = PortfolioProtectionPolicy.objects.get(strategy_id=self.pk)
      return protection
    except ObjectDoesNotExist as ex:
      logger.error("ERROR in EquityStrategy.getAssetProtectionPolicy(): ObjectDoesNotExist ".format(ex))
      return None
    except MultipleObjectsReturned as ex:
      logger.error("ERROR: in EquityStrategy.getAssetProtectionPolicy(): MultipleObjectsReturned ".format(ex))
      return None 
    return None 

  def enforceProtectionOnDisposition(self):
    protection = self.getAssetProtectionPolicy()
    is_invalid = (protection==None or (not self.isValid()) or (not protection.isValid()) )
    return None if is_invalid else protection.protect_asset_upon_move_to_transition

  def enforceProtectionOnAcquisition(self):
    protection = self.getAssetProtectionPolicy()
    is_invalid = (protection==None or (not self.isValid()) or (not protection.isValid()) )
    return None if is_invalid else protection.protect_asset_upon_acquisition

  def protectWithStopMarketOrder(self):
    protection = self.getAssetProtectionPolicy()
    is_invalid = (protection==None or (not self.isValid()) or (not protection.isValid()) )
    return None if is_invalid else protection.use_stop_market

  def protectWithStopLimitOrder(self):
    protection = self.getAssetProtectionPolicy()
    is_invalid = (protection==None or (not self.isValid()) or (not protection.isValid()) )
    return None if is_invalid else protection.use_stop_limit

  def protectWithTrailingStops(self):
    protection = self.getAssetProtectionPolicy()
    is_invalid = (protection==None or (not self.isValid()) or (not protection.isValid()) )
    return None if is_invalid else protection.use_trailing_stops

  #
  # The functions below come from the PortfolioProtectionPolicy
  #
  def getOrderManagementPolicy(self):
    try:
      orders_mgmt = OrdersManagement.objects.get(strategy_id=self.pk)
      return orders_mgmt
    except ObjectDoesNotExist as ex:
      logger.error("ERROR in EquityStrategy.getOrderManagementPolicy(): ObjectDoesNotExist ".format(ex))
      return None
    except MultipleObjectsReturned as ex:
      logger.error("ERROR: in EquityStrategy.getOrderManagementPolicy(): MultipleObjectsReturned ".format(ex))
      return None 
    return None 

  def getAcquisitionOrderType(self): 
    orders_mgmt = self.getOrderManagementPolicy()
    is_invalid = (orders_mgmt==None or (not self.isValid()) or (not orders_mgmt.isValid()) )
    return None if  is_invalid else orders_mgmt.acquisition_order_type

  def getInTransitionOrderType(self):
    orders_mgmt = self.getOrderManagementPolicy()
    is_invalid = (orders_mgmt==None or (not self.isValid()) or (not orders_mgmt.isValid()) )
    return None if is_invalid else orders_mgmt.transition_order_type

  def getCompletionOrderType(self):
    orders_mgmt = self.getOrderManagementPolicy()
    is_invalid = (orders_mgmt==None or (not self.isValid()) or (not orders_mgmt.isValid()) )
    return None if is_invalid else orders_mgmt.completion_order_type

# Determines if the conditions are met to acquire the assets.
# AcquisitionPolicy consists of Rules that are put together.
# Ideally, these rules would be constructed by the Stratedy Designers.
# Time Proximity Rule: A time proximity rule determines if time interval should be used to acquire assets acquisition time
# Volume Proximity Rule: A Volume proximity rule determines if the volume interval should be used to determin asset acquisition time
# Asset Price Proximity Rule: Price proximity rule determines, if the price interval should be used to determine asset acquisition time.
#  -Bull Price. The rule can be applied to the price of the Bull Asset.
#  -Bear price. The rule can be applied to the price of the Bear Asset
#  -Bull and Bear Price. The rule can be applied to the price of the Bulls And The Bear.
#  -Bull or Bear Price. The rule can be applied to the price of the Bull or the Bear.
# The Condition can be determine 
class AcquisitionPolicy(models.Model):
  #Price Proximity
  acquisition_price_proximity =  models.BooleanField(default=True)
  number_or_percentage = models.CharField(max_length=50,choices=CHOICES_NUMBER_OR_PERCENTAGE, default='Stock Price by Number')
  acquisition_price_factor =  models.CharField(max_length=25,choices=CHOICES_ACQUISITION_PRICE_FACTORS, default='Bull') 
  proximity_calculation_automatic = models.BooleanField(default=True)
  bull_acquisition_volatility_factor =  models.CharField(max_length=25,choices=CHOICES_ACQUISITION_VOLATILITY_FACTORS, default='.10') 
  bear_acquisition_volatility_factor =  models.CharField(max_length=25,choices=CHOICES_ACQUISITION_VOLATILITY_FACTORS, default='.10') 

  #Time Proximity
  acquisition_time_proximity = models.BooleanField(default=False)
  min_time_between_purchases = models.CharField(max_length=25,choices=CHOICES_MINIMUM_TIME_BEFORE_PURCHASES, default='60')
  and_or_1 = models.CharField(max_length=10,choices=CHOICES_AND_OR, default='OR')

  #Volume Proximity
  acquisition_volume_proximity = models.BooleanField(default=False)
  min_volume_between_purchases = models.CharField(max_length=25,choices=CHOICES_MINIMUM_VOLUME_BETWEEN_PURCHASES, default='15M')
  volume_fraction_to_average = models.IntegerField(default=1,blank=True) #NO USE at this time
  and_or_2 = models.CharField(max_length=10,choices=CHOICES_AND_OR, default='OR')

  #Volatility index to use to determine the starting point and the differences between various ...
  simultaneous_bull_bear_acquisitions = models.BooleanField(default=True)
  time_difference_between_acquisitions = models.CharField(max_length=25,choices=CHOICES_TIME_DIFFERENCE_ACQUISITION, default='1')

  creation_date = models.DateTimeField('date created',default=timezone.now)
  modify_date = models.DateTimeField('date modified',default=timezone.now)

  strategy = models.ForeignKey(EquityStrategy,on_delete=models.PROTECT, blank=True,null=True)

  def __str__(self): 
    return "Acquisition Policy-{0}".format(self.pk)
  
  def getBasicInformation(self):
    tp=self.acquisition_time_proximity
    vp=self.acquisition_volume_proximity
    pp=self.acquisition_price_proximity
    return "Acquisition Policy: {0}\n Price Proximity:{1}. Time Proximity={2}. Volume Proximity={3}. ".format(self.pk,pp,tp,vp)

  #Check if AcquisitionPolicy is valid().
  #Always returns True for now.
  def isValid(self):
    if self.acquisition_volume_proximity:
      return False
    if not self.simultaneous_bull_bear_acquisitions:
      return False 
    return True 
 
  def applyVolumeAcquisitionRule(self,robot):
    if self.acquisition_volume_proximity and (robot is not None):
      logger.info("Function is not yet implemented. {0}.".format('applyVolumeAcquisitionRule'))
    return False 

  def applyTimeAcquisitionRule(self,robot):
    if self.acquisition_time_proximity and (robot is not None):
      stable_box = robot.getStableRoundTrips()
      response = stable_box.isAssetToPurchaseWithinTimeRangeByNumber(time_interval = int(self.min_time_between_purchases))
      return True if (response == False) else False 
    return False 

  def processRuleUsed(self,price_factor):
    if price_factor.lower() == 'bull':
      return 'bull'
    elif price_factor.lower() == 'bear':
      return 'bear'
    elif price_factor.lower() == 'bull or bear':
      return 'either'
    elif price_factor.lower() == 'bull and bear':
      return 'both'
    return None   

  def processTypeUsed(self,type_used):
    if type_used.lower() == 'stock price by percentage':
      return 'percentage_stock'
    elif type_used.lower() == 'profit target by percentage':
      return 'percentage_profit'
    elif type_used.lower() == 'stock price by number':
      return 'number'
    elif type_used.lower() == 'profit target by number':
      return 'number_profit'
    elif type_used.lower() == 'weighted profit by number':
      return 'weighted_number_profit'
    elif type_used.lower() == 'weighted profit by percentage': 
      return 'weighted_percent_profit'
    elif type_used.lower() == 'transition profit tgt percent': 
      return 't_percent_profit'
    elif type_used.lower() == 'completion profit tgt percent':
      return 'c_percent_profit'

    return None   

  #def processPercent(type_used,robot):
  #  return 1 
  # weighted_percent_profit, weighted_number_profit, t_percent_profit c_percent_profit

  # Logic is a little odd. If the current price falls within boundaries of existing assets, then the check 
  # fails. We should return True, but we mean FAIL
  def applyPriceAcquisitionRule(self,robot):
    if self.acquisition_price_proximity and (robot is not None):
      stable_box = robot.getStableRoundTrips()
      type_used = self.processTypeUsed(type_used=self.number_or_percentage)
      #tgt_percent = self.processPercent(type_used=type_used,robot=robot)
      rule_used = self.processRuleUsed(price_factor=self.acquisition_price_factor)
      number_bull = float(self.bull_acquisition_volatility_factor)
      number_bear = float(self.bear_acquisition_volatility_factor)
      response = stable_box.isAssetToBuyWithinPriceRange(type_used=type_used,rule_used=rule_used,number_bull=number_bull,number_bear=number_bear)
      return True if (response == False) else False 
    return False 

  def priceProximityOnly(self):
    return self.acquisition_price_proximity and (not self.acquisition_time_proximity)

  def timeProximityOnly(self):
    return self.acquisition_time_proximity and (not self.acquisition_price_proximity)

  def priceAndTimeProximity(self):
    return self.acquisition_time_proximity and self.acquisition_price_proximity and \
           (self.and_or_1 == 'AND')

  def priceOrTimeProximity(self):
    return ( self.acquisition_time_proximity and self.acquisition_price_proximity ) and \
           ( self.and_or_1 == 'OR')

  def neitherPriceNorTime(self):
    return not ( self.acquisition_time_proximity or self.acquisition_price_proximity )

#Asset Disposition Policy.
# There are several disposition strategies, all of them based on the concept of RoundTrip through fixed states.
# Stable --> Transition ---> Completion. Each of them describe a particular state for our Roundtrip.
# Remember: We always acquire assets in pairs (Roundtrip). Here, we say that we are in Stable Position.
# RoundTrip.isStable() should return True.
# At some point, we sell one side. We say that we are in Transition. The decision to sell one side is 
# determined by a variety of factors. Some of which are calculated.
# There are various ways to enter the Transition scenario. These ways are called Transition Types.
# Transition Types can be based on the following factors:
# 1. Total Performance. Performance is measured by the unrealized price of either a Bull or a Bear.
# 2. Asset Price: Price based is measured by the current price of an asset
# 3. Spread Price To Average: Highest paid Bull Price, Highest Paid Bear Price vs Lowest Paid bull price, lowest paid bear price.
# 4. Asset Age: Oldest Bull/Oldest bear, Youngest Bull, Youngest bear. Remember: Bear and Bought are bought at the same time.
#    Therefore, the concept of age might not be very significant here ... but could be in other cases.
#    We don't want to sell the same bull and bear from the same Roundtrip.
# 5. Random within Group: random.choice(seq) in Python between [0,...,N]
# 6. Price Comparison to Average Price: Select Item, whose price is closest/furthest to the Average Purchase Price
# 7. Composition Based, Reverse Composition Based. 
# 8. Absolute Asset Spread Within the Assets itself. abs(Bull Current - Bear Current Value) getBullBearCurrentValueSpread()
# 9. Relative Asset Spread within the Asset itself. abs(Current RT Value)/ Current Value    getBullBearCostBasisSpread()
# 10. NOTE: #9 and #8 are also risk factors when Composition is different from 50%. 
#    In other words, as the asset moves in one direction vs another, how much are we potentially losing/gaining?
#    How much are we exposing ourselves?
#   The following should be calculable in the Batcham Strategy ...
#  What is the asset composition I need in order to cap my risk at 25% of investment in case of a 25% market swing?
#  'Asset Performance', 'Asset Acquisition Price', 'Price Based Inner Spread', 'Price Based Average Spread','' 
# Regression: An asset is in regression if it has been owned pass a certain period of time. 
# It has been sitting on the assembly line too long.
# max_hold_time: tells us how long we want to own an asset at the most.
# regression_policy: tells us how we want to handle an asset that has been owned pass a certain amount of time. 
# if we have defined a regression policy and want to leverage it.
# having a regression policy allows us to start diversting of assets at discounted prices, if they are sitting too long
# on the assembly line.  
# RoundTrip.isInRegression(): if it is inTransition() and max_hold_time = 14 days = 14 *24 * 60 minutes.
# If regression_duration = 25, it means it has been owned more than 14 * (100-25)*24*60 minutes.
#Validate that min_hold _time is lower than Max Hold Time.
# robot.getMaxHoldTimeInMinutes()
# BabadjouWinnerRoundtrip.isRegression() if all assets are in regression()
#
class DispositionPolicy(models.Model):
  in_transition_profit_policy = models.BooleanField(default=True)
  in_transition_profit_target_ratio = models.CharField(max_length=25,choices=CHOICES_IN_TRANSITION_PROFIT_RATIO, default='.10')

  completion_profit_policy = models.BooleanField(default=True)
  completion_complete_target_ratio = models.CharField(max_length=25,choices=CHOICES_COMPLETION_PROFIT_RATIO, default='.40')

  in_transition_asset_composition = models.CharField(max_length=25,choices=CHOICES_STRATEGY_COMPOSITION, default='1Bull x 1Bear')
  in_transition_strategy_type     = models.CharField(max_length=50,choices=CHOICES_IN_TRANSITION_STRATEGY_TYPE, default='Asset Performance')

  in_transition_entry_strategy = models.CharField(max_length=25,choices=CHOICES_IN_TRANSITION_ENTER_STRATEGY, default='worstbull_and_worstbear')
  in_transition_load_factor = models.CharField(max_length=10,choices=CHOICES_IN_TRANSITION_LOAD_FACTOR, default='25')

  #Regression Information
  completion_regression_policy = models.CharField(max_length=25,choices=CHOICES_COMPLETION_REGRESSION_POLICY, default='Automatic')
  completion_regression_duration = models.CharField(max_length=10,choices=CHOICES_COMPLETION_REGRESSION_DURATION, default='-3')
  completion_regression_factor = models.CharField(max_length=10,choices=CHOICES_COMPLETION_REGRESSION_FACTOR, default='25')

  creation_date = models.DateTimeField('date created',default=timezone.now)
  modify_date = models.DateTimeField('date modified',default=timezone.now)
  strategy = models.ForeignKey(EquityStrategy,on_delete=models.PROTECT,blank=True,null=True) 
  
  def __str__(self):
    return "Disposition-{0} ".format(self.pk)

  def isValid(self):
    if not self.in_transition_profit_policy:
      return False 
    if not self.completion_profit_policy:
      return False 
    return True 

  #def getRegressionStartDayInMinutes(self):
  #  return float(self.something * float(self.completion_regression_duration / 100))
  #Transition Load Factor is how many entries do we have in Transition?
  #Let's say we have 20 entries in Transition and we need 2 entries for transition,
  #Then we will need max of 24/2 = 12 entries. Load factor of 75 means we should only have 12 * 3/4 = 9 entries
  def getCompletionProfitTargetRatio(self,phase=None):
    if not self.isValid():
      return None 

    #If regression_policy == 'NO Policy', ignore regression logic.
    if (phase==None) or (phase=='green') or (self.completion_regression_policy == 'NO Policy'):
      return float(self.completion_complete_target_ratio) 
    
    #regression_policy is implemented. Let's use it.
    #The completion ratio goes down as we get closer to Max_Hold_day.
    #TODO: SHOULD We should get to ZERO, when in RED.
    base = float(self.completion_complete_target_ratio)

    factor = float(self.completion_regression_factor) * .01
    
    if (phase=='yellow'):
      return float(self.completion_complete_target_ratio) * (1 - 1* factor)
    elif (phase =='orange'):
      return float(self.completion_complete_target_ratio) * (1 - 2* factor)
    elif (phase =='red'):
      return float(self.completion_complete_target_ratio) * (1 - 3* factor)
    return float(self.completion_complete_target_ratio) 
  
  #Determines how to select elements to enter the Transition Strategy.
  #Could select: bestbull_and_bestbear,...
  def getBestOrWorstBullInTransitionStrategy(self):
    if not self.isValid():
      return None 
    if self.in_transition_entry_strategy == 'worstbull_and_worstbear' or \
       self.in_transition_entry_strategy == 'worstbull_and_bestbear':
      return False 
    elif self.in_transition_entry_strategy == 'bestbull_and_worstbear' or \
       self.in_transition_entry_strategy == 'bestbull_and_bestbear':
      return True 
    return None 

  def getBestOrWorstBearInTransitionStrategy(self):
    if not self.isValid():
      return None 
    if self.in_transition_entry_strategy == 'worstbull_and_worstbear' or \
       self.in_transition_entry_strategy == 'bestbull_and_worstbear':
      return False 
    elif self.in_transition_entry_strategy == 'bestbull_and_bestbear' or \
       self.in_transition_entry_strategy == 'worstbull_and_bestbear':
      return True 
    return None 

  #Determines how many bulls we want intransition.
  def getNumberOfBullsInTransitionComposition(self):
    if not self.isValid():
      return None 
    if self.in_transition_asset_composition == '1Bull x 1Bear' or \
       self.in_transition_asset_composition == '1Bull x 2Bear' or \
       self.in_transition_asset_composition == '1Bull x 3Bear':
      return 1
    elif  self.in_transition_asset_composition == '2Bull x 1Bear' or \
          self.in_transition_asset_composition == '2Bull x 2Bear':
      return 2
    elif self.in_transition_asset_composition == '3Bull x 1Bear':
      return 3 
    return None

  def getNumberOfBearsInTransitionComposition(self):
    if not self.isValid():
      return None 
    if self.in_transition_asset_composition == '1Bull x 1Bear' or \
       self.in_transition_asset_composition == '2Bull x 1Bear' or \
       self.in_transition_asset_composition == '3Bull x 1Bear':
      return 1
    elif  self.in_transition_asset_composition == '1Bull x 2Bear' or \
          self.in_transition_asset_composition == '2Bull x 2Bear':
      return 2
    elif self.in_transition_asset_composition == '1Bull x 3Bear':
      return 3 
    return None
 
  def getTransitionStrategyType(self): 
    if not self.isValid():
      return None 
    if self.in_transition_strategy_type == 'Asset Performance': 
      return 'performance'
    elif self.in_transition_strategy_type == 'Asset Acquisition Price': 
      return 'asset_price'
    elif self.in_transition_strategy_type == 'Price Based Inner Spread': 
      return 'price_inner_spread'
    elif self.in_transition_strategy_type == 'Price Based Average Spread': 
      return 'price_average_spread'
    elif self.in_transition_strategy_type == 'Price Based Average Spread 2': 
      return 'price_average_spread_elligible_only'
    return None 

# Configure how to protect assets currently owned
# Should Orders be protected upon purchase?
# Should second Asset be protected upon disposition of one? 
# No Protection is necessary, when entering both sides. Therefore no Stop Limit
# Upon first leg disposition, second asset must be protected
# What should the value of the protection be?
# Dispose of winner first.
class PortfolioProtectionPolicy(models.Model):
  protect_asset_upon_acquisition = models.BooleanField(default=False)
  protect_asset_upon_move_to_transition = models.BooleanField(default=False)
  use_trailing_stops = models.BooleanField(default=False)
  use_stop_market = models.BooleanField(default=False)
  use_stop_limit = models.BooleanField(default=False)

  creation_date = models.DateTimeField('date created',default=timezone.now)
  modify_date = models.DateTimeField('date modified',default=timezone.now)
  strategy = models.ForeignKey(EquityStrategy,on_delete=models.PROTECT, blank=True,null=True)  

  def __str__(self):
    return "Protection-{0} ".format(self.pk)

  def isValid(self):
    if self.protect_asset_upon_acquisition or \
      self.protect_asset_upon_move_to_transition or \
      self.use_trailing_stops or \
      self.use_stop_limit or \
      self.use_stop_market:
      return False 
    return True 


#Strategy to be used.
#1. Only purchase Leveraged ETFs, Always purchase both sides at the same time, for the same amount of money.
#2. Upon purchase, place an order to sell both side at the desired profit point. No need to protect the asset.
#3. Once one side sells, we know we have made profit. Immediately, we need to place protection for the second asset
#as well as the target sale price. This is the riskest time in the whole transaction. 
#Configure how orders should be placed.
#Note that 
#Should Orders be Market Orders on sell? on buy? Should I use trailing stops? How do I set them?
class OrdersManagement(models.Model):
  time_in_force_buy_orders = models.CharField(max_length=25,choices=CHOICES_ACQUISITION_TIME_IN_FORCE, default='day')
  time_in_force_sell_orders = models.CharField(max_length=25,choices=CHOICES_ACQUISITION_TIME_IN_FORCE, default='day')
  
  acquisition_order_type = models.CharField(max_length=25,choices=CHOICES_ACQUISITION_ORDER_TYPE, default='market')
  transition_order_type = models.CharField(max_length=25,choices=CHOICES_ACQUISITION_ORDER_TYPE, default='market')
  completion_order_type = models.CharField(max_length=25,choices=CHOICES_ACQUISITION_ORDER_TYPE, default='market')

  creation_date = models.DateTimeField('date created',default=timezone.now)
  modify_date = models.DateTimeField('date modified',default=timezone.now)
  strategy = models.ForeignKey(EquityStrategy,on_delete=models.PROTECT, blank=True,null=True)
  
  def __str__(self):
    return "Orders-Management-{0} ".format(self.pk) 

  def isValid(self):
    return True 
