import datetime, time, pytz, logging, unittest , sys,json
import pandas as pd
from django.utils import timezone
from django.test import TestCase
import dateutil.parser, xmlrunner
#from django.utils.timezone import datetime

from bullbearetfs.robot.models import ETFAndReversePairRobot
from bullbearetfs.models import  RobotBudgetManagement, Portfolio, BrokerageInformation

logger = logging.getLogger(__name__)

def test_datasources_dummy(request):
  logger.info(" This is just a dummy function ")

##############################################################################################
# This class tests the functionality of the DataSource + Portfolio Selection
#  This functionality is important for knowing where the orders will go to, where the budget will come from.
#
# Tests the functionality around:
#    Basic Robot Information Page.
#    Ability to navigate the conditionals
#    Several robots running at the same time.
#    Status: Incomplete
#     -RobotDataSourcesPortfolioTestCase: Basic class with all the various combinations.
#      We only have access to Alpaca. Other Brokerages are not yet setup.
#    Number of Test Classes Planned: 3-4
#    Total Number of Test Functions: 
#    Number of remaining Classes: 0-3
#    STATUS: As far complete as we can.
##############################################################################################


#
#
#
#@unittest.skip("Taking a break now")
class RobotDataSourcesPortfolioTestCase(TestCase):
  testname = 'RobotDataSourcesPortfolioTestCase'
  port_name = "Test Me Portfolio"
  port_description = "This is my model Portfolio"
  initial_cash_funds = 10000
  @classmethod 
  def setUpTestData(self):
    print("Setting up {0}".format(self.testname))
    
    alpaca = BrokerageInformation.objects.create(brokerage_type='Alpaca',name='Alpaca Brokerage',website='https://alpaca.markets/')
    etrade_reg = BrokerageInformation.objects.create(brokerage_type='eTrade Regular',name='ETrade Regular',website='https://etrade.com/')
    etrade_ret = BrokerageInformation.objects.create(brokerage_type='eTrade Retirement',name='ETrade Retirement',website='https://etrade.com/')
    local_acct = BrokerageInformation.objects.create(brokerage_type='Local Account',name='Local Account',website='')
    ameritrade = BrokerageInformation.objects.create(brokerage_type='Ameritrade',name='Ameritrade',website='https://ameritrade.com/')

    etrade_regular = Portfolio.objects.create(name=self.port_name,description=self.port_description,
      initial_cash_funds=self.initial_cash_funds,current_cash_funds=2500,max_robot_fraction='10%',
      cash_position_update_policy='immediate',brokerage=etrade_reg)    
    self.p_id = etrade_regular.pk

    etrade_retirement = Portfolio.objects.create(name=self.port_name,description=self.port_description,
      initial_cash_funds=self.initial_cash_funds,current_cash_funds=2500,max_robot_fraction='10%',
      cash_position_update_policy='immediate',brokerage=etrade_ret)
    self.p2_id = etrade_retirement.pk

    alpaca = Portfolio.objects.create(name=self.port_name,description=self.port_description,
      initial_cash_funds=self.initial_cash_funds,current_cash_funds=2500,max_robot_fraction='10%',
      cash_position_update_policy='immediate',brokerage=alpaca)
    self.p3_id = alpaca.pk

    amd = Portfolio.objects.create(name=self.port_name,description=self.port_description,
      initial_cash_funds=self.initial_cash_funds,current_cash_funds=2500,max_robot_fraction='10%',
      cash_position_update_policy='immediate',brokerage=ameritrade)
    self.amd_id = amd.pk

    local = Portfolio.objects.create(name=self.port_name,description=self.port_description,
      initial_cash_funds=self.initial_cash_funds,current_cash_funds=2500,max_robot_fraction='10%',
      cash_position_update_policy='immediate',brokerage=local_acct)
    self.local_id = local.pk

    robot_paper_0 = ETFAndReversePairRobot.objects.create(portfolio=etrade_regular,data_source_choice='live')
    self.r0_id = robot_paper_0.id
    robot_paper_1 = ETFAndReversePairRobot.objects.create(portfolio=etrade_retirement,data_source_choice='backtest')
    self.r1_id = robot_paper_1.id

    #Alpaca Paper
    robot_paper_2 = ETFAndReversePairRobot.objects.create(portfolio=alpaca,data_source_choice='paper')
    self.r2_id = robot_paper_2.id

    #Local Backtest
    robot_paper_3 = ETFAndReversePairRobot.objects.create(portfolio=local,data_source_choice='backtest')
    self.r3_id = robot_paper_3.id

    #Alpaca Live
    robot_paper_4 = ETFAndReversePairRobot.objects.create(portfolio=alpaca,data_source_choice='live')
    self.r4_id = robot_paper_4.id

  def testAlpacaPortfolioTest(self):
    alpaca = Portfolio.objects.get(pk=self.p3_id)
    self.assertEqual(alpaca.isAlpaca(),True)
    self.assertEqual(alpaca.isLocal(),False)
    self.assertEqual(alpaca.isAmeritrade(),False)
    self.assertEqual(alpaca.isETradeRegular(),False)
    self.assertEqual(alpaca.isETradeRetirement(),False) 

  def testLocalPortfolioTest(self):
    local = Portfolio.objects.get(pk=self.local_id)
    self.assertEqual(local.isLocal(),True)
    self.assertEqual(local.isAlpaca(),False)
    self.assertEqual(local.isAmeritrade(),False)
    self.assertEqual(local.isETradeRegular(),False)
    self.assertEqual(local.isETradeRetirement(),False) 

  def testAmeritradePortfolioTest(self):
    ameri = Portfolio.objects.get(pk=self.amd_id)
    self.assertEqual(ameri.isAmeritrade(),True)
    self.assertEqual(ameri.isLocal(),False)
    self.assertEqual(ameri.isAlpaca(),False)
    self.assertEqual(ameri.isETradeRegular(),False)
    self.assertEqual(ameri.isETradeRetirement(),False) 

  def testETradePortfolioTest(self):
    et_1 = Portfolio.objects.get(pk=self.p_id)
    self.assertEqual(et_1.isETradeRegular(),True)
    self.assertEqual(et_1.isAlpaca(),False)
    self.assertEqual(et_1.isAmeritrade(),False)
    self.assertEqual(et_1.isLocal(),False)
    self.assertEqual(et_1.isETradeRetirement(),False) 

  def testETradeRetPortfolioTest(self):
    et_2 = Portfolio.objects.get(pk=self.p2_id)
    self.assertEqual(et_2.isETradeRetirement(),True) 
    self.assertEqual(et_2.isETradeRegular(),False)
    self.assertEqual(et_2.isAlpaca(),False)
    self.assertEqual(et_2.isAmeritrade(),False)
    self.assertEqual(et_2.isLocal(),False)

  def testLiveFeedPortfolioTest(self):
    r_paper0 = ETFAndReversePairRobot.objects.get(pk=self.r0_id)
    self.assertEqual(r_paper0.isDataSourceLiveFeed(),True) 
    self.assertEqual(r_paper0.isDataSourcePaperAccount(),False) 
    self.assertEqual(r_paper0.isDataSourceLocal(),False) 
    self.assertEqual(r_paper0.isDataSourceBacktest(),False) 

  def testPaperFeedPortfolioTest(self):
    r_paper2 = ETFAndReversePairRobot.objects.get(pk=self.r2_id)
    self.assertEqual(r_paper2.isDataSourcePaperAccount(),True) 
    self.assertEqual(r_paper2.isDataSourceLiveFeed(),False) 
    self.assertEqual(r_paper2.isDataSourceLocal(),False) 
    self.assertEqual(r_paper2.isDataSourceBacktest(),False) 

  def testLocalFeedPortfolioTest(self):
    r_paper1 = ETFAndReversePairRobot.objects.get(pk=self.r1_id)
    self.assertEqual(r_paper1.isDataSourceLocal(),True) 
    self.assertEqual(r_paper1.isDataSourceBacktest(),True) 
    self.assertEqual(r_paper1.isDataSourcePaperAccount(),False) 
    self.assertEqual(r_paper1.isDataSourceLiveFeed(),False)  

  def testAlpacaPaperAccountTest(self):
    alpaca_paper = ETFAndReversePairRobot.objects.get(pk=self.r2_id)
    self.assertEqual(alpaca_paper.isAlpacaPaperAccount(),True) 
    self.assertEqual(alpaca_paper.isAlpacaLiveAccount(),False) 
    self.assertEqual(alpaca_paper.isEtradeRegularPaperAccount(),False) 
    self.assertEqual(alpaca_paper.isEtradeRetirementPaperAccount(),False) 

  def testLocalBacktestAccountTest(self):
    local_backtest = ETFAndReversePairRobot.objects.get(pk=self.r3_id)
    self.assertEqual(local_backtest.isLocalBacktestAccount(),True) 
    self.assertEqual(local_backtest.isAlpacaLiveAccount(),False) 
    self.assertEqual(local_backtest.isAlpacaPaperAccount(),False) 

  def testAlpacaLiveAccountTest(self):
    alpaca_live = ETFAndReversePairRobot.objects.get(pk=self.r4_id)
    self.assertEqual(alpaca_live.isAlpacaLiveAccount(),True) 
    self.assertEqual(alpaca_live.isAlpacaPaperAccount(),False) 
    self.assertEqual(alpaca_live.isEtradeRegularPaperAccount(),False) 
    self.assertEqual(alpaca_live.isEtradeRetirementPaperAccount(),False) 
    self.assertEqual(alpaca_live.isLocalBacktestAccount(),False) 


if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)

