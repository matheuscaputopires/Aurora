@echo off
"%PREFIX%\Scripts\jupyter-contrib-nbextension.exe" install --sys-prefix
if errorlevel 1 exit 1

"%PREFIX%\Scripts\jupyter-nbextension.exe" enable collapsible_headings/main --sys-prefix
if errorlevel 1 exit 1

"%PREFIX%\Scripts\jupyter-nbextension.exe" install repr_style/main
"%PREFIX%\Scripts\jupyter-nbextension.exe" enable repr_style/main
if errorlevel 1 exit 1
