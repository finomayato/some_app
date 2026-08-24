# Goal
Add role-based access control (RBAC) to the existing Full-Stack FastAPI Template so that only authorized users can access sensitive endpoints and UI sections.

We prioritize clean, maintainable code over comprehensive test coverage or extensive documentation.

You may reuse any libraries already in the template.

Note: RBAC can be implemented with simple role checks or a small policy layer. Keep scope tight. Favor clarity over cleverness.


## Implement the Following Roles
Role	Permissions
admin	Full access to user management and settings
manager	Can list users and view metrics, but not change global settings
member	Can only access their own profile and basic app features


## Protect a Small but Realistic Surface
List users
Create user
View "metrics/insights" page (simple stub is acceptable)
View and update own profile
Exact permission mapping is up to you.

State it clearly in your docs and enforce it consistently in the backend and frontend.


## Example Permission Matrix (Document Something Similar)
Action	admin	manager	member
List all users	✓	✓	✗
Create user	✓	✗	✗
View metrics	✓	✓	✗
Update own profile	✓	✓	✓
Update any profile	✓	✗	✗


## Code Quality Expectations
We prioritize maintainable, readable code over clever solutions.

Clear naming: Function/variable names that explain intent without comments
Single responsibility: Small, focused functions
Easy to extend: Adding a new role shouldn't require touching 10+ files
Self-documenting: Code structure makes the authorization model obvious


Architecture & Documentation
Document your implementation approach clearly but concisely.

## Required
 Permission matrix in README showing which role can access what
 Brief explanation (2-4 paragraphs) of your authorization approach:
Where authorization checks live (middleware, dependencies, decorators?)
How roles are stored and validated
How frontend learns about user capabilities
 Inline code comments only for non-obvious authorization logic
Optional (Bonus Points)
 1-2 Architecture Decision Records (ADRs) for your most critical decisions
Use any simple ADR format (problem, options, decision, trade-offs)
200-400 words each
Example topics: Why you chose your authorization pattern, where checks live, how the frontend handles permissions
 Simple diagram showing where auth/authz checks happen
Mermaid, C4-style, or hand-drawn PNG is fine


## Non-Functional Requirements
Demonstrate you considered real-world constraints:

1. Maintainability (Critical)
Keep coupling low; use consistent patterns
A teammate should understand your authorization logic in 5 minutes
2. Testability (Important)
Provide focused backend tests covering critical authorization paths


## UX Behavior
The UI should:
Hide navigation links/buttons that the user can't access
Show a friendly "Forbidden" or "Access Denied" message if navigating directly to unauthorized routes
Not just fail silently or show cryptic errors

## Developer UX
Update the README with:

How to run locally (setup, dependencies, database)
How to seed test data with at least one admin and one non-admin user
How to run tests
Database migrations for any schema changes (if applicable)
Make it easy for us to run your solution without hunting for setup instructions.


