import datetime
import logging
from django.test import TestCase
# Import Models
from bullbearetfs.market.models import WebsiteContactPage
from bullbearetfs.indicator.models import EquityIndicator, CHOICES_INDICATOR_CLASS


def test_indicator_dummy(request):
  pass
  
# Create your tests here.
class WebsiteContactPageTestCase(TestCase):
  def setUp(self):
    WebsiteContactPage.objects.create(subject="Trawick",email="JohnDoe@trawick.com",comment="This is a comment")

  def test_website_contact_page(self):
    contact = WebsiteContactPage.objects.get(subject="Trawick")
    self.assertEqual(contact.getSubject(),"Trawick")

def testFunction(**kwargs):
  h=''
  if 'current_time' in kwargs and 'last_successful' in kwargs:
    current_t = kwargs['current_time']
    last_successful =kwargs['last_successful']
    difference = current_t - last_successful
    print("HENRI: Time Difference {0}".format(difference))
    if h == True:
    	print("YES. IT WORKS.")
  else:
    print("HENRI")

  return 
#
# Indicator Validity Test Cases: Invalid scenarios
# This class tests the validity of Indicators
# All Indicators must be invalid
class EquityIndicatorTriggeredTestCase(TestCase):

  @classmethod 
  def setUpTestData(self):
    #The Indicators below are invalid. How does isTriggered() respond?
    EquityIndicator.objects.create(name='i_i0',indicator_class='Manual Indicator',indicator_family='Fibonacci')
    EquityIndicator.objects.create(name='i_i1',indicator_class='Time Indicator',indicator_family='Fibonacci')
    EquityIndicator.objects.create(name='i_i2',indicator_class='Time Indicator',indicator_family='Fibonacci')
    mytime = datetime.datetime(2020,7,31)
    #last_successful = datetime.datetime.now()
    print("Henri's other time: {0}".format(mytime))
    testFunction(current_time=datetime.datetime.now(),last_successful=mytime)
    # The Indicators below are valid.
    EquityIndicator.objects.create(name='manual_i0',indicator_class='Manual Indicator')
    # for Immediate Indicator, Circuit Breaker,
    EquityIndicator.objects.create(name='cb_i0',indicator_class='Circuit Breaker')
    EquityIndicator.objects.create(name='immediate_i0',indicator_class='Immediate Indicator')
    #Volume Indicator
    EquityIndicator.objects.create(name='volume_i0',indicator_class='Volume Indicator')
    EquityIndicator.objects.create(name='volume_i1',indicator_class='Volume Indicator',volume_interval='20% Average Volume',treshold_to_volume_open='2 Millions')
    EquityIndicator.objects.create(name='volume_i2',indicator_class='Volume Indicator',volume_interval='25% Average Volume',treshold_to_volume_open='2 Millions')
    # Time Indicator
    EquityIndicator.objects.create(name='time_i0',indicator_class='Time Indicator')
    EquityIndicator.objects.create(name='time_i1',indicator_class='Time Indicator',time_interval='60',treshold_to_market_open='45')
    EquityIndicator.objects.create(name='time_i2',indicator_class='Time Indicator',time_interval='45',treshold_to_market_open='10')

    # Profi Indicator
    EquityIndicator.objects.create(name='p_i0',indicator_class='Profit Indicator')
    EquityIndicator.objects.create(name='p_i1',indicator_class='Profit Indicator')
    EquityIndicator.objects.create(name='p_i2',indicator_class='Profit Indicator')

  #Attempts to trigger invalid indicators. All results should be False
  def testTriggersInvalid(self):
    ind_0 = self.getIndicator(name='i_i0')
    ind_1 = self.getIndicator(name='i_i1')
    ind_2 = self.getIndicator(name='i_i2')
    self.assertEqual(ind_0.isTriggered(),False)
    self.assertEqual(ind_1.isTriggered(),False)
    self.assertEqual(ind_2.isTriggered(),False)

  # Manual Indicators require param manual_check=True or manual_check=False
  def testIsTriggeredWithArgsOnManualIndicator(self):
    valid_manual_i0 = self.getIndicator(name='manual_i0')
    #Confirm it is Valid
    self.assertEqual(valid_manual_i0.isValid(),True)    
    #Pass varioud args , starting with the good one
    self.assertEqual(valid_manual_i0.isTriggered(manual_check=True),True)
    self.assertEqual(valid_manual_i0.isTriggered(manual_check=False),False)

  # Circuit Breaker Indicators require param circuit_breaker_check=True 
  # or circuit_breaker_check=False
  def testIsTriggeredWithArgsOnCBIndicator(self):
    valid_cb_i0 = self.getIndicator(name='cb_i0')
    #Confirm it is Valid
    self.assertEqual(valid_cb_i0.isValid(),True)    
    #Pass varioud args , starting with the good one
    self.assertEqual(valid_cb_i0.isTriggered(circuit_breaker_check=True),True)
    self.assertEqual(valid_cb_i0.isTriggered(circuit_breaker_check=False),False)

  # Immediate Indicators require param immediate_check=True 
  # or immediate_check=False
  def testIsTriggeredWithArgsOnImmediateIndicator(self):
    valid_now_i0 = self.getIndicator(name='immediate_i0')
    #Confirm it is Valid
    self.assertEqual(valid_now_i0.isValid(),True)    
    #Pass varioud args , starting with the good one
    self.assertEqual(valid_now_i0.isTriggered(immediate_check=True),True)
    self.assertEqual(valid_now_i0.isTriggered(immediate_check=False),False)

  #Testing 2 internal functions to convert Strings into Integers in a more fluent
  # And readable way.
  def testGetLowestVolume(self):
  	valid_volume_i0 = self.getIndicator(name='volume_i0')
  	self.assertEqual(valid_volume_i0.isValid(),True)
  	# Check Lowest Volume
  	self.assertEqual(valid_volume_i0.getLowestVolume(),1000000)

  	#Check Average Daily      	
  	self.assertEqual(valid_volume_i0.getVolumeInterval(7000000),700000)



  # Volume Indicators require param last_successful, current_volume and average_volume of symbol
  # internally: treshold_to_open, interval 
  # TODO: Consider adding a new System Function to update nightly data before market reopens
  # Many things to be reset, including last_successful_date
  # i0 (10%,1M), i1 (20%,2M ), i2(25%,2M )
  def testIsTriggeredWithArgsOnVolumeIndicator(self):
    valid_volume_i0 = self.getIndicator(name='volume_i0')
    valid_volume_i1_20p_2M = self.getIndicator(name='volume_i1')
    valid_volume_i2_25p_2M = self.getIndicator(name='volume_i2')
    #Confirm  all are Valid
    self.assertEqual(valid_volume_i0.isValid(),True)    
    self.assertEqual(valid_volume_i1_20p_2M.isValid(),True)    
    self.assertEqual(valid_volume_i2_25p_2M.isValid(),True)    
    #Pass various args: last_successful (LS), current_volume (CV), average_volume (AV) (monthly)

    #There are various scenarios to test. First let's test the successful ones.
    #1. Current Volume (CV)= 660K below 10% of Average Volume (AV) treshold (700k shares), Last Successful = 0, 
    # isTriggered() should return True for i1, i2 and False for i0
    cv = 600000 
    ls = 0
    av = 7000000
    self.assertEqual(valid_volume_i0.isTriggered(last_successful=ls,current_volume=cv,average_volume=av),False)
    self.assertEqual(valid_volume_i1_20p_2M.isTriggered(last_successful=ls,current_volume=cv,average_volume=av),False) 
    self.assertEqual(valid_volume_i2_25p_2M.isTriggered(last_successful=ls,current_volume=cv,average_volume=av),False)   

    #2. CV =4.5M, AV = 7M, LS = 3M. isTriggered
    cv = 4500000
    ls = 3000000
    av = 7000000
    
    #interval=
    #replace it with minimum_volume,lowes_volume
    #treshold_to_open=1M
    # if current_volume < lowest_volume return false
    # else calculate interval = average_volume * percentage
    # if current_volume - last_successful >=interval return True
    # When saving last successful, you must save with a date, because ...
    # 

    self.assertEqual(valid_volume_i0.isTriggered(last_successful=ls,current_volume=cv,average_volume=av),True)
    self.assertEqual(valid_volume_i0.isTriggered(immediate_check=False),False)

  # Time Indicators require param last_successful, current_time, 
  # internally: treshold_to_market, time_interval
  # TODO: Consider adding a new System Function to update nightly data before market reopens
  # Many things to be reset, including last_successful_time
  # CHOICES_TIME_INTERVAL = [30,45,60, ...] time_interval (60)
  # CHOICES_TRESHOLD_TO_MARKET_OPEN = [5,10,15,30,45,...], treshold_to_market_open (5)
  # i0 (5,60), i1 (15,45), 12 (45,10)
  def testIsTriggeredWithArgsOnTimeIndicator(self):
    valid_time_i0_5_60 = self.getIndicator(name='time_i0')
    valid_time_i1_15_45 = self.getIndicator(name='time_i1')
    valid_time_i2_45_10 = self.getIndicator(name='time_i2')
    #Confirm  all are Valid
    self.assertEqual(valid_time_i0_5_60.isValid(),True)    
    self.assertEqual(valid_time_i1_15_45.isValid(),True)    
    self.assertEqual(valid_time_i2_45_10.isValid(),True)    
    ls = datetime.datetime(2020,8,3)
    ct = datetime.datetime.now()

    self.assertEqual(valid_time_i0_5_60.isTriggered(last_successful=ls,current_time=ct),False)
    self.assertEqual(valid_time_i1_15_45.isTriggered(last_successful=ls,current_time=ct),False) 
    self.assertEqual(valid_time_i2_45_10.isTriggered(last_successful=ls,current_time=ct),False)   

  def getIndicator(self,name):
    match=name
    indicator = EquityIndicator.objects.get(name=match)
    
    return indicator


#
# Indicator Validity Test Cases: Invalid scenarios
# This class tests the validity of Indicators
# All Indicators must be invalid
class EquityIndicatorInvalidTestCase(TestCase):

  @classmethod 
  def setUpTestData(self):
    EquityIndicator.objects.create(name='i_i0',indicator_class='Manual Indicator',indicator_family='Fibonacci')
    EquityIndicator.objects.create(name='i_i1',indicator_class='Time Indicator',indicator_family='Fibonacci')
    EquityIndicator.objects.create(name='i_i2',indicator_class='Time Indicator',indicator_family='Fibonacci')

  def testInvalidIndicator(self):
    ind_0 = self.getIndicator(name='i_i0')
    ind_1 = self.getIndicator(name='i_i1')
    ind_2 = self.getIndicator(name='i_i2')
    self.assertEqual(ind_0.isValid(),False)
    self.assertEqual(ind_1.isValid(),False)
    self.assertEqual(ind_2.isValid(),False)

  def getIndicator(self,name):
    match=name
    indicator = EquityIndicator.objects.get(name=match)
    
    return indicator


#
# Indicator Validity Test Cases
# This class tests the validity of Indicators
# All Indicators must be valid
class EquityIndicatorValidTestCase(TestCase):

  @classmethod 
  def setUpTestData(self):
    trigger_family = 'Triggers'

  	#Defaults Indicators
    EquityIndicator.objects.create(name='default_i0')
    EquityIndicator.objects.create(name='default_i1')
    EquityIndicator.objects.create(name='default_i2')

    #Manual Indicators
    EquityIndicator.objects.create(name='manual_i0',indicator_class='Manual Indicator')
    EquityIndicator.objects.create(name='manual_i1',indicator_class='Manual Indicator',indicator_family=trigger_family)
    EquityIndicator.objects.create(name='manual_i2',indicator_class='Manual Indicator',indicator_family=trigger_family)
    
    #Volumne Indicators
    EquityIndicator.objects.create(name='volume_i0',indicator_class='Volume Indicator')
    EquityIndicator.objects.create(name='volume_i1',indicator_class='Volume Indicator',indicator_family=trigger_family)
    EquityIndicator.objects.create(name='volume_i2',indicator_class='Volume Indicator',indicator_family=trigger_family)

    #Time Indicators
    EquityIndicator.objects.create(name='time_i0',indicator_class='Time Indicator')
    EquityIndicator.objects.create(name='time_i1',indicator_class='Time Indicator',indicator_family=trigger_family)
    EquityIndicator.objects.create(name='time_i2',indicator_class='Time Indicator',indicator_family=trigger_family)

    #Circuit Breaker Indicators
    EquityIndicator.objects.create(name='cb_i0',indicator_class='Circuit Breaker')
    EquityIndicator.objects.create(name='cb_i1',indicator_class='Circuit Breaker',indicator_family=trigger_family)
    EquityIndicator.objects.create(name='cb_i2',indicator_class='Circuit Breaker',indicator_family=trigger_family)

    #Profit Indicators
    EquityIndicator.objects.create(name='profit_i0',indicator_class='Profit Indicator')
    EquityIndicator.objects.create(name='profit_i1',indicator_class='Profit Indicator',indicator_family=trigger_family)
    EquityIndicator.objects.create(name='profit_i2',indicator_class='Profit Indicator',indicator_family=trigger_family)

    #Immediate Indicators
    EquityIndicator.objects.create(name='now_i0',indicator_class='Immediate Indicator')
    EquityIndicator.objects.create(name='now_i1',indicator_class='Immediate Indicator',indicator_family=trigger_family)
    EquityIndicator.objects.create(name='now_i2',indicator_class='Immediate Indicator',indicator_family=trigger_family)

    #Technical Analysis
    EquityIndicator.objects.create(name='tech_i0',indicator_class='Technical Indicator',indicator_family='Fibonacci')
    EquityIndicator.objects.create(name='tech_i1',indicator_class='Technical Indicator',indicator_family='SMA')
    EquityIndicator.objects.create(name='tech_i2',indicator_class='Technical Indicator',indicator_family='EMA')
    print("Setting up Infrastructure for Testing.")


  def testImmediateIndicator(self):
    ind0 = self.getIndicator(name='now_i0')
    ind1 = self.getIndicator(name='now_i1')
    ind2 = self.getIndicator(name='now_i2')
    self.assertEqual(ind0.isValid(),True)
    self.assertEqual(ind1.isValid(),True)
    self.assertEqual(ind2.isValid(),True)

#Default Indicator is a Time Indicator
  def testTechnicalIndicator(self):
    ind0 = self.getIndicator(name='tech_i0')
    ind1 = self.getIndicator(name='tech_i1')
    ind2 = self.getIndicator(name='tech_i2')
    self.assertEqual(ind0.isValid(),True)
    self.assertEqual(ind1.isValid(),True)
    self.assertEqual(ind2.isValid(),True)

  def testDefaultIndicator(self):
    ind0 = self.getIndicator(name='default_i0')
    ind1 = self.getIndicator(name='default_i1')
    ind2 = self.getIndicator(name='default_i2')
    self.assertEqual(ind0.isValid(),True)
    self.assertEqual(ind1.isValid(),True)
    self.assertEqual(ind2.isValid(),True)

  def testTimeIndicator(self):
    ind0 = self.getIndicator(name='time_i0')
    ind1 = self.getIndicator(name='time_i1')
    ind2 = self.getIndicator(name='time_i1')
    self.assertEqual(ind0.isValid(),True)
    self.assertEqual(ind1.isValid(),True)
    self.assertEqual(ind2.isValid(),True)

  def testVolumeIndicator(self):
    ind0 = self.getIndicator(name='volume_i0')
    ind1 = self.getIndicator(name='volume_i1')
    ind2 = self.getIndicator(name='volume_i2')
    self.assertEqual(ind0.isValid(),True)
    self.assertEqual(ind1.isValid(),True)
    self.assertEqual(ind2.isValid(),True)

  def testManualIndicator(self):
    ind0 = self.getIndicator(name='manual_i0')
    ind1 = self.getIndicator(name='manual_i1')
    ind2 = self.getIndicator(name='manual_i1')
    self.assertEqual(ind0.isValid(),True)
    self.assertEqual(ind1.isValid(),True)
    self.assertEqual(ind2.isValid(),True)

  def testCircuitBreakerIndicator(self):
    ind0 = self.getIndicator(name='cb_i0')
    ind1 = self.getIndicator(name='cb_i1')
    ind2 = self.getIndicator(name='cb_i2')
    self.assertEqual(ind0.isValid(),True)
    self.assertEqual(ind1.isValid(),True)
    self.assertEqual(ind2.isValid(),True)

  def getIndicator(self,name):
    match=name
    indicator = EquityIndicator.objects.get(name=match)
    
    return indicator

#  def createTypedIndicator(self,i_class,i_fam,name):
#    name = name
#    i_class = i_class
#    i_fam = i_fam
#    EquityIndicator.objects.create(name=name,indicator_class=i_class,indicator_family=i_fam)

#    return

#  def createDefaultIndicator(self):
#    EquityIndicator.objects.create(name='default_indicator')

#    return True
		
#  def test_function(self):
#  	return True