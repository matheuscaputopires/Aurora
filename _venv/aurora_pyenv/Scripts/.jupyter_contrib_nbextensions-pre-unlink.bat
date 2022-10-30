@echo off

"%PREFIX%\Scripts\jupyter-contrib-nbextension.exe" uninstall --sys-prefix
if errorlevel 1 exit 1
