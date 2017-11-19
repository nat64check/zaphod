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
            if request.user.is_anonymous:
                return obj.is_public

            return obj.owner_id == request.user.id
        else:
            if request.user.is_anonymous:
                return False

            return obj.owner_id == request.user.id


class CreatePublicBasedPermission(permissions.IsAuthenticatedOrReadOnly):
    public_methods = list(permissions.SAFE_METHODS) + ['POST']

    def has_permission(self, request, view):
        if request.user.is_superuser:
            # Superuser always has access
            return True

        # The rest has read and create access, but nothing else
        return request.method in self.public_methods

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            # Superuser always has access
            return True

        if request.method in self.public_methods:
            # Check public access
            if request.user.is_anonymous:
                # Anonymous users can only see public records
                return obj.is_public

            # The rest can see their own
            return obj.owner_id == request.user.id
        else:
            if request.user.is_anonymous:
                # Anonymous users can't write
                return False

            # The rest can only write their own
            return obj.owner_id == request.user.id
