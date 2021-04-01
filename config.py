# Still working on discord-side triggering

# IMPORTANT! You must have a log for event reports and death leaderboards
# logs are achieved by using -logfile flag on launch, or by logging stdout
# Windows Users use forward slashes
file = '/var/log/valheim.log'

BOT_TOKEN = ""

# Change ? to command prefix you want to use
BOT_PREFIX = "!"

# Make sure are seen between server and script host
SERVER_ADDRESS = ("0.0.0.0",2457)

# Shows up in embeds for stats report
SERVER_NAME = "Server Name"

# LOGCHAIN - where the bot outputs death and random mob events
LOGCHAN_ID  = 000000000000000

# use a locked VC channel to report player count, if not, set as False
USEVCSTATS = True

# VCHANNEL - where the bot shows server ticker, must be voice channel
VCHANNEL_ID = 000000000000000000

# MYSQL server info (Stolenvw)
SQL_HOST = 'localhost'
SQL_PORT = '3306'
SQL_USER = 'username'
SQL_PASS = 'password'
SQL_DATABASE = 'database'

# EXSERVERINFO - used to enable extra server data info gathering from logs ***Must add the extra server info table in mysql***
EXSERVERINFO = True

# World file location used for showing file size.
WORLDSIZE = True
worldfile = '/home/user/valheim/.config/unity3d/IronGate/Valheim/worlds/world.db.old'

# Enable sending debug info to a channel
USEDEBUGCHAN = True

# BUGCHANNEL - where the bot shows debug info
BUGCHANNEL_ID = 7293481670000121
