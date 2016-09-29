@echo off
setlocal enableDelayedExpansion
type src\module.info | findstr -i version > _wmvers.tmp
for /f "eol== tokens=1,2 delims==" %%B in (_wmvers.tmp) do set "wmvers=%%C"
del _wmvers.tmp
echo
echo Parsing source files...
echo Version of source is: %wmvers%

7z.exe a -ttar -so vBoxControl_%wmvers%.wbm src\* | 7z.exe a -si modules\vBoxControl_%wmvers%.wbm.gz
