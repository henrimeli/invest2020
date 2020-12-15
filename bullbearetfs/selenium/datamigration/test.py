from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest, xmlrunner, time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from  bullbearetfs.selenium.core.browsers import EggheadSeleniumBrowser

#####################################################################################
# Dashboard Component.
#   
#   
#
class TestDataMigrationComponent(StaticLiveServerTestCase):
  testname ='TestDataMigrationComponent'

  @classmethod 
  def setUp(self):
    self.browser = EggheadSeleniumBrowser()
    self.driver = self.browser.getDriver()

  @classmethod
  def tearDown(self):
    self.driver.quit()	

  def test_HomePage(self):
    self.driver.maximize_window()
    time.sleep(1)
