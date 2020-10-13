from youtube_search import YoutubeSearch


class song:

	album = ""
	name = ""
	artists = []
	explicit = False
	duration = 0

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
		query = YoutubeSearch(search, max_results=10).to_dict()

		return sorted(query,key=lambda s: this.compSongByDuration(s))[0]




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
