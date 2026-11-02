# 更新日志

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循语义化版本。

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
