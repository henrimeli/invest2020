
import datetime, time,logging, unittest
from django.test import TestCase
import dateutil.parser, xmlrunner
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, strToDatetime, shouldUsePrint, displayOutput,displayError

"""
  TODO: 
"""
logger = logging.getLogger(__name__)

#
#
#
@unittest.skip("TODO: Create this test ")
class TestRobotConditionals(TestCase):
  testname ='TestRobotConditionals'

  @classmethod 
  def setUpTestData(self):
    displayOutput(str="Setting up {0}".format(self.testname))
 
  def testInfrastructureFailure(self):
    displayOutput(str="TODO: Testing the Infrastructure Failure ")
    self.assertEqual(True,True)

  def testMarketCrashFailure(self):
    displayOutput(str="TODO: Testing the Market Crash Failure ")
    self.assertEqual(True,True)

  def testBrokerageFailure(self):
    displayOutput(str="TODO: Testing the Brokerage Failure ")
    self.assertEqual(True,True)

if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)
