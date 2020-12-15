import datetime, time, pytz, logging, unittest , sys,json
import pandas as pd
from django.utils import timezone
from django.test import TestCase
import dateutil.parser
from bullbearetfs.models import Notifications, NotificationType, Settings

"""
  This module contains unittests test classes for the Customer Management component.
  These are tests that check the functionality of the backend for the Business Intelligence
  Below is the complete list of all the tests modules and classes in this application:
 
   tests.py: contains all the classes to test the validity of function1 and function2

"""
logger = logging.getLogger(__name__)

def test_notifications_dummy(request):
	logger.info("Just a dummy function to force the Build.")


#
#
#@unittest.skip("Taking a break now")
class NotificationsTestCase(TestCase):
  testname ='NotificationsTestCase'

  @classmethod 
  def setUpTestData(self):
    print("Setting up {0}".format(self.testname))
    now=datetime.datetime.now(timezone.utc)

    entry = Notifications.objects.create(notifications_name='Email To John',from_user=2,to_user=1,
                                         share_date=now,read_date=now)
    self.entry_id = entry.pk 
    
  def testEmptyNotificationsTest(self):
    basic = Notifications.objects.get(pk=self.entry_id)
    self.assertEqual(basic.notifications_name,'Email To John')

