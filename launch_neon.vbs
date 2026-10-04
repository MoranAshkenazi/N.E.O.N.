Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' קבלת הנתיב המלא של התיקייה שבה נמצא הקובץ
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' הפעלת desktop_runner.py ישירות דרך ה-Python של ה-venv
pythonExe = scriptDir & "\venv\Scripts\python.exe"
runnerScript = scriptDir & "\desktop_runner.py"

WshShell.CurrentDirectory = scriptDir
WshShell.Run """" & pythonExe & """ """ & runnerScript & """", 0, False