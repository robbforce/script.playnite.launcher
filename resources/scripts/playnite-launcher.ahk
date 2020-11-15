; KODI Playnite Launcher autohotkey script by Nathaniel Roark, 2020-11-11.
;
; Inspired by Steam Launcher by teeedub: https://github.com/teeedubb/teeedubb-xbmc-repo & http://forum.xbmc.org/showthread.php?tid=157499
; Also inspired by Kodi-Launches-Playnite-Addon by hoksilato2: https://github.com/hoksilato2/Kodi-Launches-Playnite-Addon
; which was forked from Kodi-Launches-Steam-Addon by BrosMakingSoftware. :)
;
; The original Steam Launcher ahk script has been so heavily re-factored that only the logic flow is intact. Instead of
; polling for the Playnite window, this uses window messages to watch for destroyed or minimized events. Other notable
; changes include parsing the command line paramters into an array, using the PID of the executed process for the win
; commands, and the ability to restore Playnite from the sysstem tray.
;
; Thanks go out to Fanatic Guru for the TrayIcon and WinHook libraries:
; https://gist.github.com/tmplinshi/83c52a9dffe65c105803d026ca1a07da
; https://www.autohotkey.com/boards/viewtopic.php?t=59149
;
; Manual script usage: playnite-launcher.exe "e:\path\to\playnite.exe" "d:\path\to\kodi.exe" "0/1" "true/false" "scriptpath/false" "scriptpath/false" "playnite parameters" "0"
; Example: playnite-launcher.exe "C:\Emulation\Playnite\Playnite.DesktopApp.exe" "C:\Program Files\Kodi\kodi.exe" "0" "false" "false" "false" "" "0"
; Command-line parameters:
;   $1 = Playnite executable
;   $2 = Kodi executable
;   $3 = 0 Quit KODI, 1 Minimize KODI
;   $4 = KODI portable mode
;   $5 = pre script
;   $6 = post script
;   $7 = Playnite parameters
;   $8 = force kill kodi and how long to wait for, greater than 0 = true
;
; Change the 'playnite.launcher.script.revision' number below to 999 to preserve changes through addon updates, otherwise
; it'll be overwritten. You'll need to install AutoHotKey to compile this .ahk file into an .exe, to work with the addon.
;
; playnite.launcher.script.revision=001

#NoEnv
#SingleInstance force
#include WinHook.ahk
#include TrayIcon.ahk
DetectHiddenWindows, Off
SetWorkingDir %A_ScriptDir%
OnExit(ObjBindMethod(WinHook.Event, "UnHookAll"))

If (A_Args.Length() < 8)
{
  MsgBox % "This script requires 8 arguments, but it only received " . A_Args.Length() . ". See script file for details."
  ExitApp
}

; Set some variables. Trying to use A_Args directly results in a compilation error in autohotkey, especially when running
; without all parameters. This loop and referencing this array gets around that. It also allows us to replace the legacy
; parameter variables with something slightly more readable.
Global Parameters := {}
For Index, Value in A_Args
  Parameters[Index] := Value
SplitPath, % Parameters.1, PlayniteExe, PlayniteDir
SplitPath, % Parameters.2, KodiExe

KodiClass := "Kodi"

; Uncomment the following line and add the PID of a running app to see the title and class in a msgbox.
;GetProcessInfo(20400)

; ----------------------------------------------------------------------------------------------------------------------
; Execute pre-playnite script.
If (Parameters.5 != "false")
{
  RunWait, % Parameters.5,, Hide
}

; ----------------------------------------------------------------------------------------------------------------------
; Check first if Playnite is in the system tray, use another approach and commands to activate the window.
oIcons := {}
oIcons := TrayIcon_GetInfo(PlayniteExe)

; Use the process name to make sure the system icon was found and send a double left-click to retore the window.
If (oIcons[1].process = PlayniteExe)
{
  TrayIcon_Button(PlayniteExe, "L", True)
  WinWaitActive, ahk_exe %PlayniteExe%,,5
}

; Check if Playnite is running and launch or focus it.
Process, Exist, %PlayniteExe%
If (ErrorLevel > 0)
{
  varPID = %ErrorLevel%
  If (WinExist("ahk_pid " . varPID))
  {
    WinRestore, ahk_pid %varPID%
    WinActivate, ahk_pid %varPID%
  }
}
Else
{
  ; Launch Playnite and store the PID in a local variable.
  Run, % Parameters.1 Parameters.7,, UseErrorLevel, varPID
  If (ErrorLevel = ERROR)
  {
    Msgbox % "There was an error trying to run the Playnite exe."
  }
}

; ----------------------------------------------------------------------------------------------------------------------
PlayniteLoop:
; Wait for playnite to load. Set timeout to 5, so this script doesn't hang.
WinWaitActive, ahk_pid %varPID%,, 5

; Register win hooks to detect when Playnite is closed or minimized.
WinHook.Event.Add(0x8001, 0x8001, "PlayniteClosedEvent", varPID, "Playnite")
WinHook.Event.Add(0x0016, 0x0016, "PlayniteMinimizedEvent", varPID, "Playnite")

; Now close / kill Kodi.
If (Parameters.3 = "0")
{
  Process, Exist, %KodiExe%
  If (ErrorLevel > 0)
  {
    varPID = %ErrorLevel%
    Process, Close, %varPID%
  }

  ; If the process failed to close (Process, Close will set ErrorLevel to 0 on failure) and a timeout parameter
  ; was supplied, then try again with the tskill command.
  If (ErrorLevel = 0 And Parameters.8 > 0)
  {
    Run, % comspec . " /c timeout /t " . Parameters.8 . " && tskill " . varPID,, Hide
  }
}

; Or minimize Kodi instead.
If (Parameters.3 = "1") And (WinExist("ahk_class " . KodiClass))
{
  WinMinimize
}

Return


; ----------------------------------------------------------------------------------------------------------------------
OpenKodi:
; Execute post playnite script.
If (Parameters.6 != "false")
{
  RunWait, % Parameters.6,, Hide
}

; If Kodi is running, but minimized, store the PID in a local variable and restore the window.
Process, Exist, %KodiExe%
If (ErrorLevel > 0)
{
  varPID = %ErrorLevel%
  If (Parameters.3 = "1") And (WinExist("ahk_pid " . varPID))
  {
    WinRestore, ahk_pid %varPID%
    WinActivate, ahk_pid %varPID%
  }
}

; Run the Kodi executable if the script closed it earlier.
If (Parameters.3 = "0")
{
  ; Check if it should run in portable mode or not.
  If (Parameters.4 = "true")
  {
    varRunCmd := % Parameters.2 . " -p"
  }
  Else
  {
    varRunCmd := % Parameters.2
  }

  ; Launch Kodi and store the PID in a local variable.
  Run, %varRunCmd%,, UseErrorLevel, varPID
  If (ErrorLevel = ERROR)
  {
    Msgbox % "There was an error trying to run the Kodi exe."
  }
}

; Wait for Kodi to load. Set timeout to 5, so this script doesn't hang.
WinWaitActive, ahk_pid %varPID%,,5

; ----------------------------------------------------------------------------------------------------------------------
; Check if Playnite re-opened after an update. ErrorLevel 0 indicates the window was found.
WinWaitActive, ahk_exe %PlayniteExe%,,10
If (ErrorLevel = 0)
{
  ; Set the PID variable again.
  Process, Exist, %PlayniteExe%
  If (ErrorLevel > 0)
  {
    varPID = %ErrorLevel%

    ; In case Playnite was minimized earlier, unhook events since we'll be adding new event hooks.
    WinHook.Event.UnHookAll()

    ; Run the pre-Playnite script again if needed.
    If (Parameters.5 != "false")
    {
      RunWait, % Parameters.5,, Hide
    }

    ; Go back to listening for the close event.
    Goto, PlayniteLoop
  }
}

ExitApp

RunAsAdmin()
{
  Loop, %0%
  {
    param := %A_Index%  ; Fetch the contents of the variable whose name is contained in A_Index.
    params .= A_Space . param
  }
  ShellExecute := A_IsUnicode ? "shell32\ShellExecute":"shell32\ShellExecuteA"
  if not A_IsAdmin
  {
    If A_IsCompiled
      DllCall(ShellExecute, uint, 0, str, "RunAs", str, A_ScriptFullPath, str, params, str, A_WorkingDir, int, 1)
    Else
      DllCall(ShellExecute, uint, 0, str, "RunAs", str, A_AhkPath, str, """" . A_ScriptFullPath . """" . A_Space . params, str, A_WorkingDir, int, 1)
    ExitApp
  }
}

; ----------------------------------------------------------------------------------------------------------------------
; Call this function with the PID you need info from. Ex: GetProcessInfo(21964)
GetProcessInfo(p_pid)
{
  If (WinExist("ahk_pid " . p_pid))
  {
    WinGet, varHwnd, ID
    WinGet, varProcessName, ProcessName
    WinGetTitle, varWindowTitle, ahk_exe %varProcessName%
    WinGetClass, varWindowClass, ahk_exe %varProcessName%
  }
  MsgBox % "PID: " . p_pid . "`n" . "hWnd: " . varHwnd . "`n" . "Process name: " . varProcessName . "`n" . "Window title: " . varWindowTitle . "`n" . "Window class: " . varWindowClass
}

; ----------------------------------------------------------------------------------------------------------------------
; This event is only fired when Playnite is closed, re-open Kodi.
PlayniteClosedEvent(hWinEventHook, Win_Event, Win_Hwnd, idObject, idChild, dwEventThread, dwmsEventTime)
{
  GoSub, OpenKodi
}

; This event is only fired when Playnite is minimized, re-open Kodi.
PlayniteMinimizedEvent(hWinEventHook, Win_Event, Win_Hwnd, idObject, idChild, dwEventThread, dwmsEventTime)
{
  GoSub, OpenKodi
}
