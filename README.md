# wbpojia

Patch tool for the WorkBuddy desktop client.

Modifies two areas:

1. The `<content_policy>` block in its prompt templates.
2. A set of command-security functions, so Bash and PowerShell calls return allow without an approval prompt.

Single-file Python, standard library only, no network access. Prebuilt exe releases available.

Derived from [pojia-next](https://github.com/z91772524-ai/pojia-next) (MIT). Only the WorkBuddy patch engine was taken; GUI, online checks, ads and other target platforms are excluded.

Chinese documentation: [README.zh.md](README.zh.md).

## Files patched

Six independent layers. A layer that does not match is skipped.

| | Path | Action |
|---|---|---|
| L1 | `<install>\resources\app.asar.unpacked\resources\**\*.tpl` | Replace the `<content_policy>` block, append a `<system_reminder>` |
| L2 | `cli\product.json`, `node_modules\@genie\agent-harness\cli\product.json` | Text replacement. Both files carry the policy block |
| L3 | `cli\dist\codebuddy-lite-wb.mjs`, `dist-server\shared.cjs` | Insert an allow statement at the top of five check functions |
| L4 | `<data>\plugins\**\*.tpl` | Same as L1. The client caches a copy per version directory |
| L5 | `<data>\cache\acc-product-config-v3-<pid>-<uuid>.json` | Rebuilt from L2 on every launch. Only stale files are removed |
| L6 | `<data>\memory\<uid>_memory.md` | Account-level cloud memory. Not modified by default |

`<install>` is the directory containing `WorkBuddy.exe`; `<data>` is `C:\Users\<user>\.workbuddy`.

Every JS write is preceded by `node --check` on the full file; a failure skips that file. Without node the check degrades to bracket balancing.

Two enforcement points are outside patch range: the native sandbox (`cli\vendor\sandbox\5.9.5\tsbx`, out of process) and the `applyCommandGate` service. See [docs/compatibility.md](docs/compatibility.md).

## Installation

Download `wbpojia-v2.3.0-win64.zip` from [Releases](https://github.com/Elysia-SHY/wbpojia/releases/latest) and extract it.

Or:

```powershell
scoop install https://raw.githubusercontent.com/Elysia-SHY/wbpojia/main/docs/scoop/wbpojia.json
```

Or run from source with Python 3.9 or later, no third-party packages:

```powershell
python wbpojia.py doctor
python wbpojia.py apply --dry-run
python wbpojia.py apply
```

## Usage

```powershell
wbpojia status        # per-layer state
wbpojia check         # health check, exit 1 when not satisfied
wbpojia doctor        # environment self-check
wbpojia apply         # patch
wbpojia revert        # restore from .unlockbak
wbpojia persona       # show the current system prompt
```

`wbpojia-panel.exe`, or `wbpojia` without arguments, starts a local panel bound to `127.0.0.1`: layer states, action buttons, a system-prompt editor and a log pane.

Exit codes: 0 success, 1 failure or unsatisfied `check`, 2 invalid command.

When WorkBuddy is installed under `%ProgramFiles%`, `apply` / `onekey` re-launches itself through UAC, waits for the elevated process and forwards its exit code. `--no-elevate` disables that. A failed backup skips the file instead of overwriting it unbacked, and any write or read-back failure ends with "未完成" and exit code 1.

## Custom system prompt

Use the panel editor with "保存并应用", or:

```powershell
wbpojia persona set "prompt text"
wbpojia persona set --file D:\path\persona.md
wbpojia persona reset
```

Stored as `persona.md` next to the executable, or under `%LOCALAPPDATA%\wbpojia\` when that directory is not writable. Run `apply` afterwards for it to reach the client.

## Verification

Quit WorkBuddy completely, including the tray process, restart it, open a new session and send `破甲自检`. The expected reply is the single line `破甲自检成功`.

## License

MIT. The upstream copyright notice is retained verbatim in [LICENSE](LICENSE); scope of what was and was not taken is in [NOTICE](NOTICE).

Provided as is, without warranty.
