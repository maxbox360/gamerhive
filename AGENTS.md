# GamerHive — AI Coding Agent Instructions

## Project Overview

GamerHive is a "Letterboxd for video games": a social game discovery and tracking application where users can discover games, maintain a personal library, track their playing status, rate games, write reviews, and eventually interact socially with other users.

### Current Stack

* Backend: Django 5
* API: Django Ninja
* Frontend: Next.js 15
* Frontend language: TypeScript
* UI: Elastic UI (EUI)
* Database: PostgreSQL
* Cache/services: Redis
* External game metadata: IGDB
* Development environment: Docker Compose

Preserve the existing architecture and conventions unless there is a strong technical reason to change them.

---

# Development Environment

## Docker Is the Source of Truth

The GamerHive backend runs inside Docker Compose.

Do NOT use a local Python virtual environment (`venv`) to run Django commands, tests, migrations, or other backend tooling.

Before running backend commands:

1. Inspect the Docker Compose configuration if the service name is unknown.
2. Run Django commands inside the appropriate container.

Examples:

```bash
docker compose exec <django-service> python manage.py check
docker compose exec <django-service> python manage.py test
docker compose exec <django-service> python manage.py makemigrations
docker compose exec <django-service> python manage.py migrate
```

Do not install Python dependencies into the host environment unless explicitly requested.

The Docker environment used by the project should be treated as the authoritative development environment.

Never run `npm run build` while the frontend `next dev` server is running against the same `.next` directory. Stop the dev server/container before running a production build, or use isolated build output.

---

# General Development Principles

## Understand Before Changing

Before modifying code:

1. Inspect the relevant existing implementation.
2. Determine whether the requested functionality already partially exists.
3. Identify existing utilities, components, models, routers, hooks, and conventions that should be reused.
4. Avoid creating duplicate infrastructure.

For substantial changes, briefly describe the intended implementation approach before making changes.

## Keep Changes Focused

Implement only the scope of the requested Jira card or task.

Do NOT:

* Implement future Jira cards "while you're here."
* Refactor unrelated code.
* Replace existing architecture without a clear reason.
* Introduce duplicate abstractions.
* Rewrite working code unnecessarily.
* Modify unrelated files merely for stylistic consistency.

If additional changes are genuinely required, explain why they are necessary.

The goal is small, reviewable, incremental changes.

---

# Backend Guidelines

## Django

Prefer Django's built-in functionality over custom implementations when appropriate.

Reuse existing:

* Models
* Managers
* Forms/validation
* Authentication
* Permissions
* Middleware
* Utilities
* Settings conventions

Do not introduce a second framework or architectural pattern when the existing Django architecture can support the requirement.

## Django Authentication

GamerHive uses Django's built-in authentication and session system.

Do NOT introduce JWT authentication unless explicitly requested.

Use Django's:

* `django.contrib.auth`
* Sessions
* Authentication middleware
* Password hashing
* Permission/authentication mechanisms

Never store plaintext passwords or implement custom password hashing.

Do not disable CSRF protection as a shortcut.

## Django Ninja APIs

Follow the existing router and schema organization.

Django Ninja/Pydantic API request and response schemas should live in a dedicated `schemas.py` file within their respective router/package directory.

`router.py` should contain endpoint/routing logic rather than schema definitions.

Keep schemas associated with their domain/router package rather than creating one global schema module.

Reuse existing schemas when appropriate rather than creating duplicate definitions.

When adding a new API schema, add it to the appropriate `schemas.py`.

When modifying an existing schema, inspect and update the existing `schemas.py` rather than defining a duplicate schema in a router.

Preserve existing API contracts unless the Jira card explicitly calls for a contract change.

API endpoints should:

* Validate input.
* Return appropriate HTTP status codes.
* Use existing authentication mechanisms.
* Avoid exposing internal/sensitive model fields.
* Follow existing response/schema conventions.

Do not create a second API abstraction when the existing Django Ninja architecture can support the requirement.

## Database Changes

When changing Django models:

* Create the appropriate Django migration.
* Include the migration with the change.
* Do not manually alter previously applied migrations unless explicitly instructed.
* Prefer database constraints for data integrity where appropriate.

---

# Frontend Guidelines

Follow the existing Next.js application structure and conventions.

Reuse existing:

* Components
* Hooks
* API/fetch utilities
* TypeScript types
* Elastic UI components
* Loading states
* Error handling patterns

Do not introduce a new API client, state-management library, component library, or architectural pattern unless the existing implementation cannot reasonably support the requirement.

Maintain strict TypeScript correctness.

---

# Authentication & Security

Security is a requirement, not an optional enhancement.

Always:

* Use Django's password hashing.
* Protect authenticated endpoints server-side.
* Respect CSRF protection.
* Use secure cookie configuration appropriate to the environment.
* Validate user input.
* Avoid exposing sensitive information.
* Keep secrets and API keys out of source control.
* Avoid logging passwords, tokens, credentials, or other sensitive data.
* Do not read, print, or inspect values from `.env` files unless explicitly requested by the user for that task.

Never disable a security mechanism simply to make development easier without explicitly documenting why and receiving approval.

---

# Testing

Code changes should include or update appropriate tests whenever practical.

## Backend

Backend tests must be run inside the Docker container.

Do not report local `venv` test results as representative of the GamerHive backend environment.

## Reporting Test Results

Never claim that tests passed unless they were actually run.

Clearly distinguish:

* Passed
* Failed
* Blocked
* Not run

If a pre-existing environment/tooling problem prevents testing, report it separately from problems introduced by the current change.

Do not modify tests simply to make them pass unless the existing test is demonstrably incorrect.

## Frontend

Run the appropriate existing TypeScript, lint, build, or test commands for frontend changes.

If an existing tooling problem prevents a check from running, report it rather than silently working around it.

---

# Dependencies

Do not add new dependencies unless they are genuinely necessary.

Before adding a dependency:

1. Check whether an existing dependency already provides the required functionality.
2. Prefer built-in Django/Next.js functionality when appropriate.
3. Explain why the new dependency is necessary.
4. Follow the project's existing package-management workflow.

Avoid adding dependencies for trivial functionality.

---

# Pull Requests and Summaries

When preparing a PR summary for GitHub, keep it concise and copy-paste ready.

Use a short two-sentence high-level overview followed by a small bullet list with a maximum of five items.

Each bullet should be a single sentence describing a discrete change or validation result.

Do not include long explanations, nested bullets, or markdown tables.

Keep the wording concise and suitable for direct GitHub paste.

---

# Git & File Safety

Do not:

* Reset or revert unrelated user changes.
* Delete unrelated files.
* Rewrite unrelated code.
* Overwrite user work without warning.
* Commit directly to `main`; always work on a feature/fix branch and merge through a pull request.
* Merge or push to `main` unless explicitly instructed by the user.
* Commit secrets or credentials.
* Create git commits unless explicitly requested.

Keep changes reviewable and narrowly scoped.

---

# Documentation

Update relevant documentation when a change affects:

* Development setup
* Environment variables
* API behavior
* Authentication
* Database setup
* Deployment
* User-facing development workflows

Do not create documentation for trivial internal changes unless it provides meaningful value.

---

# Jira Task Discipline

GamerHive development is organized into Jira epics and small implementation cards.

Treat each Jira card as an independently reviewable unit of work.

For each task:

1. Understand the card's intended scope.
2. Inspect existing implementation.
3. Implement only that card.
4. Add/update appropriate tests.
5. Run relevant validation.
6. Report any blockers or follow-up work.

Do not silently implement requirements belonging to later Jira cards.

If a task exposes a necessary follow-up, identify it in the summary rather than automatically implementing it.

---

# Pull Request Summaries

PR summaries must always be written in Markdown.

PR summaries should include:

## Summary

What changed and why.

## Changes

A concise list of the important implementation changes.

## Testing

List checks/tests that were actually run and their results.

## Known Issues / Blockers

Document pre-existing failures, environment problems, or incomplete validation.

## Follow-up

Mention relevant work that belongs to future Jira cards rather than the current change.

Do not claim functionality was tested if it was not actually tested.

---

# Avoid Overengineering

Prefer the simplest implementation that correctly satisfies the current requirement.

GamerHive is being developed incrementally toward an MVP.

Do not prematurely implement:

* Social features
* Recommendation systems
* Advanced notification systems
* Complex caching
* Microservices
* Event-driven architecture
* Additional authentication systems
* Unnecessary abstractions

Build the current requirement well and leave future complexity for when it is actually needed.

---

# When Unsure

If the existing architecture does not clearly support the requested implementation:

1. Inspect more of the relevant code.
2. Identify the smallest change that fits the current architecture.
3. Explain important assumptions.
4. Avoid making a large architectural decision silently.

When multiple reasonable approaches exist, prefer the one that is:

1. Consistent with existing GamerHive code
2. Simplest to maintain
3. Secure
4. Easy to test
5. Appropriate for the current MVP
