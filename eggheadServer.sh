#!/bin/bash
today=`date '+%Y_%m_%d__%H_%M_%S'`
source ./components.sh

####################################################################################
# This is the file used to perform a variety of tasks such as:
#   -Start the Django server locally.
#   -Start the Egghead Runtime Server
#   
#
#   Run the Backend Unit Tests, Selenium UI Tests
#    Run single Unit Test. Run single Selenium Test
#    Run component Unit Test. Run component Selenium Test
#    Run ALL Unit Tests . Run ALL Selenium Tests
#
####################################################################################

export SELENIUM_DRIVERS_HOME=/Users/henrimeli/Library/Drivers/
export DEFAULT_BROWSER=safari
export DEFAULT_COMPONENT=foundation
#migrations command 1: python manage.py makemigrations bullbearetfs
#migrations command 2: python manage.py migrate bullbearetfs


runDjangoServer() {
  export RUNSERVERPORT=8000
  echo "Starting the Django Server "
  echo " ---- Running the Django Server for Stock Market Application on  port $RUNSERVERPORT "
  python manage.py runserver 127.0.0.1:$RUNSERVERPORT
}

#Runs Single Selenium Unit Tests
runSingleSeleniumTest(){
  #External Application Variables
  source ~/.henri_alpaca_paper.sh
  #Local Specific Variables
  source ~/.henri_local.sh

  export BROWSER_NAME=$browser_name
  export TEST_OUTPUT_DIR='./test-reports/selenium' 
  export TEST_OUTPUT_FILE_NAME='test_results.xml' 

  echo "Running Single Selenium Test on Browser: $browser_name display=$PRINT_VAR LOGGING=$LOGGING_LEVEL REPORT=$REPORT_LEVEL" 
  python manage.py test ${UI_BASE}.core.tests
  junit2html $TEST_OUTPUT_DIR/$TEST_OUTPUT_FILE_NAME $TEST_OUTPUT_DIR/selenium-results.html
  echo " To view results, please run open $TEST_OUTPUT_DIR/selenium-results.html "
  echo "Selenium Django Test completed  "
}


#Runs Selenium tests for given Component
runComponentSeleniumTests() {
source ~/.henri_alpaca_paper.sh
source ~/.henri_local.sh

  export BROWSER_NAME=$browser_name
  export TEST_OUTPUT_DIR='./test-reports/selenium' 
  export TEST_OUTPUT_FILE_NAME='test_results.xml' 

  echo "Running Selenium Component Tests on browser $browser_name for $component_names"
  echo "Executing: python manage.py test $COMP_TESTS "
  python manage.py test $COMP_TESTS
  junit2html $TEST_OUTPUT_DIR/$TEST_OUTPUT_FILE_NAME $TEST_OUTPUT_DIR/selenium-results.html
  echo " To view results, please run open $TEST_OUTPUT_DIR/selenium-results.html "
  echo "Selenium Django Components Test completed  "
}


#Runs ALL Selenium Tests
runALLSeleniumTests(){
source ~/.henri_alpaca_paper.sh
source ~/.henri_local.sh

  export BROWSER_NAME=$browser_name
  export TEST_OUTPUT_DIR='./test-reports/selenium' 
  export TEST_OUTPUT_FILE_NAME='test_results.xml' 

  echo "Running ALL Selenium Test on Browser: $browser_name for $component_names display=$PRINT_VAR LOGGING=$LOGGING_LEVEL REPORT=$REPORT_LEVEL" 
  echo "Executing: python manage.py test $COMP_TESTS "
  python manage.py test $COMP_TESTS
  junit2html $TEST_OUTPUT_DIR/$TEST_OUTPUT_FILE_NAME $TEST_OUTPUT_DIR/selenium-results.html
  echo " To view results, please run open $TEST_OUTPUT_DIR/selenium-results.html "
  echo "Selenium Django Components Test completed. ALL Tests  "
}


#Runs individual unit tests
runSingleUnitTest(){
source ~/.henri_alpaca_paper.sh
source ~/.henri_local.sh

  echo "Running Single Individual Test on Browser: $browser_name display=$PRINT_VAR LOGGING=$LOGGING_LEVEL REPORT=$REPORT_LEVEL" 
  export TEST_OUTPUT_DIR='./test-reports/unittest' 
  export TEST_OUTPUT_FILE_NAME='test_results.xml' 

  echo "Running Single UnitTest  " 

  #python manage.py test ${BE_BASE}.robot.core.tests
  python manage.py test ${BE_BASE}.robot.foundation.roundtriptests
  #python manage.py test ${BE_BASE}.robot.foundation.completedtests
  #python manage.py test ${BE_BASE}.robot.foundation.stabletests
  #python manage.py test ${BE_BASE}.robot.foundation.dataholdertests
  #python manage.py test ${BE_BASE}.robot.conditionals.tests
  #python manage.py test ${BE_BASE}.robot.symbols.tests
  #python manage.py test ${BE_BASE}.robot.budget.tests

  #python manage.py test ${BE_BASE}.errors.tests
  #python manage.py test ${BE_BASE}.datasources.tests
  #python manage.py test ${BE_BASE}.brokerages.tests
  #python manage.py test ${BE_BASE}.robotruntime.tests
  #python manage.py test ${BE_BASE}.datamigration.tests
  #python manage.py test ${BE_BASE}.bintelligence.tests
  #python manage.py test ${BE_BASE}.datasetup.tests
  #python manage.py test ${BE_BASE}.others.tests
  #python manage.py test ${BE_BASE}.eventcapture.tests
  #python manage.py test ${BE_BASE}.utilities.tests
  #python manage.py test ${BE_BASE}.executionengine.tests
  #python manage.py test ${BE_BASE}.customer.tests
  #python manage.py test ${BE_BASE}.dashboard.tests
  #python manage.py test ${BE_BASE}.reportgeneration.tests
  #python manage.py test ${BE_BASE}.strategyinfra.tests
  #python manage.py test ${BE_BASE}.strategies.tests
  #python manage.py test ${BE_BASE}.basic.tests
  #python manage.py test ${BE_BASE}.market.markettests
  #python manage.py test ${BE_BASE}.market.activitytests
  junit2html $TEST_OUTPUT_DIR/$TEST_OUTPUT_FILE_NAME $TEST_OUTPUT_DIR/test-results.html
  echo " To view results, please run open $TEST_OUTPUT_DIR/test-results.html"
  echo "Django Unit Test completed  "
}


runComponentUnitTests(){
source ~/.henri_alpaca_paper.sh
source ~/.henri_local.sh

  echo "Running Component UnitTests display=$PRINT_VAR LOGGING=$LOGGING_LEVEL REPORT=$REPORT_LEVEL" 
  export TEST_OUTPUT_DIR='./test-reports/unittest' 
  export TEST_OUTPUT_FILE_NAME='test_results.xml' 

  echo "Running Unit Test Component Tests "
  echo "Executing: python manage.py test $COMP_TESTS "
  python manage.py test $COMP_TESTS
  junit2html $TEST_OUTPUT_DIR/$TEST_OUTPUT_FILE_NAME $TEST_OUTPUT_DIR/test-results.html
  echo " To view results, please run open $TEST_OUTPUT_DIR/test-results.html "
  echo "Unittests Django Components Test completed  "
}

#Runs ALL Tests
runALLUnitTests(){
source ~/.henri_alpaca_paper.sh
source ~/.henri_local.sh

  echo "Starting ALL Django Tests : display=$PRINT_VAR LOGGING=$LOGGING_LEVEL REPORT=$REPORT_LEVEL" 
  export TEST_OUTPUT_DIR='./test-reports/unittest' 
  export TEST_OUTPUT_FILE_NAME='test_results.xml' 

  echo "Running ALL Unit Tests "
  echo "Executing: python manage.py test $COMP_TESTS "
  python manage.py test $COMP_TESTS
  junit2html $TEST_OUTPUT_DIR/$TEST_OUTPUT_FILE_NAME $TEST_OUTPUT_DIR/test-results.html
  echo " To view results, please run open $TEST_OUTPUT_DIR/test-results.html "
  echo "ALL Unit Tests on Django Test completed  "
}

#
# This is the Server Robot Manager.
#
runEggheadManager(){
source ~/.henri_alpaca_paper.sh
  echo "TRADING URL=$APCA_API_BASE_URL"
  #echo "TRADING KEY= "
  #echo "TRADING SECRET= "
  echo "Starting the Robot Manager "
  #export DJANGO_SETTINGS_MODULE=./etfs/settings.py
  cp -v ./${BASE_PKG}/manager/mainserver.py ./mainserver.py
  python mainserver.py
}

#
# This is the Function to test various things
#
testhenri(){
source ~/.henri_alpaca_paper.sh
  echo "Starting the Test Henri Function.  "
  python testhenri.py
}

#
# This is the Server Robot Manager.
#
runshutdownManager(){
source ~/.henri_alpaca_paper.sh
  echo "Starting the Shutdown Manager "
  cp -v ./${BASE_PKG}/manager/shutdownmanager.py ./shutdownmanager.py
  python shutdownmanager.py
}

#
# This is the for setting up Data into the Database
#
runSetupData(){
source ~/.henri_alpaca_paper.sh
source ~/.henri_local.sh

  echo "Starting the Setup Manager "
  cp -v ./${BASE_PKG}/setup/infrastructure.py ./infrastructure.py
  python infrastructure.py
}

#
# Deploying the Manager Files. This includes the Database. 
# I want to avoid for now the use of the live database. 
# I'm not yet comfortable with it.
deployManager(){
  MANAGER_SOURCE=${PWD}/etfs
  MANAGER_DESTINATION=${PWD}
  SQL3_SOURCE_FILE=${PWD}/db.sqlite3
  SQL3_DESTINATION_FILE=${PWD}/../alpaca/artifacts/db.sqlite3
  echo "Today is : $today "
  echo "Deploying Code and Database for the Robot Manager. "
  echo " cp $MANAGER_SOURCE/mainserver.py $MANAGER_DESTINATION/ "
  if [ -f "$SQL3_DESTINATION_FILE" ] ; then
    echo "File exists. Back it up to $SQL3_DESTINATION_FILE.$today. "
    mv -v $SQL3_DESTINATION_FILE $SQL3_DESTINATION_FILE.$today
  fi
  echo " copy the database from $DATABASE_SOURCE_FILE to $DATABASE_DESTINATION_FILE  "
  cp -v $SQL3_SOURCE_FILE $SQL3_DESTINATION_FILE
}

help(){
  echo " eggheadserver.sh -a [django|manager|shutdown|testhenri|infrastructure] -display -logging [INFO|DEBUG|] -report [LEVEL0|LEVEL1|LEVEL2|LEVEL3]"
  echo " eggheadserver.sh -t [single|component|comp|all] -c [<unittests comp list>] -display -logging [INFO|WARN] -report [LEVEL0|LEVEL2]"
  echo " eggheadserver.sh -s [single|component|comp|all] -c [<selenium comp list>] -display -logging [INFO|WARN] -report [LEVEL0] -b [chrome|safari|opera]"
  echo " eggheadserver.sh -h"
  echo " eggheadserver.sh -strategies [babadjou,batcham,balachi]"
  echo " eggheadserver.sh -e"
  echo " eggheadserver.sh -docs"
  echo " Components: $components"
  exit 1
}

#export UI_BASE="${BASE_PKG}.selenium"
#export BE_BASE="${BASE_PKG}.unittests"
#BASE_PKG="bullbearetfs"
generateDocs(){
  echo "Generate Pydoc for all components"
  echo "PYTHON PATH = $PYTHONPATH"
  export DJANGO_SETTINGS_MODULE=etfs.settings
  export SRC_FOLDERS="${BASE_PKG}.dummy ${DOC_SRC1} ${DOC_SRC2} ${DOC_SRC3} "
  export BE_TST_DOCS_SRC_FOLDERS="${BE_BASE} ${BED_DUMMY} ${DOC_BE1} ${DOC_BE2} ${DOC_BE3}"
  export UI_TST_DOCS_SRC_FOLDERS="${UI_BASE} ${UID_DUMMY} ${DOC_UI1} ${DOC_UI2} ${DOC_UI3}"
  export DEST_FOLDERS=./docs
  echo "Delete all the previews Docs HTML files"

#export BED_DUMMY="${BE_BASE}.dummy"
#export UID_DUMMY="${UI_BASE}.dummy"
  echo "Generate the DOCS for the Sources: models, forms, views, urls, packages "
  echo "python -m pydoc -w $SRC_FOLDERS"
  python -m pydoc -w $SRC_FOLDERS

  echo "Generate the DOCS for the Backend Tests: packages, modules unittest/<component>/tests"
  echo "python -m pydoc -w $BE_TST_DOCS_SRC_FOLDERS"
  python -m pydoc -w $BE_TST_DOCS_SRC_FOLDERS

  echo "Generate the DOCS for the UI Tests:  packages, modules selenium/<component>/tests"
  echo "python -m pydoc -w $UI_TST_DOCS_SRC_FOLDERS"
  python -m pydoc -w $UI_TST_DOCS_SRC_FOLDERS

  echo "Move the new doc to the dest docs folder $DEST_FOLDERS"

  echo "mv $SRC_FOLDERS/*.html $DEST_FOLDER/."
  echo "To view full documentation, type the following command: "
  
}

processStrategyTests(){
STRATEGY_TESTS=
while [ "$1" != "" ] ; do
  case $1 in
    babadjou ) STRATEGY_TESTS="$STRATEGY_TESTS ${TST_BABADJOU}" ;;
    batcham) STRATEGY_TESTS="$STRATEGY_TESTS ${TST_BATCHAM}" ;;
    balachi) STRATEGY_TESTS="$STRATEGY_TESTS ${TST_BALACHI}" ;;
    bangang) STRATEGY_TESTS="$STRATEGY_TESTS ${TST_BANGANG}" ;;
    bamendjinda) STRATEGY_TESTS="$STRATEGY_TESTS ${TST_BAMENDJINDA}" ;;
    *) echo "invalid $1 " ;;
  esac
 shift
done
}

processUITests(){
COMP_TESTS=
while [ "$1" != "" ] ; do
  
  case $1 in
    foundation ) COMP_TESTS="$COMP_TESTS ${UI_FOUND}" ;;
    basic ) COMP_TESTS="$COMP_TESTS ${UI_BASIC}" ;;
    robotmgmt |robot ) COMP_TESTS="$COMP_TESTS $UI_RMGMT" ;;
    symbols ) COMP_TESTS="$COMP_TESTS $UI_SYMBS" ;;
    budget|portfolio ) COMP_TESTS="$COMP_TESTS $UI_PBDGT" ;;
    activity|sentiment|market ) COMP_TESTS="$COMP_TESTS $UI_ACTSE" ;;
    runtime|robotruntime ) COMP_TESTS="$COMP_TESTS $UI_RUNTE" ;;
    customer ) COMP_TESTS="$COMP_TESTS $UI_CUSTM" ;;
    utilities|utility ) COMP_TESTS="$COMP_TESTS $UI_UTLTY" ;;
    errors|error) COMP_TESTS="$COMP_TESTS $UI_ERROR" ;;

    datasources) COMP_TESTS="$COMP_TESTS $UI_SOUR" ;;
    brokerages) COMP_TESTS="$COMP_TESTS $UI_BRKAG" ;;
    conditionals|conditional ) COMP_TESTS="$COMP_TESTS $UI_RCOND" ;;
    reportdata ) COMP_TESTS="$COMP_TESTS $UI_RDATA" ;;
    strategies) COMP_TESTS="$COMP_TESTS $UI_INDST" ;;
    strategyinfra) COMP_TESTS="$COMP_TESTS $UI_STGYI" ;;

    eventcapture|events ) COMP_TESTS="$COMP_TESTS ${UI_EVTCA}" ;;
    bintelligence ) COMP_TESTS="$COMP_TESTS $UI_BUINT" ;;
    dashboard ) COMP_TESTS="$COMP_TESTS $UI_DASHB" ;;
    executionengine|exengine ) COMP_TESTS="$COMP_TESTS $UI_EXENG" ;;
    reportgeneration|reports) COMP_TESTS="$COMP_TESTS $UI_RPTGE" ;;
    datasetup ) COMP_TESTS="$COMP_TESTS $UI_SETUP" ;;
    migration ) COMP_TESTS="$COMP_TESTS $UI_MIGRA" ;;
    deploymentchklist|deployment ) COMP_TESTS="$COMP_TESTS $UI_CHKLS" ;;
    others|other) COMP_TESTS="$COMP_TESTS $UI_OTHER" ;;
    *) echo "invalid $1 " ;;
  esac
 shift
done
}

processBETests(){
COMP_TESTS=
while [ "$1" != "" ] ; do
  
  case $1 in
    foundation ) COMP_TESTS="$COMP_TESTS ${BE_FOUND}" ;;
    basic ) COMP_TESTS="$COMP_TESTS ${BE_BASIC}" ;;
    robotmgmt |robot ) COMP_TESTS="$COMP_TESTS $BE_RMGMT" ;;
    symbols ) COMP_TESTS="$COMP_TESTS $BE_SYMBS" ;;
    budget|portfolio ) COMP_TESTS="$COMP_TESTS $BE_PBDGT" ;;
    activity|sentiment|market ) COMP_TESTS="$COMP_TESTS $BE_ACTSE" ;;
    runtime|robotruntime ) COMP_TESTS="$COMP_TESTS $BE_RUNTE" ;;
    customer ) COMP_TESTS="$COMP_TESTS $BE_CUSTM" ;;
    utilities|utility ) COMP_TESTS="$COMP_TESTS $BE_UTLTY" ;;
    errors|error) COMP_TESTS="$COMP_TESTS $BE_ERROR" ;;

    datasources) COMP_TESTS="$COMP_TESTS $BE_SOUR" ;;
    brokerages) COMP_TESTS="$COMP_TESTS $BE_BRKAG" ;;
    conditionals|conditional ) COMP_TESTS="$COMP_TESTS $BE_RCOND" ;;
    reportdata ) COMP_TESTS="$COMP_TESTS $BE_RDATA" ;;
    strategies) COMP_TESTS="$COMP_TESTS $BE_INDST" ;;
    strategyinfra) COMP_TESTS="$COMP_TESTS $BE_STGYI" ;;

    eventcapture|events ) COMP_TESTS="$COMP_TESTS ${BE_EVTCA}" ;;
    bintelligence ) COMP_TESTS="$COMP_TESTS $BE_BUINT" ;;
    dashboard ) COMP_TESTS="$COMP_TESTS $BE_DASHB" ;;
    executionengine|exengine ) COMP_TESTS="$COMP_TESTS $BE_EXENG" ;;
    reportgeneration|reports) COMP_TESTS="$COMP_TESTS $BE_RPTGE" ;;
    datasetup ) COMP_TESTS="$COMP_TESTS $BE_SETUP" ;;
    migration ) COMP_TESTS="$COMP_TESTS $BE_MIGRA" ;;
    deploymentchklist|deployment ) COMP_TESTS="$COMP_TESTS $BE_CHKLS" ;;
    others|other) COMP_TESTS="$COMP_TESTS $BE_OTHER" ;;
    *) echo "invalid $1 " ;;
  esac
 shift
done
}

describe() { 
  echo -e $description
}

processCMD(){
echo "PROCESSING $0: with... $*"
browser_name=$DEFAULT_BROWSER
comp_name=$DEFAULT_COMPONENT
export PRINT_VAR=
export LOGGING_LEVEL=INFO
export REPORT_LEVEL=OFF
while [ "$1" != "" ] ; do
  case $1 in
    -a | -action ) shift
                  level="level1"
                  action="$1"
                  ;;

    -t | -u | -unittest ) shift
                  level="level2"
                  tests_u="$1"
                  ;;

    -s | -selenium ) shift
                  level="level3"
                  tests_s="$1"
                  ;;

    -c | -comp | -component ) shift
                  comp_name="$1"
                  ;;

    -b | -browser ) shift
                  browser_name="$1"
                  ;;

    -strategies) shift
               level="level5"
               strategies="$1"
                  ;;

    -display ) 
             PRINT_VAR="TRUE"
                      ;;

    -report | -rpt ) shift
                  export REPORT_LEVEL="$1"
                      ;;

    -logging | -log ) shift
                  export LOGGING_LEVEL="$1"
                      ;;

    -h | -help ) help
                 ;;

    -docs ) generateDocs
                 level="level4"
                 ;;

    -e | -describe ) 
                 level="level0"
                 describe
                 ;;
    *) help
       ;;
  esac
 shift
done
}

components=foundation,basic,robot,budget,symbols,market,conditional,reportdata,brokerages,strategyinfra,strategies,datasources,robotruntime,customer,utilities,errors,eventcapture,bintelligence,dashboard,executionengine,reportgeneration,datasetup,migration,deploymentchklist,others

##############MAIN Starts Here ###########
processCMD $*

case $level in
  level0)
    echo -e ""
    ;;
  level4)
    echo "Calling the Pydoc Generator"
    ;;
  level5)
    echo "Running all tests for Strategies $strategies"
      strategy_names=`echo $strategies | sed 's/,/ /g'`
      processStrategyTests $strategy_names
      runStrategyTests
    ;;
  level1) 
    echo " Backend Unit Test selected "
    if [ "X$action" = "Xdjango" ] ; then
      echo "Django Server action"]
      runDjangoServer 
    elif [ "X$action" = "Xmanager" ] ; then
      echo "Runtime Manager start "
      runEggheadManager
    elif [ "X$action" = "Xdeploy" ] ; then
      echo "Deployment action "
      deployManager
    elif [ "X$action" = "Xshutdown" ] ; then
      echo "Runtime Manager stop"
      runShutdownManager
    elif [ "X$action" = "Xtesthenri" ] ; then
      echo "Runtime Manager stop"
      testhenri
    elif [ "X$action" = "Xinfrastructure" ] ; then
      echo "Runtime Manager stop"
      runSetupData
    else
      echo "NO valid option was selected  "
    fi
    ;;

  level2) 
    echo "Backend Unit Tests Selected "
    if [ "X$tests_u" = "Xsingle" ] ; then
      echo "Single Unit Test selected"
      runSingleUnitTest
    elif [ "X$tests_u" = "Xall" ] ; then
      echo "ALL Unit Tests selected  "]
      component_names=`echo $components | sed 's/,/ /g'`
      processBETests $component_names
      runALLUnitTests
    elif [ "X$tests_u" = "Xcomp" ] ; then
      echo "\n\n" 
      echo "Component Based Unittests for component = $comp_name"
      component_names=`echo $comp_name | sed 's/,/ /g'`
      echo "Values=$component_names"
      processBETests $component_names
      runComponentUnitTests
    else
      echo "NO valid option was selected in Backend Tests  "
    fi
    ;;

  level3) 
    echo "Selenium Tests Selected "
    if [ "X$tests_s" = "Xsingle" ] ; then
      echo "Single Selenium Test selected"]
      if [ "X$browser_name" = "Xchrome" -o "X$browser_name" = "Xopera" ] ; then
         echo "Browser Selection =$browser_name " 
      else
        browser_name=$DEFAULT_BROWSER
      fi 
      echo "\n\n" 
      runSingleSeleniumTest
    elif [ "X$tests_s" = "Xall" ] ; then
      echo "ALL Selenium Tests selected  "]
      if [ "X$browser_name" = "Xchrome" -o "X$browser_name" = "Xopera" ] ; then
         echo "Browser Selection =$browser_name " 
      else
        browser_name=$DEFAULT_BROWSER
      fi 
      component_names=`echo $components | sed 's/,/ /g'`
      processUITests $component_names
      runALLSeleniumTests
    elif [ "X$tests_s" = "Xcomp"  -o "Xtests_s" = "Xcomponent" ] ; then
      if [ "X$browser_name" = "Xchrome" -o "X$browser_name" = "Xopera" ] ; then
         echo "Browser Selection =$browser_name " 
      else
        browser_name=$DEFAULT_BROWSER
      fi 
      echo "\n\n" 
      echo "Component Based Selenium Tests for component = $comp_name"
      component_names=`echo $comp_name | sed 's/,/ /g'`
      echo "Values=$component_names"
      processUITests $component_names
      runComponentSeleniumTests
    else
      echo "NO valid option was selected in UI Tests  "
    fi
    ;;
  *) help ;; 
esac

