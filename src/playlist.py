from __future__ import unicode_literals
import youtube_dl

from youtube_search import YoutubeSearch
import os, sys
import glob


#Relative path to this file
PREFIX_PATH = sys.path[0]
MAIN_PATH = PREFIX_PATH+"/.."

class song:

	album = ""
	name = ""
	artists = []
	explicit = False
	duration = 0
	youtubeID = None

	def __init__(self, songJSON):

		self.album = songJSON["track"]["album"]["name"]

		self.artists = []
		for artist in songJSON["track"]["artists"]:
			self.artists.append(artist["name"])

		self.explicit = songJSON["track"]["explicit"]

		self.name = songJSON["track"]["name"]

		self.duration = songJSON["track"]["duration_ms"]


	def compSongByDuration(self, songYoutbeJSON):
		songYoutbeJSON = songYoutbeJSON["duration"].split(":")
		songYoutbeJSON = (int(songYoutbeJSON[0])*60+int(songYoutbeJSON[1]))*1000
		return abs(self.duration - songYoutbeJSON)

	def getYoutubeSearch(self):
		search = self.name + " by "
		for a in self.artists:
			search += a
		query = YoutubeSearch(search, max_results=1).to_dict()

		return query[0]["id"]

	def downloadAudio(self,override=False,debug=False):

		if(self.youtubeID == None):
			self.youtubeID = self.getYoutubeSearch()

		if (not override) and glob.glob(MAIN_PATH+"/audioCache/"+self.youtubeID+".*") and (not glob.glob(MAIN_PATH+"/audioCache/"+self.youtubeID+".NA")) and (not glob.glob(MAIN_PATH+"/audioCache/"+self.youtubeID+".part")):
			if(debug): print("File already loaded:",self.name)
			return

		if(debug): print("Loading audio:",self.name)


		ydl_opts = {
			"format": "bestaudio/best",
			"postprocessors": [{
			"key": "FFmpegExtractAudio",
			"preferredcodec": "mp3",
			"preferredquality": "192",
		}],
			"outtmpl": MAIN_PATH+"/audioCache/"+self.youtubeID+".%(etx)s",
			"quiet": not debug
		}

		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			ydl.download(["https://www.youtube.com/watch?v="+self.youtubeID])  # Download into the current working directory


class playlist:

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
			self.songs.append(song(songJSON))

	def updateYoutubeIDs(self,debug=False):
		for song in self.songs:

			if(debug): print("searching for",song.name)

			song.youtubeID = song.getYoutubeSearch()

			if(debug): print("found",song.youtubeID)

	def downloadAllSongs(self,debug=False, override=False):
		for song in self.songs:
			song.downloadAudio(debug=debug,override=override)

	def downloadNextSongs(self, num=1, debug=False, override=False):
		for i in range(min(len(self.songs),num)):
			self.songs[i].downloadAudio(debug=debug, override=override)
