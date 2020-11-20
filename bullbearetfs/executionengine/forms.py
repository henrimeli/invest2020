from django import forms
from django.forms import ModelForm
from django.forms.formsets import BaseFormSet

from pages.models import EquityTradingRobot, RobotActivityWindow, RobotBudgetManagement, EquityAndMarketSentiment
from pages.models import RobotEquitySymbols, EquityTradingData
from pages.executionengine.models import ETFPairRobotExecution
from pages.models import CHOICES_USE_CASH_OR_NUMBER
from pages.strategy.models import OrdersManagement
from pages.robot.models import ETFAndReversePairRobot 

from functools import partial
