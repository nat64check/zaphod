from django.contrib.admin.filters import SimpleListFilter

from instances.models import Region, CountryRegion


class RegionFilter(SimpleListFilter):
    title = "Region"
    parameter_name = 'region'

    def lookups(self, request, model_admin):
        regions = []
        for region in Region.objects.filter(level=1):
            regions.append((region.code, region.name))

            for subregion in Region.objects.filter(level=2, parent=region):
                regions.append((subregion.code, '- ' + subregion.name))

        return regions

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset

        return queryset.filter(
            country__in=CountryRegion.objects.filter(region_id=value).values_list('country', flat=True))
