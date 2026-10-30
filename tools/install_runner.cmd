@echo off
rem Double-click launcher for tools\install_runner.ps1 (registers agent-civ-lab-runner + agent-civ-lab-autosync for this folder).
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_runner.ps1" > "results\_runner\install_runner.log" 2>&1
echo done >> "results\_runner\install_runner.log"
