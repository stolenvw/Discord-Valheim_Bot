import MySQLdb
import logging
from discord.ext import commands
from config import SQL_HOST as MYhost
from config import SQL_PORT as MYport
from config import SQL_USER as MYuser
from config import SQL_PASS as MYpass
from config import SQL_DATABASE as MYbase
from config import LOG_LEVEL


logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


# Connect to MYSQL
class BotSQL(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def mydbconnect(self):
        global mydb
        try:
            mydb = MySQLdb.connect(
                host=MYhost,
                user=MYuser,
                password=MYpass,
                database=MYbase,
                port=MYport,
            )
            logger.info(
                f"Connected to MySQL database... MySQL Server version {mydb.get_server_info()}"
            )
        except MySQLdb.OperationalError as err:
            logger.error(f"{err} From MySQL database")

    # Get mysql cursor
    async def get_cursor(self):
        try:
            mydb.ping()
        except NameError as er:
            logger.warning(f"{er} Reconnecting MySQL database")
            await self.mydbconnect()
        except MySQLdb.OperationalError as err:
            if err.args[0] == 2006:
                await self.mydbconnect()
                logger.warning("Connection to MySQL database went away... Reconnecting ")
        else:
            return mydb.cursor()

    # Mysql commit
    async def botmydb(self):
        mydb.commit()

    # Mysql get database connection
    async def get_mydb(self):
        try:
            mydb.ping()
        except NameError as er:
            logger.warning(f"{er} Reconnecting MySQL database")
            await self.mydbconnect()
        except MySQLdb.OperationalError as err:
            if err.args[0] == 2006:
                await self.mydbconnect()
                logger.warning("Connection to MySQL database went away... Reconnecting ")
        else:
            return mydb


async def setup(bot):
    await bot.add_cog(BotSQL(bot))
