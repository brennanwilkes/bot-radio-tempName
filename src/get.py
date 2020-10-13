import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import json
import re


class spotifyConnection:

	def __init__(this, ID_PATH = "auth/id", SECRET_PATH = "auth/secret", URI_PATH = "auth/uri"):

		this.playlist = None

		#Load ID
		try:
			idFile = open(ID_PATH,"r")
			this.id = idFile.read().strip()
		except IOError:
			raise Exception("Please create file "+ID_PATH)
		else:
			idFile.close()

		#Load Secret
		try:
			secretFile = open(SECRET_PATH,"r")
			this.secret = secretFile.read().strip()
		except IOError:
			raise Exception("Please create file "+SECRET_PATH)
		else:
			secretFile.close()

		#Load URI
		try:
			uriFile = open(URI_PATH,"r")
			this.uri = uriFile.read().strip()
		except IOError:
			raise Exception("Please create file "+URI_PATH)
		else:
			uriFile.close()

		#Connect
		this.con = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-library-read",redirect_uri=this.uri, client_id=this.id, client_secret=this.secret))

	def loadPlaylist(this, playlist):

		urlRegexString = "^[a-z]*://open.spotify.com/playlist/([^?]*)?.*$"
		urlSearch = re.compile(urlRegexString).match(playlist)

		uriRegexString = "^spotify:playlist:(.*)$"
		uriSearch = re.compile(uriRegexString).match(playlist)

		if urlSearch != None:
			playlistID = urlSearch.group(1)
		elif uriSearch != None:
			playlistID = uriSearch.group(1)
		else:
			raise Exception("Invalid playlist",playlist)

		queryResults = this.con.user_playlist_tracks("", "spotify:playlist:"+playlistID, fields='items,uri,name,id,total', market='fr')

		this.playlist = queryResults["items"]


	def printPlaylist(this):
		for song in this.playlist:
			print(song["track"]["name"]," - ",song["track"]["album"]["name"]," - ",song["track"]["artists"][0]["name"])





test = spotifyConnection()
test.loadPlaylist("https://open.spotify.com/playlist/0NkBcnxyLMeUXKXww80lFV?si=okRaEV_wTnqJnMbmQEBrXA")
test.printPlaylist()
