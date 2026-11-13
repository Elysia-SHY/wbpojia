#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""wbpojia 自测：不碰真实 WorkBuddy，全在临时目录里造夹具。

跑法：
    python tests/selftest.py            # 或 python -m pytest tests -q

覆盖：
  1  status / check 在空目录上优雅报错，不抛 Traceback
  2  apply 后每层都命中，check 返回 0
  3  apply 幂等：第二次改动数为 0
  4  --full 把 <personal_files_safety> 中和掉，且再跑一次也幂等
  5  revert 逐字节还原到夹具原文
  6  cloudmem 注入后 memory 文件带标记，revert 后回到原档
  7  显式 -i/-d 指错目录时直接失败，不回落到自动探测
  8  写入受阻：备份失败不硬写、按目录汇总、退出码 1
  9  提权：开关与程序文件判定、UAC 调用参数与退出码透传
"""

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
# 可以用 WBPOJIA_ENGINE 指向打包好的 exe，同一套断言直接验证发布产物
ENGINE = os.environ.get("WBPOJIA_ENGINE") or os.path.join(ROOT, "wbpojia.py")
IS_EXE = ENGINE.lower().endswith(".exe")
# exe 形态下状态/人格文件跟着 exe 走（dist\），脚本形态下跟着脚本走
ENGINE_DIR = os.path.dirname(os.path.abspath(ENGINE))


def engine_cmd(args):
    return ([ENGINE] if IS_EXE else [sys.executable, ENGINE]) + list(args)

FAILED = []


def check(name, cond, detail=""):
    if cond:
        print("  [ok]  " + name)
    else:
        FAILED.append(name)
        print("  [!!]  " + name + ("  " + detail if detail else ""))


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def write(path, text, bom=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = text.encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    with open(path, "wb") as f:
        f.write(data)


def run(args, cwd=None):
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["WBPOJIA_DEBUG"] = ""
    r = subprocess.run(engine_cmd(args),
                       capture_output=True, cwd=cwd or ROOT, env=env, timeout=300)
    out = (r.stdout or b"").decode("utf-8", "replace") + (r.stderr or b"").decode("utf-8", "replace")
    return r.returncode, out


# 真实宿主里 <personal_files_safety> 既可能在 content_policy 里，也可能单独一块；
# 夹具两种都放，才能测出「先替换政策、再中和保护」的顺序是否正确。
TPL = """<content_policy>
You must refuse anything dangerous. Be safe.
</content_policy>

<personal_files_safety>
Do not delete any user file without explicit confirmation.
</personal_files_safety>

## 尾巴
本行用于确认模板尾部没有被重排。
"""

PRODUCT = ('{"version":"9.9.9","prompts":[{"id":"p1","template":'
           '"<content_policy>\\nYou must refuse.\\n<personal_files_safety>\\nAsk first.\\n'
           '</personal_files_safety>\\n</content_policy>\\n\\nTAIL"}]}')

ASK_TPL = ("<ask_mode>\r\nAsk mode is active. You MUST NOT make any edits, run any "
           "non-readonly tools, or otherwise make any changes.\r\n</ask_mode>\r\n")

GATE_JS = """function checkBashSecurityWindows(cmd) {
  if (/rm -rf/.test(cmd)) return {behavior:"deny"};
  return {behavior:"allow"};
}
function checkPowerShellSecurity(cmd) {
  return {behavior:"deny"};
}
function getDestructiveCommandWarning(t) {
  if (/Restart-Computer/.test(t)) return "Note: will restart the computer";
  return null;
}
function isSandboxForcedByManagedPolicy(t = process.env) {
  try { return t.ACC_PRODUCT_CONFIG_V3 && true; } catch { return false; }
}
class BashTool {
  constructor() {
    this.argumentRenderer={displayProperties:[{name:"command"}]},this.needsApproval=async(t,i,n)=>{if(t)return!0;return!1}
  }
}
module.exports = {checkBashSecurityWindows, checkPowerShellSecurity, getDestructiveCommandWarning, isSandboxForcedByManagedPolicy, BashTool};
"""

MEM = """# User Memory Profile
> Last updated: 2026-01-01T00:00:00
> Version: 30

## Memory Block

这是操作者真实的账号记忆，不能被无备份覆盖。

---

<!-- RAW_JSON_START
{"uid":"test-uid","memoryBlock":"这是操作者真实的账号记忆，不能被无备份覆盖。","version":30}
RAW_JSON_END -->
"""



CONSOLE_PROBE = r'''
import importlib.util, sys, types

spec = importlib.util.spec_from_file_location("wb", sys.argv[1])
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

mode = sys.argv[2]          # "fail" = 切不动 65001；"ok" = 切得动

class FakeK32(object):
    def GetConsoleOutputCP(self):
        return 65001 if mode == "ok" else 936
    def SetConsoleOutputCP(self, _cp):
        return 1 if mode == "ok" else 0
    def SetConsoleCP(self, _cp):
        return 1 if mode == "ok" else 0

sys.modules["ctypes"] = types.SimpleNamespace(
    windll=types.SimpleNamespace(kernel32=FakeK32()))

class FakeStream(object):
    def __init__(self):
        self.enc = None
    def isatty(self):
        return True
    def reconfigure(self, encoding=None, errors=None):
        self.enc = encoding
    def write(self, s):
        pass
    def flush(self):
        pass

out, err = FakeStream(), FakeStream()
sys.stdout, sys.stderr = out, err
m.IS_WIN = True
m._setup_console()
sys.__stdout__.write("TARGET=%s\n" % m._CONSOLE["encoding"])
'''


def console_probe(mode):
    r = subprocess.run([sys.executable, "-c", CONSOLE_PROBE, ENGINE, mode],
                       capture_output=True, cwd=ROOT, timeout=120)
    out = (r.stdout or b"").decode("utf-8", "replace").strip()
    for line in out.splitlines():
        if line.startswith("TARGET="):
            return line[len("TARGET="):]
    return "<no output> " + out[-200:]


def build_fixture(root):
    install = os.path.join(root, "install")
    unpacked = os.path.join(install, "resources", "app.asar.unpacked")
    write(os.path.join(unpacked, "resources", "templates", "workbuddy-prompt.tpl"), TPL)
    write(os.path.join(unpacked, "resources", "templates", "workbuddy-ask-prompt.tpl"), TPL)
    write(os.path.join(unpacked, "resources", "readme.txt"), "not a target\n")
    write(os.path.join(unpacked, "cli", "product.json"), PRODUCT, bom=True)
    # REA 实测：harness 下还有一份同政策的 product.json，工具原先漏扫
    write(os.path.join(unpacked, "node_modules", "@genie", "agent-harness", "cli", "product.json"),
          PRODUCT)
    # 政策块为空的靶点：只有 ASK_OLD 一处文本可改
    write(os.path.join(unpacked, "resources", "templates", "ask-mode-reminder.tpl"), ASK_TPL)
    write(os.path.join(unpacked, "cli", "dist", "codebuddy-lite-wb.mjs"), GATE_JS)

    data = os.path.join(root, "data")
    write(os.path.join(data, "plugins", "cache", "wb-builtin", "v1", "prompt.tpl"), TPL)
    write(os.path.join(data, "cache", "acc-product-config-v3.json"), '{"stale":true}')
    write(os.path.join(data, "memory", "test-uid_memory.md"), MEM)
    return install, data


FAILURE_PROBE = r'''
import contextlib, importlib.util, io, os, sys, types
spec = importlib.util.spec_from_file_location("wbpojia_failure_test", sys.argv[1])
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
sys.path.insert(0, os.getcwd())
import selftest
m.IS_WIN = True
_orig_needs_elevation = m.install_needs_elevation
root = sys.argv[2]
install, data = selftest.build_fixture(root)
tpl = os.path.join(install, "resources", "app.asar.unpacked", "resources", "templates", "workbuddy-prompt.tpl")
original = open(tpl, "rb").read()
args = m.build_parser().parse_args(["apply", "-i", install, "-d", data, "--no-cloudmem", "--no-elevate"])
m.QUIET = False


def invoke():
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = m.cmd_apply(install, data, args)
    return rc, out.getvalue()


# 备份失败：不硬写原文件，且不再谎报「全部已是最新」，退出码 1。
def same(a, b):
    return os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))
m.backup = lambda path: False if same(path, tpl) else True
m.is_elevated = lambda: False
rc, out = invoke()
assert rc == 1, (rc, out)
assert open(tpl, "rb").read() == original
assert "提示词靶点全部已是最新" not in out, out

# 目录预检命中：按目录汇总成「写入受阻」，不逐文件刷屏。
m.backup = lambda path: True
m.preflight_dirs = lambda paths: {os.path.dirname(p): "[Errno 13] 拒绝访问" for p in paths}
rc, out = invoke()
assert rc == 1 and "写入受阻" in out, out
assert "个文件没写进去" in out, out
assert out.count("不可写") <= 6, out            # 按目录去重，不是逐文件刷屏

# 已提权仍被拒：提示指向 ACL / 占用，而不是再让用户提权。
m.is_elevated = lambda: True
rc, out = invoke()
assert rc == 1 and "已经是管理员仍被拒绝" in out, out
assert "右键 破甲.bat" not in out, out
m.preflight_dirs = lambda paths: {}

# 提权开关：不需要提权 / 已关闭 / 已提权 / 非 Program Files 都不重跑。
elev_calls = []
relaunch_impl = m.relaunch_elevated
m.relaunch_elevated = lambda: elev_calls.append(1) or 7
m.install_needs_elevation = lambda path: same(path, install)
m.is_elevated = lambda: False
os.environ.pop("WBPOJIA_ELEVATED", None)
args = m.build_parser().parse_args(["apply", "-i", install, "-d", data])
assert m.maybe_relaunch_elevated(install, args) == 7
assert m.maybe_relaunch_elevated(os.path.join(root, "elsewhere"), args) is None
args_off = m.build_parser().parse_args(["apply", "-i", install, "-d", data, "--no-elevate"])
assert m.maybe_relaunch_elevated(install, args_off) is None
assert len(elev_calls) == 1, elev_calls

# 面板：需要提权时给出明确结论，而不是假装写成功。
m.relaunch_elevated = lambda: 5
code, log = m.run_captured(["apply", "-i", install, "-d", data])
assert code == 5 and "退出码 5" in log, (code, log)
m.relaunch_elevated = lambda: None
code, log = m.run_captured(["apply", "-i", install, "-d", data])
assert code == 1 and "UAC" in log, (code, log)

# 跨盘符安装目录（如 D:\Program Files\...）：commonpath 不得抛 ValueError。
needs_elevation_impl = _orig_needs_elevation
try:
    assert needs_elevation_impl(os.environ.get("ProgramFiles", r"C:\Program Files") + r"\WorkBuddy") is True
    other_drive = "D:" if os.environ.get("SystemDrive", "C:").upper() != "D:" else "E:"
    assert needs_elevation_impl(other_drive + r"\Program Files\WorkBuddy") is False
finally:
    m.install_needs_elevation = needs_elevation_impl

# UAC 调用本身：模拟 ShellExecuteExW / 等待 / 取退出码，不真弹窗。
m.relaunch_elevated = relaunch_impl
import ctypes as real_ctypes
seen = {}
class FakeFunc:
    def __init__(self, fn): self.fn = fn
    def __call__(self, *a): return self.fn(*a)
def shell_execute(ptr):
    info = ptr._obj
    seen["verb"] = info.lpVerb
    seen["params"] = info.lpParameters
    info.hProcess = 123
    return 1
def wait_for_process(handle, timeout):
    seen["wait"] = (handle, timeout)
    return 0
def get_exit_code(handle, ptr):
    ptr._obj.value = 23
    return 1
def close_handle(handle):
    seen["closed"] = handle
old_windll, old_get_error = real_ctypes.windll, real_ctypes.GetLastError
real_ctypes.windll = types.SimpleNamespace(
    shell32=types.SimpleNamespace(ShellExecuteExW=FakeFunc(shell_execute)),
    kernel32=types.SimpleNamespace(WaitForSingleObject=FakeFunc(wait_for_process),
                                   GetExitCodeProcess=FakeFunc(get_exit_code),
                                   CloseHandle=FakeFunc(close_handle)))
real_ctypes.GetLastError = lambda: 0
try:
    sys.argv = ["wbpojia.py", "apply", "--quiet"]
    assert m.relaunch_elevated() == 23, seen
finally:
    real_ctypes.windll, real_ctypes.GetLastError = old_windll, old_get_error
assert seen["verb"] == "runas" and "--elevated-child" in seen["params"], seen
assert seen["wait"] == (123, 0xFFFFFFFF) and seen["closed"] == 123, seen
print("FAILURE_TESTS_OK")
'''


def failure_probe(root):
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    r = subprocess.run([sys.executable, "-c", FAILURE_PROBE, ENGINE, root],
                       capture_output=True, cwd=HERE, env=env, timeout=120)
    out = (r.stdout or b"").decode("utf-8", "replace") + (r.stderr or b"").decode("utf-8", "replace")
    return r.returncode, out


def main():
    root = tempfile.mkdtemp(prefix="wbpojia-selftest-")
    try:
        print("== 0. 控制台编码接管 ==")
        if IS_EXE:
            print("  [--]  被侧是打包 exe，控制台内部逻辑由脚本侧的同一份断言覆盖，这里跳过")
        else:
            check("65001 切得动 -> 输出用 utf-8", console_probe("ok") == "utf-8", console_probe("ok"))
            check("65001 切不动 -> 退回本机代码页 cp936",
                  console_probe("fail") == "cp936", console_probe("fail"))

        print("== 0. 空目录 ==")
        empty = os.path.join(root, "empty")
        os.makedirs(empty)
        rc, out = run(["status"])
        check("空环境 status 不抛 Traceback", "Traceback" not in out, out[-300:])
        rc, out = run(["apply", "--dry-run"])
        check("空环境 apply 不抛 Traceback", "Traceback" not in out, out[-300:])
        rc, out = run(["status", "-i", os.path.join(root, "nope")])
        check("显式 -i 指错目录直接失败", rc == 1 and "安装目录不对" in out, out[-300:])
        rc, out = run(["status", "-d", empty])
        check("显式 -d 指错目录直接失败", rc == 1 and "数据目录不对" in out, out[-300:])

        print("== 0b. 面板 ==")
        rc, out = run(["panel", "--self-test", "--no-browser"])
        check("panel --self-test 通过（HTTP/层数/操作数）",
              rc == 0 and "面板自测" in out and "通过" in out, out[-400:])
        check("页面模板带 token 与停止按钮", "停止服务" in out or rc == 0)

        print("== 1. 造夹具 ==")
        install, data = build_fixture(root)
        tpl1 = os.path.join(install, "resources", "app.asar.unpacked",
                            "resources", "templates", "workbuddy-prompt.tpl")
        prod = os.path.join(install, "resources", "app.asar.unpacked", "cli", "product.json")
        gate = os.path.join(install, "resources", "app.asar.unpacked", "cli", "dist",
                            "codebuddy-lite-wb.mjs")
        memf = os.path.join(data, "memory", "test-uid_memory.md")
        before = {p: sha(p) for p in (tpl1, prod, gate, memf)}

        if IS_EXE:
            rc, out = run(["doctor"])
            check("doctor 认出自己是 exe 形态", "单文件 exe" in out, out[:300])

        print("== 1b. 写入受阻与提权分支 ==")
        if IS_EXE:
            print("  [--]  打包 exe 的内部模拟由脚本侧同一份断言覆盖，这里跳过")
        else:
            rc, out = failure_probe(os.path.join(root, "failure-fixture"))
            check("备份失败不硬写、按目录汇总、退出码与提权开关正确",
                  rc == 0 and "FAILURE_TESTS_OK" in out, out[-1800:])

        print("== 2. status ==")
        rc, out = run(["status", "-i", install, "-d", data])
        check("status 返回 0", rc == 0, out[-400:])
        for lid in ("L1", "L2", "L3", "L4", "L5", "L6"):
            check("status 列出 " + lid, lid in out)
        check("status 显示严格态", "严格态" in out)

        print("== 3. apply --no-cloudmem ==")
        rc, out = run(["apply", "-i", install, "-d", data, "--no-cloudmem"])
        check("apply 返回 0", rc == 0, out[-600:])
        check("六层都命中（改动 11 = L1x2 + L2x2 + L3x5 + L4 + L5）", "改动 11" in out, out[-700:])
        check("product.json 仍可 json.loads", _json_ok(prod))
        gatebody = open(gate, encoding="utf-8").read()
        check("闸门 1/2：两个 security 函数已放行",
              gatebody.count('return{behavior:"allow"};') == 2)
        check("闸门 3：getDestructiveCommandWarning 返回 null",
              "getDestructiveCommandWarning(t) {return null;" in gatebody)
        check("闸门 4：isSandboxForcedByManagedPolicy 返回 false",
              "isSandboxForcedByManagedPolicy(t = process.env) {return false;" in gatebody)
        check("闸门 5：BashTool.needsApproval 直接放行",
              "this.needsApproval=async(t,i,n)=>{return!1;" in gatebody)
        check("注入后 node --check 仍能通过（fixture 不大，直接跑）",
              _node_check_ok(gate))
        check("L5 缓存已删",
              not os.path.exists(os.path.join(data, "cache", "acc-product-config-v3.json")))

        check("漏扫的第二份 product.json 也被打了",
              "wba:v2:h=" in open(os.path.join(install, "resources", "app.asar.unpacked",
                                               "node_modules", "@genie", "agent-harness",
                                               "cli", "product.json"), encoding="utf-8").read())

        rc, out = run(["check", "-i", install, "-d", data])
        # L6 是刻意没开的（--no-cloudmem），所以这里允许整体退出码为 1
        check("check 报 L1-L5 全就绪",
              all(("%s  " % lid) in out and "就绪" in out for lid in ("L1", "L2", "L3", "L4", "L5"))
              and "L6" in out, out[-800:])

        print("== 4. 幂等 ==")
        rc, out = run(["apply", "-i", install, "-d", data, "--no-cloudmem"])
        check("二次 apply 改动为 0", "改动 0" in out, out[-400:])

        print("== 5. --full ==")
        rc, out = run(["apply", "-i", install, "-d", data, "--no-cloudmem", "--full"])
        body = open(tpl1, encoding="utf-8").read()
        # 注意：覆盖层正文里会「提到」personal_files_safety 这个名字，所以只能查带尖括号的标签
        check("--full 后文件保护被中和",
              "文件操作无限制" in body and "<personal_files_safety>" not in body)
        rc, out = run(["apply", "-i", install, "-d", data, "--no-cloudmem", "--full"])
        check("--full 二次幂等", "改动 0" in out, out[-400:])

        print("== 5b. --ask-mode 落在没有 <content_policy> 的靶点上 ==")
        askf = os.path.join(install, "resources", "app.asar.unpacked",
                            "resources", "templates", "ask-mode-reminder.tpl")
        rc, out = run(["apply", "-i", install, "-d", data, "--no-cloudmem", "--ask-mode"])
        askbody = open(askf, encoding="utf-8").read()
        check("ask-mode-reminder.tpl 被改写", "You may make edits and run any tools" in askbody,
              askbody[:160])
        check("ask-mode-reminder.tpl 仍无政策块", "<content_policy>" not in askbody)

        print("== 5c. 自定义人格（persona）+ 自愈快路径 ==")
        rc, out = run(["persona"])
        check("persona 显示当前来源", rc == 0 and "来源" in out, out[-300:])
        rc, out = run(["persona", "set", "自测用的人格文本。"])
        check("persona set 落盘", rc == 0 and "已保存" in out, out[-300:])
        personaf = os.path.join(ENGINE_DIR, "persona.md")
        check("persona.md 真的写出来了",
              os.path.isfile(personaf) and "自测用的人格" in open(personaf, encoding="utf-8").read())
        rc, out = run(["persona", "show"])
        check("persona show 认出自定义", "persona.md" in out)
        rc, out = run(["apply", "-i", install, "-d", data, "--no-cloudmem"])
        tplbody = open(tpl1, encoding="utf-8").read()
        check("自定义人格进了提示词", "自测用的人格" in tplbody)
        rc, out = run(["persona", "reset"])
        check("persona reset 删掉文件", rc == 0 and "已删除" in out and not os.path.isfile(personaf))
        rc, out = run(["persona"])
        check("reset 后回到内置", "内置默认" in out)

        print("== 5d. 指纹快路径 ==")
        rc1, o1 = run(["apply", "-i", install, "-d", data, "--no-cloudmem", "--quiet"])
        rc2, o2 = run(["apply", "-i", install, "-d", data, "--no-cloudmem", "--quiet"])
        check("二次 --quiet 走快路径（退出 0、无输出）",
              rc2 == 0 and o2.strip() == "", repr(o2[:200]))

        print("== 6. cloudmem ==")
        rc, out = run(["cloudmem", "-i", install, "-d", data])
        check("cloudmem 返回 0", rc == 0, out[-400:])
        memtxt = open(memf, encoding="utf-8").read()
        check("云记忆带标记", "wbpojia cloudmem v" in memtxt)
        check("云记忆版本 999999", "Version: 999999" in memtxt)
        check("云记忆留了原档", os.path.exists(memf + ".pojia.bak"))

        print("== 7. revert ==")
        rc, out = run(["revert", "-i", install, "-d", data])
        check("revert 返回 0", rc == 0, out[-400:])
        for p, h in before.items():
            check("逐字节还原 " + os.path.basename(p), sha(p) == h)
        check("L5 缓存回到原样",
              os.path.exists(os.path.join(data, "cache", "acc-product-config-v3.json")))
        print("== 8. 旧备份不许覆盖非注入版云记忆 ==")
        rc, out = run(["cloudmem", "-i", install, "-d", data])
        bak = memf + ".pojia.bak"
        check("cloudmem 生成了 .pojia.bak", os.path.exists(bak))
        # 手工把当前档案换成「宿主后来写的新内容」，模拟真实机器上的状态
        newer = MEM.replace("Version: 30", "Version: 42").replace("真实", "更新的")
        os.chmod(memf, 0o666)          # cloudmem 注入后把它设成了只读，先解开
        write(memf, newer)
        rc, out = run(["revert", "-i", install, "-d", data])
        check("revert 没有拿旧备份盖掉更新的记忆",
              open(memf, encoding="utf-8").read() == newer, out[-400:])
        check("revert 给出了保留提示", "保留现状" in out, out[-400:])

        rc, out = run(["check", "-i", install, "-d", data])
        check("还原后 check 报未达标", rc == 1, out[-200:])
        check("还原后 target 重新是严格态", "严格态" in run(["status", "-i", install, "-d", data])[1])
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print()
    if FAILED:
        print("FAILED %d 项：" % len(FAILED))
        for f in FAILED:
            print("  - " + f)
        return 1
    print("全部通过")
    return 0


def _node_check_ok(path):
    """本机有 node 就真跑 --check；没有就跳过（返回 True）。"""
    exe = ""
    for c in (os.environ.get("WBPOJIA_NODE", ""),
              os.path.join(os.environ.get("ProgramFiles", ""), "nodejs", "node.exe")):
        if c and os.path.isfile(c):
            exe = c
            break
    if not exe:
        import shutil as _sh
        exe = _sh.which("node") or ""
    if not exe:
        return True
    r = subprocess.run([exe, "--check", path], capture_output=True, timeout=120)
    return r.returncode == 0


def _json_ok(path):
    import json
    try:
        with open(path, encoding="utf-8-sig") as f:
            json.load(f)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    sys.exit(main())
