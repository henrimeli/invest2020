import os,os.path, sys,asyncio
import time, logging, datetime
import alpaca_trade_api as tradeapi
import time, logging, json
from datetime import date
from django import forms
from django.forms import ModelForm
from bullbearetfs.executionengine.models import ETFPairRobotExecution

"""
  This module contains all the forms needed for this Component
"""
class CustomerCreationForm(ModelForm):
  """
  This form is used to create a new Execution Instance.
  When a Backtest is run, a new Execution Instance is created and performed 
  """
  class Meta:
    model = ETFPairRobotExecution
    fields = ['creation_date','exec_start_date','exec_end_date','robot','result_data',
              'execution_name','execution_pace','visual_mode','execution_status' ]
    labels = {'creation_date':'Creation Date','exec_start_date':'Start Date','exec_end_date':'End Date',
              'execution_name':'Execution Name','execution_pace':' Execution Pace','visual_mode':'Visual Mode',
              'execution_status':'Execution Status'}
