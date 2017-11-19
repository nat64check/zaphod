from rest_framework import permissions


class OwnerBasedPermission(permissions.IsAuthenticatedOrReadOnly):
    def has_permission(self, request, view):
        return not request.user.is_anonymous

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if request.user.is_anonymous:
            return False

        return obj.owner_id == request.user.id


class OwnerOrPublicBasedPermission(permissions.IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            if request.user.is_anonymous:
                return obj.is_public

            return obj.owner_id == request.user.id
        else:
            if request.user.is_anonymous:
                return False

            return obj.owner_id == request.user.id
