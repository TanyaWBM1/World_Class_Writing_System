Set shell = CreateObject("WScript.Shell")
repoRoot = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
command = Chr(34) & repoRoot & "\launch_dashboard.bat" & Chr(34)
shell.Run command, 0, False
