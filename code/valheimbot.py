import os, time, re, discord, asyncio, config, emoji, sys, colorama, typing, signal, errno, mysql.connector, a2s
from datetime import datetime, timedelta
from colorama import Fore, Style, init
from config import LOGCHAN_ID as lchanID
from config import VCHANNEL_ID as chanID
from config import BUGCHANNEL_ID as dbchanID
from config import file
from discord.ext import commands


######################### Code below ##########################
##### Dont complain if you edit it and something dont work ####

#Color init
colorama.init()

pdeath = '^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: Got character ZDOID from (\w+) : 0:0'
pevent = '^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: Random event set:(\w+)'
pjoin = '^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: Got character ZDOID from (\w+) : ([-0-9]*:[-0-9]*)$'
pquit = '^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: Destroying abandoned non persistent zdo ([-0-9]*:[0-9]*) owner [-0-9]*$'
pfind = '^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: Found location of type (\w+)'
# Extra Server Info
ssaved1 = '^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: Saved ([0-9]+) zdos$'
ssaved2 = '^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: World saved \( ([0-9]+\.[0-9]+)ms \)$'
sversion = '^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: Valheim version:([\.0-9]+)$'
gdays = '^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: Time [\.0-9]+, day:([0-9]+)\s{1,}nextm:[\.0-9]+\s+skipspeed:[\.0-9]+$'
ploc = '^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: Placed locations in zone ([-,0-9]+)  duration ([\.0-9]+) ms$'
tloc = '^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: Loaded ([0-9]+) locations$'

bot = commands.Bot(command_prefix=config.BOT_PREFIX)
server_name = config.SERVER_NAME
sonline = 1
startup_extensions = ["utils.botsql"]
cogs_dir = "botcmds"

# Method for catching SIGINT, cleaner output for restarting bot
def signal_handler(signal, frame):
  os._exit(0)

signal.signal(signal.SIGINT, signal_handler)

async def timenow():
    now = datetime.now()
    gettime = now.strftime("%m/%d/%Y %H:%M:%S")
    return gettime

async def convert(n):
    return str(timedelta(seconds = n))

@bot.event
async def on_ready():
    print(Fore.GREEN + f'Bot connected as {bot.user} :)' + Style.RESET_ALL)
    print('Command prefix: %s' % config.BOT_PREFIX)
    print('Log channel: #%s' % (bot.get_channel(lchanID)))
    if config.USEVCSTATS == True:
        print('VoIP channel: %d' % (chanID))
    if config.USEDEBUGCHAN == True:
        print('Debug channel: #%s' % (bot.get_channel(dbchanID)))
        bugchan = bot.get_channel(dbchanID)
        buginfo = discord.Embed(title=":white_check_mark: **INFO** :white_check_mark:", color=0x7EFF00)
        buginfo.set_author(name=server_name)
        buginfo.add_field(name="Bot connected as:",
                          value="{}".format(bot.user),
                          inline=False)
        buginfo.add_field(name="Command prefix:",
                          value="{}".format(config.BOT_PREFIX),
                          inline=False)
        buginfo.add_field(name="Log channel:",
                          value="#{}".format(bot.get_channel(lchanID)),
                          inline=False)
        if config.USEVCSTATS == True:
            buginfo.add_field(name="VoIP channel:",
                              value="#{}".format(chanID),
                              inline=False)
        buginfo.add_field(name="Debug channel",
                          value="#{}".format(bot.get_channel(dbchanID)),
                          inline=False)
        await bugchan.send(embed=buginfo)
    if __name__ == "__main__":
        icount = 0
        ecount = 0
        for extension in startup_extensions:
            try:
                bot.load_extension(extension)
                print(Fore.GREEN + 'Loaded extension {}'.format(extension) + Style.RESET_ALL)
                if config.USEDEBUGCHAN == True:
                    if icount == 1:
                        description = description + '\n' + '{}'.format(extension)
                    else:
                        description = '{}'.format(extension)
                        icount = 1
            except Exception as e:
                exc = '{}: {}'.format(type(e).__name__, e)
                print(Fore.RED + 'Failed to load extension {}\n{}'.format(extension, exc) + Style.RESET_ALL)
                if config.USEDEBUGCHAN == True:
                    if ecount == 1:
                        erdescription = erdescription + '\n' + '{}'.format(extension)
                    else:
                        erdescription = '{}'.format(extension)
                        ecount = 1
        for extension in [f.replace('.py', '') for f in os.listdir(cogs_dir) if os.path.isfile(os.path.join(cogs_dir, f))]:
            try:
                bot.load_extension(cogs_dir + "." + extension)
                print(Fore.GREEN + 'Loaded extension {}.{}'.format(cogs_dir, extension) + Style.RESET_ALL)
                if config.USEDEBUGCHAN == True:
                    if icount == 1:
                        description = description + '\n' + '{}.{}'.format(cogs_dir, extension)
                    else:
                        description = '{}.{}'.format(cogs_dir, extension)
                        icount = 1
            except Exception as e:
                exc = '{}: {}'.format(type(e).__name__, e)
                print(Fore.RED + 'Failed to load extension {}\n{}'.format(extension, exc) + Style.RESET_ALL)
                if config.USEDEBUGCHAN == True:
                    if ecount == 1:
                        erdescription = erdescription + '\n' + '{}.{}'.format(cogs_dir, extension)
                    else:
                        erdescription = '{}.{}'.format(cogs_dir, extension)
                        ecount = 1
        if icount == 1:
            buginfo = discord.Embed(title=":white_check_mark: **INFO** :white_check_mark:", color=0x7EFF00)
            buginfo.set_author(name=server_name)
            buginfo.add_field(name="Loaded extensions:",
                              value="{}".format(description),
                              inline=False)
            await bugchan.send(embed=buginfo)
        if ecount == 1:
            bugerror = discord.Embed(title=":sos: **ERROR** :sos:", color=0xFF001E)
            bugerror.set_author(name=server_name)
            bugerror.add_field(name="Failed to load extensions:",
                              value="{}".format(erdescription),
                              inline=False)
            await bugchan.send(embed=bugerror)
    bot.loop.create_task(serveronline())
    botsql = bot.get_cog('BotSQL')
    await botsql.mydbconnect()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Stolenvw ValheimBot"))

# Main loop for reading log file and outputing events
async def mainloop(file):
    await bot.wait_until_ready()
    lchannel = bot.get_channel(lchanID)
    bugchan = bot.get_channel(dbchanID)
    print('Main loop: init')
    if config.USEDEBUGCHAN == True:
        buginfo = discord.Embed(title=":white_check_mark: **INFO** :white_check_mark:", description="Main Loop Started", color=0x7EFF00)
        buginfo.set_author(name=server_name)
        await bugchan.send(embed=buginfo)
    try:
        testfile = open(file)
        testfile.close()
        while not bot.is_closed():
            with open(file, encoding='utf-8', mode='r') as f:
                f.seek(0,2)
                while True:
                    try:
                        line = f.readline()
                    except UnicodeDecodeError:
                        print('Got an invalid utf-8 character! Skipping moving to next line')
                        if config.USEDEBUGCHAN == True:
                            bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description="Got an invalid utf-8 character! Skipping.. moving to next line", color=0xFF001E)
                            bugerror.set_author(name=server_name)
                            await bugchan.send(embed=bugerror)
                    else:
                        if(re.search(pdeath, line)):
                            pname = re.search(pdeath, line).group(1)
                            botsql = bot.get_cog('BotSQL')
                            mycursor = await botsql.get_cursor()
                            sql = """UPDATE players SET deaths = deaths + 1 WHERE user = '%s'""" % (pname)
                            mycursor.execute(sql)
                            await botsql.botmydb()
                            mycursor.close()
                            await lchannel.send(':skull: **' + pname + '** just died!')
                    # Announcing of mob events
                        if(re.search(pevent, line)):
                            eventID = re.search(pevent, line).group(1)
                            botsql = bot.get_cog('BotSQL')
                            mycursor = await botsql.get_cursor()
                            sql = """SELECT type, smessage, image FROM events WHERE type = '%s' LIMIT 1""" % (eventID)
                            mycursor.execute(sql)
                            Info = mycursor.fetchall()
                            row_count = mycursor.rowcount
                            if row_count == 0:
                               print(Fore.RED + 'ERROR: Event' + eventID + ' missing from database' + Style.RESET_ALL)
                               if config.USEDEBUGCHAN == True:
                                bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description='Event {} missing from database'.format(eventID), color=0xFF001E)
                                bugerror.set_author(name=server_name)
                                await bugchan.send(embed=bugerror)
                            else:
                              Info=Info[0]
                              image = discord.File('img/' + Info[2], filename=Info[2])
                              embed = discord.Embed(title=Info[0], colour=discord.Colour(0xb6000e), description="*" + Info[1] + "*")
                              embed.set_thumbnail(url='attachment://' + Info[2])
                              embed.set_author(name="📢 Random Mob Event")
                              await lchannel.send(file=image, embed=embed)
                            mycursor.close()
                    # Announcing when a player joins the server, Announcing if they are a new player on the server, adds player to db if new, updates db with login time
                        if(re.search(pjoin, line)):
                            logJoin = re.search(pjoin, line).group(1)
                            logID = re.search(pjoin, line).group(2)
                            botsql = bot.get_cog('BotSQL')
                            mycursor = await botsql.get_cursor()
                            sql = """SELECT id, ingame FROM players WHERE user = '%s'""" % (logJoin)
                            mycursor.execute(sql)
                            Info = mycursor.fetchall()
                            row_count = mycursor.rowcount
                            if row_count == 0:
                                StartDate = await timenow()
                                JoinTime = int(time.time())
                                InGame = 1
                                sql = """INSERT INTO players (user, valid, startdate, jointime, ingame) VALUES ('%s', '%s', '%s', '%s', '%s')""" % (logJoin, logID, StartDate, JoinTime, InGame)
                                mycursor.execute(sql)
                                await botsql.botmydb()
                                await lchannel.send(':airplane_arriving: New player **' + logJoin + '** has joined the party!')
                            else:
                                Info=Info[0]
                                if Info[1] == 1:
                                    sql = """UPDATE players SET valid = '%s' WHERE id = '%s'""" % (logID, Info[0])
                                    mycursor.execute(sql)
                                    await botsql.botmydb()
                                else:
                                    JoinTime = int(time.time())
                                    InGame = 1
                                    sql = """UPDATE players SET valid = '%s', jointime = '%s', ingame = '%s' WHERE user = '%s'""" % (logID, JoinTime, InGame, logJoin)
                                    mycursor.execute(sql)
                                    await botsql.botmydb()
                                    await lchannel.send(':airplane_arriving: **' + logJoin + '** has joined the party!')
                            sql2 = """INSERT INTO serverstats (date, timestamp, users) VALUES ('%s', '%s', '%s')""" % (await timenow(), int(time.time()), await serverstatsupdate())
                            mycursor.execute(sql2)
                            await botsql.botmydb()
                            mycursor.close()
                    # Announcing when a player leaves the server, updates db with playtime
                        if(re.search(pquit, line)):
                            logquit = re.search(pquit, line).group(1)
                            botsql = bot.get_cog('BotSQL')
                            mycursor = await botsql.get_cursor()
                            sql = """SELECT id, user, jointime, playtime FROM players WHERE valid = '%s'""" % (logquit)
                            mycursor.execute(sql)
                            Info = mycursor.fetchall()
                            row_count = mycursor.rowcount
                            if row_count == 1:
                                Info=Info[0]
                                EndTime = int(time.time())
                                Ptime = EndTime - Info[2] + Info[3]
                                ponline = await convert(EndTime - Info[2])
                                InGame = 0
                                sql = """UPDATE players SET playtime = '%s', ingame = '%s' WHERE id = '%s'""" % (Ptime, InGame, Info[0])
                                mycursor.execute(sql)
                                await botsql.botmydb()
                                await lchannel.send(':airplane_departure: **' + Info[1] + '** has left the party! Online for: ' + ponline + '')
                                sql2 = """INSERT INTO serverstats (date, timestamp, users) VALUES ('%s', '%s', '%s')""" % (await timenow(), int(time.time()), await serverstatsupdate())
                                mycursor.execute(sql2)
                                await botsql.botmydb()
                            mycursor.close()
                        # Annocing that a boss location was found
                        if(re.search(pfind, line)):
                            newitem = re.search(pfind, line).group(1)
                            botsql = bot.get_cog('BotSQL')
                            mycursor = await botsql.get_cursor()
                            sql = """SELECT type, smessage, image FROM events WHERE type = '%s' LIMIT 1""" % (newitem)
                            mycursor.execute(sql)
                            Info = mycursor.fetchall()
                            Info=Info[0]
                            image = discord.File('img/' + Info[2], filename=Info[2])
                            embed = discord.Embed(title=Info[0], colour=discord.Colour(0x77ac18))
                            embed.set_thumbnail(url='attachment://' + Info[2])
                            embed.set_author(name="📢 Location Found")
                            await lchannel.send(file=image, embed=embed)
                            mycursor.close()
                        # Extra Server Info DB After this point
                        if config.EXSERVERINFO == True:
                        # Getting and storing how many zdos where saved
                            if(re.search(ssaved1, line)):
                                save1 = re.search(ssaved1, line).group(1)
                                botsql = bot.get_cog('BotSQL')
                                mycursor = await botsql.get_cursor()
                                sql = """INSERT INTO exstats (savezdos, timestamp) VALUES ('%s', '%s')""" % (save1, int(time.time()))
                                mycursor.execute(sql)
                                await botsql.botmydb()
                                mycursor.close()
                            # Getting time it took for the save
                            if(re.search(ssaved2, line)):
                                save2 = re.search(ssaved2, line).group(1)
                                botsql = bot.get_cog('BotSQL')
                                mycursor = await botsql.get_cursor()
                                tlookup = int(time.time()) - 60
                                sql = """SELECT id FROM exstats WHERE savesec is null AND timestamp BETWEEN '%s' AND '%s' LIMIT 1""" % (tlookup, int(time.time()))
                                mycursor.execute(sql)
                                Info = mycursor.fetchall()
                                row_count = mycursor.rowcount
                                if row_count == 1:
                                    Info=Info[0]
                                    if config.WORLDSIZE == True:
                                        sql ="""UPDATE exstats SET savesec = '%s', worldsize = '%s' WHERE id = '%s'""" % (save2, '{:,.2f}'.format(os.path.getsize(config.worldfile)/float(1<<20)), Info[0])
                                    else:
                                        sql = """UPDATE exstats SET savesec = '%s' WHERE id = '%s'""" % (save2, Info[0])
                                    mycursor.execute(sql)
                                    await botsql.botmydb()
                                else:
                                    print(Fore.RED + 'ERROR: Could not find save zdos info' + Style.RESET_ALL)
                                    if config.USEDEBUGCHAN == True:
                                        bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description="Could not find save zdos info", color=0xFF001E)
                                        bugerror.set_author(name=server_name)
                                        await bugchan.send(embed=bugerror)
                                mycursor.close()
                        # Getting and storing server version number in db, and announcing in channel if version was updated
                            if(re.search(sversion, line)):
                                serversion = re.search(sversion, line).group(1)
                                botsql = bot.get_cog('BotSQL')
                                mycursor = await botsql.get_cursor()
                                sql = """SELECT id, serverversion FROM exstats WHERE id = 1"""
                                mycursor.execute(sql)
                                Info = mycursor.fetchall()
                                row_count = mycursor.rowcount
                                if row_count == 0:
                                    print(Fore.RED + 'ERROR: Extra server info is set, but missing database table/info' + Style.RESET_ALL)
                                    if config.USEDEBUGCHAN == True:
                                        bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description="Extra server info is set, but missing database table/info", color=0xFF001E)
                                        bugerror.set_author(name=server_name)
                                        await bugchan.send(embed=bugerror)
                                else:
                                    Info=Info[0]
                                    if serversion != Info[1]:
                                        sql = """UPDATE exstats SET serverversion = '%s' WHERE id = '%s'""" % (serversion, Info[0])
                                        mycursor.execute(sql)
                                        await botsql.botmydb()
                                        await lchannel.send('**INFO:** Server has been updated to version: ' + serversion + '')
                                mycursor.close()
                            # Getting and storing game day in db (only reported in log when doing a sleep) reports day of sleep not day after waking up
                            if(re.search(gdays, line)):
                                gamedays = re.search(gdays, line).group(1)
                                botsql = bot.get_cog('BotSQL')
                                mycursor = await botsql.get_cursor()
                                sql = """INSERT INTO exstats (gameday, timestamp) VALUES ('%s', '%s')""" % (gamedays, int(time.time()))
                                mycursor.execute(sql)
                                await botsql.botmydb()
                                await lchannel.send('**INFO:** Server reported in game day as: ' + gamedays + '')
                                mycursor.close()
                        if config.PLOCINFO == True:
                            if(re.search(ploc, line)):
                                zone = re.search(ploc, line).group(1)
                                duration = re.search(ploc, line).group(2)
                                botsql = bot.get_cog('BotSQL')
                                mycursor = await botsql.get_cursor()
                                sql = """INSERT INTO plocinfo (zone, duration) VALUES ('%s', '%s')""" % (zone, duration)
                                mycursor.execute(sql)
                                await botsql.botmydb()
                                mycursor.close()
                            if(re.search(tloc, line)):
                                location = re.search(tloc, line).group(1)
                                botsql = bot.get_cog('BotSQL')
                                mycursor = await botsql.get_cursor()
                                sql = """SELECT id, locations FROM plocinfo WHERE locations IS NOT NULL"""
                                mycursor.execute(sql)
                                Info = mycursor.fetchall()
                                row_count = mycursor.rowcount
                                if row_count == 0:
                                    sql = """INSERT INTO plocinfo (locations) VALUES ('%s')""" % (location)
                                    mycursor.execute(sql)
                                    await botsql.botmydb()
                                    print(Fore.GREEN + '**INFO:** ' + location + ' Locations Loaded' + Style.RESET_ALL)
                                    if config.USEDEBUGCHAN == True:
                                        buginfo = discord.Embed(title=":white_check_mark: **INFO** :white_check_mark:", description='{} Locations Loaded'.format(location), color=0x7EFF00)
                                        await bugchan.send(embed=buginfo)
                                else:
                                    Info=Info[0]
                                    if location != Info[1]:
                                        sql = """UPDATE plocinfo SET locations = '%s' WHERE id = '%s'""" % (location, Info[0])
                                        mycursor.execute(sql)
                                        await botsql.botmydb()
                                        print(Fore.GREEN + '**INFO:** Locations has been updated to: ' + location + '' + Style.RESET_ALL)
                                        if config.USEDEBUGCHAN == True:
                                            buginfo = discord.Embed(title=":white_check_mark: **INFO** :white_check_mark:", description='Locations has been updated to: {}'.format(location), color=0x7EFF00)
                                            await bugchan.send(embed=buginfo)
                                mycursor.close()
                        await asyncio.sleep(0.2)
    except IOError:
        print('No valid log found, event reports disabled. Please check config.py')
        print('To generate server logs, run server with -logfile launch flag')
        print('Or permission error getting world file size')
        if config.USEDEBUGCHAN == True:
            bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description="No valid log found, event reports disabled. Please check config.py \n To generate server logs, run server with -logfile launch flag \n Or permission error getting world file size", color=0xFF001E)
            bugerror.set_author(name=server_name)
            await bugchan.send(embed=bugerror)

async def serverstatsupdate():
    try:
        if a2s.info(config.SERVER_ADDRESS):
            channel = bot.get_channel(chanID)
            oplayers = a2s.info(config.SERVER_ADDRESS).player_count
            if config.USEVCSTATS == True:
                await channel.edit(name=f"{emoji.emojize(':house:')} In-Game: {oplayers}" +" / 10")
    except Exception as e:
        print(Fore.RED + await timenow(), e, 'from A2S' + Style.RESET_ALL)
        channel = bot.get_channel(chanID)
        oplayers = 0
        if config.USEVCSTATS == True:
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
                    if config.USEVCSTATS == True:
                        channel = bot.get_channel(chanID)
                        await channel.edit(name=f"{emoji.emojize(':house:')} Server OnLine")
        except Exception as e:
            if config.USEVCSTATS == True:
                channel = bot.get_channel(chanID)
                await channel.edit(name=f"{emoji.emojize(':cross_mark:')} Server Offline")
            if sonline == 1:
                sonline = 0
                botsql = bot.get_cog('BotSQL')
                mycursor = await botsql.get_cursor()
                sql2 = """INSERT INTO serverstats (date, timestamp, users) VALUES ('%s', '%s', '%s')""" % (await timenow(), int(time.time()), sonline)
                mycursor.execute(sql2)
                await botsql.botmydb()
                mycursor.close()
            print(Fore.RED + await timenow(), e, 'from A2S, retrying (60s)...' + Style.RESET_ALL)
            if config.USEDEBUGCHAN == True:
                bugchan = bot.get_channel(dbchanID)
                bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description="{} from A2S, retrying (60s)...".format(e), color=0xFF001E)
                bugerror.set_author(name=server_name)
                await bugchan.send(embed=bugerror)
        await asyncio.sleep(60)

bot.loop.create_task(mainloop(file))
bot.run(config.BOT_TOKEN)
