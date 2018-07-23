import collections
import copy

from rest_framework.fields import JSONField
from rest_framework_serializer_extensions.serializers import EXPAND_DELIMITER


class SerializerExtensionsJSONField(JSONField):
    @staticmethod
    def _clean_up_filters(exclude, only):
        my_exclude = [item for item in exclude if item]
        if only:
            my_only = [item for item in only if item] or None
        else:
            my_only = None

        return my_exclude, my_only

    def _selective_copy(self, source, exclude, only):
        if isinstance(source, collections.Mapping):
            # Here we filter on keys
            out = {}
            for key, value in source.items():
                my_exclude = [item[1:] for item in exclude if item[0] == key]
                my_only = [item[1:] for item in only if item[0] == key] if only else None

                # If there is an only spec then apply it
                if my_only is not None and len(my_only) == 0:
                    # This key wasn't listed
                    continue

                # If there is no further exclude spec then exclude the whole
                exclude_whole = any([len(subkeys) == 0 for subkeys in my_exclude])
                if exclude_whole:
                    continue

                # Clean up filters and recurse
                my_exclude, my_only = self._clean_up_filters(my_exclude, my_only)
                out[key] = self._selective_copy(value, my_exclude, my_only)

        elif isinstance(source, collections.Iterable) and not isinstance(source, (str, bytes)):
            # We filter on keys: pass filter down to item level
            out = [self._selective_copy(item, exclude, only) for item in source]

        else:
            # Just make a deep copy
            out = copy.deepcopy(source)

        return out

    def to_representation(self, value):
        try:
            exclude_set = self.context['exclude']
        except KeyError:
            exclude_set = set()

        exclude_components = [item.split(EXPAND_DELIMITER) for item in exclude_set]
        my_exclude = [item[1:] for item in exclude_components if item[0] == self.field_name]

        try:
            only_set = self.context['only']
        except KeyError:
            only_set = None

        only_components = [item.split(EXPAND_DELIMITER) for item in only_set]
        my_only = [item[1:] for item in only_components if item[0] == self.field_name] if only_set else None

        my_exclude, my_only = self._clean_up_filters(my_exclude, my_only)
        if my_exclude or my_only:
            # Don't mess with the original
            value = self._selective_copy(value, my_exclude, my_only)

        return super().to_representation(value)
