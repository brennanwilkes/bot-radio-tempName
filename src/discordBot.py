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

    '''
    #not implemented yet
    async def leave(self):
        await self.voice_client.disconnect()
    '''

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if (not len(message.content)) or (not message.content[0] == self.commandChar):
            return
        
        args = message.content.split(" ")

        if args[0] == ".queue":
            if not playlist:
                await message.channel.send("Error! Playlist is empty")
            else:
                await message.channel.send('\n'.join([s.name for s in self.playlist.songs]))
        elif args[0] == ".play":
            self.makePlaylist(args[1])
        
            #connect to the voice channel that the person who wrote the message is in
            VC = await message.author.voice.channel.connect()
            '''
            #From music bot discord.py example - might need this in the future
            if ctx.voice_client is not None:
                return await ctx.voice_client.move_to(channel)
            '''

            song_path = PREFIX_PATH + "/test.webm"

            if os.name == 'nt': #windows
                source = await discord.FFmpegOpusAudio.from_probe(executable="C:/Program Files/ffmpeg/bin/ffmpeg.exe", source = song_path, method='fallback')
            else:
                source = await discord.FFmpegOpusAudio.from_probe(executable="ffmpeg", source = song_path, method='fallback')
            VC.play(source)


        print('Message from {0.author}: {0.content}'.format(message))
        secret_passphrase = "wah"
        if message.content == secret_passphrase:# and message.author.id == 224020595103236096:
            await message.channel.send("no u")