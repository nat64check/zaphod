# Generated by Django 2.0b1 on 2017-10-29 20:39

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CountryRegion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', django_countries.fields.CountryField(max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('code', models.PositiveIntegerField(primary_key=True, serialize=False)),
                ('level', models.PositiveSmallIntegerField()),
                ('name', models.CharField(max_length=100)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='instances.Region')),
            ],
            options={
                'ordering': ('parent__name', 'name'),
            },
        ),
        migrations.CreateModel(
            name='Trillian',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('location', django.contrib.gis.db.models.fields.PointField(geography=True, srid=4326)),
            ],
        ),
        migrations.AddField(
            model_name='countryregion',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='instances.Region'),
        ),
    ]