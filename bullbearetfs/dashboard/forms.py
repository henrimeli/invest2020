from django import forms
from django.forms import ModelForm
from django.forms.formsets import BaseFormSet

# This is the form for creating and editing new IndicatorInformation. 
# A ModelForm is created. 
class DashboardInformationForm(forms.Form):
  total_shares = forms.FloatField(widget=forms.NumberInput(), disabled=True)
  
  def __init__(self,*args,**kwargs):
    self.context = dict()
    self.title_dict = dict()
    self.table1_metrics = dict()
    print ( "DashboardInformation Form Initialization: ")
    super(DashboardInformationForm,self).__init__(*args, **kwargs)

  def setRowAndColumnsLabels(self):
    self.title_dict["table_title"]="Transactions, Shares, Values, Deltas"

    return


  # Returns the Context Data
  def contextData(self):
    #Put it all together now.
    self.setRowAndColumnsLabels()
    self.context["dashboard_table"]=self.title_dict
    self.context["table1_metrics"]=self.table1_metrics

    return self.context
  
