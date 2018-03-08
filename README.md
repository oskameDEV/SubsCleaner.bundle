# SubsCleaner.bundle
A Plex agent that removes nuisances from subtitle files, such as <HTML> tags, pesky advertisements, and more with customizable filters.  

⚠️[IN BETA] NOTE THE FOLLOWING⚠️
- Don't run it on your entire library until it is out of beta
- After installing make sure to first set it up. And enable the agent (both for Movies and TV-shows)  
- Report any problem you find so I can fix it ASAP in order to avoid damaging subtitle files (special thanks to those who have)  
  
**Installation Instructions**  
Manual install only right now, auto-install coming SOON through UAS (WebTools' Unsupported App Store)  
https://github.com/ukdtom/WebTools.bundle  

**IMPORTANT: CONFIGURE BEFORE USING**  
After installing go to http://plex.tv/web/#!/settings/server/ and to your server settings → Agents
Now first find "SubsCleaner" and tap the gear to set it up.  
Once you've done that you can enable it for each of the agent groups for Movies and TV-shows.  
Make sure to put the cleaner below any agent that downloads subtitles (like SubZero)

**Manual Installation Instructions**  
/!\ Installing it this way does not come with the auto-update option /!\  

Download the latest version (green button on this page) and after unzipping, make sure the folder name is called "SubsCleaner.bundle" (remove the -master part)  
Move the SubsCleaner.bundle to your plugin directory

MacOS	:	~/Library/Application Support/Plex Media Server/Plug-ins  
Windows	:	C:\Users\YOURUSERNAME\AppData\Local\Plex Media Server\Plug-ins  
Linux	:	/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-ins  