import datetime, time, logging
import sys,json,unittest,os 
from django.utils import timezone
from django.test import TestCase

# Import Models
from bullbearetfs.models import TradeDataHolder, ETFAndReversePairRobot
from bullbearetfs.utilities.core  import  getTimeZoneInfo,shouldUsePrint
from bullbearetfs.utilities.errors import InvalidTradeDataHolderException
from bullbearetfs.robot.models import RobotEquitySymbols 

logger = logging.getLogger(__name__)

#
# Dummy function needed to force rebuild on change.
#
def test_robots_data_dummy(request):
  logger.info(" This is just a dummy function ")

##############################################################################################################
# The TradeDataHolder Class contains information about the Foundational class of our application.
# This data represent transactions that have been performed (or about to be performed) on the Brokerage.
#   Each entry represents an actual transaction with the most important information such as:
#   Symbol, Quantity, Buyprice, Sellprice, buy_date, sell_date, buy_order_client_id,sell_order_client_id, ....
# This data constitutest the foundation of our strategy.
# Additionally, several functions are built on top of this class. These functions are organized in two main categories:
# Static methods: These represent the actions to be performed on all instances such
# Instance methods: These are methods performed on each of the entries.
##############################################################################################################
# Tests the functionality around:
#    BuyPairSellBearBullTestCase : Create the smallest structure needed for the creation of an order.
#                                  Validate that we can record an acquisition in the Database and the sell of a Bear
#                                  Validate that we can record an acquisition in the Database and the sell of a Bull
#    Status: Complete
#
#    GenerateBuySellOrderClientIDsTestCase:  Generation of RootClientOrderIDs, BuyClientOrderIDs, SellClientOrderIDs
#                                    Validate that these variable look are as expected.
#    Status: Complete
#
#    BuySeveralPairsTestCase: Validate that we can record a large number of entries and retrieve them appropriately. 
#    Status: Complete
#
#    SimpleBuyPairTestCase:  Validate status related and financial calculation functions of the class.
#    Status: Complete 
#
#    InvalidScenariosTestCase: Validate some invalid scenarios and ensure that we can handle them smoothly.
#    Status: Complete
#
#        Number of Test Classes Planned: 5
#        Total Number of Test Functions: 12 tests
#        Number of remaining Classes: 0
#  
##############################################################################################
# Buy a Pair (Bull + Bear) + Sell Operations
#
# Tests the functionality around the TradeDataHolder Class.
#    Buying Pairs, Selling Individually side (sell the bear, sell the bull).
#    Status: Complete
##############################################################################################
#
# One Pair Buy + Sell Operations
#
#@unittest.skip("Taking a break now")
class BuyPairSellBearBullTestCase(TestCase):
  testname='BuyPaidSellBearBullTestCase'
  current_times=['2020-08-03 04:00:00-04:00']
  bull_prices=[120.47]
  bear_prices=[29.4]
  bull_symbol='TQQQ'
  bear_symbol='SQQQ'
  
  @classmethod 
  def setUpTestData(self):
    if shouldUsePrint():
      print("Setting up {0}".format(self.testname))

    index = 0
    self.bullish = dict()
    self.bearish = dict()
    for x in self.current_times:
      self.bullish['symbol']=self.bull_symbol
      self.bullish['price']=self.bull_prices[index]
      self.bullish['qty']=10
      self.bullish['date']=self.current_times[index]

      self.bearish['symbol']=self.bear_symbol
      self.bearish['price']=self.bear_prices[index]
      self.bearish['qty']=170
      self.bearish['date']=self.current_times[index]
      order_ids = TradeDataHolder.generateBuyOrderClientIDs(bear_symbol=self.bear_symbol,bull_symbol=self.bull_symbol,
                                project_root='HelloWorld')
      self.bullish['bull_buy_order_client_id']= order_ids['bull_buy_order_client_id']
      self.bearish['bear_buy_order_client_id']= order_ids['bear_buy_order_client_id']
      TradeDataHolder.recordAcquisitionTransaction(robot=None,bullish=self.bullish,bearish=self.bearish)
      index = index+1
  
  #
  # Make one Pair purchase and perform a Sale of the Bear
  #
  #@unittest.skip("Taking a break now")
  def testBuyPairSellBear(self):
    bull_data = TradeDataHolder.objects.get(buy_order_client_id=self.bullish["bull_buy_order_client_id"])    
    bear_data = TradeDataHolder.objects.get(buy_order_client_id=self.bearish["bear_buy_order_client_id"])
    self.assertEqual(bear_data.isValid(),True) 
    self.assertEqual(bull_data.isValid(),True) 

    sale_order = dict()
    sale_order['sell_order_client_id']= bear_data.getSellClientOrderID()
    sale_order['buy_order_client_id']= bear_data.getBuyClientOrderID()
    sale_order['sell_date'] = datetime.datetime.now(getTimeZoneInfo())
    sale_order['sell_price'] = 6.95

    bear_data = TradeDataHolder.recordDispositionTransaction(robot=None,order=sale_order)
    self.assertEqual(bear_data.isValidAfterSale(),True) 
    self.assertEqual(bear_data.isRealized(), True) 
    self.assertEqual(bear_data.isUnRealized(), False) 
    self.assertEqual(bull_data.isRealized(), False) 
    self.assertEqual(bull_data.isUnRealized(), True) 

  #
  # Purchase Pair, sell Bull
  #
  def testBuyPairSellBull(self):
    bull_data = TradeDataHolder.objects.get(buy_order_client_id=self.bullish["bull_buy_order_client_id"])    
    bear_data = TradeDataHolder.objects.get(buy_order_client_id=self.bearish["bear_buy_order_client_id"])
    self.assertEqual(bear_data.isValid(),True) 
    self.assertEqual(bull_data.isValid(),True)     
    
    sale_order = dict()
    sale_order['sell_order_client_id']= bull_data.getSellClientOrderID()
    sale_order['buy_order_client_id']= bull_data.getBuyClientOrderID()
    sale_order['sell_date'] = datetime.datetime.now(getTimeZoneInfo())
    sale_order['sell_price'] = 126.95
    bull_data = TradeDataHolder.recordDispositionTransaction(robot=None,order=sale_order)
    self.assertEqual(bull_data.isValidAfterSale(),True) 
    self.assertEqual(bull_data.isRealized(), True) 
    self.assertEqual(bull_data.isUnRealized(), False) 
    self.assertEqual(bear_data.isRealized(), False) 
    self.assertEqual(bear_data.isUnRealized(), True) 

    sale_order = dict()
    sale_order['sell_order_client_id']= bear_data.getSellClientOrderID()
    sale_order['buy_order_client_id']= bear_data.getBuyClientOrderID()
    sale_order['sell_date'] = datetime.datetime.now(getTimeZoneInfo())
    sale_order['sell_price'] = 6.95

    bear_data = TradeDataHolder.recordDispositionTransaction(robot=None,order=sale_order)
    self.assertEqual(bear_data.isValidAfterSale(),True) 
    self.assertEqual(bear_data.isRealized(), True) 
    self.assertEqual(bear_data.isUnRealized(), False) 


  # Sell both Sides. The Bull and the Bear.
  # Validate that all data is correct
  #
  def testBuyPairSellBoth(self):
    bull_data = TradeDataHolder.objects.get(buy_order_client_id=self.bullish["bull_buy_order_client_id"])    
    bear_data = TradeDataHolder.objects.get(buy_order_client_id=self.bearish["bear_buy_order_client_id"])
    
    sale_order = dict()
    sale_order['sell_order_client_id']= bull_data.getSellClientOrderID()
    sale_order['buy_order_client_id']= bull_data.getBuyClientOrderID()
    sale_order['sell_date'] = datetime.datetime.now(getTimeZoneInfo())
    sale_order['sell_price'] = 126.95
    bull_data = TradeDataHolder.recordDispositionTransaction(robot=None,order=sale_order)
    self.assertEqual(bull_data.isValidAfterSale(),True) 
    self.assertEqual(bull_data.isRealized(), True) 
    self.assertEqual(bull_data.isUnRealized(), False) 

#
# Generating OrderClientIDs for Buy, Sell and Root.
#
#@unittest.skip("Taking a break now")
class GenerateBuySellOrderClientIDsTestCase(TestCase):
  testname='Generate Buy and Sell order Client IDs'
  bull_symbol = 'TQQQ'
  bear_symbol = 'SQQQ'  

  @classmethod 
  def setUpTestData(self):
    if shouldUsePrint():
      print("Setting up {0}".format(self.testname))

    self.buy_order_ids=TradeDataHolder.generateBuyOrderClientIDs(project_root='project_name',
          bull_symbol=self.bull_symbol,bear_symbol=self.bear_symbol)

    self.sell_order_ids=TradeDataHolder.generateSellOrderClientIDs(project_root='project_name',
          bull_symbol=self.bull_symbol,bear_symbol=self.bear_symbol)

  #@unittest.skip("Taking a break now")
  def testGenerateBuyClientOrderIDs(self):
    # Generate Special Data
    bull_id = self.buy_order_ids['bull_buy_order_client_id']
    bear_id = self.buy_order_ids['bear_buy_order_client_id']

    self.assertNotEqual(bull_id,bear_id)
    bull_root = bull_id.replace('_buy_','').replace(self.bull_symbol,'')
    bear_root = bear_id.replace('_buy_','').replace(self.bear_symbol,'')
    self.assertEqual(bull_root,bear_root)

  #@unittest.skip("Taking a break now")
  def testGenerateSellClientOrderIDs(self):
    bull_id = self.sell_order_ids['bull_sell_order_client_id']
    bear_id = self.sell_order_ids['bear_sell_order_client_id']
    self.assertNotEqual(bull_id,bear_id)
    bull_root = bull_id.replace('_sell_','').replace(self.bull_symbol,'')
    bear_root = bear_id.replace('_sell_','').replace(self.bear_symbol,'')
    self.assertEqual(bull_root,bear_root)

#
# Several Acquisitions can be recorded
#
#@unittest.skip("Taking a break now")
class BuySeveralPairsTestCase(TestCase):
  testname= 'Buy Several Pairs Test Case'
  bull_json1 ='{"symbol":"TQQQ","price":126,"qty":10,"bull_buy_order_client_id":"a_buy_TQQQ","date":"2020-08-03 04:00:00-04:00"}'
  bear_json1 ='{"symbol":"SQQQ","price":5.5,"qty":170,"bear_buy_order_client_id":"a_buy_SQQQ","date":"2020-08-03 04:00:00-04:00"}'
  bull_json2 ='{"symbol":"TQQQ","price":126.5,"qty":9,"bull_buy_order_client_id":"b_buy_TQQQ","date":"2020-08-03 04:00:00-04:00"}'
  bear_json2 ='{"symbol":"SQQQ","price":5.4,"qty":171,"bear_buy_order_client_id":"b_buy_SQQQ","date":"2020-08-03 04:00:00-04:00"}'
  bull_json3 ='{"symbol":"TQQQ","price":127,"qty":9,"bull_buy_order_client_id":"c_buy_TQQQ","date":"2020-08-03 04:00:00-04:00"}'
  bear_json3 ='{"symbol":"SQQQ","price":5.3,"qty":172,"bear_buy_order_client_id":"c_buy_SQQQ","date":"2020-08-03 04:00:00-04:00"}'
  bull1 = json.loads(bull_json1)
  bear1 = json.loads(bear_json1)
  bull2 = json.loads(bull_json2)
  bear2 = json.loads(bear_json2)
  bull3 = json.loads(bull_json3)
  bear3 = json.loads(bear_json3)
  buy_date = datetime.datetime.now(getTimeZoneInfo())

  @classmethod 
  def setUpTestData(self):
    if shouldUsePrint():
      print("Setting up {0}".format(self.testname))
    TradeDataHolder.recordAcquisitionTransaction(robot=None,bullish=self.bull1,bearish=self.bear1)
    TradeDataHolder.recordAcquisitionTransaction(robot=None,bullish=self.bull2,bearish=self.bear2)
    TradeDataHolder.recordAcquisitionTransaction(robot=None,bullish=self.bull3,bearish=self.bear3)

  #@unittest.skip("Taking a break now")
  def testSeveralBuysDataPair(self):
    bull_data1 = TradeDataHolder.objects.get(buy_order_client_id=self.bull1["bull_buy_order_client_id"])    
    bear_data1 = TradeDataHolder.objects.get(buy_order_client_id=self.bear1["bear_buy_order_client_id"])
    bull_data2 = TradeDataHolder.objects.get(buy_order_client_id=self.bull2["bull_buy_order_client_id"])    
    bear_data2 = TradeDataHolder.objects.get(buy_order_client_id=self.bear2["bear_buy_order_client_id"])
    bull_data3 = TradeDataHolder.objects.get(buy_order_client_id=self.bull3["bull_buy_order_client_id"])    
    bear_data3 = TradeDataHolder.objects.get(buy_order_client_id=self.bear3["bear_buy_order_client_id"])
    self.assertEqual(bear_data1.isValid(),True) 
    self.assertEqual(bull_data1.isValid(),True)     
    self.assertEqual(bear_data2.isValid(),True) 
    self.assertEqual(bull_data2.isValid(),True)     
    self.assertEqual(bear_data3.isValid(),True) 
    self.assertEqual(bull_data3.isValid(),True)     

#
# Validate Status related and financial related functions
#
#@unittest.skip("Taking a break now")
class SimpleBuyPairTestCase(TestCase):
  testname = 'Simple Buy Pair Test Case'
  current_times=['2020-08-03 04:00:00-04:00']
  bull_prices=[126]
  bear_prices=[29.4]
  bull_symbol = 'TQQQ'
  bear_symbol = 'SQQQ'
  
  @classmethod 
  def setUpTestData(self):
    if shouldUsePrint():
      print("Setting up {0}".format(self.testname))

    index = 0
    self.bullish = dict()
    self.bearish = dict()
    for x in self.current_times:
      self.bullish['symbol']=self.bull_symbol
      self.bullish['price']=self.bull_prices[index]
      self.bullish['qty']=10
      self.bullish['date']=self.current_times[index]

      self.bearish['symbol']=self.bear_symbol
      self.bearish['price']=self.bear_prices[index]
      self.bearish['qty']=35
      self.bearish['date']=self.current_times[index]
      order_ids = TradeDataHolder.generateBuyOrderClientIDs(bear_symbol=self.bear_symbol,bull_symbol=self.bull_symbol,
                                project_root='hello_world')
      self.bullish['bull_buy_order_client_id']= order_ids['bull_buy_order_client_id']
      self.bearish['bear_buy_order_client_id']= order_ids['bear_buy_order_client_id']
      TradeDataHolder.recordAcquisitionTransaction(robot=None,bullish=self.bullish,bearish=self.bearish)
      index = index+1
  

  #@unittest.skip("Taking a break now")
  def testSingleBuyPair(self):
    bull_data = TradeDataHolder.objects.get(buy_order_client_id=self.bullish["bull_buy_order_client_id"])    
    bear_data = TradeDataHolder.objects.get(buy_order_client_id=self.bearish["bear_buy_order_client_id"])

    #Sanity Check for a simple entry of bull and bear ...
    #Peer Data MUST exist. And identifiable by order_client_id
    self.assertEqual(bull_data.isValid(),True)  
    self.assertEqual(bear_data.isValid(),True)  
    self.assertEqual(bull_data.hasPeerEntry(),True)  
    self.assertEqual(bear_data.hasPeerEntry(),True) 

    #Validity Functions : Both Bear and Bull are Unrealized. Values should be -1
    self.assertEqual(bear_data.isRealized(), False) 
    self.assertEqual(bear_data.isUnRealized(), True) 

    self.assertEqual(bull_data.isRealized(), False) 
    self.assertEqual(bull_data.isUnRealized(), True) 

    #Financial Functions
    self.assertEqual(bull_data.getUnRealizedValue(current_price=126),1260.0)  
    self.assertEqual(bear_data.getUnRealizedValue(current_price=28),980.0)  
    self.assertEqual(bull_data.getRealizedValue(),0)  
    self.assertEqual(bear_data.getRealizedValue(),0)  

#
# This test case cover invalid data scenarios:
# Invalid symbols, Invalid Price, Invalid quantity, Invalid Client_order_id, 
# Bull without a Bear and vice versa
#@unittest.skip("Taking a break now")
class InvalidScenariosTestCase(TestCase):
  testname="InvalidScenariosTestCase"

  buy_date = datetime.datetime.now(getTimeZoneInfo())

  bull_json_empty_symbol ='{"symbol":"","price":126,"qty":10,"bull_buy_order_client_id":"a_buy_TQQQ"}'
  bear_json_empty_symbol ='{"symbol":"","price":5.5,"qty":170,"bear_buy_order_client_id":"a_buy_SQQQ"}'
  bull_empty = json.loads(bull_json_empty_symbol)
  bear_empty = json.loads(bear_json_empty_symbol)

  bull_json_bad_price ='{"symbol":"TQQQ","price":0,"qty":10,"bull_buy_order_client_id":"a_buy_TQQQ"}'
  bear_json_bad_price ='{"symbol":"SQQQ","price":0,"qty":170,"bear_buy_order_client_id":"a_buy_SQQQ"}'
  bull_b_p = json.loads(bull_json_bad_price)
  bear_b_p = json.loads(bull_json_bad_price)

  bull_json_negative_price ='{"symbol":"TQQQ","price":-1,"qty":10,"bull_buy_order_client_id":"a_buy_TQQQ"}'
  bear_json_negative_price ='{"symbol":"SQQQ","price":-5,"qty":170,"bear_buy_order_client_id":"a_buy_SQQQ"}'
  bull_n_p = json.loads(bull_json_negative_price)
  bear_n_p = json.loads(bear_json_negative_price)

  bull_json_invalid_quantity ='{"symbol":"TQQQ","price":120,"qty":0,"bull_buy_order_client_id":"a_buy_TQQQ"}'
  bear_json_invalid_quantity ='{"symbol":"SQQQ","price":6,"qty":0,"bear_buy_order_client_id":"a_buy_SQQQ"}'
  bull_i_q = json.loads(bull_json_invalid_quantity)
  bear_i_q = json.loads(bull_json_invalid_quantity)

  bull_json_invalid_cID ='{"symbol":"TQQQ","price":120,"qty":10,"bull_buy_order_client_id":"b_"}'
  bear_json_invalid_cID ='{"symbol":"SQQQ","price":6,"qty":170,"bear_buy_order_client_id":"bb_"}'
  bull_i_cID = json.loads(bull_json_invalid_cID)
  bear_i_cID = json.loads(bear_json_invalid_cID)

  @classmethod 
  def setUpTestData(self):
    if shouldUsePrint():
      print("Setting up {0}".format(self.testname))

  #@unittest.skip("Taking a break now")
  def testEmptySymbol(self):
    try:
      TradeDataHolder.recordAcquisitionTransaction(robot=None,bullish=self.bull_empty,bearish=self.bear_empty)
    except InvalidTradeDataHolderException:
      self.assertEqual(True,True)
    else:
      self.assertEqual(False,True)
  
  #@unittest.skip("Taking a break now")
  def testBadPrice(self):
    try:
      TradeDataHolder.recordAcquisitionTransaction(robot=None,bullish=self.bull_b_p,bearish=self.bear_b_p)
    except InvalidTradeDataHolderException:
      self.assertEqual(True,True)
    else:
      self.assertEqual(False,True)

  #@unittest.skip("Taking a break now")
  def testNegativePrice(self):
    try:
      TradeDataHolder.recordAcquisitionTransaction(robot=None,bullish=self.bull_n_p,bearish=self.bear_n_p)
    except InvalidTradeDataHolderException:
      self.assertEqual(True,True)
    else:
      self.assertEqual(False,True)

  #@unittest.skip("Taking a break now")
  def testInvalidQuantity(self):
    try:
      TradeDataHolder.recordAcquisitionTransaction(robot=None,bullish=self.bull_i_q,bearish=self.bear_i_q)
    except InvalidTradeDataHolderException:
      self.assertEqual(True,True)
    else:
      self.assertEqual(False,True)

  #@unittest.skip("Taking a break now")
  def testInvalidClientID(self):
    try:
      TradeDataHolder.recordAcquisitionTransaction(robot=None,bullish=self.bull_i_cID,bearish=self.bear_i_cID)
    except InvalidTradeDataHolderException:
      self.assertEqual(True,True)
    else:
      self.assertEqual(False,True)