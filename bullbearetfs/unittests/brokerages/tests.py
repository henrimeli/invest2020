import datetime, logging, pytz, xmlrunner
import unittest, json, time
from django.test import TestCase
import pandas as pd 
from datetime import timedelta
from datetime import date
from django.utils import timezone
from bullbearetfs.brokerages.alpaca import AlpacaAPIBase, AccountInformation, OpenPositions
from bullbearetfs.brokerages.alpaca import BullBearBuyOrder , QueryOrders, SellOrder,AlpacaMarketClock
from bullbearetfs.utilities.core import getTimeZoneInfo
logger = logging.getLogger(__name__)

"""
  This module contains unittests for the Brokerages component.
  These are tests that check the functionality of the backend for the Business Intelligence
  Below is the complete list of all the tests classes in this test:
 
  BasicConnectionTestCase :
  AccountInformationTestCase :
  MarketClockTestCase :
  SellOrderTestCase:
"""
def test_brokerages_dummy(request):
  pass


#
# Dummy function needed to force rebuild on change.
#
def test_brokerage_dummy(request):
  pass

##############################################################################################
# Brokerate Related Interface.
#
# Tests the functionality around the interaction with the Brokerage (Alpaca).
# Alpaca offers APIs that can be accessed for a variety of functions.
# These functions can all be seen from this URL: https://github.com/alpacahq/alpaca-trade-api-python
# The information retrieve from the Brokerage can be divided in the following groups:
#   Basic Connection Test: BasicConnectionTestCase
#   Account Information: AccountInformation
#   Market Information: OpenPositionsTestCase
#   Sell Order : SellOrderTestCase
#   Bull Bear Buy Order:  BullBearBuyOrderTestCase
#   QueryOrdersTestCase:
#   
##############################################################################################################
# Tests the functionality around:
#  Unit Test Organization. Most unittests will be organized in the following classes.
#    A Test Class for the empty set and validations to ensure proper returns, when there is no data.
#    A Test Class with up to 5 Data entries to make sure the functions are called and respond properly.
#    A Test Class with a large number of data (20-50 maybe)
#    A Test Class with combined Robots to ensure that application can function with various Robots.
#    Optionally a Test Class with Risk, Performance, ... etc.
#    
#    RoundtripBasicOneBuyTestCase : Create a Robot and execute a single Buy Operation
#    Status: Complete
#
#    RoundtripThreeEntriesMovingDatesTestCase:  Create a Robot and add 1 entry, then move the 'currenttime' several times
#                                     just like a typical day in the Market would look like. 
#    Status: Complete
#
#    RoundtripFiveEntriesAddedTestCase: Uses Conditional to determin purchase decision. INCOMPLETE
#    Status: Complete
#
#    RoundtripWithOneBuyOneSaleTestCase: 
#    Status: Complete 
#
#    RoundTripWithRiskExposureCalculationTestCase: INCOMPLETE
#    Roundtrip15RobotsWithLotsofDataTestCase: INCOMPLETE
#        Number of Test Classes Planned: 6
#        Total Number of Test Functions: many
#        Number of remaining Classes: 2
#  
#####################################################################################################
#
# One Simple Roundtrip . Validate that all basic functions can be reached and executed with correct results.
#
#@unittest.skip("Taking a break now")

  
def generate_root_client_order_id():
  order_client_id = datetime.datetime.now().strftime("egghead%Y%m%d_%H_%M_%S")
  return order_client_id

#symbol=bull_payload['symbol'],qty=bull_payload['qty'],side='buy',type='market',
# time_in_force=payload['time_in_force'],client_order_id=bull_payload['buy_client_order_id'])
#TODO: This MUST come from the Robot
def generate_bull_bear_buy_payload(order_type):	
  bull_payload = dict()
  bear_payload = dict()
  payload = dict()
  bull_symbol = 'TQQQ'
  bear_symbol = 'SQQQ'
  if order_type=='market':
    payload['type']='market'
    bull_payload['buy_client_order_id']=generate_root_client_order_id() + '_buy_'+bull_symbol
    bear_payload['buy_client_order_id']=generate_root_client_order_id() + '_buy_'+bear_symbol
    bull_payload['symbol']=bull_symbol
    bull_payload['qty'] = 1
    bear_payload['symbol']=bear_symbol
    bear_payload['qty'] = 1

  elif order_type == 'limit':
    payload['type']='limit'
    bull_payload['buy_client_order_id']=generate_root_client_order_id() + '_buy_'+bull_symbol
    bear_payload['buy_client_order_id']=generate_root_client_order_id() + '_buy_'+bear_symbol
    bull_payload['symbol']=bull_symbol
    bull_payload['qty'] = 1
    bear_payload['symbol']=bear_symbol
    bear_payload['qty'] = 1
  else:
  	logger.error('')
  payload['time_in_force']='gtc'
  payload['bull_payload'] = bull_payload
  payload['bear_payload'] = bear_payload
  return payload

# self.getAPI().submit_order(symbol=payload['symbol'],qty=payload['qty'],side='sell',type='market',
#  time_in_force=payload['time_in_force'],client_order_id=payload['sell_client_order_id'])

def generate_sell_payload(order_type):
  payload = dict() 
  symbol = 'TQQQ'
  if order_type=='market':
    payload['type']='market'
    payload['sell_client_order_id']=generate_root_client_order_id() + '_sell_'+symbol
    payload['symbol']=symbol
    payload['qty'] = 1

  elif order_type == 'limit':
    payload['type']='limit'
    payload['sell_client_order_id']=generate_root_client_order_id() + '_sell_'+symbol
    payload['symbol']=symbol
    payload['qty'] = 1

  return payload

#
# Tests the Connection to a server. Confirms that we can connect to Alpaca.
#
@unittest.skip("Taking a break now")
class BasicConnectionTestCase(TestCase):
  """
    This class tests the connectivity to the Alpaca. An good result confirms that we can connect to 
    the Brokerage

    The following tests are run:

  """
  @classmethod 
  def setUpTestData(self):
    pass
    
  # Tests connectivity to the Alpaca API
  # NOTE: You must make sure that the KEYS are defined in 
  # the appropriate files on the test case servers
  def testBaseConnectionToAlpaca(self):
    name ='testBaseConnectionToAlpaca'
    alpaca = AlpacaAPIBase()
    self.assertEqual(alpaca.isValid(),True)

  def testPaperAccount(self):
    name = 'testPaperAccount'
    alpaca = AlpacaAPIBase()
    self.assertEqual(alpaca.isPaperAccount(),True)

  # Tests connectivity to the LIVE Alpaca API
  # NOTE: You must make sure that the KEYS are defined in 
  # the appropriate files on the test case servers.
  # Should only be run in LIVE settings.
  #TODO: Research me and implement me 
  @unittest.skip("Taking a break now")
  def testLiveAccount(self):
    name = 'testLiveAccount'
    alpaca = AlpacaAPIBase()
    self.assertEqual(alpaca.isLiveAccount(),True)


#
# Validates that we can retrieve Account Information from the Alpaca Server
#
@unittest.skip("Taking a break now")
class AccountInformationTestCase(TestCase):
  """
    This class validates that Account information can be retrieved.
    An good result confirms that we can connect to the Brokerage and retrieved the information needed.

    The following tests are run:
    
  """

  @classmethod 
  def setUpTestData(self):
    pass
    
  def testAccountStatus(self):
    name ='testAccountStatus'
    alpaca = AccountInformation()
    self.assertEqual(alpaca.isActive(),True)
    self.assertEqual(alpaca.getAccountStatus(),'ACTIVE')
    self.assertEqual(alpaca.accountIsBlockedByBrokerage(),False)
    self.assertEqual(alpaca.isValid(),True)

  #TODO: Research and implement me.
  def testCashflowScenarios(self):
    name ='testCashflowScenarios'
    alpaca = AccountInformation()
    self.assertEqual(alpaca.isValid(),True)
    self.assertEqual(alpaca.getBuyingPower(),396718.24)

#
# Validates that we can retrieve the Market Clock from the Alpaca Server
#
#@unittest.skip("Taking a break now")
class MarketClockTestCase(TestCase):
  """
    This class validates check if the market is open can be retrieved. 
    An good result confirms that we can connect to the Brokerage

    The following tests are run:
    
  """

  @classmethod 
  def setUpTestData(self):
    pass
    
  #
  # Tests ability to check if the Market is open or closed.TODO: Make this test results time sensitive
  #
  @unittest.skip("Taking a break now")
  def testMarketClock(self):
    name ='testMarketClock'
    today = datetime.datetime.now(getTimeZoneInfo())
    week_day = True if today.isoweekday() in range(1, 6) else False
    hour = True if today.hour in range (9,16) else False
    alpaca = MarketClock()
    self.assertEqual(alpaca.isOpen(),week_day and hour)

  def testTradingCalendarNoEndDate(self):
    name ='testTradingCalendar'
    alpaca = AlpacaMarketClock()
    start_date = datetime.datetime(2020,10,1,tzinfo=timezone.utc).isoformat()
    results=alpaca.getTradingCalendar(start_date=start_date)
    self.assertTrue(len(results)>10)
    #print("entries = {} ".format(len(result)))

  def testStartSameAsEnddate(self):
    name ='testTradingCalendar'
    alpaca = AlpacaMarketClock()
    start_date = datetime.datetime(2020,10,1,tzinfo=timezone.utc).isoformat()
    end_date = datetime.datetime(2020,10,1,tzinfo=timezone.utc).isoformat()
    results=alpaca.getTradingCalendar(start_date=start_date,end_date=end_date)
    self.assertEqual(len(results),1)

  def testStartAndEndDateDifferent(self):
    name ='testTradingCalendar'
    alpaca = AlpacaMarketClock()
    start_date = datetime.datetime(2020,10,1,tzinfo=timezone.utc).isoformat()
    end_date = datetime.datetime(2020,10,3,tzinfo=timezone.utc).isoformat()
    results=alpaca.getTradingCalendar(start_date=start_date,end_date=end_date)
    self.assertEqual(len(results),2)

#
# Validates that we can retrieve the Various orders placed from the Alpaca Server
#
@unittest.skip("Taking a break now")
class QueryOrdersTestCase(TestCase):
  """
    This class validates that Alpaca orders can be retrieved. 

    The following tests are run:
    
  """

  @classmethod 
  def setUpTestData(self):
    pass
 
  # A Dual Buy Order has been submitted to the server. 
  # Now, run a command to retrieve the results.
  # There might NOT be results.
  # Also handle the scenario where there are other errors or no connection   
  # querySellOrderByClientOrderID
  def testQueryBullBearBuyOrders(self):
    """
      TODO: This class validates the connection to the Alpaca. An good result confirms that we can connect to 
      the Brokerage

      The following tests are run:
    
    """

    name ='testQueryBullBearBuyOrders'
    alpaca = QueryOrders()
    order_ids = dict()
    order_ids['bull_buy_client_order_id'] = 'abc'
    order_ids['bear_buy_client_order_id'] = 'bear_buy_client_order_id'
    result = alpaca.queryBullBearBuyOrderByClientOrderID(payload=order_ids)
    bull_result = result['bull_order_result']
    bear_result = result['bear_order_result']
    print("HENRI: \n Bull Results: {0}.  \n Bear Results: {1}.".format(bull_result,bear_result))
    self.assertEqual(False,True)

  # A Sell Order has been submitted to the server. 
  # Now, run a command to retrieve the results.
  # querySellOrderByClientOrderID
  def testQuerySellOrders(self):
    name ='testQueryBullBearBuyOrders'
    alpaca = QueryOrders()
    order_ids = dict()
    order_ids['sell_client_order_id'] = 'abc'
    result = alpaca.testQuerySellOrders(payload=order_ids)
    sell_result = result['sell_order_result']
    print("HENRI: \n Sell Results: {0}.".format(sell_result))
    self.assertEqual(False,True)


#
# What are my current positions? This should be used in
# a class that reconciles the Portfolio with the Local Robot Data
# to ensure consistency and accuracy. Ideally should run every night or after market closed at 7PM
# TODO: The results of reconciliation can be analyzed by Cameroon/Cali based teams to ensure no errors/discrepency.
#
@unittest.skip("Taking a break now")
class OpenPositionsTestCase(TestCase):
  """
    TODO: This class validates the connection to the Alpaca. An good result confirms that we can connect to 
    the Brokerage

    The following tests are run:
    
  """

  @classmethod 
  def setUpTestData(self):
    pass
    
  #
  def testOpenPositionInformation(self):
    name ='testOpenPositionInformation'
    alpaca = OpenPositions()
    self.assertEqual(alpaca.isValid(),True)
    self.assertEqual(False,True)

# Places an order to purchase both the Bull and the Bear at the same time.
# A variable is used to determine if there should be a delay in the purchase
# or if both should happen exactly at the same moment.
# We want to insist for now that all we don't fill partial orders. Only ALL or NOTHING.
@unittest.skip("Taking a break now")
class BullBearBuyOrderTestCase(TestCase):
  """
    TODO: This class validates the connection to the Alpaca. An good result confirms that we can connect to 
    the Brokerage

    The following tests are run:
    
  """

  @classmethod 
  def setUpTestData(self):
    pass
    
  # Tests Bull Bear Market Order 
  #
  def testBullBuyMarketOrder(self):
    name ='testBullBuyMarketOrder'
    alpaca = BullBearBuyOrder()
    market_payload = generate_bull_bear_buy_payload(order_type='market') 
    self.assertEqual(alpaca.isValid(),True)
    result = alpaca.submitMarket(payload=market_payload)
    self.assertEqual(alpaca.isValid(),True)
    self.assertEqual(result,True)

  # Tests Bull Bear Limit Order 
  #
  def testBullBuyLimitOrder(self):
    name ='testBullBuyLimitOrder'
    alpaca = BullBearBuyOrder()
    limit_payload = generate_bull_bear_buy_payload(order_type='limit') 
    self.assertEqual(alpaca.isValid(),True)
    result = alpaca.submitMarket(payload=limit_payload)
    self.assertEqual(alpaca.isValid(),True)
    self.assertEqual(result,True)

  def testInvalid1BullBuyMarketOrder(self):
    name ='testInvalid1BullBuyOrder'
    alpaca = BullBearBuyOrder()
    limit_payload = generate_invalid1_bull_bear_buy_payload(order_type='limit') 
    self.assertEqual(alpaca.isValid(),True)
    result = alpaca.submitMarket(payload=limit_payload)
    self.assertEqual(alpaca.isValid(),True)
    self.assertEqual(result,True)

  #When submitting a limit order, Alpaca has some constraints related to the difference between
  #limit price and the current actual price. In some instances, the orders submitted will be rejected
  # because of the price. Make sure to capture this scenario and handle appropriately.
  def testInvalid2BullBuyLimitOrder(self):
    name ='testInvalid2BullBuyOrder'
    alpaca = BullBearBuyOrder()
    limit_payload = generate_invalid2_bull_bear_buy_payload(order_type='limit') 
    self.assertEqual(alpaca.isValid(),True)
    result = alpaca.submitMarket(payload=limit_payload)
    self.assertEqual(alpaca.isValid(),True)
    self.assertEqual(result,True)

# Places an order to sell. We only sell one blaock at a time.
# We would like for all the orders to be ALL or NOTHING. We don't want partial orders at this time.
# We want to insist for now that all we don't fill partial orders. Only ALL or NOTHING.
@unittest.skip("Taking a break now")
class SellOrderTestCase(TestCase):
  """
    TODO: This class validates the connection to the Alpaca. An good result confirms that we can connect to 
    the Brokerage

    The following tests are run:
    
  """

  @classmethod 
  def setUpTestData(self):
    pass
    
  # Tests Bull Bear Market Order 
  #
  def testSellMarketOrder(self):
    name ='testSellMarketOrder'
    alpaca = SellOrder()
    market_payload = generate_sell_payload(order_type='market') 
    self.assertEqual(alpaca.isValid(),True)
    result = alpaca.submitMarket(payload=market_payload)
    self.assertEqual(alpaca.isValid(),True)
    self.assertEqual(result,True)

  # Tests Limit Order 
  #
  def testSellLimitOrder(self):
    name ='testSellLimitOrder'
    alpaca = SellOrder()
    limit_payload = generate_sell_payload(order_type='limit') 
    self.assertEqual(alpaca.isValid(),True)
    result = alpaca.submitMarket(payload=limit_payload)
    self.assertEqual(alpaca.isValid(),True)
    self.assertEqual(result,True)


if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)