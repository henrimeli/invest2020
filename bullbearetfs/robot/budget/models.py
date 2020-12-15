from django.db import models
import logging

"""
  TODO: Describe the Module here ...

  List the classes of the module here
"""

logger = logging.getLogger(__name__)


CHOICES_ROBOT_FRACTIONS = ((0.10,'10%'),(0.20,'20%'),(0.25,'25%'),(0.30,'30%'))
CHOICES_CASH_POSITION_UPDATE_POLICY = ((24,'1 day'),(1,'hourly'),(0,'immediate'),(48,'2 days'),(72,'3 days'))
CHOICES_USE_CASH_OR_NUMBER= (('Number','Number'),('Percent','Percent'))
CHOICES_TAX_RATE = (('0','0'),('5','5'))
CHOICES_COMMISSION_PER_TRADE = (('0','0'),('1','1'),('5','5'))
CHOICES_OTHER_COSTS = (('0','0'),('5','5'))
CHOICES_MAX_BUDGET_PER_ACQUISITION_PERCENT = (('10','10'),('15','15'),('20','20'),('25','25'),('30','30'))
CHOICES_MAX_BUDGET_PER_ACQUISITION_NUMBER = (('500','500'),('250','250'),('1000','1000'),('1500','1500'),('2000','2000'),('2500','2500'))



# ######################## Portfolio Information ##################
#  
# This is the Portfolio related Information: 
# It captures information about the portfolio at the brokerage.
# How much cash is available, and various portolio policies such
# as margin trading requirements, ... 
# Choices are expressed in percentage
# max_robot_fraction specifies how much a robot can invest in total.
# NOTE: Do not confuse with BudgetManagement From each Robot
class Portfolio(models.Model):
  """
    TODO: The portfolio class represents the Portfolio at the Brokerage weighted based on Robot settings.
  """
  name = models.CharField(max_length=50,default='')
  description = models.CharField(max_length=150,default='')
  owner = models.ForeignKey('Customer', on_delete=models.PROTECT,blank=True,null=True)
  brokerage = models.ForeignKey('BrokerageInformation',on_delete=models.PROTECT,blank=True,null=True)
  initial_cash_funds = models.FloatField(default=0) #Updated every 24 hours
  current_cash_funds = models.FloatField(default=0)
  max_robot_fraction = models.CharField(max_length=25, choices = CHOICES_ROBOT_FRACTIONS,default='10')
  cash_position_update_policy = models.CharField(max_length=15,choices=CHOICES_CASH_POSITION_UPDATE_POLICY,default='daily')

  def __str__(self):
    return "Portfolio - {}.".format(self.name)

  #
  # Alpaca has a function to see if your portfolio has issues.
  # Always run this call to make sure your expections are correct.
  # TODO: For Alpaca ...
  def isValid(self):
    return True 

  # This is the Robot Portfolio Cash position * Fraction for each robot
  def getInitialRobotBudget(self):
    return self.initial_cash_funds 

  def getCurrentRobotCashPosition(self):
    return self.current_cash_position

  #100 000 is the value that comes from the Brokerage
  # I have 100k * ration_per_robot as initial cash per day
  # This is where I calculate everything based on the ratio per robot
  def synchronizeBudgetWithBrokerage(self):
    self.initial_cash_funds = float(self.max_robot_fraction) * 100000
    self.current_cash_funds = self.initial_cash_funds
    self.save()

  def isAlpaca(self):
    return self.brokerage.isAlpaca()

  def isETradeRegular(self):
    return self.brokerage.isETradeRegular()

  def isETradeRetirement(self):
    return self.brokerage.isETradeRetirement()

  def isAmeritrade(self):
    return self.brokerage.isAmeritrade()

  def isLocal(self):
    return self.brokerage.isLocal()

  #def getAvailableCashFollowingSale(self,duration=0, amount=0):
  #  R_CHOICES_CASH_POSITION_UPDATE_POLICY = getReversedTuple(tuple_data=CHOICES_CASH_POSITION_UPDATE_POLICY)
  #  cash_update_policy = R_CHOICES_CASH_POSITION_UPDATE_POLICY[self.cash_position_update_policy]
  #  if self.cash_position_update_policy == 'immediate':
  #    return amount
  #  elif self.cash_position_update_policy == 'daily' and ( duration > 24*60):
  #    return amount
  #  elif self.cash_position_update_policy == '3 days' and ( duration > 3*24*60):
  #    return amount 
  #  return 0  
  #
  

# Managing the money used to acquire shares
# The goal here is to determine where the Robot should get funds for trading.
# Robot gets assigned initial funds from Portfolio.
# If Robot generates money, Robot should be able to use have more money to trade with
# If Robot loses money, Robot should have less money to trade, unless portfolio gives him money
# Portfolio management is shared between Robot and Portfolio management.
# Robot's share is always a percentage of Portfolio, up to a certain extend. 
class RobotBudgetManagement(models.Model):
  """
    TODO: This class is used to manage budget used to acquire assets
    This class provides functionality, so that it can respond appropriately if there is enough fund to acquire
    asset at any moment.
  """
  #Initial Value. Should be updated every day. Value should come from the Portfolio via the Robot.
  #Remove them from the Model and keep them as class variables only
  portfolio_initial_budget = models.FloatField(default=0.0, blank=True, null=True)

  # Usage per Acquisition 
  use_percentage_or_fixed_value = models.CharField(max_length=15,choices=CHOICES_USE_CASH_OR_NUMBER,default='Number')

  # Current Cash Position
  current_cash_position = models.FloatField(default=0.0)
  cash_position_update_policy = models.CharField(max_length=15,choices=CHOICES_CASH_POSITION_UPDATE_POLICY,default='daily')

  add_taxes = models.BooleanField(default=False)
  add_commission = models.BooleanField(default=False)
  add_other_costs = models.BooleanField(default=False)

  taxes_rate = models.CharField(max_length=5,choices=CHOICES_TAX_RATE,default='0')
  commission_per_trade = models.CharField(max_length=5,choices=CHOICES_COMMISSION_PER_TRADE,default='0')
  other_costs = models.CharField(max_length=5,choices=CHOICES_OTHER_COSTS,default='0')

  #Budget per equity acquisition
  max_budget_per_purchase_percent = models.CharField(max_length=15,choices=CHOICES_MAX_BUDGET_PER_ACQUISITION_PERCENT, default='15')
  max_budget_per_purchase_number = models.CharField(max_length=15,choices=CHOICES_MAX_BUDGET_PER_ACQUISITION_NUMBER, default='2000')

  pair_robot = models.ForeignKey('ETFAndReversePairRobot',on_delete=models.PROTECT, blank=True,null=True)


  def __str__(self):
    return "Budget Management - {0}.".format(self.id)

  # Is called Once per day from the main robot to provide budget updates from the Portfolio
  # Is called after the Synchronization with the Brokerage Portfolio has already been run
  # This will only replicate the data from the Portfolio here once per day. All daily transactions
  # will be updated from this interface.
  def setInitialDailyBudget(self,robot):
    self.portfolio_initial_budget = robot.portfolio.getInitialRobotBudget()
    self.current_cash_position = self.portfolio_initial_budget
    self.save()

  def updateBudgetAfterAcquisition(self,amount):
    self.current_cash_position = self.current_cash_position - amount
    self.save()
    return self.current_cash_position

  def updateBudgetAfterDisposition(self,amount):
    self.current_cash_position = self.current_cash_position + amount
    self.save()
    return self.current_cash_position

  def haveEnoughFundsToPurchase(self):
    #print("HENRI: Has enough funds? current_cash={}  getCostBasisPerRoundtrip={}".format(self.current_cash_position,self.getCostBasisPerRoundtrip()))
    return self.current_cash_position >= self.getCostBasisPerRoundtrip() 

  def getCostBasisPerRoundtrip(self):
    if self.use_percentage_or_fixed_value == 'Number':
      return float(self.max_budget_per_purchase_number)
    else:
      return float(self.max_budget_per_purchase_percent) * self.current_cash_position *.01

  def getAvailableTotalCash(self):
    return self.current_cash_position

  

