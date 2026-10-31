@echo off
rem Double-click: find a working free substitute for nemotron_super. Output: results\_runner\probe_substitutes.txt
cd /d "%~dp0.."
python -m tools.probe_substitutes > "results\_runner\probe_out.txt" 2>&1
