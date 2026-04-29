#!/usr/bin/env python3
"""
Todoist API v1 CRUD helper script for Hermes Agent Skill.

Usage:
  python3 todoist.py list [--filter FILTER] [--project_id ID] [--limit N]
  python3 todoist.py get <task_id>
  python3 todoist.py create --content TEXT [--description TEXT] [--project_id ID]
                            [--due_string TEXT] [--due_date YYYY-MM-DD]
                            [--priority 1-4] [--labels LABEL1,LABEL2]
                            [--parent_id ID] [--section_id ID]
  python3 todoist.py update <task_id> [--content TEXT] [--description TEXT]
                            [--due_string TEXT] [--due_date YYYY-MM-DD]
                            [--priority 1-4] [--labels LABEL1,LABEL2]
  python3 todoist.py complete <task_id>
  python3 todoist.py reopen <task_id>
  python3 todoist.py delete <task_id>
  python3 todoist.py projects

API Key is read from ~/.hermes/.env (TODOIST_API_KEY=...).
All output is JSON (stdout). Errors go to stderr with non-zero exit code.

API Base: https://api.todoist.com/api/v1
Ref: https://developer.todoist.com/api/v1/
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta


API_BASE = "https://api.todoist.com/api/v1"
ENV_PATH = os.path.expanduser("~/.hermes/.env")


def load_api_key() -> str:
    if not os.path.exists(ENV_PATH):
        raise RuntimeError(f"ENV file not found: {ENV_PATH}")
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line.startswith("TODOIST_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                if key:
                    return key
    raise RuntimeError("TODOIST_API_KEY not found in ~/.hermes/.env")


def make_request(method: str, path: str, api_key: str, data: dict = None, params: dict = None) -> dict:
    url = f"{API_BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw.strip() else {"success": True}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        try:
            err_json = json.loads(err_body)
        except Exception:
            err_json = {"error": err_body}
        print(json.dumps({"http_error": e.code, "detail": err_json}), file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


def cmd_list(api_key: str, args) -> None:
    params = {}
    if args.filter:
        params["filter"] = args.filter
    if args.project_id:
        params["project_id"] = args.project_id
    if args.limit:
        params["limit"] = args.limit

    result = make_request("GET", "/tasks", api_key, params=params)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_get(api_key: str, args) -> None:
    result = make_request("GET", f"/tasks/{args.task_id}", api_key)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_create(api_key: str, args) -> None:
    data = {"content": args.content}
    if args.description:
        data["description"] = args.description
    if args.project_id:
        data["project_id"] = args.project_id
    if args.due_string:
        data["due_string"] = args.due_string
    if args.due_date:
        data["due_date"] = args.due_date
    if args.priority:
        data["priority"] = args.priority
    if args.labels:
        data["labels"] = [l.strip() for l in args.labels.split(",") if l.strip()]
    if args.parent_id:
        data["parent_id"] = args.parent_id
    if args.section_id:
        data["section_id"] = args.section_id

    result = make_request("POST", "/tasks", api_key, data=data)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_update(api_key: str, args) -> None:
    data = {}
    if args.content:
        data["content"] = args.content
    if args.description is not None:
        data["description"] = args.description
    if args.due_string:
        data["due_string"] = args.due_string
    if args.due_date:
        data["due_date"] = args.due_date
    if args.priority:
        data["priority"] = args.priority
    if args.labels is not None:
        data["labels"] = [l.strip() for l in args.labels.split(",") if l.strip()]

    if not data:
        print(json.dumps({"error": "No fields to update provided"}), file=sys.stderr)
        sys.exit(1)

    result = make_request("POST", f"/tasks/{args.task_id}", api_key, data=data)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_complete(api_key: str, args) -> None:
    result = make_request("POST", f"/tasks/{args.task_id}/close", api_key)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_reopen(api_key: str, args) -> None:
    result = make_request("POST", f"/tasks/{args.task_id}/reopen", api_key)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_delete(api_key: str, args) -> None:
    result = make_request("DELETE", f"/tasks/{args.task_id}", api_key)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_projects(api_key: str, args) -> None:
    result = make_request("GET", "/projects", api_key)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def _extract_tasks(result) -> list:
    """Safely extract task list from API response (handles both list and dict with 'results' key)."""
    if isinstance(result, list):
        return result
    return result.get("results", [])


def _filter_has_due(tasks: list) -> list:
    """Remove tasks where due is null — Todoist API quirk: 'overdue' filter includes no-due tasks."""
    return [t for t in tasks if t.get("due") is not None]


def _due_date(task: dict) -> str:
    """Safely get due date string from a task, returns '未知' if missing."""
    due = task.get("due")
    if due and isinstance(due, dict):
        return due.get("date", "未知")
    return "未知"


def cmd_today_overdue(api_key: str, args) -> None:
    """List overdue and today's tasks in separate sections."""
    today_str = date.today().isoformat()

    overdue_result = make_request("GET", "/tasks", api_key, params={"filter": "overdue"})
    today_result = make_request("GET", "/tasks", api_key, params={"filter": "today"})

    overdue_tasks = _filter_has_due(_extract_tasks(overdue_result))
    today_tasks = _filter_has_due(_extract_tasks(today_result))

    output = {
        "date": today_str,
        "summary": {
            "overdue_count": len(overdue_tasks),
            "today_count": len(today_tasks),
            "total": len(overdue_tasks) + len(today_tasks),
        },
        "overdue": overdue_tasks,
        "today": today_tasks,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_daily_summary(api_key: str, args) -> None:
    """Daily execution summary: today pending + overdue reschedule prompts + tomorrow preview."""
    today = date.today()
    tomorrow = today + timedelta(days=1)

    overdue_result = make_request("GET", "/tasks", api_key, params={"filter": "overdue"})
    today_result = make_request("GET", "/tasks", api_key, params={"filter": "today"})
    tomorrow_result = make_request("GET", "/tasks", api_key, params={"filter": "tomorrow"})

    overdue_tasks = _filter_has_due(_extract_tasks(overdue_result))
    today_tasks = _filter_has_due(_extract_tasks(today_result))
    tomorrow_tasks = _filter_has_due(_extract_tasks(tomorrow_result))

    reschedule_items = [
        {
            "id": t.get("id"),
            "content": t.get("content"),
            "due": t.get("due"),
            "priority": t.get("priority"),
            "labels": t.get("labels", []),
            "reschedule_prompt": f"任務「{t.get('content')}」已過期（原到期：{_due_date(t)}），請問要改期、完成還是刪除？",
        }
        for t in overdue_tasks
    ]

    output = {
        "report_date": today.isoformat(),
        "tomorrow_date": tomorrow.isoformat(),
        "today_execution": {
            "pending_count": len(today_tasks),
            "tasks": today_tasks,
        },
        "overdue": {
            "count": len(overdue_tasks),
            "tasks": overdue_tasks,
            "reschedule_items": reschedule_items,
            "agent_instruction": (
                "以下任務已逾期，請逐一向使用者確認：要改期（提供新日期）、標記完成，還是刪除？"
                if overdue_tasks else None
            ),
        },
        "tomorrow_preview": {
            "count": len(tomorrow_tasks),
            "tasks": tomorrow_tasks,
        },
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Todoist API v1 CRUD helper for Hermes Agent"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p_list = sub.add_parser("list", help="List tasks")
    p_list.add_argument("--filter", help="Todoist filter string (e.g. 'today|overdue')")
    p_list.add_argument("--project_id", help="Filter by project ID")
    p_list.add_argument("--limit", type=int, help="Max number of results")

    # get
    p_get = sub.add_parser("get", help="Get a single task")
    p_get.add_argument("task_id", help="Task ID")

    # create
    p_create = sub.add_parser("create", help="Create a new task")
    p_create.add_argument("--content", required=True, help="Task title/content")
    p_create.add_argument("--description", help="Task description (markdown)")
    p_create.add_argument("--project_id", help="Project ID (defaults to Inbox)")
    p_create.add_argument("--due_string", help="Natural language due date (e.g. 'tomorrow', 'next Monday')")
    p_create.add_argument("--due_date", help="Due date in YYYY-MM-DD format")
    p_create.add_argument("--priority", type=int, choices=[1, 2, 3, 4],
                          help="Priority: 1=urgent/red, 2=high/orange, 3=medium/blue, 4=normal/none")
    p_create.add_argument("--labels", help="Comma-separated label names")
    p_create.add_argument("--parent_id", help="Parent task ID (for sub-tasks)")
    p_create.add_argument("--section_id", help="Section ID within the project")

    # update
    p_update = sub.add_parser("update", help="Update an existing task")
    p_update.add_argument("task_id", help="Task ID")
    p_update.add_argument("--content", help="New task title/content")
    p_update.add_argument("--description", help="New task description")
    p_update.add_argument("--due_string", help="Natural language due date")
    p_update.add_argument("--due_date", help="Due date in YYYY-MM-DD format")
    p_update.add_argument("--priority", type=int, choices=[1, 2, 3, 4], help="New priority")
    p_update.add_argument("--labels", help="Comma-separated label names (replaces existing)")

    # complete
    p_complete = sub.add_parser("complete", help="Mark a task as complete")
    p_complete.add_argument("task_id", help="Task ID")

    # reopen
    p_reopen = sub.add_parser("reopen", help="Reopen a completed task")
    p_reopen.add_argument("task_id", help="Task ID")

    # delete
    p_delete = sub.add_parser("delete", help="Delete a task permanently")
    p_delete.add_argument("task_id", help="Task ID")

    # projects
    sub.add_parser("projects", help="List all projects")

    # today_overdue
    sub.add_parser("today_overdue", help="List overdue and today's tasks in separate sections")

    # daily_summary
    sub.add_parser(
        "daily_summary",
        help="Daily summary: today pending tasks + overdue reschedule prompts + tomorrow preview",
    )

    args = parser.parse_args()

    try:
        api_key = load_api_key()
    except RuntimeError as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

    dispatch = {
        "list": cmd_list,
        "get": cmd_get,
        "create": cmd_create,
        "update": cmd_update,
        "complete": cmd_complete,
        "reopen": cmd_reopen,
        "delete": cmd_delete,
        "projects": cmd_projects,
        "today_overdue": cmd_today_overdue,
        "daily_summary": cmd_daily_summary,
    }

    dispatch[args.command](api_key, args)


if __name__ == "__main__":
    main()
