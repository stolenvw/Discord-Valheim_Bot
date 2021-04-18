# Valheim-Discord_Bot
Valheim discord bot originally based off of [ckbaudio's valheim-discord-bot](https://github.com/ckbaudio/valheim-discord-bot) with a lot of changes.

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

## Usage:
`python3 valheimbot.py` While in the `code` dir.  
`nohup python3 valheimbot.py &` Too run in background.  
Or you can create a service to run `valheimbot.py` under systemd  

**help** Shows available commands

### Example Output:
![](example/example.png)
