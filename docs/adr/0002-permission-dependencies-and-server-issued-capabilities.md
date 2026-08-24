# 2. Permission dependencies, and capabilities issued by the server

Status: accepted

## Problem

Two questions, one answer. On the backend: where does an authorization check physically
live, so that a teammate can find it and adding a role does not mean auditing every route?
On the frontend: how does the UI know to hide the "Add User" button from a manager, without
growing a second copy of the rules that silently drifts from the first?

## Options

For enforcement: inline `if user.role == Role.ADMIN` at the top of each handler — obvious in
isolation, but the policy ends up scattered across route files with no single place to read
it. ASGI middleware — one chokepoint, but it has no idea which route it is in front of, so it
would re-implement path matching, and the rule stops being visible where the route is defined.
A per-route dependency naming a permission — the check sits in the decorator, immediately
above the signature, and the rules themselves live in one table.

For the frontend: hardcode the matrix in TypeScript (fast, and wrong the first time the
backend changes); derive it from the user's `role` (same duplication, one step removed); or
have the server send the permission list it already computed.

## Decision

Routes declare `dependencies=[Depends(require_permission(Permission.USERS_READ))]`.
`require_permission` is a small factory in `app/api/deps.py` that closes over a permission and
returns a dependency; the actual role-to-permission mapping lives entirely in
`ROLE_PERMISSIONS` in `app/core/permissions.py`.

`GET /users/me` returns a `UserMePublic` carrying `permissions`, the computed list for that
user's role. `useAuth()` exposes `hasPermission(...)`, and the frontend asks that and nothing
else. It never sees `ROLE_PERMISSIONS`.

## Consequences

The permission table is the only place policy is written. Changing what a manager may do is a
one-line edit that propagates to the API, the OpenAPI schema, the generated TypeScript client,
and the UI — no frontend release required, and no possibility of the two disagreeing, because
there is only one of them.

Because the check is a dependency rather than code in the handler body, it is invisible if you
read only the function. It is in the decorator directly above, and it appears in the generated
API docs, which we judged sufficient. Two routes still check inline — reading your own user,
and the item routes — because those depend on record ownership rather than role alone; both
carry a comment saying so.

The frontend guard is advisory, and deliberately so. It runs after the route mounts, which
means a user who types `/admin` directly sees the Access denied page at that URL rather than
being bounced elsewhere. Nothing is protected by hiding it: every rule is enforced again on the
server, and the UI check exists only to avoid leading someone into a dead end.

This also forced a related fix. The client previously treated `401` and `403` identically —
clearing the token and redirecting to login. Under RBAC that would log a user out every time
they touched something not meant for them, so the two are now separated: `401` ends the
session, `403` keeps it and shows the denial. For that split to be meaningful the API had to
stop returning `403` for an invalid token, which it now reports as `401`.
