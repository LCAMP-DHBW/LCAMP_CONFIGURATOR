<#
.SYNOPSIS
    Sicheres Git-Update-Skript ohne hardcodierte Secrets
.DESCRIPTION
    - Erstellt Commit mit Zeitstempel
    - Optionaler Push
    - GitHub Token wird aus Umgebungsvariable gelesen
#>

param(
    [string]$Branch = "main",
    [string]$CommitPrefix = "Update"
)

# -----------------------------
# Hilfsfunktionen
# -----------------------------
function Fail($msg) {
    Write-Error $msg
    exit 1
}

# -----------------------------
# Vorbedingungen prüfen
# -----------------------------
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Fail "Git ist nicht installiert oder nicht im PATH."
}

# GitHub Token aus ENV (optional, nur nötig bei HTTPS + Push)
$GitHubToken = $env:GITHUB_TOKEN

# -----------------------------
# Git Status
# -----------------------------
Write-Host "📦 Prüfe Git-Status..."
git status

# -----------------------------
# Commit erstellen
# -----------------------------
$datum = Get-Date -Format "yyyyMMdd_HHmmss"
$commitMessage = "$CommitPrefix_$datum"

Write-Host "📝 Commit: $commitMessage"


git add .
git commit -m "$commitMessage"

if ($LASTEXITCODE -ne 0) {
    Fail "Commit fehlgeschlagen."
}

# -----------------------------
# Push (optional)
# -----------------------------
$push = Read-Host "➡️  Push nach origin/$Branch? (y/n)"

if ($push -eq "y") {

    if (-not $GitHubToken) {
        Write-Host "⚠️  Kein GITHUB_TOKEN gesetzt – normaler Push wird versucht."
    } else {
        Write-Host "🔐 GitHub Token aus ENV wird verwendet (nicht im Code)."
    }

    git push origin $Branch

    if ($LASTEXITCODE -ne 0) {
        Fail "Push fehlgeschlagen."
    }

    Write-Host "✅ Push erfolgreich."
}
else {
    Write-Host "⏭️  Push übersprungen."
}

Write-Host "🎉 Fertig."

Pause


