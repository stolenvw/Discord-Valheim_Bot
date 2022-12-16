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
            print(
                Fore.GREEN + "Connected to MySQL database... MySQL Server version ",
                db_Info + Style.RESET_ALL,
            )
    except mysql.connector.Error as err:
        print(Fore.RED + err + "From MySQL database" + Style.RESET_ALL)


mydbconnect()


def updatedb():
    print(Fore.GREEN + "Updating databases" + Style.RESET_ALL)
    mycursor = mydb.cursor()
    sql = """ALTER TABLE `serverstats` ADD `jocode` INT NULL AFTER `users`;"""
    mycursor.execute(sql)
    mydb.commit()
    print(Fore.GREEN + "Database updated" + Style.RESET_ALL)
    mycursor.close()
    addseekers()

def addseekers():
    print(Fore.GREEN + "Adding Mistland events info to table events" + Style.RESET_ALL)
    mycursor = mydb.cursor()
    sql = """SELECT id FROM events WHERE id = '16' LIMIT 1"""
    mycursor.execute(sql)
    Info = mycursor.fetchall()
    row_count = mycursor.rowcount
    if row_count == 0:
       print(Fore.RED + 'ERROR: Cant find data in Events table' + Style.RESET_ALL)
    else:
        Info=Info[0]
        sql = """INSERT INTO `events` (`id`, `type`, `smessage`, `image`) VALUES (%s, %s, %s, %s)"""
        val = [
            (17, 'army_seekers', 'They Sought You Out', 'seekers.png'),
            (18, 'Gjall', 'What\'s up gjall?', 'gjall.png'),
            (19, 'Mistlands_DvergrBossEntrance1', 'Mistlands', 'thequeen.png')
        ]
        mycursor.executemany(sql, val)
        mydb.commit()
        print(Fore.GREEN + "Mistland events added to the database" + Style.RESET_ALL)
    mycursor.close()

updatedb()
mydb.close()
exit()
