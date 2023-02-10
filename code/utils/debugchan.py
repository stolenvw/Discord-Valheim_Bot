import logging
import re
import discord
from datetime import datetime
from discord.ext import commands, tasks
from config import LOG_LEVEL, BUGCHANNEL_ID, LOG_FILE, SERVER_NAME

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


class DebugBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_pos = False

    # Loop for reading bots log file and sending to discord channel
    @tasks.loop(seconds=2)
    async def debugloop(self):
        bugchannel = self.bot.get_channel(BUGCHANNEL_ID)
        try:
            testfile = open(LOG_FILE)
            testfile.close()
            with open(LOG_FILE, encoding="utf-8", mode="r") as f:
                if self.last_pos and not await self.checktime():
                    f.seek(self.last_pos)
                elif len(f.readlines()) < 25:
                    f.seek(0, 0)
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
                    if line:
                        newline = re.search(
                            "^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} - (\w+) - ([\w\._]+:) (.+)$",
                            line,
                        )
                        if re.search(
                            "^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} - \w+ - [\w\._]+: Got current time: 00:01, Resetting log file position for debug channel output$",
                            line,
                        ):
                            return
                        if newline:
                            if newline.group(1) == "INFO":
                                buginfo = discord.Embed(
                                    title=":white_check_mark: **INFO** :white_check_mark:",
                                    description=newline.group(3),
                                    color=0x7EFF00,
                                )
                                buginfo.set_author(name=SERVER_NAME)
                                buginfo.set_footer(text=newline.group(2))
                            elif newline.group(1) == "WARNING":
                                buginfo = discord.Embed(
                                    title=":biohazard: **WARNING** :biohazard:",
                                    description=newline.group(3),
                                    color=0xD36803,
                                )
                                buginfo.set_author(name=SERVER_NAME)
                                buginfo.set_footer(text=newline.group(2))
                            elif newline.group(1) == "ERROR":
                                buginfo = discord.Embed(
                                    title=":sos: **ERROR** :sos:",
                                    description=newline.group(3),
                                    color=0xFF001E,
                                )
                                buginfo.set_author(name=SERVER_NAME)
                                buginfo.set_footer(text=newline.group(2))
                            else:
                                buginfo = discord.Embed(
                                    title=f":large_blue_diamond: **{newline.group(1)}** :large_blue_diamond:",
                                    description=newline.group(3),
                                    color=0x0407CD,
                                )
                                buginfo.set_author(name=SERVER_NAME)
                                buginfo.set_footer(text=newline.group(2))
                            await bugchannel.send(embed=buginfo)

        except IOError:
            logger.exception("Log file not found")

    @debugloop.before_loop
    async def before_debugloop(self):
        await self.bot.wait_until_ready()
        logger.info(f"Bug channel: {self.bot.get_channel(BUGCHANNEL_ID)}")
        logger.info("Bug to discord loop started")

    # Check if its 1 min after midnight and reset log position
    async def checktime(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        if current_time == "00:01":
            logger.debug(
                f"Got current time: {current_time}, Resetting log file position for debug channel output"
            )
            return True
        else:
            return False


async def setup(bot):
    await bot.add_cog(DebugBot(bot))
