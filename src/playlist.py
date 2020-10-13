class song:

	album = ""
	name = ""
	artists = []
	explicit = False

	def __init__(this, songJSON):

		this.album = songJSON["track"]["album"]["name"]

		this.artists = []
		for artist in songJSON["track"]["artists"]:
			this.artists.append(artist["name"])

		this.explicit = songJSON["track"]["explicit"]

		this.name = songJSON["track"]["name"]


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
