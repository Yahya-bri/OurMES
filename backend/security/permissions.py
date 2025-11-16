from rest_framework import permissions


class RoleBasedPermission(permissions.BasePermission):
    """Global role-based permission for OurMES.

    Rules (applies to all API endpoints unless explicitly excepted):
    - SAFE_METHODS (GET/HEAD/OPTIONS): any authenticated user in any role.
    - POST/PUT/PATCH: Planner, Supervisor, or Admin.
    - DELETE: Admin only.
    Exceptions:
    - ProductionCountingViewSet: Operators may POST (record production) as well.
    - Technology viewset changes (create/update): Supervisor or Admin only.
    """

    SAFE = permissions.SAFE_METHODS

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Everyone authenticated can read
        if request.method in self.SAFE:
            return True

        # Resolve role from user groups
        user_groups = set(user.groups.values_list('name', flat=True))
        has_any = lambda roles: bool(user_groups.intersection(set(roles)))

        view_name = getattr(view.__class__, "__name__", "")

        # Special case: allow Operators to POST production counting entries
        if view_name == 'ProductionCountingViewSet' and request.method == 'POST':
            return has_any(['Operator', 'Planner', 'Supervisor', 'Admin'])

        # Technologies modifications: Supervisor or Admin only
        if view_name in ('TechnologyViewSet', 'OperationViewSet', 'TechnologyOperationComponentViewSet') and request.method in {'POST', 'PUT', 'PATCH'}:
            return has_any(['Supervisor', 'Admin'])

        # General write permissions
        if request.method in {'POST', 'PUT', 'PATCH'}:
            return has_any(['Planner', 'Supervisor', 'Admin'])

        if request.method == 'DELETE':
            return has_any(['Admin'])

        return False

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.owner == request.user

class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to admin users.
        return request.user and request.user.is_staff

class IsAuthenticated(permissions.BasePermission):
    """
    Custom permission to only allow authenticated users to access the resource.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated