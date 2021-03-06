:: Build an executable for the app Chamannas using PyInstaller
@ECHO off
python -O -m PyInstaller --hidden-import tkinter --hidden-import babel.numbers --onefile --icon="assets/icons/app_icon.ico" chamannas.pyw
COPY /Y dist\chamannas.exe .
ECHO The executable "chamannas.exe" has been created