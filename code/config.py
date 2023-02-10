# IMPORTANT! You must have a log for event reports and death leaderboards
# logs are achieved by using -logfile flag on launch, or by logging stdout
# Windows Users use forward slashes

# Path to your Valheim servers log file
VALHEIM_SERVER_LOG = '/var/log/valheim.log'

BOT_TOKEN = ""

# Change ? to command prefix you want to use
BOT_PREFIX = "!"

# Server ip and port for A2S port needs to be +1 of the port number used in -port
SERVER_ADDRESS = ("0.0.0.0",2457)

# Shows up in embeds for stats report
SERVER_NAME = "Server Name"

# DISCORD_SERVER - Discord server id for syncing slash commands
DISCORD_SERVER = 000000000000000000

# LOGCHAIN - where the bot outputs death and random mob events
LOGCHAN_ID  = 000000000000000

# use a locked VC channel to report player count, if not, set as False
USEVCSTATS = True

# VCHANNEL - where the bot shows server ticker, must be voice channel
VCHANNEL_ID = 000000000000000000

# MYSQL server info
SQL_HOST = 'localhost'
SQL_PORT = '3306'
SQL_USER = 'username'
SQL_PASS = 'password'
SQL_DATABASE = 'database'

# EXSERVERINFO - used to enable extra server data info gathering from logs ***Extra server info table will be loaded into MySQL if this is enabled***
EXSERVERINFO = True

# World file location used for showing file size.
WORLDSIZE = False
worldfile = '/home/user/valheim/.config/unity3d/IronGate/Valheim/worlds/world.db.old'

# 30 min version check loop, If disabled bot needs to be running before starting server so it can get version info from log file.
VERSIONLOOP = False

# Enable sending debug info to a channel
USEDEBUGCHAN = False

# BUGCHANNEL - where the bot shows debug info
BUGCHANNEL_ID = 000000000000000000

# PLOCINFO - used for tracking placed locations to determine percent of world exploed ***Must rerun dbsetup.py if changing this to True if you ran it all ready***
PLOCINFO = True

# Path to save bots log file
LOG_FILE = "logs/valheimbot.log"

# Logging level DEBUG|INFO|WARNING|ERROR|CRITICAL
LOG_LEVEL = "INFO"

# Check steam for server updates (Does not check default_old or beta branches)
# Steam does not list the servers version number, this checks the last updated timestamp from steam 
# and stores it in the mysql database to see if it has changed. If timestamp from steam is newer then one in 
# mysql database sends a notice to log and LOGCHAN_ID channel
# EXSERVERINFO needs to be set to True if setting this to True
CHECK_UPDATE = False
