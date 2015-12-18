from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from .models import Message
from .models import cust_file_path_aud, cust_file_path_img

import json, os, random, utils


def create_user(username, password):
   user = User.objects.create_user(username, '', password)
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


class EndToEndTests(TestCase):

   def test_end_to_end(self):

      # Register a new user.

      username = 'tianyiw'
      password = '123'

      post_data = {'username': username,
                   'password': password,
                   'password_copy': password,
                   'email': 'wang103uiuc@gmail.com',}

      response_str = self.client.post(reverse('stvcore:register_new_usr'), post_data)
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])

      # Login.

      post_data = {'username': username,
                   'password': password,}

      response_str = self.client.post(reverse('stvcore:login_usr'), post_data)
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertEqual(response['user_info']['username'], username)

      # Check user info.

      response_str = self.client.post(reverse('stvcore:user_info'), {})
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertEqual(response['user_info']['username'], username)
      self.assertEqual(response['user_info']['email'], 'wang103uiuc@gmail.com')

      # Submit a new message.

      msg_text = 'hello'
      post_data = {'msg_text': msg_text}

      response_str = self.client.post(reverse('stvcore:submit_new_msg'), post_data)
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertEqual(response['msg_detail']['msg_text'], msg_text)
      self.assertEqual(response['msg_detail']['creator'], username)

      # Retrieve the message's QR code via user.

      response_str = self.client.post(reverse('stvcore:user_msgs'), {})
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])

      qr_str = response['msgs'][0]['qr_str']

      # Retrieve the message via QR code.

      response_str = self.client.get(reverse('stvcore:msg_detail', args=(qr_str,)))
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertEqual(response['msg_detail']['msg_text'], msg_text)
      self.assertEqual(response['msg_detail']['qr_str'], qr_str)
      self.assertEqual(response['msg_detail']['creator'], username)

      # Logout.

      response_str = self.client.post(reverse('stvcore:logout_usr'), {})
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])

      response_str = self.client.post(reverse('stvcore:check_login'), {})
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertFalse(response['is_logged_in'])


class LoginAndLogoutTests(TestCase):

   def test_logout_without_login(self):
      response_str = self.client.post(reverse('stvcore:logout_usr'), {})
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])

   def test_login_logout_with_valid_credentials(self):
      username = 'tianyiw'
      password = '123'
      create_user(username, password)

      post_data = {'username': username,
                   'password': password,}

      response_str = self.client.post(reverse('stvcore:login_usr'), post_data)
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertEqual(response['user_info']['username'], username)

      response_str = self.client.post(reverse('stvcore:check_login'), {})
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertTrue(response['is_logged_in'])

      response_str = self.client.post(reverse('stvcore:logout_usr'), {})
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])

      response_str = self.client.post(reverse('stvcore:check_login'), {})
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertFalse(response['is_logged_in'])

   def test_login_with_inactive_user(self):
      username = 'tianyiw'
      password = '123'
      user = create_user(username, password)
      user.is_active = False
      user.save()

      post_data = {'username': username,
                   'password': password,}

      response_str = self.client.post(reverse('stvcore:login_usr'), post_data)
      response = json.loads(response_str.content)

      self.assertFalse(response['success'])
      self.assertEqual(response['ec'], utils.EC_ACCOUNT_DISABLED)

      response_str = self.client.post(reverse('stvcore:check_login'), {})
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertFalse(response['is_logged_in'])

   def test_login_with_invalid_username(self):
      post_data = {'username': 'tianyiw',
                   'password': '123',}

      response_str = self.client.post(reverse('stvcore:login_usr'), post_data)
      response = json.loads(response_str.content)

      self.assertFalse(response['success'])
      self.assertEqual(response['ec'], utils.EC_INVALID_CREDS)

      response_str = self.client.post(reverse('stvcore:check_login'), {})
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertFalse(response['is_logged_in'])

   def test_login_with_invalid_password(self):
      username = 'tianyiw'
      password = '123'
      create_user(username, password)

      post_data = {'username': username,
                   'password': '1234',}

      response_str = self.client.post(reverse('stvcore:login_usr'), post_data)
      response = json.loads(response_str.content)

      self.assertFalse(response['success'])
      self.assertEqual(response['ec'], utils.EC_INVALID_CREDS)

      response_str = self.client.post(reverse('stvcore:check_login'), {})
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertFalse(response['is_logged_in'])


class RegisterNewUserTests(TransactionTestCase):

   def test_register_two_usrs_with_different_usernames(self):
      post_data = {'username': 'tianyiw',
                   'password': '123',
                   'password_copy': '123',
                   'email': 'wang103uiuc@gmail.com',}

      response_str = self.client.post(reverse('stvcore:register_new_usr'), post_data)
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertEqual(User.objects.count(), 1)

      post_data['username'] = 'tianyi'

      response_str = self.client.post(reverse('stvcore:register_new_usr'), post_data)
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertEqual(User.objects.count(), 2)

   def test_register_two_usrs_with_same_username(self):
      post_data = {'username': 'tianyiw',
                   'password': '123',
                   'password_copy': '123',
                   'email': 'wang103uiuc@gmail.com',
                   'first_name': 'Tianyi',
                   'last_name': 'Wang',}

      response_str = self.client.post(reverse('stvcore:register_new_usr'), post_data)
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertEqual(User.objects.count(), 1)

      post_data['email'] = 'test@test.com'
      post_data['first_name'] = 'Tian'

      response_str = self.client.post(reverse('stvcore:register_new_usr'), post_data)
      response = json.loads(response_str.content)

      self.assertFalse(response['success'])
      self.assertEqual(User.objects.count(), 1)

   def test_register_one_usr(self):
      post_data = {'username': 'tianyiw',
                   'password': '123',
                   'password_copy': '123',
                   'email': 'wang103uiuc@gmail.com',
                   'first_name': 'Tianyi',
                   'last_name': 'Wang',}

      response_str = self.client.post(reverse('stvcore:register_new_usr'), post_data)
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertEqual(response['usr_detail']['username'], 'tianyiw')
      self.assertEqual(response['usr_detail']['email'], 'wang103uiuc@gmail.com')
      self.assertEqual(response['usr_detail']['first_name'], 'Tianyi')
      self.assertEqual(response['usr_detail']['last_name'], 'Wang')

   def test_register_new_usr_with_invalid_email(self):
      post_data = {'username': 'tianyiw',
                   'password': '123',
                   'password_copy': '123',
                   'email': ''}
      response_str = self.client.post(reverse('stvcore:register_new_usr'), post_data)
      response = json.loads(response_str.content)

      self.assertFalse(response['success'])
      self.assertEqual(response['ec'], utils.EC_INVALID_EMAIL)

      post_data['email'] = 'wang103uiucgmail.com'

      response_str = self.client.post(reverse('stvcore:register_new_usr'), post_data)
      response = json.loads(response_str.content)

      self.assertFalse(response['success'])
      self.assertEqual(response['ec'], utils.EC_INVALID_EMAIL)

   def test_register_new_usr_with_mismatched_passwords(self):
      post_data = {'username': 'tianyiw',
                   'password': '123',
                   'password_copy': '1234'}
      response_str = self.client.post(reverse('stvcore:register_new_usr'), post_data)
      response = json.loads(response_str.content)

      self.assertFalse(response['success'])
      self.assertEqual(response['ec'], utils.EC_PASSWORDS_MISMATCH)

   def test_register_new_usr_with_invalid_password(self):
      post_data = {'username': 'tianyiw',
                   'password': '',
                   'password_copy': ''}
      response_str = self.client.post(reverse('stvcore:register_new_usr'), post_data)
      response = json.loads(response_str.content)

      self.assertFalse(response['success'])
      self.assertEqual(response['ec'], utils.EC_INVALID_PASSWORD)

   def test_register_new_usr_with_invalid_username(self):
      post_data = {'username': '',
                   'password': '123',
                   'password_copy': '123'}
      response_str = self.client.post(reverse('stvcore:register_new_usr'), post_data)
      response = json.loads(response_str.content)

      self.assertFalse(response['success'])
      self.assertEqual(response['ec'], utils.EC_INVALID_USERNAME)


class NewUserViewTests(TestCase):

   def test_new_usr_view(self):
      response = self.client.get(reverse('stvcore:new_usr'))
      self.assertEqual(response.status_code, 200)


class SubmitNewMessageTests(TransactionTestCase):

   def test_submit_two_new_msgs_with_same_init_qr_str(self):
      username = 'tianyiw'
      create_user(username, '123')

      post_data = {'username': username,
                   'password': '123',}

      self.client.post(reverse('stvcore:login_usr'), post_data)

      msg_text = 'hello'
      post_data = {'msg_text': msg_text}

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
      username = 'tianyiw'
      create_user(username, '123')

      post_data = {'username': username,
                   'password': '123',}

      self.client.post(reverse('stvcore:login_usr'), post_data)

      msg_text = 'hello'
      post_data = {'msg_text': msg_text}

      response_str = self.client.post(reverse('stvcore:submit_new_msg'), post_data)
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertEqual(response['msg_detail']['msg_text'], msg_text)
      self.assertEqual(response['msg_detail']['creator'], username)

   def test_submit_empty_msg(self):
      username = 'tianyiw'
      create_user(username, '123')

      post_data = {'username': username,
                   'password': '123',}

      self.client.post(reverse('stvcore:login_usr'), post_data)

      post_data = {'msg_text': ''}

      response_str = self.client.post(reverse('stvcore:submit_new_msg'), post_data)
      response = json.loads(response_str.content)

      self.assertFalse(response['success'])
      self.assertEqual(response['ec'], utils.EC_EMPTY_MESSAGE)

   def test_submit_new_msg_without_login(self):
      username = 'tianyiw'
      password = '123'
      create_user(username, password)

      response_str = self.client.post(reverse('stvcore:submit_new_msg'), {})
      response = json.loads(response_str.content)

      self.assertFalse(response['success'])
      self.assertEqual(response['ec'], utils.EC_NOT_LOGGED_IN)


class NewMessageViewTests(TestCase):

   def test_new_msg_view(self):
      response = self.client.get(reverse('stvcore:new_msg'))
      self.assertEqual(response.status_code, 200)


class MessageDetailViewTests(TestCase):

   def test_msg_detail_view_with_valid_qr_str(self):
      msg_text = 'hello'
      qr_str = '000'
      username = 'tianyiw'
      user = create_user(username, '123')
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
      user = create_user(username, '123')
      msg1 = create_msg('hi', '000', user)
      msg2 = create_msg('hello', '001', user)
      
      post_data = {'username': username,
                   'password': '123',}

      self.client.post(reverse('stvcore:login_usr'), post_data)

      response_str = self.client.post(reverse('stvcore:user_msgs'), {})
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertEqual(response['msgs'][0]['qr_str'], msg2.qr_str)
      self.assertEqual(response['msgs'][1]['qr_str'], msg1.qr_str)

   def test_user_msgs_view_with_one_msg(self):
      username = 'tianyiw'
      user = create_user(username, '123')
      msg1 = create_msg('hi', '000', user)
      
      post_data = {'username': username,
                   'password': '123',}

      self.client.post(reverse('stvcore:login_usr'), post_data)

      response_str = self.client.post(reverse('stvcore:user_msgs'), {})
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertEqual(response['msgs'][0]['qr_str'], msg1.qr_str)

   def test_user_msgs_view_with_empty_msgs(self):
      username = 'tianyiw'
      password = '123'
      create_user(username, password)

      post_data = {'username': username,
                   'password': password,}

      self.client.post(reverse('stvcore:login_usr'), post_data)

      response_str = self.client.post(reverse('stvcore:user_msgs'), {})
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])

   def test_user_msgs_view_without_login(self):
      username = 'tianyiw'
      password = '123'
      create_user(username, password)

      response_str = self.client.post(reverse('stvcore:user_msgs'), {})
      response = json.loads(response_str.content)

      self.assertFalse(response['success'])
      self.assertEqual(response['ec'], utils.EC_NOT_LOGGED_IN)


class UserInfoViewTests(TestCase):

   def test_user_info_view_with_login(self):
      username = 'tianyiw'
      password = '123'
      create_user(username, password)

      post_data = {'username': username,
                   'password': password,}

      self.client.post(reverse('stvcore:login_usr'), post_data)

      response_str = self.client.post(reverse('stvcore:user_info'), {})
      response = json.loads(response_str.content)

      self.assertTrue(response['success'])
      self.assertEqual(response['user_info']['username'], username)

   def test_user_info_view_without_login(self):
      username = 'tianyiw'
      password = '123'
      create_user(username, password)

      response_str = self.client.post(reverse('stvcore:user_info'), {})
      response = json.loads(response_str.content)

      self.assertFalse(response['success'])
      self.assertEqual(response['ec'], utils.EC_NOT_LOGGED_IN)


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

