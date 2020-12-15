
import datetime, time,logging, unittest
from django.test import TestCase
import dateutil.parser, xmlrunner
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, strToDatetime, shouldUsePrint, displayOutput,displayError
"""
  The tests module is used to host backend tests for the basic component.
  Below is the complete list of all the tests in this module:

  TestBasicComponentUseCase: These are all the backend tests for the Basic component
  TestBasicComponentUseCase2: These are all the backend tests for the Basic component

"""

logger = logging.getLogger(__name__)

#
#@unittest.skip("Taking a break now")
class TestBasicComponentUseCase1(TestCase):
  """
  The Class is used to validate the functionality .
  The following functions are implemented:

  testHomePage:

  testCreateRobotButton:

  testCreateStrategyButton:

  testListRobotsButton:

  testListStrategiesButton:
  """
  testname ='TestBasicComponentUseCase1'

  @classmethod 
  def setUpTestData(self):
    displayOutput(str="TODO: Setting up the test scenario: {0}".format(self.testname))
 
  def testFunction1(self):
    """
    This module is used to validate that we can find the home page button .
    """
    displayOutput("TODO: Testing Function1. ")
    self.assertEqual(True,True)
#
#@unittest.skip("Taking a break now")
class TestBasicComponentUseCase2(TestCase):
  testname ='TestBasicComponentUseCase2'

  @classmethod 
  def setUpTestData(self):
    displayOutput("str=Setting up {0}. ".format(self.testname))
 
  def testHomePage(self):
    displayOutput("TODO: Testing Function2")
    self.assertEqual(True,True)


if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)
