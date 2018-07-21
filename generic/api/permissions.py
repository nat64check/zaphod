from rest_framework.permissions import IsAuthenticated


class AllowSelf(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            # Superuser always has access
            return True

        # The rest has access to their own objects
        return obj == request.user
