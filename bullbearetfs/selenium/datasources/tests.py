from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest, xmlrunner, time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from  bullbearetfs.selenium.core.browsers import EggheadSeleniumBrowser

#####################################################################################
# Data Sources And Infrastructure
#
class TestDatasources(StaticLiveServerTestCase):
  testname ='TestDatasources'

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
    self.driver.get(self.live_server_url)
    time.sleep(3)
    self.assertEqual(self.driver.title,'This is the home page for Egghead Project.')
    
    dashboard_menu=self.driver.find_element_by_xpath("//*[@id='navbar']/ul[1]/li[2]")
    dashboard_menu.click()
    time.sleep(3)
    
    home_menu=self.driver.find_element_by_xpath("/html/body/nav/div/div[1]/a")
    home_menu.click()
    time.sleep(3)
    
    robots_menu=self.driver.find_element_by_xpath("//*[@id='navbar']/ul[1]/li[3]/a")
    robots_menu.click()
    time.sleep(3)

    strategies_menu=self.driver.find_element_by_xpath("//*[@id='navbar']/ul[1]/li[4]/a")
    strategies_menu.click()
    time.sleep(3)

    create_strategy_menu=self.driver.find_element_by_xpath("//*[@id='navbar']/ul[2]/li[1]/a")
    create_strategy_menu.click()
    time.sleep(3)

    create_robot_menu=self.driver.find_element_by_xpath("//*[@id='navbar']/ul[2]/li[2]/a")
    create_robot_menu.click()
    time.sleep(3)


if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)
