from django.db import models

# Create your models here.
# Type of Notification such as:
# 1. doc shared notification
# 2. message notification
class NotificationType(models.Model):
  name = models.CharField(max_length=20,default='')
  value = models.IntegerField(default=0)
  #ok = models.IntegerField(default=0)

  def __str__(self):
    return "{0} {1} ".format(self.name, self.value)