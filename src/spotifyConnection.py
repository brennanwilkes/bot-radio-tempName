import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re, sys
from requireHeaders import PREFIX_PATH, getTokenFromFile

class SpotifyConnection:

	con = None
	id = ""
	secret = ""
	uri = ""
	verbose = True

	#Constructor
	def __init__(self, ID_F = "id", SECRET_F = "secret", URI_F = "uri", verbose=True):

		self.verbose = verbose

		#Load ID
		self.id = getTokenFromFile(ID_F)
		#Load Secret
		self.secret = getTokenFromFile(SECRET_F)
		#Load URI
		self.uri = getTokenFromFile(URI_F)

	def connect(self):
		#Connect
		self.con = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-library-read",redirect_uri=self.uri, client_id=self.id, client_secret=self.secret))
		if(self.verbose):
			print("Succesfully connected to spotify ID "+self.id[:4]+("*"*len(self.id[4:])))

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

		if(self.verbose):
			print("Searching for genres for "+artist)

		result = self.con.search(artist)
		track = result['tracks']['items'][0]
		artist = self.con.artist(track["artists"][0]["external_urls"]["spotify"])
		album = self.con.album(track["album"]["external_urls"]["spotify"])
		genres = album["genres"] + artist["genres"]
		if(len(genres) == 0):
			genres.append("good music")
		return genres

	def getSong(self, query):
		result = self.con.search(query)
		return result["tracks"]["items"][0]

	#Debug
	def printPlaylist(self, playlist):
		for song in playlist:
			print(song["track"]["name"]," - ",song["track"]["album"]["name"]," - ",song["track"]["artists"][0]["name"])
