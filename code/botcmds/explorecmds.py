import discord, typing, config
from discord.ext import commands

class Explored(commands.Cog):
    """
    Explored commands
    """

    def __init__(self, bot):
        self.bot = bot

    async def chancheck(ctx):
        if ctx.channel.id == config.LOGCHAN_ID or commands.is_owner():
            return True

    @commands.command(name='explored',
                      brief="Explored stats",
                      help="Shows total world locations and how many have be explored.",
                      )
    @commands.has_any_role(config.PLOC_CMD)
    @commands.check(chancheck)
    async def explored(self, ctx):
        ldrembed = discord.Embed(title="World Explored Stats", color=0x33a163)
        botsql = self.bot.get_cog('BotSQL')
        mycursor = await botsql.get_cursor()
        sql = """SELECT COUNT(*) FROM plocinfo WHERE locations IS NULL"""
        mycursor.execute(sql)
        Info = mycursor.fetchall()
        sql1 = """SELECT locations FROM plocinfo WHERE locations IS NOT NULL LIMIT 1"""
        mycursor.execute(sql1)
        Info1 = mycursor.fetchall()
        mycursor.close()
        Info=Info[0]
        Info1=Info1[0]
        ldrembed.add_field(name="Total Locations",
                           value="{}".format(Info1[0]),
                           inline=True)
        ldrembed.add_field(name="Locations Explored",
                           value="{}".format(Info[0]),
                           inline=True)
        ldrembed.add_field(name="Percent of World Explored",
                           value="{}%".format(format(Info[0]/int(Info1[0])*100, ".2f")),
                           inline=True)
        await ctx.send(embed=ldrembed)

    @explored.error
    async def explored_error_handler(self, ctx, error):
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
    bot.add_cog(Explored(bot))
