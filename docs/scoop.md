# 用 Scoop 装 wbpojia

清单本体：[scoop/wbpojia.json](scoop/wbpojia.json)。清单装的是 Release 里的 `wbpojia-v<版本>-win64.zip`，解出来两个 exe：

| 文件 | 用途 |
|---|---|
| `wbpojia-panel.exe` | 只开面板，没有控制台窗口（`scoop` 的 shim 会把它伪装成 `wbpojia-panel`） |
| `wbpojia.exe` | 命令行引擎，也是双击会开面板的那个；`scoop` 里直接敲 `wbpojia` |

前提：Windows 10/11 x64 + 已装 [Scoop](https://scoop.sh)。清单没有 `depends`，不装 Python、不装运行时。

---

## 1. 装

### 1.1 直接从仓库清单装（推荐，不用建 bucket）

```powershell
scoop install https://raw.githubusercontent.com/Elysia-SHY/wbpojia/main/docs/scoop/wbpojia.json
```

Scoop 会把它当作一个临时 bucket 里的应用处理，照样能进 `scoop list`、能升级（升级时重新拉同一份清单）。

### 1.2 建本地 bucket（要改清单、离线安装时用）

```powershell
git clone https://github.com/Elysia-SHY/wbpojia.git D:\tools\wbpojia
scoop bucket add wbpojia D:\tools\wbpojia\docs\scoop
scoop install wbpojia
```

`scoop bucket add` 也接受本地目录，只要那个目录根下就是 `wbpojia.json`（本仓库的 `docs\scoop\` 正是这个布局）。路径换成你自己的克隆位置。

装完可以验证一下：

```powershell
wbpojia --version      # wbpojia 2.1
scoop which wbpojia    # 指向 scoop\shims\wbpojia.exe
```

---

## 2. 装完先干什么

Scoop 只负责把 exe 放到盘上，不会替你打补丁。补丁要显式跑一次：

```powershell
wbpojia doctor            # 只读自检：目录探测、写入权限、闸门与备份状态
wbpojia status            # 六层逐层状态（L3 会逐条列出闸门名与「已开/未开」）
wbpojia apply --dry-run   # 演练：一个字节都不写
wbpojia apply             # 正式打补丁
wbpojia check             # 体检，未达标退出码 1
```

打完要**完全退出 WorkBuddy（含托盘图标）**再开，然后新建会话发四个字 `破甲自检`，正确回复只有一行 `破甲自检成功`。

不开命令行也行：`wbpojia-panel`（或 `wbpojia` 不带参数）会起本地面板，页面上有「人格」卡片和九个按钮，和命令行等价。

---

## 3. 升级

```powershell
scoop update           # 更新 scoop 自己和所有 bucket
scoop update wbpojia   # 只更它
```

升级之后**必须重跑一次 `wbpojia apply`**：新版本目录里的 exe 不认识旧的补丁状态，而且 WorkBuddy 客户端自己更新也会把模板顶回去。想省事就 `wbpojia guard-install` 装两条计划任务（每 30 分钟 + 登录时，需要管理员终端），它会在客户端换版本后自己补。

两个跟升级有关的实情：

- `scoop` 升级是**换掉整个 `apps\wbpojia\current\` 目录**。引擎的状态目录 `_wb状态\`（记住的 `-i/-d` 路径、护照、人格哈希）跟 exe 同目录，所以升级后这些会回到初始状态，重新跑 `wbpojia apply -i "<安装根>" -d "<数据目录>" --save-path` 一次即可。
- 人格文件同理：`wbpojia persona set "<文本>"` 把内容写到 exe 同目录的 `persona.md`（scoop 目录用户可写，所以写在那里，而不是 `%LOCALAPPDATA%`，那个落点只在 exe 放不进安装目录时才用）。升级会替换它。三种保法任选：

  - **给清单加 `persist`**（省事，推荐）：

    ```json
    "persist": ["persona.md", "_wb状态"]
    ```

    改完重新 `scoop uninstall wbpojia` + `scoop install wbpojia` 生效；之后升级就不会动这两样。
  - 升级后重跑一次 `wbpojia persona set "<文本>"`（文本自己留一份）。
  - 或者每次显式带上 `-p`：`wbpojia apply -p D:\tools\my-persona.md`，`--persona` 优先级最高且不落盘。

---

## 4. 卸载

顺序别反，先摘自愈任务，再还原文件，最后才是 scoop：

```powershell
wbpojia guard-remove     # 删两条计划任务（含历史旧任务名），需要管理员终端
wbpojia revert           # 从 .unlockbak 还原全部改动
scoop uninstall wbpojia
scoop bucket rm wbpojia  # 只有建过本地 bucket 才需要
```

反了会怎样：先 `scoop uninstall` 把 exe 删了，计划任务还在，它到点就去找一个不存在的路径空转；补丁文件则留在客户端里没人还原。

想要干净到底，再手动删这两个目录（Scoop 不管它们，因为它们是引擎运行时生成的）：

- `_wb状态\`（在 exe 同目录；exe 被 scoop 删掉后一般随目录一起没了）
- `%LOCALAPPDATA%\wbpojia\`（exe 放不进 Program Files 时的落点，以及状态目录的退路）

---

## 5. 维护清单

### 5.1 填 hash

清单里的 `hash` 目前是占位符 `<待填：release 后更新>`：**tag 打好、zip 传上去之后**才能算。两种填法：

```powershell
# 从 Release 附件算（curl 要写全路径，别落在当前目录）
curl.exe -L -o "$env:TEMP\wbpojia-v2.1.0-win64.zip" "https://github.com/Elysia-SHY/wbpojia/releases/download/v2.1.0/wbpojia-v2.1.0-win64.zip"
(Get-FileHash -Algorithm SHA256 -LiteralPath "$env:TEMP\wbpojia-v2.1.0-win64.zip").Hash.ToLower()
```

偷懒的话不用下载：Release 附件里的 `SHA256SUMS.txt` 就有 zip 那一行，直接抄进来即可（同一份哈希）。

粘进 `docs/scoop/wbpojia.json` 的 `architecture.64bit.hash`，提交。占位符没换掉的话 `scoop install` 会报 hash check failed。

### 5.2 版本 bump

只需要改这几处（`autoupdate` 里的 `$version` 不用动）：

- `version`
- `architecture.64bit.url` 里的两处 `2.1.0`
- `architecture.64bit.hash`

`checkver` 用 GitHub releases 取最新 tag（本仓库 tag 形如 `v2.1.0`，Scoop 会自动去掉 `v`），`autoupdate` 负责自动拼新 URL，建了 bucket 之后 `scoop update` 就能跟上，不需要手改。

### 5.3 换 sha 之后它说缓存还是旧的

```powershell
scoop cache rm wbpojia
```

Scoop 会拿缓存里的旧 zip 去对新的 hash，对不上就报错；清掉缓存重下即可。
