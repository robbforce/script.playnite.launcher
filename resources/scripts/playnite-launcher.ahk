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
PlayniteDesktopExe := "Playnite.DesktopApp.exe"
PlayniteFullscreenExe := "Playnite.FullscreenApp.exe"
GroupAdd, PlayniteExes, % "ahk_exe " . PlayniteDesktopExe
GroupAdd, PlayniteExes, % "ahk_exe " . PlayniteFullscreenExe

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

; Check if Playnite is running for the current user and launch or focus it.
varPID := ProcessExist(PlayniteExe, A_UserName)
If (varPID > 0)
{
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
;WinHook.Event.Add(0x0016, 0x0016, "PlayniteMinimizedEvent", varPID, "Playnite")

; Now close / kill Kodi for the current user.
If (Parameters.3 = "0")
{
  varPID := ProcessExist(KodiExe, A_UserName)
  If (varPID > 0)
  {
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

; If Kodi is running for the current user, but minimized, store the PID in a local variable and restore the window.
varPID := ProcessExist(KodiExe, A_UserName)
If (varPID > 0)
{
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
; Check if Playnite re-opened after an update or the user switched to the dekstop / fullscreen exe.
; ErrorLevel 0 indicates the window was found.
WinWaitActive, ahk_group PlayniteExes,,10
If (ErrorLevel = 0)
{
  ; Set the PID variable again. Try the fullscreen exe first.
  varPID := ProcessExist(PlayniteFullscreenExe, A_UserName)
  If (varPID > 0)
  {
    PlayniteExe = PlayniteFullscreenExe
  }
  Else
  {
    ; Fullscreen wasn't found so the desktop exe should be active then.
    varPID := ProcessExist(PlayniteDesktopExe, A_UserName)
    If (varPID > 0)
    {
      PlayniteExe = PlayniteDesktopExe
    }
  }

  If (varPID > 0)
  {
    ; Unhook events just in case, since we'll be adding new event hooks.
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
; Simulate the Process, Exist command, but apply a filter for the current user.
ProcessExist(varProcessName, processOwnerUserName := "")
{
  varQuery := "Select ProcessId from Win32_Process WHERE Name LIKE '%" . varProcessName . "%'"

  For varProcess in ComObjGet("winmgmts:").ExecQuery(varQuery, "WQL", 48)
  {
    If (processOwnerUserName != "")
    {
      currentProcessOwnerUserName := ComVar()
      varProcess.GetOwner(currentProcessOwnerUserName.ref)
      If (currentProcessOwnerUserName[] != processOwnerUserName)
        Continue
    }
    ; This will exit the loop early with the PID.
    Return varProcess.processID
  }
  ; If we've landed outside the loop, then the process wasn't found. Simulate the Process, Exist command by returning 0.
  Return 0
}

; ----------------------------------------------------------------------------------------------------------------------
; These com functions are required by the ProcessExist function, to query Win32_Process.
ComVar(Type=0xC)
{
  static base := { __Get: "ComVarGet", __Set: "ComVarSet", __Delete: "ComVarDel" }
  ; Create an array of 1 VARIANT.  This method allows built-in code to take
  ; care of all conversions between VARIANT and AutoHotkey internal types.
  arr := ComObjArray(Type, 1)
  ; Lock the array and retrieve a pointer to the VARIANT.
  DllCall("oleaut32\SafeArrayAccessData", "ptr", ComObjValue(arr), "ptr*", arr_data)
  ; Store the array and an object which can be used to pass the VARIANT ByRef.
  Return { ref: ComObjParameter(0x4000|Type, arr_data), _: arr, base: base }
}

; Called when script accesses an unknown field.
ComVarGet(cv, p*)
{
  If p.MaxIndex() = "" ; No name/parameters, i.e. cv[]
    Return cv._[0]
}

; Called when script sets an unknown field.
ComVarSet(cv, v, p*)
{
  If p.MaxIndex() = "" ; No name/parameters, i.e. cv[]:=v
    Return cv._[0] := v
}

; Called when the object is being freed.
ComVarDel(cv)
{
  ; This must be done to allow the internal array to be freed.
  DllCall("oleaut32\SafeArrayUnaccessData", "ptr", ComObjValue(cv._))
}

; ----------------------------------------------------------------------------------------------------------------------
; This event is only fired when Playnite is closed, re-open Kodi.
PlayniteClosedEvent(hWinEventHook, Win_Event, Win_Hwnd, idObject, idChild, dwEventThread, dwmsEventTime)
{
  GoSub, OpenKodi
}

; This event is only fired when Playnite is minimized, re-open Kodi.
; PlayniteMinimizedEvent(hWinEventHook, Win_Event, Win_Hwnd, idObject, idChild, dwEventThread, dwmsEventTime)
; {
;   GoSub, OpenKodi
; }
