import asyncio
from django.db import models
from django.db.models import Count, F, Value
from django.db.models import FloatField
from django.db.models import Sum,Avg,Max,Min
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.utils.timezone import datetime
from datetime import date
from django.utils import timezone
from django.contrib.auth.models import  User
import logging
import difflib 
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple,displayOutput,displayError,strToDatetime
from bullbearetfs.datasources.datasources import  BackTestArrayInfrastructure,BackTestFileInfrastructure, BackTestDatabaseInfrastructure

"""
  TODO: Describe the Module here ...

  List the classes of the module here
"""

logger = logging.getLogger(__name__)

######################## Classes for Robot Execution Engine ###############
#
# This class manages/manipulates the BackTest Execution Functionality through the lifecycle
# of an execution. It takes parameters from the UI (or configuration),
# Launches a test and watches it until completion. The parameters of the robot are stored and 
# can be retrieved and re-used later
#
class ETFPairBackTestRobotExecutionEngine():
  """
    TODO: This class manipulates the BackTest Execution Functionality through the lifecycle of 
    an execution.

    List of methods: 
  """
  def __init__(self,robot,executor_id,request=None, datasource=None):
    self.executor_id = executor_id
    self.request = request
    self.robot = robot
    self.datasource = datasource    

  #
  # Display Current Executor Information 
  #
  def printExecutorData(self):
    executor = ETFPairRobotExecution.objects.get(pk=self.executor_id)
    print("Executor: {}".format(executor))

  #
  # Compares The configuration parameters between two executions.
  # TODO: This still needs some work.
  #
  def compareExecutionResults(self,candidate):
    executor1 = ETFPairRobotExecution.objects.get(pk=self.executor_id)
    executor2 = ETFPairRobotExecution.objects.get(pk=candidate.id)
    diff = difflib.ndiff(executor1.getConfigurationData(),executor2.getConfigurationData())
    output_list = [li for li in diff if not li.startswith(' ')]
    return output_list

  #
  # Executes the BackTest against the given Robot and Datafeed.
  #
  def executeBackTest(self):
    user_name = 'Dummy User' if self.request==None else self.request.user.get_username()
    displayOutput("{} is executing Backtest with data:{}".format(user_name,self.executor_id))

    executor = ETFPairRobotExecution.objects.get(pk=self.executor_id)
    
    #Delete all entries made by this executor. 
    #Clear the Data from own executiondata class
    #clear data from TradeDataHolder class
    ETFPairRobotExecutionData.deleteExecutionRecords(robot_execution=executor)
    
    #Associate Executor to the Robot, Remove any data that might have been created prior by Execution Engine
    self.robot.setExecutionEngine(execution_engine=executor,purge_previous=True) 

    payload = self.robot.getSymbolsPairAsPayload()
    logger.info("Payload: {0}".format(payload))
  
    serialized = self.robot.getSerializedRobotObject()

    if isinstance(self.datasource,BackTestArrayInfrastructure):
      #Update the Executor Status to 'in progress', save the config_parameters
      executor.config_params = serialized
      print("Size = {} ".format(len(serialized)))
      executor.start_date=None 
      executor.end_date = None 
      executor.execution_status='in progress'
      executor.save()
     
      #Initialize the Datafeed Infrastructure
      backtest_data = self.datasource.getFeedData()

      #Launch the Run ...
      for feed in backtest_data:
        self.robot.prepareTrades(key=feed)
      
      #Upon completion, mark it as completed.
      executor.result_data = 'TODO: results go here.'
      executor.execution_status='completed'
      executor.save()

    elif isinstance(self.datasource,BackTestFileInfrastructure):
      #Update the Executor 
      executor.config_params = serialized
      executor.start_date=None 
      executor.end_date = None 
      executor.execution_status='in progress'
      executor.save()
     
      #Initialize the Datafeed Infrastructure
      backtest_data = self.datasource.getFeedData()
      #Launch the Run ...
      for feed in backtest_data:
        self.robot.prepareTrades(key=feed)
      
      #Upon completion, mark it as completed.
      executor.result_data = 'TODO: results go here.'
      executor.execution_status='completed'
      executor.save()

    elif isinstance(self.datasource,BackTestDatabaseInfrastructure):
      #Update the Executor 
      executor.config_params = serialized
      executor.execution_status='in progress'
      executor.save()
     
      #
      backtest_data = self.datasource.getFeedData(start_date=executor.exec_start_date,end_date=executor.exec_end_date)
      data_amount = len(backtest_data)
      logger.info("Test Data Size={}".format(data_amount))

      #Launch the Run ...
      for feed in backtest_data:
        payload=feed.getBasicInformation()
        self.robot.prepareTrades(key=payload)

      #Upon completion, mark it as completed.
      executor.result_data = 'TODO: results go here.'
      executor.execution_status='completed'
      executor.save()
    else:
      print("Executor type not found.... try again")

    return True 


  #
  # Lists all Executions that belong to this Robot.
  #
  def listAllExecutions(self):
    executors = ETFPairRobotExecution.objects.filter(robot=self.robot)
    return executors

  #
  # Clear the Backtest data
  #
  def clearBackTestData(self):
    executor = ETFPairRobotExecution.objects.get(pk=self.executor_id)
    ETFPairRobotExecutionData.deleteExecutionRecords(robot_execution=executor)
    #Associate Executor to the Robot, Remove any data that might have been created prior by Execution Engine
    self.robot.setExecutionEngine(execution_engine=executor,purge_previous=True) 

  #
  # Generate a report that can be easily consumed by command line and UI.
  # This report focuses on the Financial picture of all transactions.
  #
  def getExecEngineFinancialReport(self):
    executor = ETFPairRobotExecution.objects.get(pk=self.executor_id)
    results = ETFPairRobotExecutionData.objects.filter(execution=executor).order_by('trade_time')

    total_cost = 0
    buy_transactions = 0
    sell_transactions = 0
    exec_financial_report =dict()
    report_entry=[]
    for x in results:
      entry=self.robot.getEntryBasedOnOrderClientID(exec_engine_order_client_id=x.order_client_id)
      total_cost = total_cost + entry['cost']
      entry.update({'total_cost':total_cost})
      entry.pop('quantity',None)
      entry.pop('price',None)
      report_entry += [entry]
    
    #Create Summary Result 
    summary = dict()
    summary['total_cost'] = total_cost
    summary['transactions'] = len(results)
    exec_financial_report['summary']=summary
    exec_financial_report['entries']=report_entry
    return exec_financial_report 

  #
  # Generate a report that can be easily consumed by command line and UI.
  # This report focuses on the timelines based on time
  #
  def getExecEngineReplayReport(self):
    executor = ETFPairRobotExecution.objects.get(pk=self.executor_id)
    results = ETFPairRobotExecutionData.objects.filter(execution=executor).order_by('trade_time')
    total_cost = 0

    exec_replay_report =dict()
    report_entry=[]
    for x in results:
      entry=self.robot.getEntryBasedOnOrderClientID(exec_engine_order_client_id=x.order_client_id)
      total_cost = total_cost + entry['cost']
      entry.update({'total_cost':total_cost})
      report_entry += [entry]

    #Create Summary Result 
    summary = dict()
    summary['total_cost'] = total_cost
    summary['transactions'] = len(results)
    exec_replay_report['summary']=summary
    exec_replay_report['entries']=report_entry

    return exec_replay_report 

#
# This class records step by step information of any RobotExecution.
# Information will be replayed, if needed.
# Step by Step execution could be recorded in TradeDataHolder, but it wouldn't be 
# suited to also have configuration information. That's why this class is needed.
#
CHOICES_ACTIONS= (('buy','buy'),('sell','sell'))
class ETFPairRobotExecutionData(models.Model):
  execution = models.ForeignKey('ETFPairRobotExecution',on_delete=models.PROTECT,blank=True,null=True)
  trade_time = models.DateTimeField('date created',default=timezone.now) #This is the NOW time.
  exec_time = models.DateTimeField('date created',default=timezone.now)   #This is the time of the stock quote
  exec_action = models.CharField(max_length=10, choices = CHOICES_ACTIONS,default='buy') # Buy or Sell action. To expand and add protection
  exec_params = models.CharField(max_length=3500,default='', blank=True) #Which params were used
  cost_or_income = models.FloatField(default=0) #Monetary transaction: cost or income ( cost is negative, income is positive)
  order_client_id = models.CharField(max_length=100,blank=True,null=True) #Keeps track of transactions in the TradeDataHolder table

  def __str__(self):
    return "{} {} {} {} ".format(self.execution.id,self.exec_time,self.exec_action,self.order_client_id)

  @staticmethod
  def recordAcquisitionExecution(executor,exec_time,exec_params,cost,order_client_id):
    now = datetime.now(getTimeZoneInfo())
    action = 'buy'
    entry = ETFPairRobotExecutionData.objects.create(execution=executor,trade_time=now,exec_time=exec_time,
                                             exec_action=action,cost_or_income=cost,order_client_id=order_client_id)
    

  @staticmethod
  def recordDispositionExecution(executor,exec_time,exec_params,income,order_client_id):
    now = datetime.now(getTimeZoneInfo())
    action='sell'
    ETFPairRobotExecutionData.objects.create(execution=executor,trade_time=now,exec_time=exec_time,
                                             exec_action=action,cost_or_income=income,order_client_id=order_client_id)

  @staticmethod
  def deleteExecutionRecords(robot_execution):
    ETFPairRobotExecutionData.objects.filter(execution=robot_execution).delete()
    print("Deleted Previous Execution Records. {}".format(robot_execution))
#
# This class contains all the basic information about RobotExecutions such as name, parameters at the beginning 
# The Step by Step execution is kept in another file. 
# This class has a ForeignKey into the TradeHolder file, which matches actions with the execution. 
#
CHOICES_EXECUTION_PACE = (('slow','slow'),('medium','medium'),('fast','fast'))
CHOICES_STATUS_PACE = (('started','started'),('inprogress','inprogress'),('completed','completed'),('not started','not started'))
class ETFPairRobotExecution(models.Model):
  creation_date =  models.DateTimeField('date created',default=timezone.now) 
  exec_start_date = models.DateTimeField('date created',default=timezone.now) 
  exec_end_date = models.DateTimeField('date created',default=timezone.now) 
  robot = models.ForeignKey('ETFAndReversePairRobot',on_delete=models.PROTECT,blank=True,null=True)
  config_params = models.CharField(max_length=3500,default='', blank=True)
  result_data = models.CharField(max_length=100,default='', blank=True)
  execution_name = models.CharField(max_length=100,default='', blank=True)
  execution_pace = models.CharField(max_length=20, choices = CHOICES_EXECUTION_PACE,default='medium')
  visual_mode=models.BooleanField(default=False) # Visual Mode?
  execution_status = models.CharField(max_length=20, choices = CHOICES_STATUS_PACE,default='not started')
  dispose_all_on_close=models.BooleanField(default=False) # Sell all Positions on the last trade?

  def __str__(self):
    basic_1 = "Engine_ID={}. Name={}. Start={}. End={}. ".format(self.pk, self.execution_name,self.exec_start_date,self.exec_end_date)
    basic_2 = "visual_mode={}. execution_status={}. execution_pace={}. ".format(self.visual_mode,self.execution_status,self.execution_pace)
    basic_3 = "Robot name={}. Result_Data={}.".format(self.robot.name,self.result_data)
    basic_4 = "Config={}".format(self.config_params)
    return "{}. \n {}. \n {} \n{}".format(basic_1,basic_2,basic_3,basic_4)

  def getConfigurationData(self):
    return self.config_params

  def getSummaryReportData(self):
    return self.result_data

  @staticmethod
  def createRobotExecution(exec_start_date,exec_end_date,robot,config_params='',result_data='',execution_pace='fast',
  	                       execution_name=None, visual_mode=False,dispose_all_on_close=False):

    now = datetime.now(getTimeZoneInfo())
    start_date = now if (exec_start_date==None) else exec_start_date
    end_date = now if (exec_end_date == None) else exec_end_date
    exec_name = execution_name if (execution_name != None) else now.strftime("{0}_%Y%m%d-%H-%M-%S.%f".format(robot.name))

    ex = ETFPairRobotExecution.objects.create(creation_date=now,exec_start_date=start_date,exec_end_date=end_date,
    	                                 robot=robot,config_params=config_params,result_data=result_data,execution_name=exec_name,
    	                                 execution_pace=execution_pace,visual_mode=visual_mode,
    	                                 dispose_all_on_close=dispose_all_on_close,execution_status='not started')
    return ex
