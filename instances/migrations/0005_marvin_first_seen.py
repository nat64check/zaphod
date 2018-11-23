# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD
#  3-Clause License. Please see the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

# Generated by Django 2.0.7 on 2018-07-15 15:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('instances', '0004_rename_trillian_alive'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marvin',
            name='first_seen',
            field=models.DateTimeField(verbose_name='first seen'),
        ),
        migrations.AlterField(
            model_name='trillian',
            name='is_alive',
            field=models.BooleanField(default=True, verbose_name='is alive'),
        ),
    ]
