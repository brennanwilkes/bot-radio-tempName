import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re, sys

#Relative path to self file
PREFIX_PATH = sys.path[0]

class spotifyConnection:

	con = None
	id = ""
	secret = ""
	uri = ""

	#Constructor
	def __init__(self, ID_PATH = PREFIX_PATH+"/auth/id", SECRET_PATH = PREFIX_PATH+"/auth/secret", URI_PATH = PREFIX_PATH+"/auth/uri"):

		#Load ID
		try:
			idFile = open(ID_PATH,"r")
			self.id = idFile.read().strip()
		except IOError:
			raise Exception("Please create file "+ID_PATH)
		else:
			idFile.close()

		#Load Secret
		try:
			secretFile = open(SECRET_PATH,"r")
			self.secret = secretFile.read().strip()
		except IOError:
			raise Exception("Please create file "+SECRET_PATH)
		else:
			secretFile.close()

		#Load URI
		try:
			uriFile = open(URI_PATH,"r")
			self.uri = uriFile.read().strip()
		except IOError:
			raise Exception("Please create file "+URI_PATH)
		else:
			uriFile.close()

		#Connect
		self.con = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-library-read",redirect_uri=self.uri, client_id=self.id, client_secret=self.secret))

	#Returns a JSON object of the search results
	def loadPlaylist(self, playlist):

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


		return self.con.playlist("spotify:playlist:"+playlistID)

	def getArtistGenres(self, artist):
		result = self.con.search(artist)
		track = result['tracks']['items'][0]
		artist = self.con.artist(track["artists"][0]["external_urls"]["spotify"])
		album = self.con.album(track["album"]["external_urls"]["spotify"])
		return album["genres"] + artist["genres"]

	#Debug
	def printPlaylist(self, playlist):
		for song in playlist:
			print(song["track"]["name"]," - ",song["track"]["album"]["name"]," - ",song["track"]["artists"][0]["name"])
