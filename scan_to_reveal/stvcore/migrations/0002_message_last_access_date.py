# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('stvcore', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='last_access_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 1, 10, 15, 56, 349474, tzinfo=utc), verbose_name=b'last access'),
            preserve_default=False,
        ),
    ]
