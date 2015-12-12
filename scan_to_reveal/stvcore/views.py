from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

import random

from .models import Message


def user_info(request, username):
   response = {}
   try:
      user = User.objects.get(username=username)
   except (User.DoesNotExist):
      response['success'] = False
      return JsonResponse(response)

   user_info = {}
   user_info['username'] = user.username
   user_info['id'] = user.id
   user_info['last_login'] = user.last_login
   user_info['is_superuser'] = user.is_superuser
   user_info['first_name'] = user.first_name
   user_info['last_name'] = user.last_name
   user_info['email'] = user.email
   user_info['date_joined'] = user.date_joined

   response['user_info'] = user_info
   response['success'] = True

   return JsonResponse(response)


def user_msgs(request, username):
   response = {}
   try:
      user = User.objects.get(username=username)
   except (User.DoesNotExist):
      response['success'] = False
      return JsonResponse(response)

   msg_list = Message.objects.filter(creator=user).order_by('-create_date')
   msgs = []

   for msg in msg_list:
      cur_msg = {}
      cur_msg['qr_str'] = msg.qr_str
      cur_msg['create_date'] = msg.create_date
      msgs.append(cur_msg)
 
   response['msgs'] = msgs
   response['success'] = True

   return JsonResponse(response)


def get_msg_detail_in_dict(msg):
   msg_detail = {}

   msg_detail['id'] = msg.id
   if msg.audio_file:
      msg_detail['audio_file'] = msg.audio_file.url
   msg_detail['msg_text'] = msg.msg_text
   if msg.image_file:
      msg_detail['image_file'] = msg.image_file.url
   msg_detail['qr_str'] = msg.qr_str
   msg_detail['creator'] = msg.creator.username
   msg_detail['create_date'] = msg.create_date
   msg_detail['last_access_date'] = msg.last_access_date
   msg_detail['access_count'] = msg.access_count

   return msg_detail


def msg_detail(request, msg_qr_str):
   response = {}
   try:
      msg = Message.objects.get(qr_str=msg_qr_str)
   except (Message.DoesNotExist):
      response['success'] = False
      return JsonResponse(response)

   msg_detail = get_msg_detail_in_dict(msg)

   response['msg_detail'] = msg_detail
   response['success'] = True

   return JsonResponse(response)


def new_msg(request):
   context = {}
   template = 'stvcore/new_msg.html'

   return render(request, template, context)


def submit_new_msg(request):
   response = {}
   try:
      creator = User.objects.get(username=request.POST['creator'])
   except (KeyError, User.DoesNotExist):
      response['success']= False
      return JsonResponse(response)

   try:
      audio_file = request.FILES['audio_file']
   except (KeyError):
      audio_file = None

   try:
      msg_text = request.POST['msg_text']
   except (KeyError):
      msg_text = None

   try:
      image_file = request.FILES['image_file']
   except (KeyError):
      image_file = None

   create_date = timezone.now()
   last_access_date = None
   access_count = 0

   # The QR string field in DB is at most 255 chars, and each char is a digit.
   # This means there are 10^255 possible values.
   # 2^847 < 10^255, so we set the randbits to be 847 here.
   num_rand_bit = 847

   qr_str = str(random.getrandbits(num_rand_bit))

   # Create the new message and save it to the database.
   msg = Message(audio_file=audio_file, msg_text=msg_text, image_file=image_file,
                 qr_str=qr_str, creator=creator, create_date=create_date,
                 last_access_date=last_access_date, access_count = access_count)

   save_is_successful = False
   while not save_is_successful:
      try:
         msg.save()
      except (IntegrityError):
         # Another msg with the same qr string exists, generate another one.
         qr_str = str(random.getrandbits(num_rand_bit))
         msg.qr_str = qr_str
         continue
      save_is_successful = True

   msg_detail = get_msg_detail_in_dict(msg)

   response['msg_detail'] = msg_detail
   response['success'] = True
 
   return JsonResponse(response)

