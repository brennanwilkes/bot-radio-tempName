from youtube_search import YoutubeSearch
import pafy

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

		#return sorted(query,key=lambda s: this.compSongByDuration(s))[0]["id"]
		return query[0]["id"]

	def downloadAudio(this):
		if(this.youtubeID == None):
			this.youtubeID = this.getYoutubeSearch()

		vid = pafy.new("https://www.youtube.com/watch?v="+this.youtubeID)

		stream = vid.getbestaudio(preftype="m4a")

		print(this.youtubeID)
		#print(stream.url)
		#print(stream.url_https)
		stream.download(filepath="audioCache/"+this.name.replace(' ', '-')+"."+stream.extension)

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
