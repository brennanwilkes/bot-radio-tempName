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
			parts = arg.split("|")
			buildParts = build.split(arg)

			build = ""
			for p in parts:
				build += buildParts[0] + ("["+p[1:]+"]" if (p[0] == "?") else p) + buildParts[1]+"\n\t"
			break

	if(build[-2:] == "\n\t"):
		build = build[:-2]
	return build

def cmdMatches(cmd,desired):
	for p in range(len(desired)):
		if(desired[p][0] != "?" and (cmd[p] if p>0 else cmd[p][1:]) != desired[p] ):
			return False
	return True

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

	async def cmdVoice(self,message=None,cmd=None,failed=False):
		if cmd[1] == "list":
			await message.channel.send("```Available voices: "+"\n"+'\n'.join([v for v in googleRadioVoices])+"```")
		elif cmd[1] in googleRadioVoices:
			self.voice = cmd[1]
			await message.channel.send("Voice set to "+self.voice)
		else:
			await message.channel.send("Invalid voice "+cmd[1])

	async def cmdRequest(self,message=None,cmd=None,failed=False):
		try:
			songReq = " ".join(cmd[1:])
			self.console("Requesting "+songReq)
			await message.add_reaction("\U0000260E")
			await message.add_reaction("\U0001F44C")

			req = song.Song(spotifyConInstance.getSong(songReq))
			self.console("Found "+req.name)
			await message.channel.send("Found song: "+req.name)

			self.playlist.insertSong(req,message,self.voice,DJ_PATH,verbose=self.verbose)
		except Exception as e:
			await message.channel.send("Invalid Request")
			self.console("Error "+str(e))
		else:
			await message.channel.send("\U0000260E"+" "+req.name+" coming up next "+"\U0000260E")

	async def cmdDie(self,message=None,cmd=None,failed=False):
		if(self.VC):
			await self.VC.disconnect()
		await self.change_presence(activity=None)
		await message.channel.send("Thank you for playing wing commander!")
		await self.logout()

	async def cmdPlay(self,message=None,cmd=None,failed=False):
		await message.add_reaction("\U0001F4FB")
		reqStation = None
		for s in stations:
			if(cmd[1] == s.waveLength):
				reqStation = s
		if(reqStation):
			self.playlist = reqStation
			self.voice = self.playlist.host

		else:
			try:
				self.playlist = playlist.Playlist(spotifyConInstance.loadPlaylist(cmd[1]))

			except Exception as e:
				await message.channel.send("Invalid Playlist!")
				self.console(e)
				return

		await message.add_reaction("\U0001F44C")


		random.shuffle(self.playlist.songs)
		#dj.writeDJAudio(DJ_PATH,voice=self.voice,text=dj.getWelcomeText(self.playlist),verbose=self.verbose)


		self.playlist.prepareNextSongs(2,verbose=self.verbose, voice=self.voice,welcome=True)


		while(True):
			try:
				self.console("Connecting to voice channel "+message.author.voice.channel.name)
				#connect to the voice channel that the person who wrote the message is in
				if self.VC and (not self.VC == message.author.voice.channel):
					await self.VC.disconnect()

				self.VC = await message.author.voice.channel.connect()

				await self.playNextSong(None,welcome=True)
			except Exception as e:
				print(e)
			else:
				break

	async def cmdStationCreate(self,message=None,cmd=None,failed=False):
		duplicate = False
		for s in stations:
			duplicate = duplicate or (cmd[2] == s.waveLength)
		if(duplicate):
			await message.channel.send("Wavelength "+cmd[2]+" already exists!")
		else:
			s = Station(waveLength=cmd[2],verbose=self.verbose,owner=message.author.nick)
			stations.append(s)
			await message.channel.send("Created station "+s.waveLength)

	async def cmdStationAdd(self,message=None,cmd=None,failed=False):
		for s in stations:
			if(s.waveLength == cmd[2]):
				try:
					addedPlaylist = playlist.Playlist(spotifyConInstance.loadPlaylist(cmd[3]))
				except Exception as e:
					await message.channel.send("Invalid Playlist!")
					self.console(e)
					return
				else:
					numAdded = s.addPlaylist(addedPlaylist,verbose=self.verbose)
					s.saveToFile(verbose=self.verbose)
					await message.channel.send("Added "+str(numAdded)+" songs to "+s.waveLength)
					return
		await message.channel.send("Could not find station "+cmd[2])

	async def cmdStationName(self,message=None,cmd=None,failed=False):
		for s in stations:
			if(s.waveLength == cmd[2]):
				s.name = " ".join(cmd[3:])
				s.saveToFile(verbose=self.verbose)
				await message.channel.send("Named station "+cmd[2]+" "+" ".join(cmd[3:]))
				return
		await message.channel.send("Could not find station "+cmd[2])

	async def cmdStationOwner(self,message=None,cmd=None,failed=False):
			for s in stations:
				if(s.waveLength == cmd[2]):
					s.owner = message.author.nick
					await message.channel.send("Set station "+cmd[2]+" owner to "+message.author.nick)
					s.saveToFile(verbose=self.verbose)
					return
			await message.channel.send("Could not find station "+cmd[2])

	async def cmdStationList(self,message=None,cmd=None,failed=False):
			await message.channel.send("```Available stations:"+'\n'.join([s.waveLength+" | "+s.name for s in stations])+"```")

	async def cmdStationCache(self,message=None,cmd=None,failed=False):
		for s in stations:
			if(s.waveLength == cmd[2]):
				await message.channel.send("Caching "+str(len(s.songs))+" songs in station "+cmd[2])
				s.preCache(verbose=self.verbose)

				gen = s.calcGenres(verbose=self.verbose)
				sortedGen = sorted(gen.items(), key=lambda x: x[1], reverse=True)

				await message.channel.send("Successfully cached "+str(len(s.songs))+" songs in station "+cmd[2])
				await message.channel.send("Top genres: "+", ".join([s[0] for s in sortedGen[:3]]))

				return
		await message.channel.send("Could not find station "+cmd[2])

	async def cmdStationVoice(self,message=None,cmd=None,failed=False):
			if cmd[3] in googleRadioVoices:
				for s in stations:
					if(s.waveLength == cmd[2]):
						s.host = cmd[3]
						s.saveToFile(verbose=self.verbose)
						await message.channel.send("Station "+cmd[2]+" host voice set to "+self.voice)
						return
				await message.channel.send("Could not find station "+cmd[2])
			else:
				await message.channel.send("Invalid voice "+cmd[1])
				await message.channel.send("```Available voices: "+"\n"+'\n'.join([v for v in googleRadioVoices])+"```")

	def __init__(self):
		super(DiscordClient, self).__init__()
		self.validCommands = [
			[["help"],self.cmdHelp],
			[["play","?playlist|station wavelength"],self.cmdPlay],
			[["queue"],self.cmdQueue],
			[["station","create","?wavelength"],self.cmdStationCreate],
			[["station","add","?wavelength","?playlist|?song|?station"],self.cmdStationAdd],
			[["station","name","?wavelength","?name"],self.cmdStationName],
			[["station","voice","?wavelength","?voice"],self.cmdStationVoice],
			[["station","owner","?wavelength"],self.cmdStationOwner],
			[["station","cache","?wavelength"],self.cmdStationCache],
			[["station","list"],self.cmdStationList],
			[["voice","?voice|list"],self.cmdVoice],
			[["request","?song"],self.cmdRequest],
			[["die"],self.cmdDie],
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

	async def playNextSong(self,error,welcome=False):

		if(len(self.playlist.songs)==0):
			self.console("Empty playlist")
			return

		self.mode = 1 - self.mode
		if(self.mode == 0):
			djFn = self.playlist.songs[0].fileName+"-welcome-dj" if welcome else self.currentSong.fileName+"-dj-"+self.playlist.getNextSong(remove=False).youtubeID
			self.console("Playing DJ track "+djFn)
			self.VC.play(await self.getSongSource(glob.glob(djFn+".*")[0]), after=self.triggerNextSong)
		else:

			self.currentSong = self.playlist.getNextSong()

			await self.change_presence(activity=discord.Game(name=self.currentSong.artists[0] + " - " + self.currentSong.name))
			songURL = self.currentSong.getAudioFilename()

			self.VC.play(await self.getSongSource(songURL), after=self.triggerNextSong)
			self.playlist.prepareNextSongs(2,verbose=self.verbose, voice=self.voice,prevFn=self.currentSong.fileName)





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

		foundCmd = False
		foundRootCmd = False
		usageMessage = "```Usage:"
		for validCmd in self.validCommands:
			if(cmd == validCmd[0][0]):
				foundRootCmd = True
				if(len(args) < len(validCmd[0]) or not cmdMatches(args,validCmd[0])):
					usageMessage += "\n\t"+parseCmdPrint(args[0][0],validCmd[0])
				else:
					await validCmd[1](message=message,cmd=args)
					foundCmd = True
					break
		if(not foundRootCmd):
			await message.channel.send("```Invalid command '"+cmd+"'\ntry '"+self.commandChar+"help'```")
		elif(not foundCmd):
			await message.channel.send(usageMessage+"```")

		self.console('Message from {0.author}: {0.content}'.format(message))
