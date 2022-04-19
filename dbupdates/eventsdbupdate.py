import os, re, config, sys, mysql.connector
from colorama import Fore, Style, init
from mysql.connector import errorcode
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

def updateblobs():
    print(Fore.GREEN + "Updating message for Blobs event" + Style.RESET_ALL)
    mycursor = mydb.cursor()
    sql = """SELECT id FROM events WHERE type = 'Blobs' LIMIT 1"""
    mycursor.execute(sql)
    Info = mycursor.fetchall()
    row_count = mycursor.rowcount
    if row_count == 0:
       print(Fore.RED + 'ERROR: Event Blobs not found in the database' + Style.RESET_ALL)
    else:
      Info=Info[0]
      sql = """UPDATE events SET smessage = 'A foul smell from the swamp' WHERE id = '%s'""" % (Info[0])
      print(Fore.GREEN + "Blobs event message updated" + Style.RESET_ALL)
      mycursor.execute(sql)
      mydb.commit()
    mycursor.close()
    addbats()

def addbats():
    print(Fore.GREEN + "Adding Bats event info to table events" + Style.RESET_ALL)
    mycursor = mydb.cursor()
    sql = """SELECT id FROM events WHERE id = '15' LIMIT 1"""
    mycursor.execute(sql)
    Info = mycursor.fetchall()
    row_count = mycursor.rowcount
    if row_count == 0:
       print(Fore.RED + 'ERROR: Cant find data in Events table' + Style.RESET_ALL)
    else:
      Info=Info[0]
      sql = """INSERT INTO `events` (`type`, `smessage`, `image`) VALUES ('Bats', 'You stirred the cauldron', 'Bat.png')"""
      print(Fore.GREEN + "Bats event added to the database" + Style.RESET_ALL)
      mycursor.execute(sql)
      mydb.commit()
    mycursor.close()

updateblobs()
mydb.close()
exit()
