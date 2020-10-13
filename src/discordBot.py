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
    spotC = ""
    playlist = ""
    commandChar = "."

    def makePlaylist(self, url):
        self.spotC = spot.spotifyConnection()
        self.playlist = playlist.playlist(self.spotC.loadPlaylist(url))

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if not message.content[0] == self.commandChar:
            return
        
        args = message.content.split(" ")

        if args[0] == ".queue":
            if not playlist:
                await message.channel.send("Error! Playlist is empty")
            else:
                await message.channel.send('\n'.join([s.name for s in self.playlist.songs]))
        elif args[0] == ".play":
            self.makePlaylist(args[1])
        
            #self.joinVC

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