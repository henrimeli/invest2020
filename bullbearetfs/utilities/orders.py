import os,os.path
import sys,asyncio
import time
import logging
import json
import datetime
from django.utils import timezone
from bullbearetfs.market.models import WebsiteContactPage
from bullbearetfs.errors.customerrors import CustomError 
from bullbearetfs.utilities.alpaca import AlpacaAPIBase , AlpacaPolygon
import alpaca_trade_api as tradeapi


 
class RobotSellOrderExecutor():

  def __init__(self,sell_order):
    self.sell_order = sell_order 

  def executeAndGetResults(self,use_alpaca,use_historical,sell_price):
    if use_alpaca and not use_historical:
      print("Can't use Alpaca live data now")
    elif use_alpaca and use_historical:
      print("Not yet set up")
    else:
      sell_order = dict()
      sell_order['symbol']=self.sell_order['symbol']
      sell_order['client_order_id']= self.sell_order['client_order_id']
      sell_order['date']= datetime.datetime.now(timezone.utc)
      sell_order['qty']= self.sell_order['qty']
      sell_order['price']= sell_price

    return sell_order

#
# A BuyOrderExecutor is responsible to dispatching the order to the appropriate
# Backend System and processing the results upon completion.
#
class RobotBuyOrderExecutor():

  def __init__(self,buy_order,order_method):
    self.buy_order = buy_order 
    self.order_method = order_method
    self.alpaca = AlpacaPolygon()

  def order_method_alpaca_historical(self):
    #bull_price = self.alpaca.quoteOfOpenDay(symbol=self.buy_order['bull_symbol'],day='2020-08-14')
    #bear_price = self.alpaca.quoteOfOpenDay(symbol=self.buy_order['bear_symbol'],day='2020-08-14')
    bull_price = 120
    bear_price = 4
    bull_filled_share_price = bull_price
    bear_filled_share_price = bear_price

    bull_order = dict()
    bull_order['symbol']=self.buy_order['bull_symbol']
    bull_order['bull_buy_order_client_id']= self.buy_order['bull_buy_order_client_id']
    bull_order['date']= datetime.datetime.now(timezone.utc)
    bull_order['qty']= self.buy_order['bull_qty']
    bull_order['price']= bull_filled_share_price

    bear_order = dict()
    bear_order = dict()
    bear_order['symbol']=self.buy_order['bear_symbol']
    bear_order['bear_buy_order_client_id']= self.buy_order['bear_buy_order_client_id']
    bear_order['date']= datetime.datetime.now(timezone.utc)
    bear_order['qty']= self.buy_order['bear_qty']
    bear_order['price']= bear_filled_share_price
    
    order_result = dict()
    order_result['bull'] = bull_order
    order_result['bear'] = bear_order

    return order_result

  def order_method_alpaca_live_api(self):
    pass

  def order_method_alpaca_paper(self):
    pass 

  def order_method_dummy_data(self):
    bull_filled_share_price = 123.56 
    bear_filled_share_price = 5.59
    bull_order = dict()
    bull_order['symbol']=self.buy_order['bull_symbol']
    bull_order['bull_buy_order_client_id']= self.buy_order['bull_buy_order_client_id']
    bull_order['date']= datetime.datetime.now(timezone.utc)
    bull_order['qty']= self.buy_order['bull_qty']
    bull_order['price']= bull_filled_share_price

    bear_order = dict()
    bear_order = dict()
    bear_order['symbol']=self.buy_order['bear_symbol']
    bear_order['bear_buy_order_client_id']= self.buy_order['bear_buy_order_client_id']
    bear_order['date']= datetime.datetime.now(timezone.utc)
    bear_order['qty']= self.buy_order['bear_qty']
    bear_order['price']= bear_filled_share_price
    
    order_result = dict()
    order_result['bull'] = bull_order
    order_result['bear'] = bear_order

    return order_result

  def executeAndGetResults(self):
  	if self.order_method in 'alpaca_live_api':
  	  return self.order_method_alpaca_live_api()
  	elif self.order_method in 'alpaca_paper':
  	  return self.order_method_alpaca_paper()
  	elif self.order_method in 'dummy_data':
  	  return self.order_method_dummy_data()
  	elif self.order_method == 'alpaca_historical':
  	  return self.order_method_alpaca_historical()
