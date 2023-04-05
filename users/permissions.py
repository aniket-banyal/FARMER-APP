from rest_framework import permissions
from .models import *


class IsAuthenticated(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_permission(self, request, view):

        if request.user.is_authenticated:
            return True
        return False


class IsFarmer(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role == 7:
            return True
        else:
            return False


class IsIndustry(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.role == 8:
            return True
        else:
            return False
