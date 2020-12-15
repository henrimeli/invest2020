import datetime, time, pytz, logging, unittest , sys,json
from django.utils import timezone
from django.test import TestCase
import dateutil.parser,xmlrunner
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, strToDatetime, shouldUsePrint, displayOutput,displayError

"""
  TODO: please describe this module
"""

logger = logging.getLogger(__name__)

def test_others_dummy(request):
  logger.info(" This is just a dummy function ")


# This test case covers the creation of a new Class Instance of the Robot.
# We will be testing the following Interfaces that are critical for the function.
#
@unittest.skip("TODO: not yet implemented")
class TestOthers(TestCase):
  testname = 'TestOthers'

  @classmethod 
  def setUpTestData(self):
    displayOutput(str="Setting up {0}".format(self.testname))

  def testValidDispositionPolicyTest(self):
    self.assertEqual(False,True)

if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)

