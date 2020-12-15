
import datetime, time,logging, unittest
from django.test import TestCase
import dateutil.parser, xmlrunner
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, strToDatetime, shouldUsePrint, displayOutput,displayError

"""
  TODO: Describe this module
"""

logger = logging.getLogger(__name__)

#
@unittest.skip("TODO: Not yet implemented.")
class TestBaseCustomError(TestCase):
  """
    This class validates the Base Custom Errors
  """
  testname ='TestBaseCustomError'

  @classmethod 
  def setUpTestData(self):
    displayOutput(str="Setting up {0}".format(self.testname))
 
  def testCustomError(self):
    displayOutput("Testing the custom error Scenario")
    self.assertEqual(True,True)

#
@unittest.skip("TODO: Not yet implemented.")
class TestExtendedCustomErrors(TestCase):
  """
    This class validates the Extended Custom Errors
  """
  testname ='TestExtendedCustomErrors'

  @classmethod 
  def setUpTestData(self):
    displayOutput(str="Setting up {0}".format(self.testname))
 
  def testExtendedCustomError(self):
    displayOutput(str="Testing the Home Page Scenario")
    self.assertEqual(True,True)

if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)
