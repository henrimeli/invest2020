import datetime, time, pytz, logging, unittest , sys,json
import pandas as pd
from django.utils import timezone
from django.test import TestCase
import dateutil.parser, xmlrunner

# Import Models
from bullbearetfs.robot.activitysentiments.models import EquityAndMarketSentiment
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple, strToDatetime, shouldUsePrint, displayOutput,displayError
#from bullbearetfs.models import CHOICES_SENTIMENTS_SCALE, CHOICES_SENTIMENTS_WEIGHT_SCALE, CHOICES_SENTIMENTS_FEED

logger = logging.getLogger(__name__)

def test_market_dummy(request):
	logger.info("Just a dummy function to force the Build.")


#
# Create Asset Composition based on the Various sentiments around an asset.
# There are 4 entries that influence Sentiment. External, Market, Sector, Top15 Stocks.
# 
######################################################################################################################
# EquityAndMarketSentiment Functionality:
# EquityAndMarketSentiment functionality encapsulates the concept of understanding how we feel about a particular
# Equity, Sector, Market and External Factors.
# Then we can decide if our feeling need to influence how much money we spend on an asset.
#
#
# 
##############################################################################################################
# Tests the functionality around:
#   Check if the market is opened at a given time.
#   Get the market calendar for a given time interval.
#   Helper/Convenience Functionality:
#    -Update the Table with Data from a given interval
#    -Check if Data is uptodate. if yes, do nothing. if no, update it.
#####################################################################################################
#  TestCases:
#@unittest.skip("Taking a break now")
class EquityAndMarketSentimentClassBasicTestCase(TestCase):
  test_name = 'EquityAndMarketSentimentClassBasicTestCase'

  s_bull_bear_0 = ['3x Bearish','2x Bearish','1x Bearish','3x Bearish']
  s_bull_bear_weight_0 = [100,50,100,100]

  s_bull_bear_1 = ['1x Bearish','3x Bearish','1x Bullish','2x Bullish']
  s_bull_bear_weight_1 = [100,100,100,0]

  s_bull_bear_2 = ['2x Bullish','3x Bullish','3x Bearish','3x Bearish']
  s_bull_bear_weight_2 = [0,0,0,0]

  s_bull_bear_3 = ['3x Bullish','Neutral','3x Bearish','3x Bullish']
  s_bull_bear_weight_3 = [0,50,50,100]

  s_bull_bear_4 = ['2x Bullish','3x Bearish','2x Bearish','3x Bullish']
  s_bull_bear_weight_4 = [100,50,0,100]

  s_bull_bear_5 = ['Neutral','3x Bearish','2x Bullish','1x Bearish']
  s_bull_bear_weight_5 = [100,50,100,50]

  s_bull_bear_6 = ['Neutral','Neutral','Neutral','3x Bearish']
  s_bull_bear_weight_6 = [50,50,50,50]

  s_all_bearish = ['3x Bearish','3x Bearish','3x Bearish','3x Bearish']
  s_all_bearish_weight = [100,100,100,100]

  s_all_bullish = ['3x Bullish','3x Bullish','3x Bullish','3x Bullish']
  s_all_bullish_weight = [100,100,100,100]

  s_all_neutral = ['Neutral','Neutral','Neutral','Neutral']
  s_all_neutral_weight = [100,100,100,100]


  s0_id = 0
  s1_id = 0
  s2_id = 0
  s3_id = 0
  s4_id = 0
  s5_id = 0
  s6_id = 0
  s7_id = 0
  s8_id = 0
  s9_id = 0
  
  #
  feed_types = ['Automatic','Manual','','','','']

  @classmethod 
  def setUpTestData(self):
    displayOutput(str="Setting up the test cases for  EquityAndMarketSentimentClassBasicTestCase ... ")
    sentiment_0 = EquityAndMarketSentiment.objects.create(pair_robot=None,influences_acquisition=True,circuit_breaker=False,sentiment_feed='Manual',
            external_sentiment=self.s_bull_bear_0[0], market_sentiment=self.s_bull_bear_0[1], sector_sentiment=self.s_bull_bear_0[2], equity_sentiment=self.s_bull_bear_0[3],
      external_sentiment_weight=self.s_bull_bear_weight_0[0],market_sentiment_weight=self.s_bull_bear_weight_0[1],sector_sentiment_weight=self.s_bull_bear_weight_0[2],
      equity_sentiment_weight=self.s_bull_bear_weight_0[3])
 
    self.s0_id = sentiment_0.pk

    sentiment_1 = EquityAndMarketSentiment.objects.create(pair_robot=None,influences_acquisition=True,circuit_breaker=False,sentiment_feed='Manual',
            external_sentiment=self.s_bull_bear_1[0], market_sentiment=self.s_bull_bear_1[1], sector_sentiment=self.s_bull_bear_1[2], equity_sentiment=self.s_bull_bear_1[3],
      external_sentiment_weight=self.s_bull_bear_weight_1[0],market_sentiment_weight=self.s_bull_bear_weight_1[1],sector_sentiment_weight=self.s_bull_bear_weight_1[2],
      equity_sentiment_weight=self.s_bull_bear_weight_1[3])
 
    self.s1_id = sentiment_1.pk

    sentiment_2 = EquityAndMarketSentiment.objects.create(pair_robot=None,influences_acquisition=True,circuit_breaker=False,sentiment_feed='Manual',
            external_sentiment=self.s_bull_bear_2[0], market_sentiment=self.s_bull_bear_2[1], sector_sentiment=self.s_bull_bear_2[2], equity_sentiment=self.s_bull_bear_2[3],
      external_sentiment_weight=self.s_bull_bear_weight_2[0],market_sentiment_weight=self.s_bull_bear_weight_2[1],sector_sentiment_weight=self.s_bull_bear_weight_2[2],
      equity_sentiment_weight=self.s_bull_bear_weight_2[3])
 
    self.s2_id = sentiment_2.pk

    sentiment_3 = EquityAndMarketSentiment.objects.create(pair_robot=None,influences_acquisition=True,circuit_breaker=False,sentiment_feed='Manual',
            external_sentiment=self.s_bull_bear_3[0], market_sentiment=self.s_bull_bear_3[1], sector_sentiment=self.s_bull_bear_3[2], equity_sentiment=self.s_bull_bear_3[3],
      external_sentiment_weight=self.s_bull_bear_weight_3[0],market_sentiment_weight=self.s_bull_bear_weight_3[1],sector_sentiment_weight=self.s_bull_bear_weight_3[2],
      equity_sentiment_weight=self.s_bull_bear_weight_3[3])
 
    self.s3_id = sentiment_3.pk

    sentiment_4 = EquityAndMarketSentiment.objects.create(pair_robot=None,influences_acquisition=True,circuit_breaker=False,sentiment_feed='Manual',
            external_sentiment=self.s_bull_bear_4[0], market_sentiment=self.s_bull_bear_4[1], sector_sentiment=self.s_bull_bear_4[2], equity_sentiment=self.s_bull_bear_4[3],
      external_sentiment_weight=self.s_bull_bear_weight_4[0],market_sentiment_weight=self.s_bull_bear_weight_4[1],sector_sentiment_weight=self.s_bull_bear_weight_4[2],
      equity_sentiment_weight=self.s_bull_bear_weight_4[3])
 
    self.s4_id = sentiment_4.pk

    sentiment_5 = EquityAndMarketSentiment.objects.create(pair_robot=None,influences_acquisition=True,circuit_breaker=False,sentiment_feed='Manual',
            external_sentiment=self.s_bull_bear_5[0], market_sentiment=self.s_bull_bear_5[1], sector_sentiment=self.s_bull_bear_5[2], equity_sentiment=self.s_bull_bear_5[3],
      external_sentiment_weight=self.s_bull_bear_weight_5[0],market_sentiment_weight=self.s_bull_bear_weight_5[1],sector_sentiment_weight=self.s_bull_bear_weight_5[2],
      equity_sentiment_weight=self.s_bull_bear_weight_5[3])
 
    self.s5_id = sentiment_5.pk

    sentiment_6 = EquityAndMarketSentiment.objects.create(pair_robot=None,influences_acquisition=True,circuit_breaker=False,sentiment_feed='Manual',
            external_sentiment=self.s_bull_bear_6[0], market_sentiment=self.s_bull_bear_6[1], sector_sentiment=self.s_bull_bear_6[2], equity_sentiment=self.s_bull_bear_6[3],
      external_sentiment_weight=self.s_bull_bear_weight_6[0],market_sentiment_weight=self.s_bull_bear_weight_6[1],sector_sentiment_weight=self.s_bull_bear_weight_6[2],
      equity_sentiment_weight=self.s_bull_bear_weight_6[3])
 
    self.s6_id = sentiment_6.pk

####### All Bear, All Bulls, All Neutrals below
    sentiment_7 = EquityAndMarketSentiment.objects.create(pair_robot=None,influences_acquisition=True,circuit_breaker=False,sentiment_feed='Manual',
            external_sentiment=self.s_all_bearish[0], market_sentiment=self.s_all_bearish[1], sector_sentiment=self.s_all_bearish[2], equity_sentiment=self.s_all_bearish[3],
      external_sentiment_weight=self.s_all_bearish_weight[0],market_sentiment_weight=self.s_all_bearish_weight[1],sector_sentiment_weight=self.s_all_bearish_weight[2],
      equity_sentiment_weight=self.s_all_bearish_weight[3])
 
    self.s7_id = sentiment_7.pk

    sentiment_8 = EquityAndMarketSentiment.objects.create(pair_robot=None,influences_acquisition=True,circuit_breaker=False,sentiment_feed='Manual',
            external_sentiment=self.s_all_bullish[0], market_sentiment=self.s_all_bullish[1], sector_sentiment=self.s_all_bullish[2], equity_sentiment=self.s_all_bullish[3],
      external_sentiment_weight=self.s_all_bullish_weight[0],market_sentiment_weight=self.s_all_bullish_weight[1],sector_sentiment_weight=self.s_all_bullish_weight[2],
      equity_sentiment_weight=self.s_all_bullish_weight[3])
 
    self.s8_id = sentiment_8.pk

    sentiment_9 = EquityAndMarketSentiment.objects.create(pair_robot=None,influences_acquisition=True,circuit_breaker=False,sentiment_feed='Manual',
            external_sentiment=self.s_all_neutral[0], market_sentiment=self.s_all_neutral[1], sector_sentiment=self.s_all_neutral[2], equity_sentiment=self.s_all_neutral[3],
      external_sentiment_weight=self.s_all_neutral_weight[0],market_sentiment_weight=self.s_all_neutral_weight[1],sector_sentiment_weight=self.s_all_neutral_weight[2],
      equity_sentiment_weight=self.s_all_neutral_weight[3])
 
    self.s9_id = sentiment_9.pk

  # Sentiment Map:
  # [-1200, +1200] 80/20[-1200,-1000], 75/25[-1000,-800] 70/30[-800,-600] 60/40[-600,-150], 50/50[-150,150], 
                  #[40/60[150-600], 30/70[600,800], 25/75[800,1000], 20/80[1000,1200]
  #
  # Mostly Bearish Sentiment. Sentiment Value around -800
  # 
  #@unittest.skip("Taking a break now")
  def testMarketSentiment0Test(self):
    sent = EquityAndMarketSentiment.objects.get(pk=self.s0_id)

    self.assertEqual(sent.isValid(),True)
    self.assertEqual(sent.external_sentiment,'3x Bearish')
    self.assertEqual(sent.market_sentiment,'2x Bearish')
    self.assertEqual(sent.sector_sentiment,'1x Bearish')
    self.assertEqual(sent.equity_sentiment,'3x Bearish')

    self.assertEqual(sent.isMarketCrashing(),False)
    self.assertEqual(sent.isCircuitBreakerEnabled(),False)
    self.assertEqual(sent.getAssetComposition()['bull'],30) 
    self.assertEqual(sent.getAssetComposition()['bear'],70)


    sent.influences_acquisition = False 
    sent.save()

    self.assertEqual(sent.isMarketCrashing(),False)
    self.assertEqual(sent.isCircuitBreakerEnabled(),False)
    self.assertEqual(sent.getAssetComposition()['bull'],50) 
    self.assertEqual(sent.getAssetComposition()['bear'],50)

  #
  # Bearish
  # weights:  [100,100,100,0]
  #@unittest.skip("Taking a break now")
  def testMarketSentiment1Test(self):
    sent = EquityAndMarketSentiment.objects.get(pk=self.s1_id)
    self.assertEqual(sent.isValid(),True)
    self.assertEqual(sent.external_sentiment,'1x Bearish')
    self.assertEqual(sent.market_sentiment,'3x Bearish')
    self.assertEqual(sent.sector_sentiment,'1x Bullish')
    self.assertEqual(sent.equity_sentiment,'2x Bullish')
    self.assertEqual(sent.calculateValues(),-300)
    self.assertEqual(sent.isMarketCrashing(),False)
    self.assertEqual(sent.isCircuitBreakerEnabled(),False)
    self.assertEqual(sent.getAssetComposition()['bull'],50) 
    self.assertEqual(sent.getAssetComposition()['bear'],50)


  #
  # Bearish/Bullish: NOTE: Weights are all 0
  #s_bull_bear_weight_2 = [0,0,0,0]
  #@unittest.skip("Taking a break now")
  def testMarketSentiment2Test(self):
    sent = EquityAndMarketSentiment.objects.get(pk=self.s2_id)

    self.assertEqual(sent.isValid(),True)
    self.assertEqual(sent.external_sentiment,'2x Bullish')
    self.assertEqual(sent.market_sentiment,'3x Bullish')
    self.assertEqual(sent.sector_sentiment,'3x Bearish')
    self.assertEqual(sent.equity_sentiment,'3x Bearish')
    self.assertEqual(sent.calculateValues(),0)
    self.assertEqual(sent.isMarketCrashing(),False)
    self.assertEqual(sent.isCircuitBreakerEnabled(),False)
    self.assertEqual(sent.getAssetComposition()['bull'],50) 
    self.assertEqual(sent.getAssetComposition()['bear'],50)

  #
  # Bearish/Bullish: 
  #s_bull_bear_weight_ = [0,50,50,100]
  #@unittest.skip("Taking a break now")
  def testMarketSentiment3Test(self):
    sent = EquityAndMarketSentiment.objects.get(id=self.s3_id)
    self.assertEqual(sent.isValid(),True)
    self.assertEqual(sent.external_sentiment,'3x Bullish')
    self.assertEqual(sent.market_sentiment,'Neutral')
    self.assertEqual(sent.sector_sentiment,'3x Bearish')
    self.assertEqual(sent.equity_sentiment,'3x Bullish')
    self.assertEqual(sent.calculateValues(),150)
    self.assertEqual(sent.isMarketCrashing(),False)
    self.assertEqual(sent.isCircuitBreakerEnabled(),False)
    self.assertEqual(sent.getAssetComposition()['bull'],50) 
    self.assertEqual(sent.getAssetComposition()['bear'],50)

  #
  # Bearish/Bullish: 
  #s_bull_bear_weight_4 = [100,50,50,100]
  #@unittest.skip("Taking a break now")
  def testMarketSentiment4Test(self):
    sent = EquityAndMarketSentiment.objects.get(id=self.s4_id)
    self.assertEqual(sent.isValid(),True)
    self.assertEqual(sent.external_sentiment,'2x Bullish')
    self.assertEqual(sent.market_sentiment,'3x Bearish')
    self.assertEqual(sent.sector_sentiment,'2x Bearish')
    self.assertEqual(sent.equity_sentiment,'3x Bullish')
    self.assertEqual(sent.calculateValues(),350)
    self.assertEqual(sent.isMarketCrashing(),False)
    self.assertEqual(sent.isCircuitBreakerEnabled(),False)
    self.assertEqual(sent.getAssetComposition()['bull'],60) 
    self.assertEqual(sent.getAssetComposition()['bear'],40)

  #  s_bull_bear_weight_5 = [100,50,100,50]
  #@unittest.skip("Taking a break now")
  def testMarketSentiment5Test(self):
    sent = EquityAndMarketSentiment.objects.get(id=self.s5_id)
    self.assertEqual(sent.isValid(),True)
    self.assertEqual(sent.external_sentiment,'Neutral')
    self.assertEqual(sent.market_sentiment,'3x Bearish')
    self.assertEqual(sent.sector_sentiment,'2x Bullish')
    self.assertEqual(sent.equity_sentiment,'1x Bearish')
    self.assertEqual(sent.calculateValues(),0)
    self.assertEqual(sent.isMarketCrashing(),False)
    self.assertEqual(sent.isCircuitBreakerEnabled(),False)
    self.assertEqual(sent.getAssetComposition()['bull'],50) 
    self.assertEqual(sent.getAssetComposition()['bear'],50)

  #  s_bull_bear_6 = ['Neutral','Neutral','Neutral','3x Bearish']
  #  s_bull_bear_weight_6 = [50,50,50,50]
  #@unittest.skip("Taking a break now")
  def testMarketSentiment6Test(self):
    sent = EquityAndMarketSentiment.objects.get(id=self.s6_id)
    self.assertEqual(sent.isValid(),True)
    self.assertEqual(sent.external_sentiment,self.s_bull_bear_6[0])
    self.assertEqual(sent.market_sentiment,self.s_bull_bear_6[1])
    self.assertEqual(sent.sector_sentiment,self.s_bull_bear_6[2])
    self.assertEqual(sent.equity_sentiment,self.s_bull_bear_6[3])
    self.assertEqual(sent.calculateValues(),-150)
    self.assertEqual(sent.isMarketCrashing(),False)
    self.assertEqual(sent.isCircuitBreakerEnabled(),False)
    self.assertEqual(sent.getAssetComposition()['bull'],50) 
    self.assertEqual(sent.getAssetComposition()['bear'],50)


  #@unittest.skip("Taking a break now")
  def testMarketSentiment7Test(self):
    sent = EquityAndMarketSentiment.objects.get(id=self.s7_id)
    self.assertEqual(sent.isValid(),True)
    self.assertEqual(sent.external_sentiment,self.s_all_bearish[0])
    self.assertEqual(sent.market_sentiment,self.s_all_bearish[1])
    self.assertEqual(sent.sector_sentiment,self.s_all_bearish[2])
    self.assertEqual(sent.equity_sentiment,self.s_all_bearish[3])
    self.assertEqual(sent.calculateValues(),-1200)
    self.assertEqual(sent.isMarketCrashing(),True)
    self.assertEqual(sent.isCircuitBreakerEnabled(),False)
    self.assertEqual(sent.getAssetComposition()['bull'],20) 
    self.assertEqual(sent.getAssetComposition()['bear'],80)

  #@unittest.skip("Taking a break now")
  def testMarketSentiment8Test(self):
    sent = EquityAndMarketSentiment.objects.get(id=self.s8_id)
    self.assertEqual(sent.isValid(),True)
    self.assertEqual(sent.external_sentiment,self.s_all_bullish[0])
    self.assertEqual(sent.market_sentiment,self.s_all_bullish[1])
    self.assertEqual(sent.sector_sentiment,self.s_all_bullish[2])
    self.assertEqual(sent.equity_sentiment,self.s_all_bullish[3])
    self.assertEqual(sent.calculateValues(),1200)
    self.assertEqual(sent.isMarketCrashing(),False)
    self.assertEqual(sent.isCircuitBreakerEnabled(),False)
    self.assertEqual(sent.getAssetComposition()['bull'],80) 
    self.assertEqual(sent.getAssetComposition()['bear'],20)

  #@unittest.skip("Taking a break now")
  def testMarketSentiment9Test(self):
    sent = EquityAndMarketSentiment.objects.get(id=self.s9_id)
    self.assertEqual(sent.isValid(),True)
    self.assertEqual(sent.external_sentiment,self.s_all_neutral[0])
    self.assertEqual(sent.market_sentiment,self.s_all_neutral[1])
    self.assertEqual(sent.sector_sentiment,self.s_all_neutral[2])
    self.assertEqual(sent.equity_sentiment,self.s_all_neutral[3])
    self.assertEqual(sent.calculateValues(),0)
    self.assertEqual(sent.isMarketCrashing(),False)
    self.assertEqual(sent.isCircuitBreakerEnabled(),False)
    self.assertEqual(sent.getAssetComposition()['bull'],50) 
    self.assertEqual(sent.getAssetComposition()['bear'],50)


##############################################################################################################
# Tests the functionality around:
#   Check if the market is opened at a given time.
#   Get the market calendar for a given time interval.
#   Helper/Convenience Functionality:
#    -Update the Table with Data from a given interval
#    -Check if Data is uptodate. if yes, do nothing. if no, update it.
#####################################################################################################
#  TestCases:
#@unittest.skip("Taking a break now")
class EquityAndMarketWithRandomAssetComposition(TestCase):
  test_name = 'EquityAndMarketAssetDynamicComposition'
  s_bull_bear_0 = ['3x Bearish','2x Bearish','1x Bearish','3x Bearish']
  s_bull_bear_weight_0 = [100,50,100,100]


  #
  feed_types = ['Automatic','Manual','','','','']

  @classmethod 
  def setUpTestData(self):
    displayOutput(str="Setting up the test cases for  {} ".format( self.test_name))
    sentiment_0 = EquityAndMarketSentiment.objects.create(pair_robot=None,influences_acquisition=True,circuit_breaker=False,sentiment_feed='Automatic',
            external_sentiment=self.s_bull_bear_0[0], market_sentiment=self.s_bull_bear_0[1], sector_sentiment=self.s_bull_bear_0[2], equity_sentiment=self.s_bull_bear_0[3],
      external_sentiment_weight=self.s_bull_bear_weight_0[0],market_sentiment_weight=self.s_bull_bear_weight_0[1],sector_sentiment_weight=self.s_bull_bear_weight_0[2],
      equity_sentiment_weight=self.s_bull_bear_weight_0[3])
 
    self.s0_id = sentiment_0.pk

  # Sentiment Map:
  # [-1200, +1200] 80/20[-1200,-1000], 75/25[-1000,-800] 70/30[-800,-600] 60/40[-600,-150], 50/50[-150,150], 
                  #[40/60[150-600], 30/70[600,800], 25/75[800,1000], 20/80[1000,1200]
  #CHOICES_COMPOSITION_CALCULATION  = (('Random','Random'),('A1','A1'),('A2','A2'),('A3','A3'),('A4','A4'),('A5','A5'),('A6','A6'))

  #
  # Random Composition Tests: Any composition between -1200 and 1200 to be chosen 
  # Only 1 Random Composition is created.
  #
  #@unittest.skip("Taking a break now")
  def testSingleRandomCompositionTest(self):
    sent = EquityAndMarketSentiment.objects.get(pk=self.s0_id)
    sent.composition_calc='Random'
    sent.save()

    self.assertEqual(sent.isValid(),True)
    self.assertTrue(sent.calculateValues()>= -1200)
    self.assertTrue(sent.calculateValues()<= 1200)
    self.assertEqual(sent.isMarketCrashing(),False)
    self.assertEqual(sent.isCircuitBreakerEnabled(),False)
    composition = sent.getAssetComposition()
    self.assertTrue(composition['bull']>=20) 
    self.assertTrue(composition['bear']<=80)

  #
  # Random Composition Tests: Any composition between -1200 and 1200 to be chosen 
  # Neutral is not permitted
  @unittest.skip("Composition must be fixed.")
  def testRandomCompositionNoNeutralTest(self):
    sent = EquityAndMarketSentiment.objects.get(pk=self.s0_id)
    sent.composition_calc='Random'
    sent.ignore_neutral_outcome=True
    sent.save()

    self.assertEqual(sent.isValid(),True)
    self.assertTrue(sent.calculateValues()>= -1200)
    self.assertTrue(sent.calculateValues()<= 1200)
    self.assertEqual(sent.isMarketCrashing(),False)
    self.assertEqual(sent.isCircuitBreakerEnabled(),False)

    #Run is several times in a row and make sure you don't always get the same answers
    composition1 = sent.getAssetComposition()
    self.assertTrue(composition1['bull']>=20) 
    self.assertTrue(composition1['bear']<=80)
    self.assertFalse(composition1['bear']==50)
    self.assertFalse(composition1['bull']==50)

    composition2 = sent.getAssetComposition()
    self.assertTrue(composition2['bull']>=20) 
    self.assertTrue(composition2['bear']<=80)
    self.assertFalse(composition2['bear']==50)
    self.assertFalse(composition2['bull']==50)

    composition3 = sent.getAssetComposition()
    self.assertTrue(composition3['bull']>=20) 
    self.assertTrue(composition3['bear']<=80)
    self.assertFalse(composition3['bear']==50)
    self.assertFalse(composition3['bull']==50)
    #TODO: Fix me    
    self.assertEqual(composition1['bull'],composition2['bull'])

  #
  #
  # Single Layer Random Composition Tests: Any composition between -1200 and 1200 to be chosen
  #  
  # Neutral IS Permitted
  # Bull/Bear Composition will alternate between Positive / Negative
  # I.e.: 80/20 , 30/70, 75/25, 25/75, 50/50, ... etc.
  #
  @unittest.skip("Taking a break now")
  def testAlternatingRandomTest(self):
    sent = EquityAndMarketSentiment.objects.get(pk=self.s0_id)
    sent.composition_calc='A1'
    sent.ignore_neutral_outcome=False
    sent.save()

    self.assertEqual(False,True)
    self.assertEqual(sent.isValid(),True)
    self.assertEqual(sent.calculateValues(),0)
    self.assertEqual(sent.isMarketCrashing(),False)
    self.assertEqual(sent.isCircuitBreakerEnabled(),False)
    self.assertEqual(sent.getAssetComposition()['bull'],50) 
    self.assertEqual(sent.getAssetComposition()['bear'],50)

  #
  #
  # Single Layer Random Composition Tests No Neutral Permitted: 
  # Bull/Bear Composition will alternate between Positive / Negative
  # I.e.: 80/20 , 30/70, 75/25, 25/75, ... etc.
  # 50/50 is NOT allowed in this area
  @unittest.skip("Taking a break now")
  def testAlternatingRandomNoNeutralTest(self):
    sent = EquityAndMarketSentiment.objects.get(pk=self.s0_id)
    sent.composition_calc='A1'
    sent.ignore_neutral_outcome=True
    sent.save()
    self.assertEqual(False,True)
    self.assertEqual(sent.isValid(),True)
    self.assertEqual(sent.calculateValues(),0)
    self.assertEqual(sent.isMarketCrashing(),False)
    self.assertEqual(sent.isCircuitBreakerEnabled(),False)
    self.assertEqual(sent.getAssetComposition()['bull'],50) 
    self.assertEqual(sent.getAssetComposition()['bear'],50)
  
  #
  # Single Layer Random Composition Tests: Any composition between -1200 and 1200 to be chosen
  #  
  # Neutral is not permitted
  # 
  @unittest.skip("Taking a break now")
  def testSingleLayerAlternatingRandomTest(self):
    sent = EquityAndMarketSentiment.objects.get(pk=self.s0_id)
    sent.composition_calc='A1'
    sent.ignore_neutral_outcome=False
    sent.save()

    self.assertEqual(sent.isValid(),True)
    self.assertEqual(sent.calculateValues(),0)
    self.assertEqual(sent.isMarketCrashing(),False)
    self.assertEqual(sent.isCircuitBreakerEnabled(),False)
    self.assertEqual(sent.getAssetComposition()['bull'],50) 
    self.assertEqual(sent.getAssetComposition()['bear'],50)


##################################################################################################################
# Bull/Bear Asset Composition at the time of Purchase is really key to achieving acceptable profits in the market.
# Having a rigid / manually changeable Asset Composition limits the ability to ...
# It is therefore important to understand/see trends as early as possible, so that one can capitalize on those trends
# within our window of operation to maximize our profits.
# Tests the functionality around:
#
#   Check if the market is opened at a given time.
#   Get the market calendar for a given time interval.
#   Helper/Convenience Functionality:
#    -Update the Table with Data from a given interval
#    -Check if Data is uptodate. if yes, do nothing. if no, update it.
#####################################################################################################
#  TestCases:
#@unittest.skip("Taking a break now")
class EquityAndMarketWithKnowledgeBasedAssetComposition(TestCase):
  test_name = 'EquityAndMarketWithKnowledgeBasedAssetComposition'
  s_bull_bear_0 = ['3x Bearish','2x Bearish','1x Bearish','3x Bearish']
  s_bull_bear_weight_0 = [100,50,100,100]


  #
  feed_types = ['Automatic','Manual','','','','']

  @classmethod 
  def setUpTestData(self):
    displayOutput("\nSetting up the test cases for {}.".format(self.test_name))
  
    sentiment_0 = EquityAndMarketSentiment.objects.create(pair_robot=None,influences_acquisition=True,circuit_breaker=False,sentiment_feed='Automatic',
            external_sentiment=self.s_bull_bear_0[0], market_sentiment=self.s_bull_bear_0[1], sector_sentiment=self.s_bull_bear_0[2], equity_sentiment=self.s_bull_bear_0[3],
      external_sentiment_weight=self.s_bull_bear_weight_0[0],market_sentiment_weight=self.s_bull_bear_weight_0[1],sector_sentiment_weight=self.s_bull_bear_weight_0[2],
      equity_sentiment_weight=self.s_bull_bear_weight_0[3])
 
    self.s0_id = sentiment_0.pk


  #
  # EggheadSimpleMoving Average Based on either all Actives, only Composition Tests: Any composition between -1200 and 1200 to be chosen 
  # Only 1 Random Composition is created.
  #
  # 
  #
  @unittest.skip("Taking a break now")
  def testSimpleEggheadMovingAverage(self):
    sent = EquityAndMarketSentiment.objects.get(pk=self.s0_id)
    sent.composition_calc='A3'
    sent.save()

    self.assertEqual(False,True)
    self.assertEqual(sent.isValid(),True)
    self.assertTrue(sent.calculateValues()>= -1200)
    self.assertTrue(sent.calculateValues()<= 1200)
    self.assertEqual(sent.isMarketCrashing(),False)
    self.assertEqual(sent.isCircuitBreakerEnabled(),False)
    composition = sent.getAssetComposition()
    self.assertTrue(composition['bull']>=20) 
    self.assertTrue(composition['bear']<=80)

  #
  # Uses the Price Spread to determine the next good Asset Composition.
  #  Trending Negative, higher bull Composition
  #
  #@unittest.skip("Taking a break now")
  def testPortfolioTrendingNegativeHighBullOwnership(self):
    sent = EquityAndMarketSentiment.objects.get(pk=self.s0_id)
    sent.composition_calc='A4'
    sent.save()

    self.assertEqual(sent.isValid(),True)
    self.assertEqual(sent.isMarketCrashing(),False)
    self.assertEqual(sent.isCircuitBreakerEnabled(),False)
    stable_portfolio_trend = dict()
    #3. How many negative spread attributed to Bears?
    stable_portfolio_trend = dict()
    stable_portfolio_trend['type'] = 'stable_value_spread'
    stable_portfolio_trend['spread_total_value'] = -50
    stable_portfolio_trend['current_bull_composition'] = 60
    stable_portfolio_trend['current_bear_composition'] = 40

    composition = sent.getAssetComposition(current_trend = stable_portfolio_trend)
    self.assertTrue(composition['bull']<=50) 
    self.assertTrue(composition['bear']>=50)

  #
  # Uses the Price Spread to determine the next good Asset Composition.
  #  Trending Negative, higher Bear Composition
  #
  @unittest.skip("TODO: Taking a break now")
  def testPortfolioTrendingNegativeHighBearOwnership(self):
    sent = EquityAndMarketSentiment.objects.get(pk=self.s0_id)
    sent.composition_calc='A4'
    sent.save()

    self.assertEqual(sent.isValid(),True)
    self.assertEqual(sent.isMarketCrashing(),False)
    self.assertEqual(sent.isCircuitBreakerEnabled(),False)
    stable_portfolio_trend = dict()
    #3. How many negative spread attributed to Bears?
    stable_portfolio_trend = dict()
    stable_portfolio_trend['type'] = 'stable_value_spread'
    stable_portfolio_trend['spread_total_value'] = -50
    stable_portfolio_trend['current_bull_composition'] = 40
    stable_portfolio_trend['current_bear_composition'] = 60

    composition = sent.getAssetComposition(current_trend = stable_portfolio_trend)
    print(" {}".format(composition['bull']))
    self.assertTrue(composition['bull']<=50) 
    self.assertTrue(composition['bear']>=50)

if __name__ == '__main__':
  unittest.main(
        testRunner=xmlrunner.XMLTestRunner(),
        # these make sure that some options that are not applicable
        # remain hidden from the help menu.
        failfast=False, buffer=False, catchbreak=False)
