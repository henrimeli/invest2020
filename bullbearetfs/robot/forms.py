from django import forms
from django.forms import ModelForm
from django.forms.formsets import BaseFormSet
from bullbearetfs.robot.symbols.models import RobotEquitySymbols, BullBearETFData
from bullbearetfs.robot.budget.models import RobotBudgetManagement, Portfolio
from bullbearetfs.robot.activitysentiments.models import RobotActivityWindow, EquityAndMarketSentiment
from bullbearetfs.models import EquityTradingRobot
from bullbearetfs.models import EquityTradingData
from bullbearetfs.executionengine.models import ETFPairRobotExecution
#from bullbearetfs.models import CHOICES_USE_CASH_OR_NUMBER
from bullbearetfs.strategy.models import OrdersManagement
from bullbearetfs.robot.models import ETFAndReversePairRobot 

from functools import partial

DateInput = partial(forms.DateInput, {'class': 'datepicker'})

# This form is used to create a new Execution Instance.
# When a Backtest is run, a new Execution Instance is created and performed 
class RobotExecutionCreationForm(ModelForm):
  class Meta:
    model = ETFPairRobotExecution
    fields = ['creation_date','exec_start_date','exec_end_date','robot','result_data',
              'execution_name','execution_pace','visual_mode','execution_status' ]
    labels = {'creation_date':'Creation Date','exec_start_date':'Start Date','exec_end_date':'End Date',
              'execution_name':'Execution Name','execution_pace':' Execution Pace','visual_mode':'Visual Mode',
              'execution_status':'Execution Status'}

  #def __init__(self, *args, **kwargs):
  #  super(RobotExecutionCreationForm,self).__init__(*args,**kwargs)
  # self.fields['exec_start_date'] = forms.DateField(widget=DateInput())
  #    self.fields['execution_name'] = 'Hello World'




class ETFAndReversePairExecutionForm2(forms.Form):
  start_date = forms.DateField(widget=DateInput())
  end_date = forms.DateField(widget=DateInput())

  def __init__(self, *args, **kwargs):
    super(ETFAndReversePairExecutionForm,self).__init__(*args,**kwargs)
    #self.start_date['creation_date'].disabled = False
    #self.end_date['end_date'].disabled = False
    self.context = dict()
    self.title_dict = dict()

  #
  def setRowAndColumnsLabels(self):
    self.title_dict["creation_date"]="Start Date"
    self.title_dict["end_date"] ="End Date"

# This is the form for creating and editing new EquityTradingRobot. 
# A ModelForm is created. 
class ETFAndReversePairRobotCreationForm(ModelForm):
  class Meta:
    model = ETFAndReversePairRobot
    fields = ['name','enabled', 'max_roundtrips','cost_basis_per_roundtrip','profit_target_per_roundtrip','max_hold_time',
              'creation_date','owner','description','visibility','version','cost_basis_per_roundtrip','data_source_choice',
              'minimum_hold_time','hold_time_includes_holiday','symbols','strategy','portfolio','max_sell_transactions_per_day']

    labels = {'name':'Robot Name','description':'Robot Description','owner':'Robot Owner','enabled':'Enabled','max_hold_time':'Maximum Hold Time',
              'visibility':'Visible','version':'Version','creation_date':'Creation Date','profit_target_per_roundtrip':'Profit Target per Roundtrip',
              'max_roundtrips':'Max Number of Roundtrips','cost_basis_per_roundtrip':'Cost Basis per Roundtrip ($)',
              'max_sell_transactions_per_day':'Max Number Of Allowed Daily Sell','max_asset_hold_time':'Maximum Asset Hold Time','hold_time_includes_holiday':'Hold Time includes Holidays?',
              'portfolio':'Portfolio','symbols':'Equity Selection','strategy':'Robot Strategy','data_source_choice':'Data Source'}
    help_texts = {'name':'Enter a valid name','description':'Enter a valid Description','modify_date':'Last modified'}

  def __init__(self, *args, **kwargs):
    super(ETFAndReversePairRobotCreationForm,self).__init__(*args,**kwargs)
    self.fields['creation_date'].disabled = True

# This is the form for creating and editing new EquityTradingRobot. 
# A ModelForm is created. 
class ETFAndReversePairRobotInformationForm(ModelForm):
  class Meta:
    model = ETFAndReversePairRobot
    fields = ['name','enabled','strategy','max_roundtrips','cost_basis_per_roundtrip','profit_target_per_roundtrip',
              'creation_date','owner','description','visibility','version','cost_basis_per_roundtrip','data_source_choice',
              'minimum_hold_time','hold_time_includes_holiday','live_data_check_interval','max_hold_time',
              'symbols','internal_name','sell_remaining_before_buy','profit_target_per_roundtrip',
             'liquidate_on_next_opportunity','modify_date','portfolio','max_sell_transactions_per_day']
    labels = {'name':'Robot Name','description':'Robot Description','owner':'Robot Owner','enabled':'Enabled','max_hold_time':'Maximu Hold Time',
              'visibility':'Visible','version':'Version','creation_date':'Creation Date','profit_target_per_roundtrip':'Profit Target per Roundtrip:',
              'max_roundtrips':'Max Number of Roundtrips','cost_basis_per_roundtrip':'Cost Basis per Roundtrip ($):',
              'max_asset_hold_time':'Maximum Asset Hold Time','hold_time_includes_holiday':'Hold Time includes Holidays?',
              'portfolio':'Portfolio','symbols':'Equity Selection','strategy':'Robot Strategy','data_source_choice':'Data Source',
              'live_data_check_interval':'Pause Between Trades (seconds)','minimum_hold_time':'Minimum Hold Time (trading sessions)',
              'internal_name':'Internal Name','sell_remaining_before_buy':'Dispose all before new Purchases',
              'liquidate_on_next_opportunity':'Liquidate all assets at next Opportunity','max_sell_transactions_per_day':'Max Number Of Allowed Daily Sell'}
    help_texts = {'name':'Enter a valid name','description':'Enter a valid Description','modify_date':'Last modified'}

  def __init__(self, *args, **kwargs):
    super(ETFAndReversePairRobotInformationForm,self).__init__(*args,**kwargs)
    self.fields['creation_date'].disabled = True
    self.fields['modify_date'].disabled = True
    self.fields['internal_name'].disabled = True

# This is the form for creating and editing new EquityTradingRobot. 
# A ModelForm is created. 
class ETFAndReversePairRobotUpdateForm(ModelForm):
  class Meta:
    model = ETFAndReversePairRobot
    fields = ['name','enabled','strategy', 'max_roundtrips','cost_basis_per_roundtrip','profit_target_per_roundtrip',
              'creation_date','owner','description','visibility','version','max_hold_time',
              'minimum_hold_time','hold_time_includes_holiday','live_data_check_interval','cost_basis_per_roundtrip',
              'data_source_choice','symbols','internal_name','sell_remaining_before_buy','profit_target_per_roundtrip',
             'liquidate_on_next_opportunity','modify_date']

    labels = {'name':'Robot Name','description':'Robot Description','owner':'Robot Owner','enabled':'Enabled','max_hold_time':'Maximum Hold Time',
              'visibility':'Visible','version':'Version','creation_date':'Creation Date','profit_target_per_roundtrip':'Profit Target per Roundtrip',
              'max_roundtrips':'Max Number of Roundtrips','cost_basis_per_roundtrip':'Cost Basis per Roundtrip ($)',
              'strategy':'Robot Strategy','max_asset_hold_time':'Maximum Asset Hold Time',
              'hold_time_includes_holiday':'Hold Time includes Holidays?','live_data_check_interval':'Pause Between Trades (seconds)',
              'data_feed_frequency':'Data Feed Frequency(Beta Test Only)','portfolio':'Portfolio','symbols':'Equity Symbols',
              'internal_name':'Internal Name','sell_remaining_before_buy':'Dispose all before new Purchases',
              'liquidate_on_next_opportunity':'Liquidate all assets at next Opportunity','symbols':'Equity Selection'}
    help_texts = {'name':'Enter a valid name','description':'Enter a valid Description','modify_date':'Last modified'}

  def __init__(self, *args, **kwargs):
    super(ETFAndReversePairRobotForm,self).__init__(*args,**kwargs)
    self.fields['creation_date'].disabled = True
    self.fields['symbols'].disabled = True
    self.fields['internal_name'].disabled = True


# This represents data calculated. 
class CompletedRoundTripForm(forms.Form):
  
  def __init__(self,*args,**kwargs):
    self.user_name = kwargs.pop('user_name',None)
    roundtrip_data = kwargs.pop('roundtrip_data',None)
    self.summary_data = roundtrip_data['summary_data']
    self.content_data = roundtrip_data['content_data']
    self.context = dict()
    self.title_dict = dict()
    self.summary_metrics=dict()
    self.data_metrics = dict()
    print("Completed: summary_data. {0}".format(self.summary_data))
    print("Completed: content_data. {0}".format(self.content_data))
    super(CompletedRoundTripForm,self).__init__(*args, **kwargs)

  # Tables Columns, Raw Labels
  def setRowAndColumnsLabels(self):
    self.title_dict["completed1_title"]="Summary Completed"
    self.title_dict["completed1_col1"] ="completed"
    self.title_dict["completed1_col2"] ="successful"
    self.title_dict["completed1_col3"] ="unsuccessful"
    self.title_dict["completed1_col4"] ="average_profit"
    self.title_dict["completed1_col5"] ="average_age"      
    self.title_dict["completed1_col6"] ="unsuccessful"
    self.title_dict["completed1_col7"] ="average_profit"
    self.title_dict["completed1_col8"] ="average_age"      
    self.title_dict["completed2_title"] ="Data From 5 Most Recent Roundtrips"
    self.title_dict["completed2_col1"] ="buy_date"
    self.title_dict["completed2_col2"] ="sell_date"
    self.title_dict["completed2_col3"] ="profit"
    self.title_dict["completed2_col4"] ="buy_date"
    self.title_dict["completed2_col5"] ="sell_date"
    self.title_dict["completed2_col6"] ="profit"
    self.title_dict["completed2_col7"] ="buy_date"
    self.title_dict["completed2_col8"] ="sell_date"
    self.title_dict["completed2_col9"] ="profit"
    
  def calculateValues(self):
    self.summary_metrics['completed']   = self.summary_data['completed_size']
    self.summary_metrics['successful']  = self.summary_data['successful']
    self.summary_metrics['unsuccessful']= self.summary_data['unsuccessful']
    self.summary_metrics['average_age'] = self.summary_data['average_age']
    self.summary_metrics['average_profit']= self.summary_data['average_profit']
    self.summary_metrics['average_time']  = self.summary_data['average_profit']

 # Returns the Context Data
  def contextData(self,**kwargs):
    #Put it all together now.
    self.setRowAndColumnsLabels()
    self.calculateValues()
    self.context["completed_tables"]=self.title_dict
    self.context["summary_metrics"]=self.summary_metrics
    self.context['data_metrics']=self.content_data

    return self.context

# This represents data (listing) to be pulled from a table 
# A ModelForm is created using the Model Data
class InTransitionRoundTripForm(forms.Form):
  
  def __init__(self,*args,**kwargs):
    self.user_name = kwargs.pop('user_name',None)
    roundtrip_data =kwargs.pop('roundtrip_data',None)
    self.summary_data = roundtrip_data['summary_data']
    self.content_data = roundtrip_data['content_data']
    self.context = dict()
    self.title_dict = dict()
    self.summary_metrics=dict()
    self.data_metrics = dict()
    print("InTransition: summary_data. {0}".format(self.summary_data))
    print("InTransition: content_data. {0}".format(self.content_data))
    super(InTransitionRoundTripForm,self).__init__(*args, **kwargs)

    # Tables Columns, Raw Labels
  def setRowAndColumnsLabels(self):
    self.title_dict["t1_title"]="In Transition Table"
    self.title_dict["t1_col1"] ="best_bear"
    self.title_dict["t1_col2"] ="best_bull"
    self.title_dict["t1_col3"] ="youngest"
    self.title_dict["t1_col4"] ="best_value"
    self.title_dict["t1_col5"] ="average_age"      
    self.title_dict["t1_col6"] ="unsuccessful"
    self.title_dict["t1_col7"] ="average_profit"
    self.title_dict["t1_col8"] ="average_age"      
    self.title_dict["t2_title"] ="Data From 5 Most Recent Roundtrips"
    self.title_dict["t2_col1"] ="buy_date"
    self.title_dict["t2_col2"] ="sell_date"
    self.title_dict["t2_col3"] ="profit"
    self.title_dict["t2_col4"] ="buy_date"
    self.title_dict["t2_col5"] ="sell_date"
    self.title_dict["t2_col6"] ="profit"
    self.title_dict["t2_col7"] ="buy_date"
    self.title_dict["t2_col8"] ="sell_date"
    self.title_dict["t2_col9"] ="profit"

  def calculateValues(self):
    self.summary_metrics['intransition']   = self.summary_data['intransition_size']
    self.summary_metrics['best_bear']  = self.summary_data['best_bear']
    self.summary_metrics['best_bull']= self.summary_data['best_bull']
    self.summary_metrics['youngest'] = self.summary_data['youngest']
    self.summary_metrics['best_value']= self.summary_data['best_value']
    #self.summary_metrics['average_time']  = self.summary_data['average_profit']

 # Returns the Context Data
  def contextData(self,**kwargs):
    #Put it all together now.
    self.setRowAndColumnsLabels()
    self.calculateValues()
    self.context["in_transition_tables"]=self.title_dict
    self.context["summary_metrics"]=self.summary_metrics
    self.context['data_metrics']=self.content_data

    return self.context

# This represents data (listing) to be pulled from a table 
class StableRoundTripForm(forms.Form):
  
  def __init__(self,*args,**kwargs):
    self.user_name = kwargs.pop('user_name',None)
    roundtrip_data =kwargs.pop('roundtrip_data',None)
    self.summary_data = roundtrip_data['summary_data']
    self.content_data = roundtrip_data['content_data']
    self.context = dict()
    self.title_dict = dict()
    self.summary_metrics=dict()
    self.data_metrics = dict()
    print("Stable: summary_data. {0}".format(self.summary_data))
    print("Stable: content_data. {0}".format(self.content_data))
    super(StableRoundTripForm,self).__init__(*args, **kwargs)


  # Tables Columns, Raw Labels
  def setRowAndColumnsLabels(self):
    self.title_dict["t1_title"]="Summary of Stable Table"
    self.title_dict["t1_col1"] ="stable_size"
    self.title_dict["t1_col1"] ="cost_basis"
    self.title_dict["t1_col1"] ="bull_cost_basis"
    self.title_dict["t1_col1"] ="bear_cost_basis"
    self.title_dict["t1_col1"] ="average_age"      
    self.title_dict["t1_col1"] ="stable_size"
    self.title_dict["t1_col1"] ="cost_basis"
    self.title_dict["t1_col1"] ="bull_cost_basis"      
    self.title_dict["t2_title"] ="Data From All Stable Roundtrips"
    self.title_dict["t2_col1"] ="delta"
    self.title_dict["t2_col1"] ="buy_date"
    self.title_dict["t2_col1"] ="profit"
    self.title_dict["t2_col1"] ="duration"
    self.title_dict["t2_col1"] ="delta"
    self.title_dict["t2_col1"] ="profit"
    self.title_dict["t2_col1"] ="buy_date"
    self.title_dict["t2_col1"] ="buy_date"
    self.title_dict["t2_col1"] ="profit"

  def calculateValues(self):
    self.summary_metrics['stable_size']         = self.summary_data['stable_size']
    self.summary_metrics['cost_basis']          = self.summary_data['bull_cheapest']
    self.summary_metrics['bull_cost_basis']     = self.summary_data['bull_cheapest']
    self.summary_metrics['bear_cost_basis']     = self.summary_data['bull_cheapest']
    self.summary_metrics['current_bull_price']  = self.summary_data['bull_cheapest']
    self.summary_metrics['current_bear_price']  = self.summary_data['bull_cheapest']

 # Returns the Context Data
  def contextData(self,**kwargs):
    #Put it all together now.
    self.setRowAndColumnsLabels()
    self.calculateValues()
    self.context["stable_tables"]=self.title_dict
    self.context["summary_metrics"]=self.summary_metrics
    self.context['data_metrics']=self.content_data

    return self.context

#######################################################################################################################
# This is the form for creating and editing new EquityTradingRobot. 
# A ModelForm is created. 
class EquityTradingRobotForm(ModelForm):
  class Meta:
    model = EquityTradingRobot
    fields = ['name','owner','visibility', 'description','active','deployed','version','strategy',
              'max_asset_hold_time','hold_time_includes_holiday','live_data_check_interval',
              'data_feed_frequency','portfolio','symbols','internal_name','sell_remaining_before_buy',
              'liquidate_on_next_opportunity','modify_date','symbols']
    labels = {'name':'Robot Name','description':'Robot Description','owner':'Robot Owner','visibility':'Private',
              'active':'Active','deployed':'Deployed','version':'Version','strategy':'Robot Strategy Selection','max_asset_hold_time':'Maximum Asset Hold Time',
              'hold_time_includes_holiday':'Hold Time includes Holidays?','live_data_check_interval':'Pause Between Trades (seconds)',
              'data_feed_frequency':'Data Feed Frequency(Beta Test Only)','portfolio':'Portfolio','symbols':'Equity Symbols',
              'internal_name':'Internal Name','sell_remaining_before_buy':'Dispose all before new Purchases',
              'liquidate_on_next_opportunity':'Liquidate all assets at next Opportunity','symbols':'Equity Selection'}
    help_texts = {'name':'Enter a valid name','description':'Enter a valid Description','modify_date':'Last modified'}

  def __init__(self, *args, **kwargs):
    super(EquityTradingRobotForm,self).__init__(*args,**kwargs)
    self.fields['version'].disabled = True
    self.fields['internal_name'].disabled = True
    self.fields['modify_date'].disabled = True
# Information Form
class RobotInformationForm(ModelForm):
  class Meta:
    model = EquityTradingRobot
    fields = ['name','owner','visibility', 'description','active','deployed','version','strategy',
              'max_asset_hold_time','hold_time_includes_holiday','live_data_check_interval',
              'data_feed_frequency','portfolio','symbols','internal_name','sell_remaining_before_buy',
              'liquidate_on_next_opportunity','modify_date']
    labels = {'name':'Robot Name','description':'Robot Description','owner':'Robot Owner','visibility':'Private',
              'active':'Active','deployed':'Deployed','version':'Version','strategy':'Robot Strategy Selection','max_asset_hold_time':'Maximum Asset Hold Time (days)',
              'hold_time_includes_holiday':'Hold Time includes Holidays?','live_data_check_interval':'Pause Between Trades (seconds)',
              'data_feed_frequency':'Data Feed Frequency(Beta Test Only)','portfolio':'Portfolio','symbols':'Equity Symbols',
              'internal_name':'Internal Name','sell_remaining_before_buy':'Dispose all before new Purchases',
              'liquidate_on_next_opportunity':'Liquidate all assets at next Opportunity','modify_date':'Last modified'}
    help_texts = {'name':'Enter a valid name','description':'Enter a valid Description'}

  def __init__(self, *args, **kwargs):
    super(RobotInformationForm,self).__init__(*args,**kwargs)	
    self.fields['version'].disabled = True	
    self.fields['internal_name'].disabled = True
    self.fields['modify_date'].disabled = True


class RobotTradingSecurityForm(ModelForm):
  class Meta:
    model = EquityTradingRobot
    fields = ['name','owner']
    labels = {'name':'Robot Name','description':'Robot Description'}
    help_texts = {'name':'Enter a valid name','description':'Enter a valid Description'}


class RobotNotificationForm(ModelForm):
  class Meta:
    model = EquityTradingRobot
    fields = ['name','owner']
    labels = {'name':'Robot Name','description':'Robot Description'}
    help_texts = {'name':'Enter a valid name','description':'Enter a valid Description'}

# Consolidation of Robot:
class RobotEquitySymbolsForm(forms.Form):
  
  def __init__(self, *args, **kwargs):
    self.user_name = kwargs.pop('user_name',None)
    self.context = dict()
    self.title_dict = dict()
    super(RobotEquitySymbolsForm,self).__init__(*args,**kwargs)
    # Tables Columns, Raw Labels

  def setRowAndColumnsLabels(self):
    self.title_dict["title"]="This the Equities Table Title"
    self.title_dict["col1"] ="Symbol"
    self.title_dict["col2"] ="Price"
    self.title_dict["col3"] ="Open"
    self.title_dict["col4"] ="Close"
    self.title_dict["col5"] ="7 day High"
    self.title_dict["col6"] ="7 day Low"
    self.title_dict["col7"] ="col7"
    self.title_dict["col8"] ="col8"
    self.title_dict["col9"] ="col9"
    self.title_dict["col10"] ="col10"
    self.title_dict["col11"] ="col11"
    self.title_dict["col12"] ="col12"

  # Returns the Context Data
  def contextData(self):
    self.setRowAndColumnsLabels()
    return self.context


class RobotEquitySymbolsFormDeleteme(ModelForm):
  class Meta:
    model = RobotEquitySymbols
    fields = ['symbol','bullishSymbol','bearishSymbol']
    labels = {'symbol':'Symbol','bullishSymbol':'Bullish','bearishSymbol':'Bearish'}

    def __init__(self, *args, **kwargs):
      self.user_name = kwargs.pop('user_name',None)
      self.stable_data = kwargs.pop('roundtrip_data',None)
      self.fields['symbol'].disabled = True
      self.fields['bullishSymbol'].disabled = True
      self.fields['bearishSymbol'].disabled = True
      super(RobotEquitySymbolsFormDeleteme,self).__init__(*args,**kwargs)


# This is the form for creating and editing new Robot Activity Policy. 
# A ModelForm is created using the Model Data
class RobotActivityWindowForm(ModelForm):
	class Meta:
		model = RobotActivityWindow
		fields = ['trade_before_open','trade_after_close','offset_after_open','offset_before_close',
		          'blackout_midday_from','blackout_midday_time_interval','live_data_feed']
		labels = {'trade_before_open':'Trade Before Open  [7:00am - 9:30am]?','trade_after_close':'Trade After Close  [4:00pm - 7:00pm]?',
		          'offset_before_close':'Blackout before Close (in minutes)','offset_after_open':'Blackout after Open (in minutes)',
		          'blackout_midday_from':'Blackout Midday from (time): ','blackout_midday_time_interval':'Blackout Interval (in minutes)',
		          'live_data_feed':'Live Data Feed'}
		help_texts = {'offset_after_open':'Enter a valid offset time'}

# This is the form for creating and editing new Budget Management Policy. 
# A ModelForm is created using the Model Data
class RobotBudgetManagementForm(ModelForm):
  class Meta:
    model = RobotBudgetManagement
    fields = ['portfolio_initial_budget','max_budget_per_purchase_percent','use_percentage_or_fixed_value',
		          'max_budget_per_purchase_number','current_cash_position','cash_position_update_policy',
              'add_taxes','add_commission','add_other_costs','taxes_rate','commission_per_trade','other_costs']
    labels = {'portfolio_initial_budget':'Portfolio Initial Budget (Calculated)','current_cash_position':' Current Cash Position (Calculated)',
              'use_percentage_or_fixed_value':'Use Percentage','max_budget_per_purchase_percent':'Maximum Budget per Acquisition (%)',
              'max_budget_per_purchase_number':'Max Budget per Acquisition ($)', 'add_taxes':' Add Taxes','add_commission':'Add Trade Commissions',
		          'add_other_costs':'Other Costs','taxes_rate':'Tax Rates','commission_per_trade':'Commission per Trade',
              'other_costs':'Other Costs'}
    help_texts = {'portfolio_initial_budget':'Enter a valid minimum cash to equity ratio'}
  def __init__(self, *args, **kwargs):
    super(RobotBudgetManagementForm,self).__init__(*args,**kwargs)	
    self.fields['portfolio_initial_budget'].disabled = True	
    self.fields['current_cash_position'].disabled = True	
#
# This is the form for creating and editing new Budget Management Policy. 
# A ModelForm is created using the Model Data
class EquityAndMarketSentimentForm(ModelForm):
	class Meta:
		model = EquityAndMarketSentiment
		fields = ['external_sentiment','sector_sentiment','equity_sentiment','market_sentiment','influences_acquisition','circuit_breaker',
		          'sentiment_feed','external_sentiment_weight','market_sentiment_weight','equity_sentiment_weight','sector_sentiment_weight']
		labels = {'external_sentiment':'External Sentiment Scale','sector_sentiment':'Sector Sentiment Scale','equity_sentiment':'Equity Sentiment Scale(Top 10 Holdings)',
		          'market_sentiment':'Market Sentiment Scale','sentiment_feed':'Sentiment Feed Origin','sector_sentiment_weight':'Sector Sentiment Weight',
		          'external_sentiment_weight':'External Sentiment Weight','market_sentiment_weight':'Market Sentiment Weight','circuit_breaker':'Circuit Breaker (TODO)',
		          'equity_sentiment_weight':'Equity Sentiment Weight(Top 10 Holdings)','influences_acquisition':'Influences Acquisition(TODO: Synchronize)'}
		help_texts = {'sector_sentiment':'Enter a valid Sector Sentiment'}


# This represents data (listing) to be pulled from a table 
# A ModelForm is created using the Model Data
#class AssetsMarketTransactionForm(ModelForm):
#	class Meta:
#		model = AssetsMarketTransaction
#		fields = ['name']
#		labels = {'name':'Name'}
#		help_texts = {'name':'Enter a valid name'}
