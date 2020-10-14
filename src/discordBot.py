import discord
from discord.ext import commands
import requests
import shutil
import os, sys, random
import glob
import json
import asyncio


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
	spotC = None
	playlist = None
	commandChar = "$"
	VC = None
	currentSong = None

	'''
	#not implemented yet
	async def leave(self):
		await self.voice_client.disconnect()
	'''

	def triggerNextSong(self,error):
		asyncLoop = asyncio.run(self.playNextSong(error))

	async def playNextSong(self,error):

		if(len(self.playlist.songs)==0):
			print("Empty playlist")
			return

		self.currentSong = self.playlist.songs.pop(0)
		songURL = glob.glob(PREFIX_PATH+"/../audioCache/"+self.currentSong.youtubeID+".*")[0]

		self.VC.play(await self.getSongSource(songURL), after=self.triggerNextSong)
		self.playlist.downloadNextSongs(3)


	async def on_ready(self):
		self.spotC = spot.spotifyConnection()
		print('Logged on as {0}!'.format(self.user))

	async def getSongSource(self,fn):
		if os.name == 'nt': #windows
			source = await discord.FFmpegOpusAudio.from_probe(executable="C:/Program Files/ffmpeg/bin/ffmpeg.exe", source = fn, method='fallback')
		else:
			source = await discord.FFmpegOpusAudio.from_probe(executable="ffmpeg", source = fn, method='fallback')
		return source

	async def on_message(self, message):

		secret_passphrase = "wah"
		if message.content == secret_passphrase:# and message.author.id == 224020595103236096:
			await message.channel.send("no u")

		if (not len(message.content)) or (not message.content[0] == self.commandChar):
			return

		args = message.content.split(" ")

		if args[0] == self.commandChar+"queue":
			if not self.playlist:
				await message.channel.send("Error! Playlist is empty")
			else:
				await message.channel.send('\n'.join([s.name for s in self.playlist.songs]))
		elif args[0] == self.commandChar+"play":

			try:
				self.playlist = playlist.playlist(self.spotC.loadPlaylist(args[1]))
			except Exception as e:
				await message.channel.send("Invalid Playlist! AGHHHHH")
				print(e)
			else:
				random.shuffle(self.playlist.songs)
				self.playlist.downloadNextSongs(1,override=True)

				#connect to the voice channel that the person who wrote the message is in
				self.VC = await message.author.voice.channel.connect()
				await self.playNextSong(None)
			'''
			#From music bot discord.py example - might need this in the future
			if ctx.voice_client is not None:
				return await ctx.voice_client.move_to(channel)
			'''

		print('Message from {0.author}: {0.content}'.format(message))
