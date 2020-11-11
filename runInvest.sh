export RUNSERVERPORT=8002
echo "------ Running the Django Server for the Stock Investment Application 2020 on port $RUNSERVERPORT "
python manage.py runserver 127.0.0.1:$RUNSERVERPORT
