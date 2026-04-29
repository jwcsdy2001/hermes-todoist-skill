---
name: todoist-crud
description: |
  對 Todoist 任務進行完整 CRUD 操作（建立、查詢、更新、完成、重開、刪除）。
  使用 Todoist API v1（REST v2 / Sync v9 已於 2026-02-10 停用）。
  API Key 從 ~/.hermes/.env 的 TODOIST_API_KEY 讀取。
  觸發情境：建立任務、查任務、更新任務、完成任務、刪除任務、管理待辦。
allowed-tools: ["Bash"]
---

# Todoist CRUD Skill

對 Todoist 任務進行完整 CRUD 操作，使用 Todoist API v1。

## 重要提醒：API 版本

> ⚠️ Todoist REST v2（`api.todoist.com/rest/v2/`）和 Sync v9（`api.todoist.com/sync/v9/`）已於 **2026-02-10** 停用，請求會回傳 **410 Gone**。
>
> 本 Skill 僅使用 **API v1**：`https://api.todoist.com/api/v1/`

## 腳本位置

Skill 目錄下的 `scripts/todoist.py`。執行時用絕對路徑，或先 `cd` 到 Skill 目錄。

## API Key 讀取

腳本自動從 `~/.hermes/.env` 讀取 `TODOIST_API_KEY`，無需手動傳入。

## 觸發條件

- 「新增任務 XXX」、「幫我建一個 Todoist 任務」
- 「查 Todoist 任務」、「列出今天的待辦」、「查某個任務的詳情」
- 「更新任務 XXX」、「把任務 XXX 的截止日改成明天」
- 「完成任務 XXX」、「標記 XXX 為已完成」
- 「重新開啟任務 XXX」
- 「刪除任務 XXX」
- 「列出今天到期及已過期的任務」、「今日待辦 + 過期任務」
- 「今天的執行狀況」、「今日任務統整」、「明天要做什麼」、「幫我整理今天的工作並展望明天」、「過期任務要不要改期」

---

## 優先度對照（Todoist 定義）

| 參數值 | 顏色 | 意義     |
|--------|------|----------|
| `1`    | 🔴 紅 | 緊急 (p1) |
| `2`    | 🟠 橙 | 高 (p2)   |
| `3`    | 🔵 藍 | 中 (p3)   |
| `4`    | ⬜ 無 | 一般 (p4，預設) |

---

## 操作一覽

### 1. 列出任務（List Tasks）

```bash
python3 scripts/todoist.py list [--filter FILTER] [--project_id ID] [--limit N]
```

常用 filter 範例：
- `today` — 今天到期
- `overdue` — 已過期
- `today|overdue` — 今天 + 過期（需 URL encode 但腳本會處理）
- `#ProjectName` — 特定專案
- `@label` — 特定標籤
- `p1` — 優先度 1

回傳：`{ "results": [...], "next_cursor": null }`

每筆任務欄位：
- `id` — 任務 ID（後續操作用）
- `content` — 標題
- `description` — 描述（Markdown）
- `due` — `{ "date": "YYYY-MM-DD", "string": "...", "is_recurring": false }`
- `priority` — 1-4（1=最高）
- `labels` — 標籤陣列
- `project_id` — 所屬專案 ID
- `checked` — 是否已完成
- `is_deleted` — 是否已刪除

---

### 2. 查詢單一任務（Get Task）

```bash
python3 scripts/todoist.py get <task_id>
```

---

### 3. 建立任務（Create Task）

```bash
python3 scripts/todoist.py create \
  --content "任務標題" \
  [--description "描述（支援 Markdown）"] \
  [--project_id PROJECT_ID] \
  [--due_string "tomorrow"] \
  [--due_date "2026-05-01"] \
  [--priority 1] \
  [--labels "label1,label2"] \
  [--parent_id PARENT_TASK_ID] \
  [--section_id SECTION_ID]
```

- `--content` 必填
- `--due_string` 支援自然語言（Todoist 會解析），例如 `"明天下午三點"`、`"next Monday"`
- `--due_date` 固定日期格式 `YYYY-MM-DD`，與 `--due_string` 擇一使用
- `--priority` 不填預設為 4（一般）
- 不指定 `--project_id` 則放入收件匣（Inbox）

回傳：建立後的完整任務物件

---

### 4. 更新任務（Update Task）

```bash
python3 scripts/todoist.py update <task_id> \
  [--content "新標題"] \
  [--description "新描述"] \
  [--due_string "next Friday"] \
  [--due_date "2026-05-10"] \
  [--priority 2] \
  [--labels "new_label1,new_label2"]
```

- 只需傳要修改的欄位，其餘不變
- `--labels` 會**完整替換**現有標籤

回傳：更新後的完整任務物件

---

### 5. 完成任務（Complete Task）

```bash
python3 scripts/todoist.py complete <task_id>
```

回傳：`{ "success": true }`（HTTP 204）

---

### 6. 重新開啟任務（Reopen Task）

```bash
python3 scripts/todoist.py reopen <task_id>
```

回傳：`{ "success": true }`（HTTP 204）

---

### 7. 刪除任務（Delete Task）

```bash
python3 scripts/todoist.py delete <task_id>
```

⚠️ 刪除是**永久性**操作，無法復原。刪除前應向使用者確認。

回傳：`{ "success": true }`（HTTP 204）

---

### 8. 列出專案（List Projects）

```bash
python3 scripts/todoist.py projects
```

回傳：`{ "results": [...] }`，每筆含 `id`、`name`、`color`、`is_inbox_project` 等欄位。

---

### 9. 列出今日及過期任務（Today + Overdue）

```bash
python3 scripts/todoist.py today_overdue
```

同時拉取 `overdue` 與 `today` 兩個 filter，分區回傳：

```json
{
  "date": "2026-04-29",
  "summary": { "overdue_count": 2, "today_count": 3, "total": 5 },
  "overdue": [ ...任務列表... ],
  "today":   [ ...任務列表... ]
}
```

---

### 10. 每日執行統整 + 明日展望（Daily Summary）

```bash
python3 scripts/todoist.py daily_summary
```

同時拉取 `overdue`、`today`、`tomorrow` 三個 filter，回傳完整每日報告：

```json
{
  "report_date": "2026-04-29",
  "tomorrow_date": "2026-04-30",
  "today_execution": {
    "pending_count": 3,
    "tasks": [ ...今日待辦... ]
  },
  "overdue": {
    "count": 2,
    "tasks": [ ...過期任務... ],
    "reschedule_items": [
      {
        "id": "abc123",
        "content": "任務名稱",
        "due": { "date": "2026-04-27" },
        "reschedule_prompt": "任務「...」已過期（原到期：2026-04-27），請問要改期、完成還是刪除？"
      }
    ],
    "agent_instruction": "以下任務已逾期，請逐一向使用者確認：要改期（提供新日期）、標記完成，還是刪除？"
  },
  "tomorrow_preview": {
    "count": 2,
    "tasks": [ ...明日任務... ]
  }
}
```

**代理人使用建議（daily_summary）：**
`reschedule_items` 已包含每筆過期任務的 `reschedule_prompt` 字串，可直接用於向使用者詢問。
後續操作：改期用 `update`、完成用 `complete`、刪除用 `delete`（需二次確認）。

---

## 典型工作流程

### 建立有截止日的任務

```bash
python3 scripts/todoist.py create \
  --content "回覆 ABC 客戶 email" \
  --due_string "today 18:00" \
  --priority 2
```

### 查今天+過期的任務

```bash
python3 scripts/todoist.py list --filter "today|overdue"
```

### 查特定專案的任務

```bash
# 先查專案 ID
python3 scripts/todoist.py projects

# 再查該專案的任務
python3 scripts/todoist.py list --project_id <project_id>
```

### 完成一個任務

```bash
# 先查任務 ID（假設搜尋關鍵字）
python3 scripts/todoist.py list --filter "search: 客戶 email"

# 完成該任務
python3 scripts/todoist.py complete 6c3JXPfgqJv3PMhr
```

### 更新截止日

```bash
python3 scripts/todoist.py update 6c3JXPfgqJv3PMhr --due_string "tomorrow"
```

---

## 錯誤處理

| 錯誤 | 說明 |
|------|------|
| `401 Unauthorized` | API Key 錯誤或過期，檢查 `~/.hermes/.env` 的 `TODOIST_API_KEY` |
| `403 Forbidden` | 無權限操作（例如嘗試操作他人任務） |
| `404 Not Found` | 任務 ID 不存在或已被刪除 |
| `410 Gone` | 使用了舊版 API（REST v2 / Sync v9），請改用 API v1 |
| `429 Too Many Requests` | 超過 API 限制，稍待片刻再重試 |

腳本在 HTTP 錯誤時輸出 JSON 到 stderr 並以非零 exit code 退出：
```json
{ "http_error": 404, "detail": { "error": "Task not found" } }
```

---

## 已知陷阱

| 陷阱 | 說明 |
|------|------|
| REST v2 回 410 | `api.todoist.com/rest/v2/tasks` 已停用 |
| Sync v9 回 410 | `api.todoist.com/sync/v9/sync` 已停用 |
| `tmp-` 開頭的 ID | 是前端暫時 ID，尚未同步到伺服器，不可用於 API |
| priority 語義 | Todoist API 中 `priority=1` 是最高（紅/緊急），`priority=4` 是最低（一般） |
| labels 替換 | update 的 `--labels` 會完整替換現有標籤，不是追加 |
| delete 不可復原 | 刪除任務前應向使用者確認 |

---

## 參考資料

- [Todoist API v1 官方文件](https://developer.todoist.com/api/v1/)
- [Todoist Python SDK](https://doist.github.io/todoist-api-python/)
- API Key 位置：`~/.hermes/.env` → `TODOIST_API_KEY`
