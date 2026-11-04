# 兼容性：打得到什么、打不到什么

这份文档只讲边界：v2.1 的补丁覆盖 WorkBuddy 的哪些判定点、哪些判定点在 JS 补丁射程之外、客户端升级或重装之后会怎样。
证据全部来自对客户端产物的静态核对，文件、偏移与清单在 [rea-workbuddy.md](rea-workbuddy.md)；这里只做结论汇总，两边数字不一致时以那份为准。

核对基准：

| 项 | 值 |
|---|---|
| 客户端 | WorkBuddy（Electron / PE x64），安装清单 `appVersion 5.9.3` |
| 数据目录 | `%USERPROFILE%\.workbuddy` |
| 本工具 | wbpojia v2.1（命令契约 11 个子命令） |
| 本机实测 | 两个闸门文件均为 `已开 5/5`；`check` 的 L3 行 `2/2 就绪` |

---

## 1. 打得到的判定点（v2.1）

命令闸门这一层（L3）在 v2.1 从 2 处扩到 4 处 `function` 闸门，另外补一处属性式注入：

| # | 名称 | 注入语句 | 作用 | v2.1 |
|---|---|---|---|---|
| 1 | `checkBashSecurityWindows` | `return{behavior:"allow"};` | Bash 命令安全校验 | 原有 |
| 2 | `checkPowerShellSecurity` | `return{behavior:"allow"};` | PowerShell 命令安全校验 | 原有 |
| 3 | `getDestructiveCommandWarning` | `return null;` | 危险命令提示文案 | 新增 |
| 4 | `isSandboxForcedByManagedPolicy` | `return false;` | 托管策略强制开沙箱 | 新增 |
| 5 | `BashTool.needsApproval` | `return!1;` | **真正会弹审批的地方** | 新增 |

前 4 条都是 `function <名字>(...)` 形式，每个 dist 文件里各命中一处；第 5 条锚在 Bash 工具的 `this.argumentRenderer={displayProperties:[{name:"command"}]}` 之后，是对 tool 类属性的注入，不是函数声明。所以 `status` 的 L3 行按文件统计命中条数：本机两个文件都是 `[已开 5/5]`（旧版产物里若没有那个 tool 类，就是 `4/4`）。

两个落点（旧版 `cli\dist`，新版 `dist-server`）都要打，缺一个就等于没打：

| 文件 | 大小 | `needsApproval` 字符偏移 | `applyCommandGate` 首次调用偏移 |
|---|---|---|---|
| `<install>\resources\app.asar.unpacked\cli\dist\codebuddy-lite-wb.mjs` | 9,880,112 B | 5,884,518 | 5,884,884 |
| `<install>\...\node_modules\@genie\agent-harness\cli\dist-server\shared.cjs` | 21,141,865 B | 8,048,861 | 8,049,238 |

第 5 条为什么重要：`BashTool.needsApproval` 自己又判了一遍，先看 `checkBashSecurityWindows(command).behavior`，再走 `sandboxPermissionGateway.shouldUseSandboxPath`，然后拿 `applyCommandGate` 的返回值决定要不要弹审批。只打两个 `checkXxxSecurity` 时，这条分支仍然可能把命令送进审批；v2.1 直接让它返回 `false`。

注入后还有一道语法安全网：改完 JS 立刻 `node --check`，不通过就放弃这个文件（不写盘、继续处理其余文件）；找不到 node 时退化成括号配平检查。`--no-verify` 可以跳过这道检查，不建议，跳过之后写坏了要自己拿 `.unlockbak` 还原。

---

## 2. 改不动的两处

这两处并非遗漏，而是字符串级 JS 补丁在该层面无效。列出以便在「命令仍被拦截」时直接排查，而非重复检查 L3。

### 2.1 原生沙箱 `cli\vendor\sandbox\5.9.5\`

- 内容：`tsbx.dll`、`sandbox-cli.exe`、`sandbox-center.exe`、`betterleaks.exe`。
- 它跑在进程外：JS 侧通过 `sandboxPermissionGateway.shouldUseSandboxPath(...)` 决定要不要把命令交给它（`codebuddy-lite-wb.mjs` 5,884,700 附近的调用链），真正的隔离在原生进程里做。
- 所以：改 `.mjs` / `.cjs` 里的字符串管不到它。`isSandboxForcedByManagedPolicy` 那条只关掉「托管策略强制开沙箱」的判定，不等于拆掉沙箱本身。
- v2.1 的做法是绕开入口而不是改沙箱：`BashTool.needsApproval` 首行返回 `false`，命令不会再走到需要沙箱决策的那条分支。

### 2.2 `applyCommandGate` 服务

- 形如 `p.applyCommandGate(this, t, i, n, "permission", resolveArgs)`，`p` 是从容器里取的权限服务（`n_.ContainerUtil.get(nr.FJ)`）。
- 它在 `BashTool.needsApproval` 里被调用两次：沙箱分支一次（mode `"hooks"`），常规分支一次（mode `"permission"`）。返回值是审批决定，`undefined` 表示「本服务不表态，继续走后面的判定」。
- 本工具不去改这个方法体：它是一个服务层方法，改它要动的是类成员定义而不是函数声明，收益低而破坏面大。取的是同一个效果，`needsApproval` 首行 `return!1` 之后，这两处调用不可达。
- 换句话说：闸门是「在门口拦掉」，不是「把服务拆了」。真要拆，属于另一个层面的活，不在这个工具的契约里。

---

## 3. 宿主侧的校验与自愈

有校验，但不恢复内容，这是能放心用字符串补丁的前提：

- `app.asar` 头里给 9893 个条目都声明了 SHA-256 + 4 MiB block，`EnableEmbeddedAsarIntegrityValidation` 是 enabled；本工具改的全是 `app.asar.unpacked\` 下的伴生文件。实测 16 处声明不符的状态下，客户端照常启动。
- `RepairApp.exe` 按 `install-manifest.json`（118 条纯路径、不含哈希）只查文件在不在，对 `app.asar.unpacked` 的处置是「要求重装」，不会把提示词内容改回去。
- 结论：没有内容级自愈。升级会覆盖，但覆盖 ≠ 校验失败。

数据侧的自愈是按版本重建：`installed_plugins.json` 指向 `plugins\cache\workbuddy-builtin\<mode>\<version>\`，版本号一动就重建原始 `.tpl`；`acc-product-config-v3-<pid>-<uuid>.json` 每次启动从已打补丁的 `cli\product.json` 重建，48 小时自清理。

---

## 4. 场景 × 结果

| 场景 | 现象 | 处置 |
|---|---|---|
| 客户端小版本更新 | 模板、`product.json`、闸门脚本被覆盖，`check` 掉层 | 重跑 `apply`；开着 `guard-install` 的话等它下一轮（每 30 分钟） |
| 插件重装 / `installed_plugins.json` 版本号变化 | 数据侧 `plugins` 里的 `prompt.tpl` 回到原始 | 同上；L4 会重新打 |
| 重启客户端 | L5 缓存重建（从已打补丁的 product.json） | 不用管，`status` 的 L5 显示「正常」即可 |
| 命令还是被拦 | 多半个是沙箱或服务层，不是 L3 没打上 | 先 `wbpojia status` 看 L3 是不是全 `已开`（含 `BashTool.needsApproval` 那一行），再对照第 2 节 |
| 企业托管策略 | `clientSecurity` 由产品配置下发，v2.1 只让 `isSandboxForcedByManagedPolicy` 返回 false | 策略侧仍可能通过别的入口生效，本工具不保证 |
| 网页内容过滤 / Ask 模式 | 属条件层（`--web-filter` / `--ask-mode` / `--full`） | 不带参数时不动这两处 |
| 升级后 `guard` 到点跑 | 指纹没变就秒退，不再扫整个目录 | 想强制重扫：`wbpojia apply --force` |

---

## 5. 未验证 / 已知空白

- 远端重下发：`ACC_PRODUCT_CONFIG` 链路支持 endpoint 侧合并产品配置，理论上存在远端覆盖本地补丁的路径；7 份重建缓存的实测里没有观测到。记为未证实。
- 其它客户端版本：上面所有偏移都按 `appVersion 5.9.3` 的两个 dist 文件量出来的；本机数据目录里 5.8.3 / 5.9.0 / 5.9.2 / 5.9.3 四套 `prompt.tpl` 都打得上（L4 的 12 个文件），但那只是模板，**旧版本的闸门 JS 没有逐一核对**。大版本改结构时先 `check` 看还有几层命中，再看 `status` 的 L3 明细。
- **原生沙箱的独立行为**：`tsbx` 自己的策略文件、它拦什么不拦什么，没有在这里展开；v2.1 的策略是绕开调用入口，不是与它对抗。
- **非 Windows**：闸门、计划任务、面板都不适用，引擎会直接以退出码 2 结束。
