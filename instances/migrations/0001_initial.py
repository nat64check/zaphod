# Generated by Django 2.0.7 on 2018-07-07 19:36

import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields
import django.core.validators
import django.db.models.deletion
import django_countries.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Marvin',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('name', models.CharField(
                    max_length=100,
                    verbose_name='name')),
                ('hostname', models.CharField(
                    max_length=127,
                    validators=[django.core.validators.RegexValidator(
                        '([a-z¡-\uffff0-9](?:[a-z¡-\uffff0-9-]{0,61}[a-z¡-\uffff0-9])?'
                        '(?:\\.(?!-)[a-z¡-\uffff0-9-]{1,63}(?<!-))*'
                        '\\.(?!-)(?:[a-z¡-\uffff-]{2,63}|xn--[a-z0-9]{1,59})(?<!-)'
                        '\\.?|localhost)',
                        message='Please provide a valid host name')],
                    verbose_name='hostname')),
                ('type', models.CharField(
                    max_length=50,
                    verbose_name='type')),
                ('version', django.contrib.postgres.fields.ArrayField(
                    base_field=models.PositiveSmallIntegerField(),
                    size=None,
                    verbose_name='version')),
                ('browser_name', models.CharField(
                    max_length=150,
                    verbose_name='browser name')),
                ('browser_version', django.contrib.postgres.fields.ArrayField(
                    base_field=models.PositiveSmallIntegerField(),
                    size=None,
                    verbose_name='browser version')),
                ('instance_type', models.CharField(
                    choices=[('v4only', 'IPv4-only'), ('v6only', 'IPv6-only'), ('nat64', 'IPv6 with NAT64')],
                    max_length=10,
                    verbose_name='instance type')),
                ('addresses', django.contrib.postgres.fields.ArrayField(
                    base_field=models.GenericIPAddressField(),
                    default=list,
                    size=None,
                    verbose_name='addresses')),
                ('first_seen', models.DateTimeField(
                    auto_now_add=True,
                    verbose_name='first seen')),
                ('last_seen', models.DateTimeField(
                    verbose_name='last seen')),
                ('alive', models.BooleanField(
                    default=True,
                    verbose_name='alive')),
            ],
            options={
                'ordering': ('trillian', 'name'),
            },
        ),
        migrations.CreateModel(
            name='Trillian',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('name', models.CharField(
                    max_length=100,
                    unique=True,
                    verbose_name='name')),
                ('hostname', models.CharField(
                    max_length=127,
                    unique=True,
                    validators=[django.core.validators.RegexValidator(
                        '([a-z¡-\uffff0-9](?:[a-z¡-\uffff0-9-]{0,61}[a-z¡-\uffff0-9])?'
                        '(?:\\.(?!-)[a-z¡-\uffff0-9-]{1,63}(?<!-))*'
                        '\\.(?!-)(?:[a-z¡-\uffff-]{2,63}|xn--[a-z0-9]{1,59})(?<!-)'
                        '\\.?|localhost)',
                        message='Please provide a valid host name')],
                    verbose_name='hostname')),
                ('first_seen', models.DateTimeField(
                    auto_now_add=True,
                    verbose_name='first seen')),
                ('last_seen', models.DateTimeField(
                    verbose_name='last seen')),
                ('alive', models.BooleanField(
                    default=True,
                    verbose_name='alive')),
                ('version', django.contrib.postgres.fields.ArrayField(
                    base_field=models.PositiveSmallIntegerField(),
                    size=None,
                    verbose_name='version')),
                ('country', django_countries.fields.CountryField(
                    db_index=True,
                    max_length=2,
                    verbose_name='country')),
                ('location', django.contrib.gis.db.models.PointField(
                    geography=True,
                    srid=4326,
                    verbose_name='location')),
                ('admins', models.ManyToManyField(
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='admins')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='marvin',
            name='trillian',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='marvins',
                to='instances.Trillian',
                verbose_name='Trillian'),
        ),
        migrations.AlterUniqueTogether(
            name='marvin',
            unique_together={('trillian', 'name')},
        ),
    ]
