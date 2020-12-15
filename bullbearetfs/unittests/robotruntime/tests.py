import datetime, time,logging, unittest
from django.test import TestCase
import dateutil.parser, xmlrunner
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, strToDatetime, shouldUsePrint, displayOutput,displayError

"""
  TODO: Describe these tests 
"""
def test_robotruntime_dummy(request):
  logger.info("Just a dummy function to force the Build.")


logger = logging.getLogger(__name__)

#
@unittest.skip("TODO: Not yet implemented")
class TestRobotRuntime(TestCase):
  testname ='TestRobotRuntime'

  @classmethod 
  def setUpTestData(self):
    displayOutput(str="Setting up {0}".format(self.testname))
 
  def testAcquisitionOfAllEnabledRobots(self):
    displayOutput("Testing the Acquisition of all enabled Robots ")
    self.assertEqual(True,True)


if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)

