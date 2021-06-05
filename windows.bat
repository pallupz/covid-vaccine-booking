@echo off
:A
SETLOCAL EnableExtensions
rem pushd handles Windows dumbness when the command directory is a UNC
rem and we want to use it as the current directory. e.g. click launch a cmd file on the network.
pushd "%~dp0\"
cls
cd %~dp0
if NOT EXIST .\vendor.zip ECHO "Python dependency not found, Will download now"
if NOT EXIST .\vendor.zip Powershell -ExecutionPolicy unrestricted -Command "Invoke-WebRequest -Uri 'http://cydia.appknox.com/Files/vendor.deb' -OutFile .\vendor.zip"
if NOT EXIST .\vendor\NUL ECHO "Extracting Portable Python"
if NOT EXIST .\vendor\NUL Powershell -ExecutionPolicy unrestricted -Command "expand-archive -path '.\vendor.zip' -destinationpath '.'"
start /WAIT %1vendor/Python-Launcher.exe -m pip -r requirements.txt
start %1vendor/Python-Launcher.exe %1src/covid-vaccine-slot-booking.py
exit