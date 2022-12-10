import config
import mysql.connector
from colorama import Fore, Style
from mysql.connector import errorcode
from config import SQL_HOST as MYhost
from config import SQL_PORT as MYport
from config import SQL_USER as MYuser
from config import SQL_PASS as MYpass
from config import SQL_DATABASE as MYbase

TABLES = {}
TABLES['events'] = (
    "CREATE TABLE `events` ("
    "  `id` int NOT NULL AUTO_INCREMENT,"
    " `type` text NOT NULL,"
    " `smessage` text NOT NULL,"
    " `image` text NOT NULL,"
    " PRIMARY KEY (`id`),"
    " UNIQUE KEY `type` (`type`(7)) USING BTREE"
    ") ENGINE=InnoDB")

if config.EXSERVERINFO:
    TABLES['exstats'] = (
        "CREATE TABLE `exstats` ("
        "  `id` int NOT NULL AUTO_INCREMENT,"
        "  `savezdos` varchar(50) DEFAULT NULL,"
        "  `savesec` varchar(10) DEFAULT NULL,"
        "  `worldsize` varchar(10) DEFAULT NULL,"
        "  `serverversion` varchar(10) DEFAULT NULL,"
        "  `gameday` int DEFAULT NULL,"
        "  `timestamp` bigint DEFAULT NULL,"
        "  PRIMARY KEY (`id`)"
        ") ENGINE=InnoDB")


if config.PLOCINFO:
    TABLES['plocinfo'] = (
        "CREATE TABLE `plocinfo` ("
        "  `id` int NOT NULL AUTO_INCREMENT,"
        "  `locations` varchar(10) DEFAULT NULL,"
        "  `zone` varchar(10) DEFAULT NULL,"
        "  `duration` varchar(10) DEFAULT NULL,"
        "  PRIMARY KEY (`id`)"
        ") ENGINE=InnoDB")

TABLES['players'] = (
    "CREATE TABLE `players` ("
    "  `id` int NOT NULL AUTO_INCREMENT,"
    "  `user` varchar(100) NOT NULL,"
    "  `deaths` int NOT NULL DEFAULT '0',"
    "  `valid` varchar(50) DEFAULT NULL,"
    "  `startdate` varchar(20) DEFAULT NULL,"
    "  `playtime` bigint DEFAULT '0',"
    "  `jointime` bigint DEFAULT NULL,"
    "  `ingame` int NOT NULL DEFAULT '0',"
    "  PRIMARY KEY (`id`) USING BTREE,"
    "  UNIQUE KEY `users` (`user`)"
    ") ENGINE=InnoDB")

TABLES['serverstats'] = (
    "CREATE TABLE `serverstats` ("
    "  `id` int NOT NULL AUTO_INCREMENT,"
    "  `date` varchar(20) DEFAULT NULL,"
    "  `timestamp` bigint DEFAULT NULL,"
    "  `users` int NOT NULL DEFAULT '0',"
    "  `jocode` int DEFAULT NULL,"
    "  PRIMARY KEY (`id`) USING BTREE,"
    "  UNIQUE KEY `timestamp` (`timestamp`)"
    ") ENGINE=InnoDB")

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

def maketable():
    mycursor = mydb.cursor()
    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print(Fore.GREEN + "Creating table {}: ".format(table_name), end='')
            mycursor.execute(table_description)
            if table_name == "events":
                eventinsert()
            if table_name == "exstats":
                exstatinsert()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print(Fore.RED + "already exists." + Style.RESET_ALL)
            else:
                print(Fore.RED + err.msg + Style.RESET_ALL)
        else:
            print(Fore.GREEN + "OK" + Style.RESET_ALL)
    mycursor.close()
    print(Fore.GREEN + "Done" + Style.RESET_ALL)

def eventinsert():
    print(Fore.GREEN + "Adding events info to table events" + Style.RESET_ALL)
    mycursor1 = mydb.cursor()
    sql = """INSERT INTO `events` (`id`, `type`, `smessage`, `image`) VALUES (%s, %s, %s, %s)"""
    val = [
        (1, 'Skeletons', 'Skeleton Surprise', 'skeleton.png'),
        (2, 'Blobs', 'A foul smell from the swamp', 'Ooze.png'),
        (3, 'Foresttrolls', 'The ground is shaking', 'troll.png'),
        (4, 'Wolves', 'You are being hunted', 'wolf.png'),
        (5, 'Surtlings', 'There\'s a smell of sulfur in the air', 'surtling.png'),
        (6, 'Eikthyrnir', 'Meadows', 'Eikthyr.png'),
        (7, 'GDKing', 'Black Forest', 'The_Elder.png'),
        (8, 'Bonemass', 'Swamp', 'Bonemass.png'),
        (9, 'Dragonqueen', 'Mountain', 'Moder.png'),
        (10, 'GoblinKing', 'Plains', 'Yagluth.png'),
        (11, 'army_eikthyr', 'Eikthyr rallies the creatures of the forest', 'Boar.png'),
        (12, 'army_theelder', 'The forest is moving...', 'Greydwarf.png'),
        (13, 'army_bonemass', 'A foul smell from the swamp', 'Draugr.png'),
        (14, 'army_moder', 'A cold wind blows from the mountains', 'Drake.png'),
        (15, 'army_goblin', 'The horde is attacking', 'Fuling.png'),
        (16, 'Bats', 'You stirred the cauldron', 'Bat.png'),
        (17, 'army_seekers', 'They Sought You Out', 'seekers.png'),
        (18, 'Gjall', 'What\'s up gjall?', 'gjall.png')
    ]
    mycursor1.executemany(sql, val)
    mydb.commit()
    mycursor1.close()

def exstatinsert():
    mycursor2 = mydb.cursor()
    print(Fore.GREEN + "Adding 1st row to table exstats" + Style.RESET_ALL)
    sql = """INSERT INTO `exstats` VALUES (1,'NULL','NULL','NULL',NULL,NULL,1616448381)"""
    mycursor2.execute(sql)
    mydb.commit()
    mycursor2.close()


maketable()
mydb.close()
exit()
