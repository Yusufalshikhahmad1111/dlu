$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host "== DLU Lab Windows release build =="

python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

$env:QT_QPA_PLATFORM = "offscreen"
python tools/capture_screenshots.py --output-dir artifacts/screenshots

if (Test-Path pysidedeploy.spec) { Remove-Item pysidedeploy.spec -Force }
pyside6-deploy --force --init main.py
New-Item -ItemType Directory -Force -Path dist | Out-Null

$vswhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (Test-Path $vswhere) {
    $installationPath = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
    if ($installationPath) {
        $vcvars = Join-Path $installationPath "VC\Auxiliary\Build\vcvars64.bat"
        if (Test-Path $vcvars) {
            cmd /c "`"$vcvars`" && set" | ForEach-Object {
                if ($_ -match "^(.*?)=(.*)$") {
                    Set-Item -Path "Env:$($matches[1])" -Value $matches[2]
                }
            }
        }
    }
}

pyside6-deploy --force --no-warn --mode onefile main.py

$exe = Get-ChildItem -Path dist -Filter "*.exe" -File | Select-Object -First 1
if (-not $exe) {
    throw "Packaging did not produce a Windows executable in dist/."
}

Write-Host "Built executable: $($exe.FullName)"
& $exe.FullName --smoke-test
if ($LASTEXITCODE -ne 0) {
    throw "Packaged executable smoke test failed with exit code $LASTEXITCODE."
}
