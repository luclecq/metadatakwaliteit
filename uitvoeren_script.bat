rem =================================================================================================================
rem Uitvoeren controlescript metadatakwaliteit v0.6, november 2018
rem 
rem Gemaakt door Luc van der Lecq en Gerard Nienhuis.
rem
rem Dit batchbestand versoepelt het opstarten van het controlescript metadatakwaliteit op installaties van Overijssel.
rem =================================================================================================================

SET python_exe=C:\python27\arcgis10.4\python.exe

SET python_script=

SET input=

SET output=

@echo off

cls

echo.

echo Uitvoeren van controlescript metadatakwaliteit v0.6

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
