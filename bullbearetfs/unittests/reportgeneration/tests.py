
import datetime, time,logging, unittest
from django.test import TestCase
import dateutil.parser, xmlrunner
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, strToDatetime, shouldUsePrint, displayOutput,displayError

"""
  TODO: Add module information
"""
logger = logging.getLogger(__name__)

#
@unittest.skip("TODO: Not yet implemented")
class TestReportGenerationCase(TestCase):
  testname ='TestReportGenerationCase'

  @classmethod 
  def setUpTestData(self):
    displayOutput(str="Setting up {0}".format(self.testname))
 
  def testReportGeneration(self):
    displayOutput(str="Testing the Report Generation Scenario")
    self.assertEqual(True,True)


if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)
