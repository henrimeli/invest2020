import logging
from django import forms
from django.forms import ModelForm
from django.forms.formsets import BaseFormSet
from bullbearetfs.strategy.models import EquityStrategy ,AcquisitionPolicy, DispositionPolicy
from bullbearetfs.strategy.models import PortfolioProtectionPolicy,OrdersManagement

# Get a logger instance
logger = logging.getLogger(__name__)
  
# This is the form for creating and editing new Strategies.
class EquityStrategyForm(ModelForm):
  class Meta:
    model = EquityStrategy
    fields = ['name','owner','visibility', 'description','strategy_class','strategy_category']
    labels = {'name':'Strategy Name','description':'Strategy Description','owner':'Strategy Owner','visibility':'Private',
              'strategy_category':'Strategy Category','strategy_class':'Strategy Class'}
    help_texts = {'name':'Enter a valid name'}

# Information Form. Is used to display Strategy for Update mode
class StrategyBasicInformationForm(ModelForm):
	class Meta:
		model = EquityStrategy
		fields = ['name','owner','visibility', 'description','strategy_class', 'strategy_category','modify_date',
		          'minimum_entries_before_trading','trade_only_after_fully_loaded','manual_asset_composition',
		          'automatic_generation_client_order_id','modify_date','manual_asset_composition_policy']
		labels = {'name':'Strategy Name','description':'Strategy Description','owner':'Strategy Owner','modify_date':'Modify Date',
		          'visibility':'Private','strategy_category':'Strategy Category','modify_date':'Last Modified','manual_asset_composition_policy':'Asset Composition Policy (Automatic / Manual)',
		          'minimum_entries_before_trading':'Minimum Entries Before Trading','trade_only_after_fully_loaded':'Trade after fully loaded',
		          'manual_asset_composition':'Automatic Asset Composition','automatic_generation_client_order_id':'Automatic Client Order ID Generation'}
		help_texts = {'name':'Enter a valid name','description':'Enter a valid Description'}

	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.fields['modify_date'].disabled=True

# This is the form for creating and editing new Acquisition Policy. 
# A ModelForm is created using the Model Data
class AcquisitionPolicyForm(ModelForm):
	class Meta:
		model = AcquisitionPolicy
		fields = ['acquisition_time_proximity','min_time_between_purchases','acquisition_volume_proximity','and_or_1','and_or_2',
		          'min_volume_between_purchases','volume_fraction_to_average','time_difference_between_acquisitions',
		          'acquisition_price_proximity', 'acquisition_price_factor','proximity_calculation_automatic','bear_acquisition_volatility_factor',
		          'bull_acquisition_volatility_factor','simultaneous_bull_bear_acquisitions','modify_date','number_or_percentage']
		labels = {'min_time_between_purchases':'Minimum Time Between Purchases','acquisition_price_proximity':'Enforce Acquisition Price Proximity Rule',
		          'min_volume_between_purchases':'Minumum Volume Between Purchases','acquisition_price_factor':'Acquisition Price Factor',
		          'volume_fraction_to_average':'Volume Fraction To Average','modify_date':'Modified Date','and_or_2':' AND / OR Volume Proximity:',
		          'time_difference_between_acquisitions':'Time Difference Between Acquisitions (minutes)','and_or_1':'AND / OR Time Proximity:',
		          'simultaneous_bull_bear_acquisitions':'Simultaneous Bull / Bear Acquisitions?','bull_acquisition_volatility_factor':'Bull Acquisition Volatility Factor',
		          'number_or_percentage':'Use Number or Percentage','bear_acquisition_volatility_factor':'Bear Acquisition Volatility Factor',
		          'acquisition_volume_proximity':'Volume Proximity'}
		help_texts = {'acquisition_time_proximity':'Enter a valid acquisition_time_proximity'}

	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.fields['acquisition_volume_proximity'].disabled=True
		self.fields['min_volume_between_purchases'].disabled=True
		self.fields['volume_fraction_to_average'].disabled=True
		self.fields['modify_date'].disabled=True

# This is the form for creating and editing new Acquisition Policy. 
# A ModelForm is created using the Model Data
class DispositionPolicyForm(ModelForm):
	class Meta:
		model = DispositionPolicy
		fields = ['in_transition_profit_policy','in_transition_profit_target_ratio','completion_profit_policy',
		          'completion_complete_target_ratio','in_transition_strategy_type','in_transition_entry_strategy',
		          'modify_date','in_transition_asset_composition','in_transition_load_factor','completion_regression_policy',
		           'completion_regression_duration','completion_regression_factor']
		labels = {'in_transition_profit_policy':'In Transition Profit Policy','in_transition_asset_composition':'Asset Composition',
		          'in_transition_profit_target_ratio':'In Transition Profit Ratio','completion_complete_target_ratio':'Completion Profit Ratio',
		          'completion_profit_policy':'Completion Profit Policy','in_transition_load_factor':'Transition Load Factor',
		          'in_transition_entry_strategy':'In Transition Entry Strategy','completion_regression_policy':'Completion Regression Policy',
		          'in_transition_strategy_type':'In Transition Strategy Type','modify_date':'Modified Date',
		          'completion_regression_duration':'Regression Duration (in Percentage of Max_Time )','completion_regression_factor':'Regression Factor'}
		help_texts = {'in_transition_profit_policy':'Enter a valid in_transition_profit_policy'}

	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.fields['in_transition_profit_policy'].disabled=True
		self.fields['completion_profit_policy'].disabled=True
		self.fields['modify_date'].disabled=True


# This is the form for creating and editing new Acquisition Policy. 
# A ModelForm is created using the Model Data 
class OrdersManagementForm(ModelForm):
	class Meta:
		model = OrdersManagement
		fields = ['acquisition_order_type','transition_order_type','completion_order_type','time_in_force_sell_orders',
		          'time_in_force_buy_orders','modify_date']
		labels = {'acquisition_order_type':'Acquisition Order Type','transition_order_type':'Transition Sell Order Type',
		          'completion_order_type':'Completion Sell Order Type','modify_date':'Modified Date'}
		help_texts = {'acquisition_order_type':'Enter a valid buy_order_type'}
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.fields['modify_date'].disabled=True

# This is the form for creating and editing new Acquisition Policy. 
# A ModelForm is created using the Model Data
class PortfolioProtectionForm(ModelForm):
	class Meta:
		model = PortfolioProtectionPolicy
		fields = ['protect_asset_upon_acquisition','protect_asset_upon_move_to_transition',
		'use_stop_limit','use_stop_market','use_trailing_stops','modify_date']
		labels = {'use_trailing_stops':'Use Trainling Stops','use_stop_market':'Use Stop Market',
		          'use_stop_limit':'Use Stop Limit Orders','modify_date':'Modify Date',
		          'protect_asset_upon_acquisition':'Protect Asset upon Acquisition','protect_asset_upon_move_to_transition':'Protect Asset upon move to Transition'}
		help_texts = {'protect_asset_upon_acquisition':'Enter a valid protect_asset_upon_acquisition'}	
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.fields['modify_date'].disabled=True

#This is the form for entering individual Indicators information
#
class AcquisitionIndicatorsForm(forms.Form):
    #unit_price = forms.FloatField(widget=forms.NumberInput(attrs={'placeholder':'Rent Price'}), required=True)
    indicator_name = forms.CharField(max_length=30,widget=forms.TextInput(attrs={'placeholder':'Indicator Name'}), required=False,disabled=True)
    indicator_class = forms.CharField(max_length=17,widget=forms.TextInput(attrs={'placeholder':'Indicator Class'}), required=False,disabled=True)
    indicator_family = forms.CharField(max_length=17,widget=forms.TextInput(attrs={'placeholder':'Indicator Class'}), required=False,disabled=True)    
    #unit_configuration = forms.ChoiceField(choices=CHOICES_UNIT_CONFIGURATION)
    #indicator_ddd = forms.IntegerField()
    #indicator_family = forms.FloatField(widget=forms.NumberInput(), disabled=True)
    indicator_parameters = forms.IntegerField(widget=forms.NumberInput(), disabled=True)
    #loss_to_market = forms.FloatField(widget=forms.NumberInput(), disabled=True)
    #lease_type = forms.ChoiceField(choices=CHOICES_LEASE_TYPE   )
    #lease_start = forms.DateField(widget=forms.SelectDateWidget())
    #lease_end = forms.DateField(widget=forms.SelectDateWidget())
    #unit_status = forms.ChoiceField(choices=CHOICES_UNIT_STATUS)

    def __init__(self,*args,**kwargs):
        self.user_name = kwargs.pop('user_name',None)
        logger.debug( " Indicator Form Initialization: This user: {0} Indicator ".format(self.user_name) )
        super(AcquisitionIndicatorsForm,self).__init__(*args, **kwargs)
        self.fields['indicator_start'] = forms.CharField(max_length=20)
        self.fields['indicator_interval'] = forms.CharField(max_length=20)

        return
# Adds valuation ... not sure why.
# Will need to add valuation to make sure that no two combination of
# bedrooms, bathrooms, size, ... etc are the same
# Also make sure the total number of units matches.
class BaseIndicatorConfigFormSet(BaseFormSet):

  def clean(self):
    print ('In the Clean Method for Formset')
    return