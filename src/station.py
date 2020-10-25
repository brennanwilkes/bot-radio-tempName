import os, sys
import json
import glob, re
import random

import dj
from globalSingleton import *
from song import Song
from requireHeaders import PREFIX_PATH, commaSeparator
MAIN_PATH = PREFIX_PATH+"/.."


stationtemplateDJTexts = [
	"You're listening to WAVELENGTH FM, PLAYLIST_NAME. Next up, SONG_NAME",
	"This is WAVELENGTH FM, PLAYLIST_NAME. Coming your way next is SONG_NAME",
	"Coming right up next on PLAYLIST_NAME WAVELENGTH, we've got SONG_NAME by SONG_ARTIST",
	"Hit SONG_GENRE music. All day. WAVELENGTH FM, PLAYLIST_NAME. Up next, SONG_NAME",
	"WAVELENGTH FM PLAYLIST_NAME brings you the best SONG_GENRE and PAST_SONG_GENRE 24 7. Now playing SONG_NAME off of SONG_ALBUM."
]

rssStationTemplateDJTexts = [
	"This is WAVELENGTH FM, here's RSS_NAME with some news. RSS_TITLE, RSS_DESC. Once again that was RSS_NAME on WAVELENGTH FM. Next up we've got some SONG_GENRE by SONG_ARTIST coming your way, here's SONG_NAME.",
	"And an update coming your way exclusive to listeners of WAVELENGTH FM. RSS_TITLE, RSS_DESC. That was brought to you by RSS_NAME, exclusive on WAVELENGTH FM. Now back to what you're here for, we've got SONG_NAME by SONG_ARTIST coming your way.",
	"Music. News. Weather. WAVELENGTH FM has it all. RSS_TITLE, RSS_DESC. Now here's SONG_NAME by SONG_ARTIST, exclusive on WAVELENGTH FM."
]



class Station:

	def __init__(self, loadFromFile=None, playlistJSON=None, playlist=None, station=None, host="en-AU-Wavenet-B", waveLength="100.0", verbose=False, owner="", name=None):
		self.songs = []
		self.requests = []
		self.host = host
		self.waveLength = waveLength
		if(name):
			self.name = name
		else:
			self.name = "GCS "+waveLength
		self.owner = owner
		self.description = ""
		self.genres = {}
		self.currentSong = None
		self.customVoiceLines = []

		if(playlistJSON):
			self.addPlaylistJSON(playlistJSON)
		if(playlist):
			self.addPlaylist(playlist, verbose=verbose)
		if(station):
			self.waveLength = station.waveLength
			self.host = station.host
			self.genres = station.genres
			self.customVoiceLines = station.customVoiceLines
			self.addPlaylist(station, verbose=verbose)

		if(loadFromFile):
			f = open(loadFromFile, "r")
			data = f.read()
			f.close()
			load = json.loads(data)
			for s in load["songs"]:
				self.songs.append(Song(songDict=s))

			self.genres = load["genres"]
			self.host = load["host"]
			self.waveLength = load["waveLength"]
			self.name = load["name"]
			self.owner = load["owner"]
			self.description = load["description"]
			if "customVoiceLines" in load:
				self.customVoiceLines = load["customVoiceLines"]


		elif(not station):
			self.saveToFile(verbose=verbose)

	def addPlaylistJSON(self, playlistJSON):
		for songJSON in playlistJSON["tracks"]["items"]:
			self.songs.append(Song(songJSON["track"]))

	def addPlaylist(self, playlist, verbose=False):
		self.owner=playlist.owner
		self.name=playlist.name
		self.description=playlist.description

		curSongCache = {}
		for song in self.songs:
			curSongCache[song.name] = True

		numAdded = 0
		for song in playlist.songs:
			if(song.name in curSongCache):
				if(verbose):
					print(song.name,"already in",self.waveLength)
			else:
				numAdded += 1
				self.songs.append(Song(song=song))
		return numAdded

	def filterStationDJText(self,text):

		text = re.sub("WAVELENGTH", self.waveLength, text)

		return text

	def prepareNextSongs(self, num=1, voice=None, verbose=False, override=False, welcome=False, prevFn=None):
		if(not voice):
			voice = self.host
		if((not prevFn) and (self.currentSong != None)):
			prevFn = self.currentSong.fileName

		for i in range(min(len(self.songs),num)):
			if(verbose): print("Preparing "+str(i+1)+"/"+str(min(len(self.songs),num)))
			if(i >= len(self.songs)):
				break

			suc = self.songs[i].prepare(verbose=verbose, override=override)

			if(suc):
				if (i==0 and welcome):
					djFn = self.songs[i].fileName+"-welcome-dj"
				else:
					if(prevFn and i==0):
						djFn = prevFn+"-dj-"+self.songs[i].youtubeID
					else:
						djFn = self.songs[i-1].fileName+"-dj-"+self.songs[i].youtubeID

				if override or not glob.glob(djFn+".*"):
					if(i == 0 and welcome):
						if(verbose):
							print("Preparing DJ welcome audio")
						text = dj.getWelcomeText(self)
					else:
						if(verbose):
							print("Preparing DJ audio for "+self.songs[i-1].name+" -> "+self.songs[i].name)

						djScript = random.choice([
							random.choice(stationtemplateDJTexts + self.customVoiceLines),
							random.choice(dj.templateDJTexts),
							random.choice(dj.rssTemplateDJTexts + rssStationTemplateDJTexts)])
						##APPLY CUSTOM TEXTS

						text = dj.filterDJText(djScript, self.songs[i-1], curSong = self.songs[i], nm = self.name, desc = self.description, owner = self.owner)
						text = self.filterStationDJText(text)

					dj.writeGoogleAudio(voice,djFn,text,verbose=verbose)

			else:
				self.songs.pop(i)
		self.saveToFile(verbose=verbose)

	def insertSong(self,newSong,message,voice,fn,verbose=False):
		self.requests.insert(0,newSong)
		self.requests[0].prepare(verbose=verbose)
		if(verbose):
			print("Preparing DJ request audio for "+self.currentSong.name+" -> "+newSong.name)
		dj.writeDJRequestAudio(self.currentSong.fileName+"-dj-"+newSong.youtubeID,newSong,message,voice=voice,verbose=verbose)


	def saveToFile(self,filename=None,verbose=False):
		if(not filename): filename = MAIN_PATH+"/stations/station"+self.waveLength+".json"

		serial = Station(station=self).__dict__
		for s in range(len(serial["songs"])):
			serial["songs"][s] = Song(song=serial["songs"][s]).__dict__

		f = open(filename, 'w')
		f.write(json.dumps(serial,indent=4))
		f.close()

		if(verbose): print("Station saved to "+filename)
		return filename

	def getNextSong(self, remove = True):
		if(len(self.requests) > 0):
			if(not remove):
				return self.requests[0]
			s = self.requests.pop(0)
			self.currentSong = s
			return s
		else:
			if(not remove):
				return self.songs[0]
			next = self.songs.pop(0)
			self.songs.append(next)
			self.currentSong = next
			return next

	def preCache(self,verbose=False):
		for s in self.songs:
			s.prepare(verbose=verbose,downloadFile=False)
			self.saveToFile(verbose=False)

	def calcGenres(self,verbose=False):
		self.genres = {}
		for s in self.songs:
			if(s.genres):
				for g in s.genres:
					if g in self.genres:
						self.genres[g] += 1
					else:
						if(verbose):
							print("Added genre "+g)
						self.genres[g] = 1

		self.saveToFile(verbose=verbose)
		return self.genres
