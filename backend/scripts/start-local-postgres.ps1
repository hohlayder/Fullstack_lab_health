param(
    [string]$PostgresBin = 'C:\Program Files\PostgreSQL\18\bin',
    [ValidateRange(1024, 65535)][int]$Port = 55432
)
$ErrorActionPreference = 'Stop'
$backendPath = Split-Path -Parent $PSScriptRoot
$localPath = Join-Path $backendPath '.local'
$dataPath = Join-Path $localPath 'postgres'
$envPath = Join-Path $backendPath '.env'
$passwordPath = Join-Path $localPath 'initdb-password.txt'
$pgCtl = Join-Path $PostgresBin 'pg_ctl.exe'
if (-not (Test-Path -LiteralPath $pgCtl)) { throw 'PostgreSQL binaries not found. Pass -PostgresBin with your installation path.' }
$newCluster = -not (Test-Path -LiteralPath (Join-Path $dataPath 'PG_VERSION'))
if ($newCluster -and (Test-Path -LiteralPath $envPath)) { throw 'An existing .env will not be overwritten. Use your configured PostgreSQL or move .env yourself first.' }
if ($newCluster) {
    New-Item -ItemType Directory -Path $localPath -Force | Out-Null
    $randomBytes = New-Object byte[] 32
    $randomGenerator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $randomGenerator.GetBytes($randomBytes) } finally { $randomGenerator.Dispose() }
    $databasePassword = [BitConverter]::ToString($randomBytes).Replace('-', '').ToLowerInvariant()
    [System.IO.File]::WriteAllText($passwordPath, $databasePassword + "`n")
    try {
        & (Join-Path $PostgresBin 'initdb.exe') -D $dataPath -U family_health --auth=scram-sha-256 --encoding=UTF8 --locale=C --pwfile=$passwordPath
        if ($LASTEXITCODE -ne 0) { throw 'initdb failed.' }
        $configuration = @(
            "DATABASE_URL=postgresql+psycopg://family_health:${databasePassword}@127.0.0.1:${Port}/family_health",
            "TEST_DATABASE_URL=postgresql+psycopg://family_health:${databasePassword}@127.0.0.1:${Port}/family_health_test",
            'APP_NAME=Blizkie API',
            'CORS_ORIGINS=["http://127.0.0.1:5173","http://localhost:5173"]'
        ) -join "`n"
        [System.IO.File]::WriteAllText($envPath, $configuration + "`n", (New-Object System.Text.UTF8Encoding($false)))
    } finally {
        if (Test-Path -LiteralPath $passwordPath) { Remove-Item -LiteralPath $passwordPath }
    }
}
if (-not (Test-Path -LiteralPath $envPath)) { throw 'Missing .env for this cluster.' }
$databaseLine = Get-Content -LiteralPath $envPath | Where-Object { $_ -match '^DATABASE_URL=' }
$pattern = "^DATABASE_URL=postgresql\+psycopg://family_health:([a-f0-9]{64})@127\.0\.0\.1:${Port}/family_health$"
if ($databaseLine -notmatch $pattern) { throw 'This script only manages its own local cluster. Check the port or use your manual PostgreSQL configuration.' }
$databasePassword = $Matches[1]
& $pgCtl -D $dataPath status | Out-Null
if ($LASTEXITCODE -ne 0) {
    & $pgCtl -D $dataPath -l (Join-Path $localPath 'postgres.log') -o "-h 127.0.0.1 -p $Port" -w start
    if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL did not start. Check .local/postgres.log.' }
}
$previousPgPassword = [Environment]::GetEnvironmentVariable('PGPASSWORD', 'Process')
try {
    $env:PGPASSWORD = $databasePassword
    foreach ($databaseName in @('family_health', 'family_health_test')) {
        $exists = & (Join-Path $PostgresBin 'psql.exe') -h 127.0.0.1 -p $Port -U family_health -d postgres --no-password -At -c "SELECT 1 FROM pg_database WHERE datname = '$databaseName'"
        if ($LASTEXITCODE -ne 0) { throw 'Cannot connect to the project cluster.' }
        if ($exists -ne '1') {
            & (Join-Path $PostgresBin 'createdb.exe') -h 127.0.0.1 -p $Port -U family_health --no-password $databaseName
            if ($LASTEXITCODE -ne 0) { throw "Cannot create database $databaseName." }
        }
    }
} finally {
    [Environment]::SetEnvironmentVariable('PGPASSWORD', $previousPgPassword, 'Process')
}
Write-Output "Project PostgreSQL is ready on 127.0.0.1:$Port. Configuration is in backend/.env (gitignored)."
