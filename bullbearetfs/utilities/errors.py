import os,os.path
import sys

#
# Customized Errors goes here  
#
class CustomError(Exception):
  pass

#
#
#
class ApplicationStoppedException(Exception):
  pass

class RobotFatalException(Exception):
  pass

class BrokerageFatalException(Exception):
  pass

class InvalidTradeDataHolderException(Exception):
  pass