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
; playnite.launcher.script.revision=002

#Requires AutoHotkey v2.0.11+
#SingleInstance force
#include WinHook.ahk
Persistent true
DetectHiddenWindows false

OnExit(ObjBindMethod(WinHook.Event, "UnHookAll"))

If (A_Args.Length < 8)
{
  MsgBox "This script requires 8 arguments, but it only received " . A_Args.Length() . ". See script file for details."
  ExitApp
}

; Set some variables. Trying to use A_Args directly results in a compilation error in autohotkey, especially when running
; without all parameters. This loop and referencing this array gets around that. It also allows us to replace the legacy
; parameter variables with something slightly more readable.
Parameters := Array()
Loop A_Args.Length {
  Parameters.Push A_Args[A_Index]
}
SplitPath Parameters[1], &PlayniteExe, &PlayniteDir
SplitPath Parameters[2], &KodiExe, &KodiDir
QuitOrMinKodi := Parameters[3]
PortableKodi := Parameters[4]
PreScript := Parameters[5]
PostScript := Parameters[6]
PlayniteParameters := Parameters[7]
ForceKillTime := Parameters[8]

KodiClass := "Kodi"
PlayniteWindowTitle := "Playnite"
PlayniteDesktopExe := "Playnite.DesktopApp.exe"
PlayniteFullscreenExe := "Playnite.FullscreenApp.exe"

; Uncomment the following line and add the PID of a running app to see the title and class in a msgbox.
;GetProcessInfo(20400)

; ----------------------------------------------------------------------------------------------------------------------
; Execute pre-Playnite script.
If (PreScript != "false") {
  RunWait '"' . PreScript . '"',, "Hide"
}

; Even if Playnite is already running, brute force execute again since it runs in single instance mode.
; This will (re)launch Playnite, wait for the new window to load, then retrieve and store the PID.
Try {
  Run PlayniteExe . ' "' . PlayniteParameters . '"', PlayniteDir
  WinWaitActive PlayniteWindowTitle,, 10
  varPID := ProcessExist(PlayniteExe, A_UserName)
}
Catch {
  Msgbox "There was an error trying to run the Playnite exe."
  ExitApp
}
;GetProcessInfo(varPID)
SetPlayniteHook(varPID)

; ----------------------------------------------------------------------------------------------------------------------
SetPlayniteHook(PlaynitePID := 0) {
  ; Wait for playnite to load. Set timeout to 10, so this script doesn't hang.
  WinWaitActive "ahk_pid " . PlaynitePID,, 10

  ; Register win hooks to detect when Playnite is closed or minimized.
  WinHook.Event.Add(0x8001, 0x8001, PlayniteClosedEvent, PlaynitePID, "Playnite")
  ;WinHook.Event.Add(0x0016, 0x0016, PlayniteMinimizedEvent, PlaynitePID, "Playnite")

  ; If requested, close / kill Kodi for the current user.
  KodiPID := ProcessExist(KodiExe, A_UserName)
  If (KodiPID > 0) {
    Switch QuitOrMinKodi {
      Case "0":
        ; Simply close using the class.
        WinClose("ahk_class " . KodiClass)
        varClosed := WinWaitClose("ahk_pid " . KodiPID,, 10)

        ; If the process failed to close (ProcessClose will return 0 on failure) and a timeout parameter
        ; was supplied, then try again with the tskill command.
        If (varClosed = 0 And ForceKillTime > 0) {
          Run A_ComSpec . " /c timeout /t " . ForceKillTime . " && tskill " . KodiPID,, "Hide"
        }
      Case "1":
        WinMinimize "ahk_pid " . KodiPID
    }
  }

  Return
}

; ----------------------------------------------------------------------------------------------------------------------
OpenKodi() {
  ; Execute post-Playnite script.
  If (PostScript != "false") {
    RunWait '"' . PostScript . '"',, "Hide"
  }

  ; If Kodi is running for the current user, but minimized, restore the window.
  KodiPID := ProcessExist(KodiExe, A_UserName)
  If (KodiPID > 0) {
    If (QuitOrMinKodi = "1") And (WinExist("ahk_class " . KodiClass)) {
      ;WinRestore "ahk_pid " . KodiPID
      WinActivate "ahk_class " . KodiClass
    }
  }

  ; Run the Kodi executable if the script closed it earlier.
  If (QuitOrMinKodi = "0") {
    varRunCmd := KodiExe

    ; Check if it should run in portable mode or not.
    If (PortableKodi = "true") {
      varRunCmd := varRunCmd . " -p"
    }

    Try {
      ; Launch Kodi.
      Run varRunCmd, KodiDir
    }
    Catch {
      Msgbox "There was an error trying to run the Kodi exe."
      ExitApp
    }
  }

  ; Wait for Kodi to load. Set timeout, so this script doesn't hang.
  WinWaitActive "ahk_class " . KodiClass,, 10

  ; ----------------------------------------------------------------------------------------------------------------------
  ; Check if Playnite re-opened after an update or the user switched to the desktop / fullscreen exe.
  varHwnd := WinWaitActive(PlayniteWindowTitle,, 30)
  If (varHwnd > 0) {
    ; Set the PID variable again. Try the fullscreen exe first.
    PlaynitePID := ProcessExist(PlayniteFullscreenExe, A_UserName)
    If (PlaynitePID > 0) {
      PlayniteExe := PlayniteFullscreenExe
    }
    Else {
      ; Fullscreen wasn't found so the desktop exe should be active then.
      PlaynitePID := ProcessExist(PlayniteDesktopExe, A_UserName)
      If (PlaynitePID > 0) {
        PlayniteExe := PlayniteDesktopExe
      }
    }

    If (PlaynitePID > 0) {
      ; Unhook events just in case; we'll be adding new event hooks.
      WinHook.Event.UnHookAll()

      ; Run the pre-Playnite script again if needed.
      If (PreScript != "false")
      {
        RunWait '"' . PreScript . '"',, "Hide"
      }

      ; Go back to listening for the close event.
      SetPlayniteHook(PlaynitePID)
    }
  }
  Else {
    ; Close the script.
    ExitApp
  }
}

; ----------------------------------------------------------------------------------------------------------------------
; Call this function with the PID you need info from. Ex: GetProcessInfo(21964)
GetProcessInfo(vPid) {
  If (WinExist("ahk_pid " . vPid)) {
    varHwnd := WinGetID("ahk_pid " . vPid)
    varProcessName := WinGetProcessName("ahk_pid " . vPid)
    varWindowTitle := WinGetTitle("ahk_exe " . varProcessName)
    varWindowClass := WinGetClass("ahk_exe " . varProcessName)
    MsgBox "PID: " . vPid . "`n" . "hWnd: " . varHwnd . "`n" . "Process name: " . varProcessName . "`n" . "Window title: " . varWindowTitle . "`n" . "Window class: " . varWindowClass
  }
  Else (
    MsgBox "Unable to find window for PID: " . vPid
  )
}

; ----------------------------------------------------------------------------------------------------------------------
; Simulate the Process, Exist command, but apply a filter for the current user.
ProcessExist(varProcessName, varUserName := "") {
  varQuery := "Select ProcessId from Win32_Process WHERE Name LIKE '%" . varProcessName . "%'"

  For objProcess in ComObjGet("winmgmts:{impersonationLevel=impersonate}!\\.\root\cimv2").ExecQuery(varQuery, "WQL", 48) {
    ; If GetOwner returns 0, then it succeeded.
    If (objProcess.GetOwner(varUserName) = 0) {
        ; This will exit the loop early with the PID.
        Return objProcess.processID
    }
  }
  ; If we've landed outside the loop, then the process wasn't found. Simulate the Process, Exist command by returning 0.
  Return 0
}

; ----------------------------------------------------------------------------------------------------------------------
; This event is only fired when Playnite is closed, re-open Kodi.
PlayniteClosedEvent(hWinEventHook, Win_Event, Win_Hwnd, idObject, idChild, dwEventThread, dwmsEventTime) {
  OpenKodi()
}

; This event is only fired when Playnite is minimized, re-open Kodi.
; PlayniteMinimizedEvent(hWinEventHook, Win_Event, Win_Hwnd, idObject, idChild, dwEventThread, dwmsEventTime)
; {
;   OpenKodi()
; }
