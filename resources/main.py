
# KODI Playnite Launcher addon script modified by Nathaniel Roark, 2020-11-11.
#
# Based on the Steam Launcher by teeedubb. http://forum.xbmc.org/showthread.php?tid=157499
# and Kodi Launches Playnite by hoksilato2. https://github.com/hoksilato2/Kodi-Launches-Playnite-Addon
# Steam Launcher was based on Rom Collection Browser as a guide, plus borrowed ideas and code from it.
#
# Playnite is Windows only, so all other OS support has been commented out.
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

#playniteLinux = addon.getSetting("PlayniteLinux").decode("utf-8")
#kodiLinux = addon.getSetting("KodiLinux").decode("utf-8")
PlayniteDesktopWin = addon.getSetting("PlayniteDesktopWin").decode("utf-8")
PlayniteFullscreenWin = addon.getSetting("PlayniteFullscreenWin").decode("utf-8")
kodiWin = addon.getSetting("KodiWin").decode("utf-8")
#playniteOsx = addon.getSetting("PlayniteOsx").decode("utf-8")
#kodiOsx = addon.getSetting("KodiOsx").decode("utf-8")
delUserScriptSett = addon.getSetting("DelUserScript")
quitKodiSetting = addon.getSetting("QuitKodi")
busyDialogTime = int(addon.getSetting("BusyDialogTime"))
scriptUpdateCheck = addon.getSetting("ScriptUpdateCheck")
filePathCheck = addon.getSetting("FilePathCheck")
kodiPortable = addon.getSetting("KodiPortable")
preScriptEnabled = addon.getSetting("PreScriptEnabled")
preScript = addon.getSetting("PreScript").decode("utf-8")
postScriptEnabled = addon.getSetting("PostScriptEnabled")
postScript = addon.getSetting("PostScript").decode("utf-8")
osWin = xbmc.getCondVisibility('system.platform.windows')
osOsx = xbmc.getCondVisibility('system.platform.osx')
osLinux = xbmc.getCondVisibility('system.platform.linux')
osAndroid = xbmc.getCondVisibility('system.platform.android')
#wmctrlCheck = addon.getSetting("WmctrlCheck")
suspendAudio = addon.getSetting("SuspendAudio")
customScriptFolder = addon.getSetting("CustomScriptFolder").decode("utf-8")
customScriptFolderEnabled = addon.getSetting("CustomScript")
minimiseKodi = addon.getSetting("MinimiseKodi")
playniteParameters = addon.getSetting("PlayniteParameters")
forceKillKodi = addon.getSetting("ForceKillKodi")
desktopMode = addon.getSetting("DesktopMode")

def log(msg):
  msg = msg.encode(txt_encode)
  xbmc.log('%s: %s' % (scriptid, msg))

def getAddonInstallPath():
  path = addon.getAddonInfo('path').decode("utf-8")
  return path

def getAddonDataPath():
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

def copyLauncherScriptsToUserdata():
  oldBasePath = os.path.join(getAddonInstallPath(), 'resources', 'scripts')
  if osWin:
    oldPath = os.path.join(oldBasePath, 'playnite-launcher.ahk')
    newPath = os.path.join(scripts_path, 'playnite-launcher.ahk')
    copyFile(oldPath, newPath)
    oldPath = os.path.join(oldBasePath, 'playnite-launcher.exe')
    newPath = os.path.join(scripts_path, 'playnite-launcher.exe')
    copyFile(oldPath, newPath)
  # elif osLinux + osOsx:
  #   oldPath = os.path.join(oldBasePath, 'playnite-launcher.sh')
  #   newPath = os.path.join(scripts_path, 'playnite-launcher.sh')
  #   copyFile(oldPath, newPath)

def copyFile(oldPath, newPath):
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

# def makeScriptExec():
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

def usrScriptDelete():
  if delUserScriptSett == 'true':
    log('deleting userdata scripts, option enabled: delUserScriptSett = %s' % delUserScriptSett)
    scriptFile = os.path.join(scripts_path, 'playnite-launcher.ahk')
    delUserScript(scriptFile)
    scriptFile = os.path.join(scripts_path, 'playnite-launcher.exe')
    delUserScript(scriptFile)
    # scriptFile = os.path.join(scripts_path, 'playnite-launcher.sh')
    # delUserScript(scriptFile)
  elif delUserScriptSett == 'false':
    log('skipping deleting userdata scripts, option disabled: delUserScriptSett = %s' % delUserScriptSett)

def delUserScript(scriptFile):
  if os.path.isfile(scriptFile):
    try:
      os.remove(scriptFile)
      log('found and deleting: %s' % scriptFile)
    except:
      log('ERROR: deleting failed: %s' % scriptFile)
      dialog.notification(language(50212), language(50215), addonIcon, 5000)
    addon.setSetting(id="DelUserScript", value="false")

def fileChecker():
  # if osLinux:
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
  #   if minimiseKodi == "true":
  #     if subprocess.call(["which", "xdotool"]) != 0:
  #       log('ERROR: Minimised Kodi enabled and system program "xdotool" not present, install it via you system package manager. Xdotool is required to minimise Kodi.')
  #       dialog.notification(language(50212), language(50215), addonIcon, 5000)
  #       sys.exit()
  #     else:
  #       log('xdotool present...')
  if filePathCheck == 'true':
    log('running program file check, option is enabled: filePathCheck = %s' % filePathCheck)
    if osWin:
      PlayniteDesktopWin = addon.getSetting("PlayniteDesktopWin").decode("utf-8")
      PlayniteFullscreenWin = addon.getSetting("PlayniteFullscreenWin").decode("utf-8")
      kodiWin = addon.getSetting("KodiWin").decode("utf-8")
      playniteDesktopExe = os.path.join(PlayniteDesktopWin).decode("utf-8")
      playniteFullscreenExe = os.path.join(PlayniteFullscreenWin).decode("utf-8")
      xbmcExe = os.path.join(kodiWin).decode("utf-8")
      programFileCheck(PlayniteDesktopWin, PlayniteFullscreenWin, xbmcExe)
    # elif osOsx:
    #   playniteOsx = addon.getSetting("PlayniteOsx")
    #   kodiOsx = addon.getSetting("KodiOsx")
    #   playniteExe = os.path.join(playniteOsx).decode("utf-8")
    #   xbmcExe = os.path.join(kodiOsx).decode("utf-8")
    #   programFileCheck(playniteExe, xbmcExe)
    # elif osLinux:
    #   playniteLinux = addon.getSetting("PlayniteLinux")
    #   kodiLinux = addon.getSetting("KodiLinux")
    #   playniteExe = os.path.join(playniteLinux).decode("utf-8")
    #   xbmcExe = os.path.join(kodiLinux).decode("utf-8")
    #   programFileCheck(playniteExe, xbmcExe)
  else:
    log('skipping program file check, option disabled: filePathCheck = %s' % filePathCheck)

def programFileCheck(playniteDesktopExe, playniteFullscreenExe, xbmcExe):
  # if osWin + osLinux:
  if osWin:
    if os.path.isfile(os.path.join(playniteDesktopExe)):
      log('Playnite executable exists %s' % playniteDesktopExe)
    else:
      fileCheckDialog(playniteDesktopExe)
    if os.path.isfile(os.path.join(playniteFullscreenExe)):
      log('Playnite executable exists %s' % playniteFullscreenExe)
    else:
      fileCheckDialog(playniteFullscreenExe)
    if os.path.isfile(os.path.join(xbmcExe)):
      log('Kodi executable exists %s' % xbmcExe)
    else:
      fileCheckDialog(xbmcExe)
  # if osOsx:
  #   if os.path.isdir(os.path.join(playniteExe)):
  #     log('Playnite folder exists %s' % playniteExe)
  #   else:
  #     fileCheckDialog(playniteExe)
  #   if os.path.isdir(os.path.join(xbmcExe)):
  #     log('Xbmc executable exists %s' % xbmcExe)
  #   else:
  #     fileCheckDialog(xbmcExe)

def fileCheckDialog(programExe):
  log('ERROR: dialog to go to addon settings because executable does not exist: %s' % programExe)
  if dialog.yesno(language(50212), programExe, language(50210), language(50211)):
    log('yes selected, opening addon settings')
    addon.openSettings()
    fileChecker()
    sys.exit()
  else:
    log('ERROR: no selected with invalid executable, exiting: %s' % programExe)
    sys.exit()

def scriptVersionCheck():
  if scriptUpdateCheck == 'true':
    log('usr scripts are set to be checked for updates...')
    if delUserScriptSett == 'false':
      log('usr scripts are not set to be deleted, running version check')
      sysScriptDir = os.path.join(getAddonInstallPath(), 'resources', 'scripts')
      if osWin:
        sysScriptPath = os.path.join(sysScriptDir, 'playnite-launcher.ahk')
        usrScriptPath = os.path.join(scripts_path, 'playnite-launcher.ahk')
        if os.path.isfile(os.path.join(usrScriptPath)):
          compareFile(sysScriptPath, usrScriptPath)
        else:
          log('usr script does not exist, skipping version check')
      # elif osLinux + osOsx:
      #   sysScriptPath = os.path.join(sysScriptDir, 'playnite-launcher.sh')
      #   usrScriptPath = os.path.join(scripts_path, 'playnite-launcher.sh')
      #   if os.path.isfile(os.path.join(usrScriptPath)):
      #     compareFile(sysScriptPath, usrScriptPath)
      #   else:
      #     log('usr script does not exist, skipping version check')
    else:
      log('usr scripts are set to be deleted, no version check needed')
  else:
    log('usr scripts are set to not be checked for updates, skipping version check')

def compareFile(sysScriptPath, usrScriptPath):
  global delUserScriptSett
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
      delUserScriptSett = 'true'
      log('yes selected, option delUserScriptSett enabled: %s' % delUserScriptSett)
    else:
      delUserScriptSett = 'false'
      log('no selected, script update check disabled: ScriptUpdateCheck = %s' % scriptUpdateCheck)
  else:
    log('userdata scripts are up to date')

def quitKodiDialog():
  global quitKodiSetting
  if quitKodiSetting == '2':
    log('quit setting: %s selected, asking user to pick' % quitKodiSetting)
    if dialog.yesno('Playnite Launcher', language(50053)):
      quitKodiSetting = '0'
    else:
      quitKodiSetting = '1'
  if quitKodiSetting == '1' and minimiseKodi == "false":
    quitKodiSetting = '3'
  log('quit setting selected: %s' % quitKodiSetting)

def kodiBusyDialog():
  if busyDialogTime != 0:
    xbmc.executebuiltin("ActivateWindow(busydialognocancel)")
    log('busy dialog started')
    time.sleep(busyDialogTime)
    xbmc.executebuiltin("Dialog.Close(busydialognocancel)")
    log('busy dialog stopped after: %s seconds' % busyDialogTime)

def playnitePrePost():
  global postScript
  global preScript
  if preScriptEnabled == 'false':
    preScript = 'false'
  elif preScriptEnabled == 'true':
    if not os.path.isfile(os.path.join(preScript)):
      log('pre-playnite script does not exist, disabling!: "%s"' % preScript)
      preScript = 'false'
      dialog.notification(language(50212), language(50215), addonIcon, 5000)
  elif preScript == '':
    preScript = 'false'
  log('pre playnite script: %s' % preScript)
  if postScriptEnabled == 'false':
    postScript = 'false'
  elif preScriptEnabled == 'true':
    if not os.path.isfile(os.path.join(postScript)):
      log('post-playnite script does not exist, disabling!: "%s"' % postScript)
      postScript = 'false'
      dialog.notification(language(50212), language(50215), addonIcon, 5000)
  elif postScript == '':
    postScript = 'false'
  log('post playnite script: %s' % postScript)

def launchPlaynite():
  # if osAndroid:
  #   cmd = "com.valvesoftware.android.steam.community"
  #   log('attempting to launch: "%s"' % cmd)
  #   xbmc.executebuiltin('XBMC.StartAndroidActivity("%s")' % cmd)
  #   kodiBusyDialog()
  #   sys.exit()
  # elif osWin:
  if osWin:
    playnitelauncher = os.path.join(scripts_path, 'playnite-launcher.exe')
    playniteWin = PlayniteDesktopWin if desktopMode == 'true' else PlayniteFullscreenWin
    cmd = '"%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s"' % (playnitelauncher, playniteWin, kodiWin, quitKodiSetting, kodiPortable, preScript, postScript, playniteParameters, forceKillKodi)
  # elif osOsx:
  #   playnitelauncher = os.path.join(scripts_path, 'steam-launcher.sh')
  #   cmd = '"%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s"' % (steamlauncher, steamOsx, kodiOsx, quitKodiSetting, kodiPortable, preScript, postScript, steamParameters, forceKillKodi, desktopMode)
  # elif osLinux:
  #   playnitelauncher = os.path.join(scripts_path, 'steam-launcher.sh')
  #   cmd = '"%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s" "%s"' % (playnitelauncher, playniteLinux, kodiLinux, quitKodiSetting, kodiPortable, preScript, postScript, playniteParameters, forceKillKodi, desktopMode)
  try:
    log('attempting to launch: %s' % cmd)
    print cmd.encode('utf-8')
    if suspendAudio == 'true':
      xbmc.audioSuspend()
      log('audio suspended')
    if quitKodiSetting != '0' and suspendAudio == 'true':
      proc_h = subprocess.Popen(cmd.encode(txt_encode), shell=True, close_fds=False)
      kodiBusyDialog()
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
      kodiBusyDialog()
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
# if osAndroid:
#   osLinux = 0
#   txt_encode = 'utf-8'
log('*running Playnite-Launcher v%s....' % addonVersion)
#log('running on osAndroid, osOsx, osLinux, osWin: %s %s %s %s ' % (osAndroid, osOsx, osLinux, osWin))
log('running on osWin: %s ' % (osWin))
log('system text encoding in use: %s' % txt_encode)
if customScriptFolderEnabled == 'true':
  scripts_path = customScriptFolder
else:
  scripts_path = os.path.join(getAddonDataPath(), 'scripts')
scriptVersionCheck()
usrScriptDelete()
copyLauncherScriptsToUserdata()
fileChecker()
#makeScriptExec()
playnitePrePost()
quitKodiDialog()
launchPlaynite()
