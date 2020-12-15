import datetime, time, pytz, logging, unittest , sys,json
import pandas as pd
from django.utils import timezone
from django.test import TestCase
import dateutil.parser,xmlrunner

from bullbearetfs.customer.models import Address, BusinessInformation, Billing,Customer,CustomerProfile
from bullbearetfs.customer.models import CustomerBasic, CustomerSecurity
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, strToDatetime, shouldUsePrint, displayOutput,displayError

"""
  TODO: Describe this test module
"""
logger = logging.getLogger(__name__)

def test_customer_dummy(request):
	logger.info("Just a dummy function to force the Build.")

#
#
@unittest.skip("TODO: Not yet implemented.")
class CustomerBasicTestCase(TestCase):
  testname ='CustomerBasicTestCase'

  @classmethod 
  def setUpTestData(self):
    displayOutput(str="Setting up {0}".format(self.testname))
    cb = CustomerBasic.objects.create(first_name='John',last_name='Doe',username='john_doe',main_phone='919 111 2222',
    	               alternate_phone='800 123 4567',alternate_email='john_doe@gmail.com',main_email='john_doe@yahoo.com')
    self.cb_id = cb.pk 
    
  def testEmptyCustomerProfileTest(self):
    basic = CustomerBasic.objects.get(pk=self.cb_id)
    self.assertEqual(basic.first_name,'John')


#
#
@unittest.skip("TODO: Not yet implemented.")
class CustomerProfileTestCase(TestCase):
  testname ='CustomerProfileTestCase'

  @classmethod 
  def setUpTestData(self):
    displayOutput(str="Setting up {0}".format(CustomerProfileTestCase))
    cp = CustomerProfile.objects.create()
    self.cp_id = cp.pk 

  def testEmptyCustomerProfileTest(self):
    count = -1 
    #self.assertTrue(count>=0)
    self.assertEqual(count,-1)


if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)

