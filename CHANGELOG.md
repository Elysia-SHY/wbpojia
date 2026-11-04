# 更新日志

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循语义化版本。

## v2.1.0 — 2026-11-04

自带自定义系统提示词、命令闸门从 2 处扩到 4 处（外加真正弹审批的 `BashTool.needsApproval`）、计划任务自愈改成指纹秒退，并补上 Scoop 清单与兼容性说明。

### 新增

- **自定义系统提示词（`persona` 子命令）**：`persona`（无参）显示当前人格的来源、字数与保存位置；`persona set "<文本>"` 直接设置；`persona set --file <路径>` 从文件读；`persona reset` 删除自定义、回到内置「小码酱」。
- **面板「人格」卡片**：多行文本框 + 「保存」「保存并应用」「恢复内置默认」三个按钮（另有「载入内置默认文本」，把内置人格填进框里再改）。保存后 `apply` 时生效；「保存并应用」= 保存完立刻打一次补丁。
- **人格存储五档优先级**：`--persona` 参数 > 脚本/exe 同目录 `persona.md` > 同目录 `my-prompt.txt` > 状态目录 `_wb状态\persona.md` > 内置默认。第三、四顺位的实际落点由可写性决定（exe 放在 `Program Files` 时自动落到 `%LOCALAPPDATA%\wbpojia\persona.md`）。**不用再手改文件**：面板里写完点「保存并应用」，或者命令行 `persona set` 都行。
- **JS 语法安全网**：改完 JS 立刻 `node --check`，不通过就放弃这个文件（不写盘，其余文件继续处理）；找不到 node 时退化成括号配平检查。`--no-verify` 可跳过这道检查。
- **Scoop 清单**：`docs/scoop/wbpojia.json`（装 zip 里的两个 exe、带 shortcuts、`checkver` + `autoupdate` 跟 GitHub releases）与 `docs/scoop.md`（怎么装、怎么升级、怎么卸载、hash 怎么维护）。
- **`docs/compatibility.md`**：打得到哪些判定点、哪两处改不动、客户端升级或重装之后按什么顺序处置。

### 变更

- **命令契约从 10 个扩到 11 个**：新增 `persona`。参数表新增 `--file`（`persona set` 从文件读）、`--reset`（`persona` 删自定义人格）、`--no-verify`（跳过 JS 语法校验）。
- **命令闸门从 2 处扩到 4 处**（另加一处属性注入）：除 `checkBashSecurityWindows` / `checkPowerShellSecurity` 的首行 `return{behavior:"allow"};` 之外，`getDestructiveCommandWarning` 首行 `return null;`、`isSandboxForcedByManagedPolicy` 首行 `return false;`；而真正会弹审批的 `BashTool.needsApproval` 首行打成 `return!1;`。`status` 的 L3 段除 `[已开 N/M]` 外逐条列出闸门名与「已开 / 未开 / 不存在」，`check` 的 L3 行仍是文件级 `2/2`。
- **计划任务自愈走指纹快路径**：`apply --quiet` 先比对指纹（目标目录 mtime + 条目数 + `installed_plugins.json` 与 `cli\product.json` 的哈希 + 引擎版本），没变就直接退出，不再扫 692 个文件；`--force` 跳过快路径强制重扫。`guard-install` 仍是两条任务（每 30 分钟 + 登录时）。
- **发版物料**：Release 包名 `wbpojia-v2.1.0-win64.zip`；两份 README 与本文档的版本号引用同步到 v2.1。

### 修正

- **真正弹审批的那一环之前没打**：只打两个 `checkXxxSecurity` 时，`BashTool.needsApproval` 还会自己再判一次（先看 `checkBashSecurityWindows(command).behavior`，再走 `sandboxPermissionGateway.shouldUseSandboxPath`，最后取 `applyCommandGate` 的返回值），命令仍可能进审批。现在它首行返回 `false`。
- **托管策略那一环之前没打**：`clientSecurity → isSandboxForcedByManagedPolicy` 读 `ACC_PRODUCT_CONFIG_*` 的下发值，企业策略把它打开时沙箱强制生效。现在首行 `return false`。
- **危险命令提示那一环之前没打**：`getDestructiveCommandWarning` 逻辑独立于两个 `checkXxxSecurity` 函数，现在 `return null`。
- **写坏的风险**：注入是纯字符串插入，宿主换个写法就可能落下语法不成立的 JS。现在先过 `node --check`，不通过就不落盘。
- **自愈空转**：每 30 分钟全量扫描在「什么都没变」时纯属浪费，改成指纹比对后同一状态下直接退出（护照里记 `fingerprint` 与 `version`，升级后第一次仍会全量跑）。

## v2.0 — 2026-11-02

首个作为独立仓库公开发布的版本。

### 新增

- 发布物料齐备：`README.md`（英文简版）、`README.zh.md`（中文全文）、`LICENSE`、`NOTICE`、`CHANGELOG.md`、`.gitignore`、`.github/workflows/ci.yml`、`persona.example.md`、`docs/upstream.md`。
- **单文件 exe**：`build-exe.ps1` 一条命令产出 `dist\wbpojia.exe`（PyInstaller 6.16 `--onefile`，7.45 MB，冷启动 0.6–1.8 s）；引擎支持冻结态（`sys.frozen`），状态目录跟 exe 走、可写性探测失败自动退 `%LOCALAPPDATA%\wbpojia`，`guard-install` 在 exe 形态下直接指向 exe。三个 bat 优先用同目录 exe，没有才回退 Python。`tests/selftest.py` 支持 `WBPOJIA_ENGINE`，同一套断言可直接跑在 exe 上。
- `docs/upstream.md`：上游 [pojia-next](https://github.com/z91772524-ai/pojia-next) 的许可证与作者核实记录（URL + 原文片段）。
- GitHub Actions CI：`windows-latest` × Python 3.9 / 3.11 / 3.12，做语法编译、`--help` 命令契约、空目录 `--dry-run` / `check` / `status` 冒烟（不接触真实安装目录）、发布物料与 `.gitignore` 规则校验、以及「仓库内不得出现本机绝对路径」检查。

### 变更

- **命令契约冻结为 v2.0，共 10 个子命令**：引擎文件 `wbpojia.py`；`status` / `check` / `doctor` / `apply` / `revert` / `cloudmem` / `guard-install` / `guard-remove` / `menu` / `onekey`。`doctor` 是只读环境自检，也是「显示异常 / 找不到目录」的第一处置手段，属契约内命令（CI 的 `--help` 校验必须 10 个名字齐全）。参数 `-i` `-d` `-p` `--dry-run` `--full` `--ask-mode` `--web-filter` `--nofileguard` `--force` `--restart` `--keep-cache` `--no-js` `--deep-js` `--no-cloudmem` `--clean-spill` `--purge-spill` `--quiet` `-v` `--pick` `--all` `--save-path`。文档与代码以本清单为准，不再引入清单外的参数。
- 引擎由维护者重写，行为按「六层靶点」契约保持（模板 `<content_policy>` 替换、`product.json` 文本级替换、命令闸门放行、`plugins` 副本同步、`acc-product-config-v3.json` 重建、云记忆通道）。重写与原 v1.1 实现的逐行差异以仓库提交记录为准。
- 输出分层：`status` 对 L1–L6 逐层输出（该层没有文件也出标题与 0 行小计），`check` 输出「层 / 说明 / 达标 / 结论」四列表 + 问题清单；
- 控制台代码页由引擎接管：读当前输出代码页 → 尝试 `SetConsoleOutputCP(65001)` → 切不动就退回本机代码页并把 stdout/stderr 设为 `errors="replace"`。修掉 v1.1「有些东西显示不了 / 满屏问号」（bat 里 `chcp 65001` + `PYTHONIOENCODING=utf-8` 与 936 控制台不一致）；
- 三个双击入口：`破甲.bat`（`onekey` = `apply --no-cloudmem`）、`破甲菜单.bat`（`menu`，可带参数直达，如 `破甲菜单.bat 3`）、`自检.bat`（`doctor`）；三者零硬编码，按 `WBPOJIA_PYTHON` → `where py` → `python` → `python3` 自适应，找不到 Python 时停窗提示并退出码 1。
- 许可：上游核实为 **MIT**（`Copyright (c) 2026 z91772524-ai`），本仓库沿用 MIT 并保留上游版权行。

### 修正（全部来自 REA 对客户端的静态核对，证据见 `docs/rea-workbuddy.md`）

- **L2 补上被漏扫的第二份政策源**：`node_modules\@genie\agent-harness\cli\product.json`（358 KB）同样含 `<content_policy>`，v1.1 的目标表与 JS 列表都不含它。现在两份 `product.json` 都归 L2。
- **L5 从「盲删一个已不存在的文件名」改成按现行命名判定**：当前缓存是 `acc-product-config-v3-<pid>-<uuid>.json`，每次启动从已打补丁的 `cli\product.json` 重建、48 小时自清理。现在逐份检查里面有没有覆盖层，只清「从未打补丁的 product.json 重建出来的」那一份；全部正常时明确说「无需处理」。
- **`--ask-mode` 真正生效**：`ASK_OLD` 的唯一靶点 `resources\templates\ask-mode-reminder.tpl` 没有 `<content_policy>`，v1.1 在「不含政策块就跳过」这一步把改动丢掉了，该参数一直是空转。现在不含政策块的文件也会走写入路径（仅文本补丁），并单独标注。
- **`revert` 不再拿旧备份覆盖新记忆**：`cloudmem_revert` 原先只要发现 `.pojia.bak` 就盖回去，本机存在 10/16 的旧备份而现行档案是 10/21 的 `Version: 30`，直接跑会吞掉 5 天的账号记忆。现在仅当「当前档案确实是本工具注入过」才回滚，否则保留现状并提示。
- **L5 删除前留档**：删缓存前先落 `.unlockbak`，`revert` 才真的能回到原状。

### 未变更

- 零第三方依赖（仅标准库）、无联网、无 GUI。

## v1.1 — 归档版本

仓库化之前的最后一个脚本版本（归档文件名为 `pojia-wb.py.v1.1-archive`）。

- 六层靶点完整实现，含 `plugins` 下 `welcomemode` 副本同步与 `acc-product-config-v3.json` 重建。
- 云记忆通道：`memory\<uid>_memory.md` 的 `memoryBlock`，`Version 999999`、只读、原档存 `.pojia.bak`。
- `guard-install` 注册两条计划任务（`WorkBuddyUnlockV6_Hourly` 每 30 分钟、`WorkBuddyUnlockV6_Logon` 登录时），`guard-remove` 一并清理历史旧任务名。
- `menu` 数字菜单与 `onekey` 一键入口。
- 备份后缀 `.unlockbak`；状态目录 `_wb状态\`。

## v1.0 — 早期版本

- 从上游 [pojia-next](https://github.com/z91772524-ai/pojia-next) 的补丁引擎中把 WorkBuddy 这一路单独拆出，去掉图形界面、在线校验、广告位与其余目标平台。
- 早期版本的细节**未核实**（仅保留归档文件 `pojia-wb.py.bak-20261025`），此处不展开。
