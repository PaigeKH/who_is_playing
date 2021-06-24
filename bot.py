import discord
import requests
import urllib.parse
import time

TOKEN = 'token'
IPADDR = 'addr'
URL = 'https://www.gametracker.com/server_info/' + IPADDR
playerList = [];

client = discord.Client()

@client.event
async def on_message(message):
    wasLastUser = await get_last_message()

    if message.content.startswith('!players'):
        if not wasLastUser:
            sent = await send_message(message, True, 0, 0)
        else:
            sent = wasLastUser
        while True:
            time.sleep(120)
            await send_message(message, False, sent.id, sent.channel.id)

async def get_last_message():
    oldestMessage = None
    for channel in client.get_all_channels():
        fetchMessage = await channel.history(limit = 10).find(lambda m: m.author.id == client.user.id)
        if fetchMessage is None:
            continue

        if oldestMessage is None:
            oldestMessage = fetchMessage
        else:
            if fetchMessage.created_at > oldestMessage.created_at:
                oldestMessage = fetchMessage

    if (oldestMessage is not None):
        return oldestMessage
    else:
        return False

async def send_message(message, shouldWriteNew, messageID, channelID):
    page = requests.get(URL)
    startIndex = str(page.content).index("ONLINE PLAYERS")
    firstCut = str(page.content)[startIndex:]

    canKeepRunning = True
    while (canKeepRunning):
        firstCut = list_players(firstCut)
        if not firstCut:
            canKeepRunning = False

    if len(playerList) == 0:
        msg = "There are currently 0 players online.\n\nThis bot updates every 2 minutes."
        if (shouldWriteNew):
            sent = await message.channel.send(msg)
            return sent

        else:
            originalChannel = client.get_channel(channelID)
            orignalMessage = await originalChannel.fetch_message(messageID)
            await orignalMessage.edit(content=msg)
    else:
        fixedPlayerList = []
        for player in playerList:
            fixedPlayerList.append(urllib.parse.unquote(player))
        playerList.clear()
        msg = "There is currently 1 player online."
        if len(fixedPlayerList) > 1:
            msg = "There are currently"
            msg = msg + " **" + str(len(fixedPlayerList)) + "** players online."

        msg = msg + "\n```"
        while len(fixedPlayerList) > 0:
            msg = msg + "\n" + fixedPlayerList.pop(0)
        msg = msg + "```\nThis bot updates every 2 minutes."
        if (shouldWriteNew):
            sent = await message.channel.send(msg)
            return sent
        else:
            originalChannel = client.get_channel(channelID)
            orignalMessage = await originalChannel.fetch_message(messageID)
            await orignalMessage.edit(content=msg)


def list_players(pageContent):
    if (pageContent.index("TOP 10 PLAYERS") < pageContent.index("href") + 14):
        return False
    secondCut = pageContent[pageContent.index("href") + 14:]
    playerList.append(secondCut[:secondCut.index(IPADDR)])
    return secondCut

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
