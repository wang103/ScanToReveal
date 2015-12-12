from django.contrib import admin

from .models import Message


class MessageAdmin(admin.ModelAdmin):
   fieldsets = [
      ('Message content', {'fields': ['audio_file', 'msg_text', 'image_file']}),
      ('QR',              {'fields': ['qr_str']}),
      ('MISC',            {'fields': ['creator', 'create_date', 'last_access_date', 'access_count']}),
   ]

   list_display = ('__unicode__', 'creator', 'create_date', 'last_access_date', 'access_count')

   list_filter = ['create_date']


admin.site.register(Message, MessageAdmin)

