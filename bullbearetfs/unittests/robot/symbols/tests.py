import datetime, time, pytz
from datetime import date
import logging, unittest, sys,json
import pandas as pd
from django.utils import timezone
from django.test import TestCase
import dateutil.parser
import xmlrunner
# Import Models
from bullbearetfs.models import EquityTradingData
from bullbearetfs.robot.symbols.models import RobotEquitySymbols
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, strToDatetime, shouldUsePrint, displayOutput,displayError
from bullbearetfs.datasources.datasources import  BackTestInfrastructure, DownloadableETFBullBear

logger = logging.getLogger(__name__)

######################################################################################################################
# RobotEquitySymbols,EquityTradingData Functionality:
# Our strategies are based on the acquisition of a Bull and a Bear ETFs. 
# In order to understand how to buy/sell smart, it is important for us to understand recent activities about
# the given equities. Therefore, we capture entries every trading tick into the EquityTradingData class and 
# use it to calculate various averages. We believe we can get this from outside sources, but it might be an expensive
# operation. Why not write our own to keep it up?

#
# Populate the EquitySymbols Table.
# Validate that some pairs are valid pairs. 
# This should prevent us from selecting things we haven't vetted.
#@unittest.skip("Taking a break now")
class RobotEquitySymbolsLoadDefaultTestCase(TestCase):
  test_name = 'RobotEquitySymbolsLoadDefaultTestCase'

  @classmethod 
  def setUpTestData(self):
    displayOutput(str="Setting up Test Data for test: {}".format(self.test_name))

  #@unittest.skip("Taking a break now")
  def testInsertMasterEquities(self):
    all_equities=RobotEquitySymbols.insertMasterEquities(count=3)
    total_number = RobotEquitySymbols.getTotalMaster()
    self.assertEqual(total_number,3)
    self.assertEqual(RobotEquitySymbols.isValidPair(bull='TQQQ',bear='SQQQ'),True)
    self.assertEqual(RobotEquitySymbols.isValidPair(bull='SQQQ',bear='TQQQ'),False)
    self.assertEqual(RobotEquitySymbols.isValidPair(bull='LABU',bear='LABD'),True)

  #
  # Validate that if I try inserting the same entry several times, things will not be duplicated.
  # I should get a message saying that it is already present.
  #
  #@unittest.skip("Taking a break now")
  def testInsertMasterEquitiesNoDuplicates(self):
    all_equities=RobotEquitySymbols.insertMasterEquities(count=3)
    all_equities=RobotEquitySymbols.insertMasterEquities(count=2)
    all_equities=RobotEquitySymbols.insertMasterEquities(count=1)
    total_number = RobotEquitySymbols.getTotalMaster()
    self.assertEqual(total_number,3)
    self.assertEqual(RobotEquitySymbols.isValidPair(bull='TQQQ',bear='SQQQ'),True)
    self.assertEqual(RobotEquitySymbols.isValidPair(bull='SQQQ',bear='TQQQ'),False)
    self.assertEqual(RobotEquitySymbols.isValidPair(bull='LABU',bear='LABD'),True)
    self.assertEqual(RobotEquitySymbols.isValidPair(bull='NADA',bear='JOE'),False)



#
# The RobotEquitySymbols uses another class to keep track of the .
# Various functions are run on this to make sure that we can retrieve data properly to be displayed on the UI.
# getFourWeeksEquitiesData(),
# Insert Data into the EquityTradingData class and check to make sure we are getting the right averages.
# NOTE: Can't use fixed dates, because it will shift and test will fail. Instead use time intervals
# 
#@unittest.skip("Taking a break now")
class RobotEquitySymbolsUIPresentationDataTestCase(TestCase):
  number_entries = 1
  test_name = 'RobotEquitySymbolsClassBasicTestCase'
  @classmethod 
  def setUpTestData(self):
    displayOutput(str="Setting up Test Data for test: {}".format(self.test_name))
    #Set up the Data to feed the Robot.
    RobotEquitySymbols.insertMasterEquities(count=self.number_entries)
    #Start Date on October 01
    start_date = datetime.datetime(2020,10,1,tzinfo=timezone.utc).isoformat()
    backtesting = BackTestInfrastructure(action='download',useMasterTable=True)
    response = backtesting.processTradeData(start_date=start_date)
    response0 = backtesting.downloadAndStore(target='both',update=False)
    #Data has loaded completely.

  #@unittest.skip("Taking a break now")
  def testEquitiesDataTest(self):
    pair = dict()
    pair['bull_symbol']='TQQQ'
    pair['bear_symbol']='SQQQ'
    pair['etf_symbol']='QQQ'

    res_hour = RobotEquitySymbols.getHourlyEquitiesData(pair=pair)
    res_today = RobotEquitySymbols.getTodayEquitiesData(pair=pair)
    res_week = RobotEquitySymbols.getWeekEquitiesData(pair=pair)
    res_2_weeks = RobotEquitySymbols.getTwoWeeksEquitiesData(pair=pair)
    res_3_weeks = RobotEquitySymbols.getThreeWeeksEquitiesData(pair=pair)
    res_4_weeks = RobotEquitySymbols.getFourWeeksEquitiesData(pair=pair)

    #Difficult to Assert?
    self.assertTrue(int(res_hour['bull_h'])>0)
    self.assertTrue(int(res_hour['bull_l'])>0)
    self.assertTrue(int(res_hour['bull_a'])>0)
    self.assertTrue(int(res_hour['bull_s'])>0)

    self.assertTrue(int(res_hour['bear_h'])>0)
    self.assertTrue(int(res_hour['bear_l'])>0)
    self.assertTrue(int(res_hour['bear_a'])>0)
    self.assertTrue(int(res_hour['bear_s'])>=0)

    self.assertTrue(int(res_hour['etf_h'])>0)
    self.assertTrue(int(res_hour['etf_l'])>0)
    self.assertTrue(int(res_hour['etf_a'])>0)
    self.assertTrue(int(res_hour['etf_s'])>=0)

if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)
