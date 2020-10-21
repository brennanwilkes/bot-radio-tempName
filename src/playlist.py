from __future__ import unicode_literals
import youtube_dl
from youtube_search import YoutubeSearch
import os, sys
import glob
import dj
from pydub import AudioSegment

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

	def updateYoutubeIDs(self,verbose=False):
		for song in self.songs:

			if(verbose):
				print("searching for",song.name)

			song.youtubeID = song.getYoutubeSearch()

			if(verbose):
				print("found",song.youtubeID)

	def insertSong(self,newSong,sp,message,voice,fn,verbose=False):
		self.songs.insert(0,newSong)
		self.downloadNextSongs(1,verbose=verbose,override=True)
		self.updateNextSongsGenres(1,verbose=verbose,sp=sp)
		dj.writeDJRequestAudio(fn,newSong,message,voice=voice,verbose=verbose)

	def downloadAllSongs(self,verbose=False, override=False):
		self.downloadNextSongs(num=len(self.songs),verbose=verbose,override=override)

	def downloadNextSongs(self, num=1, verbose=False, override=False):
		for i in range(min(len(self.songs),num)):
			if(i >= len(self.songs)):
				break

			suc = self.songs[i].downloadAudio(verbose=verbose, override=override)
			if not suc:
				self.songs.pop(i)

	def updateNextSongsGenres(self, num=1, sp=None, verbose=False, override=False):
		for i in range(min(len(self.songs),num)):
			self.songs[i].genres = sp.getArtistGenres(self.songs[i].artists[0])
			if(len(self.songs[i].genres) == 0):
				self.songs[i].genres.append("good music")
