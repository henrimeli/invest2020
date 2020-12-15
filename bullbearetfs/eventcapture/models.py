from django.db import models
from datetime import timedelta
from django.utils.timezone import datetime
from datetime import date
from django.utils import timezone
from django.contrib.auth.models import  User
import logging
from bullbearetfs.utilities.core import getTimeZoneInfo, getReversedTuple,displayOutput,displayError,strToDatetime

"""
  TODO: Describe the Module here ...

  List the classes of the module here
"""

logger = logging.getLogger(__name__)

#
# Startup Status
# time, action, robot, comment 
CHOICES_STARTUP_ACTIONS = (('start','start'),('stop','stop'))
class StartupStatus(models.Model):
  """
      TODO: Describe the class here

      List the methods of the class here
  """
  log_time = models.DateTimeField('date created',default=timezone.now)
  comment = models.CharField(max_length=50,default='',blank=True,null=True)
  action = models.CharField(max_length=10, choices = CHOICES_STARTUP_ACTIONS,default='start')
  object_type = models.CharField(max_length=10, choices = CHOICES_STARTUP_ACTIONS,default='start')
  object_identifier = models.IntegerField(default=0,blank=True,null=True)
  modified_by = models.ForeignKey('Customer',on_delete=models.PROTECT, blank=True,null=True)

  def __str__(self):
    return "Startup-time-{0} ".format(self.log_time )

  @staticmethod
  def recordTransaction(log_time,action,object_type,object_id, modified_by,comment): 
    """ TODO: Describe the method here"""
    StartupStatus.objects.create(log_time=log_time,action=action,object_type=object_type,object_identifier=object_id,comment=comment)

  @staticmethod
  def getUptimeOfRobot(robot_id):
    """ TODO: Describe the method here"""
    starts = StartupStatus.objects.filter(object_identifier=robot_id).filter(action='start').orderby('log_time')
    stops = StartupStatus.objects.filter(object_identifier=robot_id).filter(action='stop').orderby('log_time')
    start = None if (len(starts)==0) else starts[0]
    stop = None if (len(stops)==0) else stops[0]
    current_time = datetime.now(getTimeZoneInfo())
    return 0 if (stop>start) else round((current_time-start).total_seconds()/60,2)    
    
  def getNumberOfEvents(robot_id):
    """ TODO: Describe the method here"""
    starts = StartupStatus.objects.filter(object_identifier=robot_id)
    return len(starts)
