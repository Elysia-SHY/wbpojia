# 更新日志

## v2.1.0 — 2026-11-04

### 新增

- `persona` 子命令：查看当前人格，或者 `persona set "..."`、`persona set --file ...`、`persona reset`。
- 面板加了一个人格输入框，带「保存」「保存并应用」「恢复内置默认」。
- 改 JS 之后用 `node --check` 验语法，不通过就不写盘；没装 node 时只查括号配平。
- Scoop 清单 `docs/scoop/wbpojia.json`，以及 `docs/scoop.md`、`docs/compatibility.md`。

### 变更

- 命令从 11 个变 12 个，加了 `persona`。
- 闸门从 2 个加到 5 个。除了原来那两个，补上 `BashTool.needsApproval`（真正弹审批的那个）、`isSandboxForcedByManagedPolicy`、`getDestructiveCommandWarning`。
- `status` 的 L3 段逐条列出闸门名和状态。
- `apply --quiet` 先比指纹，没变就直接退出，不再全量扫描。
- Release 包名改成 `wbpojia-v2.1.0-win64.zip`。

### 修正

- 改了人格，已经打过补丁的文件不更新。原因是为省一次 386 KB 写盘而跳过「哈希对不上」的文件，把人格变更一起吞了。现在哈希对不上就重写。
- `persona reset` 会把 "reset" 当成正文写进去。

## v2.0.0 — 2026-11-02

第一次单独发版。

- 引擎重写：六层分开输出，加了 `doctor`，控制台代码页自己接管（修 v1.1 的乱码）。
- 打出两个 exe：控制台版和无窗口的面板版，双击都是开面板。
- L2 补上漏扫的 `node_modules\@genie\agent-harness\cli\product.json`。
- L5 删的是已不存在的文件名，改成按 `<pid>-<uuid>` 命名逐份判断。
- `--ask-mode` 之前空转，因为唯一靶点没有 `<content_policy>`，改动被跳过逻辑丢了。
- `revert` 会拿旧 `.pojia.bak` 覆盖客户端后来写的新记忆。
- `apply --full` 先中和文件保护再整块替换政策块，中和白做。
- `guard-install --dry-run` 一直返回 1；两条计划任务都补了 `/RL HIGHEST`。

## v1.1（归档）

仓库化之前的脚本版本，留在 `pojia-wb.py.v1.1-archive`。

## v1.0（早期）

从 pojia-next 拆出 WorkBuddy 这一路。细节没有留存，只剩 `pojia-wb.py.bak-20261025`。
