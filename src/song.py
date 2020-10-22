from __future__ import unicode_literals
from youtube_search import YoutubeSearch
import os, sys
import glob
import youtube_dl
from pydub import AudioSegment
from globalSingleton import *

from requireHeaders import PREFIX_PATH, commaSeparator
MAIN_PATH = PREFIX_PATH+"/.."


class Song:

	album = ""
	name = ""
	artists = []
	explicit = False
	duration = 0
	youtubeID = None
	fileName = None
	extension = None

	def __init__(self, songJSON):

		self.album = songJSON["album"]["name"]

		self.release = songJSON["album"]["release_date"]

		self.artists = []
		for artist in songJSON["artists"]:
			self.artists.append(artist["name"])

		self.explicit = songJSON["explicit"]

		self.name = songJSON["name"]

		self.duration = songJSON["duration_ms"]

		self.genres = None


	def prepare(self,override=False,verbose=False):
		if(self.youtubeID == None):
			self.youtubeID = self.getYoutubeSearch()
		if(self.youtubeID == "CANNOT_FIND_SONG"):
			return False

		self.fileName = MAIN_PATH+"/audioCache/"+self.youtubeID

		return self.downloadAudio(override=override, verbose=verbose)



	def getYoutubeSearch(self):
		search = self.name + " by " + commaSeparator(self.artists) + " audio official song"

		query = YoutubeSearch(search, max_results=1).to_dict()

		if(query == None or len(query) < 1):
			return "CANNOT_FIND_SONG"
		return query[0]["id"]

	def downloadAudio(self,override=False,verbose=False):

		if (not override) and glob.glob(self.fileName+".*") and (not glob.glob(self.fileName+".NA")) and (not glob.glob(self.fileName+".part")):
			if(verbose):
				print("File already loaded:",self.name)
			return True

		if(verbose):
			print("Loading audio:",self.name)


		ydl_opts = {
			"format": "bestaudio/best",
			"postprocessors": [{
			"key": "FFmpegExtractAudio",
			"preferredcodec": "mp3",
			"preferredquality": "192",
		}],
			"outtmpl": self.fileName+".%(etx)s",
			"quiet": not verbose
		}

		tries = 0
		while tries < 5:
			try:
				with youtube_dl.YoutubeDL(ydl_opts) as ydl:
					ydl.download(["https://www.youtube.com/watch?v="+self.youtubeID])
			except Exception:
				if(verbose):
					print("failed to load",self.youtubeID)
				tries += 1
			else:
				break
		if(tries >= 5):
			if(verbose):
				print("Could not find youtube source for",self.youtubeID)
			return False

		if glob.glob(self.fileName+".*") and (not glob.glob(self.fileName+".NA")) and (not glob.glob(self.fileName+".part")):
			self.extension = os.path.splitext(glob.glob(self.fileName+".*")[0])[1][1:]
		else:
			return False

		adj = AudioSegment.from_mp3(self.fileName+"."+self.extension)
		adj = adj - 5
		adj.export(self.fileName+"."+self.extension, format=self.extension)

		return True
