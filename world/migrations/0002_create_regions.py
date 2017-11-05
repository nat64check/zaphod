import csv
import os

from django.db import migrations
# noinspection PyPep8Naming
from django_countries.fields import Country


def import_regions(apps, schema_editor):
    # Database references
    Region = apps.get_model("world", "Region")
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

            country = Country(country_line['ISO3166-1-Alpha-2'])

            if region and country not in region.countries:
                region.countries = sorted(region.countries + [country], key=lambda country: country.code)
                region.save()

            if sub_region and country not in sub_region.countries:
                sub_region.countries = sorted(sub_region.countries + [country], key=lambda country: country.code)
                sub_region.save()

            if int_region and country not in int_region.countries:
                int_region.countries = sorted(int_region.countries + [country], key=lambda country: country.code)
                int_region.save()


# noinspection PyPep8Naming
def delete_regions(apps, schema_editor):
    Region = apps.get_model("world", "Region")
    db_alias = schema_editor.connection.alias

    Region.objects.using(db_alias).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('world', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(import_regions, delete_regions)
    ]
