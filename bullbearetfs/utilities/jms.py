import os,os.path
import sys,time,logging,json
import stomp
from bullbearetfs.errors.customerrors import CustomError 
#from bullbearetfs.utilities.internalmessaging import InternalMessaging 


logger = logging.getLogger(__name__)
# 
# JMS Connection Parameters. To be moved to a configuration file.
#
s_queue = '{"hosts":"[(\'localhost\', 61613)]",\
            "user":"admin","password":"admin",\
            "destination":"com.siriusinnovate.robotmanager.system.queue"}'

m_queue = '{"hosts":"[(\'localhost\', 61613)]",\
            "user":"admin","password":"admin",\
            "destination":"com.siriusinnovate.robotmanager.market.queue"}'

r_queue = '{"hosts":"[(\'localhost\', 61613)]",\
            "user":"admin","password":"admin",\
            "destination":"com.siriusinnovate.robotmanager.robot.queue"}'

#
# Internal messaging makes sure all the messages 
# between consumers and producers follow a specific
# format.
# It also decodes the return message to understand which actions to take.
#
class InternalMessaging():

#
# Composes the message to be set on the producer
#
  def producer_system_shutdown(self):
    message = dict()
    message["family"] = "system"
    message["code"] = "shutdown"
    return json.dumps(message)

#
# Retrieves the message from the consumer
#
  def consumer_system_shutdown(self,message):
    message = message
    x = json.loads(message)
    return x

#
# JMS Listener. Listens to a variety of events.
#    Listens to Stock Market orders execution
#    Listens to System changes and safely shuts down the server
#    Listens to Robots events and safely performs the operations as needed
#    Listens to other events  
#
class RobotsEventsListener(stomp.ConnectionListener):
  def __init__(self,name):
  	super().__init__()
  	self.name = name

  def on_error(self, headers, message):
  	logger.error("Listener: '{0}' had an error: {1}".format(self.name,message))
  def on_message(self, headers, message):
  	logger.info("Listener: '{0}' had an information: {1}".format(self.name,message))

#
# This is the Wrapper for the JMSEvents Producers and Consumers
# If Producer, use type producer
# If Consumer, use type consumer
# 
class EggheadJMSConsumerWrapper(stomp.ConnectionListener):
  def __init__(self,name):
    self.name = name
    self.conn = stomp.Connection(host_and_ports = [('localhost', 61613)])
    self.conn.set_listener('', stomp.ConnectionListener())

  def connect_and_subscribe(self,destination):
    self.conn.connect('admin', 'admin', wait=True )
    self.conn.subscribe(destination=destination, id=1, ack='auto')

  def on_error(self, headers, message):
    logger.error("Listener: '{0}' had an error: {1}".format(self.name,message))

  def on_message(self, headers, message):
    logger.info("Listener: '{0}' had an information: {1}".format(self.name,message))
    self.retrieve_and_process(message)

  def retrieve_and_process(self,message):
    logger.info("Processing the message here ...")

  def disconnect(self):
    self.conn.disconnect()


class EggheadJMSProducerWrapper():
  def __init__(self,name):
    self.name = name
    self.conn = stomp.Connection(host_and_ports = [('localhost', 61613)])
    self.conn.set_listener('',  stomp.ConnectionListener())

  def connect_and_send(self,destination,message):
    self.conn.connect('admin','admin', wait=True )
    #self.conn.subscribe(destination=destination, id=1, ack='auto')
    self.conn.send(body=' '.join(message), destination=destination)

  def on_error(self, headers, message):
    logger.error("Listener: '{0}' had an error: {1}".format(self.name,message))

  def on_message(self, headers, message):
    logger.info("Listener: '{0}' had an information: {1}".format(self.name,message))
    self.retrieve_and_process(message)

  def disconnect(self):
    self.conn.disconnect()
    
#
# This is the Wrapper for the JMSEvents Producers and Consumers
# If Producer, use type producer
# If Consumer, use type consumer
# 
class EggheadJMSListenerWrapper():
  def __init__(self,type,name,message=''):
    if type == 'system':
      self.jms = json.loads(s_queue)
      self.name = name
    elif type == 'market':
      self.jms = json.loads(m_queue)
      self.name = name
    elif type == 'robot':
      self.jms = json.loads(r_queue)
      self.name = name
    elif type == 'shutdown':
      self.jms = json.loads(s_queue)
      self.name = name
      self.message = message
    else:
      logger.error("Error creating Listener. Wrong type was passed: {0}".format(type))

      return

    logger.debug("Values: {0} ".format(self.jms["hosts"]))
    self.conn = stomp.Connection(host_and_ports = [('localhost', 61613)])
    self.conn.set_listener('', RobotsEventsListener(name=self.name))
    self.conn.connect(self.jms["user"], self.jms["password"], wait=True )
    if type == 'shutdown':
      self.conn.send(body=' '.join(self.message), destination=self.jms["destination"])
    else:
      self.conn.subscribe(destination=self.jms["destination"], id=1, ack='auto')

  #def connect_and_subscribe(self):

#
# Disconnect from the Queue safely.
#
  def disconnect(self):
  	self.conn.disconnect()

  def isAlive(self):
  	return True