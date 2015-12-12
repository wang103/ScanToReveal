from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from .models import Message
from .models import cust_file_path_aud, cust_file_path_img

import json, os, random


def create_user(username):
   user = User(username=username)
   user.save()
   return user


def create_msg(msg_text, qr_str, creator):
   create_date = timezone.now()
   last_access_date = None
   access_count = 0

   msg = Message(msg_text=msg_text,
                 qr_str=qr_str, creator=creator, create_date=create_date,
                 last_access_date=last_access_date, access_count = access_count)
   msg.save()
   return msg


class SubmitNewMessageTests(TransactionTestCase):

   def test_submit_two_new_msgs_with_same_init_qr_str(self):
      msg_text = 'hello'
      username = 'tianyiw'
      user = create_user(username)
      post_data = {'msg_text': msg_text,
                   'creator': username}

      random.seed(1)
      response_str = self.client.post(reverse('stvcore:submit_new_msg'), post_data)
      response = json.loads(response_str.content)

      msg1_qr_str = response['msg_detail']['qr_str']

      self.assertTrue(response['success'])
      self.assertEqual(response['msg_detail']['msg_text'], msg_text)
      self.assertEqual(response['msg_detail']['creator'], username)

      msg_text = 'hi'
      post_data['msg_text'] = msg_text

      random.seed(1)
      response_str = self.client.post(reverse('stvcore:submit_new_msg'), post_data)
      response = json.loads(response_str.content)

      msg2_qr_str = response['msg_detail']['qr_str']

      self.assertTrue(response['success'])
      self.assertEqual(response['msg_detail']['msg_text'], msg_text)
      self.assertEqual(response['msg_detail']['creator'], username)

      self.assertNotEqual(msg1_qr_str, msg2_qr_str)

   def test_submit_one_new_msg(self):
      msg_text = 'hello'
      username = 'tianyiw'
      user = create_user(username)
      post_data = {'msg_text': msg_text,
                   'creator': username}

      response_str = self.client.post(reverse('stvcore:submit_new_msg'), post_data)
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertEqual(response['msg_detail']['msg_text'], msg_text)
      self.assertEqual(response['msg_detail']['creator'], username)

   def test_submit_new_msg_without_creator(self):
      post_data = {}
      response_str = self.client.post(reverse('stvcore:submit_new_msg'), post_data)
      response = json.loads(response_str.content)

      self.assertFalse(response['success'])

   def test_submit_new_msg_with_invalid_creator(self):
      post_data = {'creator': 'tianyiw'}
      response_str = self.client.post(reverse('stvcore:submit_new_msg'), post_data)
      response = json.loads(response_str.content)

      self.assertFalse(response['success'])


class NewMessageViewTests(TestCase):

   def test_new_msg_view(self):
      response = self.client.get(reverse('stvcore:new_msg'))
      self.assertEqual(response.status_code, 200)


class MessageDetailViewTests(TestCase):

   def test_msg_detail_view_with_valid_qr_str(self):
      msg_text = 'hello'
      qr_str = '000'
      username = 'tianyiw'
      user = create_user(username)
      msg = create_msg(msg_text, qr_str, user)

      response_str = self.client.get(reverse('stvcore:msg_detail', args=(qr_str,)))
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertEqual(response['msg_detail']['msg_text'], msg_text)
      self.assertEqual(response['msg_detail']['qr_str'], qr_str)
      self.assertEqual(response['msg_detail']['creator'], username)

   def test_msg_detail_view_with_invalid_qr_str(self):
      qr_str = '000'
      response_str = self.client.get(reverse('stvcore:msg_detail', args=(qr_str,)))
      response = json.loads(response_str.content)

      self.assertFalse(response['success'])


class UserMessagesViewTests(TestCase):

   def test_user_msgs_view_with_two_msgs(self):
      username = 'tianyiw'
      user = create_user(username)
      msg1 = create_msg('hi', '000', user)
      msg2 = create_msg('hello', '001', user)
      
      response_str = self.client.get(reverse('stvcore:user_msgs', args=(username,)))
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertEqual(response['msgs'][0]['qr_str'], msg2.qr_str)
      self.assertEqual(response['msgs'][1]['qr_str'], msg1.qr_str)

   def test_user_msgs_view_with_one_msg(self):
      username = 'tianyiw'
      user = create_user(username)
      msg1 = create_msg('hi', '000', user)
      
      response_str = self.client.get(reverse('stvcore:user_msgs', args=(username,)))
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertEqual(response['msgs'][0]['qr_str'], msg1.qr_str)

   def test_user_msgs_view_with_empty_msgs(self):
      username = 'tianyiw'
      create_user(username)
      response_str = self.client.get(reverse('stvcore:user_msgs', args=(username,)))
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])

   def test_user_msgs_view_with_invalid_username(self):
      username = 'tianyiw'
      response_str = self.client.get(reverse('stvcore:user_msgs', args=(username,)))
      response = json.loads(response_str.content)

      self.assertFalse(response['success'])


class UserInfoViewTests(TestCase):

   def test_user_info_view_with_valid_username(self):
      username = 'tianyiw'
      create_user(username)
      response_str = self.client.get(reverse('stvcore:user_info', args=(username,)))
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertEqual(response['user_info']['username'], username)

   def test_user_info_view_with_invalid_username(self):
      username = 'tianyiw'
      response_str = self.client.get(reverse('stvcore:user_info', args=(username,)))
      response = json.loads(response_str.content)

      self.assertFalse(response['success'])


class MessageMethodTests(TestCase):

   def test_increment_access_count(self):
      msg = Message()
      self.assertEqual(msg.access_count, 0)
      msg.increment_access_count()
      self.assertEqual(msg.access_count, 1)

   def test_cust_file_path_aud(self):
      user = User(username = 'tianyiw')
      msg = Message(creator=user)
      filename = 'Mozart.mp3'

      actual = cust_file_path_aud(msg, filename)
      expected_start = os.path.join('tianyiw', 'audio')
      expected_end = '.mp3'
      
      self.assertTrue(actual.startswith(expected_start))
      self.assertTrue(actual.endswith(expected_end))
      self.assertEqual(actual.find('Mozart'), -1)

   def test_cust_file_path_img(self):
      user = User(username = 'tianyiw')
      msg = Message(creator=user)
      filename = 'cat.png'

      actual = cust_file_path_img(msg, filename)
      expected_start = os.path.join('tianyiw', 'image')
      expected_end = '.png'

      self.assertTrue(actual.startswith(expected_start))
      self.assertTrue(actual.endswith(expected_end))
      self.assertEqual(actual.find('cat'), -1)

