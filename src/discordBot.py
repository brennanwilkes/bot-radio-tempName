import discord
from discord.ext import commands
import requests
import shutil
import os, sys, random
import glob

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
	commandChar = "."

	def makePlaylist(self, url):
		self.playlist = playlist.playlist(self.spotC.loadPlaylist(url))
		random.shuffle(self.playlist.songs)

	'''
	#not implemented yet
	async def leave(self):
		await self.voice_client.disconnect()
	'''

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

			self.playlist.songs[0].downloadAudio(override=True,debug=True)

			#connect to the voice channel that the person who wrote the message is in
			VC = await message.author.voice.channel.connect()
			'''
			#From music bot discord.py example - might need this in the future
			if ctx.voice_client is not None:
				return await ctx.voice_client.move_to(channel)
			'''

			print("Playing",self.playlist.songs[0].name)

			VC.play(await self.getSongSource(glob.glob(PREFIX_PATH+"/../audioCache/"+self.playlist.songs[0].youtubeID+".*")[0]))


		print('Message from {0.author}: {0.content}'.format(message))
		secret_passphrase = "wah"
		if message.content == secret_passphrase:# and message.author.id == 224020595103236096:
			await message.channel.send("no u")
