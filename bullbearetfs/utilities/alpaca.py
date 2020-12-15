import os,os.path, sys,asyncio
import time, logging, json, datetime
from datetime import date
import alpaca_trade_api as tradeapi

logger = logging.getLogger(__name__)

#
# This is the base class for all ALPACA Requests.
# This class knows how to work with Alpaca Infrastructure
# https://paper-api.alpaca.markets
class AlpacaAPIBase():
 
  def __init__(self):
    try:
      self.tradeapi = tradeapi.REST()
      self.conn = tradeapi.stream2.StreamConn()
      self.valid = True
    except:
      print("Error connecting to Alpaca API")
      valid = False

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
    valid = False
    return True


#
# This class accesses the Account and retrieve important information
#
class AlpacaAccountInformation(AlpacaAPIBase):
  
  def getAccountStatus(self):
    return self.getAPI().get_account().status

  # Each Robot is assigned a weight of the Account.
  # Information about the Account will depend on the weight 
  # The Robot has on the account.
  def getWeightedAccountInformation(self,weight):
  	weight = weight
  	account = self.getAPI().get_account()
  	weighted = dict()
  	weighted['cash'] = float(account.cash) * weight 
  	weighted['buying_power'] = float(account.buying_power) * weight
  	weighted['daytrading_buying_power'] = float(account.daytrading_buying_power) * weight 

  	return json.dumps(weighted)

#
# Mimics and adapts the the Alpaca Assets API
#
class AlpacaAssetsInformation(AlpacaAPIBase):

  def getAllAssets(self):
    return self.getAPI().get_assets(status='active',asset_class='us_equity')  

  def getAssetByTickerSymbol(self,symbol):
  	ticker = symbol
  	return self.getAPI().get_asset(symbol=ticker)


#
# Mimics and adapts the the Alpaca Positions API
#
class AlpacaOpenPositions(AlpacaAPIBase):

  def listAllPositions(self):
    return self.getAPI().list_positions()  

  def getPositionByTickerSymbol(self,symbol):
  	ticker = symbol
  	return self.getAPI().get_position(symbol=ticker)


#
# Mimics and adapts the the Alpaca Positions API
#
class AlpacaMarketClock(AlpacaAPIBase):

  def __init__(self):
    self.today = date.today()
    self.yesterday =(date.today() + datetime.timedelta(days=-1)).isoformat()
    self.default_start_date =   datetime.date(2020,10,1).isoformat()

  def isOpen(self):
    return self.getAPI().get_clock().is_open  

  def getTradingCalendar(self,start_date=None,end_date=None,includes_today=False):
    count=1
    if start_date==None:
      start_date = datetime.date(2020,6,1).isoformat()
    if includes_today:
      count=0

    first_day = self.default_start_date if start_date==None else start_date
    last_day = self.default_start_date if start_date==None else start_date
    #start_date=(date.today() + datetime.timedelta(days=-count)).isoformat()
    #end_date=(date.today() + datetime.timedelta(days=-count)).isoformat()
    calendar = self.getAPI().get_calendar(start=first_day,end=last_day)
    data = [{"start_date":(l.date).strftime("%Y-%m-%d")} for l in calendar]

    return data

#
# Mimics and adapts the the Alpaca Watchlist API
#
class AlpacaWatchLists(AlpacaAPIBase):

  def getWatchlists(self):
    return self.getAPI().get_watchlists()    

  # Creates a watch list with name and array of symbols
  def createWatchlist(self,name,symbols):
    name = name
    tickers = symbols
    self.getAPI().create_watchlists(name=name, symbol=tickers)



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

#open the connection
#conn = something

# Define the function
#@conn.on(r'A$')
#async def testme(conn, channel, data):
#  ts = data.start
#  print ("Starting point is {0}".format(ts))
#
#channels = ['trade_update']
#symbol_channels = ['A.{}'.format()]
  
# Define the channels

#
# Mimics and adapts the the Alpaca streaming
#
class AlpacaStreaming(AlpacaAPIBase):

  def listAllOrdersStreaming(self):
  	#conn = tradeapi.stream2.StreamConn()
  	#client_orders = r'A$'
  	#@self.getConn().on(client_order_id)
  	#async def on_msg(conn, channel, data):
    #  print("I have received a message from Streaming. ")

    return self.getAPI().get_watchlists()    	


class AlpacaOrdersBuyETFAndReverse(AlpacaAPIBase):

  def submitMarketOrderETFAndReverse(self,symbol1,quantity1,symbol2,quantity2,client_order_id1,client_order_id2):
    etf = symbol1
    reverse = symbol2
    q_etf = quantity1
    q_reverse = quantity2
    
    client_order_id1 = client_order_id1
    client_order_id2 = client_order_id2
    self.getAPI().submit_order(symbol=etf,qty=q_etf,side='buy',type='market',time_in_force='gtc',client_order_id=client_order_id1)
    self.getAPI().submit_order(symbol=reverse,qty=q_reverse,side='buy',type='market',time_in_force='gtc',client_order_id=client_order_id2)    
    time.sleep(10)
    my_order_etf = self.getAPI().get_order_by_client_order_id(client_order_id1)  
    my_order_reverse = self.getAPI().get_order_by_client_order_id(client_order_id2)  
    temp = "{0}   {1}".format(my_order_etf,my_order_reverse)
    #temp.update(my_order_reverse)
    return temp  


#
# Mimics Simple Buy Orders (Buy Market, Buy limit ) on Alpaca
#
class AlpacaSimpleBuyOrders(AlpacaAPIBase):

  def submitMarketOrderGTC(self,symbol,quantity,client_order_id):
    ticker = symbol
    qty = quantity
    client_order_id = client_order_id
    self.getAPI().submit_order(symbol=ticker,qty=qty,side='buy',type='market',time_in_force='gtc',client_order_id=client_order_id)    	
    my_order = self.getAPI().get_order_by_client_order_id(client_order_id)  
    return my_order  

  def submitLimitOrderGTC(self,symbol,quantity,limit_price):
    ticker = symbol
    qty = quantity
    limit = limit_price
    return self.getAPI().submit_order(symbol=ticker,limit_price=limit,qty=qty,side='buy',type='market',time_in_force='gtc')    	

  def submitBuyMarketOrders(self,symbol,quantity,time_in_force):
    return self.getAPI().get_watchlists()    	

#
# Mimics Bracket Orders (Buy Market, Buy limit ) on Alpaca
#
class AlpacaBracketBuyOrders(AlpacaAPIBase):
  def getWatchlists(self):
    return self.getAPI().get_watchlists()    	


#
# Mimics and adapts the the Alpaca Watchlist API
#
class AlpacaAccountActivities(AlpacaAPIBase):

  def getWatchlists(self):
    return self.getAPI().get_watchlists()    	

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
# Mimics and adapts the the Alpaca Historical data API
#
class AlpacaPortfolioHistory(AlpacaAPIBase):

  # timestamp: 2020-08-03T09:30:00-04:00
  #
  #
  def getDailyBar(self,symbols,limit,start,end):
    symbols = symbols
    timeframe = 'day'
    limit = limit
    start = start
    end = end 
    barset = self.getAPI().get_barset(symbols=symbols,timeframe=timeframe,limit=limit,start=start)    	
    return self.processBarset(bar=barset[symbols],symbol=symbols,size=len(barset))

  # timestamp: 2020-08-03T09:30:00-04:00
  #
  def get15MinutesBar(self,symbols,limit,start,end):
    symbols = symbols
    timeframe = '15Min'
    limit = limit
    start = start
    end = end 
    barset = self.getAPI().get_barset(symbols=symbols,timeframe=timeframe,limit=limit,start=start)  
   	
    return self.processBarset(bar=barset[symbols],symbol=symbols,size=len(barset))

  def processBarset(self,bar,symbol,size):
    bar_i = bar
    symbol_i = symbol 
    size_i = size 
    info = dict()
    bar_high = list()
    bar_low = list()
    info['open'] = bar_i[0].o 
    info['close'] = bar_i[size_i-1].c
    for x in bar_i:
    	bar_high.append(x.h)
    	bar_low.append(x.l)
    highest = max(bar_high)
    lowest = min(bar_low)
    info['symbol']=symbol_i
    info['high'] = highest
    info['low'] = lowest
    info['per_open_close'] = 100 * ((bar_i[0].o  - bar_i[size_i-1].c) / bar_i[0].o )
    info['per_high_low'] = 100 * ((highest - lowest ) / highest )
    info['start_time' ]= bar_i[0].t.strftime('%Y-%m-%d : %H %M %S')
    info['end_time' ]= bar_i[size_i-1].t.strftime('%Y-%m-%d : %H %M %S')
    return json.dumps(info)


  # timestamp: 2020-08-03T09:30:00-04:00
  #
  def get5MinutesBar(self,symbols,limit,start,end):
    symbols = symbols
    timeframe = '5Min'
    limit = limit
    start = start
    end = end 
    barset = self.getAPI().get_barset(symbols=symbols,timeframe=timeframe,limit=limit,start=start) 

    return self.processBarset(bar=barset[symbols],symbol=symbol,size=len(barset))

  # timestamp: 2020-08-03T09:30:00-04:00
  #
  def get1MinuteBar(self,symbols,limit,start,end):
    symbols = symbols
    timeframe = '1Min'
    limit = limit
    start = start
    end = end 
    barset = self.getAPI().get_barset(symbols=symbols,timeframe=timeframe,limit=limit,start=start)     
    return self.processBarset(bar=barset[symbols],symbol=symbols,size=limit)

