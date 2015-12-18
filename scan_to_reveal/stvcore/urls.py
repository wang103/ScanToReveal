from django.conf.urls import url

from . import views


urlpatterns = [
   url(r'^login_usr/$',                  views.login_usr,        name='login_usr'),
   url(r'^logout_usr/$',                 views.logout_usr,       name='logout_usr'),
   url(r'^check_login/$',                views.check_login,      name='check_login'),
   url(r'^usr_info/$',                   views.user_info,        name='user_info'),
   url(r'^usr_msgs/$',                   views.user_msgs,        name='user_msgs'),
   url(r'^msg/(?P<msg_qr_str>[0-9]+)/$', views.msg_detail,       name='msg_detail'),
   url(r'^new_msg/$',                    views.new_msg,          name='new_msg'),
   url(r'^submit_new_msg/$',             views.submit_new_msg,   name='submit_new_msg'),
   url(r'^new_usr/$',                    views.new_usr,          name='new_usr'),
   url(r'^register_new_usr/$',           views.register_new_usr, name='register_new_usr'),
]

