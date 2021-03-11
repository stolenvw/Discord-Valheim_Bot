# Discord-Valheim_Bot
Valheim discord bot based off of ckbaudio / valheim-discord-bot (https://github.com/ckbaudio/valheim-discord-bot)

## MYSQL Tabel INFO
```
CREATE TABLE `players` (
  `id` int NOT NULL,
  `user` varchar(100) NOT NULL,
  `deaths` int NOT NULL DEFAULT '0',
  `valid` varchar(50) DEFAULT NULL,
  `startdate` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `playtime` bigint DEFAULT '0',
  `jointime` bigint DEFAULT NULL,
  `ingame` int NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


ALTER TABLE `players`
  ADD PRIMARY KEY (`id`) USING BTREE,
  ADD UNIQUE KEY `users` (`user`);


ALTER TABLE `players`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;
```
