$ErrorActionPreference = "Stop"
if ($null -ne (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue)) {
    $PSNativeCommandUseErrorActionPreference = $false
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
$apiRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$expectedModules = @(
    "tests.test_invitations",
    "tests.test_comments",
    "tests.test_audit_events"
)
$expectedFiles = @(
    "tests\test_invitations.py",
    "tests\test_comments.py",
    "tests\test_audit_events.py"
)

if (-not (Test-Path $python)) {
    throw "Expected Python virtual environment at $python"
}

Set-Location $apiRoot

foreach ($file in $expectedFiles) {
    if (-not (Test-Path $file)) {
        throw "Expected auth regression test module is missing: $file"
    }
}

$stdoutFile = Join-Path ([System.IO.Path]::GetTempPath()) ("auth-gate-{0}.out.txt" -f ([System.Guid]::NewGuid().ToString("N")))
$stderrFile = Join-Path ([System.IO.Path]::GetTempPath()) ("auth-gate-{0}.err.txt" -f ([System.Guid]::NewGuid().ToString("N")))

try {
    $process = Start-Process `
        -FilePath $python `
        -ArgumentList (@("-m", "unittest", "-v") + $expectedModules) `
        -WorkingDirectory $apiRoot `
        -NoNewWindow `
        -Wait `
        -PassThru `
        -RedirectStandardOutput $stdoutFile `
        -RedirectStandardError $stderrFile

    $output = @()
    if (Test-Path $stdoutFile) {
        $output += Get-Content $stdoutFile
    }
    if (Test-Path $stderrFile) {
        $output += Get-Content $stderrFile
    }

    $exitCode = $process.ExitCode
    $output | ForEach-Object { $_ }
}
finally {
    Remove-Item $stdoutFile, $stderrFile -ErrorAction SilentlyContinue
}

if ($exitCode -ne 0) {
    throw "Focused auth regression suite failed with exit code $exitCode"
}

if (($output | Out-String) -match "skipped=") {
    throw "Focused auth regression suite reported skipped tests"
}
