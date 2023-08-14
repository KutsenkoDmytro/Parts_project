from rest_framework import permissions
from ..models import Profile


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):

        if request.method in permissions.SAFE_METHODS:
            return True

        return bool(request.user and request.user.is_staff)


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user


class IsAdminSiteOrAdminHoldingOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):


        profile = Profile.objects.get(user=request.user)
        role = profile.role
        holding = profile.holding
        if request.method in permissions.SAFE_METHODS and str(
                role) == 'holding_admin' and obj.company.holding == holding:
            return True

        return bool(request.user and request.user.is_staff)
