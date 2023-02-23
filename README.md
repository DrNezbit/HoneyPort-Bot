# HoneyBot - A HoneyPort Discord Bot

## This is designed as an early detection system for home network intrusion  
It will open port 22 (the default SSH port) and listen for connections.  If the port gets scanned or a SSH connection is attempted it will log it and alert you through a discord direct message from the bot.  Included in the bot are a command to restart it, a command to view the current logs, and a command to clear the log file.  Upon clearing logs you will be sent a confirmation notification that the logs have been cleared to their last entry.  

By being alerted to suspicious activity in your network early you can take required actions to defend your network and protect yourself.  If you own a home network and do not know what SSH is then any activity to port 22 can be considered suspicious and should be looked into.  It is not a common protocol for use unless you have set it up (in which case the default port is not recommended to use for it) and can be a high target port for a network intruder.

## Setup:
Setup by first changing your SSH port (deafult 22) if in use.  Next step is installing docker and docker-compose (if not already installed) and editing "secret.env" to include your bot token ( if unfamiliar with how to create a discord bot or get a token see: https://www.writebots.com/discord-bot-token/ ), your discord user ID (for messages to go to), and server ID (for commands to be added to).  Once those are set, use "docker-compose up" from within the project root folder to build the image and run it.  Once it says your bot name is online, port 22 should be listening.  This can be confirmed by scanning your devices ports (which should also alert you of the scan). 

## Notes:
This uses my HoneyPort repository ( https://github.com/DrNezbit/HoneyPort ) to open the port and log activity.  Included here is a discord bot to scan the logs and notify you of changes by direct message.  If interested in writing your own python discord bot check out my template here: https://github.com/DrNezbit/python-discord-bot-template--docker-ready