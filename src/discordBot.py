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
from requireHeaders import PREFIX_PATH
import spotifyConnection as spot
import playlist, song
import dj
from globalSingleton import *
from station import Station

#Path to store dj files
DJ_PATH = PREFIX_PATH+"/../audioCache/dj"

def parseCmdPrint(cmdChar,cmd):
	build = cmdChar+" ".join([("["+cp[1:]+"]" if (cp[0]=="?" and not "|" in cp) else cp) for cp in cmd])
	for arg in cmd:
		if("|" in arg):
			optional = (arg[0] == "?")
			parts = arg.replace("?","").split("|")
			buildParts = build.split(arg)

			build = ""
			for p in parts:
				build += buildParts[0] + ("["+p+"]" if optional else p) + buildParts[1]+"\n\t"
			break

	if(build[-2:] == "\n\t"):
		build = build[:-2]
	return build


class DiscordClient(discord.Client):
	playlist = None
	commandChar = "$"
	VC = None
	currentSong = None
	mode = 1
	voice = None
	verbose = False
	defaultChannelName = "radio"
	defaultChannel = None

	async def cmdQueue(self,message=None,cmd=None,failed=False):
		if not self.playlist or not self.currentSong:
			await message.channel.send("Error! Playlist is empty")
		else:
			await message.channel.send(self.generateQueueText(self.currentSong,self.playlist.songs))

	async def cmdHelp(self,message=None,cmd=None,failed=False):
		await message.channel.send("```Avalable commands:\n\t"+'\n\t'.join([parseCmdPrint(cmd[0][0],c[0]) for c in self.validCommands])+"```")

	async def cmdPlay(self,message=None,cmd=None,failed=False,usage=None):

		await message.add_reaction("\U0001F4FB")

		reqStation = None
		if(len(args) > 1):
			for s in stations:
				if(args[1] == s.waveLength):
					reqStation = s
		if(reqStation):
			self.playlist = reqStation
			self.voice = self.playlist.host

		else:
			try:
				self.playlist = playlist.Playlist(spotifyConInstance.loadPlaylist(args[1]))

			except Exception as e:
				await message.channel.send("Invalid Playlist!")
				self.console(e)
				return

		await message.add_reaction("\U0001F44C")


		random.shuffle(self.playlist.songs)
		dj.writeDJAudio(DJ_PATH,voice=self.voice,text=dj.getWelcomeText(self.playlist),verbose=self.verbose)

		self.playlist.prepareNextSongs(3,override=True,verbose=self.verbose)

		self.console("Connecting to voice channel "+message.author.voice.channel.name)
		#connect to the voice channel that the person who wrote the message is in
		if self.VC and (not self.VC == message.author.voice.channel):
			await self.VC.disconnect()
		self.VC = await message.author.voice.channel.connect()

		await self.playNextSong(None)

	def __init__(self):
		super(DiscordClient, self).__init__()
		self.validCommands = [
			[["help"],self.cmdHelp],
			[["play","?playlist|station wavelength"],self.cmdPlay],
			[["queue"],self.cmdQueue],
			[["station","create","?wavelength"],self.cmdHelp],
			[["station","add","?wavelength","?playlist|song|station"],self.cmdHelp],
			[["station","name","?wavelength","?name"],self.cmdHelp],
			[["station","voice","?wavelength","?voice"],self.cmdHelp],
			[["station","list"],self.cmdHelp],
			[["voice","?voice"],self.cmdHelp],
			[["voice","list"],self.cmdHelp]
		]

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
			self.playlist.songs.append(self.currentSong)

			await self.change_presence(activity=discord.Game(name=self.currentSong.artists[0] + " - " + self.currentSong.name))
			songURL = self.currentSong.getAudioFilename()

			self.VC.play(await self.getSongSource(songURL), after=self.triggerNextSong)
			self.playlist.prepareNextSongs(3,verbose=self.verbose)

			dj.writeDJAudio(DJ_PATH,voice=self.voice,pastSong=self.currentSong,playlist=self.playlist,verbose=self.verbose)




	async def on_ready(self):
		spotifyConInstance.verbose = self.verbose
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

		for validCmd in self.validCommands:
			if(cmd == validCmd[0][0]):
				if(len(args) != len(validCmd[0])):
					await message.channel.send("```Usage:\n\t"+parseCmdPrint(args[0][0],validCmd[0])+"```")
				else:
					await validCmd[1](message=message,cmd=args)

		if cmd == "queue" or cmd == "q":
			if not self.playlist or not self.currentSong:
				await message.channel.send("Error! Playlist is empty")
			else:
				await message.channel.send(self.generateQueueText(self.currentSong,self.playlist.songs))

		elif cmd == "play" or cmd =="p":
			await message.add_reaction("\U0001F4FB")

			reqStation = None
			if(len(args) > 1):
				for s in stations:
					if(args[1] == s.waveLength):
						reqStation = s
			if(reqStation):
				self.playlist = reqStation
				self.voice = self.playlist.host

			else:
				try:
					self.playlist = playlist.Playlist(spotifyConInstance.loadPlaylist(args[1]))

				except Exception as e:
					await message.channel.send("Invalid Playlist!")
					self.console(e)
					return

			await message.add_reaction("\U0001F44C")


			random.shuffle(self.playlist.songs)
			dj.writeDJAudio(DJ_PATH,voice=self.voice,text=dj.getWelcomeText(self.playlist),verbose=self.verbose)

			self.playlist.prepareNextSongs(3,override=True,verbose=self.verbose)

			self.console("Connecting to voice channel "+message.author.voice.channel.name)
			#connect to the voice channel that the person who wrote the message is in
			if self.VC and (not self.VC == message.author.voice.channel):
				await self.VC.disconnect()
			self.VC = await message.author.voice.channel.connect()

			await self.playNextSong(None)
		elif cmd == "station":
			if(len(args) > 1):
				if(args[1] == "create"):
					if(len(args) > 2):
						duplicate = False
						for s in stations:
							duplicate = duplicate or (args[2] == s.waveLength)
						if(duplicate):
							await message.channel.send("Wavelength "+args[2]+" already exists!")
						else:
							s = Station(waveLength=args[2],verbose=self.verbose,owner=message.author.nick)
							stations.append(s)
							await message.channel.send("Created station "+s.waveLength)
					else:
						await message.channel.send("Please provide a station wavelength ex. '94.5'")
				elif(args[1] == "add"):
					if(len(args) > 3):
						for s in stations:
							if(s.waveLength == args[2]):
								try:
									addedPlaylist = playlist.Playlist(spotifyConInstance.loadPlaylist(args[3]))
								except Exception as e:
									await message.channel.send("Invalid Playlist!")
									self.console(e)
									return
								else:
									numAdded = s.addPlaylist(addedPlaylist,verbose=self.verbose)
									s.saveToFile(verbose=self.verbose)
									await message.channel.send("Added "+str(numAdded)+" songs to "+s.waveLength)
									return
						await message.channel.send("Could not find station "+args[2])
					else:
						await message.channel.send("Invalid form. Please use:\n"+self.commandChar+"station add [wavelength] [playlist]\nin order to add spotify songs to a station")
				elif(args[1] == "name"):
					if(len(args) > 3):
						for s in stations:
							if(s.waveLength == args[2]):
								s.name = " ".join(args[3:])
								s.saveToFile(verbose=self.verbose)
								await message.channel.send("Named station "+args[2]+" "+" ".join(args[3:]))
								return
						await message.channel.send("Could not find station "+args[2])
					else:
						await message.channel.send("Invalid form. Please use:\n"+self.commandChar+"station name [wavelength] [name]\nin order to name a station")
				elif(args[1] == "owner"):
					if(len(args) > 2):
						for s in stations:
							if(s.waveLength == args[2]):
								s.owner = message.author.nick
								await message.channel.send("Set station "+args[2]+" owner to "+message.author.nick)
								s.saveToFile(verbose=self.verbose)
								return
						await message.channel.send("Could not find station "+args[2])
					else:
						await message.channel.send("Invalid form. Please use:\n"+self.commandChar+"station owner [wavelength]\nin order to take ownership of a station")
				elif(args[1] == "list"):
					await message.channel.send("```Available stations:"+'\n'.join([s.waveLength+" | "+s.name for s in stations])+"```")
				elif(args[1] == "voice" or args[1] == "host"):
					if len(args) > 3 and args[3] in googleRadioVoices:
						for s in stations:
							if(s.waveLength == args[2]):
								s.host = args[3]
								s.saveToFile(verbose=self.verbose)
								await message.channel.send("Station "+args[2]+" host voice set to "+self.voice)
								return
						await message.channel.send("Could not find station "+args[2])
					else:
						if(len(args) > 1):
							await message.channel.send("Invalid voice "+args[1])
						await message.channel.send("```Available voices: "+"\n"+'\n'.join([v for v in googleRadioVoices])+"```")
			else:
				await message.channel.send('''```Station Commands:
				$station create [wavelength]
				$station add [wavelength] [playlist]
				$station name [wavelength] [name]
				$station voice [wavelength] [voice]
				$station owner [wavelength]
				$station list```''')

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
				await message.channel.send("Please type a song name after "+self.commandChar+"request")
			else:
				try:
					songReq = " ".join(args[1:])
					self.console("Requesting "+songReq)
					await message.add_reaction("\U0000260E")
					await message.add_reaction("\U0001F44C")

					req = song.Song(spotifyConInstance.getSong(songReq))
					self.console("Found"+req.name)
					await message.channel.send("Found song: "+req.name)

					self.playlist.insertSong(req,message,self.voice,DJ_PATH,verbose=self.verbose)
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
			$play [station wavelength]
			$queue
			$station create [wavelength]
			$station add [wavelength] [playlist]
			$station name [wavelength] [name]
			$station voice [wavelength] [voice]
			$station owner [wavelength]
			$station list
			$voice
			$voice [voice]```''')
		else:
			await message.channel.send("Unknown command "+cmd)


		self.console('Message from {0.author}: {0.content}'.format(message))
