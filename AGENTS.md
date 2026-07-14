# AGENTS.md — hermes-todoist-skill

---

## Git 分支治理規範（Branch Governance）

本專案採用以下分支策略，所有協作者（含 AI agent）皆須遵守：

### 分支角色

| 分支 | 角色 | 限制 |
|---|---|---|
| `main`（或 `master`） | 正式發布 | 禁止直接 push，只能由 PR 合併 |
| `dev` | 整合開發 | 禁止直接 push，只能由 PR 合併 |
| `feat/*` | 功能開發 | 必須由 `dev` 建立，PR 只能合併至 `dev` |
| `fix/*` | 一般修復 | 必須由 `dev` 建立，PR 只能合併至 `dev` |
| `hotfix/*` | 緊急修復 | 必須由 `main` 建立，可合併至 `main`；完成後必須再 PR 回 `dev` |
| `release/*` | 發布準備 | 由 `dev` 建立，可合併至 `main` 與 `dev` |

### PR 合併規則

- PR 目標為 `dev`：只允許來源 `feat/*`、`fix/*`、`hotfix/*`、`release/*`
- PR 目標為 `main`：只允許來源 `dev`、`release/*`、`hotfix/*`
- 違規 PR 會被 `branch-policy` workflow 標記為失敗，不得合併。

### Conventional Commits

所有 commit message 前綴須遵循 Conventional Commits：

| 前綴 | 用途 |
|---|---|
| `feat:` | 新功能 |
| `fix:` | 修復 bug |
| `refactor:` | 重構（不改變行為） |
| `docs:` | 文件變更 |
| `chore:` | 雜務（建置、依賴、設定等） |

範例：
```
feat: add SDS comparison export endpoint
fix: correct Klimisch scoring null check
refactor: extract citation formatter
docs: update README deployment section
chore: bump dependencies
```

### 禁止事項

- 禁止直接 push 到 `main` / `dev`
- 禁止 force push 到任何受保護分支
- 禁止未經審核自行 merge PR