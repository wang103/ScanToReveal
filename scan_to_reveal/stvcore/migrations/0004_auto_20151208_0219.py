# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import stvcore.models


class Migration(migrations.Migration):

    dependencies = [
        ('stvcore', '0003_auto_20151201_0302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='audio_file',
            field=models.FileField(null=True, upload_to=stvcore.models.cust_file_path_aud, blank=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='image_file',
            field=models.ImageField(null=True, upload_to=stvcore.models.cust_file_path_img, blank=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='qr_str',
            field=models.CharField(unique=True, max_length=255),
        ),
    ]
