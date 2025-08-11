from rest_framework import permissions

class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Allow safe methods for everyone, but only creator can modify/delete.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, 'creator', None) == request.user
