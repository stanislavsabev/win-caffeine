Set objShell = WScript.CreateObject("WScript.Shell")
Set objArgs = WScript.Arguments

argString = " "

If objArgs.Count > 0 Then
    For Each arg In objArgs
        argString = argString & " " & Chr(34) & arg & Chr(34) 
    Next ' arg
End If

objShell.Run "cmd /c win-caffeine.bat" & argString, 0, True
