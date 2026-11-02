# WorkBuddy 破甲靶点面 —— REA 静态核对报告

> **路径约定**：本文所有证据里的本机路径已替换为占位符 —— `<INSTALL>` = WorkBuddy 安装根，`<USERPROFILE>` = 当前用户主目录，`<user>` = 用户名。文件内容、偏移、行号未做任何改动。

- 被分析物：`<INSTALL>`（WorkBuddy，Electron / PE x64，安装清单 appVersion 5.9.3）
- 数据目录：`<USERPROFILE>\.workbuddy`
- 核对对象：`scripts (脚本库 按来源分类)\workbuddy\pojia-wb.py`（1534 行，VERSION 1.1）
- 分析方式：REA MCP 6.7.0 静态分析（`analyze_javascript_application` / `inspect_managed_artifact` / `inspect_managed_members` / `inspect_electron_fuses`）+ ASAR 头直接解析（只读）。**未运行 WorkBuddy**，未修改安装目录与数据目录任何文件。
- 每个结论标注证据；`[观测]` = 产物实测，`[推断]` = 由观测推导，`[未知]` 见文末。

关键产物身份（证据）：

| 产物 | 大小 | SHA-256（REA 读数） |
|---|---|---|
| `resources\app.asar` | 181,996,084 | `dcabcd90f07a627a06f1fd55bc872a1c25a79aab43c3012930b6287840ab3d20` |
| `WorkBuddy.exe` | 204,590,360 | `bbf504003825e0e22dd8c401b396d79db78ec603558088565d1b2e81561704a0` |
| `RepairApp.exe` | 260,888 | `ab772597f7aaa224a778d11ee37ff372b7f7db66908eafb265039fbb78d8ffb9`（MVID `553b6e63-59ec-4101-a3ba-345d7cc74730`） |

ASAR 结构：header 2,609,612 字节，数据起点 2,609,620，目录内 **9893 个条目**（6585 打包 / 3308 解包），**每个条目都带 SHA-256 + 4 MiB block 声明**。

---

## ① 含 `<content_policy>` 的资源清单：26 个命中面，与 find_targets 的 26 一致；另有 1 个被漏掉

`[观测]` 分类统计：安装侧 13 个 `.tpl` + `cli\product.json` = **14**；数据侧 12 个 `.tpl` = **12**；合计 **26**。另有 1 个含同样政策的文件未被任何一层覆盖（见下）。

### 安装侧（`resources\app.asar.unpacked`）

| # | 文件（相对 app.asar.unpacked） | 命中行 | pojia 层 |
|---|---|---|---|
| 1 | `resources\templates\workbuddy-prompt.tpl` | 25 | 1 |
| 2 | `resources\templates\workbuddy-expert-prompt.tpl` | 10 | 1 |
| 3 | `resources\templates\workbuddy-expert-coding-prompt.tpl` | 10 | 1 |
| 4 | `resources\templates\workbuddy-expert-code-prompt.tpl` | 10 | 1 |
| 5 | `resources\templates\workbuddy-craft-design-prompt.tpl` | 34 | 1 |
| 6 | `resources\templates\workbuddy-craft-coding-prompt.tpl` | 25 | 1 |
| 7 | `resources\templates\workbuddy-craft-code-prompt.tpl` | 25 | 1 |
| 8 | `resources\templates\workbuddy-ask-prompt.tpl` | 25 | 1 |
| 9 | `resources\templates\workbuddy-ask-coding-prompt.tpl` | 25 | 1 |
| 10 | `resources\templates\workbuddy-ask-code-prompt.tpl` | 25 | 1 |
| 11 | `resources\plugins\workbuddy-builtin\welcomemode\code\prompt.tpl` | 24 | 1 |
| 12 | `resources\plugins\workbuddy-builtin\welcomemode\design\prompt.tpl` | 38 | 1 |
| 13 | `resources\plugins\workbuddy-builtin\welcomemode\work\prompt.tpl` | 33 | 1 |
| 14 | `cli\product.json` | JSON 行 1242（`prompts["1"].template`，长度 21,301） | 2 |
| **漏** | `node_modules\@genie\agent-harness\cli\product.json` | 行 1（整份单行 JSON） | **无** |

`[观测]` `resources\templates` 共 19 个 `.tpl`，其中 6 个不含政策：`ask-mode-reminder.tpl`、`craft-mode-reminder.tpl`、`system-reminder.tpl`、`user-context-identity.tpl`、`user-context-expert-identity.tpl`、`workbuddy-quick-prompt.tpl`。find_targets 会扫到它们，但因不含 `<content_policy>` 被跳过（`pojia-wb.py:1073`、`:1115`、`:1300`）。

### 数据侧（`<USERPROFILE>\.workbuddy`）

12 个文件，路径规律 `plugins\cache\workbuddy-builtin\welcomemode-{code,design,work}\<版本>\prompt.tpl`，四个版本目录各一份：

- `5.8.3-wb.41334564.gdb0e9b51.h4da087921e4a`
- `5.9.0-wb.41809846.g0f0c2199.hbd0fd5f89518`
- `5.9.2-wb.42136757.g0b5051be.hd4338c001c60`
- `5.9.3-wb.42398134.gd4692421.h480e8d1fee0f`

`[观测]` 12 份全部已打补丁（`最高优先级覆盖` ×2、`请求即授权` ×2、`破甲自检` ×2），mtime 全部为 `2026-11-02T12:02:47`；安装侧同 3 个 welcomemode 副本 mtime 相同、字节长度相同（code 31,164 / design 27,816 / work 31,518），说明是同一次 apply 写入。

### find_targets 扫描范围评价

`[观测]` `pojia-wb.py:692-732`：安装侧只走 `app.asar.unpacked\resources`（递归 `.tpl`）与 `app.asar.unpacked\cli`（递归 `.tpl`）加死路径 `cli\product.json`；数据侧走 `<data>\plugins` 递归 `.tpl`。

- **方向正确**：13 个安装侧 tpl 全在 `resources\` 下，12 个数据侧副本全在 `plugins\` 下，都被覆盖。
- **统计噪音**：数据侧递归会把 `plugins\marketplaces\...\ppt-implement\...\templates\cover\*.tpl`（PPT 封面模板，本机数百个）一并扫入，靠"不含 `<content_policy>` 就跳过"才没坏事（`pojia-wb.py:1115`）。
- **真实漏洞（唯一一处）**：`node_modules\@genie\agent-harness\cli\product.json` 含 `<content_policy>`，且与 asar 声明的 SHA-256 一致（未被打补丁），而 find_targets 的目标表与 JS_REL 都不含这个路径。
- **边界说明**：`resources\qm`、`resources\vendor`、`resources\wb-guest-sdk`、`resources\scripts` 内无政策文本；整个 9893 条目的 app.asar 里 `<content_policy>` 只出现在 `main/database-factory.js`，那是一段**剥离** `<content_policy>…</content_policy>` 的正则（用于从历史消息里抽用户原话，模块内偏移 ≈242,263），不是第二份政策源。

---

## ② 命令闸门：真实位置、数量与偏移（与 pojia 假设一致，但不是唯一一道门）

`[观测]` 全解包树 grep `checkBashSecurityWindows|checkPowerShellSecurity`，只有 2 个文件命中（外加各自 `.unlockbak`）：

| 文件 | 函数 | 定义位置 | 已注入放行 |
|---|---|---|---|
| `cli\dist\codebuddy-lite-wb.mjs`（9,880,112 B） | `checkBashSecurityWindows` | 字符偏移 **5,848,897**（grep 行 1782） | `return{behavior:"allow"};` 紧跟 `{` 之后，偏移 5,848,934 |
| 同上 | `checkPowerShellSecurity` | 偏移 **5,871,905**（grep 行 2012） | 紧跟注入，偏移 5,871,941 |
| `node_modules\@genie\agent-harness\cli\dist-server\shared.cjs`（21,141,865 B） | `checkBashSecurityWindows` | 偏移 **8,012,630**（grep 行 1611） | 注入偏移 8,012,668 |
| 同上 | `checkPowerShellSecurity` | 偏移 **8,035,770**（grep 行 1633） | 注入偏移 8,035,807 |

- 每个名字在文件里**只有一处是 function 定义**，其余是调用点（Bash 各 3 处、PowerShell 各 4 处：`codebuddy-lite-wb.mjs` 调用点在 5,884,700 / 5,888,116 与 5,875,189 / 6,338,422 / 6,340,365；`shared.cjs` 对应 8,049,051 / 8,052,612 与 8,039,193 / 8,545,619 / 8,547,689）。因此 `_gate_match` 的"只 patch 第一处定义"（`pojia-wb.py:528-540`）在这里**正好够用**。
- `[观测]` `main/server.js` 的 CLI 解析顺序：`cli/bin/codebuddy` → `cli/dist/codebuddy-lite-wb.mjs` → `cli/dist/codebuddy-headless.js`，可用 `CODEBUDDY_CODE_PATH` 覆盖（模块内偏移 2,913,566 与 3,584,423）。`cli/bin/codebuddy` 本体是 JS 启动器（12,886 B），靠 `CODEBUDDY_FORCE_LITE_WB_BUNDLE` 分流到 lite-wb 包（该文件偏移 7,468–7,766 的注释）。所以两处闸门都是活路径，缺一不可。

**pojia 未覆盖的第二、三道门（`[观测]`，同文件内）**：

1. `getDestructiveCommandWarning` —— `checkPowerShellSecurity` 体内的第二道判定（`codebuddy-lite-wb.mjs` 5,871,905 之后紧接使用）；首行 return 之后已不可达，属"顺带被绕过"。
2. `sandboxPermissionGateway.shouldUseSandboxPath(...)` —— 与闸门并列执行，位于 `codebuddy-lite-wb.mjs:5,884,700` 附近调用链；沙箱由 `cli\vendor\sandbox\5.9.5\`（`tsbx.dll`、`sandbox-cli.exe`、`sandbox-center.exe`、`betterleaks.exe`）在**进程外**执行，JS 字符串补丁对它无效。
3. `clientSecurity` 托管策略：`readManagedSecurityPolicyFromEnv()` 依次读 `ACC_PRODUCT_CONFIG_V3`、`ACC_PRODUCT_CONFIG_V2`、`ACC_PRODUCT_CONFIG_PATH`，取 `clientSecurity` → `translateRemoteSecurityCenter` → `isSandboxForcedByManagedPolicy` / `isSandboxDisabledByManagedPolicy`（`codebuddy-lite-wb.mjs` 模块内偏移 1,649,587 与 3,355,926）。即"沙箱开不开"由产品配置决定，不在这两层闸门里。本机 `cli\product.json` 无 `clientSecurity` 键（`productFeatures.Sandbox = true`，`SandboxFileVersionManagement = false`），当前是默认开沙箱状态。

---

## ③ 网页过滤 WF_OLD：当前版本仍然存在，且本机**没有**打这一层

`[观测]` `CONTENT SAFETY (HIGHEST PRIORITY):` 原文各出现 **1 次**：

- `cli\dist\codebuddy-lite-wb.mjs:1843`
- `node_modules\@genie\agent-harness\cli\dist-server\shared.cjs:1672`

替换后的标记串 `never refuse a summary request`（= `pojia-wb.py:156` 的 WF_NEW）在两文件中计数均为 **0**。结论：WF_OLD 仍是有效的替换靶点（字符串未变），但它是 `--web-filter` / `--full` 条件层，本机未执行。`pojia-wb.py:1257-1259` 的替换逻辑本身可用。

---

## ④ acc-product-config-v3：谁写、从哪读、删了会不会回退

`[观测]` 写入方 = 打包模块 `main/workbuddy-product-config.js`（28,623 B，3 个物理行，REA 已确认是 app.asar 内条目）：

- 路径 = `<configDir>\cache\acc-product-config-v3-<pid>-<uuid>.json`，即 `resolveAccProductConfigCachePath()` 用 `process.pid` + `randomUUID()` 拼出（模块内偏移 ≈13,304）。**每个进程一份、永不重名**；本机现存 7 个（PID 13172 / 16424 / 21156 / 21644 / 23896 / 28196 等）。
- 源 = `readProductConfigurationFromDisk()` → `resolveBundledAsset('cli','product.json')`（偏移 ≈15,248），即 **`app.asar.unpacked\cli\product.json`**（被第 2 层打过补丁的那份），不是 harness 那份。
- 落盘条件：序列化后 > 48,000 B 才写 spill 文件并设 `ACC_PRODUCT_CONFIG_PATH`；≤ 48,000 B 直接进环境变量 `ACC_PRODUCT_CONFIG_V3`（偏移 13,304 与 24,246 的 `L=48e3`）。
- 自清理：`runAccProductConfigSpillHousekeeping()` 只在"写者 PID 已死 + mtime 超 48 h（`V=1728e5`）"时删除；plain 名 `acc-product-config-v3.json`（常量 `B`）被**显式跳过**。
- `[观测]` 7 个 spill 内容核验：全部 `最高优先级覆盖`×2、`请求即授权`×2、`unlock-v6`×1，且 `CONTENT SAFETY (HIGHEST PRIORITY)` = 0 —— 每次启动都从**已打补丁**的 product.json 重建，不存在旧缓存反噬。

**对第 5 层的判定**：`pojia-wb.py:1091/1263` 直接删 `<data>\cache\acc-product-config-v3.json` —— 该文件名在当前版本**已不存在**（本机只剩工具当年留下的 `acc-product-config-v3.json.unlockbak`，411,250 B，2026-10-21 22:15，内含原始政策、无覆盖层）。当前版本按 PID+UUID 命名、启动即重建、48 h 自带清理。**该层是过时步骤：无害，但无效**。

---

## ⑤ 宿主完整性与自愈：有校验、有修复工具，但都不恢复提示词内容

### 5.1 ASAR 内嵌完整性：每个条目都声明了 SHA-256

`[观测]` ASAR 目录树 9893/9893 条目带 `integrity{algorithm:SHA256, hash, blockSize:4194304, blocks[]}`，含 3308 个 `.unpacked=true` 条目。逐项比对（声明值 vs 磁盘实际值）：

| 目标 | asar 声明 | 磁盘实际 | 结果 |
|---|---|---|---|
| `cli\product.json` | `a73bea91…eed61` | `5aa33640…637dd` | **不符**（第 2 层改过） |
| `cli\dist\codebuddy-lite-wb.mjs` | `c57a02ee…77ea5` | `71ea2a1e…71ad6` | **不符**（第 3 层） |
| `…\dist-server\shared.cjs` | `9da830d4…d692b` | `2fc2f4e4…3d75d9` | **不符**（第 3 层） |
| `resources\templates\workbuddy-prompt.tpl` | `a8ed75f2…477e9a` | `bcfb6a8a…5668c2` | **不符**（第 1 层） |
| 另 9 个 `workbuddy-{ask,craft,expert}-*-prompt.tpl` | — | — | 同样不符 |
| `resources\plugins\…\welcomemode\{code,design,work}\prompt.tpl` | — | — | 同样不符 |
| `node_modules\@genie\agent-harness\cli\product.json` | `8e949431…b7246` | `8e949431…b7246` | **一致**（未打补丁） |
| `ask-mode-reminder.tpl` / `craft-mode-reminder.tpl` / `system-reminder.tpl` / `user-context-*.tpl` / `workbuddy-quick-prompt.tpl` | — | — | 一致（未打补丁） |

合计 **16 处不符**（10 个 `resources\templates` tpl + 3 个 welcomemode tpl + 3 个 JS/JSON）。REA 的限制项也逐条复述了这 16 条（另含 job-object.node、koffi.node、node-pty 等打包期签名/裁剪造成的原生文件不符，与本工具无关）。

### 5.2 Electron fuses（`inspect_electron_fuses`，`WorkBuddy.exe` 偏移 168,886,096，wire v1）

| fuse | 状态 | REA 语义 |
|---|---|---|
| `EnableEmbeddedAsarIntegrityValidation` | **enabled** | outcome = **enforced** |
| `OnlyLoadAppFromAsar` | **enabled** | restricted_to_app_asar |
| `RunAsNode` | enabled | honored |
| `EnableNodeOptionsEnvironmentVariable` | enabled | — |
| `EnableNodeCliInspectArguments` | enabled | honored |
| `EnableCookieEncryption` | disabled | — |
| `GrantFileProtocolExtraPrivileges` | enabled | — |

`[推断]` 该 fuse 校验的是**打包在 asar 内的块**（blockSize/blocks 声明），而本工具改的全是 `.unpacked` 伴生文件。实测支持这个判断：10/27 17:31 起 16 处不符就存在，11/01 18:38 应用仍正常启动并生成**带覆盖层**的 spill（见 ④）。即：**改 tpl/JS/product.json 不会触发启动失败**，但"文件被动过"在产物里是留痕的、可被离线比对。

### 5.3 RepairApp.exe：真正的自愈/预检入口，但**只查存在性、不修 asar-unpacked**

`[观测]` `RepairApp.exe` = .NET Framework 4.6.2 WPF 预检/修复器（anycpu，445 方法，76 类型）。其 `#US` 字符串字面量（REA `inspect_managed_members` → `user_strings`，共 444 条）直接给出机制：

- `install-manifest.json` / `asar.scan: installRoot=` / `manifest=` / `asar.scan: manifest not found, skipping integrity scan` / `asar-unpacked` / **`# skip asar-unpacked: reinstall required`**
- `preflight.done: issueCount={0} hasFatal={1} hasReinstall={2} kinds=[{3}] issues=[{4}]`、`preflight: reinstall needed, showing dialog`
- `preflight.muted: … asar & SingletonLock fatals always bypass mute`、`repair-muted.marker`
- 修复流程：`repair.script.built` → `repair-script-last.ps1`（生成 PowerShell 脚本）、`[wb-repair]`、UAC 相关 `SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System`、`WB-REPAIR-BACKUP`（改名挪开、不重建）、`repair.relaunch.immediate` / `--wb-repair-relaunch`
- **明确指向被改文件**：字符串里出现 `app.asar.unpacked\cli\product.json`

`[观测]` 但 `resources\install-manifest.json` 只有 118 个**纯字符串路径**（`version:1, appVersion:5.9.3, generatedAt:2026-10-27T09:29:19Z`，键仅 `files`，无哈希、无尺寸）→ 它的"asar 完整性扫描"只能是**存在性检查**，无法发现文件被改写。

**结论（自愈问题的回答）**：宿主**有**自愈/预检（RepairApp 预检 + 生成 PowerShell 修复 + 要求重启），但

- 不比对内容哈希，故**检测不到提示词 / 配置被改写**；
- 对 `asar-unpacked` 内容的态度是 **"需要重装"（reinstall required）**，而不是从本地副本恢复；
- `[观测]` 在 9893 条 asar 条目里 `install-manifest` 命中 **0** 次 —— JS 主进程不参与该检查，检查只在原生 RepairApp 里。

### 5.4 数据侧 tpl 的"自愈"= 按版本重建，不是按内容修复

`[观测]` `plugins\installed_plugins.json`（version 2）为每个内置插件记录 `installPath` + `version`，当前全部指向 `5.9.3-wb.42398134.gd4692421.h480e8d1fee0f`（`lastUpdated: 2026-10-28T11:22:36`）。目录命名 = `<semver>-wb.<build>.g<git短sha>.h<内容hash>`，同插件 4 个版本共存，部分旧目录带 `.orphaned_at` 标记。

`[观测]` 时间线把"升级会顶掉补丁"这件事钉死了：

- 2026-10-27 09:29 —— 安装清单重建（appVersion 5.9.3，即本次升级）
- 2026-10-27 17:31:32 —— 第 1 层 `.unlockbak` 落盘（升级后第一次打补丁）
- 2026-10-28 11:22:36 —— 内置插件重新安装到 5.9.3 版本目录（`lastUpdated`）
- 2026-11-01 18:38 —— 应用运行，spill 内含覆盖层
- 2026-11-02 12:02:47 —— 15 份 welcomemode 副本被再次整体打补丁

`[推断]` 插件版本号变化会重建 `plugins\cache\...\<新版本>\prompt.tpl`（原始内容），旧目录里的补丁不会被继承 → 这是"升级后失效"的真实机制；同一版本内没有发现"检测到改动就回滚"的代码路径。

---

## ⑥ `managed-prompts\pojia-yijiantong` 是谁产生的：上游 pojia-yijiantong 工具，不是宿主

`[观测]` 全 asar（9893 条目）扫描：`managed-prompts` = **0 命中**，`pojia` = 0，`破甲` = 0，`unlock-v6` = 0。宿主代码里根本没有这个目录名。

`[观测]` 该目录内容自述身份（`passport.json`）：

```json
{"tool":"pojia-yijiantong","version":"8.18","target":"wb","root":"<USERPROFILE>\\.workbuddy",
 "mode":"policy","last_action":"apply","last_apply_time":"2026-10-22T17:37:05",
 "passphrase":"破甲自检","persona_hash":"831cf40e80ed","file_stamps":{},
 "install":"D:\\Program Files\\workbuddy","data_dir":"<USERPROFILE>\\.workbuddy"}
```

`selfcheck.txt` 给出的预期回复是 `自检成功｜项目完全免费｜官方交流群：1121243020｜GitHub：https://github.com/z91772524-ai/pojia-next/｜中转站推荐：https://pursueray.cn/`。

结论：这是**上游 pojia-next 系工具（pojia-yijiantong v8.18）自己的护照文件**，属历史遗留，不是 WorkBuddy 的功能。同时暴露一处**版本漂移**：当前 `pojia-wb.py` 的 `SIGNAL_REPLY = "破甲自检成功"`（`pojia-wb.py:81`）与该护照记录的口令回复不同，两者对不上属正常（不同工具、不同代）。

---

## ⑦ 逐层核对结论（对 pojia-wb.py 六层的判定）

| 层 | 判定 | 依据 |
|---|---|---|
| 1 安装侧 tpl | **准确、完整** | 13 个含政策 tpl 全被覆盖（①表 1-13），磁盘上 13 份都已是补丁态 |
| 2 `cli\product.json` | **准确但不完整** | 该文件确为 ACC 配置的源（④）；但 `node_modules\@genie\agent-harness\cli\product.json` 含同一政策且未打 |
| 3 命令闸门 | **准确、完整（就这两个函数而言）** | 两文件、各一处定义、均已注入（②）；但沙箱 / `clientSecurity` / 原生 `tsbx` 不在覆盖范围 |
| 4 `<data>\plugins\**\*.tpl` | **准确但噪音大** | 12 个 welcomemode 副本全覆盖；同时会扫入数百个 PPT 封面 `.tpl`（无害） |
| 5 删 `acc-product-config-v3.json` | **过时（无效）** | 该名已不存在（只剩工具自己的 `.unlockbak`）；现行按 PID+UUID 每进程重建，48 h 自清理（④） |
| 6 `memory\<uid>_memory.md` | **未生效 / 易被宿主覆盖** | 当前文件为 `Version: 30`、无 pojia 块（5,473 B，mtime 2026-10-21 12:34）；`.pojia.bak` 反而是 27,849 B 的旧档（10/16）。宿主内存服务在 `main/authority-snapshot.js`（`_memory.md` / `RAW_JSON_START` / `> Version: (\d+)` 解析，模块内偏移 115,805 与 118,110），会按自身 `version`/`storageVersion` 重写该文件 |

补充（JS 侧事实）：`main/database-factory.js` 只把 `<content_policy>` 当"要剔除的上下文标签"（偏移 ≈242,263），不存在数据库侧的第二份政策副本。

---

## 未完成 / 待查

1. **`EnableEmbeddedAsarIntegrityValidation` 是否校验 `.unpacked` 伴生文件**：只给到"fuse=enabled、REA 语义 enforced"+"16 处不符下应用仍在 11/01 正常运行"的实测组合；无法证明 Electron 对该类文件的具体校验边界（需要运行目标或读 Electron 源码，本次按只读约束未运行）。
2. **`RepairApp.exe` 的 `asar.scan` 精确语义**：只到字符串 + 清单结构推定（存在性检查）。CIL 未反编译——当前 REA 没有 C# 反编译器 provider（`import_managed_reconstruction` 只接收外部反编译产物），"哪些路径会被判 fatal"仍未知。
3. **`pojia-wb.py` 的 Ask 模式是否真存在**：`ASK_OLD`/`ASK_NEW` 定义在 148-149 行，其唯一真实靶点 `resources\templates\ask-mode-reminder.tpl:2` 在磁盘上**未被打补丁**（哈希与 asar 声明一致）。我在已读窗口（1-800、1080-1100、1240-1320 行）没找到调用点，但未做全文调用图确认 → 记为"疑似未实现/死代码"，不下断言。
4. **远端能否重下发提示词**：`ACC_PRODUCT_CONFIG` 链路支持由 endpoint 侧提供的产品配置合并（CLI 里 `ClientInternetEnviromentProductProvider`，priority = `CLIENT_SETTINGS_ENDPOINT+5`），但本机 7 份 spill 一致且都含覆盖层，**没有观测到远端推送 prompts 覆盖本地补丁**。该字段是否存在、什么条件触发：未知。
5. **`memory.md` 的 `Version: 999999` 是否真能阻止宿主更新**：宿主读 `^> Version: (\d+)` 的调用方（`tryReadExistingVersion` 的 caller）未定位，冲突解决策略未知；当前文件已被宿主压回 `Version: 30`，可作为"可被覆盖"的实测。
6. **`main/authority-snapshot.js`（814,150 B）与 `main/server.js`（3,726,608 B）只做定点取样**：两文件是超长单行 bundle，未做全量语义梳理；`memoryBlock` 注入点（server.js 14 处、authority-snapshot.js 15 处）只确认了内存档读写，未确认系统提示拼装顺序。
7. **REA 全量 JS 图未跑完**：`analyze_javascript_application` 对 181 MB asar 的全图分析两次超时（540 s / 900 s 内未返回），改为"自有 ASAR 解析 + 单模块定点分析（`source_paths`）"完成核对；模块级引用图（`trace_application_feature`）未建立。定位靠"全字节串扫描覆盖 9893 条目 + 单模块提取"，覆盖完整，但缺 REA 的图关系证据层。
8. **未覆盖的写入面**：`sessions\`、`traces\`、`skills\`、`storage\` 未做内容普查（不在六层靶点内，仅确认不是政策源）。
