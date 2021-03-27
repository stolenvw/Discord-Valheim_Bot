import os, time, re, discord, asyncio, config, emoji, sys, colorama, typing, signal, errno, mysql.connector, a2s
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
from colorama import Fore, Style, init
from config import LOGCHAN_ID as lchanID
from config import VCHANNEL_ID as chanID
from config import SQL_HOST as MYhost
from config import SQL_PORT as MYport
from config import SQL_USER as MYuser
from config import SQL_PASS as MYpass
from config import SQL_DATABASE as MYbase
from config import file
from discord.ext import commands
import matplotlib.dates as md
import matplotlib.ticker as ticker
import matplotlib.spines as ms
import pandas as pd

#Color init
colorama.init()

pdeath = '.*?Got character ZDOID from (\w+) : 0:0'
pevent = '.*? Random event set:(\w+)'
pjoin = '.*? Got character ZDOID from (\w+) : ([-0-9]*:[-0-9]*)$'
pquit = '.*? Destroying abandoned non persistent zdo ([-0-9]*:[0-9]*) owner [-0-9]*$'
pfind = '.*? Found location of type (\w+)'
# Extra Server Info
# Seed getting log line was removed, leaving here commented out just incase it comes back
#sseed = '.*? Initializing world generator seed:(\w+) \( ([-0-9]+) \)\s{1,}menu:False  worldgen version:([0-9]{1,})$'
ssaved1 = '.*? Saved ([0-9]+) zdos$'
ssaved2 = '.*? World saved \( ([0-9]+\.[0-9]+)ms \)$'
sversion = '.*? Valheim version:([\.0-9]+)$'
gdays = '.*? Time [\.0-9]+, day:([0-9]+)\s{1,}nextm:[\.0-9]+\s+skipspeed:[\.0-9]+$'

server_name = config.SERVER_NAME
bot = commands.Bot(command_prefix='!', help_command=None)
sonline = 1

    # maybe in the future for reformatting output of random mob events
    # eventype = ['Skeletons', 'Blobs', 'Forest Trolls', 'Wolves', 'Surtlings']

#Connect to MYSQL
def mydbconnect():
    global mydb
    mydb = mysql.connector.connect(
        host=MYhost,
        user=MYuser,
        password=MYpass,
        database=MYbase,
        port=MYport,
        )
    try:
        if mydb.is_connected():
            db_Info = mydb.get_server_info()
            print(Fore.GREEN + "Connected to MySQL database... MySQL Server version on ", db_Info + Style.RESET_ALL)
    except mysql.connector.Error as err:
        print(Fore.RED + err + Style.RESET_ALL)

mydbconnect()

def get_cursor():
    try:
        mydb.ping(reconnect=True, attempts=3, delay=5)
    except mysql.connector.Error as err:
        mydbconnect()
        print(Fore.RED + "Connection to MySQL database went away... Reconnecting " + Style.RESET_ALL)
    return mydb.cursor()

def signal_handler(signal, frame):          # Method for catching SIGINT, cleaner output for restarting bot
  os._exit(0)

signal.signal(signal.SIGINT, signal_handler)

async def timenow():
    now = datetime.now()
    gettime = now.strftime("%d/%m/%Y %H:%M:%S")
    return gettime

def convert(n):
    return str(timedelta(seconds = n))

@bot.event
async def on_ready():
    print(Fore.GREEN + f'Bot connected as {bot.user} :)' + Style.RESET_ALL)
    print('Log channel : %d' % (lchanID))
    if config.USEVCSTATS == True:
        print('VoIP channel: %d' % (chanID))
        bot.loop.create_task(serveronline())

@bot.command(name='help')
async def help_ctx(ctx):
    help_embed = discord.Embed(description="[**Valheim Discord Bot**](https://github.com/ckbaudio/valheim-discord-bot)", color=0x33a163,)
    help_embed.add_field(name="{}stats <n>".format(bot.command_prefix),
                        value="Plots a graph of connected players over the last X hours.\n Example: `{}stats 12` \n Available: 24, 12, w (*default: 24*)".format(bot.command_prefix),
                        inline=True)
    help_embed.add_field(name="{}deaths <n>".format(bot.command_prefix),
                        value="Shows a top 5 leaderboard of players with the most deaths. \n Example:`{}deaths 3` \n Available: 1-10 (*default: 10*)".format(bot.command_prefix),
                        inline=True)
    help_embed.add_field(name="{}playerstats <playername>".format(bot.command_prefix),
                        value="Shows player stats on active monitored world. \n Example: '{}playerstats stolenvw'".format(bot.command_prefix),
                        inline=True)
    help_embed.add_field(name="{}active".format(bot.command_prefix),
                        value="Shows who is currently logged into the server and how long they have been on for. \n Example: '{}active'".format(bot.command_prefix),
                        inline=True)
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        help_embed.add_field(name="**Owner**",
                            value="Owner only commands",
                            inline=False)
        help_embed.add_field(name="{}setstatus <type> <message>".format(bot.command_prefix),
                            value='Set status message of the bot. \n Example: `{}setstatus playing "Valheim"` \n Available type: playing, watching, listening'.format(bot.command_prefix),
                            inline=True)
    help_embed.set_footer(text="ckbaudio Valbot v0.42, stolenvw edit v0.51")
    await ctx.send(embed=help_embed)

@bot.command(name="deaths")
async def leaderboards(ctx, arg: typing.Optional[str] = '5'):
    ldrembed = discord.Embed(title=":skull_crossbones: __Death Leaderboards (top " + arg + ")__ :skull_crossbones:", color=0xFFC02C)
    mycursor = get_cursor()
    sql = """SELECT user, deaths FROM players WHERE deaths > 0 ORDER BY deaths DESC LIMIT %s""" % (arg)
    mycursor.execute(sql)
    Info = mycursor.fetchall()
    row_count = mycursor.rowcount
    l = 1 #just in case I want to make listed iterations l8r
    for ind in Info:
        grammarnazi = 'deaths'
        leader = ''
        pdname = ind[0]
        pddeath = ind[1]
        if pddeath == 1 :
            grammarnazi = 'death'
        if l == 1:
            leader = ':crown:'
        ldrembed.add_field(name="{} {}".format(pdname,leader),
                           value='{} {}'.format(pddeath,grammarnazi),
                           inline=False)
        l += 1
    mycursor.close()
    await ctx.send(embed=ldrembed)

@bot.command(name="stats")
async def gen_plot(ctx, tmf: typing.Optional[str] = '24'):
    user_range = 0
    if tmf.lower() in ['w', 'week', 'weeks']:
        user_range = 168 - 1
        tlookup = int(time.time()) - 604800
        interval = 24
        date_format = '%m/%d'
        timedo = 'week'
        description = 'Players online in the past ' + timedo + ':'
    elif tmf.lower() in ['12', '12hrs', '12h', '12hr']:
        user_range = 12 - 0.15
        tlookup = int(time.time()) - 43200
        interval = 1
        date_format = '%H'
        timedo = '12hrs'
        description = 'Players online in the past ' + timedo + ':'
    else:
        user_range = 24 - 0.30
        tlookup = int(time.time()) - 86400
        interval = 2
        date_format = '%H'
        timedo = '24hrs'
        description = 'Players online in the past ' + timedo + ':'

    #Get data from mysql
    mycursor = get_cursor()
    mycursor.close()
    sqls = """SELECT date, users FROM serverstats WHERE timestamp BETWEEN '%s' AND '%s'""" % (tlookup, int(time.time()))
    df = pd.read_sql(sqls, mydb, parse_dates=['date'])
    lastday = datetime.now() - timedelta(hours = user_range)

    # Plot formatting / styling matplotlib
    plt.style.use('seaborn-pastel')
    plt.minorticks_off()
    fig, ax = plt.subplots()
    ax.grid(b=True, alpha=0.2)
    ax.set_xlim(lastday, datetime.now())
    # ax.set_ylim(0, 10) Not sure about this one yet
    for axis in [ax.xaxis, ax.yaxis]:
        axis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.xaxis.set_major_formatter(md.DateFormatter(date_format))
    ax.xaxis.set_major_locator(md.HourLocator(interval=interval))
    for spine in ax.spines.values():
        spine.set_visible(False)
    for tick in ax.get_xticklabels():
        tick.set_color('gray')
    for tick in ax.get_yticklabels():
        tick.set_color('gray')

    #Plot and rasterize figure
    plt.gcf().set_size_inches([5.5,3.0])
    plt.plot(df['date'], df['users'], drawstyle='steps-post')
    plt.tick_params(axis='both', which='both', bottom=False, left=False)
    plt.margins(x=0,y=0,tight=True)
    plt.tight_layout()
    fig.savefig('temp.png', transparent=True, pad_inches=0) # Save and upload Plot
    image = discord.File('temp.png', filename='temp.png')
    plt.close()
    embed = discord.Embed(title=server_name, description=description, colour=12320855)
    embed.set_image(url='attachment://temp.png')
    await ctx.send(file=image, embed=embed)

@bot.command(name="playerstats")
async def playstats(ctx, arg):
    mycursor = get_cursor()
    sql = """SELECT user, deaths, startdate, playtime FROM players WHERE user = '%s'""" % (arg)
    mycursor.execute(sql)
    Info = mycursor.fetchall()
    row_count = mycursor.rowcount
    if row_count == 1:
        Info=Info[0]
        plsembed = discord.Embed(title=":bar_chart: __Player Stats For " + Info[0] + "__ :bar_chart:", color=0x4A90E2)
        plsembed.add_field(name="Server Join Date:",
                           value='{}'.format(Info[2]),
                           inline=True)
        plsembed.add_field(name="Play Time:",
                          value=convert(Info[3]),
                          inline=True)
        plsembed.add_field(name="Deaths:",
                          value=Info[1],
                          inline=True)
        await ctx.send(embed=plsembed)
    else:
        await ctx.send(content=':no_entry_sign: **' + arg + '** Not Found')
    mycursor.close()

@bot.command(name="active")
async def leaderboards(ctx):
    mycursor = get_cursor()
    sql = """SELECT user, jointime FROM players WHERE ingame = 1 ORDER BY jointime LIMIT 10"""
    mycursor.execute(sql)
    Info = mycursor.fetchall()
    row_count = mycursor.rowcount
    if row_count == 0:
       await ctx.send(content=':globe_with_meridians: 0 Players Active')
    else:
         ldrembed = discord.Embed(title=":man_raising_hand: __Active Users__ :woman_raising_hand:", color=0x50E3C2)
         EndTime = int(time.time())
         for ind in Info:
             pname = ind[0]
             onfor = "Online For:"
             ponline = convert(EndTime - ind[1])
             ldrembed.add_field(name="{}".format(pname),
                                value='{} {}'.format(onfor,ponline),
                                inline=False)
         await ctx.send(embed=ldrembed)
    mycursor.close()

@bot.command(name="setstatus")
@commands.is_owner()
async def setstatus(ctx, arg: typing.Optional[str] = '0', arg1: typing.Optional[str] = '1'):
      if arg == "playing":
         await bot.change_presence(activity=discord.Game(arg1))
#      elif arg == "streaming":
#         await bot.change_presence(activity=discord.Streaming(name=arg1, url=arg2))
      elif arg == "watching":
         await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=arg1))
      elif arg == "listening":
         await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=arg1))
      else:
           await ctx.channel.send('Usage: `{}setstatus <playing|watching|listening> "<Some activity>"`'.format(bot.command_prefix))

async def mainloop(file):
    await bot.wait_until_ready()
    lchannel = bot.get_channel(lchanID)
    print('Main loop: init')
    try:
        testfile = open(file)
        testfile.close()
        while not bot.is_closed():
            with open(file, encoding='utf-8', mode='r') as f:
                f.seek(0,2)
                while True:
                    line = f.readline()
                    if(re.search(pdeath, line)):
                        pname = re.search(pdeath, line).group(1)
                        mycursor = get_cursor()
                        sql = """UPDATE players SET deaths = deaths + 1 WHERE user = '%s'""" % (pname)
                        mycursor.execute(sql)
                        mydb.commit()
                        mycursor.close()
                        await lchannel.send(':skull: **' + pname + '** just died!')
                    if(re.search(pevent, line)):
                        eventID = re.search(pevent, line).group(1)
                        mycursor = get_cursor()
                        sql = """SELECT type, smessage, image FROM events WHERE type = '%s' LIMIT 1""" % (eventID)
                        mycursor.execute(sql)
                        Info = mycursor.fetchall()
                        Info=Info[0]
                        image = discord.File('img/' + Info[2], filename=Info[2])
                        embed = discord.Embed(title=Info[0], colour=discord.Colour(0xb6000e), description="*" + Info[1] + "*")
                        embed.set_thumbnail(url='attachment://' + Info[2])
                        embed.set_author(name="📢 Random Mob Event")
                        await lchannel.send(file=image, embed=embed)
                        mycursor.close()
                    if(re.search(pjoin, line)):
                        logJoin = re.search(pjoin, line).group(1)
                        logID = re.search(pjoin, line).group(2)
                        tnow = datetime.now()
                        mycursor = get_cursor()
                        sql = """SELECT id, ingame FROM players WHERE user = '%s'""" % (logJoin)
                        mycursor.execute(sql)
                        Info = mycursor.fetchall()
                        row_count = mycursor.rowcount
                        if row_count == 0:
                           StartDate = tnow.strftime("%m/%d/%Y %H:%M:%S")
                           JoinTime = int(time.time())
                           InGame = 1
                           sql = """INSERT INTO players (user, valid, startdate, jointime, ingame) VALUES ('%s', '%s', '%s', '%s', '%s')""" % (logJoin, logID, StartDate, JoinTime, InGame)
                           mycursor.execute(sql)
                           mydb.commit()
                           await lchannel.send(':airplane_arriving: New player **' + logJoin + '** has joined the party!')
                        else:
                            Info=Info[0]
                            if Info[1] == 1:
                                sql = """UPDATE players SET valid = '%s' WHERE id = '%s'""" % (logID, Info[0])
                                mycursor.execute(sql)
                                mydb.commit()
                            else:
                                JoinTime = int(time.time())
                                InGame = 1
                                sql = """UPDATE players SET valid = '%s', jointime = '%s', ingame = '%s' WHERE user = '%s'""" % (logID, JoinTime, InGame, logJoin)
                                mycursor.execute(sql)
                                mydb.commit()
                                await lchannel.send(':airplane_arriving: **' + logJoin + '** has joined the party!')
                        sql2 = """INSERT INTO serverstats (date, timestamp, users) VALUES ('%s', '%s', '%s')""" % (tnow.strftime("%m/%d/%Y %H:%M:%S"), int(time.time()), await serverstatsupdate())
                        mycursor.execute(sql2)
                        mydb.commit()
                        mycursor.close()
                    if(re.search(pquit, line)):
                        logquit = re.search(pquit, line).group(1)
                        tnow = datetime.now()
                        mycursor = get_cursor()
                        sql = """SELECT id, user, jointime, playtime FROM players WHERE valid = '%s'""" % (logquit)
                        mycursor.execute(sql)
                        Info = mycursor.fetchall()
                        row_count = mycursor.rowcount
                        if row_count == 1:
                           Info=Info[0]
                           EndTime = int(time.time())
                           Ptime = EndTime - Info[2] + Info[3]
                           ponline = convert(EndTime - Info[2])
                           InGame = 0
                           sql = """UPDATE players SET playtime = '%s', ingame = '%s' WHERE id = '%s'""" % (Ptime, InGame, Info[0])
                           mycursor.execute(sql)
                           mydb.commit()
                           await lchannel.send(':airplane_departure: **' + Info[1] + '** has left the party! Online for: ' + ponline + '')
                           sql2 = """INSERT INTO serverstats (date, timestamp, users) VALUES ('%s', '%s', '%s')""" % (tnow.strftime("%m/%d/%Y %H:%M:%S"), int(time.time()), await serverstatsupdate())
                           mycursor.execute(sql2)
                           mydb.commit()
                        mycursor.close()
                    if(re.search(pfind, line)):
                        newitem = re.search(pfind, line).group(1)
                        await lchannel.send(':crossed_swords: Found location of **' + newitem + '**')
                    if config.EXSERVERINFO == True:
                        if(re.search(ssaved1, line)):
                            save1 = re.search(ssaved1, line).group(1)
                            mycursor = get_cursor()
                            sql = """INSERT INTO exstats (savezdos, timestamp) VALUES ('%s', '%s')""" % (save1, int(time.time()))
                            mycursor.execute(sql)
                            mydb.commit()
                            mycursor.close()
                        if(re.search(ssaved2, line)):
                            save2 = re.search(ssaved2, line).group(1)
                            mycursor = get_cursor()
                            tlookup = int(time.time()) - 120
                            sql = """SELECT id FROM exstats WHERE savesec is null AND timestamp BETWEEN '%s' AND '%s' LIMIT 1""" % (tlookup, int(time.time()))
                            mycursor.execute(sql)
                            Info = mycursor.fetchall()
                            row_count = mycursor.rowcount
                            if row_count == 1:
                                Info=Info[0]
                                sql = """UPDATE exstats SET savesec = '%s' WHERE id = '%s'""" % (save2, Info[0])
                                mycursor.execute(sql)
                                mydb.commit()
                            else:
                                print('ERROR: Could not find save zdos info')
                            mycursor.close()
                        if(re.search(sversion, line)):
                            serversion = re.search(sversion, line).group(1)
                            mycursor = get_cursor()
                            sql = """SELECT id, serverversion FROM exstats WHERE id = 1"""
                            mycursor.execute(sql)
                            Info = mycursor.fetchall()
                            row_count = mycursor.rowcount
                            if row_count == 0:
                                await lchannel.send('**ERROR:** Extra server info is set, but missing database table/info')
                            else:
                                Info=Info[0]
                                if serversion != Info[1]:
                                    sql = """UPDATE exstats SET serverversion = '%s' WHERE id = '%s'""" % (serversion, Info[0])
                                    mycursor.execute(sql)
                                    mydb.commit()
                                    await lchannel.send('**INFO:** Server has been updated to version: ' + serversion + '')
                            mycursor.close()
                        if(re.search(gdays, line)):
                            gamedays = re.search(gdays, line).group(1)
                            mycursor = get_cursor()
                            sql = """INSERT INTO exstats (gameday, timestamp) VALUES ('%s', '%s')""" % (gamedays, int(time.time()))
                            mycursor.execute(sql)
                            mydb.commit()
                            await lchannel.send('**INFO:** Server reported in game day as: ' + gamedays + '')
                            mycursor.close()
                    await asyncio.sleep(0.2)
    except IOError:
        print('No valid log found, event reports disabled. Please check config.py')
        print('To generate server logs, run server with -logfile launch flag')

async def serverstatsupdate():
    try:
        if a2s.info(config.SERVER_ADDRESS):
            channel = bot.get_channel(chanID)
            oplayers = a2s.info(config.SERVER_ADDRESS).player_count
            await channel.edit(name=f"{emoji.emojize(':house:')} In-Game: {oplayers}" +" / 10")
    except Exception as e:
        print(Fore.RED + await timenow(), e, 'from A2S' + Style.RESET_ALL)
        channel = bot.get_channel(chanID)
        oplayers = 0
        await channel.edit(name=f"{emoji.emojize(':cross_mark:')} Server Offline")
    else:
        return oplayers

async def serveronline():
    global sonline
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            if a2s.info(config.SERVER_ADDRESS):
                meonline = a2s.info(config.SERVER_ADDRESS).player_count
                if sonline == 0:
                    sonline = 1
                    channel = bot.get_channel(chanID)
                    await channel.edit(name=f"{emoji.emojize(':house:')} Server OnLine")
        except Exception as e:
            channel = bot.get_channel(chanID)
            await channel.edit(name=f"{emoji.emojize(':cross_mark:')} Server Offline")
            if sonline == 1:
                sonline = 0
                tnow = datetime.now()
                mycursor = get_cursor()
                sql2 = """INSERT INTO serverstats (date, timestamp, users) VALUES ('%s', '%s', '%s')""" % (tnow.strftime("%m/%d/%Y %H:%M:%S"), int(time.time()), sonline)
                mycursor.execute(sql2)
                mydb.commit()
                mycursor.close()
            print(Fore.RED + await timenow(), e, 'from A2S, retrying (60s)...' + Style.RESET_ALL)
        await asyncio.sleep(60)

bot.loop.create_task(mainloop(file))
bot.run(config.BOT_TOKEN)
