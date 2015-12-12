from django.contrib.auth.models import User
from django.db import models

import datetime, os, time


def cust_file_path(instance, filename, filetype):   
   username = instance.creator.username

   ts = time.time()
   timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M:%S')

   _, file_ext = os.path.splitext(filename)
   new_filename = timestamp + file_ext

   return os.path.join(username, filetype, new_filename)

def cust_file_path_aud(instance, filename):
   return cust_file_path(instance, filename, 'audio')

def cust_file_path_img(instance, filename):
   return cust_file_path(instance, filename, 'image')


class Message(models.Model):
   audio_file = models.FileField(upload_to=cust_file_path_aud, blank=True, null=True)
   msg_text   = models.CharField(max_length=256, blank=True, null=True)
   image_file = models.ImageField(upload_to=cust_file_path_img, blank=True, null=True)

   # Make QR code string maximum length of 255.
   qr_str = models.CharField(unique=True, max_length=255)

   creator          = models.ForeignKey(User)
   create_date      = models.DateTimeField('date created')
   last_access_date = models.DateTimeField('last access', blank=True, null=True)
   access_count     = models.PositiveIntegerField(default=0)


   def increment_access_count(self):
      self.access_count += 1

   def __unicode__(self):
      return 'Message #' + str(self.id) + ': ' + self.msg_text

