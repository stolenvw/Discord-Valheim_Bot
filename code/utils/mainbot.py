import config
import logging
import discord
import re
import time
import emoji
import a2s
import os
from discord.ext import commands, tasks
from datetime import datetime, timedelta


pdeath = "^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: Got character ZDOID from ([\w ]+) : 0:0"
pevent = (
    "^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: Random event set:(\w+)"
)
pjoin = "^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: Got character ZDOID from ([\w ]+) : ([-0-9]*:[-0-9]*)$"
pquit = "^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: Destroying abandoned non persistent zdo ([-0-9]*:[0-9]*) owner [-0-9]*$"
pfind = "^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: Found location of type (\w+)"
ssaved1 = (
    "^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: Saved ([0-9]+) ZDOs$"
)
ssaved2 = "^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: World saved \( ([0-9]+\.[0-9]+)ms \)$"
sversion = "^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: Valheim version: l-([\.0-9]+) \(network version [0-9]*\)$"
gdays = "^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: Time [\.0-9]+, day:([0-9]+)\s{1,}nextm:[\.0-9]+\s+skipspeed:[\.0-9]+$"
ploc = "^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: Placed locations in zone ([-,0-9]+)  duration ([\.0-9]+) ms$"
tloc = "^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: Loaded ([0-9]+) locations$"
joincode = '^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: Session "[\w ]+" registered with join code ([0-9]+)$'
servconnections = "^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}: Connections ([0-9]+) ZDOS:[0-9]+  sent:[0-9]+ recv:[0-9]+"
servplayfab = "^[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}:.+([pP]lay[fF]ab) logged in as .+$"

logger = logging.getLogger(__name__)
logger.setLevel(config.LOG_LEVEL)


class MainBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sonline = False
        self.last_pos = False
        self.crossplay = False
        self.voipchan = False
        self.vplayers = 0

    # Main loop for reading log file and outputing events
    @tasks.loop(seconds=2)
    async def mainloop(self, file):
        lchannel = self.bot.get_channel(config.LOGCHAN_ID)
        try:
            testfile = open(file)
            testfile.close()
            with open(file, encoding="utf-8", mode="r") as f:
                if self.last_pos:
                    f.seek(self.last_pos)
                else:
                    f.seek(0, 2)
                try:
                    line = f.readline()
                    self.last_pos = f.tell()
                except UnicodeDecodeError:
                    logger.warning(
                        "Got an invalid utf-8 character! Skipping moving to next line"
                    )
                else:
                    # Announcing join code and saving it to the mysql db
                    if re.search(joincode, line):
                        jocode = re.search(joincode, line).group(1)
                        botsql = self.bot.get_cog("BotSQL")
                        mycursor = await botsql.get_cursor()
                        mycursor.execute(
                            """SELECT jocode FROM serverinfo WHERE id = 1 LIMIT 1"""
                        )
                        Info = mycursor.fetchall()
                        row_count = mycursor.rowcount
                        if row_count == 0:
                            logger.error(f"ERROR: Join code missing from database")
                        else:
                            mycursor.execute(
                                """UPDATE serverinfo SET jocode = %s WHERE id = 1""",
                                (jocode,),
                            )
                            await botsql.botmydb()
                            embed = discord.Embed(
                                title="Join Code",
                                colour=discord.Colour(0xB6000E),
                                description=f"*{jocode}*",
                            )
                            embed.set_author(name=f"📢 {config.SERVER_NAME}")
                            await lchannel.send(embed=embed)
                        mycursor.close()
                    # Announcing players death
                    if re.search(pdeath, line):
                        pname = re.search(pdeath, line).group(1)
                        botsql = self.bot.get_cog("BotSQL")
                        mycursor = await botsql.get_cursor()
                        mycursor.execute(
                            """UPDATE players SET deaths = deaths + 1 WHERE user = %s""",
                            (pname,),
                        )
                        await botsql.botmydb()
                        mycursor.close()
                        await lchannel.send(f":skull: **{pname}** just died!")
                    # Announcing of mob events
                    if re.search(pevent, line):
                        eventID = re.search(pevent, line).group(1)
                        botsql = self.bot.get_cog("BotSQL")
                        mycursor = await botsql.get_cursor()
                        mycursor.execute(
                            """SELECT type, smessage, image FROM events WHERE type = %s LIMIT 1""",
                            (eventID,),
                        )
                        Info = mycursor.fetchall()
                        row_count = mycursor.rowcount
                        if row_count == 0:
                            logger.error(f"Event {eventID} missing from database")
                        else:
                            Info = Info[0]
                            image = discord.File(f"img/{Info[2]}", filename=Info[2])
                            embed = discord.Embed(
                                title=Info[0],
                                colour=discord.Colour(0xB6000E),
                                description=f"*{Info[1]}*",
                            )
                            embed.set_thumbnail(url=f"attachment://{Info[2]}")
                            embed.set_author(name="📢 Random Mob Event")
                            await lchannel.send(file=image, embed=embed)
                        mycursor.close()
                    # Announcing when a player joins the server, Announcing if they are a new player on the server, adds player to db if new, updates db with login time
                    if re.search(pjoin, line):
                        logJoin = re.search(pjoin, line).group(1)
                        logID = re.search(pjoin, line).group(2)
                        botsql = self.bot.get_cog("BotSQL")
                        mycursor = await botsql.get_cursor()
                        mycursor.execute(
                            """SELECT id, ingame FROM players WHERE user = %s""",
                            (logJoin,),
                        )
                        Info = mycursor.fetchall()
                        row_count = mycursor.rowcount
                        if row_count == 0:
                            StartDate = await self.timenow()
                            JoinTime = int(time.time())
                            InGame = 1
                            mycursor.execute(
                                """INSERT INTO players (user, valid, startdate, jointime, ingame) VALUES (%s, %s, %s, %s, %s)""",
                                (logJoin, logID, StartDate, JoinTime, InGame),
                            )
                            await botsql.botmydb()
                            await lchannel.send(
                                f":airplane_arriving: New player **{logJoin}** has joined the party!"
                            )
                        else:
                            Info = Info[0]
                            if Info[1] == 1:
                                mycursor.execute(
                                    """UPDATE players SET valid = %s WHERE id = %s""",
                                    (logID, Info[0]),
                                )
                                await botsql.botmydb()
                            else:
                                JoinTime = int(time.time())
                                InGame = 1
                                mycursor.execute(
                                    """UPDATE players SET valid = %s, jointime = %s, ingame = %s WHERE user = %s""",
                                    (logID, JoinTime, InGame, logJoin),
                                )
                                await botsql.botmydb()
                                await lchannel.send(
                                    f":airplane_arriving: **{logJoin}** has joined the party!"
                                )
                        mycursor.close()
                        if not self.crossplay:
                            await self.serverstatsupdate()
                    # Announcing when a player leaves the server, updates db with playtime
                    if re.search(pquit, line):
                        logquit = re.search(pquit, line).group(1)
                        botsql = self.bot.get_cog("BotSQL")
                        mycursor = await botsql.get_cursor()
                        mycursor.execute(
                            """SELECT id, user, jointime, playtime FROM players WHERE valid = %s""",
                            (logquit,),
                        )
                        Info = mycursor.fetchall()
                        row_count = mycursor.rowcount
                        if row_count == 1:
                            Info = Info[0]
                            EndTime = int(time.time())
                            Ptime = EndTime - Info[2] + Info[3]
                            ponline = await self.convert(EndTime - Info[2])
                            InGame = 0
                            mycursor.execute(
                                """UPDATE players SET playtime = %s, ingame = %s WHERE id = %s""",
                                (Ptime, InGame, Info[0]),
                            )
                            await botsql.botmydb()
                            await lchannel.send(
                                f":airplane_departure: **{Info[1]}** has left the party! Online for: {ponline}"
                            )
                        mycursor.close()
                        if not self.crossplay:
                            await self.serverstatsupdate()
                    # Announcing that a boss location was found
                    if re.search(pfind, line):
                        newitem = re.search(pfind, line).group(1)
                        botsql = self.bot.get_cog("BotSQL")
                        mycursor = await botsql.get_cursor()
                        mycursor.execute(
                            """SELECT type, smessage, image FROM events WHERE type = %s LIMIT 1""",
                            (newitem,),
                        )
                        Info = mycursor.fetchall()
                        try:
                            Info = Info[0]
                        except IndexError:
                            logger.error(
                                f"Could not find boss location info for {newitem} in the database."
                            )
                        image = discord.File(f"img/{Info[2]}", filename=Info[2])
                        embed = discord.Embed(
                            title=Info[0], colour=discord.Colour(0x77AC18)
                        )
                        embed.set_thumbnail(url=f"attachment://{Info[2]}")
                        embed.set_author(name="📢 Location Found")
                        await lchannel.send(file=image, embed=embed)
                        mycursor.close()
                    # Extra Server Info DB After this point
                    if config.EXSERVERINFO:
                        # Getting and storing how many zdos where saved
                        if re.search(ssaved1, line):
                            save1 = re.search(ssaved1, line).group(1)
                            botsql = self.bot.get_cog("BotSQL")
                            mycursor = await botsql.get_cursor()
                            mycursor.execute(
                                """INSERT INTO exstats (savezdos, timestamp) VALUES (%s, %s)""",
                                (save1, int(time.time())),
                            )
                            await botsql.botmydb()
                            mycursor.close()
                        # Getting time it took for the save
                        if re.search(ssaved2, line):
                            save2 = re.search(ssaved2, line).group(1)
                            botsql = self.bot.get_cog("BotSQL")
                            mycursor = await botsql.get_cursor()
                            tlookup = int(time.time()) - 60
                            mycursor.execute(
                                """SELECT id FROM exstats WHERE savesec is null AND timestamp BETWEEN %s AND %s LIMIT 1""",
                                (tlookup, int(time.time())),
                            )
                            Info = mycursor.fetchall()
                            row_count = mycursor.rowcount
                            if row_count == 1:
                                Info = Info[0]
                                if config.WORLDSIZE:
                                    mycursor.execute(
                                        """UPDATE exstats SET savesec = %s, worldsize = %s WHERE id = %s""",
                                        (
                                            save2,
                                            "{:,.2f}".format(
                                                os.path.getsize(config.worldfile)
                                                / float(1 << 20)
                                            ),
                                            Info[0],
                                        ),
                                    )
                                else:
                                    mycursor.execute(
                                        """UPDATE exstats SET savesec = %s WHERE id = %s""",
                                        (save2, Info[0]),
                                    )
                                    logger.debug(f"Last save took: {save2}ms.")
                                await botsql.botmydb()
                            else:
                                logger.error("Could not find save zdos info")
                            mycursor.close()
                        # Getting and storing server version number in db, and announcing in channel if version was updated
                        if re.search(sversion, line):
                            serversion = re.search(sversion, line).group(1)
                            botsql = self.bot.get_cog("BotSQL")
                            mycursor = await botsql.get_cursor()
                            mycursor.execute(
                                """SELECT id, serverversion FROM serverinfo WHERE id = 1"""
                            )
                            Info = mycursor.fetchall()
                            row_count = mycursor.rowcount
                            if row_count == 0:
                                logger.error(
                                    "Extra server info is set, but missing database table/info"
                                )
                            else:
                                Info = Info[0]
                                if serversion != Info[1]:
                                    mycursor.execute(
                                        """UPDATE serverinfo SET serverversion = %s WHERE id = %s""",
                                        (serversion, Info[0]),
                                    )
                                    if config.CHECK_UPDATE:
                                        getupdateinfo = self.bot.get_cog(
                                            "UpdateNeeeded"
                                        )
                                        valheiminfo = (
                                            await getupdateinfo.getvalheiminfo()
                                        )
                                        mycursor.execute(
                                            """UPDATE serverinfo SET steamtime = %s WHERE id = 1""",
                                            (valheiminfo,),
                                        )
                                    await botsql.botmydb()
                                    await lchannel.send(
                                        f"**INFO:** Server has been updated to version: {serversion}"
                                    )
                                    logger.info(
                                        f"Server has been updated to version: {serversion}"
                                    )
                            mycursor.close()
                        # Getting and storing game day in db (only reported in log when doing a sleep) reports day of sleep not day after waking up
                        if re.search(gdays, line):
                            gamedays = re.search(gdays, line).group(1)
                            botsql = self.bot.get_cog("BotSQL")
                            mycursor = await botsql.get_cursor()
                            mycursor.execute(
                                """UPDATE serverinfo SET gameday = %s WHERE id = 1""",
                                (gamedays,),
                            )
                            await botsql.botmydb()
                            await lchannel.send(
                                f"**INFO:** Server reported in game day as: {gamedays}"
                            )
                            mycursor.close()
                    # Locations Info DB After this point
                    if config.PLOCINFO:
                        # Add new location on map explored
                        if re.search(ploc, line):
                            zone = re.search(ploc, line).group(1)
                            duration = re.search(ploc, line).group(2)
                            botsql = self.bot.get_cog("BotSQL")
                            mycursor = await botsql.get_cursor()
                            mycursor.execute(
                                """INSERT INTO plocinfo (zone, duration) VALUES (%s, %s)""",
                                (zone, duration),
                            )
                            await botsql.botmydb()
                            mycursor.close()
                        # Add total locations to db
                        if re.search(tloc, line):
                            location = re.search(tloc, line).group(1)
                            botsql = self.bot.get_cog("BotSQL")
                            mycursor = await botsql.get_cursor()
                            mycursor.execute(
                                """SELECT id, locations FROM plocinfo WHERE locations IS NOT NULL"""
                            )
                            Info = mycursor.fetchall()
                            row_count = mycursor.rowcount
                            if row_count == 0:
                                mycursor.execute(
                                    """INSERT INTO plocinfo (locations) VALUES (%s)""",
                                    (location,),
                                )
                                await botsql.botmydb()
                                logger.info(f"{location} Locations Loaded")
                            else:
                                Info = Info[0]
                                if location != Info[1]:
                                    mycursor.execute(
                                        """UPDATE plocinfo SET locations = %s WHERE id = %s""",
                                        (location, Info[0]),
                                    )
                                    await botsql.botmydb()
                                    logger.info(
                                        f"Locations has been updated to: {location}"
                                    )
                            mycursor.close()
                    # Check if server is using crossplay
                    if not self.crossplay:
                        if re.search(servplayfab, line):
                            self.crossplay = True
                            logger.info(
                                "Server running in crossplay mode, using slower player count update!"
                            )
                    if self.crossplay:
                        # Crossplay update connected players
                        if re.search(servconnections, line):
                            oplayers = re.search(servconnections, line).group(1)
                            if oplayers != self.vplayers:
                                self.vplayers = oplayers
                                if config.USEVCSTATS and self.voipchan != None:
                                    channel = self.bot.get_channel(config.VCHANNEL_ID)
                                    await channel.edit(
                                        name=f"{emoji.emojize(':house:')} In-Game: {oplayers} / 10"
                                    )
        except IOError:
            logger.exception(
                "No valid log found, event reports disabled. Please check config.py \nTo generate server logs, run server with -logfile launch flag \nOr permission error getting world file size"
            )

    @mainloop.before_loop
    async def before_mainloop(self):
        await self.bot.wait_until_ready()
        logger.info("Valheim Discord Bot V4.0.0")
        logger.info(f"Bot connected as {self.bot.user}")
        logger.info(f"Command prefix: {config.BOT_PREFIX}")
        logger.info(f"Log channel: #{self.bot.get_channel(config.LOGCHAN_ID)}")
        if config.USEVCSTATS == True:
            logger.info(f"VoIP channel: #{self.bot.get_channel(config.VCHANNEL_ID)}")
            if self.bot.get_channel(config.VCHANNEL_ID) == None:
                logger.warn(
                    "USEVCSTATS is set to True, but VCHANNEL_ID returns no channel."
                )
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="Stolenvw ValheimBot"
            )
        )
        logger.info("Main loop started")

    async def timenow(self):
        now = datetime.now()
        gettime = now.strftime("%m/%d/%Y %H:%M:%S")
        return gettime

    async def convert(self, n):
        return str(timedelta(seconds=n))

    # Check to get how many players are on server and update voice channel name
    async def serverstatsupdate(self):
        try:
            if a2s.info(config.SERVER_ADDRESS):
                oplayers = a2s.info(config.SERVER_ADDRESS).player_count
                if config.USEVCSTATS and self.voipchan != None:
                    channel = self.bot.get_channel(config.VCHANNEL_ID)
                    await channel.edit(
                        name=f"{emoji.emojize(':house:')} In-Game: {oplayers} / 10"
                    )
        except Exception:
            logger.exception(f"Error from A2S")
            oplayers = 0
            if config.USEVCSTATS and self.voipchan != None:
                channel = self.bot.get_channel(config.VCHANNEL_ID)
                await channel.edit(
                    name=f"{emoji.emojize(':cross_mark:')} Server Offline"
                )
        else:
            return oplayers  # pyright: ignore

    # Loop to check if server is on-line
    @tasks.loop(minutes=1)
    async def serveronline(self):
        try:
            if a2s.info(config.SERVER_ADDRESS) and not self.sonline:
                self.sonline = True
                if config.USEVCSTATS and self.voipchan != None:
                    channel = self.bot.get_channel(config.VCHANNEL_ID)
                    await channel.edit(name=f"{emoji.emojize(':house:')} Server OnLine")
                logger.info("Server online")
        except Exception as e:
            if config.USEVCSTATS and self.voipchan != None:
                channel = self.bot.get_channel(config.VCHANNEL_ID)
                await channel.edit(
                    name=f"{emoji.emojize(':cross_mark:')} Server Offline"
                )
            if self.sonline:
                self.sonline = False
            logger.warning(f"{e} from A2S, retrying (60s)...")

    @serveronline.before_loop
    async def before_serveronline(self):
        await self.bot.wait_until_ready()
        self.voipchan = self.bot.get_channel(config.VCHANNEL_ID)
        logger.info("Server online loop started")

    # Opitional loop for checking server version from A2s instead of useing version from log file
    @tasks.loop(minutes=30)
    async def versioncheck(self):
        lchannel = self.bot.get_channel(config.LOGCHAN_ID)
        try:
            keyword = a2s.info(config.SERVER_ADDRESS).keywords
            serversion = re.search('^g=([0-9.]+)', keyword).group(1)
            logger.debug(f"Version check loop got version {serversion}")
            botsql = self.bot.get_cog("BotSQL")
            mycursor = await botsql.get_cursor()
            mycursor.execute(
                """SELECT id, serverversion FROM serverinfo WHERE id = 1"""
            )
            Info = mycursor.fetchall()
            row_count = mycursor.rowcount
            if row_count == 0:
                logger.error(
                    "Extra server info is set, but missing database table/info"
                )
            else:
                Info = Info[0]
                if serversion != Info[1]:
                    mycursor.execute(
                        """UPDATE serverinfo SET serverversion = %s WHERE id = %s""",
                        (serversion, Info[0]),
                    )
                    await botsql.botmydb()
                    await lchannel.send(
                        f"**INFO:** Server has been updated to version: {serversion}"
                    )
            mycursor.close()
        except Exception:
            logger.exception(
                f"Failed to get version info from server, trying again in 30 minutes."
            )

    @versioncheck.before_loop
    async def before_versioncheck(self):
        await self.bot.wait_until_ready()
        logger.info("Server verion check loop started")


async def setup(bot):
    await bot.add_cog(MainBot(bot))
