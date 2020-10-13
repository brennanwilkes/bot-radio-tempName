import discord
from discord.ext import commands
import requests
import shutil
import os, sys

#may need to fix later
import spotifyConnection as spot
import playlist

PREFIX_PATH = sys.path[0]


def token():
    TOKEN_FILE = PREFIX_PATH+"/auth/discordToken"
    fname = open(TOKEN_FILE)
    token = fname.read()
    return token


class MyClient(discord.Client):
    myConn = ""
    playlist = ""


    def makePlaylist(self, url):
        spotC = spot.spotifyConnection()
        self.playlist = playlist.playlist(spotC.loadPlaylist(url))

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))


    async def on_message(self, message):
        if message.content == ".queue":
            await message.channel.send('\n'.join([s.name for s in self.playlist.songs]))
        if message.content[:len(".play")] == ".play":
            self.makePlaylist(message.content.split(" ")[1])
        #git commit -m "feat: added 'play' and 'queue' commands, to load playlist from a URI and display the playlist, respectively"
        print('Message from {0.author}: {0.content}'.format(message))
        secret_passphrase = "wah"
        if message.content == secret_passphrase:# and message.author.id == 224020595103236096:

            await message.channel.send("no u")
            '''
            atts = 0
            embs = 0

            async for msg in message.channel.history(limit=1000):
                atts += len(msg.attachments)
                embs += len(msg.embeds)
                print("Attachments ({}), Embeds({})".format(len(msg.attachments), len(msg.embeds)))
                for embed in msg.embeds:
                    print(embed.url)
                for att in msg.attachments:
                    print(att.url)
                    download_image(att.url,str(message.channel.id),str(msg.id))
            print("Attachments ({}), Embeds({})".format(atts, embs))
            '''