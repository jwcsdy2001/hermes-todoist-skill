# Spec: Todoist Task CRUD

**API Base:** `https://api.todoist.com/api/v1`
**Auth:** `Authorization: Bearer <token>`
**Content-Type:** `application/json`

---

## GET /tasks

List tasks. Returns paginated results.

### Query Parameters

| Name | Type | Description |
|------|------|-------------|
| `filter` | string | Todoist filter expression (e.g. `today\|overdue`, `#ProjectName`, `@label`, `p1`) |
| `project_id` | string | Filter by project ID |
| `section_id` | string | Filter by section ID |
| `label` | string | Filter by label name |
| `limit` | integer | Max results per page (default: 50, max: 200) |
| `cursor` | string | Pagination cursor from previous response |

### Response 200

```json
{
  "results": [
    {
      "id": "6c3JXPfgqJv3PMhr",
      "user_id": "4726327",
      "project_id": "6Xv52MrfH2825G9r",
      "section_id": null,
      "parent_id": null,
      "content": "Task title",
      "description": "Optional description (Markdown)",
      "checked": false,
      "is_deleted": false,
      "priority": 4,
      "due": {
        "date": "2026-04-30",
        "string": "Apr 30",
        "is_recurring": false,
        "timezone": null
      },
      "labels": ["label1"],
      "added_at": "2026-04-01T10:00:00Z",
      "updated_at": "2026-04-01T10:00:00Z",
      "completed_at": null
    }
  ],
  "next_cursor": null
}
```

---

## GET /tasks/{task_id}

Get a single task by ID.

### Path Parameters

| Name | Type | Description |
|------|------|-------------|
| `task_id` | string | Task ID (base32-encoded, not `tmp-` prefix) |

### Response 200

Full task object (same schema as list item above).

### Response 404

Task not found or deleted.

---

## POST /tasks

Create a new task.

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content` | string | ✅ | Task title |
| `description` | string | | Markdown description |
| `project_id` | string | | Target project (defaults to Inbox) |
| `section_id` | string | | Section within project |
| `parent_id` | string | | Parent task ID (creates sub-task) |
| `due_string` | string | | Natural language due date (e.g. `"tomorrow"`, `"next Monday"`) |
| `due_date` | string | | Fixed date `YYYY-MM-DD` (mutually exclusive with `due_string`) |
| `due_datetime` | string | | Fixed datetime in RFC3339 (mutually exclusive with `due_string`) |
| `priority` | integer | | 1=urgent 2=high 3=medium 4=normal (default: 4) |
| `labels` | array[string] | | Label names |
| `order` | integer | | Manual sort order |

### Response 200

Full task object of the created task.

---

## POST /tasks/{task_id}

Update an existing task. Only send fields to change.

### Path Parameters

| Name | Type | Description |
|------|------|-------------|
| `task_id` | string | Task ID |

### Request Body (all optional)

| Field | Type | Description |
|-------|------|-------------|
| `content` | string | New title |
| `description` | string | New description |
| `due_string` | string | New natural language due date |
| `due_date` | string | New fixed date `YYYY-MM-DD` |
| `due_datetime` | string | New fixed datetime RFC3339 |
| `priority` | integer | New priority (1–4) |
| `labels` | array[string] | New labels (replaces existing) |

### Response 200

Updated full task object.

---

## POST /tasks/{task_id}/close

Mark task as complete.

### Response 204

Empty body. Script returns `{"success": true}`.

---

## POST /tasks/{task_id}/reopen

Reopen a completed task.

### Response 204

Empty body. Script returns `{"success": true}`.

---

## DELETE /tasks/{task_id}

Permanently delete a task. **Irreversible.**

### Response 204

Empty body. Script returns `{"success": true}`.

---

## GET /projects

List all projects.

### Response 200

```json
{
  "results": [
    {
      "id": "6Xv52MrfH2825G9r",
      "name": "Inbox",
      "color": "charcoal",
      "is_favorite": false,
      "inbox_project": true,
      "parent_id": null,
      "is_archived": false,
      "is_deleted": false,
      "created_at": "2025-05-01T00:00:00Z",
      "updated_at": "2025-05-01T00:00:00Z"
    }
  ],
  "next_cursor": null
}
```

---

## Script Command: today_overdue

Calls `GET /tasks` twice (`filter=overdue` + `filter=today`) and merges results into separate sections.

### Response (script JSON output)

```json
{
  "date": "2026-04-29",
  "summary": {
    "overdue_count": 2,
    "today_count": 3,
    "total": 5
  },
  "overdue": [ ...task objects... ],
  "today":   [ ...task objects... ]
}
```

---

## Script Command: daily_summary

Calls `GET /tasks` three times (`filter=overdue`, `filter=today`, `filter=tomorrow`) and assembles a full daily report with reschedule prompts.

### Response (script JSON output)

```json
{
  "report_date": "2026-04-29",
  "tomorrow_date": "2026-04-30",
  "today_execution": {
    "pending_count": 3,
    "tasks": [ ...task objects... ]
  },
  "overdue": {
    "count": 2,
    "tasks": [ ...task objects... ],
    "reschedule_items": [
      {
        "id": "abc123",
        "content": "Task title",
        "due": { "date": "2026-04-27" },
        "priority": 2,
        "labels": [],
        "reschedule_prompt": "任務「Task title」已過期（原到期：2026-04-27），請問要改期、完成還是刪除？"
      }
    ],
    "agent_instruction": "以下任務已逾期，請逐一向使用者確認：要改期（提供新日期）、標記完成，還是刪除？"
  },
  "tomorrow_preview": {
    "count": 2,
    "tasks": [ ...task objects... ]
  }
}
```

`agent_instruction` is `null` when there are no overdue tasks.

---

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad request / invalid parameters |
| 401 | Unauthorized — invalid or missing API key |
| 403 | Forbidden — no permission |
| 404 | Resource not found |
| 410 | Gone — deprecated endpoint (REST v2 / Sync v9) |
| 429 | Rate limited — retry after delay |
| 500 | Server error |
