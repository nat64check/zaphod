import csv
import os

from django.core.management.base import BaseCommand
from django_countries.fields import Country

from instances.models import Region, CountryRegion


class Command(BaseCommand):
    help = 'Import region to country mapping'

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super().__init__(stdout, stderr, no_color)
        self.already_created = {}

    def create_region(self, code, name, parent=None):
        if not code or not name:
            return None

        code = int(code)
        if code not in self.already_created:
            if parent:
                level = parent.level + 1
            else:
                level = 1

            region = Region(code=code, parent=parent, level=level, name=name)
            region.save()

            if parent:
                self.stdout.write("Created {} as child of {}".format(name, parent.name))
            else:
                self.stdout.write("Created {}".format(name))

            self.already_created[code] = region

        return self.already_created[code]

    def create_country_region(self, region, country_code):
        if not region:
            return

        country = Country(country_code)
        CountryRegion.objects.get_or_create(region=region, country=country)

        self.stdout.write("Added {} to {}".format(country.name, region.name))

    def handle(self, *args, **options):
        commands_dir = os.path.dirname(__file__)
        management_dir = os.path.dirname(commands_dir)
        app_dir = os.path.dirname(management_dir)

        country_code_filename = os.path.join(app_dir, 'data', 'country-codes.csv')

        with open(country_code_filename, newline='') as csv_file:
            for country in csv.DictReader(csv_file):
                # Fix bad data
                if country['ISO3166-1-Alpha-3'] == 'NAM':
                    country['ISO3166-1-Alpha-2'] = 'NA'

                if not country['ISO3166-1-Alpha-2']:
                    continue

                region = self.create_region(country['Region Code'], country['Region Name'])
                sub_region = self.create_region(country['Sub-region Code'], country['Sub-region Name'], region)
                int_region = self.create_region(country['Intermediate Region Code'],
                                                country['Intermediate Region Name'], sub_region)

                self.create_country_region(region, country['ISO3166-1-Alpha-2'])
                self.create_country_region(sub_region, country['ISO3166-1-Alpha-2'])
                self.create_country_region(int_region, country['ISO3166-1-Alpha-2'])
