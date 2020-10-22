import os, sys
import dj
from globalSingleton import *

from song import Song
from requireHeaders import PREFIX_PATH, commaSeparator
MAIN_PATH = PREFIX_PATH+"/.."


class Station:

	def __init__(self, playlistJSON=None, playlist=None, station=None, host="en-AU-Wavenet-B", waveLength="100.0"):
		self.songs = []
		self.host = host
		self.waveLength = waveLength

		if(playlistJSON):
			self.addPlaylistJSON(playlistJSON)
		if(playlist):
			self.addPlaylist(playlist)
		if(station):
			self.addPlaylist(station)

	def addPlaylistJSON(self, playlistJSON):
		for songJSON in playlistJSON["tracks"]["items"]:
			self.songs.append(Song(songJSON["track"]))

	def addPlaylist(self, playlist):
		for song in playlist.songs:
			self.songs.append(song.clone())

	def prepareNextSongs(self, num=1, verbose=False, override=False):
		for i in range(min(len(self.songs),num)):
			if(i >= len(self.songs)):
				break

			suc = self.songs[i].prepare(verbose=verbose, override=override)
			if not suc:
				self.songs.pop(i)
