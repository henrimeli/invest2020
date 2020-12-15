import datetime, time,logging, unittest
from django.test import TestCase
import dateutil.parser, xmlrunner
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, strToDatetime, shouldUsePrint, displayOutput,displayError

"""
  This module contains unittests for the Event Capture component.
  These are tests that check the functionality of the backend for the Event Capture
  Below is the complete list of all the tests classes in this test:
 
  TestEventCapture1
  TestEventCapture2
  TestEventCapture3
  TestEventCapture4
"""

logger = logging.getLogger(__name__)

#
@unittest.skip("TODO: Not yet implemented ")
class TestEventCapture(TestCase):
  testname ='TestEventCapture'

  @classmethod 
  def setUpTestData(self):
    displayOutput(str="Setting up {0}".format(self.testname))
 
  def testStartupEvents(self):
    displayOutput(str="Testing the startup/stop server event Scenario")
    self.assertEqual(True,True)


if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)
