import os,os.path
import sys,asyncio
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'etfs.settings')
import django
django.setup()
import pandas as pd
import alpaca_trade_api as tradeapi
import time,logging,
from dateutil.parser import *
from os import path

from asgiref.sync import async_to_sync
from asgiref.sync import sync_to_async

from bullbearetfs.models import  StartupStatus, EquityTradingRobot
from bullbearetfs.utilities.jms import EggheadJMSListenerWrapper
from bullbearetfs.utilities.alpaca import AlpacaAPIBase, AlpacaLastTrade
from bullbearetfs.robot.models import ETFAndReversePairRobot,TradeDataHolder, RoundTrip
"""
  TODO: Describe the Module here ...

  List the classes of the module here
"""

logger = logging.getLogger(__name__)

#
# Robot Manager Class.
#  This class is responsible for managing the Runtime Lifecycle of Robots as they execute trades
# against the Trading APIs
#
class RobotManager(AlpacaAPIBase):
  
   
  def disconnect_components(self):
  	if self.systemsEventsListener.isAlive():
  		self.systemsEventsListener.disconnect()
  	if self.robotsEventsListener.isAlive():
  		self.robotsEventsListener.disconnect()
  	if self.marketEventsListener.isAlive():
  		self.marketEventsListener.disconnect()

  	return True

  
#
# Initialize all the components required
#
  def initialize_components(self):

    # Logging, Error messages, ... etc
    self.initialize_environment()

    # Make sure I have access to tables and such
    self.initialize_django()

    # Make sure I have access to my brokerage account
    self.initialize_brokerage()
  	
    # Make sure to connect to my Active MQ system
    self.initialize_ActiveMQ()


    # Websocket protocols to listen to orders events and Live Quotes (Polygon.io)
    # Also needs to subscribe to Portfolio events when money (cash position) changes.
    self.initialize_quotes_streaming()

    # Make sure there aren't any orders that were missed while offline
   # self.synchronizeOrders()

    # Sent the message that the server is started.

  #
  # All the Queues should already exist
  # com.siriusinnovate.robotmanager.system.queue
  # com.siriusinnovate.robotmanager.market.queue
  # com.siriusinnovate.robotmanager.robots.queue
  #
  def initialize_ActiveMQ(self):
    self.systemsEventsListener = EggheadJMSListenerWrapper(type="system",name="Operating System Listener")
    self.robotsEventsListener = EggheadJMSListenerWrapper(type="robot",name = " Robots Events listener")
    self.marketEventsListener = EggheadJMSListenerWrapper(type="market", name = "Market Events Listener")

#
# Not yet sure what to do here.
# Check if the environment variables needed are all available.
# JMS, Database, Alpaca, ... others ...
# Should this be a config file?
  def initialize_environment(self):
    logger.info("Initializing the Infrastructure.")
    if "APCA_API_BASE_URL" in os.environ:
      pass
    else:
      logger.error("Unable to locate Variable. {0}".format('APCA_API_BASE_URL'))

    return True

#
# Create a table with Server start time and server stop time
# Upon every restart, I will publish the last restart ...etc
# Read from a started table
# Write into a Startup Table. Know about the uptime of the system.
  def initialize_django(self):
    logger.info("Initializing Django.")
    #startup = StartupStatus()
    #self.startup = startup.save()

    return True

  #
  # Connects to the Brokerage. Check that the Portolio is valid.
  # Synchronize to see if there are orders that aren't filled.
  # Are all the Robots orders in synch with the portfolio?
  # Are all the positions and money in sync? I.e.: are budgets accurate for every Active Robot?
  def initialize_brokerage(self):
    logger.info("Initializing Connection to Brokerage.")
    clock = self.getAPI().get_clock()
    logger.info("Market Open? {0}".format(clock.is_open))
    account = self.getAPI().get_account()
    logger.info("Account Status: {0}.".format(account.status))
    return True

  # There are several areas we can listen to.
  # 1. Portfolio (account_updates)
  # 2. Trades (trade_updates): Same as orders
  def initialize_quotes_streaming(self):
    logger.info("Initializing Connection to Quote Streaming.")
    
    # Install the Trade Update Listener
    @self.conn.on(r'trade_update')
    async def handle_trade_updates(conn,channel,data):
      logger.info("A trade event was recorded. {0}".format(data.order.client_order_id))

    # Install the Trade Update Listener
    @self.conn.on(r'account_update')
    async def handle_account_updates(conn,channel,data):
      logger.info(" An account updates was noted. {0}".format(data.cash))

    return True


    #
    # Continue Trading 
  #
  def continueTrading(self):
    logger.info("Check Systems Queues")    
    logger.info("Check Systems Queues")    
    
    return True

  @classmethod 
  def setSymbols(self,all_symbols=[]):
    self.all_symbols = all_symbols

  @classmethod 
  def retrieveSymbols(self):

    return self.all_symbols

  @sync_to_async
  def getActiveTradingRobots(self,key=None,value=None):
    #Retrieve all active Robots
    #all_robots = EquityTradingRobot.objects.filter(active=True)
    all_robots = ETFAndReversePairRobot.objects.filter(enabled=True)

    #Print number of Robots
    logger.info("Number of Active Robots found: {0}".format(len(all_robots)))
    
    #Create the statement for execution
    statement = []
    symbols = []
    all_symbol_prices = dict()
    #alpaca = AlpacaLastTrade()

    #symbols_string =
      #symbol=robot.getSymbol()
    #  price=alpaca.getLastTrade(symbol=symbol)
    #  all_symbol_prices[symbol] = price
    
    for robot in all_robots:
      symbols.append(robot.getSymbol())
      symbols.append(robot.getBearishSymbol())
      symbols.append(robot.getBullishSymbol())

    self.setSymbols(all_symbols=symbols)

    logger.info("All Symbols: {0}".format(symbols))
    #logger.info("All Price Symbols: {0}".format(all_symbol_prices))

    logger.info("{0}".format(value))
    #Add Robots Events to the execution
    for robot in all_robots:
      statement.append(robot.AsyncPrepareTrades(key=value))

    return statement

###################################################################
#
# This is the main entry point.
# Everything runs off the RobotsManager class.
# This class doesn't store lots of data.
#
async def main(manager):
  manager.setSymbols(['TQQQ','SQQQ'])
  while manager.continueTrading():
    # Other jobs that need updated. I.e.: Updates of Stock Prices

    
    # Place all the trades from the Queues
    alpaca = AlpacaLastTrade()
    symbols = manager.retrieveSymbols()
    symbol_prices = dict()
    for symbol in symbols:
       #symbol_prices[symbol]=last_trade
      last_trade = alpaca.getLastTrade(symbol=symbol)
      print("last trade {0}".format(last_trade))
      symbol_prices[symbol]=last_trade.price
      timestamp_number = last_trade.timestamp
     # timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp_number)))
      timestampe=pd.to_datetime(timestamp_number)
      print("timestamp {0} type {1}".format(timestamp_number,timestampe))
      #pd.to_datetime
    symbol_prices['timestamp']=timestampe
    logger.info("Last Trade: price={0}".format(symbol_prices))
   
    # Update Market Information and Update the systmems
    # Get all active Robots. Each robot calls trade() function
    statement = await manager.getActiveTradingRobots(value=symbol_prices)

    

    # Await their returns
    results = await asyncio.gather(*statement)

    # Do your thing
    logger.info("Sleeping for 10 seconds ...")  
    time.sleep(10)
   

###################################################################
#
# This is the Main function.
#
if __name__ == "__main__":
  s = time.perf_counter()
  logger.info("\n\nThe Robot Manager Application was started.")
  manager = RobotManager()
  manager.initialize_components()
  asyncio.run(main(manager=manager))
  manager.disconnect_components()
  logger.info("The Robot Manager Application was stopped safely.")

  elapsed = time.perf_counter() - s
  print(f"{__file__} executed in {elapsed:0.2f} seconds.")


"""
@sync_to_async
def db_call():
    statement = []
    all_robots = EquityTradingRobot.objects.filter(active=True)
    for x in all_robots:
      #print(x.name)
      statement.append(x.trade())
    logger.info("DB Call.")
    return statement

async def main_works():

  while True:
    r = await db_call()
    await asyncio.sleep(10)
    await asyncio.gather(*r)
    ####  ==================

@sync_to_async
def db_call():
    statement = []
    all_robots = EquityTradingRobot.objects.filter(active=True)
    for x in all_robots:
      #print(x.name)
      statement.append(x.trade())
    logger.info("DB Call.")
    return statement

async def main_works():

  while True:
    r = await db_call()
    await asyncio.sleep(10)
    await asyncio.gather(*r)

####  ==================

#@async_to_sync
#async def async_function():
#  logger.info("In async function")
#
#
#sync_function = async_to_sync(async_function)
#
#async_function = sync_to_async(sync_function)
 #
 # Retrieve all Robots
 #
  def printAllRobots(self):
    all_robots = EquityTradingRobot.objects.filter().order_by('name')

    for x in all_robots:
      logger.info("Name: {0} pk={1}".format( x.name, x.pk))

 #
 # Retrieve all active Robots
 #
  def printAllActiveRobots(self):
    logger.info("Retrieving all active Robots. ")
    all_robots = EquityTradingRobot.objects.filter(active=True).order_by('name')

    for x in all_robots:
      logger.info("Name: {0} pk={1}".format( x.name, x.pk))

  def getAllInactiveRobots(self,**kwargs):
    pass

  #
  # Turn on all the listeners 
  #
  def startRobot(self,serverID):
    pass

  #
  # Turn on all the listeners to all the events
  #
  def startAllActiveRObots(self):
    pass
  #
  # Synchronize things like: Stock Splits, Portfolio changes
  #
  def nightlySynchronization(self):
    pass

  #
  # Uses JMS to listen to systems events
  # if the system was stopped, exit safely
  #
  def listenToSystemEvents(self):
    #
    # If systems event was caught, raise a ApplicationStoppedException
    return True

#
# What are Robots events? When a new robot comes online.
# When a new Robot goes offline.
# When a manual trigger is given to buy or sell instantaneously
# 
# A Robot can have acquisition events happen
# A Robot can have disposition events happen
# A Robot doesn't purchase directly. He triggers an event, and the Manager acts on the event.
  def listenToRobotsEvents():   
    logger.info("Listening to Robots Events")
    

#
# What are Brokerage Events?
# Brokerage Events are related to Portfolio Changes?
# Let's say Budgets are modified. A sale just happened and there is cash ...
# This will trigger a Robot to update its cash availability
  def listenToBrokerageEvents():
    logger.info("Listening to Brokerage Events")

#
# What are Markets Events?
# Market Events are related to Stock Prices Changes, and maybe volatility changes
# Market Events are related to Orders Changes
# 
  def listenToMarketsEvents():
    logger.info("Listening to Market Events")

  
#
# System Events are related to Shutdown on the System.
#
  def listenToSystemEvents():
    logger.info("Listening to System Events")

      #try:
      ##  self.listenToRobotsEvents()
      #  self.listenToMarketsEvents()
      #  self.listenToSystemEvents()
      #  self.listenToBrokerageEvents()
      #except ApplicationStoppedException as exception:
      #  logger.error("The Robot Manager Server was shut down safely: {0}".format(exception.message))
      #  break
      #except RobotFatalException as exception:
      #  logger.error("An error occured on the Robot Server: {0}".format(exception.message))
      #  break
      #except BrokerageFatalException as exception:
      #  logger.error("An error occured on the Brokerage: {0}".format(exception.message))
      #  break

"""
