import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re

#Relative path to this file
PREFIX_PATH = re.compile("(.*)/[^/]*").match("./"+__file__).group(1)

class spotifyConnection:

	#Constructor
	def __init__(this, ID_PATH = PREFIX_PATH+"/auth/id", SECRET_PATH = PREFIX_PATH+"/auth/secret", URI_PATH = PREFIX_PATH+"/auth/uri"):

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

	#Returns a JSON object of the search results
	def loadPlaylist(this, playlist):

		#Check if playlist url is a link format
		urlRegexString = "^[a-z]*://open.spotify.com/playlist/([^?]*)?.*$"
		urlSearch = re.compile(urlRegexString).match(playlist)

		#Check if playlist url is a URI format
		uriRegexString = "^spotify:playlist:(.*)$"
		uriSearch = re.compile(uriRegexString).match(playlist)

		if urlSearch != None:
			playlistID = urlSearch.group(1)
		elif uriSearch != None:
			playlistID = uriSearch.group(1)
		else:
			raise Exception("Invalid playlist",playlist)

		#query spotify
		return this.con.user_playlist_tracks("", "spotify:playlist:"+playlistID, fields='items,uri,name,id,total', market='fr')["items"]

	#Debug
	def printPlaylist(this, playlist):
		for song in playlist:
			print(song["track"]["name"]," - ",song["track"]["album"]["name"]," - ",song["track"]["artists"][0]["name"])
