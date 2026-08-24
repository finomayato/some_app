"""Authorization tests: one case per row of the permission matrix in the README."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.core.permissions import (
    ROLE_PERMISSIONS,
    Permission,
    Role,
    has_permission,
    permissions_for,
)
from tests.utils.user import create_random_user
from tests.utils.utils import random_email, random_lower_string

# Roles that may read the user directory and the metrics page.
READ_ACCESS = [(Role.ADMIN, 200), (Role.MANAGER, 200), (Role.MEMBER, 403)]
# Roles that may change other people's accounts.
ADMIN_ONLY = [(Role.ADMIN, 200), (Role.MANAGER, 403), (Role.MEMBER, 403)]

Headers = dict[Role, dict[str, str]]


@pytest.mark.parametrize(("role", "expected"), READ_ACCESS)
def test_list_all_users(
    client: TestClient, role_headers: Headers, role: Role, expected: int
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/", headers=role_headers[role])
    assert r.status_code == expected


@pytest.mark.parametrize(("role", "expected"), ADMIN_ONLY)
def test_create_user(
    client: TestClient, role_headers: Headers, role: Role, expected: int
) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=role_headers[role],
        json={"email": random_email(), "password": random_lower_string()},
    )
    assert r.status_code == expected


@pytest.mark.parametrize(("role", "expected"), READ_ACCESS)
def test_view_metrics(
    client: TestClient, role_headers: Headers, role: Role, expected: int
) -> None:
    r = client.get(f"{settings.API_V1_STR}/metrics/", headers=role_headers[role])
    assert r.status_code == expected
    if expected == 200:
        assert r.json()["users"] >= 1


@pytest.mark.parametrize("role", list(Role))
def test_update_own_profile(
    client: TestClient, role_headers: Headers, role: Role
) -> None:
    r = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=role_headers[role],
        json={"full_name": f"Updated {role.value}"},
    )
    assert r.status_code == 200
    assert r.json()["full_name"] == f"Updated {role.value}"


@pytest.mark.parametrize(("role", "expected"), ADMIN_ONLY)
def test_update_any_profile(
    client: TestClient, db: Session, role_headers: Headers, role: Role, expected: int
) -> None:
    target = create_random_user(db)
    r = client.patch(
        f"{settings.API_V1_STR}/users/{target.id}",
        headers=role_headers[role],
        json={"full_name": "Renamed by someone else"},
    )
    assert r.status_code == expected


@pytest.mark.parametrize("role", list(Role))
def test_me_reports_the_permissions_of_the_role(
    client: TestClient, role_headers: Headers, role: Role
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=role_headers[role])
    assert r.status_code == 200
    body = r.json()
    assert body["role"] == role.value
    assert body["permissions"] == [p.value for p in permissions_for(role)]


def test_member_cannot_promote_itself(
    client: TestClient, role_headers: Headers
) -> None:
    """`UserUpdateMe` has no role field, so the extra key must be ignored."""
    r = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=role_headers[Role.MEMBER],
        json={"role": Role.ADMIN.value},
    )
    assert r.status_code == 200
    assert r.json()["role"] == Role.MEMBER.value


def test_signup_always_creates_a_member(client: TestClient) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/users/signup",
        json={
            "email": random_email(),
            "password": random_lower_string(),
            "role": Role.ADMIN.value,
        },
    )
    assert r.status_code == 200
    assert r.json()["role"] == Role.MEMBER.value


def test_unauthenticated_request_is_401(client: TestClient) -> None:
    """401, not 403 — the frontend logs out on 401 and shows Forbidden on 403."""
    r = client.get(
        f"{settings.API_V1_STR}/users/", headers={"Authorization": "Bearer nonsense"}
    )
    assert r.status_code == 401


def test_role_survives_a_database_round_trip(db: Session) -> None:
    """The role column is a plain VARCHAR, so compare with `==`, never `is`."""
    user = create_random_user(db, role=Role.ADMIN)
    db.expire(user)
    assert user.role == Role.ADMIN
    assert has_permission(user.role, Permission.USERS_MANAGE)


def test_every_role_appears_in_the_matrix() -> None:
    """Adding a role without granting it permissions should fail here, not in prod."""
    assert set(ROLE_PERMISSIONS) == set(Role)
