import  time,pytz
import logging, unittest
import sys,json
import pandas as pd
from django.utils import timezone
from django.test import TestCase
import dateutil.parser, xmlrunner
from bullbearetfs.robot.activitysentiments.models import RobotActivityWindow, MarketBusinessHours
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple,displayOutput,displayError,strToDatetime
from bullbearetfs.utilities.core import shouldUsePrint 
from django.utils.timezone import datetime,timedelta
from datetime import date

logger = logging.getLogger(__name__)
 

#
# Dummy function needed to force rebuild on change.
#
def test_robots_activity_window_dummy(request):
  displayOutput(str=" This is just a dummy function ")


######################################################################################################################
# RobotActivityWindow Functionality:
# RobotActivityWindow functionality encapsulates the concept of understanding the various windows during which we 
# place trades. Trades are for Acquisition and Disposition. 
# The window of activity is defined by the Market business Hours and the trader decision to trade at certain
# times and avoid others. 
# Technically, the Stock Market has the following windows. Extended Pre-Market[4:00-7:00], Pre-Market[7:00-9:30], Market[9:30-4], Post Market[4-7]. 
# Not all brokers operate during all windows
# and It is important to remember that during non-regular hours, the liquidity of the market and the spread 
# are extremely unpredictable. It is therefore necessary to apply caution, when trading outside of the regular windows.
# Two classes encapsulate these functionalities:
#   RobotActivityWindow and MarketBusinessHours
# MarketBusinessHours: is similar to the Calendar function on Alpaca. Allows us to check historically if the market was
# opened on given days. 
# RobotActivityWindow: Uses entries in the MarketBusinessHours class to check if the market is opened during a given window.
#
# 
##############################################################################################################
# Tests the functionality around:
#   Check if the market is opened at a given time (Date, Time).
#   Check if we can place a trade based on our selection of when we would like to trade.
#   Allows for us to specify Blackout windows, ...etc.
#   Depending of the time, we could place various types of orders.
#####################################################################################################
#  TestCases:
#    MarketBusinessHoursTests:
#
#
#    RobotActivityClassTestCase:
#
#
# Tests Update Business Hours.
# This class tests the Hours in the calendar.
# We use the pip install holidays to upload the holidays. We use weekday() to determin the weekdays and holidays.
#@unittest.skip("Taking a break now")
class MarketBusinessHoursTests(TestCase):
  test_name = 'MarketBusinessHoursTests'

  @classmethod 
  def setUpTestData(self):
    displayOutput("Setting up Test: {}".format(self.test_name))
    today = datetime.now(getTimeZoneInfo())


  #
  # On Invalid Business Days (Week end, Holidays)
  #
  #@unittest.skip("Taking a break now")
  def testHolidayDate(self):
    #
    #  October 12, 2020 is a Holiday !!!
    # 
    candidate = datetime(year=2020, month=10, day=12,hour=12,minute=0,second=0,tzinfo=getTimeZoneInfo())
    self.assertEqual(MarketBusinessHours.isOpen(current_date=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinAfterMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinExtendedPreMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinPreMarketHours(current_time=candidate),False)
    #
    #  January 1 2020 is a Holiday !!!
    # 
    candidate = datetime(year=2020, month=1, day=1,hour=12,minute=0,second=0,tzinfo=getTimeZoneInfo())
    self.assertEqual(MarketBusinessHours.isOpen(current_date=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinAfterMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinExtendedPreMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinPreMarketHours(current_time=candidate),False)

    #
    #  January 1, 2019 is a Holiday !!!
    # 
    candidate = datetime(year=2019, month=1, day=1,hour=12,minute=0,second=0,tzinfo=getTimeZoneInfo())
    self.assertEqual(MarketBusinessHours.isOpen(current_date=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinAfterMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinExtendedPreMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinPreMarketHours(current_time=candidate),False)

  #
  # On Saturdays and Sundays
  #
  #@unittest.skip("Taking a break now")
  def testWeekEndBusinessDate(self):
    #
    #  October 03 is Saturday
    # 
    candidate = datetime(year=2020, month=10, day=3,hour=12,minute=0,second=0,tzinfo=getTimeZoneInfo())
    self.assertEqual(MarketBusinessHours.isOpen(current_date=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinAfterMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinExtendedPreMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinPreMarketHours(current_time=candidate),False)

    #
    #  October 04 is Sunday
    # 
    candidate = datetime(year=2020, month=10, day=4,hour=12,minute=0,second=0,tzinfo=getTimeZoneInfo())
    self.assertEqual(MarketBusinessHours.isOpen(current_date=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinAfterMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinExtendedPreMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinPreMarketHours(current_time=candidate),False)



  #
  #
  #
  #@unittest.skip("Taking a break now")
  def testValidBusinessDateAfternoon(self):
    #
    #  12.00 PM
    # 
    candidate = datetime(year=2020, month=10, day=2,hour=12,minute=0,second=0,tzinfo=getTimeZoneInfo())
    self.assertEqual(MarketBusinessHours.isOpen(current_date=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinMarketHours(current_time=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinAfterMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinExtendedPreMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinPreMarketHours(current_time=candidate),False)

    #
    #  13.00 PM
    # 
    candidate = datetime(year=2020, month=10, day=2,hour=13,minute=0,second=0,tzinfo=getTimeZoneInfo())
    self.assertEqual(MarketBusinessHours.isOpen(current_date=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinMarketHours(current_time=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinAfterMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinExtendedPreMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinPreMarketHours(current_time=candidate),False)

    #
    #  14.20 PM
    # 
    candidate = datetime(year=2020, month=10, day=2,hour=14,minute=20,second=0,tzinfo=getTimeZoneInfo())
    self.assertEqual(MarketBusinessHours.isOpen(current_date=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinMarketHours(current_time=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinAfterMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinExtendedPreMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinPreMarketHours(current_time=candidate),False)

    #
    #  15.39 PM
    # 
    candidate = datetime(year=2020, month=10, day=2,hour=15,minute=39,second=0,tzinfo=getTimeZoneInfo())
    self.assertEqual(MarketBusinessHours.isOpen(current_date=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinMarketHours(current_time=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinAfterMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinExtendedPreMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinPreMarketHours(current_time=candidate),False)

    #
    #  16.42 PM
    # 
    candidate = datetime(year=2020, month=10, day=2,hour=16,minute=42,second=10,tzinfo=getTimeZoneInfo())
    self.assertEqual(MarketBusinessHours.isOpen(current_date=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinAfterMarketHours(current_time=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinExtendedPreMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinPreMarketHours(current_time=candidate),False)

    #
    #  17.39 PM
    # 
    candidate = datetime(year=2020, month=10, day=2,hour=17,minute=39,second=0,tzinfo=getTimeZoneInfo())
    self.assertEqual(MarketBusinessHours.isOpen(current_date=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinAfterMarketHours(current_time=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinExtendedPreMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinPreMarketHours(current_time=candidate),False)

    #
    #  18.39 PM
    # 
    candidate = datetime(year=2020, month=10, day=2,hour=18,minute=39,second=0,tzinfo=getTimeZoneInfo())
    self.assertEqual(MarketBusinessHours.isOpen(current_date=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinAfterMarketHours(current_time=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinExtendedPreMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinPreMarketHours(current_time=candidate),False)


  #
  # These are early morning hours
  #
  #@unittest.skip("Taking a break now")
  def testOnValidBusinessDateMorning(self):
    #
    #  3.00 AM
    # 
    candidate = datetime(year=2020, month=10, day=2,hour=3,minute=0,second=1,tzinfo=getTimeZoneInfo())
    self.assertEqual(MarketBusinessHours.isOpen(current_date=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinAfterMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinExtendedPreMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinPreMarketHours(current_time=candidate),False)

    #
    #  4.00 PM
    # 
    candidate = datetime(year=2020, month=10, day=2,hour=4,minute=0,second=1,tzinfo=getTimeZoneInfo())
    self.assertEqual(MarketBusinessHours.isOpen(current_date=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinAfterMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinExtendedPreMarketHours(current_time=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinPreMarketHours(current_time=candidate),False)

    #
    #  5.01 PM
    # 
    candidate = datetime(year=2020, month=10, day=2,hour=5,minute=0,second=1,tzinfo=getTimeZoneInfo())
    self.assertEqual(MarketBusinessHours.isOpen(current_date=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinAfterMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinExtendedPreMarketHours(current_time=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinPreMarketHours(current_time=candidate),False)

    #
    #  6.01 PM
    # 
    candidate = datetime(year=2020, month=10, day=2,hour=6,minute=0,second=1,tzinfo=getTimeZoneInfo())
    self.assertEqual(MarketBusinessHours.isOpen(current_date=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinAfterMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinExtendedPreMarketHours(current_time=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinPreMarketHours(current_time=candidate),False)

    #
    #  7.01 AM
    # 
    candidate = datetime(year=2020, month=10, day=2,hour=7,minute=1,second=0,tzinfo=getTimeZoneInfo())
    self.assertEqual(MarketBusinessHours.isOpen(current_date=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinAfterMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinExtendedPreMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinPreMarketHours(current_time=candidate),True)

    #
    #  8.29 AM
    # 
    candidate = datetime(year=2020, month=10, day=2,hour=8,minute=29,second=1,tzinfo=getTimeZoneInfo())
    self.assertEqual(MarketBusinessHours.isOpen(current_date=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinAfterMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinExtendedPreMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinPreMarketHours(current_time=candidate),True)

    #
    #  9.31 AM
    # 
    candidate = datetime(year=2020, month=10, day=2,hour=9,minute=31,second=1,tzinfo=getTimeZoneInfo())
    self.assertEqual(MarketBusinessHours.isOpen(current_date=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinMarketHours(current_time=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinAfterMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinExtendedPreMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinPreMarketHours(current_time=candidate),False)

    #
    #  10.31 AM
    # 
    candidate = datetime(year=2020, month=10, day=2,hour=10,minute=31,second=1,tzinfo=getTimeZoneInfo())
    self.assertEqual(MarketBusinessHours.isOpen(current_date=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinMarketHours(current_time=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinAfterMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinExtendedPreMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinPreMarketHours(current_time=candidate),False)

    #
    #  11.35 AM
    # 
    candidate = datetime(year=2020, month=10, day=2,hour=11,minute=35,second=1,tzinfo=getTimeZoneInfo())
    self.assertEqual(MarketBusinessHours.isOpen(current_date=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinMarketHours(current_time=candidate),True)
    self.assertEqual(MarketBusinessHours.isWithinAfterMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinExtendedPreMarketHours(current_time=candidate),False)
    self.assertEqual(MarketBusinessHours.isWithinPreMarketHours(current_time=candidate),False)

  #
  # Tests if the Market is opened based on given Dates
  # 
  #@unittest.skip("Taking a break now")
  def testIsMarketOpenDates(self):
    thursday_date = date(2020,10,1)
    friday_date = date(2020,10,2)
    saturday_date = date(2020,10,3)
    sunday_date = date(2020,10,4)
    holiday_1_date = date(2020,1,1)
    holiday_2_date = date(2020,10,12)

    holiday_3_date = date(2019,1,1)
    holiday_4_date = date(2018,1,1)

    thu_is_open=MarketBusinessHours.isOpen(current_date=thursday_date)
    fri_is_open=MarketBusinessHours.isOpen(current_date=friday_date)
    sat_is_open=MarketBusinessHours.isOpen(current_date=saturday_date)
    sun_is_open=MarketBusinessHours.isOpen(current_date=sunday_date)

    hol1_is_open=MarketBusinessHours.isOpen(current_date=holiday_1_date)
    hol2_is_open=MarketBusinessHours.isOpen(current_date=holiday_2_date)

    hol3_is_open=MarketBusinessHours.isOpen(current_date=holiday_3_date)
    hol4_is_open=MarketBusinessHours.isOpen(current_date=holiday_4_date)
    
    self.assertEqual(thu_is_open,True)
    self.assertEqual(fri_is_open,True)
    self.assertEqual(sat_is_open,False)
    self.assertEqual(sun_is_open,False)

    self.assertEqual(hol1_is_open,False)
    self.assertEqual(hol2_is_open,False)

    self.assertEqual(hol3_is_open,False)
    self.assertEqual(hol4_is_open,False)

#
#RobotActivityClassTestCase:
#
#@unittest.skip("Taking a break now")
class RobotActivityClassTestCase(TestCase):
  today = datetime.now(getTimeZoneInfo())
  #This section is intentionally blank
  test_name = 'RobotActivityClassBasicTestCase'

  @classmethod 
  def setUpTestData(self):
    #Parameters to validate: regular market, market closed, pre-market, post-market, extended pre market, trade all markets combined,
    # Midday Black out. With pre-market, with post market, with extended, combined all
    displayOutput(str=" Setting up Tests for {}".format(self.test_name)) 
  #
  # Typical trading day !!!
  #
  def testActivity1TypicalTradingDayTest(self):
    tm = RobotActivityWindow.objects.create(trade_before_open=False,trade_after_close=False,trade_during_extended_opening_hours=False,
      offset_after_open='0',offset_before_close='0',blackout_midday_from='10:00am',blackout_midday_time_interval='0')
    win1=tm.pk
    a1 = RobotActivityWindow.objects.get(id=win1)
    bt = datetime(year=2020, month=10, day=1,hour=9,minute=30,second=1,tzinfo=getTimeZoneInfo())

    self.assertEqual(a1.canTradeNow(current_time = bt),True) #Opening
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-5,minutes=-30)),False) #3:00am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-3)),False) #6:30am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-2,minutes=-15)),False) #7:15am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=-2)),False) #9:28
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=2)),True) #9:31
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=5,minutes=2)),True) #14:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=7)),False) #16:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=8,minutes=2)),False) #17:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=9,minutes=2)),False) #19:32

  #
  # Trading day with pre-Market Enabled !!!
  #
  def testActivity1TradingDayWithPremarketTest(self):
    tm = RobotActivityWindow.objects.create(trade_before_open=True,trade_after_close=False,trade_during_extended_opening_hours=False,
      offset_after_open='0',offset_before_close='0',blackout_midday_from='10:00am',blackout_midday_time_interval='0')
    win1=tm.pk
    a1 = RobotActivityWindow.objects.get(id=win1)
    bt = datetime(year=2020, month=10, day=2,hour=9,minute=30,second=1,tzinfo=getTimeZoneInfo())

    self.assertEqual(a1.canTradeNow(current_time = bt),True) #Opening
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-5,minutes=-30)),False) #3:00am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-3)),False) #6:30am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-2,minutes=-15)),True) #7:15am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=-2)),True) #9:28
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=2)),True) #9:31
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=5,minutes=2)),True) #14:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=7)),False) #16:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=8,minutes=2)),False) #17:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=9,minutes=2)),False) #19:32

  
  #
  # Trading day with After Market Closed Enabled !!!
  #
  def testTradingDayAfterMarketClosedTest(self):
    tm = RobotActivityWindow.objects.create(trade_before_open=False,trade_after_close=True,trade_during_extended_opening_hours=False,
      offset_after_open='0',offset_before_close='0',blackout_midday_from='10:00am',blackout_midday_time_interval='0')
    win1=tm.pk
    a1 = RobotActivityWindow.objects.get(id=win1)
    bt = datetime(year=2020, month=10, day=2,hour=9,minute=30,second=1,tzinfo=getTimeZoneInfo())

    self.assertEqual(a1.canTradeNow(current_time = bt),True) #Opening
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-5,minutes=-30)),False) #3:00am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-3)),False) #6:30am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-2,minutes=-15)),False) #7:15am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=-2)),False) #9:28
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=2)),True) #9:31
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=5,minutes=2)),True) #14:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=7)),True) #16:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=8,minutes=2)),True) #17:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=10,minutes=2)),False) #19:32

  #
  # Trading day with After Market Closed Enabled !!!
  # 4:00 - 7:00am
  #
  def testTradingDayExtendedPreMarketOpen(self):
    tm = RobotActivityWindow.objects.create(trade_before_open=False,trade_after_close=False,trade_during_extended_opening_hours=True,
      offset_after_open='0',offset_before_close='0',blackout_midday_from='10:00am',blackout_midday_time_interval='0')
    win1=tm.pk
    a1 = RobotActivityWindow.objects.get(id=win1)
    bt = datetime(year=2020, month=10, day=6,hour=9,minute=30,second=1,tzinfo=getTimeZoneInfo())

    self.assertEqual(a1.canTradeNow(current_time = bt),True) #Opening
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-5,minutes=-30)),True) #4:00am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-3)),True) #6:30am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-2,minutes=-15)),False) #7:15am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=-2)),False) #9:28
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=2)),True) #9:31
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=5,minutes=2)),True) #14:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=7)),False) #16:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=8,minutes=2)),False) #17:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=10,minutes=2)),False) #19:32

  #
  # I only want to trade 30 minutes after open of the Market
  # 9:30 - 10:00am is blocked
  #
  def testTradingDayWithOffsetAfterOpenTest(self):
    tm = RobotActivityWindow.objects.create(trade_before_open=False,trade_after_close=False,trade_during_extended_opening_hours=False,
      offset_after_open='30',offset_before_close='0',blackout_midday_from='10:00am',blackout_midday_time_interval='0')
    win1=tm.pk
    a1 = RobotActivityWindow.objects.get(id=win1)
    bt = datetime(year=2020, month=10, day=6,hour=9,minute=30,second=1,tzinfo=getTimeZoneInfo())

    self.assertEqual(a1.canTradeNow(current_time = bt),False) #9:30Opening
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-5,minutes=-30)),False) #4:00am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-3)),False) #6:30am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-2,minutes=-15)),False) #7:15am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=-2)),False) #9:28
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=2)),False) #9:31
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=5,minutes=2)),True) #14:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=7)),False) #16:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=8,minutes=2)),False) #17:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=10,minutes=2)),False) #19:32

  #
  # I don't want to trade between 3:30 - 4:00pm of the Market
  # 
  # 
  def testTradingDayWithOffsetBeforeClose(self):
    tm = RobotActivityWindow.objects.create(trade_before_open=False,trade_after_close=False,trade_during_extended_opening_hours=False,
      offset_after_open='0',offset_before_close='30',blackout_midday_from='10:00am',blackout_midday_time_interval='0')
    win1=tm.pk
    a1 = RobotActivityWindow.objects.get(id=win1)
    bt = datetime(year=2020, month=10, day=6,hour=9,minute=30,second=1,tzinfo=getTimeZoneInfo())

    self.assertEqual(a1.canTradeNow(current_time = bt),True) #9:30Opening
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-5,minutes=-30)),False) #4:00am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-3)),False) #6:30am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-2,minutes=-15)),False) #7:15am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=-2)),False) #9:28
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=2)),True) #9:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=5,minutes=2)),True) #14:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=6)),False) #15:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=7)),False) #16:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=8,minutes=2)),False) #17:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=10,minutes=2)),False) #19:32

  #
  # I don't want to trade between 10am - 10:30am of the Market
  # 
  def testTradingWithMiddayBlackoutTest(self):
    tm = RobotActivityWindow.objects.create(trade_before_open=False,trade_after_close=False,trade_during_extended_opening_hours=False,
      offset_after_open='0',offset_before_close='0',blackout_midday_from='10:00am',blackout_midday_time_interval='30')
    win1=tm.pk
    a1 = RobotActivityWindow.objects.get(id=win1)
    bt = datetime(year=2020, month=10, day=7,hour=9,minute=30,second=1,tzinfo=getTimeZoneInfo())

    self.assertEqual(a1.canTradeNow(current_time = bt),True) #9:30Opening
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-5,minutes=-30)),False) #4:00am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-3)),False) #6:30am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-2,minutes=-15)),False) #7:15am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=-2)),False) #9:28
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=2)),True) #9:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=35)),False) #10:35
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=5,minutes=2)),True) #14:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=6)),True) #15:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=7)),False) #16:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=8,minutes=2)),False) #17:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=10,minutes=2)),False) #19:32


  #
  # Various Combinations 1
  # 
  def testTradingWithVariousCombinations1Test(self):
    tm = RobotActivityWindow.objects.create(trade_before_open=True,trade_after_close=True,trade_during_extended_opening_hours=False,
      offset_after_open='45',offset_before_close='15',blackout_midday_from='11:00am',blackout_midday_time_interval='45')
    win1=tm.pk
    a1 = RobotActivityWindow.objects.get(id=win1)
    bt = datetime(year=2020, month=10, day=7,hour=9,minute=30,second=1,tzinfo=getTimeZoneInfo())

    self.assertEqual(a1.canTradeNow(current_time = bt),False) #9:30Opening
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-5,minutes=-30)),False) #4:00am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-3)),False) #6:30am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-2,minutes=-15)),True) #7:15am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=-2)),True) #9:28
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=2)),False) #9:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=35)),False) #10:05
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=5,minutes=2)),True) #14:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=6)),True) #15:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=7)),True) #16:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=8,minutes=2)),True) #17:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=10,minutes=2)),False) #19:32


  #
  # Various Combinations 2
  # 
  def testTradingWithVariousCombinations2Test(self):
    tm = RobotActivityWindow.objects.create(trade_before_open=False,trade_after_close=True,trade_during_extended_opening_hours=True,
      offset_after_open='30',offset_before_close='15',blackout_midday_from='11:00am',blackout_midday_time_interval='45')
    win1=tm.pk
    a1 = RobotActivityWindow.objects.get(id=win1)
    bt = datetime(year=2020, month=10, day=7,hour=9,minute=30,second=1,tzinfo=getTimeZoneInfo())

    self.assertEqual(a1.canTradeNow(current_time = bt),False) #9:30Opening
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-5,minutes=-30)),True) #4:00am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-3)),True) #6:30am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-2,minutes=-15)),False) #7:15am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=-2)),False) #9:28
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=2)),False) #9:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=35)),True) #10:05
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=5,minutes=2)),True) #14:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=6,minutes=18)),False) #15:48
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=7)),True) #16:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=8,minutes=2)),True) #17:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=10,minutes=2)),False) #19:32

  #
  # Various Combinations 3
  # 
  def testTradingWithVariousCombinations3Test(self):
    tm = RobotActivityWindow.objects.create(trade_before_open=True,trade_after_close=True,trade_during_extended_opening_hours=True,
      offset_after_open='0',offset_before_close='0',blackout_midday_from='11:00am',blackout_midday_time_interval='0')
    win1=tm.pk
    a1 = RobotActivityWindow.objects.get(id=win1)
    bt = datetime(year=2020, month=10, day=7,hour=9,minute=30,second=1,tzinfo=getTimeZoneInfo())

    self.assertEqual(a1.canTradeNow(current_time = bt),True) #9:30Opening
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-5,minutes=-30)),True) #4:00am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-3)),True) #6:30am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=-2,minutes=-15)),True) #7:15am
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=-2)),True) #9:28
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=2)),True) #9:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(minutes=35)),True) #10:35
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=5,minutes=2)),True) #14:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=6)),True) #15:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=7)),True) #16:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=8,minutes=2)),True) #17:32
    self.assertEqual(a1.canTradeNow(current_time = bt + timedelta(hours=10,minutes=2)),False) #19:32



if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)