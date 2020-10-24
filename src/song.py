from __future__ import unicode_literals
import os, sys
import glob
import youtube_dl
from pydub import AudioSegment
from globalSingleton import *

import urllib.parse
import requests

from requireHeaders import PREFIX_PATH, commaSeparator
MAIN_PATH = PREFIX_PATH+"/.."

YOUTUBE_CACHE = {}

class Song:

	album = ""
	name = ""
	artists = []
	explicit = False
	duration = 0
	youtubeID = None
	fileName = None
	extension = None

	def __init__(self, songJSON=None, song=None, songDict=None):

		#Copy constructor
		if(song):
			self.album = song.album
			self.release = song.release
			self.artists = []
			for a in song.artists:
				self.artists.append(a)
			self.explicit = song.explicit
			self.name = song.name
			self.duration = song.duration
			self.genres = song.genres
			self.fileName = song.fileName
			self.youtubeID = song.youtubeID
			self.extension = song.extension
		elif(songDict):
			self.album = songDict["album"]
			self.release = songDict["release"]
			self.artists = []
			for a in songDict["artists"]:
				self.artists.append(a)
			self.explicit = songDict["explicit"]
			self.name = songDict["name"]
			self.duration = songDict["duration"]
			self.genres = songDict["genres"]
			self.fileName = songDict["fileName"]
			self.youtubeID = songDict["youtubeID"]
			self.extension = songDict["extension"]

		else:
			self.album = songJSON["album"]["name"]

			self.release = songJSON["album"]["release_date"]

			self.artists = []
			for artist in songJSON["artists"]:
				self.artists.append(artist["name"])

			self.explicit = songJSON["explicit"]

			self.name = songJSON["name"]

			self.duration = songJSON["duration_ms"]

			self.genres = None

	def prepare(self,override=False,verbose=False,downloadFile=True):
		if(self.youtubeID == None):
			if(self.name in YOUTUBE_CACHE):
				self.youtubeID = YOUTUBE_CACHE[self.name]
			else:
				self.youtubeID = self.getYoutubeSearch(verbose=verbose)
		else:
			YOUTUBE_CACHE[self.name] = self.youtubeID

		if(self.youtubeID == "CANNOT_FIND_SONG"):
			return False
		if(not self.genres):
			self.genres = spotifyConInstance.getArtistGenres(self.artists[0])

		self.fileName = MAIN_PATH+"/audioCache/"+self.youtubeID

		if(downloadFile):
			return self.downloadAudio(override=override, verbose=verbose)

	def getAudioFilename(self):
		return self.fileName + "." + self.extension

	def getYoutubeSearch(self,verbose=False):

		search = self.name + " by " + commaSeparator(self.artists) + " audio official song"

		if(verbose):
			print("Querying youtube for:",search)

		url = "https://youtube.com/results?search_query="
		query = "+".join([urllib.parse.quote(p) for p in search.split(" ")])

		if(verbose):
			print("Using query: "+query)

		try:
			res = requests.get(url+query)
			id = res.text.split("\"videoRenderer\":{\"videoId\":\"")[1].split("\"")[0]
		except Exception as e:
			if(verbose):
				print(e)
			return "CANNOT_FIND_SONG"
		else:
			if(verbose):
				print("Found ID", id)
			YOUTUBE_CACHE[self.name] = id
			return id

	def downloadAudio(self,override=False,verbose=False):

		if(verbose):
			print("Loading audio:",self.name)

		if (not override) and glob.glob(self.fileName+".*") and (not glob.glob(self.fileName+".NA")) and (not glob.glob(self.fileName+".part")):
			if(verbose):
				print("File already loaded:",self.name)

			if glob.glob(self.fileName+".*") and (not glob.glob(self.fileName+".NA")) and (not glob.glob(self.fileName+".part")):
				self.extension = os.path.splitext(glob.glob(self.fileName+".*")[0])[1][1:]
			else:
				return False

			return True

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
