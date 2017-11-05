import django.contrib.gis.db.models
import django.core.validators
import django.db.models.deletion
import django_countries.fields
from django.conf import settings
from django.db import migrations, models

import zaphod.utils


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TestResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_on_trillian', models.PositiveIntegerField(blank=True, null=True)),
                ('callback_auth_code', models.CharField(default=zaphod.utils.generate_random_token, max_length=50)),
                ('requested', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('started', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('finished', models.DateTimeField(blank=True, db_index=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TestRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(db_index=True)),
                ('requested', models.DateTimeField(db_index=True)),
                ('started', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('finished', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('is_public', models.BooleanField(default=True)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                            to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TestSchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('url', models.URLField(db_index=True)),
                ('start', models.DateField()),
                ('end', models.DateField(blank=True, null=True)),
                ('time', models.TimeField()),
                ('frequency', models.CharField(choices=[('D', 'Every day'), ('W', 'Every week'), ('M', 'Every month')],
                                               max_length=1)),
                ('is_public', models.BooleanField(default=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Trillian',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('hostname', models.CharField(max_length=127, validators=[django.core.validators.RegexValidator(
                    '([a-z¡-\uffff0-9](?:[a-z¡-\uffff0-9-]{0,61}[a-z¡-\uffff0-9])?'
                    '(?:\\.(?!-)[a-z¡-\uffff0-9-]{1,63}(?<!-))*\\.(?!-)'
                    '(?:[a-z¡-\uffff-]{2,63}|xn--[a-z0-9]{1,59})(?<!-)\\.?|localhost)',
                    message='Please provide a valid host name')])),
                ('is_active', models.BooleanField(default=True)),
                ('version', models.PositiveSmallIntegerField()),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('location', django.contrib.gis.db.models.PointField(geography=True, srid=4326)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='testschedule',
            name='trillians',
            field=models.ManyToManyField(to='zaphod.Trillian'),
        ),
        migrations.AddField(
            model_name='testrun',
            name='schedule',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    to='zaphod.TestSchedule'),
        ),
        migrations.AddField(
            model_name='testresult',
            name='testrun',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='zaphod.TestRun'),
        ),
        migrations.AddField(
            model_name='testresult',
            name='trillian',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='zaphod.Trillian'),
        ),
    ]
