# install.ps1 — Instala las skills autorales de Gustavo Carreño desde
# github.com/GustavoCarreno/claude-skills al %USERPROFILE%\.claude\skills\ del usuario.
#
# Uso recomendado (one-liner desde PowerShell):
#   iwr -useb https://raw.githubusercontent.com/GustavoCarreno/claude-skills/main/install.ps1 | iex
#
# O clone + ejecución manual:
#   git clone https://github.com/GustavoCarreno/claude-skills $env:TEMP\claude-skills
#   & "$env:TEMP\claude-skills\install.ps1"
#
# Requisitos:
#   - Git for Windows instalado y en PATH (https://git-scm.com/download/win)
#   - PowerShell 5.1 o superior
#
# Si PowerShell bloquea el script con SecurityError/UnauthorizedAccess, corre primero:
#   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
# (es one-time, per-user, no requiere admin, recomendado por Microsoft para dev machines)

$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/GustavoCarreno/claude-skills.git"
$SkillsDir = Join-Path $env:USERPROFILE ".claude\skills"
$TmpDir = Join-Path $env:TEMP ("claude-skills-install-" + [System.Guid]::NewGuid().ToString("N"))

try {
    # Verificar que git esté disponible
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Host "Error: git no está en el PATH." -ForegroundColor Red
        Write-Host "Instala Git for Windows desde https://git-scm.com/download/win y vuelve a correr." -ForegroundColor Red
        exit 1
    }

    Write-Host "Clonando repo desde $RepoUrl..." -ForegroundColor Cyan
    git clone --quiet --depth 1 $RepoUrl $TmpDir
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: git clone falló. Revisa tu conexión a internet o los permisos del folder temp." -ForegroundColor Red
        exit 1
    }

    # Crear folder de skills si no existe
    if (-not (Test-Path $SkillsDir)) {
        New-Item -ItemType Directory -Force -Path $SkillsDir | Out-Null
    }

    $installed = @()
    Get-ChildItem -Path $TmpDir -Directory | Where-Object { $_.Name -notmatch '^\.' } | ForEach-Object {
        $skillDir = $_.FullName
        $skillName = $_.Name
        $skillMd = Join-Path $skillDir "SKILL.md"

        if (Test-Path $skillMd) {
            Write-Host "Instalando skill: $skillName" -ForegroundColor Green
            $destDir = Join-Path $SkillsDir $skillName
            if (Test-Path $destDir) {
                Remove-Item -Recurse -Force $destDir
            }
            Copy-Item -Recurse $skillDir $destDir
            $installed += $skillName
        }
    }

    Write-Host ""
    if ($installed.Count -eq 0) {
        Write-Host "Advertencia: no se encontraron skills para instalar en el repo." -ForegroundColor Yellow
        exit 1
    }

    Write-Host "✓ Skills instaladas en ${SkillsDir}:" -ForegroundColor Green
    foreach ($name in $installed) {
        Write-Host "  - $name"
    }
    Write-Host ""
    Write-Host "Siguiente paso: en tu terminal de claude, corre /exit y luego claude"
    Write-Host "para que las skills aparezcan en tu lista."
} finally {
    # Cleanup del folder temporal
    if (Test-Path $TmpDir) {
        Remove-Item -Recurse -Force $TmpDir -ErrorAction SilentlyContinue
    }
}
