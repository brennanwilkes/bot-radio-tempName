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

	def __init__(this, playlistJSON):

		this.songs = []
		for songJSON in playlistJSON:
			this.songs.append(song(songJSON))
