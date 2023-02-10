import discord
import config
import time
import logging
from typing import Literal, Optional
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)
logger.setLevel(config.LOG_LEVEL)


class Main(commands.Cog):
    """
    Main bot commands
    """

    def __init__(self, bot):
        self.bot = bot

    # Slash command error handling
    async def cog_app_command_error(self, interaction, error) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            logger.error(
                f"MissingPermissions from command {interaction.command.name}, User: {interaction.user.name}, {error}"
            )
            if interaction.response.is_done():
                await interaction.followup.send(
                    f'Command "{interaction.command.name}" gave error {error}',
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    f'Command "{interaction.command.name}" gave error {error}',
                    ephemeral=True,
                )
        if isinstance(error, app_commands.errors.CheckFailure):
            logger.error(
                f"CheckFailure from command {interaction.command.name}, User: {interaction.user.name}, {error}"
            )
            if interaction.response.is_done():
                await interaction.followup.send(
                    f'Command "{interaction.command.name}" gave error {error}',
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    f'Command "{interaction.command.name}" gave error {error}',
                    ephemeral=True,
                )
        else:
            logger.error(f"An error occurred! User: {interaction.user.name}, {error}")
            if interaction.response.is_done():
                await interaction.followup.send("An error occurred!", ephemeral=True)
            else:
                await interaction.response.send_message(
                    "An error occurred!", ephemeral=True
                )

    # Deaths command
    @app_commands.command(
        name="deaths",
        description="Shows a top 5 leaderboard of players with the most deaths. \n Available: 1-10 (default: 5)",
    )
    @app_commands.default_permissions(use_application_commands=True, send_messages=True)
    @app_commands.checks.bot_has_permissions(send_messages=True)
    async def leaderboards(
        self, interaction: discord.Integration, arg: Optional[int] = 5
    ):
        ldrembed = discord.Embed(
            title=f":skull_crossbones: __Death Leaderboards (top {arg})__ :skull_crossbones:",
            color=0xFFC02C,
        )
        botsql = self.bot.get_cog("BotSQL")
        mycursor = await botsql.get_cursor()
        sql = (
            """SELECT user, deaths FROM players WHERE deaths > 0 ORDER BY deaths DESC LIMIT %s"""
            % (arg)
        )
        mycursor.execute(sql)
        Info = mycursor.fetchall()
        row_count = mycursor.rowcount
        l = 1
        for ind in Info:
            grammarnazi = "deaths"
            leader = ""
            pdname = ind[0]
            pddeath = ind[1]
            if pddeath == 1:
                grammarnazi = "death"
            if l == 1:
                leader = ":crown:"
            ldrembed.add_field(
                name="{} {}".format(pdname, leader),
                value="{} {}".format(pddeath, grammarnazi),
                inline=False,
            )
            l += 1
        mycursor.close()
        await interaction.response.send_message(embed=ldrembed)

    # Playerstats command
    @app_commands.command(
        name="playerstats",
        description="Shows player stats on active monitored world.\n Arg= <Players Name>",
    )
    @app_commands.rename(arg="name")
    @app_commands.describe(arg="Players Name")
    @app_commands.default_permissions(use_application_commands=True, send_messages=True)
    @app_commands.checks.bot_has_permissions(send_messages=True)
    async def playstats(self, interaction: discord.Integration, arg: str):
        botsql = self.bot.get_cog("BotSQL")
        mycursor = await botsql.get_cursor()
        sql = (
            """SELECT user, deaths, startdate, playtime FROM players WHERE user = '%s'"""
            % (arg)
        )
        mycursor.execute(sql)
        Info = mycursor.fetchall()
        row_count = mycursor.rowcount
        if row_count == 1:
            Info = Info[0]
            plsembed = discord.Embed(
                title=":bar_chart: __Player Stats For " + Info[0] + "__ :bar_chart:",
                color=0x4A90E2,
            )
            plsembed.add_field(
                name="Server Join Date:", value="{}".format(Info[2]), inline=True
            )
            plsembed.add_field(
                name="Play Time:", value=str(timedelta(seconds=Info[3])), inline=True
            )
            plsembed.add_field(name="Deaths:", value=Info[1], inline=True)
            await interaction.response.send_message(embed=plsembed)
        else:
            await interaction.response.send_message(
                f":no_entry_sign: **{arg}** Not Found"
            )
        mycursor.close()

    # Active command
    @app_commands.command(
        name="active",
        description="Shows who is currently logged into the server and how long they have been on for.",
    )
    @app_commands.default_permissions(use_application_commands=True, send_messages=True)
    @app_commands.checks.bot_has_permissions(send_messages=True)
    async def actives(self, interaction: discord.Integration):
        botsql = self.bot.get_cog("BotSQL")
        mycursor = await botsql.get_cursor()
        sql = """SELECT user, jointime FROM players WHERE ingame = 1 ORDER BY jointime LIMIT 10"""
        mycursor.execute(sql)
        Info = mycursor.fetchall()
        row_count = mycursor.rowcount
        if row_count == 0:
            await interaction.response.send_message(
                ":globe_with_meridians: 0 Players Active"
            )
        else:
            ldrembed = discord.Embed(
                title=":man_raising_hand: __Active Users__ :woman_raising_hand:",
                color=0x50E3C2,
            )
            EndTime = int(time.time())
            for ind in Info:
                pname = ind[0]
                onfor = "Online For:"
                ponline = str(timedelta(seconds=EndTime - ind[1]))
                ldrembed.add_field(
                    name="{}".format(pname),
                    value="{} {}".format(onfor, ponline),
                    inline=False,
                )
            await interaction.response.send_message(embed=ldrembed)
        mycursor.close()

    # Version command
    @app_commands.command(
        name="version",
        description="Shows current version of Valheim server is running.",
    )
    @app_commands.default_permissions(use_application_commands=True, send_messages=True)
    @app_commands.checks.bot_has_permissions(send_messages=True)
    async def versions(self, interaction: discord.Integration):
        botsql = self.bot.get_cog("BotSQL")
        mycursor = await botsql.get_cursor()
        sql = """SELECT serverversion FROM serverinfo WHERE id = 1"""
        mycursor.execute(sql)
        Info = mycursor.fetchall()
        row_count = mycursor.rowcount
        if row_count == 1:
            Info = Info[0]
            sembed = discord.Embed(title="Server Versions", color=0x407500)
            sembed.add_field(name="Valheim:", value="{}".format(Info[0]), inline=True)
            await interaction.response.send_message(embed=sembed)
        else:
            await interaction.response.send_message(
                content=":no_entry_sign: Sorry no game version info found in the DB"
            )
        mycursor.close()

    # Setstatus command
    @app_commands.command(
        name="setstatus", description="Set status message of the bot."
    )
    @app_commands.rename(arg="activity")
    @app_commands.rename(arg1="message")
    @app_commands.default_permissions(use_application_commands=True, send_messages=True, administrator=True)
    @app_commands.checks.bot_has_permissions(send_messages=True)
    async def _setstatus(
        self,
        interaction: discord.Integration,
        arg: Literal["playing", "watching", "listening"],
        arg1: str,
    ):
        if arg == "playing":
            await self.bot.change_presence(activity=discord.Game(arg1))
        #      elif arg == "streaming":
        #         await bot.change_presence(activity=discord.Streaming(name=arg1, url=arg2))
        elif arg == "watching":
            await self.bot.change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching, name=arg1)
            )
        elif arg == "listening":
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.listening, name=arg1
                )
            )
        await interaction.response.send_message(
            f"Status updated to: {arg}: {arg1}", ephemeral=True
        )

    # Savestats command
    @app_commands.command(
        name="savestats",
        description="Shows how many zods where saved and time it took to save them.",
    )
    @app_commands.default_permissions(use_application_commands=True, send_messages=True, administrator=True)
    @app_commands.checks.bot_has_permissions(send_messages=True)
    async def savestats(self, interaction: discord.Integration):
        if config.EXSERVERINFO == True:
            botsql = self.bot.get_cog("BotSQL")
            mycursor = await botsql.get_cursor()
            sql = """SELECT savezdos, savesec, worldsize, timestamp FROM exstats WHERE savesec is not null AND savezdos is not null ORDER BY timestamp DESC LIMIT 1"""
            mycursor.execute(sql)
            Info = mycursor.fetchall()
            row_count = mycursor.rowcount
            if row_count == 1:
                Info = Info[0]
                sembed = discord.Embed(
                    title="World File Save Stats",
                    color=0x407500,
                    timestamp=datetime.fromtimestamp(Info[3]),
                )
                sembed.set_footer(text="Last saved")
                sembed.add_field(
                    name="Zdos Saved:", value="{}".format(Info[0]), inline=True
                )
                sembed.add_field(
                    name="Saving Took:", value="{}ms".format(Info[1]), inline=True
                )
                if config.WORLDSIZE == True:
                    sembed.add_field(
                        name="World Size:", value="{}MB".format(Info[2]), inline=True
                    )
                await interaction.response.send_message(embed=sembed, ephemeral=True)
            else:
                await interaction.response.send_message(
                    ":no_entry_sign: No World File Save Stats Found", ephemeral=True
                )
            mycursor.close()
        else:
            await interaction.response.send_message(
                ":no_entry_sign: Extra Server Info is turned off, turn on to see save stats",
                ephemeral=True,
            )

    # Joincode command
    @app_commands.command(
        name="joincode",
        description="Shows join code for the server. (For servers using crossplay)",
    )
    @app_commands.default_permissions(use_application_commands=True, send_messages=True)
    @app_commands.checks.bot_has_permissions(send_messages=True)
    async def _joincode(self, interaction: discord.Integration):
        ldrembed = discord.Embed(
            title=config.SERVER_NAME,
            color=0xFFC02C,
        )
        botsql = self.bot.get_cog("BotSQL")
        mycursor = await botsql.get_cursor()
        sql = """SELECT jocode FROM serverinfo WHERE id = 1 LIMIT 1"""
        mycursor.execute(sql)
        Info = mycursor.fetchall()
        row_count = mycursor.rowcount
        if row_count == 0:
            logger.error(f"ERROR: Join code missing from database")
            await interaction.response.send_message(
                "No join code found sorry", ephemeral=True
            )
        else:
            ldrembed.add_field(
                name="Join Code",
                value=Info[0][0],
                inline=False,
            )
            await interaction.response.send_message(embed=ldrembed)
        mycursor.close()


async def setup(bot):
    await bot.add_cog(Main(bot), guilds=[discord.Object(id=config.DISCORD_SERVER)])
