from django.contrib.admin.filters import SimpleListFilter
from django.core.exceptions import ImproperlyConfigured

from world.models import Region


class RegionFilter(SimpleListFilter):
    title = "Region"
    parameter_name = 'region'
    field_name = None

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)

        if self.field_name is None:
            raise ImproperlyConfigured(
                "The list filter '%s' does not specify "
                "a 'field_name'." % self.__class__.__name__)

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

        filter_name = '{}__in'.format(self.field_name)
        return queryset.filter(**{
            filter_name: [country.code for country in Region.objects.get(code=value).countries]
        })
