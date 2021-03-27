# Discord-Valheim_Bot
Valheim discord bot based off of ckbaudio / valheim-discord-bot (https://github.com/ckbaudio/valheim-discord-bot)

## MYSQL Tabel INFO
```
CREATE TABLE `players` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user` varchar(100) NOT NULL,
  `deaths` int NOT NULL DEFAULT '0',
  `valid` varchar(50) DEFAULT NULL,
  `startdate` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `playtime` bigint DEFAULT '0',
  `jointime` bigint DEFAULT NULL,
  `ingame` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `users` (`user`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```
```
CREATE TABLE `serverstats` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date` varchar(20) DEFAULT NULL,
  `timestamp` bigint DEFAULT NULL,
  `users` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `timestamp` (`timestamp`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```
```
CREATE TABLE `events` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` text NOT NULL,
  `smessage` text NOT NULL,
  `image` text NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `type` (`type`(5))
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `events` VALUES (1,'Skeletons','Skeleton Surprise','skeleton.png'),(2,'Blobs','..','Ooze.png'),(3,'Foresttrolls','The ground is shaking','troll.png'),(4,'Wolves','You are being hunted','wolf.png'),(5,'Surtlings','There\'s a smell of sulfur in the air','surtling.png');
```
## Optional Table for Extra Server Info
```
CREATE TABLE `exstats` (
  `id` int NOT NULL AUTO_INCREMENT,
  `savezdos` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `savesec` varchar(10) DEFAULT NULL,
  `serverversion` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `gameday` int DEFAULT NULL,
  `timestamp` bigint DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `exstats` VALUES (1,'NULL',NULL,'NULL',NULL,1616448381);
```
