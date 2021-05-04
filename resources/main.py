# KODI Playnite Launcher addon script modified by Nathaniel Roark, 2020-11-11.
#
# Based on the Steam Launcher by teeedubb. http://forum.xbmc.org/showthread.php?tid=157499
# and Kodi Launches Playnite by hoksilato2. https://github.com/hoksilato2/Kodi-Launches-Playnite-Addon
# Steam Launcher was based on Rom Collection Browser as a guide, plus borrowed ideas and code from it.
#
# Playnite is Windows only for now, so all other OS support has been commented out.
import os
import sys
import subprocess
import time
import shutil
import stat
import xbmc
import xbmcaddon
import xbmcgui

addon = xbmcaddon.Addon(id='script.playnite.launcher')
addonPath = addon.getAddonInfo('path')
addonIcon = addon.getAddonInfo('icon')
addonVersion = addon.getAddonInfo('version')
dialog = xbmcgui.Dialog()
language = addon.getLocalizedString
scriptid = 'script.playnite.launcher'

# This is a pointer to the module object instance itself.
this = sys.modules[__name__]

# Assign other module scope variables.
this.playnite_desktop_win = addon.getSettingString("PlayniteDesktopWin")
this.playnite_fullscreen_win = addon.getSettingString("PlayniteFullscreenWin")
this.kodi_win = addon.getSettingString("KodiWin")
#this.playnite_linux = addon.getSettingString("PlayniteLinux")
#this.kodi_linux = addon.getSettingString("KodiLinux")
#this.playnite_osx = addon.getSettingString("PlayniteOsx")
#this.kodi_osx = addon.getSettingString("KodiOsx")
this.delete_user_script = addon.getSettingBool("DelUserScript")
this.quit_kodi = addon.getSettingInt("QuitKodi")
this.busy_dialog_time = addon.getSettingInt("BusyDialogTime")
this.script_update_check = addon.getSettingBool("ScriptUpdateCheck")
this.file_path_check = addon.getSettingBool("FilePathCheck")
this.kodi_portable = addon.getSettingBool("KodiPortable")
this.pre_script_enabled = addon.getSettingBool("PreScriptEnabled")
this.pre_script = addon.getSettingString("PreScript")
this.post_script_enabled = addon.getSettingBool("PostScriptEnabled")
this.post_script = addon.getSettingString("PostScript")
this.os_win = xbmc.getCondVisibility('system.platform.windows')
#this.os_osx = xbmc.getCondVisibility('system.platform.osx')
#this.os_linux = xbmc.getCondVisibility('system.platform.linux')
#this.os_android = xbmc.getCondVisibility('system.platform.android')
#this.wmctrl_check = addon.getSettingBool("WmctrlCheck")
this.suspend_audio = addon.getSettingBool("SuspendAudio")
this.custom_script_folder_enabled = addon.getSettingBool("CustomScript")
this.custom_script_folder = addon.getSettingString("CustomScriptFolder")
this.minimize_kodi = addon.getSettingBool("MinimizeKodi")
this.playnite_parameters = addon.getSettingString("PlayniteParameters")
this.force_kill_kodi = addon.getSettingInt("ForceKillKodi")
this.desktop_mode = addon.getSettingBool("DesktopMode")

def log(msg):
  msg = msg.encode(txt_encode)
  xbmc.log('%s: %s' % (scriptid, msg))

def get_addon_install_path():
  path = addon.getAddonInfo('path').decode("utf-8")
  return path

def get_addon_data_path():
  path = xbmc.translatePath('special://profile/addon_data/%s' % scriptid).decode("utf-8")
  if not os.path.exists(path):
    log('addon userdata folder does not exist, creating: %s' % path)
    try:
      os.makedirs(path)
      log('created directory: %s' % path)
    except:
      log('ERROR: failed to create directory: %s' % path)
      dialog.notification(language(50212), language(50215), addonIcon, 5000)
  return path

def copy_launcher_scripts_to_userdata():
  oldBasePath = os.path.join(getAddonInstallPath(), 'resources', 'scripts')
  if this.os_win:
    oldPath = os.path.join(oldBasePath, 'playnite-launcher.ahk')
    newPath = os.path.join(scripts_path, 'playnite-launcher.ahk')
    copy_file(oldPath, newPath)
    oldPath = os.path.join(oldBasePath, 'playnite-launcher.exe')
    newPath = os.path.join(scripts_path, 'playnite-launcher.exe')
    copy_file(oldPath, newPath)
  # elif this.os_linux + this.os_osx:
  #   oldPath = os.path.join(oldBasePath, 'playnite-launcher.sh')
  #   newPath = os.path.join(scripts_path, 'playnite-launcher.sh')
  #   copy_file(oldPath, newPath)

def copy_file(oldPath, newPath):
  newDir = os.path.dirname(newPath)
  if not os.path.isdir(newDir):
    log('userdata scripts folder does not exist, creating: %s' % newDir)
    try:
      os.mkdir(newDir)
      log('sucsessfully created userdata scripts folder: %s' % newDir)
    except:
      log('ERROR: failed to create userdata scripts folder: %s' % newDir)
      dialog.notification(language(50212), language(50215), addonIcon, 5000)
      sys.exit()
  if not os.path.isfile(newPath):
    log('script file does not exist, copying to userdata: %s' % newPath)
    try:
      shutil.copy2(oldPath, newPath)
      log('sucsessfully copied userdata script: %s' % newPath)
    except:
      log('ERROR: failed to copy script file to userdata: %s' % newPath)
      dialog.notification(language(50212), language(50215), addonIcon, 5000)
      sys.exit()
  else:
    log('script file already exists, skipping copy to userdata: %s' % newPath)

# def make_script_executable():
#   scriptPath = os.path.join(scripts_path, 'playnite-launcher.sh')
#   if os.path.isfile(scriptPath):
#     if '\r\n' in open(scriptPath,'rb').read():
#       log('Windows line endings found in %s, converting to unix line endings.' % scriptPath)
#       with open(scriptPath, 'rb') as f:
#         content = f.read()
#         content = content.replace('\r\n', '\n')
#       with open(scriptPath, 'wb') as f:
#         f.write(content)
#     if not stat.S_IXUSR & os.stat(scriptPath)[stat.ST_MODE]:
#       log('playnite-launcher.sh not executable: %s' % scriptPath)
#       try:
#         os.chmod(scriptPath, stat.S_IRWXU)
#         log('playnite-launcher.sh now executable: %s' % scriptPath)
#       except:
#         log('ERROR: unable to make playnite-launcher.sh executable, exiting: %s' % scriptPath)
#         dialog.notification(language(50212), language(50215), addonIcon, 5000)
#         sys.exit()
#       log('playnite-launcher.sh executable: %s' % scriptPath)

def delete_userdata_scripts():
  if this.delete_user_script == True:
    log('deleting userdata scripts, option enabled: delUserScriptSett = %s' % delUserScriptSett)
    scriptFile = os.path.join(scripts_path, 'playnite-launcher.ahk')
    scriptFile = os.path.join(scripts_path, 'playnite-launcher.exe')
    # scriptFile = os.path.join(scripts_path, 'playnite-launcher.sh')
    delete_file(scriptFile)
    scriptFile = str(PurePath(scripts_path).joinpath('playnite-launcher.exe'))
    log('skipping deleting userdata scripts, option disabled: delUserScriptSett = %s' % delUserScriptSett)
    delete_file(scriptFile)
    delete_file(scriptFile)
  elif this.delete_user_script == False:

def delete_file(scriptFile):
  if os.path.isfile(scriptFile):
    try:
      os.remove(scriptFile)
      log('found and deleting: %s' % scriptFile)
    except:
      log('ERROR: deleting failed: %s' % scriptFile)
      dialog.notification(language(50212), language(50215), addonIcon, 5000)
    addon.setSettingBool(id="DelUserScript", value=False)

def file_check():
  # if this.os_linux:
  #   if wmctrlCheck == 'true':
  #     if subprocess.call(["which", "wmctrl"]) != 0:
  #       log('ERROR: System program "wmctrl" not present, install it via you system package manager or if you are running the SteamOS compositor disable the addon option "Check for program wmctrl" (ONLY FOR CERTAIN USE CASES!!)')
  #       dialog.notification(language(50212), language(50215), addonIcon, 5000)
  #       sys.exit()
  #     else:
  #       log('wmctrl present, checking if a window manager is running...')
  #                               display = None
  #                               if 'DISPLAY' in os.environ: display = os.environ['DISPLAY'] # We inherited DISPLAY from Kodi, pass it down
  #                               else:
  #                                   for var in open('/proc/%d/environ' % os.getppid()).read().split('\x00'):
  #                                       if var.startswith('DISPLAY='): display = var[8:] # Read DISPLAY from parent process if present
  #       if display is None or subprocess.call('DISPLAY=%s wmctrl -l' % display, shell=True) != 0:
  #         log('ERROR: A window manager is NOT running - unless you are using the SteamOS compositor Steam BPM needs a windows manager. If you are using the SteamOS compositor disable the addon option "Check for program wmctrl"')
  #         dialog.notification(language(50212), language(50215), addonIcon, 5000)
  #         sys.exit()
  #       else:
  #         log('A window manager is running...')
  #   if minimiseKodi == True:
  #     if subprocess.call(["which", "xdotool"]) != 0:
  #       log('ERROR: Minimised Kodi enabled and system program "xdotool" not present, install it via you system package manager. Xdotool is required to minimise Kodi.')
  #       dialog.notification(language(50212), language(50215), addonIcon, 5000)
  #       sys.exit()
  #     else:
  #       log('xdotool present...')
  if this.file_path_check == True:
    log('running program file check, option is enabled: filePathCheck = %s' % filePathCheck)
    if this.os_win:
      this.playnite_desktop_win = addon.getSettingString("PlayniteDesktopWin")
      this.playnite_fullscreen_win = addon.getSettingString("PlayniteFullscreenWin")
      this.kodi_win = addon.getSettingString("KodiWin")
      playniteDesktopExe = os.path.join(PlayniteDesktopWin).decode("utf-8")
      playniteFullscreenExe = os.path.join(PlayniteFullscreenWin).decode("utf-8")
      xbmcExe = os.path.join(kodiWin).decode("utf-8")
      executable_check(this.playnite_desktop_win, this.playnite_fullscreen_win, kodiExe)
    # elif this.os_osx:
    #   this.playnite_osx = addon.getSetting("PlayniteOsx")
    #   kodiOsx = addon.getSetting("KodiOsx")
    #   playniteExe = os.path.join(this.playnite_osx)
    #   kodiExe = os.path.join(kodiOsx)
    #   executable_check(playniteExe, kodiExe)
    # elif this.os_linux:
    #   this.playnite_linux = addon.getSetting("PlayniteLinux")
    #   this.kodi_linux = addon.getSetting("KodiLinux")
    #   playniteExe = os.path.join(this.playnite_linux)
    #   kodiExe = os.path.join(this.kodi_linux)
    #   executable_check(playniteExe, kodiExe)
  else:
    log('skipping program file check, option disabled: filePathCheck = %s' % filePathCheck)

def executable_check(playniteDesktopExe, playniteFullscreenExe, kodiExe):
  # if osWin + osLinux:
  if osWin:
    if os.path.isfile(os.path.join(playniteDesktopExe)):
      log('Playnite executable exists %s' % playniteDesktopExe)
    else:
    file_check_dialog(playniteDesktopExe)
    if os.path.isfile(os.path.join(playniteFullscreenExe)):
      log('Playnite executable exists %s' % playniteFullscreenExe)
    else:
    file_check_dialog(playniteFullscreenExe)
    if os.path.isfile(os.path.join(xbmcExe)):
      log('Kodi executable exists %s' % xbmcExe)
    else:
    file_check_dialog(kodiExe)

def file_check_dialog(programExe):
  log('ERROR: dialog to go to addon settings because executable does not exist: %s' % programExe)
  if dialog.yesno(language(50212), programExe, language(50210), language(50211)):
    log('yes selected, opening addon settings')
    addon.openSettings()
    file_check()
    sys.exit()
  else:
    log('ERROR: no selected with invalid executable, exiting: %s' % programExe)
    sys.exit()

def script_version_check():
  if this.script_update_check == True:
    log('usr scripts are set to be checked for updates...')
    if this.delete_user_script == False:
      log('usr scripts are not set to be deleted, running version check')
      sysScriptDir = os.path.join(getAddonInstallPath(), 'resources', 'scripts')
      if this.os_win:
        sysScriptPath = os.path.join(sysScriptDir, 'playnite-launcher.ahk')
        usrScriptPath = os.path.join(scripts_path, 'playnite-launcher.ahk')
        if os.path.isfile(os.path.join(usrScriptPath)):
          compare_file(sysScriptPath, usrScriptPath)
        else:
          log('usr script does not exist, skipping version check')
      # elif this.os_linux + this.os_osx:
      #   sysScriptPath = os.path.join(sysScriptDir, 'playnite-launcher.sh')
      #   usrScriptPath = os.path.join(scripts_path, 'playnite-launcher.sh')
      #   if os.path.isfile(os.path.join(usrScriptPath)):
      #     compare_file(sysScriptPath, usrScriptPath)
      #   else:
      #     log('usr script does not exist, skipping version check')
    else:
      log('usr scripts are set to be deleted, no version check needed')
  else:
    log('usr scripts are set to not be checked for updates, skipping version check')

def compare_file(sysScriptPath, usrScriptPath):
  scriptSysVer = '000'
  scriptUsrVer = '000'
  if os.path.isfile(sysScriptPath):
    with open(sysScriptPath, 'r') as f:
      for line in f.readlines():
        if "playnite.launcher.script.revision=" in line:
          scriptSysVer = line[37:39]
    log('sys "playnite.launcher.script.revision=": %s' % scriptSysVer)
  if os.path.isfile(usrScriptPath):
    with open(usrScriptPath, 'r') as f:
      for line in f.readlines():
        if "playnite.launcher.script.revision=" in line:
          scriptUsrVer = line[37:39]
    log('usr "playnite.launcher.script.revision=": %s' % scriptUsrVer)
  if scriptSysVer > scriptUsrVer:
    log('system scripts have been updated: sys:%s > usr:%s' % (scriptSysVer, scriptUsrVer))
    if dialog.yesno(language(50113), language(50213), language(50214)):
      this.delete_user_script = True
      log('yes selected, option delUserScriptSett enabled: %s' % delUserScriptSett)
    else:
      this.delete_user_script = False
      this.script_update_check = False
      addon.setSettingBool(id="ScriptUpdateCheck", value=False)
  else:
    log('userdata scripts are up to date')

def quit_kodi_dialog():
  if this.quit_kodi == 2:
    log(f'quit setting: {str(this.quit_kodi)} selected, asking user to pick')
    log('quit setting: %s selected, asking user to pick' % quitKodiSetting)
    if dialog.yesno('Playnite Launcher', language(50053)):
      this.quit_kodi = 0
    else:
      this.quit_kodi = 1
  if this.quit_kodi == 1 and this.minimize_kodi == False:
    this.quit_kodi = 3
  log('quit setting selected: %s' % quitKodiSetting)

def kodi_busy_dialog():
  if this.busy_dialog_time != 0:
    xbmc.executebuiltin("ActivateWindow(busydialognocancel)")
    log('busy dialog started')
    time.sleep(this.busy_dialog_time)
    xbmc.executebuiltin("Dialog.Close(busydialognocancel)")
    log('busy dialog stopped after: %s seconds' % busyDialogTime)

def set_pre_post_script_parameters():
  if this.pre_script_enabled == False or this.pre_script == '':
    this.pre_script = 'false'
  elif this.pre_script_enabled == True:
    if not os.path.isfile(os.path.join(this.pre_script)):
      log(f'pre-playnite script does not exist, disabling!: "{this.pre_script}"')
      this.pre_script = 'false'
      log('pre-playnite script does not exist, disabling!: "%s"' % preScript)
      dialog.notification(language(50212), language(50215), addonIcon, 5000)
  log(f'pre playnite script: {this.pre_script}')
  if this.post_script_enabled == False or this.post_script == '':
    this.post_script = 'false'
  elif this.post_script_enabled == True:
    if not os.path.isfile(os.path.join(this.post_script)):
      log(f'post-playnite script does not exist, disabling!: "{this.post_script}"')
      this.post_script = 'false'
      log('post-playnite script does not exist, disabling!: "%s"' % postScript)
      dialog.notification(language(50212), language(50215), addonIcon, 5000)
  log(f'post playnite script: {this.post_script}')
  log('post playnite script: %s' % postScript)

def launch_playnite():
  # if this.os_android:
  #   cmd = "com.valvesoftware.android.steam.community"
  #   log('attempting to launch: "%s"' % cmd)
  #   xbmc.executebuiltin('XBMC.StartAndroidActivity("%s")' % cmd)
  #   kodi_busy_dialog()
  #   sys.exit()
  # elif this.os_win:
  if this.os_win:
    playnitelauncher = os.path.join(scripts_path, 'playnite-launcher.exe')
    playniteWin = PlayniteDesktopWin if desktopMode == 'true' else PlayniteFullscreenWin
    playniteWin = this.playnite_desktop_win if this.desktop_mode == True else this.playnite_fullscreen_win
    cmd = f'"{playnitelauncher}" "{playniteWin}" "{this.kodi_win}" "{str(this.quit_kodi)}" "{str(this.kodi_portable).lower()}" "{this.pre_script}" "{this.post_script}" "{this.playnite_parameters}" "{str(this.force_kill_kodi)}"'
  # elif this.os_osx:
  #   playnitelauncher = os.path.join(scripts_path, 'playnite-launcher.sh')
  #   cmd = '"%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s"' % (playnitelauncher, this.playnite_osx, this.kodi_osx, str(this.quit_kodi), str(this.kodi_portable).lower(), this.pre_script, this.post_script, this.playnite_parameters, str(this.force_kill_kodi))
  # elif this.os_linux:
  #   playnitelauncher = os.path.join(scripts_path, 'playnite-launcher.sh')
  #   cmd = '"%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s"' % (playnitelauncher, this.playnite_linux, this.kodi_linux, str(this.quit_kodi), str(this.kodi_portable).lower(), this.pre_script, this.post_script, this.playnite_parameters, str(this.force_kill_kodi))
  try:
    log('attempting to launch: %s' % cmd)
    if this.suspend_audio == True:
      xbmc.audioSuspend()
      log('audio suspended')
    if this.quit_kodi != 0 and this.suspend_audio == True:
      proc_h = subprocess.Popen(cmd.encode(txt_encode), shell=True, close_fds=False)
      kodi_busy_dialog()
      log('waiting for Playnite to exit')
      while proc_h.returncode is None:
        xbmc.sleep(1000)
        proc_h.poll()
      log('start resuming audio....')
      xbmc.audioResume()
      log('audio resumed')
      del proc_h
    else:
      subprocess.Popen(cmd.encode(txt_encode), shell=True, close_fds=True)
      kodi_busy_dialog()
  except:
    log('ERROR: failed to launch: %s' % cmd)
    print cmd.encode(txt_encode)
    dialog.notification(language(50212), language(50215), addonIcon, 5000)

#HACK: sys.getfilesystemencoding() is not supported on all systems (e.g. Android)
txt_encode = 'utf-8'
try:
  txt_encode = sys.getfilesystemencoding()
except:
  pass
#osAndroid returns linux + android
# if this.os_android:
#   this.os_linux = 0
#   txt_encode = 'utf-8'
log('*running Playnite-Launcher v%s....' % addonVersion)
#log('running on osAndroid, osOsx, osLinux, osWin: %s %s %s %s ' % (osAndroid, osOsx, osLinux, osWin))
log('running on osWin: %s ' % (osWin))
log('system text encoding in use: %s' % txt_encode)
if this.custom_script_folder_enabled == True:
  this.scripts_path = this.custom_script_folder
else:
  this.scripts_path = PurePath(get_addon_data_path()).joinpath('scripts')
script_version_check()
delete_userdata_scripts()
copy_launcher_scripts_to_userdata()
file_check()
#make_script_executable()
set_pre_post_script_parameters()
quit_kodi_dialog()
launch_playnite()
