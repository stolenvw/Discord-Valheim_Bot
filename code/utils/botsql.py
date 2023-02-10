import mysql.connector
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
                logger.info(
                    f"Connected to MySQL database... MySQL Server version {db_Info}"
                )
        except mysql.connector.Error as err:
            logger.error(f"{err} From MySQL database")

    # Get mysql cursor
    async def get_cursor(self):
        try:
            mydb.ping(reconnect=True, attempts=3, delay=5)
        except NameError as er:
            logger.warning(f"{er} Reconnecting MySQL database")
            await self.mydbconnect()
        except mysql.connector.Error:
            await self.mydbconnect()
            logger.warning("Connection to MySQL database went away... Reconnecting ")
        return mydb.cursor()

    # Mysql commit
    async def botmydb(self):
        mydb.commit()

    # Mysql get database connection
    async def get_mydb(self):
        try:
            mydb.ping(reconnect=True, attempts=3, delay=5)
        except NameError as er:
            logger.warning(f"{er} Reconnecting MySQL database")
            await self.mydbconnect()
        except mysql.connector.Error as err:
            await self.mydbconnect()
            logger.warning("Connection to MySQL database went away... Reconnecting ")
        return mydb


async def setup(bot):
    await bot.add_cog(BotSQL(bot))
