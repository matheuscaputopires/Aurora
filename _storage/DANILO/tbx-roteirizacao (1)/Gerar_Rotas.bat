@echo off

echo ************************************************
echo ************************************************
echo                    Cielo
echo                GERADOR DE ROTAS
echo                     GIS
echo                    v2.2
echo ************************************************
echo ************************************************



@ECHO OFF


:choice
set network= 0
set param_number_day_route= 5
set param_number_visit_per_day= 3
set continue_route= 0

set /P xlsx=Digite o caminho do arquivo (.xlsx) que sera processado:
set /P network=Digite o caminho do StreetMap Premium:
set /P saida=Digite o caminho da saida:
set /P param_number_day_route=Quantidade de Dias de Rota [5]:
set /P param_number_visit_per_day=Quantidade de Visitas por Rota [3]:
set /P continue_route=Deseja continuar a roteirizacao da onde parou? (S/N):
if /I "%continue_route%" EQU "S" goto :true
if /I "%continue_route%" EQU "N" goto :false
goto :choice

:true
set continue_route=1

:false
set continue_route=0

REM python vrp-cielo/main.py %xlsx% %network% %saida% %param_number_day_route% %param_number_visit_per_day% %continue_route%
"C:\Users\%username%\AppData\Local\ESRI\conda\envs\arcgispro-py3-clone\python.exe" vrp-cielo/main.py %xlsx% %network% %saida% %param_number_day_route% %param_number_visit_per_day% %continue_route%

:continue
pause