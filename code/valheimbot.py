import os
import discord
import signal
import logging
from config import (
    VALHEIM_SERVER_LOG,
    BOT_PREFIX,
    LOG_LEVEL,
    BOT_TOKEN,
    USEDEBUGCHAN,
    DISCORD_SERVER,
    LOG_FILE,
    EXSERVERINFO,
    VERSIONLOOP,
    CHECK_UPDATE,
)
from discord.ext import commands
from logging.handlers import TimedRotatingFileHandler


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
startup_extensions = ["utils.botsql", "utils.mainbot"]
cogs_dir = "botcmds"


logging.basicConfig(
    handlers=[TimedRotatingFileHandler(LOG_FILE, when="midnight", backupCount=5)],
    format="%(asctime)s - %(levelname)s - %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
dislog = logging.getLogger("discord")
logger.setLevel(LOG_LEVEL)
dislog.setLevel("INFO")


def signal_handler(signal, frame):
    logger.warning(f"Signal handler called with signal: {signal}... Shutting down")
    logging.shutdown()
    os._exit(0)


class MyBot(commands.Bot):
    async def setup_hook(self):
        signal.signal(signal.SIGINT, signal_handler)
        for extension in startup_extensions:
            try:
                await bot.load_extension(extension)
                logger.debug(f"Loaded extension {extension}")
            except commands.ExtensionAlreadyLoaded:
                logger.error(f"{extension} already loaded")
            except commands.ExtensionError as e:
                exc = "{}: {}".format(type(e).__name__, e)
                logger.error(exc)
        for extension in [
            f.replace(".py", "")
            for f in os.listdir(cogs_dir)
            if os.path.isfile(os.path.join(cogs_dir, f))
        ]:
            try:
                await bot.load_extension(cogs_dir + "." + extension)
                logger.debug(f"Loaded extension {cogs_dir}.{extension}")
            except Exception as e:
                exc = "{}: {}".format(type(e).__name__, e)
                logger.error(exc)
        botsql = bot.get_cog("BotSQL")
        await botsql.mydbconnect()
        maincog = bot.get_cog("MainBot")
        maincog.mainloop.start(VALHEIM_SERVER_LOG)
        maincog.serveronline.start()
        if USEDEBUGCHAN:
            await bot.load_extension("utils.debugchan")
            logger.debug("Loaded extension utils.debugchan")
            bugcog = bot.get_cog("DebugBot")
            bugcog.debugloop.start()
        if EXSERVERINFO and VERSIONLOOP:
            maincog.versioncheck.start()
        if CHECK_UPDATE:
            await bot.load_extension("utils.updateneeded")
            logger.debug("Loaded extension utils.updateneeded")
            bot.get_cog("UpdateNeeeded").checkversion.start()
        self.tree.copy_global_to(guild=discord.Object(id=DISCORD_SERVER))
        await self.tree.sync(guild=discord.Object(id=DISCORD_SERVER))
        logger.info(f"Synced slash commands for {self.user}")


if __name__ == "__main__":
    bot = MyBot(command_prefix=BOT_PREFIX, intents=intents)
    bot.run(BOT_TOKEN, log_handler=None)
