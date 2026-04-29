# Todoist CRUD Skill for Hermes Agent

A Hermes agent skill that provides full CRUD operations on Todoist tasks via the **Todoist API v1**.

> ⚠️ Todoist REST v2 and Sync v9 were **deprecated on 2026-02-10** and return `410 Gone`. This skill uses **API v1 only**.

## Features

- **List** tasks with flexible filters (today, overdue, project, label, etc.)
- **Get** a single task by ID
- **Create** tasks with content, description, due date, priority, labels, and project
- **Update** tasks (any field, partial updates supported)
- **Complete** a task (mark as done)
- **Reopen** a completed task
- **Delete** a task permanently
- **List projects** to find project IDs
- **Today + Overdue** — list overdue and today's tasks in two separate sections
- **Daily Summary** — today's pending tasks + overdue reschedule prompts + tomorrow preview

## Requirements

- Python 3.7+ (stdlib only — no external packages needed)
- Todoist API key in `~/.hermes/.env`:
  ```
  TODOIST_API_KEY=your_api_key_here
  ```

## Skill Installation (Hermes Agent)

Copy this directory to your Hermes skills folder:

```bash
cp -r hermes-todoist-skill ~/.hermes/skills/openclaw-imports/todoist-crud
```

## Direct Script Usage

```bash
# List today's and overdue tasks (two sections)
python3 scripts/todoist.py today_overdue

# Daily summary: today pending + overdue reschedule + tomorrow preview
python3 scripts/todoist.py daily_summary

# List today's and overdue tasks
python3 scripts/todoist.py list --filter "today|overdue"

# Create a task
python3 scripts/todoist.py create --content "Buy milk" --due_string "today" --priority 3

# Get a specific task
python3 scripts/todoist.py get 6c3JXPfgqJv3PMhr

# Update a task
python3 scripts/todoist.py update 6c3JXPfgqJv3PMhr --due_string "tomorrow" --priority 2

# Complete a task
python3 scripts/todoist.py complete 6c3JXPfgqJv3PMhr

# Reopen a task
python3 scripts/todoist.py reopen 6c3JXPfgqJv3PMhr

# Delete a task (irreversible!)
python3 scripts/todoist.py delete 6c3JXPfgqJv3PMhr

# List all projects
python3 scripts/todoist.py projects
```

## API Reference

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List tasks | GET | `/api/v1/tasks` |
| Get task | GET | `/api/v1/tasks/{id}` |
| Create task | POST | `/api/v1/tasks` |
| Update task | POST | `/api/v1/tasks/{id}` |
| Complete task | POST | `/api/v1/tasks/{id}/close` |
| Reopen task | POST | `/api/v1/tasks/{id}/reopen` |
| Delete task | DELETE | `/api/v1/tasks/{id}` |
| List projects | GET | `/api/v1/projects` |
| Today + Overdue | GET×2 | `/api/v1/tasks` (filter=today & filter=overdue) |
| Daily Summary | GET×3 | `/api/v1/tasks` (today, overdue, tomorrow) |

## Priority Values

| Value | Display | Meaning |
|-------|---------|---------|
| `1` | 🔴 Red | Urgent (p1) |
| `2` | 🟠 Orange | High (p2) |
| `3` | 🔵 Blue | Medium (p3) |
| `4` | ⬜ None | Normal (p4, default) |

## License

MIT
