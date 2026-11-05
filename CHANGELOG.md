# 更新日志

## v2.2.0 — 2026-11-05

### 新增

- `apply` / `onekey` 在 `%ProgramFiles%` 安装下自动请求 UAC：以 `runas` 重跑原命令，等待管理员进程结束并透传其退出码。面板触发时同样处理，并回报退出码。
- `--no-elevate`：禁止自动提权，只以当前权限执行。

### 修正

- 备份 `.unlockbak` 失败后仍会继续写入，可能在无备份的情况下改掉客户端文件。现在备份失败即跳过该文件，原文件不动。
- L1/L2/L4、L3 闸门与网页过滤全部写入失败时，仍输出「提示词靶点全部已是最新」并以 0 退出，结尾按「完成」收尾。现在失败汇总为「未完成」、返回 1，且写入列表为空时也执行回读核对。
- 权限错误一律提示「以管理员身份运行」。现在先判断当前是否已提权：已提权仍失败时，改为指向目录安全权限、所有者与安全软件拦截。
- Web 过滤写入未捕获异常，会把整个 `apply` 打断。

### 变更

- 回读核对发现的未生效项计入错误数与退出码。
- `--restart` 与「请完全退出 WorkBuddy」提示仅在无错误时出现。
- 新增回归用例：备份失败保护、错误退出码、提权分支与 UAC 调用参数、管理员进程退出码透传。

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
