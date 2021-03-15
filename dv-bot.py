import os, time, re, csv, discord, asyncio, config, emoji, sys, colorama, typing, signal, errno, mysql.connector
from valve.source.a2s import ServerQuerier, NoResponseError
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
        channel = bot.get_channel(chanID)
        await channel.edit(name=f"{emoji.emojize(':house:')} Server OnLine")
        bot.loop.create_task(serveronline())

@bot.command(name='help')
async def help_ctx(ctx):
    help_embed = discord.Embed(description="[**Valheim Discord Bot**](https://github.com/ckbaudio/valheim-discord-bot)", color=0x33a163,)
    help_embed.add_field(name="{}stats <n>".format(bot.command_prefix),
                        value="Plots a graph of connected players over the last X hours.\n Example: `{}stats 12` \n Available: 24, 12, w (*default: 24*)".format(bot.command_prefix),
                        inline=True)
    help_embed.add_field(name="{}deaths".format(bot.command_prefix),
                        value="Shows a top 5 leaderboard of players with the most deaths. \n Example:`{}deaths`".format(bot.command_prefix),
                        inline=True)
    help_embed.set_footer(text="Valbot v0.42")
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
    de = "1"
    sql = """SELECT user, jointime FROM players WHERE ingame = '%s' ORDER BY jointime LIMIT 10""" % (de)
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
                        await lchannel.send(':loudspeaker: Random mob event: **' + eventID + '** has occurred')
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
                    await asyncio.sleep(0.2)
    except IOError:
        print('No valid log found, event reports disabled. Please check config.py')
        print('To generate server logs, run server with -logfile launch flag')

async def serverstatsupdate():
    try:
        with ServerQuerier(config.SERVER_ADDRESS) as server:
            channel = bot.get_channel(chanID)
            oplayers = server.info()['player_count']
            await channel.edit(name=f"{emoji.emojize(':house:')} In-Game: {server.info()['player_count']}" +" / 10")
    except NoResponseError:
        print(Fore.RED + await timenow(), 'No reply from A2S' + Style.RESET_ALL)
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
            with ServerQuerier(config.SERVER_ADDRESS) as server:
                meonline = server.info()['player_count']
                if sonline == 0:
                    sonline = 1
                    await channel.edit(name=f"{emoji.emojize(':house:')} Server OnLine")
        except NoResponseError:
            print(Fore.RED + await timenow(), 'No reply from A2S, retrying (60s)...' + Style.RESET_ALL)
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
        await asyncio.sleep(60)

bot.loop.create_task(mainloop(file))
bot.run(config.BOT_TOKEN)
