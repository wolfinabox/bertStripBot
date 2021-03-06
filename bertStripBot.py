import discord  # For obvious reasons
import asyncio  # Needed for discord
import os
import sys
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import pyimgur
import re




#================GLOBAL VARIABLES================#
client = discord.Client()
clientID = None
imgurID=None
#Font sourced from https://www.1001fonts.com/crimson-font.html
fontPath='Crimson-Roman.ttf'
helpText='''
`To make a Bertstrip, attach an image to your message,and put what you\'d like the caption to be in quotes.`
`Optional Options:`
`-i (--imgur): Upload image to Imgur (otherwise sent in Discord chat)`
'''
#================================================#

#===============Classes===============#


class CommUsage(Exception):
    def __init__(self, arg):
        self.sterror = arg
        self.args = {arg}

#===============FUNCTIONS===============#

def loadID():
    try:
        file = open('token.txt')
        global clientID
        clientID = file.readline().strip()
        global imgurID
        imgurID=file.readline().strip()
        return True
    except FileNotFoundError:
        return False

def getBetween(string, left, right):
    try:
        return re.search(left+'(?s)(.*?)'+right, string).group(0)[1:-1]
    except Exception as e:
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

def textWrap(text,font,width):
    lines=[]
    words=text.split()
    if font.getsize(' '.join(words))[0]<=width:
        lines.append(' '.join(words))
        return lines
    i=0
    while i<len(words):
        line=''
        while i<len(words) and font.getsize(line+words[i])[0]<=width:
            line+=(words[i]+' ')
            i+=1
        if not line:
            line=words[i]
            i+=1
        lines.append(line)
    return lines

def makeStrip(im,text):
    image=Image.open(im)
    
    width,height=image.size

    #Wrap the text
    #Best looking ratio of image-width to text font is 970/50 (or, 19.4)
    fontSize=width/19.4
    font=ImageFont.truetype(fontPath,int(fontSize))
    lines=textWrap(text,font,width-(width*0.04))
    lineHeight=font.getsize("hg")[1]

    #Create blank whitespace under image
    totalLinesHeight=int(lineHeight*(len(lines))+lineHeight/2)
    tempImage=Image.new(image.mode,(width,height+totalLinesHeight),(255,255,255))
    tempImage.paste(image)
    image=tempImage
    width,height=image.size
    y=(height-totalLinesHeight)+lineHeight/4
    #Draw lines
    draw=ImageDraw.Draw(image)
    for line in lines:
        x=(width/2)-(font.getsize(line)[0]/2)
        draw.text((x,y),line,fill=(0,0,0),font=font)
        y+=lineHeight
    image.save(im)
    
def imgurUpload(im):
    imgur=pyimgur.Imgur(imgurID)
    upl_image=imgur.upload_image(im,title="bertstrip")
    return upl_image.link
    
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
        if not caption and len(message.attachments) < 1:
            raise CommUsage(helpText)

        if not caption:
            raise CommUsage(
                '`Sorry, there was no caption in that message.\nPlease include a caption enclosed in quotes ("text")`')

        #Get attachments
        if len(message.attachments) < 1:
                raise CommUsage('`Sorry, there were no attached images in that message.\nPlease attach an image to make into a BertStrip`')
        image=saveImage(message.attachments[0])

        #Edit image
        makeStrip(image,caption)
        
        #Options
        PATTERN = re.compile(r'''((?:[^ "']|"[^"]*"|'[^']*')+)''')
        strings=PATTERN.split(message.content)[1::2]

        #Send
        await client.send_message(message.channel, "Here's your Bertstrip, <@"+message.author.id+">:")
        if ("-i" in strings or "--imgur" in strings):
            link=imgurUpload(image)
            await client.send_message(message.channel,link)
        else:
            await client.send_file(message.channel,image)
        os.remove(image)

    except CommUsage as e:
        await client.send_message(message.channel, e.sterror)

    # Start Bot
try:
    if not loadID():raise discord.LoginFailure()
    client.run(clientID)
except discord.LoginFailure as e:
    print('Please create a file named "token.txt" next to this file, and place the token of your bot,\nfrom https://discordapp.com/developers/applications/me, inside it.\n')

except Exception as e:
    print('I can\'t connect to the Discord servers right now, sorry! :(\nCheck your internet connection, and then https://twitter.com/discordapp for downtimes,\n and then try again later.'
    +'\n[ERROR: '+str(e)+']\n')
