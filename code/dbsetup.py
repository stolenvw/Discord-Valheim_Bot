import config
import mysql.connector
from colorama import Fore, Style
from mysql.connector import errorcode
from config import SQL_HOST as MYhost
from config import SQL_PORT as MYport
from config import SQL_USER as MYuser
from config import SQL_PASS as MYpass
from config import SQL_DATABASE as MYbase

# Tables
TABLES = {}
TABLES["events"] = (
    "CREATE TABLE `events` ("
    "  `id` int NOT NULL AUTO_INCREMENT,"
    " `type` text NOT NULL,"
    " `smessage` text NOT NULL,"
    " `image` text NOT NULL,"
    " PRIMARY KEY (`id`),"
    " UNIQUE KEY `type` (`type`(7)) USING BTREE"
    ") ENGINE=InnoDB"
)

if config.EXSERVERINFO:
    TABLES["exstats"] = (
        "CREATE TABLE `exstats` ("
        "  `id` int NOT NULL AUTO_INCREMENT,"
        "  `savezdos` varchar(50) DEFAULT NULL,"
        "  `savesec` varchar(10) DEFAULT NULL,"
        "  `worldsize` varchar(10) DEFAULT NULL,"
        "  `timestamp` bigint DEFAULT NULL,"
        "  PRIMARY KEY (`id`)"
        ") ENGINE=InnoDB"
    )


if config.PLOCINFO:
    TABLES["plocinfo"] = (
        "CREATE TABLE `plocinfo` ("
        "  `id` int NOT NULL AUTO_INCREMENT,"
        "  `locations` varchar(10) DEFAULT NULL,"
        "  `zone` varchar(10) DEFAULT NULL,"
        "  `duration` varchar(10) DEFAULT NULL,"
        "  PRIMARY KEY (`id`)"
        ") ENGINE=InnoDB"
    )

TABLES["players"] = (
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
    ") ENGINE=InnoDB"
)

TABLES["serverinfo"] = (
    "CREATE TABLE `serverinfo` ("
    "  `id` int NOT NULL AUTO_INCREMENT,"
    "  `steamtime` int DEFAULT NULL,"
    "  `upnotify` int NOT NULL DEFAULT '0',"
    "  `botversion` varchar(10) DEFAULT NULL,"
    "  `serverversion` varchar(10) DEFAULT NULL,"
    "  `gameday` int DEFAULT NULL,"
    "  `jocode` int DEFAULT NULL,"
    " PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB"
)

# Connect to mysql
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

# List tables in the database
def showtables():
    mycursor = mydb.cursor()
    sql = "SHOW TABLES"
    mycursor.execute(sql)
    Info = mycursor.fetchall()
    mydb.commit()
    mycursor.close()
    outputList = []
    for i in Info:
        for x in i:
            outputList.append(x)
    return outputList


# Add tables to database
def maketable():
    print(
        Fore.GREEN + "Checking for tables and adding missing tables" + Style.RESET_ALL
    )
    mycursor = mydb.cursor()
    outputList = showtables()
    for table_name in TABLES:
        table_description = False
        if table_name not in outputList:
            table_description = TABLES[table_name]
        if table_description:
            try:
                print(Fore.GREEN + "Creating table {}: ".format(table_name), end="")
                mycursor.execute(table_description)
                if table_name == "events":
                    eventinsert()
                if table_name == "serverinfo":
                    serverinfoinsert()
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print(Fore.RED + "already exists." + Style.RESET_ALL)
                else:
                    print(Fore.RED + err.msg + Style.RESET_ALL)
            else:
                print(Fore.GREEN + "OK" + Style.RESET_ALL)
    mycursor.close()
    print(Fore.GREEN + "Done" + Style.RESET_ALL)
    updateserverstats()


# Add data to newly made events table
def eventinsert():
    print(Fore.GREEN + "Adding events info to table events" + Style.RESET_ALL)
    mycursor1 = mydb.cursor()
    sql = """INSERT INTO `events` (`id`, `type`, `smessage`, `image`) VALUES (%s, %s, %s, %s)"""
    val = [
        (1, "Skeletons", "Skeleton Surprise", "skeleton.png"),
        (2, "Blobs", "A foul smell from the swamp", "Ooze.png"),
        (3, "Foresttrolls", "The ground is shaking", "troll.png"),
        (4, "Wolves", "You are being hunted", "wolf.png"),
        (5, "Surtlings", "There's a smell of sulfur in the air", "surtling.png"),
        (6, "Eikthyrnir", "Meadows", "Eikthyr.png"),
        (7, "GDKing", "Black Forest", "The_Elder.png"),
        (8, "Bonemass", "Swamp", "Bonemass.png"),
        (9, "Dragonqueen", "Mountain", "Moder.png"),
        (10, "GoblinKing", "Plains", "Yagluth.png"),
        (11, "army_eikthyr", "Eikthyr rallies the creatures of the forest", "Boar.png"),
        (12, "army_theelder", "The forest is moving...", "Greydwarf.png"),
        (13, "army_bonemass", "A foul smell from the swamp", "Draugr.png"),
        (14, "army_moder", "A cold wind blows from the mountains", "Drake.png"),
        (15, "army_goblin", "The horde is attacking", "Fuling.png"),
        (16, "Bats", "You stirred the cauldron", "Bat.png"),
        (17, "army_seekers", "They Sought You Out", "seekers.png"),
        (18, "Gjall", "What's up gjall?", "gjall.png"),
        (19, "Mistlands_DvergrBossEntrance1", "Mistlands", "thequeen.png"),
    ]
    mycursor1.executemany(sql, val)
    mydb.commit()
    mycursor1.close()


# Add data to newly made serverinfo table
def serverinfoinsert():
    mycursor2 = mydb.cursor()
    print(Fore.GREEN + "Adding 1st row to table serverinfo" + Style.RESET_ALL)
    sql = (
        """INSERT INTO `serverinfo` VALUES (1,NULL,0,'3.0.1','NULL',NULL,NULL)"""
    )
    mycursor2.execute(sql)
    mydb.commit()
    mycursor2.close()


# Drop serverstats table
def updateserverstats():
    print(Fore.GREEN + "Removing serverstats table if it exist" + Style.RESET_ALL)
    outputList = showtables()
    if "serverstats" in outputList:
        mycursor = mydb.cursor()
        sql1 = "DROP TABLE serverstats"
        mycursor.execute(sql1)
        mydb.commit()
        mycursor.close()
        print(Fore.GREEN + "Removed serverstats table" + Style.RESET_ALL)
    else:
        print(Fore.BLUE + "Serverstats table already missing" + Style.RESET_ALL)
    updateevents()


# update events table
def updateevents():
    print(Fore.GREEN + "Updating events info to table events" + Style.RESET_ALL)
    mycursor = mydb.cursor()
    sql = "SELECT type FROM events"
    mycursor.execute(sql)
    Info = mycursor.fetchall()
    val = False
    check = ["Bats" not in x for x in Info]
    if False not in check:
        if not val:
            val = [("Bats", "You stirred the cauldron", "Bat.png")]
    check = ["army_seekers" not in x for x in Info]
    if False not in check:
        if not val:
            val = [("army_seekers", "They Sought You Out", "seekers.png")]
        else:
            val.append(("army_seekers", "They Sought You Out", "seekers.png"))
    check = ["Gjall" not in x for x in Info]
    if False not in check:
        if not val:
            val = [("Gjall", "What's up gjall?", "gjall.png")]
        else:
            val.append(("Gjall", "What's up gjall?", "gjall.png"))
    check = ["Mistlands_DvergrBossEntrance1" not in x for x in Info]
    if False not in check:
        if not val:
            val = [("Mistlands_DvergrBossEntrance1", "Mistlands", "thequeen.png")]
        else:
            val.append(("Mistlands_DvergrBossEntrance1", "Mistlands", "thequeen.png"))
    if val:
        Info = Info[0]
        sql = (
            """INSERT INTO `events` (`type`, `smessage`, `image`) VALUES (%s, %s, %s)"""
        )
        mycursor.executemany(sql, val)
        mydb.commit()
        for event in val:
            print(
                Fore.GREEN + f"{event[0]} event added to the database" + Style.RESET_ALL
            )
    else:
        print(Fore.BLUE + "Events already upto date" + Style.RESET_ALL)
    mycursor.close()
    updatemessage()


# Update blobs event message
def updatemessage():
    print(Fore.GREEN + "Updating message for Blobs event" + Style.RESET_ALL)
    mycursor = mydb.cursor()
    sql = """SELECT id, smessage FROM events WHERE type = 'Blobs' LIMIT 1"""
    mycursor.execute(sql)
    Info = mycursor.fetchall()
    row_count = mycursor.rowcount
    if row_count == 0:
        print(
            Fore.RED + "ERROR: Event Blobs not found in the database" + Style.RESET_ALL
        )
    else:
        Info = Info[0]
        if Info[1] != "A foul smell from the swamp":
            sql = (
                """UPDATE events SET smessage = 'A foul smell from the swamp' WHERE id = '%s'"""
                % (Info[0])
            )
            print(Fore.GREEN + "Blobs event message updated" + Style.RESET_ALL)
            mycursor.execute(sql)
            mydb.commit()
        else:
            print(Fore.BLUE + "Blobs event message already upto date" + Style.RESET_ALL)
    mycursor.close()
    movedata()


# Move some stored info from exstats table to serverinfo table
def movedata():
    print(
        Fore.GREEN
        + "Moving storage location for server version and gameday"
        + Style.RESET_ALL
    )
    mycursor = mydb.cursor()
    sql = "SELECT serverversion FROM exstats WHERE id = 1"
    sql1 = "SELECT `id`, `gameday` FROM `exstats` WHERE `gameday` IS NOT null ORDER BY `id` DESC LIMIT 1"
    try:
        mycursor.execute(sql)
        Info = mycursor.fetchall()
        row_count = mycursor.rowcount
    except mysql.connector.errors.ProgrammingError:
        row_count = 0
        print(Fore.BLUE + "Server version already moved" + Style.RESET_ALL)
    try:
        mycursor.execute(sql1)
        Info1 = mycursor.fetchall()
        row_count1 = mycursor.rowcount
    except mysql.connector.errors.ProgrammingError:
        row_count1 = 0
        print(Fore.BLUE + "Server gameday already moved" + Style.RESET_ALL)
    if row_count == 1:
        sql = f"UPDATE serverinfo SET serverversion = '{Info[0][0]}' WHERE id = '1'"  # pyright: ignore
        mycursor.execute(sql)
        mydb.commit()
        print(
            Fore.GREEN + "Moved storage location for server version" + Style.RESET_ALL
        )
        sql = """ALTER TABLE `exstats` DROP COLUMN `serverversion`"""
        mycursor.execute(sql)
        mydb.commit()
    if row_count1 == 1:
        sql = f"UPDATE serverinfo SET gameday = '{Info1[0][1]}' WHERE id = '1'"  # pyright: ignore
        mycursor.execute(sql)
        mydb.commit()
        print(
            Fore.GREEN + "Moved storage location for server gameday" + Style.RESET_ALL
        )
        sql = """ALTER TABLE `exstats` DROP COLUMN `gameday`"""
        mycursor.execute(sql)
        mydb.commit()
    print(
        Fore.GREEN
        + "Done Moving storage location for server version and gameday"
        + Style.RESET_ALL
    )
    mycursor.close()


maketable()
mydb.close()
exit()
