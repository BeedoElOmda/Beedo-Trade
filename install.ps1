# Beedo-Trade installer for Windows.
# Usage (PowerShell, from this folder):
#   powershell -ExecutionPolicy Bypass -File install.ps1 [-GoldApiKey goldapi-xxxx] [-SkipDesktop]
param([string]$GoldApiKey = "", [switch]$SkipDesktop)
$ErrorActionPreference = "Stop"
# PowerShell 5.1's "utf8" adds a BOM, which breaks JSON readers; write plain UTF-8 instead.
function Write-Utf8($path, $text) { [IO.File]::WriteAllText($path, $text, (New-Object Text.UTF8Encoding $false)) }

# Tested version of the third-party EGX server (https://github.com/M-Abdelmegeed/EGX-Data-MCP-Server)
$EgxRepo   = "https://github.com/M-Abdelmegeed/EGX-Data-MCP-Server.git"
$EgxCommit = "d4ee5625b48ed0c9682c321ab5776936b845cf63"
$EgxDir    = Join-Path $HOME "mcp-servers\EGX-Data-MCP-Server"
$SkillDir  = Join-Path $HOME ".claude\skills\beedo-trade"

function Need($cmd, $hint) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { Write-Host "Missing '$cmd'. $hint" -ForegroundColor Red; exit 1 }
}
Need git "Install Git: winget install Git.Git"
Need uv  "Install uv: powershell -c `"irm https://astral.sh/uv/install.ps1 | iex`""

Write-Host "1/4 Installing the Beedo-Trade skill to $SkillDir"
New-Item -ItemType Directory -Force (Split-Path $SkillDir) | Out-Null
if (Test-Path $SkillDir) { Remove-Item -Recurse -Force $SkillDir }
Copy-Item -Recurse (Join-Path $PSScriptRoot "skills\beedo-trade") $SkillDir

Write-Host "2/4 Installing the EGX MCP server to $EgxDir"
if (-not (Test-Path (Join-Path $EgxDir ".git"))) {
  New-Item -ItemType Directory -Force (Split-Path $EgxDir) | Out-Null
  git clone --quiet $EgxRepo $EgxDir
}
git -C $EgxDir fetch --quiet origin
git -C $EgxDir checkout --quiet --force $EgxCommit
# The server prints a startup line on stdout, which is the MCP channel; send it to stderr instead.
$main = Join-Path $EgxDir "main.py"
Write-Utf8 $main ((Get-Content $main -Raw) -replace 'print\("Starting EGX Stock Tools MCP Server\.\.\."\)', 'print("Starting EGX Stock Tools MCP Server...", file=sys.stderr)')
Push-Location $EgxDir; uv sync --quiet; Pop-Location
if ($GoldApiKey) { "GOLDAPI_KEY=$GoldApiKey" | Set-Content (Join-Path $EgxDir ".env") -Encoding ascii }

$uvPath = (Get-Command uv).Source
$server = [ordered]@{ command = $uvPath; args = @("--directory", $EgxDir, "run", "main.py") }
# Beedo-Trade's own MCP server, for Claude Desktop chat (Claude Code uses the skill instead).
$beedo  = [ordered]@{ command = $uvPath; args = @("run", "--script", (Join-Path $SkillDir "scripts\mcp_server.py")) }

Write-Host "3/4 Registering egx-mcp with Claude Code"
if (Get-Command claude -ErrorAction SilentlyContinue) {
  # PowerShell 5.1 turns native stderr into an error under "Stop", so ignore a "not found" here.
  try { claude mcp remove egx-mcp -s user 2>$null | Out-Null } catch {}
  claude mcp add egx-mcp --scope user -- $uvPath --directory $EgxDir run main.py
} else { Write-Host "   Claude Code CLI not found; skipped." }

Write-Host "4/4 Registering egx-mcp and beedo-trade with Claude Desktop"
if (-not $SkipDesktop) {
  # Standard install, then the Microsoft Store install location.
  $cfgs = @(Join-Path $env:APPDATA "Claude\claude_desktop_config.json") +
          @(Get-ChildItem (Join-Path $env:LOCALAPPDATA "Claude-Data") -Filter claude_desktop_config.json -Recurse -Depth 2 -ErrorAction SilentlyContinue | ForEach-Object FullName)
  $cfg = $cfgs | Where-Object { Test-Path $_ } | Select-Object -First 1
  if (-not $cfg) { $cfg = $cfgs[0]; New-Item -ItemType Directory -Force (Split-Path $cfg) | Out-Null; Write-Utf8 $cfg '{}' }
  Copy-Item $cfg "$cfg.bak" -Force
  $json = Get-Content $cfg -Raw | ConvertFrom-Json
  if (-not $json.mcpServers) { $json | Add-Member -NotePropertyName mcpServers -NotePropertyValue ([pscustomobject]@{}) }
  $json.mcpServers | Add-Member -NotePropertyName "egx-mcp" -NotePropertyValue ([pscustomobject]$server) -Force
  $json.mcpServers | Add-Member -NotePropertyName "beedo-trade" -NotePropertyValue ([pscustomobject]$beedo) -Force
  Write-Utf8 $cfg ($json | ConvertTo-Json -Depth 32)
  Write-Host "   Updated $cfg (backup: $cfg.bak). Fully quit and reopen Claude Desktop."
}

Write-Host "`nDone. Start a new Claude session and ask: 'Analyse COMI with my course method.'" -ForegroundColor Green
if (-not $GoldApiKey -and -not (Test-Path (Join-Path $EgxDir ".env"))) {
  Write-Host "Gold/silver prices need a free key from goldapi.io. Re-run with -GoldApiKey <key>."
}
