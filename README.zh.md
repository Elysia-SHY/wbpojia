# WorkBuddy 破甲 CLI · wbpojia

[![CI](https://github.com/Elysia-SHY/wbpojia/actions/workflows/ci.yml/badge.svg)](https://github.com/Elysia-SHY/wbpojia/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/Elysia-SHY/wbpojia?display_name=tag)](https://github.com/Elysia-SHY/wbpojia/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)


[English (short)](README.md) · **中文全文（本页）**

`wbpojia.py` 是一个**单文件、零第三方依赖**的本地命令行工具，只针对 WorkBuddy 桌面客户端（Electron 壳）做两件事：

1. **提示词政策替换** —— 把客户端内置、界面上改不到的提示词模板里的 `<content_policy>` 区块整块换成操作者自己的那份，并在文末追加一层高优先级覆盖块与自证口令。
2. **命令闸门放行** —— 在 `checkBashSecurityWindows` / `checkPowerShellSecurity` 两个函数首行插入 `return{behavior:"allow"}`，让客户端自带的命令安全校验不再拦下本机命令。

工具只改 WorkBuddy 自己那几个文件的文本：不重排 JSON、不联网、不装依赖、不动无关文件。每处改动前都在原文件旁留 `.unlockbak` 备份，一条 `revert` 回到出厂状态。

---

## 1. 上游与派生关系

本仓库是 [**z91772524-ai/pojia-next**](https://github.com/z91772524-ai/pojia-next)（「破甲一键通」）的**命令行派生版**：只取其中的 WorkBuddy 补丁引擎，删掉图形界面、在线校验、广告位与其余目标平台，重写成可以直接在终端里跑的脚本。

上游以 **MIT 许可证**发布（`Copyright (c) 2026 z91772524-ai`），本仓库沿用 MIT 并保留上游版权声明，原文与核实过程见 [LICENSE](LICENSE)、[NOTICE](NOTICE) 与 [docs/upstream.md](docs/upstream.md)。

---

## 2. 六层靶点

`apply` 按下面六层就地改文本。层与层相互独立：某一层没找到只跳过并提示，不中断其余层。`status` 对六层逐层输出（有没有文件都出），`check` 逐层判定达标情况。

| 层 | 位置 | 做什么 |
|---|---|---|
| L1 | `<install>\resources\app.asar.unpacked\resources\**\*.tpl` | `<content_policy>` 整块替换成宽松版，文末追加 `<system_reminder>` 覆盖层 |
| L2 | `<install>\...\cli\product.json` 与 `<install>\...\node_modules\@genie\agent-harness\cli\product.json` | 同样的政策文本级替换（纯字符串操作，绝不 `json.loads/dumps` 重排）。两份都含 `<content_policy>`，漏掉 harness 那份等于没打 |
| L3 | `cli\dist` 与 `node_modules\@genie\agent-harness\cli\dist-server\**\*.js/.cjs/.mjs` | 两个闸门函数首行插入 `return{behavior:"allow"}`（老版在 `codebuddy.js`，新版在 `shared.cjs`，两套都认） |
| L4 | `<data>\plugins\**\*.tpl` | 同 L1（宿主按版本目录缓存这几份副本，不补会被它顶回去） |
| L5 | `<data>\cache\acc-product-config-v3-<pid>-<uuid>.json` | 逐份查有没有覆盖层，只删「从未打补丁的 `product.json` 重建出来的」那份（删前留 `.unlockbak`）。现行每进程一份、启动即重建、48 小时自清理 |
| L6 | `<data>\memory\<uid>_memory.md` 的 `memoryBlock` | 每轮自动注入的账号级云记忆（`Version 999999` + 只读 + 原档 `.pojia.bak`） |

`<install>` = 含 `WorkBuddy.exe` 的安装根；`<data>` = 含 `memory\` 或 `cache\` 的数据目录。L6 单独由 `cloudmem` 子命令管理（会覆盖账号记忆，`apply` 默认也带，`--no-cloudmem` 可跳过）。

---

## 3. 环境要求

- Windows 10/11（L3 的闸门与计划任务自愈只对 Windows 有意义）
- Python **3.9+**，只用标准库（**用 exe 就完全不需要 Python**；见 [4.1](#41-想要-exe不用装-python)）（`argparse` `ctypes` `hashlib` `json` `locale` `os` `re` `shutil` `subprocess` `sys` `tempfile` `time` `unicodedata`）
- 已安装 WorkBuddy 桌面客户端
- 一般不需要管理员权限；例外两处：写 `Program Files` 被拒时，以及 `guard-install`（计划任务以最高权限运行）

---

## 4. 安装与三个双击入口

### 4.1 想要 exe（不用装 Python）

从 Releases 下载 `wbpojia-v2.0-win64.zip`，里面有**两个** exe，用途不同：

| 文件 | 双击会发生什么 | 什么时候用 |
|---|---|---|
| `wbpojia-panel.exe` | **只开页面，没有黑框**（无窗口子系统） | 日常用这个 |
| `wbpojia.exe` | 开一个控制台窗口，里面打印面板地址，同时页面自动打开 | 想在窗口里看日志 / 按 Ctrl+C 停服务 / 当命令行工具用 |
| `破甲面板.bat` | 优先起 `wbpojia-panel.exe`；没有再回退 Python | 和上面等价，习惯 bat 就用这个 |
| `破甲.bat` / `破甲菜单.bat` / `自检.bat` | 命令行流程（一键破甲 / 数字菜单 / 环境自检） | 不想开浏览器时 |

**exe 一个参数都不带时会开面板**——这就是双击的行为。带参数时它仍然是老老实实的命令行工具（`wbpojia.exe check`、`wbpojia.exe apply --dry-run`……）。

### 4.2 面板长这样

![面板截图](docs/panel.png)

页面上能干的事：

- 顶部三条：安装目录 / 数据目录 / 人格来源与字数——自动探测的结果直接摊开，不用再猜。
- 「六层靶点」表：L1–L6 各自 `达标/总数` 与结论（绿=就绪、黄=部分、红=未生效）。每次操作后自动刷新。
- 九个按钮：破甲 / 强制重写 / 只改提示词 / 完全破甲 / 体检 / 状态详情 / 云记忆通道 / **还原成出厂**（二次确认）/ 环境自检。
- 「输出」区显示这次操作的完整控制台文本，带耗时与退出码。
- 「停止服务」：停掉面板。**这是无窗口版唯一的停止方式**，点它（或在控制台窗口按 Ctrl+C）。

几条实情：

- 只绑 `127.0.0.1`，地址里带一次性随机 token，别的本地网页打不开你的面板（错 token 一律 403）。不联网、不引用任何外部 JS/CSS。
- 重复双击不会开一堆：第二次发现已在跑，直接把浏览器指回原来那个页面。
- 当前地址记在 `_wb状态\panel.json`，服务停了自动删。
- 端口默认自动挑空闲的；想固定用 `wbpojia.exe panel --port 8765`。
- 面板在运行时点「破甲」这类操作，和命令行跑完全等价——它们走同一个 `main()`，输出被收进页面而已。

### 4.2 用 Python 跑（源码形态）

把这四个文件放在**同一个目录**里（建议固定，例如 `D:\tools\wbp\`）：

```text
wbpojia.py      引擎本体（唯一的 Python 文件）
破甲.bat         双击 = 一键破甲
破甲菜单.bat      双击 = 数字菜单
自检.bat         双击 = 环境自检 doctor
```

三个 bat 全部**零硬编码、自适应 Python**，查找顺序：

1. 环境变量 `WBPOJIA_PYTHON`（指向你的 python.exe）
2. `where py`
3. `where python`
4. `where python3`

（同目录若存在 `wbpojia.exe`，前面这四步整段跳过。）

找不到 Python 时不会一闪而过：窗口停住并打印

```text
  [!!] Python 3.9+ not found on PATH.
       Install it, or set WBPOJIA_PYTHON to your python.exe.
```

按一次回车退出（退出码 1）。这时装个 Python 3.9+，或先 `set WBPOJIA_PYTHON=D:\Python312\python.exe` 再双击。

| 入口 | 等价命令 | 说明 |
|---|---|---|
| `破甲.bat` | `onekey` = `apply --no-cloudmem` | 提示词 + 命令闸门，不碰账号云记忆 |
| `破甲菜单.bat` | `menu` | 数字菜单；可带参数直达，如 `破甲菜单.bat 3` 直接跑体检 |
| `自检.bat` | `doctor` | 只读环境自检，排障第一步 |

不想双击时，命令行等价写法：

```powershell
python wbpojia.py status            # 先看探测到没有
python wbpojia.py apply --dry-run   # 演练：一个字节都不写
python wbpojia.py apply             # 正式打补丁
```

> 文件名随意，本文档统一按 `wbpojia.py` 写；改名后把命令里的文件名换掉即可（bat 会跟着脚本所在目录找引擎）。

目录探测顺序：命令行 `-i/-d` → 状态文件里记住的路径 → 注册表卸载项 → 运行中的进程命令行 → 常见安装路径。都没命中就用 `-i` 显式指定，之后 `--save-path` 可以记住；`doctor` 会把探测过程逐条列出来。

---

## 5. 命令表

v2.0 的命令契约是 **10 个**：

| 命令 | 作用 |
|---|---|
| `status` | 只读：探测目录 + 六层逐层状态（`--all` 连没有政策块的文件一起列） |
| `check` | 只读体检：按层出「层 / 说明 / 达标 / 结论」四列表 + 问题清单；未达标退出码 `1` |
| `doctor` | **只读环境自检 —— 显示异常、找不到目录时的第一处置手段**（见第 12 节） |
| `apply` | 打补丁（L1–L5 + 默认 L6） |
| `revert` | 从 `.unlockbak` 还原全部改动 |
| `cloudmem` | 只刷新 L6 云记忆通道 |
| `guard-install` | 装两条计划任务，每 30 分钟自愈一次 |
| `guard-remove` | 卸掉自愈任务（含历史旧任务名） |
| `menu` | 数字菜单（8 行，见下表） |
| `onekey` | 一键：提示词 + 闸门，不碰云记忆 |

### 菜单（`menu` / `破甲菜单.bat`）

| 输入 | 项 | 等价命令 |
|---|---|---|
| `1` | 破甲（提示词 + 命令闸门） | `apply --no-cloudmem` |
| `2` | 只改提示词（不动闸门） | `apply --no-cloudmem --no-js` |
| `3` | 体检 | `check` |
| `4` | 还原成出厂 | `revert`（会先问一次确认） |
| `5` | 云记忆通道（会覆盖账号记忆，先备份） | `cloudmem` |
| `6` | 环境自检 | `doctor` |
| `7` | 状态详情 | `status --all` |
| `0` | 退出 | — |

### 参数

参数由 `argparse` 统一解析，是否生效取决于子命令：

| 参数 | 长写 | 说明 |
|---|---|---|
| `-i` | `--install-dir` | WorkBuddy 安装根（该目录下有 `WorkBuddy.exe`） |
| `-d` | `--data-dir` | 数据目录（该目录下有 `memory\` 或 `cache\`） |
| `-p` | `--persona` | 指定人格文件 |
| | `--dry-run` | 演练，不写盘 |
| | `--full` | 完全破甲：+ 网页过滤 + Ask 模式 + 文件保护中和 |
| | `--ask-mode` | 解除 Ask 模式只读限制 |
| | `--web-filter` | 解除网页内容过滤 |
| | `--nofileguard` | 中和个人文件保护 |
| | `--force` | 忽略「已是最新」判定，强制重写 |
| | `--restart` | 结束后重启 WorkBuddy |
| | `--keep-cache` | 不清运行时缓存 |
| | `--no-js` | 不碰命令闸门（L3 整层跳过） |
| | `--deep-js` | 额外扫描 `cli\dist` 与 `dist-server` 下所有脚本 |
| | `--no-cloudmem` | 不覆盖云记忆档案（保留你自己的账号记忆） |
| | `--clean-spill` | 清理 24 小时以前的会话快照 |
| | `--purge-spill` | 清理全部会话快照 |
| | `--quiet` | 只输出错误 |
| `-v` | `--verbose` | 逐个文件打印 |
| | `--pick` | `menu` 直接执行某一项（1–7） |
| | `--all` | `status` 列出全部文件（含无政策块的） |
| | `--save-path` | 把探测到的目录记进状态文件 |
| | `--port` | `panel` 监听端口（默认自动挑空闲端口） |
| | `--no-browser` | `panel` 起服务但不自动开浏览器 |
| | `--self-test` | `panel` 起服务后打一次自己的 API 再退出（CI 用） |

退出码：`0` 成功；`1` 失败或 `check` 未达标；`2` 未知命令。`panel` 是长驻命令，正常停止返回 `0`。

---

## 6. `status` 输出样例（v2.0 实跑）

六层每层都出一段标题，没文件的层也出（只是行数列 0）。下面是本机实跑后**删掉路径细节**的版本（`# 略` 为省略）：

```text
================================================================
  WorkBuddy 破甲  v2.0
  提示词政策替换 / 命令闸门放行 / 云记忆注入
================================================================

  安装目录  <install>              # 略：真实输出是探测到的绝对路径
  数据目录  <data>
  人格来源  内置默认（小码酱）  230 字
  人格哈希  44cdf46d423a

  共扫描 692 个文件，其中 26 个带 <content_policy>

-- L1 安装目录 templates 政策块 ----------------------------
  状态      类型  路径                                                              字节
  --------  ----  --------------------------------------------------------------  -----
  [已破甲]  tpl   <install>\resources\app.asar.unpacked\resources\plugins\...\prompt.tpl   34421
  # 略：同类 12 行（welcomemode 的 code/design/work + resources\templates 下 10 个）
   -    另有 6 个不含政策块的文件已折叠（--all 看全部）
   -    小计：13 个带政策块 / 6 个不含

-- L2 cli/product.json 政策块 ------------------------------
  状态      类型  路径                                                                    字节
  --------  ----  ----------------------------------------------------------------------  ------
  [已破甲]  json  <install>\resources\app.asar.unpacked\cli\product.json                 391278
  [已破甲]  json  <install>\...\node_modules\@genie\agent-harness\cli\product.json      357333
   -    小计：2 个带政策块 / 0 个不含

-- L3 命令闸门 JS ------------------------------------------
  状态        文件
  ----------  ---------------------
  [已开 2/2]  codebuddy-lite-wb.mjs
  [已开 2/2]  shared.cjs
   -    小计：2 个文件，2 个已放行

-- L4 数据目录 plugins 模板 --------------------------------
  状态      类型  路径                                                                        字节
  --------  ----  ------------------------------------------------------------------------  -----
  [已破甲]  tpl   <data>\plugins\cache\workbuddy-builtin\welcomemode-code\5.9.3-wb...\prompt.tpl    34421
  # 略：同类 11 行（5.8.3 / 5.9.0 / 5.9.2 / 5.9.3 四个版本目录 × code/design/work 三套模板）
   -    另有 660 个不含政策块的文件已折叠（--all 看全部）
   -    小计：12 个带政策块 / 660 个不含

-- L5 运行时缓存 -------------------------------------------
  状态    缓存文件                                         大小
  ------  ----------------------------------------------  ---------
  [正常]  acc-product-config-v3-13172-9ad5c109-....json   412442
  # 略：同类 6 行（每进程一份，全部从已打补丁的 product.json 重建，都带覆盖层）
   -    小计：6 份，0 份过时

-- L6 云记忆通道 -------------------------------------------
  状态    档案                    版本
  ------  --------------------  ----------
  [原档]  <uid>_memory.md        Version 30
```

状态词的读法：`[已破甲]` 已替换、`[已开 2/2]` 两个闸门函数都放行、`[ok]` 该层已处理、`[原档]` 云记忆还是原始档案（没注入）。

---

## 7. `check` 输出样例（v2.0 实跑）

`check` 只判达标情况，四列：**层 / 说明 / 达标 / 结论**，末尾附问题清单：

```text
-- 按层体检 ------------------------------------------------
  层  说明                       达标   结论
  --  -------------------------  -----  ------
  L1  安装目录 templates 政策块  13/13  就绪
  L2  cli/product.json 政策块    2/2    就绪
  L3  命令闸门 JS                2/2    就绪
  L4  数据目录 plugins 模板      12/12  就绪
  L5  运行时缓存                 6/6    就绪
  L6  云记忆通道                 0/1    未生效

-- 问题清单 ------------------------------------------------
  [!!]  [L6] 云记忆未注入（要这条通道就单独跑 cloudmem）  <uid>_memory.md

  [!!]  体检：36 个检查点，35 就绪，1 处待处理
```

上面是一次没跑 `cloudmem` 的真实结果：L1–L5 就绪、L6 未生效，退出码 `1`。补一条 `python wbpojia.py cloudmem` 之后再 `check`，L6 会变成 `1/1`、结论 `就绪`、退出码 `0`。

---

## 8. 验收方法

1. 打完补丁后 **完全退出 WorkBuddy**（含托盘图标）再重新打开——只关窗口不顶用。
2. 新建一个会话，单独发四个字：`破甲自检`。
3. 正确结果是**只回一行**：

   ```
   破甲自检成功
   ```

多一个字、换行解释、或回别的，说明 L1/L2/L4 没落到客户端实际加载的那份模板。先 `check` 看哪层未生效，再 `doctor` 看目录探测，最后确认是不是被客户端更新的版本目录顶掉了。

---

## 9. 还原 / 卸载 / 自愈

```powershell
python wbpojia.py revert         # 从 .unlockbak 还原；云记忆仅当当前档案是本工具注入过时才从 .pojia.bak 回滚
python wbpojia.py guard-remove   # 卸自愈任务（含历史旧任务名）
python wbpojia.py guard-install  # 装自愈任务：Hourly（每 30 分钟）+ Logon（登录时）
```

- 还原同样建议先加 `--dry-run` 看一眼。
- 卸载顺序：先 `guard-remove`，再 `revert`，最后删脚本目录（含 `_wb状态\`）。顺序反了会留着自愈任务空转。
- 两条自愈任务都以最高权限运行（`/RL HIGHEST`），所以 `guard-install` 要用**管理员终端**；只打补丁本身不需要管理员。

---

## 10. 人格文件

`-p` 指定；或把 `persona.md` / `my-prompt.txt` 放在脚本同目录。命中优先级：`-p` > `persona.md` > `my-prompt.txt` > 内置默认人格（小码酱，约 230 字）。人格正文会拼在政策块最前面，也就是「操作者自己的那份」。

参考格式见 [persona.example.md](persona.example.md)：复制成 `persona.md` 放在脚本旁边即可。文件里的 `<!-- -->` 注释在加载时会被剥掉，可以放心写说明。

---

## 11. 状态目录

脚本同目录下会生成 `_wb状态\`：

- `passport.json` —— 本次打补丁的版本、时间、人格哈希与文件清单
- `手动指定目录.json` —— `--save-path` 记住的 `-i/-d` 路径

这个目录属于本机状态（含本机绝对路径），**不要提交进仓库**（已写进 `.gitignore`）。

---

## 12. 排障

> 显示异常、找不到目录、行为对不上——**先跑 `python wbpojia.py doctor`**（或双击 `自检.bat`）。它只读，把运行环境、代码页、路径探测、安装/数据候选、写入权限、备份与闸门状态、云记忆档案一次列全，末尾给一句结论。

### 12.1 「有些东西显示不了」/ 满屏问号（v1.1 的老毛病）

根因不是字体，也不是客户端：v1.1 的 bat 里写死 `chcp 65001` + `PYTHONIOENCODING=utf-8`，可你直接在 **936（GBK）控制台**里敲 `python ...` 时，脚本吐出的 UTF-8 字节被控制台按 GBK 渲染——中文变问号，表格错位，看起来像「有些东西显示不了」。

v2.0 由引擎自己接管代码页，顺序是：读当前输出代码页 → 尝试 `SetConsoleOutputCP(65001)` → **切不动就退回控制台真实代码页**，并把 stdout/stderr 设成 `errors="replace"`。所以能切就是全 UTF-8；切不动也照样中文可读，不会因为一个字符整段崩掉。

`doctor` 的「运行环境」段给出三行判定：

```text
  控制台页  936            ← 打开时读到的真实代码页；显示 n/a 表示 stdout 是管道/重定向，不是控制台
  已切UTF8  是 / 否         ← 否 = 切 65001 失败，已退回本机代码页
  输出编码  utf-8 / cp936   ← 实际写 stdout 用的编码；看到 cp936 就是「退回」状态
```

读法：

- `控制台页 936` + `已切UTF8 否` + `输出编码 cp936` → 已经退到 GBK，中文可读，个别生僻字/框线字符可能缺字，不影响功能。
- `已切UTF8 是` + `输出编码 utf-8` → 正常状态。
- `控制台页 n/a` → 你在管道或重定向里跑（比如 `| Out-String`、CI 日志），此时没有控制台代码页可读，输出编码直接用 utf-8。
- 想强制回到 UTF-8：换 Windows Terminal，或先在窗口里 `chcp 65001` 再跑；`PYTHONUTF8=1` 只影响 Python 自身的文件/字符串编解码，控制台仍由上面那套接管。

### 12.2 找不到目录 / 提示「目录不对？」

先 `doctor`，它会列出 `安装目录候选` 与 `数据目录候选`，命中的那行标 `[ok]`。自动探测落空（装到非默认盘、便携版）时用 `-i`/`-d` 显式指定，再加 `--save-path` 记住：

```powershell
python wbpojia.py apply -i "<安装根>" -d "<数据目录>" --save-path
```

### 12.3 升级后失效

客户端更新会整目录替换：模板、`product.json` 被覆盖，闸门脚本也换新。重新 `apply` 即可；想省事就 `guard-install` 让它自己长回来。大版本升级后结构若变，先 `check` 看还有几层命中。

### 12.4 双击 bat 直接闪退

bat 找不到 Python 时本该停住并提示（见第 4 节）；如果你看到的是真闪退，说明 bat 被改过或不在与 `wbpojia.py` 同一目录。用 `cmd` 手动跑一遍 bat 看报错，或直接命令行执行 `python wbpojia.py doctor`。

### 12.5 `check` 报「闸门未生效」

`apply` 时加了 `--no-js`，或闸门函数在更新后换了文件名——用 `--deep-js` 再扫一遍；`doctor` 的「备份与闸门」段会告诉你找到几个闸门文件、各放行几分之几。

---

## 13. 已知边界与不覆盖的面（REA 逆向实测）

这一节全部来自对 WorkBuddy 客户端产物的静态核对，证据（文件 + 行号/字节偏移）在 [docs/rea-workbuddy.md](docs/rea-workbuddy.md)。写在这里是因为**有些东西这个工具确实管不了**，与其让你以为是 bug，不如直说。

**管不了的三道门**（都在 JS 补丁的射程之外）：

- `getDestructiveCommandWarning` —— 另一处危险命令提示，逻辑独立于两个 `checkXxxSecurity` 函数。
- `sandboxPermissionGateway` + `vendor\sandbox\5.9.5` 里的原生 `tsbx` —— 沙箱在**进程外**的原生模块里跑，改 JS 拦不到它。
- `clientSecurity → isSandboxForcedByManagedPolicy` —— 读 `ACC_PRODUCT_CONFIG_*` 的策略判定；企业托管策略把它打开时，沙箱强制生效。

如果你发现**命令还是被拦**，先确认是不是这三道门之一，而不是 L3 没打上（`doctor` 的「备份与闸门」段能告诉你有几个闸门文件、各放行几分之几）。

**宿主有校验，但不恢复内容**：

- `app.asar` 头里给 9893 个条目都声明了 SHA-256，`EnableEmbeddedAsarIntegrityValidation=enabled`；但本工具改的全是 `app.asar.unpacked\` 下的伴生文件，实测（16 处声明不符的状态下）客户端照常启动。
- `RepairApp.exe` 是本机唯一的预检/修复入口，它按 `install-manifest.json`（118 条纯路径、不含哈希）**只查文件在不在**，对 `app.asar.unpacked` 的处置是「要求重装」——不会把提示词内容改回去。
- 结论：没有内容级自愈。升级会覆盖，但覆盖 ≠ 校验失败。

**数据侧的自愈 = 按版本重建**：

- `installed_plugins.json` 指向 `plugins\cache\workbuddy-builtin\<mode>\<version>\`，**版本号一动就重建原始 tpl**。本机实测：10-27 升级 → 10-27 补 → 10-28 重装插件 → 11-02 再补。所以升级/重装插件之后要重跑 `apply`，或者开着 `guard-install`。
- L5 那个旧文件名 `acc-product-config-v3.json` 在当前版本**已经不存在**了；现行是 `acc-product-config-v3-<pid>-<uuid>.json`，每次启动从**已打补丁的** `cli\product.json` 重建，48 小时自清理。所以 v2.0 不再盲删缓存，而是逐份检查有没有覆盖层，只清「从未打补丁的 product.json 重建出来的」那一份。

**云记忆会打架**：`memory\<uid>_memory.md` 由宿主的 memory 服务按自己的 `version` 重写。本机实测它被压回过 `Version: 30`。所以 L6 是可选通道，默认 `onekey` / 菜单 1 都带 `--no-cloudmem`。另外 `revert` 只在「当前档案确实被本工具注入过」时才用 `.pojia.bak` 盖回去——防止拿一份很旧的备份覆盖宿主后来写的记忆。

**远端能否重下发提示词**：`ACC_PRODUCT_CONFIG` 链路支持 endpoint 侧合并产品配置，理论上存在远端覆盖本地补丁的路径；本机 7 份重建缓存的实测里没有观测到。这条记为未证实。

## 14. 法律与免责

- 本工具修改的是**你本机上第三方客户端的本地文件**。这样做可能违反该客户端的使用条款，并可能导致账号受限或文件被更新覆盖 —— **风险自负**。
- 软件按 MIT 许可证「**按原样**」提供，不附带任何明示或默示担保。作者与贡献者不对使用本工具造成的任何直接或间接后果负责，包括但不限于数据丢失、账号处置、服务中断。
- 请只对你拥有或已获授权处置的设备与软件使用。是否使用、如何使用、以及由此产生的一切后果，由使用者本人承担。
- 上游版权声明与许可要求见 [LICENSE](LICENSE)、[NOTICE](NOTICE)。

---

## 15. 许可

MIT。见 [LICENSE](LICENSE)。上游 [pojia-next](https://github.com/z91772524-ai/pojia-next) 同为 MIT，其版权声明已一并保留。

---

## 16. 发版流程（维护者）

打 tag 就会自动发 Release，不用手工传附件：

```bash
git tag -a v2.1.0 -m "wbpojia v2.1.0"
git push origin v2.1.0
```

`.github/workflows/release.yml` 在 tag 推上来之后会：

1. `build-exe.ps1` + `build-exe.ps1 -Panel` 各打一个 exe；
2. 两个 exe 都跑一遍 `tests/selftest.py`（不通过就不发）；
3. 打 `wbpojia-<tag>-win64.zip` + 生成 `SHA256SUMS.txt`；
4. `gh release create`（不存在时）或 `gh release upload --clobber`（已存在时），附件固定是：两个 exe、zip、校验和。

Release 正文：`docs/release-notes/<tag>.md` 存在就用它，否则用 GitHub 自动生成的 notes（提交与 PR 列表）。
想在已存在的 tag 上重发一次，去 Actions 手动跑 `Release` workflow 并填 tag 即可（会覆盖同名附件、不会动 tag）。
