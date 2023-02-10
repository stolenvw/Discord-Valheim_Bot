import logging
import discord
from datetime import datetime
from discord.ext import commands, tasks
from steam.client import SteamClient
from steam.enums import EResult
from config import LOGCHAN_ID, LOG_LEVEL, SERVER_NAME


logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
client = SteamClient()


class UpdateNeeeded(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.botsql = False
        self.ServerInfo = False

    # Get release timestamp from steam for valheim dedicated server
    async def getvalheiminfo(self):
        if client.logged_on:
            try:
                valheiminfo = client.get_product_info(apps=[896660], timeout=5)["apps"][
                    896660
                ]["depots"]["branches"]["public"]["timeupdated"]
                return int(valheiminfo)
            except Exception as e:
                logger.error(f"Failed to get last update time from steam: {e}")
                return False
        if client.relogin_available:
            login = client.relogin()
            logger.debug("Relogging in to steam")
        else:
            login = client.anonymous_login()
            logger.debug("Logging in to steam")
        if login == EResult.OK:
            logger.debug("Steam login successful")
            valheiminfo = client.get_product_info(apps=[896660], timeout=5)["apps"][
                896660
            ]["depots"]["branches"]["public"]["timeupdated"]
            logger.debug(f"Got server public branch last update time as {valheiminfo}")
            client.logout()
            logger.debug("Steam logout")
            return int(valheiminfo)
        else:
            logger.warning("Failed to login to steam")
            return False

    # loop for checking if server is upto date
    @tasks.loop(hours=1)
    async def checkversion(self):
        await self.bot.wait_until_ready()
        lchannel = self.bot.get_channel(LOGCHAN_ID)
        try:
            valheiminfo = await self.getvalheiminfo()
            if not valheiminfo:
                return
            valheimupdatetime = datetime.fromtimestamp(valheiminfo).strftime(
                "%A %B %d, %Y %I:%M %p"
            )
            ldrembed = discord.Embed(
                title=":sos: **OUTDATED VERSION** :sos:", color=0xFF001E
            )
            needwarring = 0
            self.botsql = self.bot.get_cog("BotSQL")
            mycursor = await self.botsql.get_cursor()
            sql = """SELECT upnotify, steamtime FROM serverinfo WHERE id = '1'"""
            mycursor.execute(sql)
            Info = mycursor.fetchall()
            await self.botsql.botmydb()
            if valheiminfo == Info[0][1] or Info[0][1] is None:
                logger.debug("Server is running current version rechecking in (1H)...")
                if Info[0][1] is None:
                    sql = f"UPDATE serverinfo SET steamtime = '{valheiminfo}' WHERE id = '1'"
                    mycursor.execute(sql)
                    await self.botsql.botmydb()
                if Info[0][0] == 1:
                    sql = """UPDATE serverinfo SET upnotify = '0' WHERE id = '1'"""
                    mycursor.execute(sql)
                    await self.botsql.botmydb()
            else:
                logger.warning(
                    f"Server is running outdated version, please update server. New version released on {valheimupdatetime} Rechecking in (1H)..."
                )
                if Info[0][0] == 0:
                    needwarring = 1
                    sql = """UPDATE serverinfo SET upnotify = '1' WHERE id = '1'"""
                    mycursor.execute(sql)
                    await self.botsql.botmydb()
                    ldrembed.add_field(
                        name=f"{SERVER_NAME}:",
                        value=f"New version released on steam at {valheimupdatetime}",
                        inline=False,
                    )
            mycursor.close()
            if needwarring == 1:
                await lchannel.send(embed=ldrembed)
        except Exception as e:
            logger.exception(f"{e} from version check, retrying (1H)...")

    @checkversion.before_loop
    async def before_checkversion(self):
        await self.bot.wait_until_ready()
        logger.info("Checkversion loop started")

    @checkversion.after_loop
    async def on_checkversion_cancel(self):
        if self.checkversion.is_being_cancelled():
            logger.warning("Checkversion has been cancelled")
        else:
            logger.warning("Checkversion has been stopped")


async def setup(bot):
    await bot.add_cog(UpdateNeeeded(bot))
