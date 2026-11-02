# build-exe.ps1 -- 把 wbpojia.py 打成单文件 exe（PyInstaller）
#
#   .\build-exe.ps1                 # 控制台版：dist\wbpojia.exe（CLI + 双击开面板）
#   .\build-exe.ps1 -Panel          # 无窗口版：dist\wbpojia-panel.exe（双击只开页面，没有黑框）
#   .\build-exe.ps1 -Onedir         # 目录版：启动快，无临时解包
#   .\build-exe.ps1 -Python C:\Python312\python.exe
#
# 依赖只装进本目录的 .venv-build\，不污染系统 Python。

[CmdletBinding()]
param(
    [string]$Python = "",
    [switch]$Onedir,
    [switch]$Panel,
    [string]$OutDir = "dist",
    [string]$Icon = ""
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

if (-not $Python) {
    if ($env:WBPOJIA_PYTHON -and (Test-Path -LiteralPath $env:WBPOJIA_PYTHON)) {
        $Python = $env:WBPOJIA_PYTHON
    } elseif (Get-Command py -ErrorAction SilentlyContinue) {
        $Python = (Get-Command py).Source
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $Python = (Get-Command python).Source
    } else {
        throw "找不到 Python。装 3.9+ 并放上 PATH，或用 -Python 指定 python.exe"
    }
}

$ver = & $Python -c "import sys; print('%d.%d' % sys.version_info[:2])"
Write-Host "使用 Python $ver : $Python"
if ([version]$ver -lt [version]"3.9") { throw "需要 Python 3.9 以上，当前 $ver" }

$venv = Join-Path $PSScriptRoot ".venv-build"
$vpy = Join-Path $venv "Scripts\python.exe"
if (-not (Test-Path -LiteralPath $vpy)) {
    Write-Host "创建构建用虚拟环境 .venv-build ..."
    & $Python -m venv $venv
    if ($LASTEXITCODE -ne 0) { throw "venv 创建失败" }
}

Write-Host "安装/更新 PyInstaller ..."
& $vpy -m pip install --quiet --upgrade pip pyinstaller
if ($LASTEXITCODE -ne 0) { throw "PyInstaller 安装失败" }

$mode = if ($Onedir) { "--onedir" } else { "--onefile" }
$sub  = if ($Panel)  { "--windowed" } else { "--console" }
$appname = if ($Panel) { "wbpojia-panel" } else { "wbpojia" }
$pyiArgs = @(
    "-m", "PyInstaller",
    $mode, $sub, "--noupx", "--clean", "--noconfirm",
    "--name", $appname,
    "--distpath", $OutDir,
    "--workpath", (Join-Path $venv "pyi-work"),
    "--specpath", (Join-Path $venv "pyi-spec"),
    # 只排真正用不到的重模块；http / email 是面板（http.server）的依赖，不能排
    "--exclude-module", "tkinter",
    "--exclude-module", "unittest",
    "--exclude-module", "pydoc",
    "--exclude-module", "pdb",
    "--exclude-module", "test"
)
if ($Icon) { $pyiArgs += @("--icon", $Icon) }
$pyiArgs += (Join-Path $PSScriptRoot "wbpojia.py")

& $vpy @pyiArgs
if ($LASTEXITCODE -ne 0) { throw "PyInstaller 构建失败" }

$exe = if ($Onedir) { Join-Path $OutDir "$appname\$appname.exe" } else { Join-Path $OutDir "$appname.exe" }
if (-not (Test-Path -LiteralPath $exe)) { throw "构建结束但没找到 $exe" }

$sizeMB = [math]::Round((Get-Item -LiteralPath $exe).Length / 1MB, 2)
Write-Host ""
Write-Host "构建完成: $exe  ($sizeMB MB)"
Write-Host ""
Write-Host "自检：  .\$exe doctor"
Write-Host "验收：$env:WBPOJIA_ENGINE=$exe 然后跑 python tests\selftest.py"
