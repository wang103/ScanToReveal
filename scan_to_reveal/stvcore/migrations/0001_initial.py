# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('audio_file', models.FileField(upload_to=b'')),
                ('msg_text', models.CharField(max_length=256)),
                ('image_file', models.ImageField(upload_to=b'')),
                ('qr_str', models.CharField(max_length=7089, db_index=True)),
                ('create_date', models.DateTimeField(verbose_name=b'date created')),
                ('access_count', models.PositiveIntegerField(default=0)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
