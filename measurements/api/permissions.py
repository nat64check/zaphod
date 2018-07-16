from rest_framework import permissions


class OwnerBasedPermission(permissions.IsAuthenticatedOrReadOnly):
    def has_permission(self, request, view):
        # Only available to authenticated users
        return not request.user.is_anonymous

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            # Superuser always has access
            return True

        # The rest has access to their own objects
        return obj.owner_id == request.user.id


class OwnerOrPublicBasedPermission(permissions.IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            # Superuser always has access
            return True

        if request.method in permissions.SAFE_METHODS:
            return (obj.owner_id == request.user.id) or obj.is_public
        else:
            return obj.owner_id == request.user.id


class InstanceRunPermission(OwnerOrPublicBasedPermission):
    def has_object_permission(self, request, view, obj):
        if request.user.has_perm('measurements.report_back'):
            return True
        else:
            return super().has_object_permission(request, view, obj)


class CreatePublicBasedPermission(permissions.IsAuthenticatedOrReadOnly):
    PUBLIC_METHODS = list(permissions.SAFE_METHODS) + ['POST']

    def has_permission(self, request, view):
        if request.user.is_superuser:
            # Superuser always has access
            return True

        # The rest has read and create access, but nothing else
        return request.method in self.PUBLIC_METHODS

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            # Superuser always has access
            return True

        if request.method in self.PUBLIC_METHODS:
            return (obj.owner_id == request.user.id) or obj.is_public
        else:
            # The rest can only write their own
            return obj.owner_id == request.user.id
