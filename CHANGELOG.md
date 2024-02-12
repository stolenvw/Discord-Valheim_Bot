# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.2] - 2024-2-12

### Changed

- change to version regexp for changes made in 0.217.14
- change to saved zdos regexp for changes made in 0.217.14
- discord-py updated to 2.3.2
- mysql-connector-python updated to version 8.0.33
- emoji updated to version 2.10.1
- gevent 23.9.1

### Fixed

- Getting version number from A2S, by headbug

## [3.0.1] - 2023-4-12

### Changed

- regexp for getting server version from log file, due to changes in Valheim version 0.215.2

## [3.0.0] - 2023-2-10

Updating from older version:  
Backup your mysql database.  
`pip install -r requirements.txt` To install Pyhton requirements.  
Run [dbsetup.py](code/dbsetup.py) To update database. `python3 dbsetup.py` 

### Added 

- V2 Branch to keep a copy of version 2.0.0
- Serverinfo database table.
- VERSIONLOOP config setting to enable or disable checking server version every 30min.
- CHECK_UPDATE config setting to enable or disable checking steamdb timestamp to see if new version is released.
- Command check to check if bot has permissions to send messages to channel.
- Default command permissions, can override them in Discord Intergrations.
- Requirements: steam, gevent, gevent-eventemitter

### Changed

- mysql-connector-python updated to version 8.0.32
- Some [config.py](code/config.py) settings.
- [dbsetup.py](code/dbsetup.py) now handles doing database updates.
- Permission checks to use Discord Integrations settings.

### Removed

- eventsdbupdate.py
- mistlandsbossdb.py
- v2.dbupdate.py
- serverstats database table.
- Removed roles settings from [config.py](code/config.py).
- Removed command check that made them only work in LOGCHAN_ID.

### Fixed

- Command errors from giving an interaction already responed to error.
- Check for if server is using Crossplay (Playfab).

## [2.0.0] - 2022-12-10

Upgrading form older version:  
[v2.dbupdate.py](dbupdates/v2.dbupdate.py)
Move to the code dir and run `python3 v2.dbupdate.py` to update database's.  

### Added

- Bot now uses slash commands, instead of !prefix.
- Support for crossplay and Mistlands.
- Bot logging to logfile, USEDEBUGCHAN setting outputs stuff from the logfile to BUGCHANNEL_ID.
- New config file options.
- All other dependencies updated to newest versions.

### Changed

- discord.py updated to version 2.1.0.
### Removed

- "stats" and "help" commands removed
