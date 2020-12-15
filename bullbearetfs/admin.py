from django.contrib import admin

# Register your models here.
from bullbearetfs.robot.models import ETFAndReversePairRobot, TradeDataHolder
from bullbearetfs.strategy.models import DispositionPolicy, EquityStrategy, OrdersManagement
from bullbearetfs.strategy.models import AcquisitionPolicy, PortfolioProtectionPolicy
from bullbearetfs.market.models import WebsiteContactPage, MarketInformation, MarketDataProvider, MajorIndexSymbol, IndexTrackerIssuer
from bullbearetfs.market.models import IndexTrackerETFSymbol
from bullbearetfs.indicator.models import EquityIndicator
from bullbearetfs.customer.models import Address, BusinessInformation, Billing,Customer,CustomerProfile
from bullbearetfs.customer.models import CustomerBasic, CustomerSecurity
from bullbearetfs.executionengine.models import ETFPairRobotExecution,ETFPairRobotExecutionData

from bullbearetfs.models import Notifications,  NotificationType, EquityTradingRobot,EquityTradingData
from bullbearetfs.brokerages.models import BrokerageInformation
from bullbearetfs.basic.models import Settings
from bullbearetfs.robot.symbols.models import RobotEquitySymbols, BullBearETFData
from bullbearetfs.robot.activitysentiments.models import MarketBusinessHours, EquityAndMarketSentiment, RobotActivityWindow
from bullbearetfs.robot.budget.models import RobotBudgetManagement, Portfolio

admin.site.register(BullBearETFData)
admin.site.register(ETFPairRobotExecutionData)
admin.site.register(ETFPairRobotExecution)
admin.site.register(MarketDataProvider)
admin.site.register(EquityAndMarketSentiment)
admin.site.register(RobotActivityWindow)
admin.site.register(RobotBudgetManagement)
admin.site.register(ETFAndReversePairRobot)
admin.site.register(BusinessInformation)
admin.site.register(WebsiteContactPage)
admin.site.register(Customer)
#admin.site.register(InvestmentInterest)
admin.site.register(Address)
admin.site.register(Billing)
admin.site.register(Notifications)
admin.site.register(NotificationType)
admin.site.register(Settings)
admin.site.register(Portfolio)
admin.site.register(EquityTradingRobot)
admin.site.register(DispositionPolicy)
admin.site.register(CustomerBasic)
admin.site.register(CustomerSecurity)
admin.site.register(BrokerageInformation)
admin.site.register(MarketBusinessHours)
admin.site.register(MarketInformation)
admin.site.register(IndexTrackerIssuer)
admin.site.register(IndexTrackerETFSymbol)
admin.site.register(EquityTradingData)
#admin.site.register(EquityVolatility)
admin.site.register(AcquisitionPolicy)
#admin.site.register(AssetsMarketTransaction)
admin.site.register(OrdersManagement)
admin.site.register(PortfolioProtectionPolicy)
admin.site.register(EquityStrategy)
admin.site.register(EquityIndicator)
admin.site.register(RobotEquitySymbols)
admin.site.register(TradeDataHolder)





