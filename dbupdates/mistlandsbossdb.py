import mysql.connector
from colorama import Fore, Style
from config import SQL_HOST as MYhost
from config import SQL_PORT as MYport
from config import SQL_USER as MYuser
from config import SQL_PASS as MYpass
from config import SQL_DATABASE as MYbase

def mydbconnect():
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
            print(Fore.GREEN + "Connected to MySQL database... MySQL Server version ", db_Info + Style.RESET_ALL)
    except mysql.connector.Error as err:
        print(Fore.RED + err + 'From MySQL database' + Style.RESET_ALL)

mydbconnect()

def mistboss():
    print(Fore.GREEN + "Adding Mistlands_DvergrBossEntrance1 info to table events" + Style.RESET_ALL)
    mycursor = mydb.cursor()
    sql = """SELECT id FROM events WHERE TYPE = 'Mistlands_DvergrBossEntrance1' LIMIT 1"""
    mycursor.execute(sql)
    Info = mycursor.fetchall()
    row_count = mycursor.rowcount
    if row_count == 0:
        sql = """INSERT INTO `events` (`type`, `smessage`, `image`) VALUES ('Mistlands_DvergrBossEntrance1', 'Mistlands', 'thequeen.png')"""
        print(Fore.GREEN + "Mistlands_DvergrBossEntrance1 added to the database" + Style.RESET_ALL)
        mycursor.execute(sql)
        mydb.commit()
       
    else:
        print(Fore.RED + 'Mistlands_DvergrBossEntrance1 in Events table already' + Style.RESET_ALL)
    mycursor.close()

mistboss()
mydb.close()
exit()
