

from rest_framework.permissions import BasePermission
from rest_framework import permissions


def generate_user_obj_perm_class(user_filed, safe_methods=('GET', 'HEAD', 'OPTIONS')):
    def has_object_permission(self, request, view, obj):
        return request.method in safe_methods or request.user.is_staff or getattr(obj, user_filed) == request.user
    cls = type("UserObjectPermission", (BasePermission,), {"has_object_permission": has_object_permission})
    return cls


class GlobalLevel(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff or request.method == "OPTIONS":
            return True
        perms = request.user.get_all_permission_names()
        if request.method in permissions.SAFE_METHODS:
            if "read_all" in perms:
                return True
            return False
        if "write_all" in perms:
            return True
        return False


class ViewLevel(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff or request.method == "OPTIONS":
            return True
        perms = request.user.get_all_permission_names()
        permission_name = "{}.{}".format(view.__module__, view.__class__.__name__)
        if request.method in permissions.SAFE_METHODS:
            if "read_all" in perms:
                return True
            permission_name = permission_name + ".read"
        else:
            permission_name = permission_name + ".write"
            if "write_all" in perms:
                return True
        return permission_name in perms


class IsSuperuserOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS or
                request.user and
                request.user.is_superuser
        )


class IsStaffOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS or
                request.user and
                request.user.is_staff
        )
