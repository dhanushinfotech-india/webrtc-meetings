# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meeting_room', '0002_auto_20160817_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='description',
            field=models.TextField(help_text=b'Enter brief description of the meeting (Optional)', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='room_id',
            field=models.CharField(null=True, editable=False, max_length=200, blank=True, unique=True, db_index=True),
        ),
    ]
