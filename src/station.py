import os, sys
import json
import dj
from globalSingleton import *

from song import Song
from requireHeaders import PREFIX_PATH, commaSeparator
MAIN_PATH = PREFIX_PATH+"/.."


class Station:

	def __init__(self, loadFromFile=None, playlistJSON=None, playlist=None, station=None, host="en-AU-Wavenet-B", waveLength="100.0", verbose=False):
		self.songs = []
		self.host = host
		self.waveLength = waveLength

		if(playlistJSON):
			self.addPlaylistJSON(playlistJSON)
		if(playlist):
			self.addPlaylist(playlist)
		if(station):
			self.addPlaylist(station)

		if(loadFromFile):
			f = open(loadFromFile, "r")
			data = f.read()
			f.close()
			load = json.loads(data)
			for s in load["songs"]:
				self.songs.append(Song(songDict=s))

			self.host = load["host"]
			self.waveLength = load["waveLength"]
		else:
			fn = self.saveToFile()
			if(verbose): print("Station saved to "+fn)

	def addPlaylistJSON(self, playlistJSON):
		for songJSON in playlistJSON["tracks"]["items"]:
			self.songs.append(Song(songJSON["track"]))

	def addPlaylist(self, playlist):
		for song in playlist.songs:
			self.songs.append(Song(song=song))

	def prepareNextSongs(self, num=1, verbose=False, override=False):
		for i in range(min(len(self.songs),num)):
			if(i >= len(self.songs)):
				break

			suc = self.songs[i].prepare(verbose=verbose, override=override)
			if not suc:
				self.songs.pop(i)

	def saveToFile(self,filename=None):
		if(not filename): filename = MAIN_PATH+"/stations/station"+self.waveLength+".json"

		serial = self.__dict__
		for s in range(len(serial["songs"])):
			serial["songs"][s] = serial["songs"][s].__dict__

		f = open(filename, 'w')
		f.write(json.dumps(serial,indent=4))
		f.close()

		return filename
