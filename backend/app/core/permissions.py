"""The authorization model: which role may do what.

This module is the single source of truth for permissions. It is imported by the
models, the route dependencies and the `/users/me` response, and it deliberately
imports nothing from `app` so it can be read (and tested) on its own.

Adding a role means adding a member to `Role` and one entry to `ROLE_PERMISSIONS`.
Adding a permission means adding a member to `Permission` and granting it to the
roles that should have it; admins receive every permission automatically.
"""

from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"


class Permission(StrEnum):
    USERS_READ = "users:read"  # list all users, read any user by id
    USERS_CREATE = "users:create"  # create a new user
    USERS_MANAGE = "users:manage"  # update or delete any user
    ITEMS_READ_ANY = "items:read_any"  # read or modify items owned by others
    METRICS_READ = "metrics:read"  # view the metrics dashboard
    SETTINGS_MANAGE = "settings:manage"  # operational endpoints (test email, etc.)


# Acting on your own account (reading or updating your own profile, owning your
# own items) is an identity check against the current user, not a permission, so
# it has no entry here and is available to every authenticated role.
ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.ADMIN: frozenset(Permission),
    Role.MANAGER: frozenset({Permission.USERS_READ, Permission.METRICS_READ}),
    Role.MEMBER: frozenset(),
}


def has_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS[role]


def permissions_for(role: Role) -> list[Permission]:
    return sorted(ROLE_PERMISSIONS[role])
