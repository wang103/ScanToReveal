from django.conf.urls import url

from . import views


urlpatterns = [
   url(r'^usr/(?P<username>.+)/$',       views.user_info,      name='user_info'),
   url(r'^usr_msgs/(?P<username>.+)/$',  views.user_msgs,      name='user_msgs'),
   url(r'^msg/(?P<msg_qr_str>[0-9]+)/$', views.msg_detail,     name='msg_detail'),
   url(r'^new_msg/$',                    views.new_msg,        name='new_msg'),
   url(r'^submit_new_msg/$',             views.submit_new_msg, name='submit_new_msg'),
]

