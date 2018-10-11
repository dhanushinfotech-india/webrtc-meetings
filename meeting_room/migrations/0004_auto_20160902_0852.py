# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meeting_room', '0003_auto_20160901_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='description',
            field=models.TextField(default=b'', help_text=b'Enter brief description of the meeting (Optional)', null=True, blank=True),
        ),
    ]
