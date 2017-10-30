import csv
import os

from django.db import migrations
from django_countries.fields import Country


# noinspection PyPep8Naming
def import_country_regions(apps, schema_editor):
    # Database references
    Region = apps.get_model("instances", "Region")
    CountryRegion = apps.get_model("instances", "CountryRegion")
    db_alias = schema_editor.connection.alias

    # Where is data stored
    app_dir = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(app_dir, 'data')

    # Internal book keeping to prevent recreating the same regions over and over
    already_created = {}

    def create_region(code, name, parent=None):
        if not code or not name:
            return None

        code = int(code)
        if code not in already_created:
            if parent:
                level = parent.level + 1
            else:
                level = 1

            new_region = Region(code=code, parent=parent, level=level, name=name)
            new_region.save(using=db_alias)

            already_created[code] = new_region

        return already_created[code]

    def create_country_region(containing_region, country_code):
        if not containing_region:
            return

        country = Country(country_code)
        CountryRegion.objects.using(db_alias).get_or_create(region=containing_region, country=country)

    country_code_filename = os.path.join(data_dir, 'country-codes-20171030.csv')

    with open(country_code_filename, newline='') as csv_file:
        for country_line in csv.DictReader(csv_file):
            # Fix bad data
            if country_line['ISO3166-1-Alpha-3'] == 'NAM':
                country_line['ISO3166-1-Alpha-2'] = 'NA'

            if not country_line['ISO3166-1-Alpha-2']:
                continue

            region = create_region(country_line['Region Code'], country_line['Region Name'])
            sub_region = create_region(country_line['Sub-region Code'], country_line['Sub-region Name'], region)
            int_region = create_region(country_line['Intermediate Region Code'],
                                       country_line['Intermediate Region Name'], sub_region)

            create_country_region(region, country_line['ISO3166-1-Alpha-2'])
            create_country_region(sub_region, country_line['ISO3166-1-Alpha-2'])
            create_country_region(int_region, country_line['ISO3166-1-Alpha-2'])


# noinspection PyPep8Naming
def delete_country_regions(apps, schema_editor):
    Region = apps.get_model("instances", "Region")
    CountryRegion = apps.get_model("instances", "CountryRegion")
    db_alias = schema_editor.connection.alias

    CountryRegion.objects.using(db_alias).delete()
    Region.objects.using(db_alias).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('instances', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(import_country_regions, delete_country_regions)
    ]
