import os, sys
import dj
from globalSingleton import *

from song import Song
from requireHeaders import PREFIX_PATH, commaSeparator
MAIN_PATH = PREFIX_PATH+"/.."


class Playlist:

	songs = []
	collaborative = False
	description = ""
	name = ""
	owner = ""

	def __init__(self, playlistJSON):

		self.collaborative = playlistJSON["collaborative"]
		self.description = playlistJSON["description"]
		self.name = playlistJSON["name"]
		self.owner = playlistJSON["owner"]["display_name"]

		self.songs = []
		for songJSON in playlistJSON["tracks"]["items"]:
			self.songs.append(Song(songJSON["track"]))


	def insertSong(self,newSong,message,voice,fn,verbose=False):
		self.songs.insert(0,newSong)
		self.prepareNextSongs(1,verbose=verbose,override=True)
		dj.writeDJRequestAudio(fn,newSong,message,voice=voice,verbose=verbose)

	def prepareNextSongs(self, num=1, verbose=False, override=False):
		for i in range(min(len(self.songs),num)):
			if(i >= len(self.songs)):
				break

			suc = self.songs[i].prepare(verbose=verbose, override=override)
			if not suc:
				self.songs.pop(i)
