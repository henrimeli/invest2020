import datetime, time, pytz, logging, unittest , sys,json
import pandas as pd
from django.utils import timezone
from django.test import TestCase
import dateutil.parser,xmlrunner

from bullbearetfs.strategy.models import EquityStrategy, AcquisitionPolicy,DispositionPolicy
from bullbearetfs.strategy.models import OrdersManagement,PortfolioProtectionPolicy
from bullbearetfs.robot.models import  ETFAndReversePairRobot
#from bullbearetfs.utilities.core import RobotSellOrderExecutor, RobotBuyOrderExecutor
from bullbearetfs.utilities.alpaca import AlpacaLastTrade, AlpacaPolygon
from bullbearetfs.robot.symbols.models import RobotEquitySymbols
from bullbearetfs.robot.foundation.roundtrip import RoundTrip
from bullbearetfs.robot.models import RoundTrip
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, strToDatetime, shouldUsePrint, displayOutput,displayError
CHOICES_BLACKOUT_WINDOW=((1,'one'),(5,'five'),(30,'30'),(45,'45'),(60,'60'))

logger = logging.getLogger(__name__)

def test_utilities_dummy(request):
  logger.info(" This is just a dummy function ")

#
@unittest.skip("TODO: Move to the Brokerages package")
class UtilitiesCoreCase(TestCase):
  testname ='UtilitiesCoreCase'

  @classmethod 
  def setUpTestData(self):
    print("Setting up {0}".format(self.testname))

  def testTimezoneAwareDatesTest(self):
    now=datetime.datetime.now(getTimeZoneInfo())

  def testReverseTuplesTest(self):
    R_CHOICES_BLACKOUT_WINDOW = getReversedTuple(tuple_data=CHOICES_BLACKOUT_WINDOW)
    one = R_CHOICES_BLACKOUT_WINDOW['one']
    five = R_CHOICES_BLACKOUT_WINDOW['one']
    self.assertEqual(one,1)
    self.assertEqual(five,5)

  def testExceptionTest(self):
    #InvalidTradeDataHolderException
    print('Raise Exceptions {0}'.format('come exception'))

 #

@unittest.skip("TODO: Move to the Brokerages package")
class UtilitiesBuyOrdersCase(TestCase):
  testname ='UtilitiesCoreCase'

  @classmethod 
  def setUpTestData(self):
    print("Setting up {0}".format(self.testname))

  def testBuyOrder1Test(self):
    print("Testing Buy Order Scenario")

  def testBuyOrder2Test(self):
    print("Testing Buy Order 2 Scenario")

  def testBuyOrderPreMarketTest(self):
    print("Testing Buy Order Pre market Scenario")

  def testBuyOrderPostMarketTest(self):
    print("Testing Buy Order Post Market Scenario")

  def testBuyOrderExtendedPreMarketTest(self):
    print("Testing Buy Order Extended Pre Market Scenario")

  def testBuyMarketOrdersTest(self):
    print("Testing Buy Market Order Scenario")

  def testBuyLimitTest(self):
    print("Testing Buy Limit Order Scenario")

@unittest.skip("TODO: Move to the Brokerages package")
class UtilitiesSellOrdersCase(TestCase):
  testname ='UtilitiesSellOrdersCase'

  @classmethod 
  def setUpTestData(self):
    print("Setting up {0}".format(self.testname))

  def testSellOrder1Test(self):
    print("Testing Sell Order Scenario")

  def testSellOrder2Test(self):
    print("Testing Sell Order Scenario")

  def testSellOrderPreMarketTest(self):
    print("Testing Sell Order Scenario")

  def testSellOrderPostMarketTest(self):
    print("Testing Sell Order Scenario")

  def testSellOrderExtendedPreMarketTest(self):
    print("Testing Sell Order Scenario")

  def testSellMarketOrdersTest(self):
    print("Testing Sell Order Scenario")

  def testSellLimitTest(self):
    print("Testing Sell Order Scenario")


@unittest.skip("TODO: Move to the Brokerages package")
class UtilitiesProcessOrdersCase(TestCase):
  testname ='UtilitiesProcessOrdersCase'

  @classmethod 
  def setUpTestData(self):
    print("Setting up {0}".format(self.testname))

  def testSellOrder1Test(self):
    print("Testing Process Order Scenario")

  def testSellOrder2Test(self):
    print("Testing Process Order Scenario")

  def testSellOrderPreMarketTest(self):
    print("Testing Process Order Scenario")

  def testSellOrderPostMarketTest(self):
    print("Testing Process Order Scenario")

  def testSellOrderExtendedPreMarketTest(self):
    print("Testing Process Order Scenario")

  def testSellMarketOrdersTest(self):
    print("Testing Process Order Scenario")

  def testSellLimitTest(self):
    print("Testing Process Order Scenario")

if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)
