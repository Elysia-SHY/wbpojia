# WorkBuddy 破甲 CLI · wbpojia

[![CI](https://github.com/Elysia-SHY/wbpojia/actions/workflows/ci.yml/badge.svg)](https://github.com/Elysia-SHY/wbpojia/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/Elysia-SHY/wbpojia?display_name=tag)](https://github.com/Elysia-SHY/wbpojia/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)


**English (short)** · full document in Chinese: [README.zh.md](README.zh.md) ← 中文全文（主文档）

A single-file, zero-dependency command line tool for the **WorkBuddy desktop client** (Electron). It does exactly three things, locally, on your own machine:

1. **Prompt policy replacement** — swaps the `<content_policy>` block inside WorkBuddy's built-in prompt templates (the ones the UI does not expose) for the operator's own version, then appends a high-priority overlay block and a self-check passphrase.
2. **Command gate release** — injects a release statement as the first line of 4 gate functions (`checkBashSecurityWindows`, `checkPowerShellSecurity`, `getDestructiveCommandWarning`, `isSandboxForcedByManagedPolicy`) and makes `BashTool.needsApproval` return `false` outright, then syntax-checks the patched JS with `node --check` before writing it.
3. **Custom system prompt (v2.1)** — write your own persona text from the `persona` subcommand or the panel's persona card; no hand-editing files.

No network access, no third-party packages, no GUI. Every modified file is backed up as `*.unlockbak` next to the original, and a single `revert` restores factory state.

> This is a **CLI-only derivative** of [z91772524-ai/pojia-next](https://github.com/z91772524-ai/pojia-next) ("破甲一键通"): the WorkBuddy patch engine only, with the GUI, online checks, ad slots and other target platforms dropped. Upstream is MIT (`Copyright (c) 2026 z91772524-ai`); this repository keeps that notice. See [LICENSE](LICENSE), [NOTICE](NOTICE), [docs/upstream.md](docs/upstream.md).

---

## Six patch layers

`status` prints all six layers whether or not a layer has files; `check` judges each layer.

| # | Target | Action |
|---|---|---|
| L1 | `<install>\resources\app.asar.unpacked\resources\**\*.tpl` | replace `<content_policy>` wholesale, append a `<system_reminder>` overlay |
| L2 | `<install>\resources\app.asar.unpacked\cli\product.json` | same policy text replacement (pure string edit, JSON never re-serialized) |
| L3 | `cli\dist` and `node_modules\@genie\agent-harness\cli\dist-server\**\*.js/.cjs/.mjs` | release 4 gate functions (`checkXxxSecurity` → `return{behavior:"allow"}`, `getDestructiveCommandWarning` → `return null`, `isSandboxForcedByManagedPolicy` → `return false`) plus `BashTool.needsApproval` → `return!1` (old `codebuddy.js`, new `shared.cjs`, both patched) |
| L4 | `<data>\plugins\**\*.tpl` | same as L1 (per-version cached copies; otherwise they override) |
| L5 | `<data>\cache\acc-product-config-v3*.json` | delete, so the client rebuilds it from the patched `product.json` |
| L6 | `<data>\memory\<uid>_memory.md` (`memoryBlock`) | per-turn account cloud memory injection (`Version 999999`, read-only, original kept as `.pojia.bak`) |

`<install>` = install root containing `WorkBuddy.exe`; `<data>` = data root containing `memory\` or `cache\`.

---

## Requirements

- Windows 10/11 (L3 and the self-heal scheduled tasks are Windows-specific)
- **Python 3.9+**, standard library only
- WorkBuddy desktop client installed
- No admin rights in general — exceptions: writing under `Program Files` when denied, and `guard-install` (tasks run with highest privileges)

## Installation — three double-click entry points

Keep these four files in the same folder (or install the release zip / use Scoop, see below):

```text
wbpojia.py      the engine (the only Python file)
破甲.bat         double-click = one-key patch      (onekey = apply --no-cloudmem)
破甲菜单.bat      double-click = numeric menu        (menu; takes an argument, e.g. 破甲菜单.bat 3)
自检.bat         double-click = environment check    (doctor)
```

All three launchers are path-free and Python-adaptive; lookup order is `WBPOJIA_PYTHON` → `where py` → `where python` → `where python3`. When no interpreter is found the window stays open and prints `[!!] Python 3.9+ not found on PATH.` plus the hint to set `WBPOJIA_PYTHON`, then exits with code 1.

Command line equivalent:

```powershell
python wbpojia.py status             # read-only: probe dirs, per-layer state
python wbpojia.py apply --dry-run    # nothing is written
python wbpojia.py apply              # patch
python wbpojia.py check              # per-layer verdicts (exit code 1 when not ready)
python wbpojia.py doctor             # environment self-check (read-only) — first stop when anything looks off
python wbpojia.py revert             # restore from *.unlockbak
```

Prebuilt exes come from the release zip `wbpojia-v2.1.0-win64.zip` (`wbpojia.exe` + `wbpojia-panel.exe`). Scoop users can skip the download entirely:

```powershell
scoop install https://raw.githubusercontent.com/Elysia-SHY/wbpojia/main/docs/scoop/wbpojia.json
```

Scoop only puts the exes on disk — it does not patch anything for you; run `wbpojia doctor` then `wbpojia apply` once. Install/upgrade/uninstall and hash maintenance: [docs/scoop.md](docs/scoop.md).

## Commands (11 + `panel`)

`status` · `check` · `doctor` · `apply` · `revert` · `cloudmem` · `guard-install` · `guard-remove` · `menu` · `onekey` · `persona` — plus the long-running `panel`, so `--help` lists 12.

`doctor` is not optional: it is the first thing to run for "nothing shows up" and "target not found".

Menu entries: `1` patch (`apply --no-cloudmem`) · `2` prompts only · `3` check · `4` revert (asks for confirmation) · `5` cloud memory · `6` doctor · `7` status --all · `0` quit.

## Options

`-i`/`-d` (install dir / data dir) · `-p` (persona file) · `--dry-run` · `--full` · `--ask-mode` · `--web-filter` · `--nofileguard` · `--force` · `--restart` · `--keep-cache` · `--no-js` · `--deep-js` · `--no-cloudmem` · `--clean-spill` · `--purge-spill` · `--quiet` · `-v` · `--pick` · `--all` · `--save-path` · `--file` / `--reset` (persona) · `--no-verify` (skip the `node --check` gate)

Exit codes: `0` ok, `1` failed / `check` not ready, `2` unknown command. Full semantics: [README.zh.md](README.zh.md).

## Custom system prompt (v2.1)

```powershell
wbpojia persona                                  # show source, length, save path, usage
wbpojia persona set "you are ..."                # set directly
wbpojia persona set --file D:\path\persona.md    # or read from a file
wbpojia persona reset                            # drop it, back to the built-in 小码酱
```

The panel has the same thing as a card: a textarea plus **save / save & apply / restore built-in**. "Save & apply" writes the persona file and runs one `apply` for you. Resolution order: `--persona` > `persona.md` next to the script/exe > `my-prompt.txt` next to it > `_wb状态\persona.md` > built-in. Steps 2 and 4 depend on writability: an exe under `Program Files` falls back to `%LOCALAPPDATA%\wbpojia\persona.md`, and `persona` reports the path it actually uses.

## `status` sample (real v2.1 run, paths trimmed)

```text
  共扫描 692 个文件，其中 26 个带 <content_policy>

-- L1 安装目录 templates 政策块 ----------------------------
  状态      类型  路径                                    字节
  [已破甲]  tpl   <install>\resources\...\prompt.tpl      34421
  # 略：同类 12 行
   -    小计：13 个带政策块 / 6 个不含

-- L2 cli/product.json 政策块 ------------------------------
  [已破甲]  json  <install>\resources\app.asar.unpacked\cli\product.json  391280

-- L3 命令闸门 JS ------------------------------------------
  [已开 5/5]  codebuddy-lite-wb.mjs
  [已开 5/5]  shared.cjs
  [ok]  BashTool.needsApproval           已开
  # + one line per gate; N/M = released / matched in that file (5 in v2.1, 2 in v2.0)

-- L4 数据目录 plugins 模板 --------------------------------
  [已破甲]  tpl   <data>\plugins\cache\...\prompt.tpl   34421
  # 略：同类 11 行
   -    小计：12 个带政策块 / 660 个不含

-- L5 运行时缓存 -------------------------------------------
  [ok]  运行时缓存已清

-- L6 云记忆通道 -------------------------------------------
  [原档]  <uid>_memory.md        Version 30
```

## Verification

Fully quit WorkBuddy (including the tray icon), start a **new** session, send the four characters `破甲自检`. The only correct reply is a single line:

```
破甲自检成功
```

Anything else means L1/L2/L4 did not land in the template the client actually loads — run `check`, then `doctor`.

## Self-heal (optional)

`guard-install` registers two scheduled tasks (`WorkBuddyUnlockV6_Hourly` every 30 minutes, `WorkBuddyUnlockV6_Logon` at logon) that re-apply the patch after a client update. Both run with `/RL HIGHEST`, so that step needs an elevated shell; patching itself does not. `guard-remove` deletes them, including legacy task names.

Since v2.1 those tasks run `apply --quiet`, which compares a fingerprint first — target directory mtimes and entry counts, hashes of `installed_plugins.json` and `cli\product.json`, plus the engine version — and exits immediately when nothing changed instead of rescanning all 692 files. `apply --force` skips that fast path.

## Uninstall

```powershell
python wbpojia.py guard-remove
python wbpojia.py revert
```

Then delete the script directory, including the generated `_wb状态\` state folder. Remove the scheduled tasks first, otherwise the patch comes back.

## Troubleshooting

Run `python wbpojia.py doctor` (or double-click `自检.bat`) first — it is read-only and prints the runtime environment, console codepage, every path candidate, write permissions, backup and gate state, then a one-line verdict.

**"Some things won't display" / garbage text.** In v1.1 the launchers hardcoded `chcp 65001` + `PYTHONIOENCODING=utf-8`, so a plain 936 (GBK) console rendered the engine's UTF-8 bytes as GBK. v2.0 takes over the codepage itself: read the current output codepage → try `SetConsoleOutputCP(65001)` → if that fails, fall back to the console's real codepage and reconfigure stdout/stderr with `errors="replace"`. Read the three `doctor` lines as:

```text
  控制台页  936     ← codepage read at startup; "n/a" means stdout is a pipe/redirect, not a console
  已切UTF8  是/否    ← 否 = switching to 65001 failed, fell back to the native codepage
  输出编码  utf-8   ← encoding actually used for stdout; cp936 means "fallback active"
```

**Target not found** — `doctor` lists install/data candidates and marks the hit with `[ok]`; pass `-i`/`-d` explicitly and add `--save-path` to remember.

**Broken after an update** — updates replace the whole tree; re-run `apply`, or keep `guard-install` active.

## Disclaimer

This tool modifies local files of a third-party desktop client on your own machine. Doing so may violate that client's terms of service and may cause account restriction or the files to be overwritten by an update — **at your own risk**. The software is provided "AS IS" under the MIT license, without warranty of any kind; authors and contributors accept no liability for any direct or indirect consequence of its use. Use it only on devices and software you own or are authorized to administer.

## Known limits (from static reverse engineering)

Two enforcement points sit **outside** this tool's reach, both verified in the shipped client
(evidence: [docs/rea-workbuddy.md](docs/rea-workbuddy.md)):

- The native sandbox under `cli\vendor\sandbox\5.9.5\` (`tsbx.dll`, `sandbox-cli.exe`,
  `sandbox-center.exe`) — it runs out-of-process, so string patches in the JS bundles cannot reach
  it. v2.1 works around the entry point instead: `BashTool.needsApproval` returns `false` on its
  first line, so a command never reaches the branch that asks the sandbox.
- The `applyCommandGate` service — `BashTool.needsApproval` calls it twice for an approval verdict.
  The tool leaves the service implementation alone; after the early `return` both call sites are
  unreachable.

`getDestructiveCommandWarning` and `clientSecurity → isSandboxForcedByManagedPolicy` used to be on
this list in v2.0 — **v2.1 patches both** (`return null` / `return false`). Full boundary notes:
[docs/compatibility.md](docs/compatibility.md).

The host validates but does not restore: `app.asar` declares SHA-256 for 9893 entries and
`EnableEmbeddedAsarIntegrityValidation` is enabled, yet every file this tool rewrites lives under
`app.asar.unpacked\`, and the client starts normally with 16 mismatched entries. `RepairApp.exe`
only checks file existence against a hash-free 118-path manifest.

Data-side "self-healing" is version-based rebuilds: `installed_plugins.json` pins a versioned
directory, so a client update or plugin reinstall re-materialises pristine `.tpl` files — re-run
`apply` (or keep `guard-install` enabled) afterwards.

## License

MIT — see [LICENSE](LICENSE). Upstream [pojia-next](https://github.com/z91772524-ai/pojia-next) is MIT as well; its copyright notice is retained.

---

## Releasing

Push a tag — CI does the rest:

```bash
git tag -a v2.1.0 -m "wbpojia v2.1.0" && git push origin v2.1.0
```

`.github/workflows/release.yml` builds both exes, runs `tests/selftest.py` against each, packs `wbpojia-<tag>-win64.zip` with `SHA256SUMS.txt`, and creates or updates the GitHub Release. Release notes come from `docs/release-notes/<tag>.md` when present, otherwise from GitHub's generated notes.
