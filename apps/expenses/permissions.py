from rest_framework import permissions

from .models import ExpenseGroup


class ExpenseGroupPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, expense_group: ExpenseGroup):
        if request.method in permissions.SAFE_METHODS:
            return True
        return expense_group.master_id == request.user.pk
