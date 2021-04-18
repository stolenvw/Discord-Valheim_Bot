import mysql.connector, config, discord, asyncio
from discord.ext import commands
from colorama import Fore, Style, init
from config import SQL_HOST as MYhost
from config import SQL_PORT as MYport
from config import SQL_USER as MYuser
from config import SQL_PASS as MYpass
from config import SQL_DATABASE as MYbase

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
        bugchan = self.bot.get_channel(config.BUGCHANNEL_ID)
        try:
            if mydb.is_connected():
                db_Info = mydb.get_server_info()
                print(Fore.GREEN + "Connected to MySQL database... MySQL Server version ", db_Info + Style.RESET_ALL)
                if config.USEDEBUGCHAN == True:
                    buginfo = discord.Embed(title=":white_check_mark: **INFO** :white_check_mark:", description="Connected to MySQL database... MySQL Server version " + db_Info, color=0x7EFF00)
                    buginfo.set_author(name=config.SERVER_NAME)
                    await bugchan.send(embed=buginfo)
        except mysql.connector.Error as err:
            print(Fore.RED + err + 'From MySQL database' + Style.RESET_ALL)
            if config.USEDEBUGCHAN == True:
                bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description="{} From MySQL database".format(err), color=0xFF001E)
                bugerror.set_author(name=config.SERVER_NAME)
                await bugchan.send(embed=bugerror)

    async def get_cursor(self):
        try:
            mydb.ping(reconnect=True, attempts=3, delay=5)
        except NameError as er:
               print(Fore.RED, er, "Reconnecting MySQL database" + Style.RESET_ALL)
               if config.USEDEBUGCHAN == True:
                  bugchan = self.bot.get_channel(config.BUGCHANNEL_ID)
                  bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description= "{} Reconnection MySQL database".format(er), color=0xFF001E)
                  bugerror.set_author(name=config.SERVER_NAME)
                  await bugchan.send(embed=bugerror)
               await self.mydbconnect()
        except mysql.connector.Error as err:
            await self.mydbconnect()
            print(Fore.RED + "Connection to MySQL database went away... Reconnecting " + Style.RESET_ALL)
            if config.USEDEBUGCHAN == True:
                bugchan = self.bot.get_channel(config.BUGCHANNEL_ID)
                bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description="Connection to MySQL database went away... Reconnecting", color=0xFF001E)
                bugerror.set_author(name=config.SERVER_NAME)
                await bugchan.send(embed=bugerror)
        return mydb.cursor()

    async def botmydb(self):
        mydb.commit()

    async def get_mydb(self):
        try:
            mydb.ping(reconnect=True, attempts=3, delay=5)
        except NameError as er:
               print(Fore.RED, er, "Reconnecting MySQL database" + Style.RESET_ALL)
               if config.USEDEBUGCHAN == True:
                  bugchan = self.bot.get_channel(config.BUGCHANNEL_ID)
                  bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description= "{} Reconnection MySQL database".format(er), color=0xFF001E)
                  bugerror.set_author(name=config.SERVER_NAME)
                  await bugchan.send(embed=bugerror)
               await self.mydbconnect()
        except mysql.connector.Error as err:
            await self.mydbconnect()
            print(Fore.RED + "Connection to MySQL database went away... Reconnecting " + Style.RESET_ALL)
            if config.USEDEBUGCHAN == True:
                bugchan = self.bot.get_channel(config.BUGCHANNEL_ID)
                bugerror = discord.Embed(title=":sos: **ERROR** :sos:", description="Connection to MySQL database went away... Reconnecting", color=0xFF001E)
                bugerror.set_author(name=config.SERVER_NAME)
                await bugchan.send(embed=bugerror)
        return mydb

def setup(bot):
    bot.add_cog(BotSQL(bot))
