import os,os.path, sys,asyncio
import time, logging, json, datetime
import stomp
import alpaca_trade_api as tradeapi

logger = logging.getLogger(__name__)

#
# This is the base class for all ALPACA Requests.
# This class knows how to work with Alpaca Infrastructure
# https://paper-api.alpaca.markets
class AlpacaAPIBase():
 
  def __init__(self):
    self.tradeapi = tradeapi.REST()
    self.conn = tradeapi.stream2.StreamConn()

  def getAPI(self):
  	return self.tradeapi

  def getConn(self):
  	return self.conn 

  def isPaperAccount(self):
    paper_url = os.environ.get('APCA_API_BASE_URL')
    if paper_url.startswith('https://paper-api'):
      return True
    else:
      return False

  #
  # Add additional Security Layers on top of this call.
  #
  def isLiveAccount(self):
    return False

  def isValid(self):
  	return True

#
# This class accesses the Account and retrieve important information
#
class AccountInformation(AlpacaAPIBase):
  
  def getAccountStatus(self):
    return self.getAPI().get_account().status

  def accountIsBlockedByBrokerage(self):
    account = self.getAPI().get_account() 
    return account.trading_blocked
#
# Mimics and adapts the the Alpaca Positions API
#
class OpenPositions(AlpacaAPIBase):

  def getPositionByTickerSymbol(self,symbol):
    ticker = symbol
    return self.getAPI().get_position(symbol=ticker)

#
# Mimics and adapts the the Alpaca Positions API
#
class MarketClock(AlpacaAPIBase):

  def isOpen(self):
    return self.getAPI().get_clock().is_open  


#
# Mimics and adapts the the Alpaca Positions API
#
class QueryOrders(AlpacaAPIBase):

  def getBullBearBuyOrderByClientOrderID(self,payload):
    bull_order = self.getAPI().get_order_by_client_order_id(payload['bull_buy_client_order_id'])  
    bear_order = self.getAPI().get_order_by_client_order_id(payload['bear_buy_client_order_id'])  
    order_ids = dict()
    order_ids['bull_buy_client_order_id'] = bull_order
    order_ids['bear_buy_client_order_id'] = bear_order
    return order_ids  

  def getSellOrderByClientOrderID(self,payload):
    sell_order = self.getAPI().get_order_by_client_order_id(payload['sell_client_order_id'])  
    return sell_order


#
# Mimics and adapts the the Alpaca Positions API
#
class SellOrder(AlpacaAPIBase):

  def submitMarket(self,payload):
    try:
      self.getAPI().submit_order(symbol=payload['symbol'],qty=payload['qty'],side='sell',type='market',
                                 time_in_force=payload['time_in_force'],client_order_id=payload['sell_client_order_id'])

    except:
      logger.error("Error submitting a Sell Market Order to Alpaca.")
      return False
    return True

  def submitMarket(self,payload):
    try:
      self.getAPI().submit_order(symbol=payload['symbol'],qty=payload['qty'],side='sell',
                                 type='limit',limit_price=payload['limit_price'],
                                 time_in_force=payload['time_in_force'],client_order_id=payload['sell_client_order_id'])

    except:
      logger.error("Error submitting a Sell Limit Order to Alpaca.")
      return False
    return True

#
# Mimics and adapts the the Alpaca Positions API
#
class BullBearBuyOrder(AlpacaAPIBase):

  def submitMarket(self,payload):
    bull_payload = payload['bull_payload']
    bear_payload = payload['bear_payload']

    try:
      self.getAPI().submit_order(symbol=bull_payload['symbol'],qty=bull_payload['qty'],side='buy',type='market',
                                 time_in_force=payload['time_in_force'],client_order_id=bull_payload['buy_client_order_id'])

      sleep(payload['sleep_time'])

      self.getAPI().submit_order(symbol=bear_payload['symbol'],qty=bear_payload['qty'],side='buy',type='market',
                                 time_in_force=payload['time_in_force'],client_order_id=bear_payload['buy_client_order_id'])    
    except:
      logger.error("Error submitting a Buy Market Order to Alpaca.")
      return False
    return True 

  def submitLimit(self,payload):
    bull_payload = payload['bull_payload']
    bear_payload = payload['bear_payload']
    try:
      self.getAPI().submit_order(symbol=bull_payload['symbol'],qty=bull_payload['qty'],side='buy',
                                 type='limit', limit_price=bull_payload['limit_price'],
                                 time_in_force=payload['time_in_force'],client_order_id=bull_payload['buy_client_order_id'])

      sleep(payload['sleep_time'])

      self.getAPI().submit_order(symbol=bear_payload['symbol'],qty=bear_payload['qty'],side='buy',
                                 type='limit',limit_price=bull_payload['limit_price'],
                                 time_in_force=payload['time_in_force'],client_order_id=bear_payload['buy_client_order_id'])    
    except:
      logger.error("Error submitting a Buy Limit Order to Alpaca.")
      return False
    return True 

