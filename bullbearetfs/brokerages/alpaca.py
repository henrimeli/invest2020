import os,os.path, sys,asyncio
import time, logging, datetime
import alpaca_trade_api as tradeapi
import time, logging, json
from datetime import date

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

  # TODO:
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

  def __init__(self):
    super().__init__()

  def isValid(self):
    return super().isValid() 

  def isActive(self):
    return self.getAPI().get_account().status=='ACTIVE'

  def getAccountStatus(self):
    return self.getAPI().get_account().status

  def accountIsBlockedByBrokerage(self):
    account = self.getAPI().get_account() 
    return account.trading_blocked

  def getBuyingPower(self):
    return self.getAPI().get_account().buying_power

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
class AlpacaMarketClock(AlpacaAPIBase):

  def __init__(self):
    super().__init__()
    self.today = datetime.datetime.now().isoformat()
    self.yesterday =(date.today() + datetime.timedelta(days=-1)).isoformat()
    self.default_start_date =   datetime.date(2020,10,1).isoformat()

  def isOpen(self):
    return self.getAPI().get_clock().is_open  

  def getTradingCalendar(self,start_date=None,end_date=None):
    first_day = self.default_start_date if start_date==None else start_date
    last_day = self.yesterday if end_date==None else end_date
    calendar = self.getAPI().get_calendar(start=first_day,end=last_day)
    data = [{"start_date":(l.date).strftime("%Y-%m-%d")} for l in calendar]

    return data


#
# Mimics and adapts the the Alpaca.
# Gets the price of the last trade of a given symbol. 
# Difference between lastTrade() and lastQuote()
# Can the Polygon also give the quote?
# Can I get the quote on a given day? See historical data
class AlpacaLastTrade(AlpacaAPIBase):

  def getLastTrade(self,symbol):
    symbol = symbol
    return self.getAPI().get_last_trade(symbol=symbol)      

  def getLastQuote(self,symbol):
    symbol = symbol
    return self.getAPI().get_last_quote(symbol=symbol)      


#
# Mimics and adapts the the Alpaca Positions API
#
class QueryOrders(AlpacaAPIBase):

  def queryBullBearBuyOrderByClientOrderID(self,payload):
    bull_order = self.getAPI().get_order_by_client_order_id(payload['bull_buy_client_order_id'])  
    bear_order = self.getAPI().get_order_by_client_order_id(payload['bear_buy_client_order_id'])  
    order_ids = dict()
    order_ids['bull_order_result'] = bull_order
    order_ids['bear_order_result'] = bear_order
    return order_ids  

  def querySellOrderByClientOrderID(self,payload):
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

  def submitLimit(self,payload):
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

#
# Mimics and adapts the the Alpaca Polygon API
#
class AlpacaPolygon(AlpacaAPIBase):

  def __init__(self,payload=None):
    super().__init__() 
    if not payload is None:
     self.trading_unit = payload['trading_unit']
     self.resolution = payload['resolution']
     self.start_date = payload['start_date']
     self.end_date = payload['end_date'] 

  def listAllTickers(self):
    return self.getAPI().polygon.all_tickers()     

  def quotesToSave(self,symbol,trading_unit=None):
    if trading_unit is not None:
      self.trading_unit=trading_unit
    df = self.getAPI().polygon.historic_agg_v2(symbol, int(self.trading_unit), self.resolution, _from=self.start_date, to=self.end_date).df
    return df

  def quoteOfOpenDay(self,symbol, day='2020-01-02'):
    df = self.getAPI().polygon.historic_agg_v2(symbol, self.timeframe, self.resolution, _from=start, to=end).df
    return df

  def quoteOfCloseDay(self,symbol,day='2020-01-02'):
    df = self.getAPI().polygon.historic_agg_v2(symbol, self.timeframe, self.resolution, _from=start, to=end).df
    return df

  def historicalData(self,symbol):
    symbol = symbol
    return self.getAPI().polygon.historic_agg_v2(symbol, self.timeframe, self.resolution, 
                                                 _from=self.start, to=self.end).df
