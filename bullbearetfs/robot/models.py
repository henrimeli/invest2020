from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import datetime
from django.utils import timezone
from django.contrib.auth.models import  User
import logging, json, time, pytz, asyncio, re
from datetime import timedelta
import dateutil.parser
from django.db.models import Sum,Avg,Max,Min
from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers import serialize

from bullbearetfs.robot.activitysentiments.models import EquityAndMarketSentiment, RobotActivityWindow
from bullbearetfs.robot.budget.models import RobotBudgetManagement, Portfolio
from bullbearetfs.robot.symbols.models import RobotEquitySymbols
from bullbearetfs.eventcapture.models import StartupStatus
from bullbearetfs.models import Customer, EquityTradingData
from bullbearetfs.executionengine.models import ETFPairRobotExecutionData
from bullbearetfs.strategy.models import EquityStrategy
from bullbearetfs.utilities.orders import RobotSellOrderExecutor, RobotBuyOrderExecutor
from bullbearetfs.utilities.alpaca import AlpacaPolygon
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, shouldUsePrint, fixupMyDateTime, timezoneAwareDate,strToDatetime
from bullbearetfs.errors.customerrors import InvalidTradeDataHolderException
from bullbearetfs.robot.foundation.roundtrip import RoundTrip
from bullbearetfs.robot.foundation.stableroundtrip import StableRoundTrips
from bullbearetfs.robot.foundation.completedroundtrip import CompletedRoundTrips

from bullbearetfs.strategies.babadjou import BabadjouStrategy
from bullbearetfs.strategies.batcham import BatchamStrategy
#from bullbearetfs.strategies.strategyreferences import BabadjouStrategy
from asgiref.sync import async_to_sync
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

CHOICES_ROBOT_SLEEP_TIME_BETWEEN_TRADES = (('1','1'),('2','2'),('5','5'),('10','10'))
CHOICES_MAX_HOLD_DAYS = (('5','5'),('14','14'),('21','21'),('30','30'),('No Max','No Max'))
CHOICES_REGRESSION_FACTOR = (('100,50,33','100,50,33'),('50,33,25','50,33,25'),('30,20,10','30,20,10'))
CHOICES_MIN_HOLD_DAYS = (('0','0'),('0.5','0.5'),('1','1'),('1.5','1.5'),('2','2'),('3','3'),('4','4'),('5','5'),('7','7')) # trading sessions
CHOICES_DATA_SOURCE =(('live','live'),('backtest','backtest'),('paper','paper')) 
CHOICES_ROUNDTRIPS =(('4','4'),('8','8'),('10','10'),('12','12')) 
CHOICES_ROUNDTRIPS_COST_BASIS = (('500','500'),('1,000','1,000'),('1,500','1,500'),('2,500','2,500'),('4,000','4,000'),('5,000','5,000')) 
CHOICES_ROUNDTRIPS_PROFIT_TARGETS = (('.05','.05'),('.075','.075'),('.1','.1'),('.15','.15'))
CHOICES_VERSION_INFORMATION = (('1.0.0','1.0.0'),('2.0.0','2.0.0'))
CHOICES_MAX_TRANSACTIONS_PER_DAY=(('1','1'),('2','2'),('unlimited','unlimited'))



# A ETFAndReversePairRobot Object is an automated and autonoumous runner, that processes Stock Market Events at given
# intervals, then to decide when to acquire and dispose of Assets. Its main purpose is to generate profit consistent 
# and steady profits. In opposition to other robots, who are looking to make lots of money in one trade. 
# A ETFAndReversePairRobot focuses solely on Stock Market Equities, especially Bull/Bear ETF Pairs. 
# A ETFAndReversePairRobot is created and configured once then deployed. From here, it is expected to runs automatically 
# and makes autonomous decisions based on its configuration and strategies until it is stopped.
# Because this Robot can purchase Bulls and Bears, it is expected to run in almost all market conditions. 
#  
# During its run, there should be as little manual intervention as possible. It should be capable of running successfully 
# on its own and produce results that beat the major indexes over the short and the long term (after exclusing comissions and taxes).
#
# A ETFAndReversePairRobot is the central Element of the Egghead Platform and it is expected to interact with all other
# Subcomponents such as: BudgetManagement, SymbolsSelection, Strategy Management, Testing, Brokerages, ... etc.
#
# Attributes: Are used to represent the internal state of a Robot. Can be configured via the UI.
# Functions: The Robot functions are used to communicate with other Subcomponents.
# Robot Internal Information:
# Robot Communication with External Components:
#   -Foundational Components: Acquisition/Disposition Order preparation. Recording of new Bull/Bear pair Acquisition
#   -Portfolio/BudgetManagement: Determine if there is enough money in the budget to acquire asset. hasEnoughFunds()
#   -Equity Symbols: Determine which Bull/Bear Pair is to be traded by this robot. symbols attribute.
#   -Activity Window/Sentiments: Determine if the Robot can trade at the given Time. canTradeNow(), Determines the current Sentiment.
#   -Robot Conditionals: This is coming together of all components to determine acquisition/disposition time is right.
#   -Logging/Reporting: This is the set of Reporting Data about to robot to be displayed on the UI or Command line
#   -Brokerage APIs: Placing Trades, Recording Trades that have been completed into the system
#   -Strategies Infrastructure: Determines which strategy has been selected. 
#   -Data Sources: Once a Data Source has been selected, feed the data coming the data source to the
#   -Runtime Server: The Runtime Server is the active process that monitors the market and the Brokerage and pass the information
#   -Customer Manegement:
#   -Utilities Components: Make use of utility functions.
#   -Event captures: 
#   -Business Intelligence: Communicates with the 
#   -Execution Engine: 
#   -
# Robot Conditionals: canTradeNow()
# Robot UI Elements:
# At creation time, the user can select some configuration parameters specific to the robot.
# Some Basic Paratemeters such as: Name, Description, Min/Max hold time.
# Some more advanced Parameters such as: The Strategy to use, the Sybmbols pairs to use,  and how to spread the budget
# of each acquisition. The user can also configured things such as:
# 
# Then the user will select the strategy the Robot should run. Each Strategy requires a certain set of parameters
# to be calculated and optimized.
#  # The stages of the Robot. Stable, InTransition and Completion
  # Once the initialization completes, the ... moves into the trading phase.
  # During the trading phase, roundtrips are moved through their own stages.
  # The stages of each Roundtrip : Stable Phase, Transition Phase, Completion Phase.
  # What is a Roundtrip? A Roundtrip is the ownership of two assets that move in opposite direction at the same time.
  # We must own both assets in exact cost basis value. i.e.: We buy TQQQ & SQQQ for the exact same amount of money
  # at the same time. Acquisition is always done exactly at the same time.
  # After acquisition, the portfolio is stable. And regardless of the direction the market goes, our portfolio will
  # Always have the same value. Using this strategy allows us to enter the market at any time, regardless of conditions.
  # This eliminates the need to use speculative means to enter the market.
  # Once the market has moved enough in one direction, we can now exit one position and take profit.
  # At this point, the roundtrip moves into its transition period.
  # While stable, each Roundtrip is safe.
  # Robot has mini
  #################################################################################
class ETFAndReversePairRobot(models.Model):
  name = models.CharField(max_length=50,default='')
  description = models.CharField(max_length=50,default='')
  enabled = models.BooleanField(default=False) #Running?
  visibility = models.BooleanField(default=False) #Should be made visible?
  version=models.CharField(max_length=10,choices=CHOICES_VERSION_INFORMATION, default='1.0.0')
  creation_date = models.DateTimeField('date created',default=timezone.now)
  modify_date = models.DateTimeField('date modified',default=timezone.now)

  max_hold_time = models.CharField(max_length=10,choices=CHOICES_MAX_HOLD_DAYS, default='5')
  minimum_hold_time = models.CharField(max_length=5,choices=CHOICES_MIN_HOLD_DAYS, default='1')
  hold_time_includes_holiday = models.BooleanField(default=False)
  #If set, do not buy anymore ... but sell  
  sell_remaining_before_buy = models.BooleanField(default=False) 
  # If set, liquidate holdings as soon as possible.
  liquidate_on_next_opportunity = models.BooleanField(default=False) 
  #To be used with client order id generation
  internal_name = models.CharField(max_length=10,default='egghead',blank=True)
  # check system every 60 seconds. Sleep pattern within the robot 
  live_data_check_interval = models.CharField(max_length=10,choices=CHOICES_ROBOT_SLEEP_TIME_BETWEEN_TRADES, default='1')  
  #Testing, Live, ...etc
  data_source_choice = models.CharField(max_length=10,choices=CHOICES_DATA_SOURCE, default='backtest')

  max_sell_transactions_per_day =models.CharField(max_length=10,choices=CHOICES_MAX_TRANSACTIONS_PER_DAY, default='unlimited')
  ################## Roundtrip concept: Transactions #####################################################
  # We want to recycle StableBox 3 times within a trading week = 3x20 acquisitions, 3x20 sales = 120 transactions.
  # at 2500 * .005 = $12.5 per exit (sale) transaction, we should be at $750 per week.
  # If the size of Stable is 10. We invest $2500 per Roundtrip. Total investment is $2500 each time we are full.
  max_roundtrips = models.CharField(max_length=10,choices=CHOICES_ROUNDTRIPS, default='10')
  cost_basis_per_roundtrip = models.CharField(max_length=10,choices=CHOICES_ROUNDTRIPS_COST_BASIS, default='10')
  profit_target_per_roundtrip = models.CharField(max_length=10,choices=CHOICES_ROUNDTRIPS_PROFIT_TARGETS, default='.05')

  #Ownership Management
  owner = models.ForeignKey(Customer, on_delete=models.PROTECT,blank=True,null=True)  
  #Portfolion Management
  portfolio = models.ForeignKey(Portfolio, on_delete=models.PROTECT,blank=True,null=True)
  #Strategy Management
  strategy = models.ForeignKey(EquityStrategy,on_delete=models.PROTECT,blank=True,null=True)
  #Equities Management
  symbols = models.ForeignKey(RobotEquitySymbols,on_delete=models.PROTECT,blank=True,null=True)

  #TO BE DELETED. TO BE DELETED. TO BE DELETED. TO BE DELETED. TO BE DELETED.
  regression_factor = models.CharField(max_length=20,choices=CHOICES_REGRESSION_FACTOR, default='100,50,33')

  # 
  # These variables should change with every new tick.
  #
  current_bull_price= 0
  current_bear_price= 0
  current_timestamp = datetime.now(getTimeZoneInfo())
  execution_engine = None
  last_daily_update = None


  # ##########################################################################
  #     Make sure to check the Budget ...
  #
  # 
  #def __init__(self):
  #  super().__init__()
  #  self.portfolio.synchronizeBudgetWithBrokerage()



  def __str__(self):
  	return " {0} {1}".format(self.name, self.pk)
  		                                 
  # ##########################################################################
  #     Robot Basic Information Getters ...
  #
  # Switch from Enable to Disable safely
  #
  def toggleEnabled(self):
    self.disconnectSafely() if self.enabled else self.connectSafely()
    self.save()

  def disconnectSafely(self):
    self.enabled = False
    self.recordDisconnectionTransaction()

  def connectSafely(self):
    self.enabled = True
    self.recordConnectionTransaction() 

  def isEnabled(self):
    return self.enabled

  def isVisible(self):
    return self.visibility

  def getCurrentBullPrice(self):
  	return self.current_bull_price

  def getCurrentBearPrice(self):
  	return self.current_bear_price

  def getCurrentTimestamp(self):
  	return self.current_timestamp

  def getBullishSymbol(self):
    return self.symbols.bullishSymbol

  def getBearishSymbol(self):
    return self.symbols.bearishSymbol

  def getSymbol(self):
  	return self.symbols.symbol

  def getRobotVersion(self):
  	return self.version 

  #
  # Variables below come from the Robot directly
  #
  def getMaxNumberOfRoundtrips(self):
    return int(self.max_roundtrips)

  def getMaximumAssetHoldTime(self):
    return self.max_hold_time

  def getMaxHoldTimeInMinutes(self): 
    return float(self.max_hold_time) * 24 * 60

  def getMinimumAssetHoldTime(self):
    return self.minimum_hold_time  

  def getMinHoldTimeInMinutes(self):
    return float(self.minimum_hold_time) * 24 * 60  

  def getProfitTargetPerRoundtrip(self):
    return float(self.profit_target_per_roundtrip )

  def getBullTransitionProfitTarget(self):
    return self.getInTransitionProfitTarget()

  def getBearTransitionProfitTarget(self):
    return self.getInTransitionProfitTarget()

  #TODO: The numbers below are wrong and need to be fixed
  def getBullWeightedProfitTargetPerRoundtrip(self):
    return self.getProfitTargetPerRoundtrip() * self.getBullishComposition() * 0.01

  def getBearWeightedProfitTargetPerRoundtrip(self):
    return self.getProfitTargetPerRoundtrip() * self.getBearishComposition() * 0.01

  def getInTransitionProfitTarget(self):
    return self.getProfitTargetPerRoundtrip() * self.getInTransitionProfitTargetRatio()

  def getCompletionProfitTarget(self):
    return self.getProfitTargetPerRoundtrip() * self.getCompletionProfitTargetRatio()

  def shouldRemainingAssetsBeSoldBeforeAnyAcquisition(self):
    return self.sell_remaining_before_buy

  def shouldLiquidateAssetsAtNextAvailableOpportunity(self):
    return self.liquidate_on_next_opportunity

  def getInternalName(self):
    return self.internal_name

  #Production
  def isDataSourceLiveFeed(self):  
    return self.data_source_choice == 'live'

  #UAT
  def isDataSourcePaperAccount(self):
    return self.data_source_choice == 'paper'

  #SIT
  def isDataSourceBacktest(self):
    return self.data_source_choice == 'backtest'

  #SIT
  def isDataSourceLocal(self):
    return self.isDataSourceBacktest()

  def getRobotSleepTimeBetweenChecks(self):
    return self.live_data_check_interval

  #Sets the Execution. Clear Any Data that might have been present before
  def setExecutionEngine(self,execution_engine=None,purge_previous=True):
    self.execution_engine = execution_engine
    if purge_previous:
      TradeDataHolder.deleteExecutionEngineEntries(robot=self)


  # #######################################################################################
  #  Robot Symbols functionality is presented here. 
  #  Dereferrencing functions implemented at the RobotSymbol level.
  #
  def getSymbolsPairAsPayload(self):
    return self.symbols.getSymbolsPairAsPayload()

  def getCurrentTrend(self):
    return self.getStableRoundTrips().getCurrentTrend()

  # #######################################################################################
  #  Robot Market Sentiment influences Asset Composition. 
  #  Asset Composition depends on two places. Market Activity (Automatic) or Strategy (Manual).
  #  Must figure out how to synchronize both all the time. Via Javascript would be best.
  #  When one side it saved, it should adjust the other side.
  def getSentimentWindow(self):
    return self.getMaximumAssetHoldTime()

  def assetCompositionIsManual(self):
    return False if self.strategy==None else self.strategy.manual_asset_composition_policy

  def assetCompositionIsAutomatic(self):
    return not self.assetCompositionIsManual()

  def assetCompositionIsDynamic(self):
    #return True
    return not self.assetCompositionIsManual()

  def assetCompositionIsFromStrategy(self):
    return not self.assetCompositionIsManual()

  def getAssetComposition(self):
    sentiment = EquityAndMarketSentiment.objects.get(pair_robot_id=self.pk)
    if self.assetCompositionIsDynamic():
      #composition = sentiment.getAssetComposition(current_trend=self.getCurrentTrend())
      composition = sentiment.getBalancedAssetComposition()
    elif self.assetCompositionIsManual():
      composition = sentiment.getBalancedAssetComposition()
    else:
      composition = self.strategy.getCompositionOnAcquisition()
      #composition = self.strategy.getBullishCompositionOnAcquisition()
    #print("  Asset Composition: {} ".format(composition))
    return composition

  def getBullishComposition(self):
    #if self.assetCompositionIsAutomatic():
    #  sentiment = EquityAndMarketSentiment.objects.get(pair_robot_id=self.pk)
    #  bullishRatio = sentiment.getBullishComposition()
    #else:
    #  bullishRatio = self.strategy.getBullishCompositionOnAcquisition()
    composition = self.getAssetComposition()
    return int(composition['bull'])
    #return bullishRatio

  def getBearishComposition(self):
    composition = self.getAssetComposition()
    return int(composition['bear'])
    #if self.assetCompositionIsAutomatic():
    #  sentiment = EquityAndMarketSentiment.objects.get(pair_robot_id=self.pk)
    #  bearishRatio = sentiment.getBearishComposition()
    #else:
    #  bearishRatio = self.strategy.getBearishCompositionOnAcquisition()
    
    #return bearishRatio
 
  def hasReachedMaxSellTransactionsPerDay(self):
    if shouldUsePrint():
      print("Maximum Number of Sales: {}".format(self.max_sell_transactions_per_day))
    if self.max_sell_transactions_per_day == 'unlimited':
      return False
    completed = self.getCompletedRoundTrips()
    return completed.getTodayMaxTransactionsSize() >= int(self.max_sell_transactions_per_day)

  # #######################################################################################
  #     Market Trading Window  ...
  #  How and where is data added to capture the trading window?
  #  Only question it needs to answer is: Can I trade now?
  #
  def canTradeNow(self,current_time):
    activity_window = RobotActivityWindow.objects.get(pk=self.pk)
    return activity_window.canTradeNow(current_time=current_time)

  # ##########################################################################
  #            Portfolio & Budgets ...
  def updateBudgetAfterPurchase(self,amount=0):
    logger.info("Updating Robot Cash Position following Purchase. {0}".format(amount))
    budget = RobotBudgetManagement.objects.get(pair_robot_id=self.pk)    
    return budget.updateBudgetAfterAcquisition(amount=amount)

  def updateBudgetAfterDisposition(self,amount=0):
    logger.info("Updating Robot Cash Position following Disposition. {0}".format(amount))
    budget = RobotBudgetManagement.objects.get(pair_robot_id=self.pk)    
    return budget.updateBudgetAfterDisposition(amount=amount)
  
  def haveEnoughFundsToPurchase(self):
    budget = RobotBudgetManagement.objects.get(pair_robot_id=self.pk)    
    return  budget.haveEnoughFundsToPurchase()  

  def getCostBasisPerRoundtrip(self):
    budget = RobotBudgetManagement.objects.get(pair_robot_id=self.pk)    
    return  budget.getCostBasisPerRoundtrip()  


  # ##########################################################################
  #   Events such as CatastrMarket events
  def noCatastrophicEventHappening(self):
    sentiment = EquityAndMarketSentiment.objects.get(pair_robot_id=self.pk)    
    return not sentiment.isMarketCrashing()

  # ##########################################################################
  #   Events such as CatastrMarket events
  # 

  def noIssuesWithBrokerage(self):
  	#TODO: How about day trading rules? We need to keep track, so that we don't break it.
  	return True 

  # ############################################################################################
  #  InfraIsReadyForAssetAcquisition:
  #  Infrastructural Event are event that can't be classified in any of the other event groups.
  #  One of the events could be that we have reached the limit of entries on the Assembly Line.
  def infraIsReadyForAssetAcquisition(self):
  	return  True 

  # ##########################################################################
  # InfraIsReadyForAssetDisposition: 
  # Infrastructural Event are event that can't be classified in any of the other event groups.
  # One could be that we haven't reached the minimum as specified by the Strategy.
  def infraIsReadyForAssetDisposition(self):
  	return  True 

  # ##########################################################################
  #    EquityStrategy Model Information   
  #   These functions get their data from the EquityStrategy Model.
  #
  def isBatchamStrategy(self):
    return False if self.strategy==None else self.strategy.isBatchamStrategy() 

  def isBabadjouStrategy(self):
    return False if self.strategy==None else self.strategy.isBabadjouStrategy() 


  # ##########################################################################
  #  Acquisition, Disposition Policies ...
  #
  def acquisitionConditionMet(self):
  	return False if self.strategy==None else self.strategy.acquisitionConditionMet(robot=self)

  def dispositionConditionMet(self):
  	return False if self.strategy==None else self.strategy.dispositionConditionMet(robot=self)

  def getCompletionProfitTargetRatio(self):
  	return 0.5 if self.strategy==None else self.strategy.getCompletionProfitTargetRatio()

  def getInTransitionProfitTargetRatio(self):
  	return 0.5 if self.strategy==None else self.strategy.getInTransitionProfitTargetRatio()

  def getBestOrWorstBullInTransitionStrategy(self):
    return True if self.strategy==None else self.strategy.getBestOrWorstBullInTransitionStrategy()

  def getBestOrWorstBearInTransitionStrategy(self):
    return True if self.strategy==None else self.strategy.getBestOrWorstBearInTransitionStrategy()

  def getNumberOfBullsInTransitionComposition(self):
    return 1 if self.strategy==None else self.strategy.getNumberOfBullsInTransitionComposition()

  def getNumberOfBearsInTransitionComposition(self):
    return 1 if self.strategy==None else self.strategy.getNumberOfBearsInTransitionComposition()

  def getTransitionStrategyType(self):
  	return None if self.strategy==None else self.strategy.getTransitionStrategyType()

  def getTransitionLoadFactor(self):
  	return 0.5 if self.strategy==None else self.strategy.getTransitionLoadFactor()

  def getMinimumEntriesForStrategy(self):
  	return 2
  #def getRegressionTime(self):
  #  return 0 if self.strategy==None else self.strategy.getRegressionStartDayInMinutes()

  def getRegressionStartDayInMinutes(self):
    return 0 if self.strategy==None else self.strategy.getRegressionStartDayInMinutes() 

  # ##########################################################################
  #            Order Management, Portfolio Protection Strategy
  #
  # TODO: Based on various criteria, determine if I should use:
  #   -Market Order (liquid asset, business hours)
  #   -Limit Order  ( extended trading hours, ... etc.)
  def getAcquisitionOrderType(self):
    return self.strategy.getAcquisitionOrderType()
 
  def getInTransitionSellOrderType(self):
    return self.strategy.getInTransitionSellOrderType()

  def getCompletionSellOrderType(self):
    return self.strategy.getCompletionSellOrderType()

  def getAssetProtectionStrategy(self):
  	return self.strategy.retrieveAssetProtectionStrategy()

  # ################# ASSEMBLY LINE ELEMENTS FUNCTIONS ##############################
  #
  # Returns the various interfaces to the different stages within our application.
  #
  def getStableRoundTrips(self):
    stable_box = StableRoundTrips(robot=self)
    return stable_box

  def getCompletedRoundTrips(self):
    completed = CompletedRoundTrips(robot=self)
    return completed     

  #def getInTransitionRoundTrips(self):
  #  in_transition = InTransitionRoundTrips(robot=self)
  #  return in_transition

  #def getTransitionalCandidateRoundTrips(self):
  #  transitional = TransitionalCandidateRoundTrips(robot=self)
  #  return transitional

  def getCompletionCandidatesRoundTrips(self):
  	completion = CompletionCandidateRoundtrips(robot=self)
  	return completion
  


  # ################# EVENT RECORDING FUNCTIONS ################################################
  #
  # Recording of various events in the system
  #
  def recordTradeData(self):
  	EquityTradingData.objects.create(symbol=self.getBullishSymbol(),trade_datetime=self.current_timestamp,volume=0,price=self.getCurrentBullPrice())
  	EquityTradingData.objects.create(symbol=self.getBearishSymbol(),trade_datetime=self.current_timestamp,volume=0,price=self.getCurrentBearPrice())
  	EquityTradingData.objects.create(symbol=self.getSymbol(),trade_datetime=self.current_timestamp,volume=0,price=self.getCurrentBullPrice())

  def recordDisconnectionTransaction(self):
    log_time = self.getCurrentTimestamp()
    action = 'Disconnect'
    object_type = 'Robot'
    object_id = self.pk 
    modified_by = None #TODO: FixME
    comment = 'Disconnecting for no reason '
    StartupStatus.recordTransaction(log_time=log_time,action=action,object_type=object_type,
    	                            object_id=object_id, modified_by=modified_by,comment=comment)
  	
  def recordConnectionTransaction(self):
    log_time = self.getCurrentTimestamp()
    action = 'Connect'
    object_type = 'Robot'
    object_id = self.pk 
    modified_by = None #TODO: FixME
    comment = 'Connect for no reason '
    StartupStatus.recordTransaction(log_time=log_time,action=action,object_type=object_type,
    	                            object_id=object_id, modified_by=modified_by,comment=comment)

  # 
  # On regular intervall, the Robot Portfolio needs to be synchronized with the
  # 
  def synchronizeBudgetWithBrokerage(self):
    if self.isAlpacaPaperAccount() and self.isAlpacaPortfolioAccount():
      brokerage = AlpacaPaperAccount()
    elif self.isAlpacaLiveAccount():
      brokerage = AlpacaPaperAccount()
    elif self.isLocalAccount() and self.isLocalPortfolioAccount():
      brokerage = LocalAccount()

    self.portfolio.synchronizeBudgetWithBrokerage()  	

  # ################# USER INTERFACE DATA FUNCTIONS / UI REPORTING DATA ########################
  #
  # Returns Data for the Forms ... to be displaed on the UI
  #
  def getCompletedReport(self):
    return self.getCompletedRoundTrips().getCompletedReport()

  def getInTransitionReport(self):
    return self.getInTransitionRoundTrips().getInTransitionReport()

  def getStableReport(self):
    return self.getStableRoundTrips().getStableReport()


  # ################# ENTRY POINT OF APPLICATION - DAILY MARKET DATA  ################################################
  #
  # This is the entry point from the various external sources to start trading for the Robot.
  # 
  def setCurrentValues(self,current_payload):
    try:
      self.current_bull_price = current_payload[self.getBullishSymbol()]
      self.current_bear_price = current_payload[self.getBearishSymbol()]
      self.current_timestamp  = strToDatetime(business_day=current_payload['timestamp'])
    except Exception as e:
      print("The matching Bull and/or Bear symbol are missing from the current values paylod. {0}.".format(e))
      return False    
    return True


  #
  #
  #
  def TwentyFourHourUpdate(self):
    #print("24 Hour update TimeStamp: {}".format(self.current_timestamp))
    #round((self.getCurrentTimestamp() - self.getBullBuyDate()).total_seconds()/60,2)
    
    if self.last_daily_update==None: 
      self.portfolio.synchronizeBudgetWithBrokerage()
      self.last_daily_update = self.current_timestamp
    elif round((self.last_daily_update - self.current_timestamp).total_seconds()/60,2) > (24 * 60):
      self.portfolio.synchronizeBudgetWithBrokerage()
      self.last_daily_update = self.current_timestamp  #

    bud_mgmt =   RobotBudgetManagement.objects.get(pk=self.pk) 
    bud_mgmt.setInitialDailyBudget(robot=self)

  #
  # This is the main entry point to start trading with a Robot.
  # All ETFRobotBackTestExecution() and ETFRobotLiveExecution() enter through this.
  #
  def prepareTrades(self,key=None):
    if not self.isEnabled():
      logger.error("Robot has not yet been enabled. Please enable {0} before starting the trade. Exiting...".format(self.name,key))
      return -1

    logger.info("\n\nRobot'{0}' Data:{1}' launched.".format(self.name,key))

    if key == None:
      logger.error("The key passed doesn't contain any values. Make sure there are values in the Key parameter. ")
      return -1

    if not self.setCurrentValues(current_payload=key):
      return -1

    #Record the actual Share Price into the Data Table.
    self.recordTradeData()

    #Udpdate Records based on Orders execution.
    self.updateOrders()

    #24 Hour Update: Things that need to be updated every 24 hours.
    self.TwentyFourHourUpdate()

    #Invoke Strategies and let them do the rest strategy_category
    if self.isBabadjouStrategy():
      babadjou = BabadjouStrategy(robot=self)
      babadjou.setupStrategy()
      babadjou.buy()
      babadjou.sell()
    elif self.isBatchamStrategy():
      print("HENRI: Batcham Strategy !!!")
      batcham = BatchamStrategy(robot=self)
      batcham.setupStrategy()
      batcham.buy()
      batcham.sell()
    elif self.isBalatchiStrategy():
      bamendjinda = BalatchiStrategy(robot=self)
      bamendjinda.setupStrategy()
      bamendjinda.buy()
      bamendjinda.sell()
    elif self.isBalatchiStrategy():
      bamendjinda = BalatchiStrategy(robot=self)
      bamendjinda.setupStrategy()
      bamendjinda.buy()
      bamendjinda.sell()
    else:
      print("Strategy doesn't have an implementation yet. {0}.".format(strategy))
      raise Exception(" You must provide a valid strategy. ")

    self.updatePortfolioValue()


  #
  # This is like the main function of the Robot.
  # It will create an Assembly Line. An Assembly line is just an interface into trading data
  # stored in the various trading systems.
  #
  async def AsyncPrepareTrades(self,key=None):
    logger.info("     Robot '{0}' Key = {1}' is trading now ...".format(self.name,key))
    if not self.enabled:
      logger.info("Robot has not yet been enabled. Please enable {} before starting the trade. Exiting...".format(self.name,key))
      return 
    
    self.current_bull_price = key[self.getBullishSymbol()]
    self.current_bear_price = key[self.getBearishSymbol()]
    self.current_timestamp = self.fixupMyDateTime(candidate=key['timestamp'])

    await self.initializeRobot()
    await asyncio.sleep(1)
    return

  #
  #
  #
  @sync_to_async
  def initializeRobot(self,timeframe=60):
    logger.info("initializing everything")
    if self.isAssemblyLineEmpty() or (not self.isFullyLoaded() and self.isReadyToBuyByTimeInterval()):
      self.buy()
    
    if self.getOnlyTradeAfterFullyLoaded() and (not self.isFullyLoaded()):
      return
    self.updatePortfolioValue()




########################################Roundtrip Report Functions. ##################
  #TODO: Make sure to understand this logic
  def isAssemblyLineEmpty(self):
  	return 0 == self.getNumberOfActives()

  def getAllBullishRoundtrips(self):
    ex_eng_id = None if self.execution_engine == None else self.execution_engine.id
    entries = TradeDataHolder.objects.filter(robot_id=self.pk).filter(execution_id=ex_eng_id).filter(buy_order_client_id__endswith='_buy_'+self.getBullishSymbol()).order_by('buy_date')
    return entries

  def getAllBearishRoundtrips(self):
    ex_eng_id = None if self.execution_engine == None else self.execution_engine.id
    entries = TradeDataHolder.objects.filter(robot_id=self.pk).filter(execution_id=ex_eng_id).filter(buy_order_client_id__endswith='_buy_'+self.getBearishSymbol()).order_by('buy_date')
    return entries

  def getTotalBothSidesEntries(self):
    ex_eng_id = None if self.execution_engine == None else self.execution_engine.id
    entries = TradeDataHolder.objects.filter(robot_id=self.pk).filter(execution_id=ex_eng_id).filter(buy_order_client_id__icontains='_buy_').order_by('buy_date')
    return entries

  #TODO: All Active Roundtrips for this Robot and this Execution Engine.
  def getAllActiveRoundtrips(self):
    ex_eng_id = None if self.execution_engine == None else self.execution_engine.id
    entries = TradeDataHolder.objects.filter(robot_id=self.pk).filter(execution_id=ex_eng_id).filter(buy_order_client_id__endswith='_buy_'+self.getBullishSymbol()).filter(sell_order_client_id__isnull=True).order_by('buy_date')
    return entries
  #
  def getTheBull(self,buy_order_client_id):
    return TradeDataHolder.objects.get(buy_order_client_id=buy_order_client_id)    

  def getTheBear(self,buy_order_client_id):
    return TradeDataHolder.objects.get(buy_order_client_id=buy_order_client_id)    

  def hasExactlyTwoEntries(self,root_id):
    return TradeDataHolder.objects.filter(buy_order_client_id__startswith=root_id).count()

  def recordDispositionTransaction(self,order,transition_root_id):
    TradeDataHolder.recordDispositionTransaction(robot=self,order=order,transition_root_id=transition_root_id)

#  def getAllBullishRoundtrips(self):
#    entries = TradeDataHolder.objects.filter(robot_id=self.pk).filter(execution_id=self.execution_engine.id).filter(buy_order_client_id__endswith='_buy_'+self.getBullishSymbol())
#    return entries 

#  def getAllBearishRoundtrips(self):
#    entries = TradeDataHolder.objects.filter(robot_id=self.pk).filter(execution_id=self.execution_engine.id).filter(buy_order_client_id__endswith='_buy_'+self.getBearishSymbol())
#    return entries

#  def getTotalBothSidesEntries(self):
#    entries = TradeDataHolder.objects.filter(robot_id=self.pk).filter(execution_id=self.execution_engine.id).filter(buy_order_client_id__icontains='_buy_')
#    return entries 
     
  #TODO: All Active Roundtrips for this Robot and this Execution Engine.   
#  def getAllActiveRoundtrips(self):
#    entries = TradeDataHolder.objects.filter(robot_id=self.pk).filter(execution_id=self.execution_engine.id).filter(buy_order_client_id__endswith='_buy_'+self.getBullishSymbol()).filter(sell_order_client_id__isnull=True)
#    return entries 

  #Returns all, include the ones that have completed. Only includes on side (bear or bulls, not both)
  def getAllSize(self):
  	return self.getAllBullishRoundtrips().count()

  #
  # All Roundtrips should be exactly half the total. As the number of bullish and number of bearish must 
  # be identical
  #
  def areAllRoundtripsBalanced(self):
  	balanced = False
  	all_bullish_roundtrips = self.getAllBullishRoundtrips().count()
  	all_bearish_roundtrips = self.getAllBearishRoundtrips().count()
  	all_roundtrips = self.getTotalBothSidesEntries().count()/2 
  	if (all_roundtrips == all_bearish_roundtrips) and (all_roundtrips == all_bullish_roundtrips):
  	  return True 
  	return False


  #TODO: Please fix me. Only returns active (Not yet Completed.)
  def getSize(self):
  	return self.getAllActiveRoundtrips().count()

  def isFullOfActiveEntries(self):
  	actives = self.getStableRoundTrips().getStableSize() + self.getInTransitionRoundTrips().getInTransitionSize()
  	return (actives >= self.max_roundtrips)

  def isFullyLoaded(self):
  	return (self.getNumberOfRoundtrips() >= self.getMaxNumberOfRoundtrips()) 

  def getNumberOfRoundtrips(self):
    if self.areAllRoundtripsBalanced():
      return self.getTotalBothSidesEntries().count()/2
    return -1

  # ################# REPORTING FUNCTIONS #################################################################
  # This is the financial Reporting for Command Line. There is a version that runs on the UI.
  #
  def getAllActiveCosts(self):
    result = dict()
    all_candidates = self.getStableRoundTrips().getAllStableEntries()
#self.getInTransitionRoundTrips().getAllInTransitionEntries() 

    cost_basis_list       = [ c.getRoundtripCostBasis(non_digits=False) for c in all_candidates]
    bull_cost_basis_list  = [ c.getBullCostBasis() for c in all_candidates]
    bear_cost_basis_list  = [ c.getBearCostBasis() for c in all_candidates]
    bull_current_value_list  = [ c.getBullCurrentValue() for c in all_candidates]
    bear_current_value_list  = [ c.getBearCurrentValue() for c in all_candidates]
    realized_list         = [ c.getRoundtripRealizedValue(non_digits=False) for c in all_candidates]
    unrealized_list       = [ c.getRoundtripUnrealizedValue(non_digits=False) for c in all_candidates]
    realized_profits_list = [ c.getRoundtripRealizedProfit(non_digits=False) for c in all_candidates]    

    result['cost_basis'] = sum(cost_basis_list)
    result['bull_cost_basis'] = sum(bull_cost_basis_list)
    result['bear_cost_basis'] = sum(bear_cost_basis_list)
    result['bull_current_value'] = sum(bull_current_value_list)
    result['bear_current_value'] = sum(bear_current_value_list)
    result['realized'] = sum(realized_list)
    result['unrealized'] = sum(unrealized_list)
    result['realized_profits'] = sum(realized_profits_list)

    return result

  def getAllCosts(self):
    result = dict()
    all_candidates = self.getStableRoundTrips().getAllStableEntries() + \
                     self.getCompletedRoundTrips().getAllCompletedEntries()

#self.getInTransitionRoundTrips().getAllInTransitionEntries() 
    cost_basis_list       = [ c.getRoundtripCostBasis(non_digits=False) for c in all_candidates]
    bull_cost_basis_list  = [ c.getBullCostBasis() for c in all_candidates] 
    bear_cost_basis_list  = [ c.getBearCostBasis() for c in all_candidates]
    realized_list         = [ c.getRoundtripRealizedValue(non_digits=False)  for c in all_candidates]
    unrealized_list       = [ c.getRoundtripUnrealizedValue(non_digits=False) for c in all_candidates]
    realized_profits_list = [ c.getRoundtripRealizedProfit(non_digits=False) for c in all_candidates]    

    result['cost_basis'] = sum(cost_basis_list)
    result['bull_cost_basis'] = sum(bull_cost_basis_list)
    result['bear_cost_basis'] = sum(bear_cost_basis_list)
    result['realized'] =  sum(realized_list)
    result['unrealized'] =  sum(unrealized_list)
    result['realized_profits'] =  sum(realized_profits_list)

    return result


  def getPerformance1(self):
    best_bulls = self.getStableRoundTrips().getMaxBearSpreadToAverageElligiblePrice()
    print("HENRI: {}".format(best_bulls))


  def updatePortfolioValue(self):
    #in_t_size = self.getInTransitionRoundTrips().getInTransitionSize()
    st_size = self.getStableRoundTrips().getStableSize()
    com_size = self.getCompletedRoundTrips().getCompletedSize()
    c_ts = self.current_timestamp
    bull_p = self.current_bull_price
    bear_p = self.current_bear_price
    print("\n\n-----------------Portfolio Summary Information at {0} ---Bull[{1:,.2f}]---Bear[{2:,.2f}]------------------------------".format(c_ts,bull_p,bear_p))
    print("InTransition={0}. Stable={1}. Active[Stable+Transition]={2}. Completed={3}. Total Entries={4}.".format( \
   		     0, st_size,st_size ,com_size,self.getAllSize()))
    
    results = self.getAllCosts()
    cb = round(results['cost_basis'],2)
    bull_cb = 0 if cb==0 else round(100 * results['bull_cost_basis']/results['cost_basis'],2)
    bear_cb = 0 if cb==0 else round(100 * results['bear_cost_basis']/results['cost_basis'],2)
    re = round(results['realized'],2)
    un = round(results['unrealized'],2)
    rp = round(results['realized_profits'],2)
    pv = round(re + un,2)
    profit = round(pv - cb ,2)
    realized_profit = round(rp,2)

    a_results = self.getAllActiveCosts()
    a_cb = round(a_results['cost_basis'],2)
    a_bull_cb = 0 if a_cb==0 else round(100 * a_results['bull_cost_basis']/a_results['cost_basis'],2)
    a_bear_cb = 0 if a_cb==0 else round(100 * a_results['bear_cost_basis']/a_results['cost_basis'],2)
    a_re = round(a_results['realized'],2)
    a_un = round(a_results['unrealized'],2)
    a_rp = round(a_results['realized_profits'],2)
    a_pv = round(a_re + a_un,2)
    a_profit = round(a_pv - a_cb ,2)
    a_realized_profit = round(a_rp,2)
    
    stable_candidates= self.getStableRoundTrips().getAllStableEntries()
    bull_prices = [c.getBullPrint2Data() for c in stable_candidates]
    bear_prices = [c.getBearPrint2Data() for c in stable_candidates]
    price_spread = [round(c.getBullBearCurrentValueSpread(),2) for c in stable_candidates]
    total_spread = round(sum(price_spread),2)

    #Minimum Bull Price, Maximum Bull Price, Total Bull Quantity, Average Bull Price, Total Cost Basis Bull, Total Current Value
    #Minimum Bear Price, Maximum Bear Price, Total Bear Quantity, Average Bear Price, Total Cost Basis Bear, Total Current Value
    
    print("Total :C. Basis={0:,.2f}[Bull/Bear(%)={6:,.2f}/{7:,.2f}]. Profit={5:,.2f} Realized={1:,.2f}. Unrealized={2:,.2f}. Port. Value={3:,.2f}. Net win/loss={4:,.2f}.".format(cb,re,un,pv,profit,realized_profit,bull_cb,bear_cb))
    print("Active:C. Basis={0:,.2f}[Bull/Bear(%)={6:,.2f}/{7:,.2f}]. Profit={5:,.2f} Realized={1:,.2f}. Unrealized={2:,.2f}. Port. Value={3:,.2f}. Net win/loss={4:,.2f}.".format(a_cb,a_re,a_un,a_pv,a_profit,a_realized_profit,a_bull_cb,a_bear_cb))
    print("Bulls       : {} ".format(bull_prices))
    print("Bears       : {} ".format(bear_prices))
    print("Price Spread: {} . Total = {}".format(price_spread,total_spread))
    
    #self.getPerformance1()
    print("                              ---------------------------------------                      ")

  # ################# BROKERAGE FUNCTIONS #################################################################
  # These are function that interact with the Brokerage.
  # 0. The first set of functions determines the type of Brokerage (etrade, alpaca, ameritrade, Local) 
  #    and the type of data feed (live, paper, local). Not all combinations are valid combinations.
  #    Here are the only valid combinations: (eTrade, Alpaca, Ameritrade) + (live, paper), (local) + (local)
  # 1. Buy Orders: Simulteneous 
  # 2. Sell Orders: Sell one side (Transition Sale Order)
  #
  def isLocalBacktestAccount(self):
  	return self.portfolio.isLocal() and self.isDataSourceLocal()

  def isAlpacaLiveAccount(self):
  	return self.portfolio.isAlpaca() and self.isDataSourceLiveFeed()

  def isAlpacaPaperAccount(self):
  	return self.portfolio.isAlpaca() and self.isDataSourcePaperAccount()

  def isEtradeRegularPaperAccount(self):
  	return self.portfolio.isETradeRegular() and self.isDataSourcePaperAccount()

  def isEtradeRetirementPaperAccount(self):
  	return self.portfolio.isETradeRetirement() and self.isDataSourcePaperAccount()

  def updateRobotCashPosition(self,cost_basis=0):
    logger.info("Updating Cash Position.")

  def updateOrders(self):
    logger.info("TODO: Brokerage Function. Updating orders from the Brokerage ... ")
    logger.info("TODO: self.updateRobotCashPosition(): Make sure to run this following the update of the Database. ")
    return True
    if self.isAlpacaPaperAccount() and self.isAlpacaPortfolioAccount():
      brokerage = AlpacaPaperAccount()
      closed_orders = brokerage.getClosedOrders()
    elif self.isAlpacaLiveAccount():
      print(" hello")

    time.sleep(int(self.getRobotSleepTimeBetweenChecks()))
    return True

  def moveToCompletion(self,candidate):
    if shouldUsePrint():
      print("Moving to Completion (Sell the unrealized). ")
    if candidate.isInTransition():
      candidate.sellTheUnrealized()

  def moveToBearishTransition(self,candidate):
  	candidate.sellTheBull()

  def moveToBullishTransition(self,candidate):
  	candidate.sellTheBear()

  def moveBullAndBearToCompletion(self,candidate):
    candidate.sellTheBull()
    candidate.sellTheBear()

  #
  # A new Roundtrip entry will be created and added to the Assembly line.
  # TODO: This is where we place an Order with the Brokerage
  #
  def addNewRoundtripEntry(self,business_day=None):
    current_time = self.getCurrentTimestamp() if (business_day==None) else timezoneAwareDate(business_day=business_day)
    bullish = dict()
    bearish = dict()
    bullish['symbol'] = self.getBullishSymbol()
    bearish['symbol'] = self.getBearishSymbol()
    bullish['price'] = self.getCurrentBullPrice()
    bearish['price'] = self.getCurrentBearPrice() 
    order_ids = TradeDataHolder.generateBuyOrderClientIDs(r_id=self.pk,bear_symbol=self.getBearishSymbol(),bull_symbol=self.getBullishSymbol(),project_root=self.getInternalName())
    bullish['bull_buy_order_client_id']= order_ids['bull_buy_order_client_id']
    bearish['bear_buy_order_client_id']= order_ids['bear_buy_order_client_id']
    asset_composition = self.getAssetComposition()
    bears_ratio = asset_composition['bear'] * .01
    bulls_ratio = asset_composition['bull'] * .01
    if shouldUsePrint():
      print("Composition: {0} {1} {2}".format(bears_ratio,bulls_ratio,self.getCostBasisPerRoundtrip()))
    bullish['qty']= round((self.getCostBasisPerRoundtrip() * bulls_ratio)/bullish['price'])
    bearish['qty']= round((self.getCostBasisPerRoundtrip() * bears_ratio)/bearish['price'])
    bullish['date'] = current_time
    bearish['date'] = current_time
    logger.info("Cost Basis: {}".format(self.getCostBasisPerRoundtrip()))
    logger.info("Order has been sent to the Brokerage. Record Transaction ... \nBullish={}\nBearish={}\n".format(bullish,bearish))
    TradeDataHolder.recordAcquisitionTransaction(robot=self,bullish=bullish,bearish=bearish)
    
    return order_ids

######################## ###################################
#
# Transactions: Must stay here because I need both the symbol and the robot_id
# This section, we retrieve all the transaction related data
#
  def getRobotExecutionParams(self):
    return 'exect_params'

  def getBullishFilter(self):
    ex_eng_id = None if self.execution_engine == None else self.execution_engine.id
    return TradeDataHolder.objects.filter(robot_id=self.pk).filter(execution_id=ex_eng_id).filter(symbol=self.getBullishSymbol())

  def getBearishFilter(self):
    ex_eng_id = None if self.execution_engine == None else self.execution_engine.id
    return TradeDataHolder.objects.filter(robot_id=self.pk).filter(execution_id=ex_eng_id).filter(symbol=self.getBearishSymbol())

  def getAllBullishPurchaseTransactions(self):
   return self.getBullishFilter().count()

  def getAllBearishPurchaseTransactions(self):
    return self.getBearishFilter().count()

  def getAllPurchaseTransactions(self):
    return self.getAllBullishPurchaseTransactions() + self.getAllBearishPurchaseTransactions()

  def getAllBullishSaleTransactions(self):
    return self.getBullishFilter().filter(sell_order_client_id__isnull=False).count()

  def getAllBearishSaleTransactions(self):
    return self.getBearishFilter().filter(sell_order_client_id__isnull=False).count()

  def getAllSaleTransactions(self):
    return self.getAllBullishSaleTransactions() + self.getAllBearishSaleTransactions()

  def getAllTransactions(self):     
    return self.getAllPurchaseTransactions() + self.getAllSaleTransactions()

  def getAllBullishUnrealizedTransactions(self):
    return self.getBullishFilter().filter(sell_order_client_id__isnull=True).count()

  def getAllBearishUnrealizedTransactions(self):
    return self.getBearishFilter().filter(sell_order_client_id__isnull=True).count()

  def getAllUnRealizedTransactions(self):
    return self.getAllBullishUnrealizedTransactions() + self.getAllBullishUnrealizedTransactions()

###################################################
#
# Winners Strategy ...
  def getBabadjouCompletionCandidates(self):                                                                         
    ex_eng_id = None if self.execution_engine == None else self.execution_engine.id
    entries = TradeDataHolder.objects.filter(robot_id=self.pk).filter(execution_id=ex_eng_id).filter(symbol=self.getBullishSymbol()).filter(winning_order_client_id__isnull=False).distinct()
    return entries

  def generateInTransitionRootOrderClientID(self,bulls_count,bears_count,project_root,r_id):
    transition_root_id = TradeDataHolder.generateInTransitionRootOrderClientID(bulls_count=bulls_count,bears_count=bears_count,project_root=project_root,r_id=r_id)
    return transition_root_id    
    #transition_root_id = TradeDataHolder.generateInTransitionRootOrderClientID(bulls_count=bulls_size,bears_count=bears_size,project_root=p_root,r_id=r_id)

###################################################
#
# Shares Quantity (How many shares, ...) ...
  def getAllBearishSharesAcquired(self):    
    number = self.getBearishFilter().filter(buy_order_client_id__isnull=False).aggregate(total_shares=Sum('quantity'))
    return 0 if number['total_shares'] == None else number['total_shares']

  def getAllBullishSharesAcquired(self):
    number = self.getBullishFilter().filter(buy_order_client_id__isnull=False).aggregate(total_shares=Sum('quantity'))
    return 0 if number['total_shares'] == None else number['total_shares']

  def getAllSharesAcquired(self):
    return self.getAllBearishSharesAcquired() + self.getAllBullishSharesAcquired()

  def getAllBearishSharesSold(self):
    number = self.getBearishFilter().filter(sell_order_client_id__isnull=False).aggregate(total_shares=Sum('quantity'))
    return 0 if number['total_shares'] == None else number['total_shares']

  def getAllBullishSharesSold(self):
    number = self.getBullishFilter().filter(sell_order_client_id__isnull=False).aggregate(total_shares=Sum('quantity'))
    return 0 if number['total_shares'] == None else number['total_shares']

  def getAllSharesSold(self):
    return self.getAllBullishSharesSold() + self.getAllBearishSharesSold()

  def getAllBearishSharesUnrealized(self):
    number = self.getBearishFilter().filter(sell_order_client_id__isnull=True).aggregate(total_shares=Sum('quantity'))
    return 0 if number['total_shares'] == None else number['total_shares']

  def getAllBullishSharesUnrealized(self):
    number = self.getBullishFilter().filter(sell_order_client_id__isnull=True).aggregate(total_shares=Sum('quantity'))
    return 0 if number['total_shares'] == None else number['total_shares']

  def getAllSharesUnrealized(self):    
    return self.getAllBearishSharesUnrealized() + self.getAllBullishSharesUnrealized()

######################################################
#
# Financial Value
# Shares Quantity (How many shares, ...) ...
  def getCostOfAllBearishSharesAcquired(self):
    number = self.getBearishFilter().filter(buy_order_client_id__isnull=False).aggregate(total_costs=Sum(F('buy_price') * F('quantity'), output_field=FloatField()))
    return 0 if number['total_costs'] == None else number['total_costs']

  def getCostOfAllBullishSharesAcquired(self):
    number = self.getBullishFilter().filter(buy_order_client_id__isnull=False).aggregate(total_costs=Sum(F('buy_price') * F('quantity'), output_field=FloatField()))
    return 0 if number['total_costs'] == None else number['total_costs']

  def getCostOfAllSharesAcquired(self):    
    return self.getCostOfAllBullishSharesAcquired() + self.getCostOfAllBearishSharesAcquired()

  def getProfitOfAllBearishSharesSold(self):
  	#TODO: Please add filder .filter(robot_id=self.pk).filter(execution_id=self.execution_engine.id)
    entries = TradeDataHolder.objects.filter().filter(robot_id=self.pk).count()
    return entries

  def getProfitOfAllBullishSharesSold(self):
    entries = TradeDataHolder.objects.filter().filter(robot_id=self.pk).count()
    return entries

  def getProfitOfAllSharesSold(self):
    entries = TradeDataHolder.objects.filter().filter(robot_id=self.pk).count()
    return entries

  def getCostOfAllBearishSharesUnrealized(self, bear_price_per_share):
    number = self.getBearishFilter().filter(buy_order_client_id__isnull=False).aggregate(total_costs=Sum(bear_price_per_share * F('quantity'), output_field=FloatField()))
    return 0 if number['total_costs'] == None else number['total_costs']

  def getCostOfAllBullishSharesUnrealized(self, bull_price_per_share):
    number = self.getBullishFilter().filter(buy_order_client_id__isnull=False).aggregate(total_costs=Sum(bull_price_per_share * F('quantity'), output_field=FloatField()))
    return 0 if number['total_costs'] == None else number['total_costs']

  def getCostOfAllSharesUnrealized(self,bear_price_per_share,bull_price_per_share):
    return self.getCostOfAllBullishSharesUnrealized(bull_price_per_share=bull_price_per_share) + self.getCostOfAllBearishSharesUnrealized(bear_price_per_share=bear_price_per_share)

  def getEntryBasedOnOrderClientID(self,exec_engine_order_client_id):
    entry = TradeDataHolder.getEntryBasedOnOrderClientID(exec_engine_order_client_id=exec_engine_order_client_id)
    return entry 

  #
  # Serializing the Robot Instance. 
  # TODO: Implement it to call other classes serializers
  # 
  def getSerializedRobotObject(self):
    entry = [self]
    data_robot = serialize('json', entry, cls=ETFPairsRobotEncoder)

    activity_window = RobotActivityWindow.objects.get(pk=self.pk)
    activity_data = '' if activity_window==None else serialize('json', [activity_window], cls=ETFPairsRobotEncoder)
  
    sentiment_window = EquityAndMarketSentiment.objects.get(pk=self.pk)
    sentiment_data = '' if sentiment_window==None else serialize('json', [sentiment_window], cls=ETFPairsRobotEncoder)

    budget_window = RobotBudgetManagement.objects.get(pk=self.pk)
    budget_data = '' if budget_window==None else serialize('json', [budget_window], cls=ETFPairsRobotEncoder)

    data_strategy = '' if self.strategy==None else serialize('json', [self.strategy], cls=ETFPairsRobotEncoder)
    data_symbols = '' if self.symbols==None else serialize('json', [self.symbols], cls=ETFPairsRobotEncoder)
    data_portfolio = '' if self.portfolio==None else serialize('json', [self.portfolio], cls=ETFPairsRobotEncoder)
    data = data_robot + data_strategy + data_symbols + data_portfolio + activity_data + sentiment_data
    #print("Serialized: {}".format())
    return data

  def deserializedRobotObject(self):
    entry = [self]
    data_robot = serialize('json', entry, cls=ETFPairsRobotEncoder)
    data_strategy = serialize('json', [self.strategy], cls=ETFPairsRobotEncoder)
    data = data_robot + data_strategy
    return data

##############################################################################
#
# TradeDataHolder is the Infrastructure that contains all the transactions.
# It is organized in such a way that it allows for us to easily
# keep tract of acquisition and sell transactions.
# buy_order_client_id and sell_order_client_id are very important
#
class TradeDataHolder(models.Model):
  symbol =   models.CharField(max_length=10,default='')
  quantity = models.IntegerField(blank=True,null=True)
  buy_date = models.DateTimeField(timezone.now,default=timezone.now) 
  buy_price = models.FloatField(default=0.0)
  buy_order_client_id =   models.CharField(max_length=100,default='')
  sell_order_client_id =   models.CharField(max_length=100,blank=True,null=True)
  sell_price = models.FloatField(blank=True,null=True)
  sell_date = models.DateTimeField(timezone.now,blank=True,null=True)
  winning_order_client_id = models.CharField(max_length=100,blank=True,null=True)
  robot = models.ForeignKey(ETFAndReversePairRobot,on_delete=models.PROTECT,blank=True,null=True)
  execution =   models.ForeignKey('ETFPairRobotExecution',on_delete=models.PROTECT,blank=True,null=True)
  
  def __str__(self):
    return "{0} {1} {2} {3} {4} {5} {6}".format(self.symbol,self.quantity,self.buy_price,datetime.strftime(self.buy_date,"%y/%m/%d"),self.sell_price,self.buy_order_client_id,self.sell_order_client_id)

  def getBasicBuyInformation(self):
    return "[S={0}. Q={1}. P={2}]".format(self.symbol,self.quantity,self.buy_price)

  def getAdvancedBuyInformation(self):
    date_time=datetime.strftime(self.buy_date,"%y/%m/%d")
    root_id = self.getOrderClientIDRoot()
    return "[S={0}. Q={1}. P={2}. D={3} R={4}]".format(self.symbol,self.quantity,self.buy_price,date_time,root_id)

  #############################################################################
  # Data Sanity. We want to make sure we are
  # only working with good Data from the beginning.
  #
  def isValidAfterBuy(self):
    return self.isValid()

  def isValidAfterSale(self):
  	return self.isValid(after_sale=True)

  ############################################################################
  # This function checks the data integrity of our system.
  # By default, we check this after a Buy Operation (after_sale=False)
  # After a sale, we also want to make sure the data remain as expected.
  # Only check after a Buy Operation
  # Should the cost_basis be considered? Could play a role in the future.
  def isValid(self,after_sale=False):
    if not self.symbol or (not self.buy_price)\
      or (not self.buy_date) or (not self.buy_order_client_id):
      return False

    if (self.buy_price <= 0) or (self.quantity <= 0) or (self.symbol == ''):
      return False

    #Fields expected to be NULL should also be null. Only true after acquisition. After sale, this is no longer valid
    if after_sale == False:
      if (not self.sell_price is None) or (not self.sell_date is None) or (not self.sell_order_client_id is None):
        return False
    else:
      if (self.sell_price <=0) or (self.sell_date == None) or (self.sell_order_client_id is None):
      	logger.error("Either the sale price, the sell date or the sell client ID are wrong. ")
      	return False

    #Guarantee the buy_order_client_id ends with '_buy_symbol'. Only true for AfterBuy status for buy_order_client_id
    ending = '_buy_'+self.symbol
    if not self.buy_order_client_id.endswith(ending):
      return False

    #Ensure that the sell_client_order_id was set properly
    if after_sale == True:
      ending_sell = '_sell_'+self.symbol
      if not self.sell_order_client_id.endswith(ending_sell):
      	logger.error("Issue with Order_Client_ID")
      	return False
    return True

  ##################################################################################
  ### Place the Order here. buy_order should have all the pieces needed.
  ###
  @staticmethod
  def recordDispositionTransaction(robot,order,transition_root_id=None):
    sell_order = order
    entry = TradeDataHolder.objects.get(buy_order_client_id=sell_order['buy_order_client_id'])

    if entry == None:
      raise InvalidTradeDataHolderException("Unable to locate entry based on order_client_id {0}.".format(sell_order['buy_order_client_id']))

    entry.sell_price = sell_order['sell_price'] 
    entry.sell_order_client_id = sell_order['sell_order_client_id']
    entry.sell_date = sell_order['sell_date']
    if not (transition_root_id==None):
      entry.winning_order_client_id = transition_root_id
    entry.save()

    #Account for None cases
    execution_engine = None if robot==None else robot.execution_engine
    execution_params = None if robot==None else robot.getRobotExecutionParams()

    #Record a Disposition Purchase transaction with the Execution Engine:
    ETFPairRobotExecutionData.recordDispositionExecution(executor=execution_engine,exec_time=sell_order['sell_date'],
    	                           order_client_id=sell_order['sell_order_client_id'],exec_params=execution_params,income=0)

    return entry


  ##################################################################################
  ### Place the Order here. buy_order should have all the pieces needed.
  ###
  @staticmethod
  def recordAcquisitionTransaction(robot,bullish,bearish):
    if bullish['symbol'] == '' or bearish['symbol'] == '':
  	  raise InvalidTradeDataHolderException("Invalid Bullish {0} or Bearish {1} symbol.".format(bullish['symbol'],bearish['symbol']))
    if bullish['price'] <= 0 or bearish['price'] <= 0:
  	  raise InvalidTradeDataHolderException("Invalid Bullish {0} or Bearish {1} price.".format(bullish['price'],bearish['price']))
    if bullish['qty'] <= 0 or bearish['qty'] <= 0:
  	  raise InvalidTradeDataHolderException("Invalid Bullish {0} or Bearish {1} Quantity".format(bullish['qty'],bearish['qty']))
    if not (bullish['bull_buy_order_client_id'].replace('_buy_','').replace(bullish['symbol'],'') == \
  		    bearish['bear_buy_order_client_id'].replace('_buy_','').replace(bearish['symbol'],'')):
  	  raise InvalidTradeDataHolderException("Invalid Order Client ID for Bull {0} and Bear {0}. ".format(bullish['bull_buy_order_client_id'],bearish['bear_buy_order_client_id']))


    #Account for None cases
    execution_engine = None if robot==None else robot.execution_engine
    execution_params = None if robot==None else robot.getRobotExecutionParams()

    bull_entry=TradeDataHolder.objects.create(robot=robot, symbol=bullish['symbol'], buy_price=bullish['price'],
                             buy_order_client_id=bullish['bull_buy_order_client_id'],buy_date=bullish['date'],
                             quantity=bullish['qty'],execution=execution_engine )

    bear_entry=TradeDataHolder.objects.create(robot=robot, symbol=bearish['symbol'], buy_price=bearish['price'],
                             buy_order_client_id=bearish['bear_buy_order_client_id'],buy_date=bearish['date'],
                             quantity=bearish['qty'],execution=execution_engine)

    #Record the Bull Purchase transaction with the Execution Engine:
    ETFPairRobotExecutionData.recordAcquisitionExecution(executor=execution_engine,exec_time=bullish['date'],
    	                           order_client_id=bullish['bull_buy_order_client_id'],exec_params=execution_params,cost=0)

    #Record the Bear Purchase transaction with the Execution Engine:
    ETFPairRobotExecutionData.recordAcquisitionExecution(executor=execution_engine,exec_time=bearish['date'],
    	                           order_client_id=bearish['bear_buy_order_client_id'],exec_params=execution_params,cost=0)

    robot_id = None if robot==None else robot.id
    exec_engine_id = None if (execution_engine==None) or (robot.execution_engine==None) else robot.execution_engine.id

    #Delete me below
    #robot_id = robot.id
    #exec_engine_id = robot.execution_engine.id
    bull_info =bull_entry.getBasicBuyInformation()
    bear_info = bear_entry.getBasicBuyInformation()
    if shouldUsePrint():
      print("\nNew Entry added: Bull={0}. Bear={1}. Robot={2} Exec_Engine={3} ".format(bull_info,bear_info,robot_id,exec_engine_id,))


  @staticmethod
  def deleteExecutionEngineEntries(robot):
  	TradeDataHolder.objects.filter(robot=robot).filter(execution=robot.execution_engine).delete()

  @staticmethod
  def generateInTransitionRootOrderClientID(project_root,bulls_count,bears_count,r_id=None):
    project_root = project_root
    current_time = datetime.now(getTimeZoneInfo())
    root_order_client_id = current_time.strftime("{0}_{1}_{2}_{3}_%Y%m%d-%H-%M-%S.%f".format(project_root,r_id,bulls_count,bears_count))
    return root_order_client_id

  @staticmethod
  def generateRootOrderClientId(project_root,r_id=None):
    project_root = project_root
    current_time = datetime.now(getTimeZoneInfo())
    root_order_client_id = current_time.strftime("{0}_{1}_%Y%m%d-%H-%M-%S.%f".format(project_root,r_id))
    return root_order_client_id

  @staticmethod
  def generateBuyOrderClientIDs(project_root,bull_symbol,bear_symbol,r_id=None):
    root_order_client_id = TradeDataHolder.generateRootOrderClientId(project_root=project_root,r_id=r_id)   
    order_ids = dict()
    order_ids['bull_buy_order_client_id'] = root_order_client_id + "_buy_" + bull_symbol 
    order_ids['bear_buy_order_client_id'] = root_order_client_id + "_buy_" + bear_symbol 
    return order_ids

  @staticmethod
  def generateSellOrderClientIDs(project_root,bull_symbol,bear_symbol,r_id=None):
    root_order_client_id = TradeDataHolder.generateRootOrderClientId(project_root=project_root,r_id=r_id)   
    order_ids = dict()
    order_ids['bull_sell_order_client_id'] = root_order_client_id + "_sell_" + bull_symbol 
    order_ids['bear_sell_order_client_id'] = root_order_client_id + "_sell_" + bear_symbol 
    return order_ids

  @staticmethod
  def getEntryBasedOnOrderClientID(exec_engine_order_client_id):
    data = dict()
    if '_buy_' in exec_engine_order_client_id:
      entry = TradeDataHolder.objects.get(buy_order_client_id=exec_engine_order_client_id)
      data['action']='buy'
      data['quantity']=entry.quantity
      data['symbol']= entry.symbol
      data['price'] = entry.buy_price
      data['cost']= round(entry.getCostBasis() * (-1),2)
      data['buy_date']=entry.buy_date.isoformat().replace('T','')
    elif '_sell_' in exec_engine_order_client_id:
      entry = TradeDataHolder.objects.get(sell_order_client_id=exec_engine_order_client_id)
      data['action']='sell'
      data['quantity']=entry.quantity
      data['symbol']= entry.symbol
      data['price'] = entry.sell_price
      data['cost']=round(entry.getRealizedValue(),2)
      data['buy_date']=entry.sell_date.isoformat().replace('T','') 
    return data

  def getSellClientOrderID(self):
    return self.getOrderClientIDRoot() + "_sell_" + self.symbol

  def getBuyClientOrderID(self):
    return self.getOrderClientIDRoot() + "_buy_" + self.symbol

  def getOrderClientIDRoot(self):
    order_client_id_root = self.buy_order_client_id.replace('_buy_','').replace(self.symbol,'')
    return order_client_id_root

  def getWinningOrderClientIDRoot(self):
    return self.winning_order_client_id

  #TODO: please review IsValid()
  def isUnRealized(self):
    return ((self.sell_price is None) and (self.sell_date is None) and (self.sell_order_client_id is None))

  #TODO: please review IsValid()
  def isRealized(self):
    return  (not ( self.sell_price is None) and (not (self.sell_date is None)) and (not (self.sell_order_client_id is None)) )

  def hasPeerEntry(self):
    r_c_id = self.getOrderClientIDRoot()
    count = TradeDataHolder.objects.filter(buy_order_client_id__startswith=r_c_id).exclude(buy_order_client_id=self.buy_order_client_id).count()
    return (count == 1) 

  def getCostBasis(self):
  	return self.buy_price * self.quantity
  
  def getCurrentValue(self, current_price):
  	return self.quantity * current_price

  def getCurrentProfit(self, current_price):
   return self.getCurrentValue(current_price=current_price) - self.getCostBasis()
 
  def getUnRealizedValue(self,current_price):
    if self.isUnRealized():
      return (current_price ) *self.quantity
    return 0

  def getRealizedValue(self):
    if self.isUnRealized():
      return 0
    return self.quantity * self.sell_price
 
#
# This serializer is used to serialize entries for the Robot.
#   Customer
class ETFPairsRobotEncoder(DjangoJSONEncoder):
  def default(self, obj):
    if isinstance(obj, ETFAndReversePairRobot) or isinstance(obj,Portfolio):
      return str(obj)
    elif isinstance(obj, EquityStrategy) or isinstance(obj,RobotEquitySymbols):
      return str(obj)
    elif isinstance(obj,RobotActivityWindow) or isinstance(obj,EquityAndMarketSentiment):
      return str(obj)
    elif isinstance(obj,RobotBudgetManagement):
      return str(obj)
    return super().default(obj)


