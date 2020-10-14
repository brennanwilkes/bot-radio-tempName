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

	def __init__(this, songJSON):

		this.album = songJSON["track"]["album"]["name"]

		this.artists = []
		for artist in songJSON["track"]["artists"]:
			this.artists.append(artist["name"])

		this.explicit = songJSON["track"]["explicit"]

		this.name = songJSON["track"]["name"]

		this.duration = songJSON["track"]["duration_ms"]


	def compSongByDuration(this, songYoutbeJSON):
		songYoutbeJSON = songYoutbeJSON["duration"].split(":")
		songYoutbeJSON = (int(songYoutbeJSON[0])*60+int(songYoutbeJSON[1]))*1000
		return abs(this.duration - songYoutbeJSON)

	def getYoutubeSearch(this):
		search = this.name + " by "
		for a in this.artists:
			search += a
		query = YoutubeSearch(search, max_results=1).to_dict()

		return query[0]["id"]

	def downloadAudio(this,override=False,debug=False):

		if(this.youtubeID == None):
			this.youtubeID = this.getYoutubeSearch()

		if (not override) and glob.glob(MAIN_PATH+"/audioCache/"+this.youtubeID+".*") and (not glob.glob(MAIN_PATH+"/audioCache/"+this.youtubeID+".NA")) and (not glob.glob(MAIN_PATH+"/audioCache/"+this.youtubeID+".part")):
			if(debug): print("File exists! Skipping")
			return

		ydl_opts = {
			"format": "bestaudio/best",
			"postprocessors": [{
			"key": "FFmpegExtractAudio",
			"preferredcodec": "mp3",
			"preferredquality": "192",
		}],
			"outtmpl": MAIN_PATH+"/audioCache/"+this.youtubeID+".%(etx)s",
			"quiet": not debug
		}

		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			ydl.download(["https://www.youtube.com/watch?v="+this.youtubeID])  # Download into the current working directory


class playlist:

	songs = []
	collaborative = False
	description = ""
	name = ""
	owner = ""


	def __init__(this, playlistJSON):

		this.collaborative = playlistJSON["collaborative"]
		this.description = playlistJSON["description"]
		this.name = playlistJSON["name"]
		this.owner = playlistJSON["owner"]["display_name"]

		this.songs = []
		for songJSON in playlistJSON["tracks"]["items"]:
			this.songs.append(song(songJSON))

	def updateYoutubeIDs(this,debug=False):
		for song in this.songs:

			if(debug): print("searching for",song.name)

			song.youtubeID = song.getYoutubeSearch();

			if(debug): print("found",song.youtubeID)

	def downloadAllSongs(this,debug=False, override=False):
		for song in this.songs:
			song.downloadAudio(debug=debug,override=override)

	def downloadNextSongs(this, num=1, debug=False, override=False):
		for i in range(min(len(this.songs),num)):
			this.songs[i].downloadAudio(debug=debug, override=override)
