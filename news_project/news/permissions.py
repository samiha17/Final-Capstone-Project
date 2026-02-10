from rest_framework.permissions import BasePermission


# Editor Permission
class IsEditor(BasePermission):
    """
    Allows access only to users with the editor role.
    """

    def has_permission(self, request, view):
        return request.user.role == "editor"


# Journalist Permission
class IsJournalist(BasePermission):
    """
    Allows access only to users with the journalist role.
    """

    def has_permission(self, request, view):
        return request.user.role == "journalist"


# Reader Permission
class IsReader(BasePermission):
    """
    Allows access only to users with the reader role.
    """

    def has_permission(self, request, view):
        return request.user.role == "reader"
