# 1. A single role column, replacing `is_superuser`

Status: accepted

## Problem

The template shipped with one authorization primitive: `is_superuser: bool` on
`UserBase`, checked by a `get_current_active_superuser` dependency. Two states cannot
express the role we were asked to add — a `manager` who may list users but not create
them sits between "superuser" and "not". We needed a representation that supports three
roles today and more later, without a schema change per role.

## Options

**Keep `is_superuser` and add `role` alongside it.** Cheapest to land: no existing test
or route touching the boolean has to change. But it creates two sources of truth that can
disagree, and every reader then has to learn which one wins when a user is
`is_superuser=False, role=admin`. Nothing in the codebase would stop that state existing.

**A `user_role` join table.** The general answer, and necessary if a user can hold several
roles at once. It costs a table, a relationship, and a join on the hot path of every
authenticated request, to model a cardinality the requirements explicitly do not have.

**One `role` column that replaces the boolean.** A single authoritative field, migrated
with a back-fill that promotes existing superusers.

## Decision

The third. `role` is a `StrEnum` on `UserBase`, and `is_superuser` is dropped in the same
migration, which back-fills `role = 'admin' WHERE is_superuser` before removing the column.
The downgrade reverses it, so the change is not one-way.

The column is stored as `VARCHAR(20)`, not a native Postgres enum. SQLModel maps an enum
field to a native `CREATE TYPE` by default, which would mean an `ALTER TYPE ... ADD VALUE`
migration every time a role is added — precisely the per-role schema change we set out to
avoid. Forcing the type with `sa_type=Enum(Role, native_enum=False, length=20)` keeps the
Python-side enum (so the ORM still hands back a `Role`) while leaving the database column a
plain string. `values_callable` is passed because SQLAlchemy otherwise persists enum *names*
(`ADMIN`) rather than values (`admin`).

## Consequences

Adding a role is one member on the `Role` enum and one entry in `ROLE_PERMISSIONS`; no
migration, no schema change. There is exactly one field describing what a user is, so the
contradictory state is unrepresentable.

The cost was churn: roughly twenty assertions across the existing backend tests, four
frontend components, and the seeding code referenced `is_superuser` and had to be updated.
That is a one-time price for removing an ambiguity that would otherwise be permanent.

A user still holds exactly one role. If multiple roles per user is ever needed, this
becomes the join table above — but the permission checks in the routes would not change,
because they already ask about permissions rather than roles.
