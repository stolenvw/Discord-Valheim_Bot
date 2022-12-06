# Valheim-Discord_Bot
Valheim discord bot originally based off of [ckbaudio's valheim-discord-bot](https://github.com/ckbaudio/valheim-discord-bot) with a lot of changes.

## UPDATE 12/6/2022:
New version will be coming out sometime this week.  
*discord.py updated to version 2.1.0*  
*Bot now uses slash commands, instead of !prefix*  
*Updated for crossplay and Mistlands*  
*Bot logging to logfile, USEDEBUGCHAN setting outputs stuff from the logfile to BUGCHANNEL_ID*  
*Other dependencies also updated to newest version*

## Setup:
**Working MySQL server is needed for this bot.**  
`pip install -r requirements.txt` To install Pyhton requirements.

## [config.py](code/config.py)
Edit this file with your info. Setting should be self-explanitory.  

Add `-logfile /location/to/file.log` to your start command to get a logfile.  

For `WORLDSIZE` user running the bot must have read permissions to the world.db.old file

## [dbsetup.py](code/dbsetup.py)
Tables and data for the MySQL database.  

**Warning: Set up the config.py before running this**  
Run `python3 dbsetup.py` from the code dir to create tables.

## [eventsdbupdate.py](dbupdates/eventsdbupdate.py)
Move to the code dir and run `python3 eventsdbupdate.py` to update the events database with new events.

## Usage:
`python3 valheimbot.py` While in the `code` dir.  
`nohup python3 valheimbot.py &` Too run in background.  
Or you can create a service to run `valheimbot.py` under systemd  

**help** Shows available commands

### Example Output:
![](example/example.png)
