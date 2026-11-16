$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$expectedRemote = 'https://github.com/chenprof5-commits/PrimeFlixTV.git'
Push-Location $repoRoot
try {
    if (-not (Test-Path '.git')) {
        git init -b main
        if ($LASTEXITCODE -ne 0) { throw 'git init failed.' }
    }

    $origin = git remote get-url origin 2>$null
    if ($LASTEXITCODE -eq 0) {
        if ($origin.TrimEnd('/') -ne $expectedRemote.TrimEnd('/')) {
            throw "The origin remote does not match the expected target: $origin"
        }
    } else {
        git remote add origin $expectedRemote
        if ($LASTEXITCODE -ne 0) { throw 'Could not configure origin.' }
    }

    # Retire du suivi le journal Kotlin généré pendant les compilations locales,
    # s'il est encore suivi dans cet historique.
    $trackedKotlin = @(git ls-files -- apps/tv/android/.kotlin)
    if ($trackedKotlin.Count -gt 0) {
        git rm -r --cached -- apps/tv/android/.kotlin
        if ($LASTEXITCODE -ne 0) { throw 'Could not exclude the generated Kotlin log.' }
    }

    git add --all
    if ($LASTEXITCODE -ne 0) { throw 'git add failed.' }

    $stagedFiles = @(git diff --cached --name-only)
    $forbidden = @($stagedFiles | Where-Object {
        $_ -match '(^|/)\.env($|\.)' -and $_ -notmatch '(^|/)\.env\.example$' -or
        $_ -match '(^|/)(node_modules|dist|build|\.gradle|\.cxx|\.kotlin|\.vercel|__pycache__|\.pytest_cache)(/|$)' -or
        $_ -match '(^|/)local\.properties$|(^|/)debug\.keystore$|\.(apk|aab|db|jks|keystore|pem|p12|key|log)$' -or
        $_ -eq 'NetMirrorTV.apk'
    })
    if ($forbidden.Count -gt 0) {
        $forbidden | ForEach-Object { Write-Host "File must be excluded: $_" }
        throw 'The staged content contains a local artifact, possible secret, or file that must not be published. No commit or push was made.'
    }

    git diff --cached --check
    if ($LASTEXITCODE -ne 0) { throw 'Fix the reported whitespace before publishing.' }

    if ((git diff --cached --quiet) -eq $null -and $LASTEXITCODE -eq 0) {
        Write-Host 'There are no changes to commit.'
        return
    }

    git status --short
    git commit -m 'Update PrimeFlix TV source'
    if ($LASTEXITCODE -ne 0) { throw 'git commit failed. Check git user.name and user.email.' }

    git push -u origin main
    if ($LASTEXITCODE -ne 0) {
        throw 'git push failed. If GitHub says main already contains commits, do not force push; fetch and merge that branch first.'
    }

    Write-Host "Published: $expectedRemote"
} finally {
    Pop-Location
}
