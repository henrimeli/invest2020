#!/bin/bash
export RUNSERVERPORT=8002
today=`date '+%Y_%m_%d__%H_%M_%S'`

#migrations command 1: python manage.py makemigrations pages
#migrations command 2: python manage.py migrate pages

runDjangoServer() {
  echo "Starting the Django Server "
  echo "------ Running the Django Server for the Stock Investment Application 2020 on port $RUNSERVERPORT "
  python manage.py runserver 127.0.0.1:$RUNSERVERPORT
}

runUnitTest(){
  echo "Running Unit Test "
  python -Wa  manage.py test invest2020.unittests.tradedataholder.tests 
  exit 1
}


runAllUnitTests(){
  echo "Running Unit Test "
  exit 1
}


processCMD(){
echo "PROCESSING $0: with... $*"
while [ "$1" != "" ] ; do
  case $1 in
    -a | --action ) shift
                  action="$1"
                  ;;

    -d | --debug ) 
                  DEBUG="TRUE"
                      ;;
    -h | --help ) help
                 ;;
    *) help
       ;;
  esac
 shift
done
}

help(){
  echo " runInvest.sh -a [ django | unittests | unittest | all  ] -d "
  exit 1
}

##############MAIN Starts Here ###########
processCMD $*

case $action in
  django)  runDjangoServer     ;;
  unittest | single)   runUnitTest    ;;
  all | unittests)   runAllUnitTests    ;;
  *) help ;; 
esac
