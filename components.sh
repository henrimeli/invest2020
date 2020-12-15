
description="                            Description of All the Components in the system: \n \
# 0.  [UI,BE] [BASIC] Application Basic [ Static Elements: Home Page,ProfileSettings ] \n \
# 1.  [UI,BE] [FOUND] Foundational [ Roundtrip, StableRoundtrip, Completedroundtrip ]\n \
# 2.  [UI,BE] [RMGMT] Robot Managament [ Getters, Setters, Conditionals, Enable/Disable, Version, Notification... ] \n \
# 3.  [UI,BE] [PBDGT] Portfolio & Budget Management [  Portfolio, BudgetManagement ] \n \
# 4.  [UI,BE] [SYMBS] Equity Symbols [  EquityRobotSymbols ] \n \
# 5.  [UI,BE] [ACTSE] Activity Window & Market Sentiments [ ActivityWindow, MarketSentiments ] \n \
# 6.  [UI,BE] [RCOND] Robot Conditionals [ Functionality only. No class. Forced Sale, Market is crashing, Infrastructure, Brokerage challenges, ...] \n \
# 7.  [UI,BE] [DARPT] Data Reporting [ Functionality only. No class ] \n \
# 8.  [UI,BE] [BRKAG] Brokerage APIs [ BrokerageInformation, BrokerageAPIBase, alpaca, eTrade, Ameritrade ] \n \
# 9.  [UI,BE] [STGYI] Strategy Infrastructure [ Strategy, Acquisition, Disposition, Orders, Protection ] \n \
# 10. [UI,BE] [INDST] Individual Strategies [ StrategyBase, Batcham, Babadjou, Bamendjinda, ...] \n \
# 11. [UI,BE] [DSOUR] Infrastructure Data Sources [  array, database, file ] \n \
# 12. [UI,BE] [RUNTE] Runtime Server [ Robot Management / Robot Execution ] \n \
# 13. [UI,BE] [CUSTM] Customer Management [ Authentication/Authorization, User Creation, Customer Profile ] \n \
# 14. [UI,BE] [UTLTY] Utilities [ formatting, data cleanup, data synchronization, data reconcilation, data consistency, ...] \n \
# 15. [UI,BE] [ERROR] Errors & Logging [ CustomError, UI Errors, Backend Errors, Logging, Serviceability,Troubleshooting ...] \n \
# 16. [UI,BE] [EVTCA] Event Capture [  Startup ] \n \
# 17. [UI,BE] [BUINT] Business Intelligence [ Indicators, PerformanceToMarket ... ] \n \
# 18. [UI,BE] [DASHB] Dashboard [ Dashboard  ] \n \
# 19. [UI,BE] [EXENG] Execution Engine [  ] \n \
# 20. [UI,BE] [RPTGE] Report Generation [ ReportGeneration  ] \n \
# 21. [UI,BE] [SETUP] Setup [ creation of base data such as MasterSymbolsList ] \n \
# 22. [UI,BE] [MIGRA] Migration [ Version Upgrade, ...] \n \
# 23. [UI,BE] [CHKLS] Deployment Checkpoint [ Application Security, Serviceability, Live,  ... ] \n \
# 24. [UI,BE] [OTHER] Others [ Anything that doesn't fit above, research new strategies, research new pairs ] "

# Strategies
#  10. A BABADJOU
#  10. B BATCHAM
#  10. C BALACHI
BASE_PKG="bullbearetfs"
export UI_BASE="${BASE_PKG}.selenium"
export BE_BASE="${BASE_PKG}.unittests"
export BE_FBASE="${BE_BASE}.robot.foundation"

export UI_FOUND="${UI_BASE}.robot.foundation.tests"
export BE_FOUND="${BE_FBASE}.dataholdertests ${BE_FBASE}.roundtriptests ${BE_FBASE}.stabletests ${BE_FBASE}.completedtests ${BE_FBASE}.transitiontests"

export UI_BASIC="${UI_BASE}.basic.tests"
export BE_BASIC="${BE_BASE}.basic.tests"

export UI_RMGMT="${UI_BASE}.robot.core.tests"
export BE_RMGMT="${BE_BASE}.robot.core.tests"
export UI_PBDGT="${UI_BASE}.robot.budget.tests"
export BE_PBDGT="${BE_BASE}.robot.budget.tests"
export UI_SYMBS="${UI_BASE}.robot.symbols.tests"
export BE_SYMBS="${BE_BASE}.robot.symbols.tests"
export UI_ACTSE="${UI_BASE}.market.tests"
export BE_ACTSE="${BE_BASE}.market.markettests ${BE_BASE}.market.activitytests"

export UI_RCOND="${UI_BASE}.robot.conditionals.tests"
export BE_RCOND="${BE_BASE}.robot.conditionals.tests"
export UI_RDATA="${UI_BASE}.robot.reportdata.tests"
export BE_RDATA="${BE_BASE}.robot.reportdata.tests"
export UI_BRKAG="${UI_BASE}.brokerages.tests"
export BE_BRKAG="${BE_BASE}.brokerages.tests"
export UI_STGYI="${UI_BASE}.strategyinfra.tests"
export BE_STGYI="${BE_BASE}.strategyinfra.tests"
export UI_INDST="${UI_BASE}.strategies.tests "
export BE_INDST="${BE_BASE}.strategies.tests "
export UI_DSOUR="${UI_BASE}.datasources.tests"
export BE_DSOUR="${BE_BASE}.datasources.tests"
export UI_RUNTE="${UI_BASE}.robotruntime.tests"
export BE_RUNTE="${BE_BASE}.robotruntime.tests"
export UI_CUSTM="${UI_BASE}.customer.tests"
export BE_CUSTM="${BE_BASE}.customer.tests"

export UI_UTLTY="${UI_BASE}.utilities.tests"
export BE_UTLTY="${BE_BASE}.utilities.tests"
export UI_ERROR="${UI_BASE}.errors.tests"
export BE_ERROR="${BE_BASE}.errors.tests"
export UI_EVTCA="${UI_BASE}.eventcapture.tests"
export BE_EVTCA="${BE_BASE}.eventcapture.tests"
export UI_BUINT="${UI_BASE}.bintelligence.tests"
export BE_BUINT="${BE_BASE}.bintelligence.tests"
export UI_DASHB="${UI_BASE}.dashboard.tests"
export BE_DASHB="${BE_BASE}.dashboard.tests"
export UI_EXENG="${UI_BASE}.executionengine.tests"
export BE_EXENG="${BE_BASE}.executionengine.tests"
export UI_RPTGE="${UI_BASE}.reportgeneration.tests"
export BE_RPTGE="${BE_BASE}.reportgeneration.tests"
export UI_SETUP="${UI_BASE}.datasetup.tests" 
export BE_SETUP="${BE_BASE}.datasetup.tests" 
export UI_MIGRA="${UI_BASE}.datamigration.tests"
export BE_MIGRA="${BE_BASE}.datamigration.tests"
export UI_CHKLS="${UI_BASE}.deploymentchklist.tests"
export BE_CHKLS="${BE_BASE}.deploymentchklist.tests"
export UI_OTHER="${UI_BASE}.others.tests"
export BE_OTHER="${BE_BASE}.others.tests"

############# The packages below are used to generate pydoc documentation
export SRC_BASE="bullbearetfs"

#The dummy files below load the settings and initialize django for pydoc utility
# Doesn't work without them
export SRC_DUMMY="${SRC_BASE}.dummy"
export BED_DUMMY="${BE_BASE}.dummy"
export UID_DUMMY="${UI_BASE}.dummy"

# SRC_XXXXX points to the files in the source folder (models, forms, views, urls)
# TST_UI_BASIC: points to the files in the selenium test package
# TST_BE_BASIC: points to the files in the unittests package
export SRC_BASIC="${SRC_BASE}.basic ${SRC_BASE}.basic.forms ${SRC_BASE}.basic.urls ${SRC_BASE}.basic.views" 
export TST_UI_BASIC="${UI_BASE}.basic ${UI_BASE}.basic.tests"
export TST_BE_BASIC="${BE_BASE}.basic ${BE_BASE}.basic.tests"

#FOUNDATION component
export    SRC_FOUND="${SRC_BASE}.robot ${SRC_BASE}.robot.foundation ${SRC_BASE}.robot.foundation.roundtrip ${SRC_BASE}.robot.foundation.stableroundtrip ${SRC_BASE}.robot.foundation.completedroundtrip" 
export TST_UI_FOUND="${UI_BASE}.robot.foundation.tests"
export TST_BE_FOUND="${BE_FBASE}.dataholdertests ${BE_FBASE}.roundtriptests ${BE_FBASE}.stabletests ${BE_FBASE}.completedtests ${BE_FBASE}.transitiontests"

export    SRC_CUSTM="${SRC_BASE}.customer ${SRC_BASE}.customer.forms ${SRC_BASE}.customer.models ${SRC_BASE}.customer.urls ${SRC_BASE}.customer.views" 
export TST_UI_CUSTM="${UI_BASE}.customer.tests"
export TST_BE_CUSTM="${BE_BASE}.customer.tests"

#Robot Core (Robot MGMT) Component
export    SRC_RMGMT="${SRC_BASE}.robot.core ${SRC_BASE}.robot.core.forms ${SRC_BASE}.robot.core.models ${SRC_BASE}.robot.core.urls ${SRC_BASE}.robot.core.views" 
export TST_UI_RMGMT="${UI_BASE}.robot.core.tests"
export TST_BE_RMGMT="${BE_BASE}.robot.core.tests"

#Portfolio and Budget Component
export    SRC_PBDGT="${SRC_BASE}.robot.budget ${SRC_BASE}.robot.budget.forms ${SRC_BASE}.robot.budget.models ${SRC_BASE}.robot.budget.urls ${SRC_BASE}.robot.budget.views" 
export TST_UI_PBDGT="${UI_BASE}.robot.budget.tests"
export TST_BE_PBDGT="${BE_BASE}.robot.budget.tests"

#Robot Symbols
export    SRC_SYMBS="${SRC_BASE}.robot.symbols ${SRC_BASE}.robot.symbols.forms ${SRC_BASE}.robot.symbols.models ${SRC_BASE}.robot.symbols.urls ${SRC_BASE}.robot.symbols.views" 
export TST_UI_SYMBS="${UI_BASE}.robot.symbols.tests"
export TST_BE_SYMBS="${BE_BASE}.robot.symbols.tests"

#Robot Activity & Sentiments
export    SRC_ACTSE="${SRC_BASE}.market ${SRC_BASE}.market.forms ${SRC_BASE}.market.models ${SRC_BASE}.market.urls ${SRC_BASE}.market.views" 
export TST_UI_ACTSE="${UI_BASE}.market.tests"
export TST_BE_ACTSE="${BE_BASE}.market.markettests ${BE_BASE}.market.activitytests"

#Robot Conditionals
export    SRC_RCOND="" 
export TST_UI_RCOND="${UI_BASE}.robot.conditionals.tests"
export TST_BE_RCOND="${BE_BASE}.robot.conditionals.tests"

#Robot Reports Data
export    SRC_RDATA="" 
export TST_UI_RDATA="${UI_BASE}.robot.reportdata.tests"
export TST_BE_RDATA="${BE_BASE}.robot.reportdata.tests"

#Brokerages
export    SRC_BRKAG="${SRC_BASE}.brokerages ${SRC_BASE}.brokerages.alpaca ${SRC_BASE}.brokerages.ameritrade ${SRC_BASE}.brokerages.etrade" 
export TST_UI_BRKAG="${UI_BASE}.brokerages.tests"
export TST_BE_BRKAG="${BE_BASE}.brokerages.tests"

#Strategy Infrastructure
export    SRC_STGYI="${SRC_BASE}.strategy ${SRC_BASE}.strategy.forms ${SRC_BASE}.strategy.models ${SRC_BASE}.strategy.urls ${SRC_BASE}.strategy.views" 
export TST_UI_STGYI="${UI_BASE}.strategyinfra.tests"
export TST_BE_STGYI="${BE_BASE}.strategyinfra.tests"

#Strategies Development Infrastructure
export    SRC_INDST="${SRC_BASE}.strategies ${SRC_BASE}.strategies.babadjou ${SRC_BASE}.strategies.bangang ${SRC_BASE}.strategies.batcham ${SRC_BASE}.strategies.bamendjinda" 
export TST_UI_INDST="${UI_BASE}.strategies.tests"
export TST_BE_INDST="${BE_BASE}.strategies.tests"

#Data Sources
export    SRC_DSOUR="${SRC_BASE}.datasources ${SRC_BASE}.datasources.datasources" 
export TST_UI_DSOUR="${UI_BASE}.datasources.tests"
export TST_BE_DSOUR="${BE_BASE}.datasources.tests"

#Robot Runtime
export    SRC_RUNTE="${SRC_BASE}.robotruntime  ${SRC_BASE}.robotruntime.manager " 
export TST_UI_RUNTE="${UI_BASE}.robotruntime.tests"
export TST_BE_RUNTE="${BE_BASE}.robotruntime.tests"

#Utilities
export    SRC_UTLTY="${SRC_BASE}.utilities ${SRC_BASE}.utilities.core" 
export TST_UI_UTLTY="${UI_BASE}.utilities.tests"
export TST_BE_UTLTY="${BE_BASE}.utilities.tests"

#Error Handling / Custom Errors
export    SRC_ERROR="${SRC_BASE}.errors ${SRC_BASE}.errors.customerrors " 
export TST_UI_ERROR="${UI_BASE}.errors.tests"
export TST_BE_ERROR="${BE_BASE}.errors.tests"

#Event Capture
export    SRC_EVTCA="${SRC_BASE}.eventcapture ${SRC_BASE}.eventcapture.forms ${SRC_BASE}.eventcapture.models ${SRC_BASE}.eventcapture.views ${SRC_BASE}.dashboard.urls" 
export TST_UI_EVTCA="${UI_BASE}.eventcapture.tests"
export TST_BE_EVTCA="${BE_BASE}.eventcapture.tests"

#Business Intelligence
export    SRC_BUINT="${SRC_BASE}.bintelligence ${SRC_BASE}.bintelligence.models" 
export TST_UI_BUINT="${UI_BASE}.bintelligence.tests"
export TST_BE_BUINT="${BE_BASE}.bintelligence.tests"

#Dashboard
export    SRC_DASHB="${SRC_BASE}.dashboard ${SRC_BASE}.dashboard.forms ${SRC_BASE}.dashboard.models ${SRC_BASE}.dashboard.views ${SRC_BASE}.dashboard.urls" 
export TST_UI_DASHB="${UI_BASE}.dashboard.tests"
export TST_BE_DASHB="${BE_BASE}.dashboard.tests"

export    SRC_EXENG="${SRC_BASE}.executionengine ${SRC_BASE}.executionengine.forms ${SRC_BASE}.executionengine.models ${SRC_BASE}.executionengine.views ${SRC_BASE}.executionengine.urls" 
export TST_UI_EXENG="${UI_BASE}.executionengine.tests"
export TST_BE_EXENG="${BE_BASE}.executionengine.tests"

export    SRC_RPTGE="${SRC_BASE}.reportgeneration ${SRC_BASE}.reportgeneration.forms ${SRC_BASE}.reportgeneration.models ${SRC_BASE}.reportgeneration.views ${SRC_BASE}.reportgeneration.urls" 
export TST_UI_RPTGE="${UI_BASE}.reportgeneration.tests"
export TST_BE_RPTGE="${BE_BASE}.reportgeneration.tests"

export    SRC_SETUP="${SRC_BASE}.datasetup ${SRC_BASE}.datasetup.core" 
export TST_UI_SETUP="${UI_BASE}.datasetup.tests" 
export TST_BE_SETUP="${BE_BASE}.datasetup.tests" 

export    SRC_MIGRA="${SRC_BASE}.datamigration ${SRC_BASE}.datamigration.core" 
export TST_BE_MIGRA="${BE_BASE}.datamigration.tests"
export TST_UI_MIGRA="${UI_BASE}.datamigration.tests"

export    SRC_CHKLS="${SRC_BASE}.deploymentchklist ${SRC_BASE}.deploymentchklist" 
export TST_UI_CHKLS="${UI_BASE}.deploymentchklist.tests"
export TST_BE_CHKLS="${BE_BASE}.deploymentchklist.tests"

export    SRC_OTHER="${SRC_BASE}.others" 
export TST_UI_OTHER="${UI_BASE}.others.tests"
export TST_BE_OTHER="${BE_BASE}.others.tests"

export DOC_SRC1="${SRC_RDATA} ${SRC_RCOND} ${SRC_ACTSE} ${SRC_SYMBS} ${SRC_PBDGT} ${SRC_RMGMT} ${SRC_CUSTM} ${SRC_FOUND} ${SRC_BASIC}"
export DOC_SRC2="${SRC_EVTCA} ${SRC_ERROR} ${SRC_UTLTY} ${SRC_RUNTE} ${SRC_DSOUR} ${SRC_INDST} ${SRC_STGYI} ${SRC_BRKAG}"
export DOC_SRC3="${SRC_BUINT} ${SRC_DASHB} ${SRC_EXENG} ${SRC_RPTGE} ${SRC_SETUP} ${SRC_MIGRA} ${SRC_CHKLS} ${SRC_OTHER}"

export DOC_BE1="${TST_BE_RDATA} ${TST_BE_RCOND} ${TST_BE_ACTSE} ${TST_BE_SYMBS} ${TST_BE_PBDGT} ${TST_BE_RMGMT} ${TST_BE_CUSTM} ${TST_BE_FOUND} ${TST_UI_BASIC}"
export DOC_BE2="${TST_BE_EVTCA} ${TST_BE_ERROR} ${TST_BE_UTLTY} ${TST_BE_RUNTE} ${TST_BE_DSOUR} ${TST_BE_INDST} ${TST_BE_STGYI} ${TST_BE_BRKAG}"
export DOC_BE3="${TST_BE_BUINT} ${TST_BE_DASHB} ${TST_BE_EXENG} ${TST_BE_RPTGE} ${TST_BE_SETUP} ${TST_BE_MIGRA} ${TST_BE_CHKLS} ${TST_BE_OTHER}"

export DOC_UI1="${TST_UI_RDATA} ${TST_UI_RCOND} ${TST_UI_ACTSE} ${TST_UI_SYMBS} ${TST_UI_PBDGT} ${TST_UI_RMGMT} ${TST_UI_CUSTM} ${TST_UI_FOUND} ${TST_UI_BASIC}"
export DOC_UI2="${TST_UI_EVTCA} ${TST_UI_ERROR} ${TST_UI_UTLTY} ${TST_UI_RUNTE} ${TST_UI_DSOUR} ${TST_UI_INDST} ${TST_UI_STGYI} ${TST_UI_BRKAG}"
export DOC_UI3="${TST_UI_BUINT} ${TST_UI_DASHB} ${TST_UI_EXENG} ${TST_UI_RPTGE} ${TST_UI_SETUP} ${TST_UI_MIGRA} ${TST_UI_CHKLS} ${TST_UI_OTHER}"


############    Running individual Strategies   #############################################
#export BE_INDST="${BE_BASE}.strategies.tests ${BE_BASE}.strategies.babadjou.transitiontest ${BE_BASE}.strategies.babadjou.transitiontest  "
export  TST_BABADJOU_BASE=${BE_BASE}.strategies.babadjou
export  TST_BABADJOU="${TST_BABADJOU_BASE}.transitiontests ${TST_BABADJOU_BASE}.completedtests ${TST_BABADJOU_BASE}.endtoendtests  "
export  TST_BABADJOU_PAPER="${TST_BABADJOU_BASE}.transitiontest ${TST_BABADJOU_BASE}.completedtest ${TST_BABADJOU_BASE}.endtoendtest  "
export  TST_BABADJOU_LIVE="${TST_BABADJOU_BASE}.transitiontest ${TST_BABADJOU_BASE}.completedtest ${TST_BABADJOU_BASE}.endtoendtest  "
