import discord  # For obvious reasons
import asyncio  # Needed for discord
import os
import sys
from PIL import Image
from PIL import ImageFilter
import urllib3.request
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import re

#===============USER SET VARIABLES===============#
# This is the client ID of the bot account
clientID = 'NDczOTEzNjQ4NDgyMzUzMTgy.DkI2Hg.A0l4b0hRu0vIwNfkxfPtt35wWW4'
# This is the default command prefix
#defaultCommandPrefix = 'bert!'
#================================================#
client = discord.Client()

#===============Classes===============#


class CommUsage(Exception):
    def __init__(self, arg):
        self.sterror = arg
        self.args = {arg}

#===============FUNCTIONS===============#


def getBetween(string, left, right):
    try:
        return re.search(left+'(.*)'+right, string).group(0)
    except Exception:
        return None

def saveImage(attachment):
    """IMAGE DATA FORMAT:
    {'width': 862, 'url': '<link>', 'size': 42343, 'proxy_url': '<link>', 'id': '450160757296857122', 'height': 862, 'filename': 'octahedron.jpg'}"""
    #print('Grabbing image: \nName: ' + attachment['filename'] + '\nURL: ' + attachment['url'])
    connection_pool = urllib3.PoolManager()
    resp = connection_pool.request('GET',attachment['url'])
    f = open('./' + attachment['filename'], 'wb')
    f.write(resp.data)
    #print('File: ' + os.path.realpath(f.name))
    f.close()
    resp.release_conn()
    return os.path.realpath(f.name)

#===============DISCORD CODE===============#
# When we start up


@client.event
async def on_ready():
    # Header Info
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    status = 'Mention me for Bertstrips!'
    await client.change_presence(game=discord.Game(name=status))
    print('Status set to: \"' + status + '\"')
    print('Joined Servers:')
    for server in client.servers:
        print('  '+server.name)
    print('------')

# When we receive a message


@client.event
async def on_message(message):
    # Ignore bot-created messages
    if message.author == client.user or client.user not in message.mentions:
        return
    # COMMANDS
    try:
        #Get caption
        caption = getBetween(message.content, '"', '"')
        image=None
        if not caption:
            raise CommUsage(
                '`Sorry, there was no caption in that message.\nPlease include a caption enclosed in quotes ("text")`')

        #Get attachments
        if len(message.attachments) < 1:
                raise CommUsage('`Sorry, there were no attached images in that message.\nPlease attach an image to make into a BertStrip`')
        image=saveImage(message.attachments[0])
        await client.send_message(message.channel, caption)

    except CommUsage as e:
        await client.send_message(message.channel, e.sterror)

    # Start Bot
try:
    client.run(clientID)
except discord.LoginFailure as e:
    print('Please edit this file, and set the \'clientID\' variable to the token of your bot,\nfrom https://discordapp.com/developers/applications/me.\n')

except Exception as e:
    print('I can\'t connect to the Discord servers right now, sorry! :(\nCheck your internet connection, and then https://twitter.com/discordapp for downtimes,\n and then try again later.')
