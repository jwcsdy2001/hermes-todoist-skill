# Todoist CRUD Skill — OpenSpec Project Overview

## Purpose

Hermes agent skill enabling full CRUD management of Todoist tasks via Todoist API v1.

## API Base URL

```
https://api.todoist.com/api/v1
```

> Note: REST v2 (`/rest/v2/`) and Sync v9 (`/sync/v9/`) were deprecated 2026-02-10 and return 410.

## Authentication

Bearer token from `~/.hermes/.env` → `TODOIST_API_KEY`.

```
Authorization: Bearer <TODOIST_API_KEY>
```

## Capabilities

| Capability | File |
|------------|------|
| Todoist Task CRUD | `specs/todoist-crud/spec.md` |
| Today + Overdue Listing | `specs/todoist-crud/spec.md` (Command: today_overdue) |
| Daily Summary & Tomorrow Preview | `specs/todoist-crud/spec.md` (Command: daily_summary) |

## Components

- `SKILL.md` — Hermes agent instruction file
- `scripts/todoist.py` — CLI helper (Python 3, stdlib only)
- `openspec/` — API specification docs
