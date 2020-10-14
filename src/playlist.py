from __future__ import unicode_literals
import youtube_dl

from youtube_search import YoutubeSearch
import os, sys
import glob


#Relative path to self file
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

		self.release = songJSON["track"]["album"]["release_date"]

		self.artists = []
		for artist in songJSON["track"]["artists"]:
			self.artists.append(artist["name"])

		self.explicit = songJSON["track"]["explicit"]

		self.name = songJSON["track"]["name"]

		self.duration = songJSON["track"]["duration_ms"]

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

		return query[0]["id"]

	def downloadAudio(self,override=False,debug=False):

		if(self.youtubeID == None):
			self.youtubeID = self.getYoutubeSearch()

		if (not override) and glob.glob(MAIN_PATH+"/audioCache/"+self.youtubeID+".*") and (not glob.glob(MAIN_PATH+"/audioCache/"+self.youtubeID+".NA")) and (not glob.glob(MAIN_PATH+"/audioCache/"+self.youtubeID+".part")):
			if(debug): print("File already loaded:",self.name)
			return True

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

		tries = 0
		while tries < 5:
			try:
				with youtube_dl.YoutubeDL(ydl_opts) as ydl:
					ydl.download(["https://www.youtube.com/watch?v="+self.youtubeID])
			except Exception:
				print("failed to load",self.youtubeID)
				tries += 1
			else:
				break
		if(tries >= 5):
			print("Could not find youtube source for",self.youtubeID)
			return False
		return True


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
		self.downloadNextSongs(num=len(self.songs),debug=debug,override=override)

	def downloadNextSongs(self, num=1, debug=False, override=False):
		for i in range(min(len(self.songs),num)):
			if(i >= len(self.songs)):
				break

			suc = self.songs[i].downloadAudio(debug=debug, override=override)
			if not suc:
				self.songs.pop(i)

	def updateNextSongsGenres(self, num=1, sp=None, debug=False, override=False):
		for i in range(min(len(self.songs),num)):
			self.songs[i].genres = sp.getArtistGenres(self.songs[i].artists[0])
			if(len(self.songs[i].genres) == 0):
				self.songs[i].genres.append("good music")
