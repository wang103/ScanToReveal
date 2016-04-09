from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

import random
import utils

from .models import Message


def login_usr(request):
   response = {}

   username = request.POST['username']
   password = request.POST['password']

   user = authenticate(username=username, password=password)

   if user is None:
      response['success'] = False
      response['ec'] = utils.EC_INVALID_CREDS
      return JsonResponse(response)

   if not user.is_active:
      response['success'] = False
      response['ec'] = utils.EC_ACCOUNT_DISABLED
      return JsonResponse(response)

   login(request, user)

   usr_detail = get_usr_detail_in_dict(user)

   response['user_info'] = usr_detail
   response['success'] = True

   return JsonResponse(response)


def logout_usr(request):
   response = {}
   logout(request)
   response['success'] = True
   return JsonResponse(response)


def check_login(request):
   response = {}
   response['is_logged_in'] = request.user.is_authenticated()
   response['success'] = True
   return JsonResponse(response)


# Private helper method.
def get_usr_detail_in_dict(usr):
   usr_detail = {}

   usr_detail['id'] = usr.id
   usr_detail['username'] = usr.username
   usr_detail['last_login'] = usr.last_login
   usr_detail['is_superuser'] = usr.is_superuser
   usr_detail['email'] = usr.email
   usr_detail['first_name'] = usr.first_name
   usr_detail['last_name'] = usr.last_name
   usr_detail['date_joined'] = usr.date_joined

   return usr_detail


def user_info(request):
   response = {}

   user = request.user

   if not user.is_authenticated():
      response['success'] = False
      response['ec'] = utils.EC_NOT_LOGGED_IN
      return JsonResponse(response)

   usr_detail = get_usr_detail_in_dict(user)

   response['user_info'] = usr_detail
   response['success'] = True

   return JsonResponse(response)


def user_msgs(request):
   response = {}

   user = request.user

   if not user.is_authenticated():
      response['success'] = False
      response['ec'] = utils.EC_NOT_LOGGED_IN
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


# Private helper method.
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

   # Update meta info.
   msg.last_access_date = timezone.now()
   msg.access_count += 1
   msg.save()

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

   user = request.user

   if not user.is_authenticated():
      response['success'] = False
      response['ec'] = utils.EC_NOT_LOGGED_IN
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

   if not audio_file and not msg_text and not image_file:
      response['success'] = False
      response['ec'] = utils.EC_EMPTY_MESSAGE
      return JsonResponse(response)

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
                 qr_str=qr_str, creator=user, create_date=create_date,
                 last_access_date=last_access_date, access_count=access_count)

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


def new_usr(request):
   context = {}
   template = 'stvcore/new_usr.html'

   return render(request, template, context)


def register_new_usr(request):
   response = {}

   try:
      username = request.POST['username']
   except (KeyError):
      username = None

   if not username:
      response['success'] = False
      response['ec'] = utils.EC_INVALID_USERNAME
      return JsonResponse(response)
  
   try:
      password = request.POST['password']
   except (KeyError):
      password = None

   if not password:
      response['success'] = False
      response['ec'] = utils.EC_INVALID_PASSWORD
      return JsonResponse(response)

   try:
      password_copy = request.POST['password_copy']
   except (KeyError):
      password_copy = None

   if password != password_copy:
      response['success'] = False
      response['ec'] = utils.EC_PASSWORDS_MISMATCH
      return JsonResponse(response)

   try:
      email = request.POST['email']
   except (KeyError):
      email = None

   try:
      validate_email(email)
   except (ValidationError):
      response['success'] = False
      response['ec'] = utils.EC_INVALID_EMAIL
      return JsonResponse(response)

   try:
      usr = User.objects.create_user(username, email, password)
   except (IntegrityError):
      response['success'] = False
      response['ec'] = utils.EC_USERNAME_EXISTS
      return JsonResponse(response)

   try:
      first_name = request.POST['first_name']
   except (KeyError):
      first_name = ''

   try:
      last_name = request.POST['last_name']
   except (KeyError):
      last_name = ''

   usr.first_name = first_name
   usr.last_name = last_name

   usr.save()

   usr_detail = get_usr_detail_in_dict(usr)

   response['usr_detail'] = usr_detail
   response['success'] = True
 
   return JsonResponse(response)

