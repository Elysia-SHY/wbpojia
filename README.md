# wbpojia

Patches two things in the WorkBuddy desktop client:

1. The `<content_policy>` block inside its prompt templates, so it stops adding its own restrictions to answers.
2. A handful of command-security functions, so Bash and PowerShell commands run without an approval prompt.

Single-file Python, standard library only, no network. Prebuilt exes are in [Releases](https://github.com/Elysia-SHY/wbpojia/releases/latest) if you don't want Python on the machine.

Derived from [pojia-next](https://github.com/z91772524-ai/pojia-next) (MIT). Only the WorkBuddy patch engine was taken; the GUI, online checks, ads and other target platforms were dropped.

Chinese docs: [README.zh.md](README.zh.md).

## What gets patched

Six layers. Each one is independent — a layer that isn't found is skipped.

| | Path | Action |
|---|---|---|
| L1 | `<install>\resources\app.asar.unpacked\resources\**\*.tpl` | Replace the `<content_policy>` block, append a `<system_reminder>` |
| L2 | `cli\product.json` and `node_modules\@genie\agent-harness\cli\product.json` | Same text replacement. Both files carry the policy block |
| L3 | `cli\dist\codebuddy-lite-wb.mjs`, `dist-server\shared.cjs` | Insert one allow-statement at the top of five check functions |
| L4 | `<data>\plugins\**\*.tpl` | Same as L1. The client caches a copy per version directory |
| L5 | `<data>\cache\acc-product-config-v3-<pid>-<uuid>.json` | Rebuilt from L2 on every launch. Only stale ones get removed |
| L6 | `<data>\memory\<uid>_memory.md` | Account-level cloud memory. Optional, untouched by default |

`<install>` is the folder holding `WorkBuddy.exe`; `<data>` is `C:\Users\<you>\.workbuddy`.

Every JS patch is followed by `node --check` on the whole file. If it fails, the file isn't written. Without node installed it falls back to a bracket-balance check.

Two things this can't reach — the native sandbox (`cli\vendor\sandbox\5.9.5\tsbx`, out of process) and the `applyCommandGate` service. Listed in [docs/compatibility.md](docs/compatibility.md).

## Install

Grab `wbpojia-v2.1.0-win64.zip` from Releases and unpack it anywhere. Or:

```powershell
scoop install https://raw.githubusercontent.com/Elysia-SHY/wbpojia/main/docs/scoop/wbpojia.json
```

Or run from source with Python 3.9+, no packages needed:

```powershell
python wbpojia.py doctor
python wbpojia.py apply --dry-run
python wbpojia.py apply
```

## Usage

```powershell
wbpojia status        # per-layer state
wbpojia check         # health check, exit 1 if anything is off
wbpojia doctor        # environment self-check; run this first when something's wrong
wbpojia apply         # patch
wbpojia revert        # restore from .unlockbak
wbpojia persona       # show the current system prompt
```

Double-clicking `wbpojia-panel.exe` opens a local panel on `127.0.0.1` — layer states, buttons for each action, a text box for the system prompt, and a log pane. No arguments to `wbpojia.exe` does the same thing.

Exit codes: 0 ok, 1 failed or `check` failing, 2 bad command.

After patching, quit WorkBuddy completely (tray icon included), reopen it, and send `破甲自检` in a fresh session. It should reply with exactly one line: `破甲自检成功`.

## Custom system prompt

Either use the box in the panel, or:

```powershell
wbpojia persona set "your prompt"
wbpojia persona set --file D:\path\persona.md
wbpojia persona reset
```

Saved next to the executable as `persona.md`, or under `%LOCALAPPDATA%\wbpojia\` when that folder isn't writable. Run `apply` afterwards for it to take effect.

## License

MIT. Upstream copyright line kept verbatim in [LICENSE](LICENSE); what was and wasn't taken is in [NOTICE](NOTICE).

This modifies local files of a third-party client on your own machine. Provided as is, no warranty.
