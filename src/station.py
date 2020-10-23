import os, sys
import json
import dj
from globalSingleton import *

from song import Song
from requireHeaders import PREFIX_PATH, commaSeparator
MAIN_PATH = PREFIX_PATH+"/.."


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

		if(playlistJSON):
			self.addPlaylistJSON(playlistJSON)
		if(playlist):
			self.addPlaylist(playlist, verbose=verbose)
		if(station):
			self.waveLength = station.waveLength
			self.host = station.host
			self.addPlaylist(station, verbose=verbose)

		if(loadFromFile):
			f = open(loadFromFile, "r")
			data = f.read()
			f.close()
			load = json.loads(data)
			for s in load["songs"]:
				self.songs.append(Song(songDict=s))

			self.host = load["host"]
			self.waveLength = load["waveLength"]
			self.name = load["name"]
			self.owner = load["owner"]
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

	def prepareNextSongs(self, num=1, verbose=False, override=False):
		for i in range(min(len(self.songs),num)):
			if(verbose): print("Preparing "+str(i+1)+"/"+str(min(len(self.songs),num)))
			if(i >= len(self.songs)):
				break

			suc = self.songs[i].prepare(verbose=verbose, override=override)

			if not suc:
				self.songs.pop(i)

		self.saveToFile(verbose=verbose)

	def insertSong(self,newSong,message,voice,fn,verbose=False):
		self.requests.insert(0,newSong)
		self.requests[0].prepare(verbose=verbose)
		dj.writeDJRequestAudio(fn,newSong,message,voice=voice,verbose=verbose)


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

	def getNextSong(self):
		if(len(self.requests) > 0):
			return self.requests.pop(0)
		else:
			next = self.songs.pop(0)
			self.songs.append(next)
			return next
