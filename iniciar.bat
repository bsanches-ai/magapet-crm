@echo off
title MagaPet - Servidor de Impressao
cd /d "%~dp0"
netsh advfirewall firewall add rule name="MagaPet CRM" dir=in action=allow protocol=TCP localport=5000 >nul 2>&1
python servidor_impressao.py
pause
