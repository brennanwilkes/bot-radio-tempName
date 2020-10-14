import discord
from discord.ext import commands
import requests
import shutil
import os, sys, random
import glob
import json
import asyncio
import re

#may need to fix later
import spotifyConnection as spot
import playlist
import dj
from googleCloud import googleRadioVoices, googlePrimaryVoices

PREFIX_PATH = sys.path[0]
DJ_PATH = PREFIX_PATH+"/../audioCache/dj"

def token():
	TOKEN_FILE = PREFIX_PATH+"/auth/discordToken"

	#Load Discord bot token
	try:
		fname = open(TOKEN_FILE, "r")
		token = fname.read()
	except IOError:
		raise Exception("Please create file "+ TOKEN_FILE)
	else:
		fname.close()
		return token

class MyClient(discord.Client):
	spotC = None
	playlist = None
	commandChar = "$"
	VC = None
	currentSong = None
	mode = 1
	voice = None


	'''
	#not implemented yet
	async def leave(self):
		await self.voice_client.disconnect()
	'''

	def format_time_string(self, duration_ms):
		sec_tot = int(duration_ms/1000)
		mins_tot = sec_tot // 60
		
		secs = sec_tot % 60
		mins = mins_tot % 60
		hrs = mins_tot // 60
		

		if hrs > 0:
			return "{a:2d}:{b:02d}:{c:02d}".format(a=hrs,b=mins,c=secs)
		else:
			return "  {b:2d}:{c:02d}".format(a=hrs,b=mins,c=secs)


	def generateQueueText(self, currentSong, playlistSongs):
		LINE_LENGTH = 50
		i=1
		output = "```Now playing:\n"
		output += " 1. "+ currentSong.name + " "*(LINE_LENGTH-len(currentSong.name)) + self.format_time_string(currentSong.duration) + "\n"
		output += "Up next:\n"

		for song in playlistSongs:
			i+=1
			sn = song.name
			if len(song.name) > LINE_LENGTH: #truncate song name if it exceeds the line length
				sn = song.name[0:LINE_LENGTH-3]+ "..."
			output += "{a:2d}. ".format(a=i) + sn + " "*(LINE_LENGTH-len(sn)) + self.format_time_string(song.duration) + "\n"
		
		output += "```"
		return output


	def triggerNextSong(self,error):
		asyncio.run(self.playNextSong(error))

	async def playNextSong(self,error,firstTime=False):

		if(len(self.playlist.songs)==0):
			print("Empty playlist")
			return

		self.mode = 1 - self.mode
		if(self.mode == 0):
			self.VC.play(await self.getSongSource(glob.glob(DJ_PATH+".*")[0]), after=self.triggerNextSong)
			if(firstTime):
				self.playlist.downloadNextSongs(1,override=True,debug=True)
		else:

			if(self.currentSong != None and self.currentSong.name != self.playlist.songs[0].name):
				oldSong = glob.glob(PREFIX_PATH+"/../audioCache/"+self.currentSong.youtubeID+".*")[0]
				if os.path.exists(oldSong):
					print("cleaning",oldSong)
					os.remove(oldSong)

			self.currentSong = self.playlist.songs.pop(0)
			songURL = glob.glob(PREFIX_PATH+"/../audioCache/"+self.currentSong.youtubeID+".*")[0]

			self.VC.play(await self.getSongSource(songURL), after=self.triggerNextSong)
			self.playlist.downloadNextSongs(3,debug=True)
			self.playlist.updateNextSongsGenres(3,debug=True,sp=self.spotC)

			dj.writeDJAudio(DJ_PATH,voice=self.voice,pastSong=self.currentSong,playlist=self.playlist,debug=True)




	async def on_ready(self):
		self.spotC = spot.spotifyConnection()
		self.voice = random.choice(googlePrimaryVoices)
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
		if re.compile("^.*chi[cm][pk]*en run.*$").match(message.content) and message.author.id == 141762886883213312:
			await message.channel.send("NO CHICKEN RUN CHRIS")

		if (not len(message.content)) or (not message.content[0] == self.commandChar):
			return

		args = message.content.split(" ")

		if args[0] == self.commandChar+"queue":
			if not self.playlist or not self.currentSong:
				await message.channel.send("Error! Playlist is empty")
			else:
				await message.channel.send(self.generateQueueText(self.currentSong,self.playlist.songs))
					
		elif args[0] == self.commandChar+"play":
			try:
				self.playlist = playlist.playlist(self.spotC.loadPlaylist(args[1]))
			except Exception as e:
				await message.channel.send("Invalid Playlist! AGHHHHH")
				print(e)
			else:
				random.shuffle(self.playlist.songs)
				dj.writeDJAudio(DJ_PATH,voice=self.voice,text=dj.getWelcomeText(self.playlist),debug=True)

				#connect to the voice channel that the person who wrote the message is in
				self.VC = await message.author.voice.channel.connect()

				await self.playNextSong(None,firstTime=True)
			'''
			#From music bot discord.py example - might need this in the future
			if ctx.voice_client is not None:
				return await ctx.voice_client.move_to(channel)
			'''
		elif args[0] == self.commandChar+"voice":
			if len(args) > 1 and args[1] in googleRadioVoices:
				self.voice = args[1]
				await message.channel.send("Voice set to "+self.voice)
			else:
				if(len(args) > 1):
					await message.channel.send("Invalid voice "+args[1])
				await message.channel.send("Avaiable voices: "+"\n"+'\n'.join([v for v in googleRadioVoices]))

		elif args[0] == self.commandChar+"die":
			await message.channel.send("Thank you for playing wing commander!")
			sys.exit()
		elif args[0] == self.commandChar+"help":
			await message.channel.send("Commands:\n$help\n$play [playlist]\n$queue\n$voice\n$voice [voice]")

		print('Message from {0.author}: {0.content}'.format(message))
