# Playnite Launcher
An add-on for Kodi to launch the Playnite video game manager (Windows).

The goal is to provide an easy method for Kodi to launch Playnite in full screen, in order to have a better HTPC experience. Playnite is an open source video game library manager with one simple goal: To provide a unified interface for all of your games.

**THIS ADD-ON WAS DERIVED FROM AND INSPIRED BY MULTIPLE SCRIPTS:**<br/>
Steam Launcher by teeedub: https://github.com/teeedubb/teeedubb-xbmc-repo & http://forum.xbmc.org/showthread.php?tid=157499<br/>
Kodi-Launches-Playnite-Addon by hoksilato2: https://github.com/hoksilato2/Kodi-Launches-Playnite-Addon<br/>
(which was forked from) Kodi-Launches-Steam-Addon by BrosMakingSoftware: https://github.com/BrosMakingSoftware/Kodi-Launches-Steam-Addon<br/>
Credit goes to them for their open source projects that enabled me to build upon their work.

### Info you might like to know about this add-on
- All code is open source, hosted on [GitHub](https://github.com/robbforce/script.playnite.launcher) and published under the GPL v3 license.
- Created for Kodi v17 (Krypton v17.x or higher) and following most [Add-on rules](http://kodi.wiki/view/Add-on_rules). (The compiled autohotkey script is an exception.)
- To find Applications/Programs paths, this add-on relies on default environment variables found in Windows. No _"registry-hack"_ programs are used for this purpose.
- No 3rd-party libraries from unknown sources or with confusing distribution licenses. What you see on this repository is exactly what you need to run the addon. All code is written in Python and AutoHotKey script and all source is available.
- Respects your privacy by not collecting any kind of hardware / software information, usage statistics or any kind of data from you or your system

**Notes:**
This add-on is just a launcher, so it assumes that you've already installed and configured Playnite on your system. It will not assist you in installing or configuring Playnite, nor will it download games.

![addon-information.jpg](/resources/addon-screenshots/addon-information.jpg)


## Installation

#### Prerequisites
Hopefully you've already done this, but if not, you'll need to install Kodi. Download it from https://kodi.tv/ and install / configure it.
You'll also need to install and configure Playnite, which can be downloaded from https://playnite.link/ or from [Github](https://github.com/JosefNemec/Playnite), where you can also find the source. Configuration help can be found in the [wiki](https://github.com/JosefNemec/Playnite/wiki).

#### Steps
1. Download the add-on: This add-on is not currently registered on any official or unofficial Kodi repositories, therefore you'll need to install it from a zip file. Go to the [releases](https://github.com/robbforce/script.playnite.launcher/releases) page and download the latest zip file.

2. Start Kodi and navigate to `Settings -> System -> Add-ons` and enable `Unkown sources`. This setting is required until this add-on can be added to an official repository (hopefully).

3. Navigate to `Settings -> Add-ons -> Add-on browser -> Install from zip file`. In the file browser look for the zip file you downloaded in the first step and select it. Installation should be immediate and Kodi will show a notification when it's done.

4. Once the Addon is installed, navigate to Game or Program add-ons and you will see Playnite listed there.

   ![addon-selected.jpg](/resources/addon-screenshots/addon-selected.jpg)

5. Check and change the add-on settings by selecting the Playnite add-on and bringing up the contextual menu by right-clicking it (or pressing the `Guide` button on a remote, pressing `C` key on a keyboard, pressing `X` button on Xbox or `Square` button on PlayStation controllers) and selecting `Settings`.

   ![addon-settings-01.jpg](/resources/addon-screenshots/addon-settings-01.jpg)

   The settings are divided into two tabs: the `General` tab (displayed above) contains the executable paths, and the `Advanced` tab (displayed below) contains settings to  control how the add-on interacts with Kodi, pre-Playnite scripts, etc. You should set the executable paths if you've installed Kodi or Playnite in non-default folders.

   ![addon-settings-02.jpg](/resources/addon-screenshots/addon-settings-02.jpg)

6. Run the add-on and enjoy!
