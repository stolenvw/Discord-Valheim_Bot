import discord, typing, config, time, mysql.connector
from discord.ext import commands
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import matplotlib.dates as md
import matplotlib.ticker as ticker
import matplotlib.spines as ms
import pandas as pd

class Main(commands.Cog):
    """
    Main bot commands
    """

    def __init__(self, bot):
        self.bot = bot

    async def chancheck(ctx):
        if ctx.channel.id == config.LOGCHAN_ID or commands.is_owner():
            return True

    @commands.command(name="deaths",
                      brief="Deaths leaderboard",
                      help="Shows a top 5 leaderboard of players with the most deaths. \n Available: 1-10 (default: 5)",
                      usage="<n>",
                      )
    @commands.has_any_role(config.DEATHS_CMD)
    @commands.check(chancheck)
    async def leaderboards(self, ctx, arg: typing.Optional[str] = '5'):
        ldrembed = discord.Embed(title=":skull_crossbones: __Death Leaderboards (top " + arg + ")__ :skull_crossbones:", color=0xFFC02C)
        botsql = self.bot.get_cog('BotSQL')
        mycursor = await botsql.get_cursor()
        sql = """SELECT user, deaths FROM players WHERE deaths > 0 ORDER BY deaths DESC LIMIT %s""" % (arg)
        mycursor.execute(sql)
        Info = mycursor.fetchall()
        row_count = mycursor.rowcount
        l = 1
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

    @leaderboards.error
    async def deaths_error_handler(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            if config.USEDEBUGCHAN == True:
                bugchan = self.bot.get_channel(config.BUGCHANNEL_ID)
                bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description='**{}** Tried to use command: **{}**\n{}'.format(ctx.author, ctx.command, error), color=0xFF001E)
                await bugchan.send(embed=bugerror)
        if isinstance(error, commands.CheckFailure):
            if config.USEDEBUGCHAN == True:
                bugchan = self.bot.get_channel(config.BUGCHANNEL_ID)
                bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description='**{}** Tried to use command: **{}**\nIn channel **#{}**'.format(ctx.author, ctx.command, ctx.channel), color=0xFF001E)
                await bugchan.send(embed=bugerror)

    @commands.command(name="stats",
                      brief="Graph of connected players",
                      help="Plots a graph of connected players over the last X hours.\n Available args: 24, 12, w (default: 24)",
                      usage="<arg>",
                      )
    @commands.has_any_role(config.STATS_CMD)
    @commands.check(chancheck)
    async def gen_plot(self, ctx, tmf: typing.Optional[str] = '24'):
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
        botsql = self.bot.get_cog('BotSQL')
        sqls = """SELECT date, users FROM serverstats WHERE timestamp BETWEEN '%s' AND '%s'""" % (tlookup, int(time.time()))
        df = pd.read_sql(sqls, await botsql.get_mydb(), parse_dates=['date'])
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
        fig.savefig('img/temp.png', transparent=True, pad_inches=0) # Save and upload Plot
        image = discord.File('img/temp.png', filename='temp.png')
        plt.close()
        embed = discord.Embed(title=config.SERVER_NAME, description=description, colour=12320855)
        embed.set_image(url='attachment://temp.png')
        await ctx.send(file=image, embed=embed)

    @gen_plot.error
    async def stats_error_handler(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            if config.USEDEBUGCHAN == True:
                bugchan = self.bot.get_channel(config.BUGCHANNEL_ID)
                bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description='**{}** Tried to use command: **{}**\n{}'.format(ctx.author, ctx.command, error), color=0xFF001E)
                await bugchan.send(embed=bugerror)
        if isinstance(error, commands.CheckFailure):
            if config.USEDEBUGCHAN == True:
                bugchan = self.bot.get_channel(config.BUGCHANNEL_ID)
                bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description='**{}** Tried to use command: **{}**\nIn channel **#{}**'.format(ctx.author, ctx.command, ctx.channel), color=0xFF001E)
                await bugchan.send(embed=bugerror)

    @commands.command(name="playerstats",
                      brief="Player stats",
                      help="Shows player stats on active monitored world.\n Arg= <Players Name>",
                      usage="<arg>",
                      )
    @commands.has_any_role(config.PLAYERSTATS_CMD)
    @commands.check(chancheck)
    async def playstats(self, ctx, arg):
        botsql = self.bot.get_cog('BotSQL')
        mycursor = await botsql.get_cursor()
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
                              value=str(timedelta(seconds = Info[3])),
                              inline=True)
            plsembed.add_field(name="Deaths:",
                              value=Info[1],
                              inline=True)
            await ctx.send(embed=plsembed)
        else:
            await ctx.send(content=':no_entry_sign: **' + arg + '** Not Found')
        mycursor.close()

    @playstats.error
    async def playerstats_error_handler(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            if config.USEDEBUGCHAN == True:
                bugchan = self.bot.get_channel(config.BUGCHANNEL_ID)
                bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description='**{}** Tried to use command: **{}**\n{}'.format(ctx.author, ctx.command, error), color=0xFF001E)
                await bugchan.send(embed=bugerror)
        if isinstance(error, commands.CheckFailure):
            if config.USEDEBUGCHAN == True:
                bugchan = self.bot.get_channel(config.BUGCHANNEL_ID)
                bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description='**{}** Tried to use command: **{}**\nIn channel **#{}**'.format(ctx.author, ctx.command, ctx.channel), color=0xFF001E)
                await bugchan.send(embed=bugerror)

    @commands.command(name="active",
                      brief="Active players",
                      help="Shows who is currently logged into the server and how long they have been on for.",
                      )
    @commands.has_any_role(config.ACTIVE_CMD)
    @commands.check(chancheck)
    async def actives(self, ctx):
        botsql = self.bot.get_cog('BotSQL')
        mycursor = await botsql.get_cursor()
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
                 ponline = str(timedelta(seconds = EndTime - ind[1]))
                 ldrembed.add_field(name="{}".format(pname),
                                    value='{} {}'.format(onfor,ponline),
                                    inline=False)
             await ctx.send(embed=ldrembed)
        mycursor.close()

    @actives.error
    async def active_error_handler(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            if config.USEDEBUGCHAN == True:
                bugchan = self.bot.get_channel(config.BUGCHANNEL_ID)
                bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description='**{}** Tried to use command: **{}**\n{}'.format(ctx.author, ctx.command, error), color=0xFF001E)
                await bugchan.send(embed=bugerror)
        if isinstance(error, commands.CheckFailure):
            if config.USEDEBUGCHAN == True:
                bugchan = self.bot.get_channel(config.BUGCHANNEL_ID)
                bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description='**{}** Tried to use command: **{}**\nIn channel **#{}**'.format(ctx.author, ctx.command, ctx.channel), color=0xFF001E)
                await bugchan.send(embed=bugerror)

    @commands.command(name="version",
                      brief="Server Versions",
                      help="Shows current version of Valheim server is running.",
                      )
    @commands.has_any_role(config.VERSIONS_CMD)
    @commands.check(chancheck)
    async def versions(self, ctx):
        botsql = self.bot.get_cog('BotSQL')
        mycursor = await botsql.get_cursor()
        sql = """SELECT serverversion FROM exstats WHERE id = 1"""
        mycursor.execute(sql)
        Info = mycursor.fetchall()
        row_count = mycursor.rowcount
        if row_count == 1:
            Info=Info[0]
            sembed = discord.Embed(title="Server Versions", color=0x407500)
            sembed.add_field(name="Valheim:",
                               value='{}'.format(Info[0]),
                               inline=True)
            await ctx.send(embed=sembed)
        else:
            await ctx.send(content=':no_entry_sign: Sorry no game version info found in the DB')
        mycursor.close()

    @versions.error
    async def version_error_handler(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            if config.USEDEBUGCHAN == True:
                bugchan = self.bot.get_channel(config.BUGCHANNEL_ID)
                bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description='**{}** Tried to use command: **{}**\n{}'.format(ctx.author, ctx.command, error), color=0xFF001E)
                await bugchan.send(embed=bugerror)
        if isinstance(error, commands.CheckFailure):
            if config.USEDEBUGCHAN == True:
                bugchan = self.bot.get_channel(config.BUGCHANNEL_ID)
                bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description='**{}** Tried to use command: **{}**\nIn channel **#{}**'.format(ctx.author, ctx.command, ctx.channel), color=0xFF001E)
                await bugchan.send(embed=bugerror)

    @commands.command(name="setstatus",
                      brief="Set bot status",
                      help="Set status message of the bot. \n Available arg: playing, watching, listening",
                      usage='<arg> <"arg1">',
                      )
    @commands.has_any_role(config.SETSTATUS_CMD)
    @commands.check(chancheck)
    async def setstatus(self, ctx, arg: typing.Optional[str] = '0', arg1: typing.Optional[str] = '1'):
          if arg == "playing":
             await self.bot.change_presence(activity=discord.Game(arg1))
    #      elif arg == "streaming":
    #         await bot.change_presence(activity=discord.Streaming(name=arg1, url=arg2))
          elif arg == "watching":
             await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=arg1))
          elif arg == "listening":
             await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=arg1))
          else:
               await ctx.channel.send('Usage: `{}setstatus <playing|watching|listening> "<Some activity>"`'.format(self.bot.command_prefix))

    @setstatus.error
    async def setstatus_error_handler(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            if config.USEDEBUGCHAN == True:
                bugchan = self.bot.get_channel(config.BUGCHANNEL_ID)
                bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description='**{}** Tried to use command: **{}**\n{}'.format(ctx.author, ctx.command, error), color=0xFF001E)
                await bugchan.send(embed=bugerror)
            if isinstance(error, commands.CheckFailure):
                if config.USEDEBUGCHAN == True:
                    bugchan = self.bot.get_channel(config.BUGCHANNEL_ID)
                    bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description='**{}** Tried to use command: **{}**\nIn channel **#{}**'.format(ctx.author, ctx.command, ctx.channel), color=0xFF001E)
                    await bugchan.send(embed=bugerror)

    @commands.command(name="savestats",
                      brief="Save stats",
                      help="Shows how many zods where saved and time it took to save them.",
                      )
    @commands.has_any_role(config.SAVESTATS_CMD)
    @commands.check(chancheck)
    async def savestats(self, ctx):
        if config.EXSERVERINFO == True:
            botsql = self.bot.get_cog('BotSQL')
            mycursor = await botsql.get_cursor()
            sql = """SELECT savezdos, savesec, worldsize, timestamp FROM exstats WHERE savesec is not null AND savezdos is not null ORDER BY timestamp DESC LIMIT 1"""
            mycursor.execute(sql)
            Info = mycursor.fetchall()
            row_count = mycursor.rowcount
            if row_count == 1:
                Info=Info[0]
                sembed = discord.Embed(title="World File Save Stats", color=0x407500, timestamp=datetime.utcfromtimestamp(Info[3]))
                sembed.set_footer(text="Last saved")
                sembed.add_field(name="Zdos Saved:",
                               value='{}'.format(Info[0]),
                               inline=True)
                sembed.add_field(name="Saving Took:",
                              value='{}ms'.format(Info[1]),
                              inline=True)
                if config.WORLDSIZE == True:
                    sembed.add_field(name="World Size:",
                                  value='{}MB'.format(Info[2]),
                                  inline=True)
                await ctx.send(embed=sembed)
            else:
                await ctx.send(content=':no_entry_sign: No World File Save Stats Found')
            mycursor.close()
        else:
            await ctx.send(content=':no_entry_sign: Extra Server Info is turned off, turn on to see save stats')

    @savestats.error
    async def savestats_error_handler(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            if config.USEDEBUGCHAN == True:
                bugchan = self.bot.get_channel(config.BUGCHANNEL_ID)
                bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description='**{}** Tried to use command: **{}**\n{}'.format(ctx.author, ctx.command, error), color=0xFF001E)
                await bugchan.send(embed=bugerror)
            if isinstance(error, commands.CheckFailure):
                if config.USEDEBUGCHAN == True:
                    bugchan = self.bot.get_channel(config.BUGCHANNEL_ID)
                    bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description='**{}** Tried to use command: **{}**\nIn channel **#{}**'.format(ctx.author, ctx.command, ctx.channel), color=0xFF001E)
                    await bugchan.send(embed=bugerror)

def setup(bot):
    bot.add_cog(Main(bot))
