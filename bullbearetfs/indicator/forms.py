from django import forms
from django.forms import ModelForm
from django.forms.formsets import BaseFormSet

from bullbearetfs.indicator.models import EquityIndicator

# This is the form for creating and editing new IndicatorInformation. 
# A ModelForm is created. 
class EquityIndicatorInformationForm(ModelForm):
  class Meta:
    model = EquityIndicator
    fields = ['name','description','indicator_class','indicator_family','reset_on_start','reset_daily',
              'treshold_to_market_open','treshold_to_volume_open','volume_interval','time_interval','visibility','owner','use_robot_symbol','indicator_class']

    labels = {'name':'Indicator Name','indicator_family':'Indicator Family','number_of_parameters':'Indicator Parameters',
              'Indicator_class':'Indicator Class','reset_on_start':'Reset on Restart','reset_daily':'Reset Daily',
              'treshold_to_market_open':'Treshold to Market Open','owner':'Owner','visibility':'Private',
              'treshold_to_volume_open':'Treshold to Volume at Open','volume_interval':'Volume Interval',
              'time_interval':'Time Interval','use_robot_symbol':'Use Robot Symbol','description':'Description'}

    help_texts = {'name':'Enter a valid name'}

