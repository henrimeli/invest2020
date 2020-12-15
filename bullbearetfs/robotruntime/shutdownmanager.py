import os,os.path
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'etfs.settings')
import django
django.setup()

import alpaca_trade_api as tradeapi
import time
import sqlite3
from os import path
import logging
import stomp

from bullbearetfs.utilities.jms import EggheadJMSListenerWrapper
from bullbearetfs.utilities.internalmessaging import InternalMessaging

logger = logging.getLogger(__name__)

#
# Robot Shutdown Class.
#  This class is responsible for holding the code for shutting down the 
# Robot Manager Safely 
#
class ShutDownServerManager():
  
#
# Initialize all the components required
#
  def initialize_components(self):
  	
    self.initialize_and_post()
 
  #
  # Create connection to system manager and place a message
  # com.siriusinnovate.robotmanager.system.queue
  #
  def initialize_ActiveMQ(self):
    message = InternalMessaging()
    self.systemsEventsListener = EggheadJMSListenerWrapper(type="shutdown",name="Application Shutdown Request",\
    	                         message=message.producer_system_shutdown())

###################################################################
#
# This is the main entry point.
# Places a messages to JMS for a safe shutdown.
# 
#
def main():
  logger.info("The Shutdown Application was started.")
  shutdown = ShutDownServerManager()
  #shutdown.initialize_and_post()
  logger.info("The Shutdown Application completed safely.")


if __name__ == "__main__":
  main()

