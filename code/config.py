# Still working on discord-side triggering

# IMPORTANT! You must have a log for event reports and death leaderboards
# logs are achieved by using -logfile flag on launch, or by logging stdout
# Windows Users use forward slashes
# Path to your log file
file = '/var/log/valheim.log'

BOT_TOKEN = ""

# Change ? to command prefix you want to use
BOT_PREFIX = "!"

# Server ip and port for A2S port needs to be +1 of the port number used in -port
SERVER_ADDRESS = ("0.0.0.0",2457)

# Shows up in embeds for stats report
SERVER_NAME = "Server Name"

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
WORLDSIZE = True
worldfile = '/home/user/valheim/.config/unity3d/IronGate/Valheim/worlds/world.db.old'

# Enable sending debug info to a channel
USEDEBUGCHAN = True

# BUGCHANNEL - where the bot shows debug info
BUGCHANNEL_ID = 7293481670000121

# Commands Roles. Discord roles that can use command.
DEATHS_CMD = "@everyone"
STATS_CMD = "@everyone"
PLAYERSTATS_CMD = "@everyone"
ACTIVE_CMD = "@everyone"
VERSIONS_CMD = "@everyone"
SETSTATUS_CMD = "Admin"
SAVESTATS_CMD = "Admin","Mod"
PLOC_CMD = "@everyone"

# PLOCINFO - used for tracking placed locations to determine percent of world exploed. Will not show right on an existing world ***Must rerun dbsetup.py if changing this to True if you ran it all ready***
PLOCINFO = True
