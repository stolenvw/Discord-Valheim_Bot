from datetime import datetime
import time, os, re
import csv, asyncio
from valve.source.a2s import ServerQuerier, NoResponseError
import config


async def timenow():
    now = datetime.now()
    gettime = now.strftime("%d/%m/%Y %H:%M:%S")
    return gettime

async def writecsv():
    while True:    
        try:
            with ServerQuerier(config.SERVER_ADDRESS) as server:
                with open('csv/playerstats.csv', 'a', newline='') as f:
                    csvup = csv.writer(f, delimiter=',')  
                    curtime, players = await timenow(), server.info()['player_count']
                    csvup.writerow([curtime, players])
                    print(curtime, players)
        except NoResponseError:
            with open('csv/playerstats.csv', 'a', newline='') as f:
                csvup = csv.writer(f, delimiter=',')  
                curtime, players = await timenow(), '0'
                csvup.writerow([curtime, players])
                print(curtime, 'Cannot connect to server')
        await asyncio.sleep(60)


loop = asyncio.get_event_loop()
loop.create_task(writecsv())
loop.run_forever()
