
# Linux Automation
This is a suite of scripts that
1. Provides convenience functionalities to make daily computing nicer. 
2. attempts to automate the process of installing and configuring most of the software I would put on any fresh Linux installation to make it usable to me. 


    
## **3rd party software it installs:**

### Dependencies
- Zenity
- tree
- python modules 
	- ipython 
	- PyQt5, pandas, mutagen, colorama, progress 
-GNOME extensions
	- Window Calls

### Non-dependencies
-GNOME extensions
	- Alphabetical App Grid
	- AppIndicator and KStatusNotifierItem Support
	- Dash To Panel
	- Media Controls
	- NoAnnoyance v2
	- User Themes
- Keyd
- git
- Spotify Adblocker
	- Rust (dependency)
- VSCode
- Obsidian 
- Transmission
- Deemix
- Veracrypt
- Transmission
- Soulseek
  
  

## **Things it configures:**

- SSH
	- create rsa and ed25519 keys and add them to the ssh agent 
	- add keys to Github
- Cinnamon (and possible other desktop environments that use dconf)
	- keyboard shutcuts
	- taskbar
	- make symlinks in `~/.local/share/applications` to the .desktop files in `@data/AppImages`
- bash
	- aliases
	- auto-completion tweaks
- Keyd
- Nemo
	- add context menu scripts to ~/.local/share/nemo/scripts
- PYTHONPATH
    - add jtools so it can be easily used and updated. 

  

## **Things it implements itself:**

- keyboard_shortcut_router.py
	- Provides a single point of entry to access these scripts. Things like the window manager can be invoked like `python keyboard_shortcut_router.py --open Firefox`. Mostly to be used by a desktop environment's keyboard shortcut manager. This avoids having to make bin entries for each script here. 
- window_manager.py
	- Improved launching of apps via keyboard shortcut. Instead of telling the DE that alt+4 should run gnome-terminal, you tell it to send the window title of the terminal to window_manager.py. The script searches the window manager for that title via `wmctrl`. If it finds a match it activates that window instead of starting a new instance. 
- mouse_app_menu.py
	- makes a small popup window containing buttons that launch favorite websites and apps. To be launched via hotcorner, or mouse button 4/5 for fast navigation to favorites without having to type anything. 
- media_census.py
	- record the titles of music/audiobooks/etc and record them Obsidian so that in the event of total data loss I can use the list to know what I had and begin to rebuild :/
- music_classifier.py
	- aids a project whereby I want to categorize my music into one of several vibes or tiers 1 and 2. So that I can set my music player to only play tier 1 stuff or only sad vibe stuff. 
- random_reddit.py
	- Keeps a db of subreddits and offers up several random ones at a time on demand as a means of exploring reddit. Keeps track of which have already been visited and doesn't offer those. 
- tag_editor.py
	- Automates common music tag formatting jobs that all new music files have to go through before being added to the collection. 


