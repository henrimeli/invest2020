import datetime, time, pytz, logging, unittest , sys,json
import pandas as pd
from django.utils import timezone
from django.test import TestCase
import dateutil.parser, xmlrunner 
from bullbearetfs.robot.models import ETFAndReversePairRobot
from bullbearetfs.robot.budget.models import  RobotBudgetManagement, Portfolio
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, strToDatetime, shouldUsePrint, displayOutput,displayError

logger = logging.getLogger(__name__)


def test_budget_dummy(request):
  logger.info(" This is just a dummy function ")

#############################################################################################################
# Tests the functionality around the Portfolio and RobotBudgetManagament.
# This consists of the following classes:
#  1. Portfolio class: This class interfaces directly with the Portfolio on the Broker side.
#  2. RobotBudgetManagament: This class interfaces directly with the User Interface. It hides some information
#     coming from the portfolio from the User manipulating the data. 
#  Ideally, the Portfolio would require credentials to become accessible.
#

#@unittest.skip("Taking a break now")
class RobotBudgetManagementClassBasicTestCase(TestCase):
  testname = 'RobotBudgetManagementClassBasicTestCase'
  port_name='Etrade'
  port_description='This is the Etrade Account.'
  brokerage=''
  initial_cash_funds=10000
  current_cash_funds=10000
  max_robot_fraction=0.10
  max_budget_per_purchase='2000'
  cash_position_update_policy='immediate'

  @classmethod 
  def setUpTestData(self):
    displayOutput("Setting up {0}".format(self.testname))
    
    #Create Portfolio against ETrade. Use 10% of the Portfolio Budget
    etrade = Portfolio.objects.create(name=self.port_name,description=self.port_description,
      initial_cash_funds=self.initial_cash_funds,current_cash_funds=self.current_cash_funds,max_robot_fraction='10%',
      cash_position_update_policy='immediate')
    self.p_id = etrade.pk

    self.robot = ETFAndReversePairRobot.objects.create(portfolio=etrade)

    budget = RobotBudgetManagement.objects.create(use_percentage_or_fixed_value='Number',add_taxes=False,
      max_budget_per_purchase_number=self.max_budget_per_purchase, add_commission=False,add_other_costs=False,
                                                  pair_robot_id=self.robot.id)
    self.budget_id = budget.pk

  #
  #
  #
  #@unittest.skip("Taking a break now")
  def testBudgetUsingNumbers(self):
    robot = ETFAndReversePairRobot.objects.get(pk=self.robot.pk)
    portfolio = robot.portfolio

    bud = RobotBudgetManagement.objects.get(pk=self.budget_id)
    bud.setInitialDailyBudget(robot=self.robot)
    self.assertEqual(bud.getCostBasisPerRoundtrip(),float(self.max_budget_per_purchase))
    self.assertEqual(bud.haveEnoughFundsToPurchase(),True)
    self.assertEqual(bud.getAvailableTotalCash(),self.current_cash_funds)
    self.assertEqual(bud.updateBudgetAfterAcquisition(amount=2500),self.current_cash_funds - 2500) 
    self.assertEqual(bud.updateBudgetAfterAcquisition(amount=2500),self.current_cash_funds - (2*2500)) 
    self.assertEqual(bud.haveEnoughFundsToPurchase(),True)
    self.assertEqual(bud.getAvailableTotalCash(),self.current_cash_funds-(2*2500))
    self.assertEqual(bud.updateBudgetAfterAcquisition(amount=2500),self.current_cash_funds - (3*2500)) 
    self.assertEqual(bud.haveEnoughFundsToPurchase(),True)
    self.assertEqual(bud.getAvailableTotalCash(),self.current_cash_funds-(3*2500))
    self.assertEqual(bud.haveEnoughFundsToPurchase(),True)
    self.assertEqual(bud.updateBudgetAfterAcquisition(amount=2500),self.current_cash_funds - (4*2500)) 
    self.assertEqual(bud.getAvailableTotalCash(),self.current_cash_funds-(4*2500))
    self.assertEqual(bud.haveEnoughFundsToPurchase(),False)
    self.assertEqual(bud.updateBudgetAfterDisposition(amount=2500),2500) 


  # The main is to use percentages to calculate how much money to invest per acquisition.
  # This approach uses a percentage of total portfolio. (i.e.: 10%). However, we didn't a good job
  # using the same percentage through a certain period. As the $$$ diminushes, using percentages is not
  # a good Idea. This functionality should be redesigned.
  # Question: Should it be the percentage of a fixed number or a percentage of a
  # a variable number?
  # NOTE: I have concerned about this approach as I would like to see it depend only on 
  # a fixed daily value. I.e.: 
  #@unittest.skip("Taking a break now")
  def testBudgetUsingPercent(self):
    robot = ETFAndReversePairRobot.objects.get(pk=self.robot.pk)
    portfolio = robot.portfolio

    bud = RobotBudgetManagement.objects.get(pk=self.budget_id)
    
    #Change to use 'percentage vs Numbers'
    bud.use_percentage_or_fixed_value='Percent'
    bud.max_budget_per_purchase_percent='15'
    bud.save()

    bud.setInitialDailyBudget(robot=self.robot)
    self.assertEqual(bud.getCostBasisPerRoundtrip(),float(.01 * int(bud.max_budget_per_purchase_percent) * self.current_cash_funds))
    self.assertEqual(bud.haveEnoughFundsToPurchase(),True)
    self.assertEqual(bud.getAvailableTotalCash(),self.current_cash_funds)
    self.assertEqual(bud.updateBudgetAfterAcquisition(amount=2500),self.current_cash_funds - 2500) 
    self.assertEqual(bud.getCostBasisPerRoundtrip(),float(.01 * int(bud.max_budget_per_purchase_percent) * bud.getAvailableTotalCash()))
    self.assertEqual(bud.updateBudgetAfterAcquisition(amount=2500),self.current_cash_funds - (2*2500)) 
    self.assertEqual(bud.haveEnoughFundsToPurchase(),True)
    self.assertEqual(bud.updateBudgetAfterAcquisition(amount=2500),self.current_cash_funds - 3*2500) 
    self.assertEqual(bud.haveEnoughFundsToPurchase(),True)
    self.assertEqual(bud.updateBudgetAfterAcquisition(amount=2500),self.current_cash_funds - (4*2500)) 
    self.assertEqual(bud.haveEnoughFundsToPurchase(),True)
    self.assertEqual(bud.updateBudgetAfterDisposition(amount=2500),2500) 
    self.assertEqual(bud.getCostBasisPerRoundtrip(),float(.01 * int(bud.max_budget_per_purchase_percent) * bud.getAvailableTotalCash()))
    self.assertEqual(bud.getAvailableTotalCash(),2500)
    self.assertEqual(bud.haveEnoughFundsToPurchase(),True)


if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)
