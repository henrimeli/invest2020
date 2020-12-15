import os,os.path
import sys

"""
  TODO: Describe the Module here ...

  List the classes of the module here
"""

#
# Customized Errors goes here  
#
# Python Exception Reference Document: https://docs.python.org/3/tutorial/errors.html#tut-userexceptions
# Django Exception Reference Document: https://docs.djangoproject.com/en/3.1/ref/exceptions/
class CustomError(Exception):
  """
    TODO: This is the custom error class used by all.
  """
  pass

class CustomBackendError(CustomError):
  """
    TODO: Custom Backend Error
  """
#
#
#
class ApplicationStoppedException(Exception):
  pass

class RobotFatalException(CustomError):
  pass

class BrokerageFatalException(CustomError):
  pass

class InvalidTradeDataHolderException(Exception):
  pass

class NotImplementedError(CustomError):
  """
  This exception is thrown to show that a particular method in a abstract base class has been called.
  """
  pass

class CustomUIError(CustomError):
  """
    TODO: Create a custom UI Error
  """
  pass  