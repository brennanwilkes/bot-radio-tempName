from __future__ import unicode_literals
import youtube_dl
from youtube_search import YoutubeSearch
import os, sys
import glob
import dj
from pydub import AudioSegment

from requireHeaders import PREFIX_PATH, requireFile
MAIN_PATH = PREFIX_PATH+"/.."

class Song:

	album = ""
	name = ""
	artists = []
	explicit = False
	duration = 0
	youtubeID = None

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


	def compSongByDuration(self, songYoutbeJSON):
		songYoutbeJSON = songYoutbeJSON["duration"].split(":")
		songYoutbeJSON = (int(songYoutbeJSON[0])*60+int(songYoutbeJSON[1]))*1000
		return abs(self.duration - songYoutbeJSON)

	def getYoutubeSearch(self):
		search = self.name + " by "
		for a in self.artists:
			search += a
		search += " audio"
		query = YoutubeSearch(search, max_results=1).to_dict()

		if(query == None or len(query) < 1):
			return "CANNOT_FIND_SONG"
		return query[0]["id"]

	def downloadAudio(self,override=False,verbose=False):

		if(self.youtubeID == None):
			self.youtubeID = self.getYoutubeSearch()

		if (not override) and glob.glob(MAIN_PATH+"/audioCache/"+self.youtubeID+".*") and (not glob.glob(MAIN_PATH+"/audioCache/"+self.youtubeID+".NA")) and (not glob.glob(MAIN_PATH+"/audioCache/"+self.youtubeID+".part")):
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
			"outtmpl": MAIN_PATH+"/audioCache/"+self.youtubeID+".%(etx)s",
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

		adj = AudioSegment.from_mp3(MAIN_PATH+"/audioCache/"+self.youtubeID+".mp3")
		adj = adj - 5
		adj.export(MAIN_PATH+"/audioCache/"+self.youtubeID+".mp3", format="mp3")

		return True


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
