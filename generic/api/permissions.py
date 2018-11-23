# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
#  Copyright (c) 2018, S.J.M. Steffann. This software is licensed under the BSD
#  3-Clause License. Please see the LICENSE file in the project root directory.
# ••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••

from rest_framework.permissions import IsAuthenticated


class AllowSelf(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            # Superuser always has access
            return True

        # The rest has access to their own objects
        return obj == request.user
