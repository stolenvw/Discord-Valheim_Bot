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
