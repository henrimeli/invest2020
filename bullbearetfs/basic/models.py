from django.db import models

"""
  TODO: Describe the Module here ...

  List the classes of the module here
"""

# Customer Settings. Notifications
# Watching offering based on criteria (change of rental data)
# Watching 
class Settings(models.Model):
  """
  This stores the settings of a given user

  List the methods of the class
  """
  settings_name = models.CharField(max_length=20,default='settings')
  connection_request=models.BooleanField(default=False)
  mentions = models.BooleanField(default=False)
  receive_deal_updates = models.BooleanField(default=False)
  receive_reminders = models.BooleanField(default=False)
  receive_annoucements = models.BooleanField(default=False)
  enable_two_step = models.BooleanField(default=False)
  customer = models.ForeignKey('Customer',on_delete=models.PROTECT)

  def __str__(self):
    return "{0} ".format(self.settings_name)
