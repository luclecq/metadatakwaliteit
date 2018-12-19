rem =================================================================================================================
rem Uitvoeren controlescript metadatakwaliteit v1.1, december 2018
rem 
rem Gemaakt door Luc van der Lecq en Gerard Nienhuis.
rem
rem Dit batchbestand versoepelt het opstarten van het controlescript metadatakwaliteit op installaties van Overijssel.
rem
rem Voorbeeldregels:
rem SET python_script=D:\ov\py\luc\controleer_metadata_10.py
rem SET input=D:\scratch\rapport_geodata_20181217.txt
rem SET output=D:\scratch\rapport_geodata_20181217_controle.txt
rem
rem Let op: er zijn geen spaties toegestaan bij het declareren van variabelen.
rem =================================================================================================================

IF EXIST C:\python27\arcgis10.4\python.exe (
  SET python_exe=C:\python27\arcgis10.4\python.exe
) ELSE (
  SET python_exe=C:\python27\arcgis10.5\python.exe
)

SET python_script=

SET input=

SET output=

@echo off

cls

echo.

echo Uitvoeren van controlescript metadatakwaliteit v1.1

echo.

pause

echo.

echo ================================================================================================================

echo.

%python_exe% %python_script% %input% %output%

echo.

echo ================================================================================================================

echo.

pause
