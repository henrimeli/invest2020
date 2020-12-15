
import datetime, time,logging, unittest
from django.test import TestCase
import dateutil.parser, xmlrunner

"""
  This module contains unittests test classes for the Data Migration component.
  These are tests that check the functionality of the backend for the Data Migration
  Below is the complete list of all the tests modules and classes in this application:
 
  NOTE: Just a placeholder for now 

"""

logger = logging.getLogger(__name__)

#
#@unittest.skip("Taking a break now")
class TestDataMigration(TestCase):
  testname ='TestDataMigration'

  @classmethod 
  def setUpTestData(self):
    print("Setting up {0}".format(self.testname))
 
  def testHomePage(self):
    print("Testing the Home Page Scenario")
    self.assertEqual(True,True)


if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)
