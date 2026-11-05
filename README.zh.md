# WorkBuddy 破甲

WorkBuddy 桌面客户端的提示词与命令校验补丁工具。

修改范围：

1. 提示词模板中的 `<content_policy>` 段，替换后不再向回答附加限制。
2. 命令安全校验函数，改为直接返回放行，不再触发审批。

Python 单文件实现，仅依赖标准库，无网络访问。Release 提供不依赖 Python 的 exe 构建。

派生自 [pojia-next](https://github.com/z91772524-ai/pojia-next)（MIT）。仅保留 WorkBuddy 分支的补丁引擎，未包含 GUI、在线校验、广告位及其他目标平台。

## 修改的文件

六层互相独立。某一层未命中时跳过，不影响其余层。

| | 位置 | 操作 |
|---|---|---|
| L1 | `<install>\resources\app.asar.unpacked\resources\**\*.tpl` | 替换 `<content_policy>` 段，末尾追加 `<system_reminder>` |
| L2 | `cli\product.json`、`node_modules\@genie\agent-harness\cli\product.json` | 文本级替换。两份文件均含政策段 |
| L3 | `cli\dist\codebuddy-lite-wb.mjs`、`dist-server\shared.cjs` | 五个校验函数首行插入放行语句 |
| L4 | `<data>\plugins\**\*.tpl` | 同 L1。客户端按版本目录缓存副本，未补会被覆盖 |
| L5 | `<data>\cache\acc-product-config-v3-<pid>-<uuid>.json` | 每次启动由 L2 重建。仅清理由旧配置重建的文件 |
| L6 | `<data>\memory\<uid>_memory.md` | 账号级云记忆，每轮注入上下文。默认不处理 |

`<install>` 为包含 `WorkBuddy.exe` 的目录，`<data>` 为 `C:\Users\<用户>\.workbuddy`。

L3 涉及的五个函数：

- `checkBashSecurityWindows`、`checkPowerShellSecurity`：首行插入 `return{behavior:"allow"};`
- `BashTool.needsApproval`：首行插入 `return!1;`
- `isSandboxForcedByManagedPolicy`：改为 `return false;`
- `getDestructiveCommandWarning`：改为 `return null;`

JS 写入前执行 `node --check` 语法校验，未通过则跳过该文件。环境无 node 时退化为括号配平检查。

两处不受补丁影响，见 [docs/compatibility.md](docs/compatibility.md)：原生沙箱 `cli\vendor\sandbox\5.9.5\tsbx`（进程外运行），以及 `applyCommandGate` 服务。命令仍被拦截时先排查这两处。

## 安装

### exe

从 [Releases](https://github.com/Elysia-SHY/wbpojia/releases/latest) 下载 `wbpojia-v2.3.0-win64.zip`，解压至任意目录。

包内容：

```
wbpojia-panel.exe    面板，无控制台窗口
wbpojia.exe          命令行入口；无参数时启动面板
破甲.bat              onekey
破甲菜单.bat          数字菜单
破甲面板.bat          启动面板
自检.bat              doctor
README.zh.md  LICENSE  NOTICE  persona.example.md  wbpojia.py  build-exe.ps1
```

四个 bat 优先调用同目录的 `wbpojia.exe`，不存在时回退到 Python。

### Scoop

```powershell
scoop install https://raw.githubusercontent.com/Elysia-SHY/wbpojia/main/docs/scoop/wbpojia.json
```

详见 [docs/scoop.md](docs/scoop.md)。

### 源码

需要 Python 3.9 或以上，无第三方依赖。

```powershell
python wbpojia.py status
python wbpojia.py apply --dry-run
python wbpojia.py apply
```

## 使用

### 面板

执行 `wbpojia-panel.exe`，或不带参数执行 `wbpojia`，启动本地面板并打开浏览器。

![面板](docs/panel.png)

面板显示安装目录、数据目录、当前人格与六层达标数量，提供九个操作按钮、输出区和人格编辑框。服务仅绑定 `127.0.0.1`，地址携带一次性随机 token，其他页面无法访问。

重复启动时复用已有实例，浏览器指向当前页面。面板由页面上的「停止服务」按钮停止；控制台版本亦可按 Ctrl+C。

### 命令行

```powershell
wbpojia status            # 六层状态
wbpojia check             # 体检，未达标返回 1
wbpojia doctor            # 环境自检
wbpojia apply             # 打补丁
wbpojia apply --dry-run   # 演练，不写盘
wbpojia revert            # 由 .unlockbak 还原
wbpojia cloudmem          # 仅刷新 L6
wbpojia guard-install     # 注册两条计划任务
wbpojia persona           # 查看当前人格
```

常用参数：

| 参数 | 说明 |
|---|---|
| `-i` / `-d` | 指定安装目录 / 数据目录 |
| `-p` | 指定人格文件 |
| `--dry-run` | 演练，不写盘 |
| `--force` | 忽略「已是最新」，强制重写 |
| `--full` | 追加网页过滤、解除 Ask 模式、中和文件保护 |
| `--no-js` | 仅处理提示词，跳过 L3 |
| `--deep-js` | 额外扫描 `cli\dist` 与 `dist-server` 下所有脚本 |
| `--no-cloudmem` | 跳过 L6 |
| `--restart` | 补丁后重启 WorkBuddy |
| `--no-elevate` | 不自动请求 UAC；只以当前权限执行 |
| `--no-verify` | 跳过 JS 语法校验 |
| `-v` / `--quiet` | 逐文件输出 / 仅输出错误 |

`persona` 参数见下节。`panel` 另有 `--port`、`--no-browser`、`--self-test`。

退出码：0 成功；1 执行失败或 `check` 未达标；2 命令无效。

安装在 `%ProgramFiles%` 时，`apply` / `onekey` 会自动通过 Windows UAC 重新运行原命令，并等待、透传管理员进程的退出码。无需预先右键管理员运行；`--no-elevate` 可禁用该行为。备份失败时会跳过对应文件，不会无备份改写；写入受阻会汇总成一段并返回 1，全部失败时不再打印自证。若管理员进程仍报 `Errno 13`，请检查安装目录的安全权限、所有者及安全软件拦截，而不是重复提权。

## 自定义系统提示词

无需编辑文件。两个入口：

- 面板的人格编辑框，点击「保存并应用」后立即执行一次 `apply`。
- 命令行：

```powershell
wbpojia persona set "提示词内容"
wbpojia persona set --file D:\path\persona.md
wbpojia persona reset
```

`wbpojia persona` 输出当前来源、字数、文件位置与正文全文。

存储位置为 exe 同目录的 `persona.md`；该目录不可写时（例如安装于 `Program Files`）改用 `%LOCALAPPDATA%\wbpojia\persona.md`。

读取优先级：`--persona` 参数、同目录 `persona.md`、同目录 `my-prompt.txt`、状态目录 `persona.md`、内置默认人格。修改人格后需执行一次 `apply` 才写入客户端，通过面板「保存并应用」时自动完成。

## 验收

完全退出 WorkBuddy（含托盘进程）后重新启动，新建会话，单独发送：

```
破甲自检
```

预期返回单行 `破甲自检成功`。返回其他内容表示模板未写入客户端实际加载的文件，执行 `check` 确认未生效的层。

## 还原与卸载

```powershell
wbpojia revert
```

每处修改前均在原文件旁生成 `.unlockbak`，L6 的云记忆生成 `.pojia.bak`。还原即回拷这些备份。

已注册计划任务时按以下顺序：

```powershell
wbpojia guard-remove    # 先删除任务，否则每 30 分钟重新打上
wbpojia revert
```

随后删除程序目录与 `_wb状态\`。

## 计划任务

```powershell
wbpojia guard-install
```

注册两条任务：`WorkBuddyUnlockV6_Hourly` 每 30 分钟执行，`WorkBuddyUnlockV6_Logon` 登录时执行。两条均以最高权限运行，需在管理员终端中执行注册。

任务启动后先比对指纹（若干目录的 mtime 与条目数、`installed_plugins.json` 与 `product.json` 的哈希、引擎版本），无变化则直接退出。客户端升级或插件重装导致指纹变化时才执行完整扫描。

## 故障排查

执行 `wbpojia doctor`，或双击 `自检.bat`。输出包含运行环境、代码页、目录探测过程、写入权限、备份与闸门状态，末尾给出结论。

**控制台乱码**

v1.1 的问题：直接调用 python 时 UTF-8 字节按 GBK 渲染。v2.1 由引擎接管代码页，无法切换到 65001 时回退至本机代码页。`doctor` 输出的「控制台页 / 已切UTF8 / 输出编码」三行反映当前状态。

**目录未找到**

`doctor` 列出全部候选目录并标注命中项。安装在非默认路径或便携版环境下，用 `-i` / `-d` 指定，并加 `--save-path` 记录。

**客户端升级后失效**

客户端升级会整目录替换。重新执行 `apply`，或启用 `guard-install` 自动重打。

**命令仍被拦截**

参见「修改的文件」末尾列出的两处不可达位置。

## 已知限制

- 仅支持 Windows。
- L6 云记忆由客户端 memory 服务按自身版本号重写，本机实测曾被写回 `Version: 30`，故默认不处理。
- 原生沙箱与 `applyCommandGate` 不受补丁影响，见 [docs/compatibility.md](docs/compatibility.md)。
- exe 未做代码签名，首次运行可能被 SmartScreen 拦截。

## 许可

MIT。上游 [pojia-next](https://github.com/z91772524-ai/pojia-next) 的版权声明 `Copyright (c) 2026 z91772524-ai` 依 MIT 要求原样保留于 [LICENSE](LICENSE)。取用与未取用范围见 [NOTICE](NOTICE)。

本工具修改本机第三方客户端的本地文件。软件按原样提供，不附带任何担保。
