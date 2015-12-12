# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stvcore', '0002_message_last_access_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='audio_file',
            field=models.FileField(null=True, upload_to=b'', blank=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='image_file',
            field=models.ImageField(null=True, upload_to=b'', blank=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='last_access_date',
            field=models.DateTimeField(null=True, verbose_name=b'last access', blank=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='msg_text',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
    ]
