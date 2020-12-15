from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import datetime
from django.utils import timezone
from django.contrib.auth.models import  User

"""
  TODO: Describe the Module here ...

  List the classes of the module here
"""

# ######################## Dashboard #############

class Dashboard(models.Model):
  """
    TODO: Describe the dashboard class here
  """
  subject = models.CharField(max_length=50,default='')
  email = models.EmailField()
  comment = models.TextField()

  def __str__(self):
    return "{0} {1} ".format(self.email,self.subject)
