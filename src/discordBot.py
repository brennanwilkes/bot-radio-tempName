import discord
from discord.ext import commands
from discord.utils import get
import requests
import shutil
import os, sys, random
import glob
import json
import asyncio
import re
from googleCloud import googleRadioVoices, googlePrimaryVoices

#Custom imports
from requireHeaders import PREFIX_PATH, requireFile
import spotifyConnection as spot
import playlist
import dj

#Path to store dj files
DJ_PATH = PREFIX_PATH+"/../audioCache/dj"

#Discord client object
class DiscordClient(discord.Client):
	spotC = None
	playlist = None
	commandChar = "$"
	VC = None
	currentSong = None
	mode = 1
	voice = None
	verbose = False
	defaultChannelName = "radio"
	defaultChannel = None


	'''
	#not implemented yet
	async def leave(self):
		await self.voice_client.disconnect()
	'''

	def console(self,data):
		if(self.verbose):
			print(data)

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
		output += " 1. "+ currentSong.artists[0] + " - " + currentSong.name + " "*(LINE_LENGTH-len(currentSong.artists[0] + " - " + currentSong.name)) + self.format_time_string(currentSong.duration) + "\n"
		output += "Up next:\n"

		for song in playlistSongs:
			i+=1
			sn = song.artists[0] + " - " + song.name
			if len(sn) > LINE_LENGTH: #truncate song name if it exceeds the line length
				sn = sn[0:LINE_LENGTH-3]+ "..."
			output += "{a:2d}. ".format(a=i) + sn + " "*(LINE_LENGTH-len(sn)) + self.format_time_string(song.duration) + "\n"

		if len(output)> 2000: #max discord msg length
			output = output[0:1990]+ "\n ... \n"
		output += "```"
		return output


	def triggerNextSong(self,error):
		asyncio.run(self.playNextSong(error))

	async def playNextSong(self,error):

		if(len(self.playlist.songs)==0):
			self.console("Empty playlist")
			return

		self.mode = 1 - self.mode
		if(self.mode == 0):
			self.VC.play(await self.getSongSource(glob.glob(DJ_PATH+".*")[0]), after=self.triggerNextSong)
		else:
			self.currentSong = self.playlist.songs.pop(0)
			songGlobs = glob.glob(PREFIX_PATH+"/../audioCache/"+self.currentSong.youtubeID+".*")
			if(len(songGlobs) < 1):
				self.currentSong.downloadAudio(verbose=self.verbose, override=True)
				songGlobs = glob.glob(PREFIX_PATH+"/../audioCache/"+self.currentSong.youtubeID+".*")

			await self.change_presence(activity=discord.Game(name=self.currentSong.artists[0] + " - " + self.currentSong.name))
			songURL = songGlobs[0]

			self.VC.play(await self.getSongSource(songURL), after=self.triggerNextSong)
			self.playlist.downloadNextSongs(3,verbose=self.verbose)
			self.playlist.updateNextSongsGenres(3,verbose=self.verbose,sp=self.spotC)

			dj.writeDJAudio(DJ_PATH,voice=self.voice,pastSong=self.currentSong,playlist=self.playlist,verbose=self.verbose)




	async def on_ready(self):
		self.spotC = spot.SpotifyConnection(verbose=self.verbose)
		#self.voice = random.choice(googlePrimaryVoices)
		self.voice = "en-AU-Wavenet-B"
		self.console('Logged on as {0}!'.format(self.user))
		self.console('Voice {0} selected'.format(self.voice))

		for guild in self.guilds:
			for channel in guild.text_channels:
				if(channel.name == self.defaultChannelName):
					self.defaultChannel = channel
					self.console("Found default text channel "+channel.name)
		if(self.defaultChannel):
			await self.defaultChannel.send("Bot ready to rock and roll")



		await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="your every move"))


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
		cmd = args[0][1:]

		if cmd == "queue":
			if not self.playlist or not self.currentSong:
				await message.channel.send("Error! Playlist is empty")
			else:
				await message.channel.send(self.generateQueueText(self.currentSong,self.playlist.songs))

		elif cmd == "play":
			await message.add_reaction("\U0001F4FB")
			try:
				self.playlist = playlist.Playlist(self.spotC.loadPlaylist(args[1]))
			except Exception as e:
				await message.channel.send("Invalid Playlist!")
				self.console(e)
			else:
				await message.add_reaction("\U0001F44C")

				random.shuffle(self.playlist.songs)
				dj.writeDJAudio(DJ_PATH,voice=self.voice,text=dj.getWelcomeText(self.playlist),verbose=self.verbose)
				self.playlist.downloadNextSongs(1,override=True,verbose=self.verbose)

				#connect to the voice channel that the person who wrote the message is in
				if self.VC and (not self.VC == message.author.voice.channel):
					await self.VC.disconnect()
				self.VC = await message.author.voice.channel.connect()

				await self.playNextSong(None)

		elif cmd == "voice":
			if len(args) > 1 and args[1] in googleRadioVoices:
				self.voice = args[1]
				await message.channel.send("Voice set to "+self.voice)
			else:
				if(len(args) > 1):
					await message.channel.send("Invalid voice "+args[1])
				await message.channel.send("```Available voices: "+"\n"+'\n'.join([v for v in googleRadioVoices])+"```")

		elif cmd == "request":
			if(len(args)<2):
				await message.channel.send("Please type a song name after $request")
			else:
				try:
					songReq = " ".join(args[1:])
					self.console("Requesting "+songReq)
					await message.add_reaction("\U0000260E")
					await message.add_reaction("\U0001F44C")

					req = playlist.Song(self.spotC.getSong(songReq))
					self.console("Found"+req.name)
					await message.channel.send("Found song: "+req.name)

					self.playlist.insertSong(req,self.spotC,message,self.voice,DJ_PATH,verbose=self.verbose)
				except Exception as e:
					await message.channel.send("Invalid Request")
					self.console("Error "+str(e))
				else:
					await message.channel.send("\U0000260E"+" "+req.name+" coming up next "+"\U0000260E")

		elif cmd == "die":
			if(self.VC):
				await self.VC.disconnect()
			await self.change_presence(activity=None)
			await message.channel.send("Thank you for playing wing commander!")
			await self.logout()

		elif cmd == "help":
			await message.channel.send('''```Commands:
			$help
			$play [playlist]
			$queue
			$voice
			$voice [voice]```''')

		self.console('Message from {0.author}: {0.content}'.format(message))
