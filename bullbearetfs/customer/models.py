from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import datetime
from django.utils import timezone
from django.contrib.auth.models import  User
CHOICES_INVESTOR_TYPE =(('Day Trader','Day Trader'),('Swing Trader','Swing Trader'),('Long Term Investor','Long Term Investor'))
CHOICES_ASSETS_PREFERENCE = (('US Equity','US Equity'),('Market Indices','Market Indices'),('Stocks','Stocks'))
CHOICES_RISK_TOLERANCE = (('High','High'),('Medium','Medium'),('Low','Low'))

CHOICES_ACCOUNT_TYPES = (('Free','Free'),('Paid','Paid'),('Trial','Trial'))
CHOICES_BILLING_TYPES = (('Visa','Visa'),('Mastercard','Mastercard'),('Discover','Discover'),('Paypal','Paypal'))
# Jobs titles
CHOICES_JOB_TITLES = (('Principal','Principal'),('Director','Director'),('S','Student'),('N/A','Not Available'),)


# ######################## User Management Package ######
# Consists of the section that deals with user specific
# information such as:
# Customer model is the complete and contains:
#   CustomerBasic (first name, last name, email, phone, username)
#   CustomerSecurity (password, recovery, alternate, challenges, bio)
#   CustomerProfile (Picture, short bio, job title)
#   CustomerAddress (Street, City, Zip, Country, Geo)
#   CustomerBusiness (Company, website, phone)
#   CustomerSettings (Messages Notification)

class CustomerBasic(models.Model):
  first_name = models.CharField(max_length=50,default='')
  last_name = models.CharField(max_length=50,default='')
  username = models.CharField(max_length=50,default='')
  main_phone = models.CharField(max_length=30, default='')
  alternate_phone = models.CharField(max_length=30, default='')
  main_email = models.CharField(max_length=30,default='')
  alternate_email = models.CharField(max_length=30,default='')

  def __str__(self):
    return "{0} {1} {2}".format(self.first_name,self.last_name,self.username)

# password, recovery, hint questions and answers
# TODO: implement hints
class CustomerSecurity(models.Model):
  name = models.CharField(max_length=25,default='')
  password = models.CharField(max_length=50, default='')
  recovery_phone = models.CharField(max_length=30, default='')
  recovery_email = models.CharField(max_length=30,default='')
  password_hint_1 = models.CharField(max_length=30,default='')
  password_hint_2 = models.CharField(max_length=30,default='')
  password_hint_3 = models.CharField(max_length=30,default='')
  enable_two_step = models.BooleanField(default=False)

  def __str__(self):
    return "{0} {1}".format(self.recovery_phone,self.recovery_email)

class Address(models.Model):
  street = models.CharField(max_length=20,default='')
  city = models.CharField(max_length=20,default='')
  zipcode = models.CharField(max_length=10,default='')
  state = models.CharField(max_length=20,default='')
  country = models.CharField(max_length=10,default='')
  geolocation = models.TextField(default=' ')

  def __str__(self):
    return "{0} {1} {2} {3}".format(self.street, self.zipcode, self.state,  self.country)

# business_name, address, website
class BusinessInformation(models.Model):
  company_name = models.CharField(max_length=50,default='')
  address = models.ForeignKey(Address, on_delete=models.PROTECT) #TODO: This is not required
  website = models.CharField(max_length=40,default='') #TODO: This is not required.

  def __str__(self):
    return "{0} {1}".format(self.company_name,self.website)

# TODO: Add Listener, when membership status is modified.
# Can also go on validation. 
class Billing(models.Model):
  creation_date = models.DateTimeField('date created',default=timezone.now)
  modified_date = models.DateTimeField('date modified',default=timezone.now)
  name = models.CharField(max_length=25,default='')
  membership_status = models.CharField(max_length=10,choices=CHOICES_ACCOUNT_TYPES,default='Trial')
  status_creation_date = models.DateTimeField('date created',default=timezone.now)
  billing_information = models.CharField(max_length=10,choices=CHOICES_BILLING_TYPES,default='Visa')
  credit_card_number = models.CharField(max_length=20,default='')
  #Foreign Keys
  address = models.ForeignKey(Address, on_delete=models.PROTECT, default=1)
  #Functions
  def __str__(self):
    return "{0} {1} ".format(self.name, self.membership_status)

#Customer Profile (change type, team)
class CustomerProfile(models.Model):
  #TODO: In order to use imageField, pillow MUST be installed
  #main_picture = models.ImageField(upload_to = 'pic_folder/', default = '')
  job_title = models.CharField(max_length=25, choices = CHOICES_JOB_TITLES,default='Investor')
  short_bio = models.TextField(default=' ')
  tax_bracket = models.IntegerField(default=30)

  def __str__(self):
    return "{0} {1} ".format(self.job_title, self.tax_bracket)

# 
# Customer is an aggregation of various information
#
class Customer(models.Model):
  creation_date = models.DateTimeField('date created',auto_now_add=True)
  modified_date = models.DateTimeField('date modified',auto_now_add=True)
  #Foreigh Keys
  basic_information = models.ForeignKey(CustomerBasic,on_delete=models.PROTECT,default=1)
  security_information = models.ForeignKey(CustomerSecurity,on_delete=models.PROTECT,default=1)
  billing = models.ForeignKey(Billing,on_delete=models.PROTECT,default=1)
  #investor_profile = models.ForeignKey(InvestmentInterest,on_delete=models.PROTECT,default=1)
  company = models.ForeignKey(BusinessInformation,on_delete=models.PROTECT,default=1)
  personal_profile = models.ForeignKey(CustomerProfile,on_delete=models.PROTECT,blank=True,null=True)

  def __str__(self):
    return "{0} {1}".format(self.basic_information.first_name,self.basic_information.last_name)
