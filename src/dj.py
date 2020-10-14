from gtts import gTTS
from pydub import AudioSegment
import re
import random

templateDJTexts = [
	"You're listening to GCS discord radio. Next up, SONG_NAME, by SONG_ARTIST.",
	"That was PAST_SONG_NAME. Here's SONG_NAME.",
	"From PAST_SONG_ARTIST we move to the sweet tunes of SONG_ARTIST.",
	"These tunes brought to you by PLAYLIST_OWNER.",
	"You're listening to PLAYLIST_NAME on GCS discord radio.",
	"Do you like SONG_ARTIST? I hope so, because it's SONG_NAME up next.",
	"If you liked that song you can find it and much more on PAST_SONG_ARTIST's album PAST_SONG_ALBUM.",
	"Coming up next from SONG_ARTIST's album SONG_ALBUM, we've got SONG_NAME.",
	"This next one is specially requested by PLAYLIST_OWNER.",
	"Here at GCS discord radio we love SONG_ARTIST's album SONG_ALBUM, so here's SONG_NAME",
	"Incase you forgot, that was PAST_SONG_NAME by PAST_SONG_ARTIST off of PAST_SONG_ALBUM.",
	"Here's SONG_NAME",
	"More SONG_ARTIST next",
	"Did you know that PAST_SONG_ARTIST has 16 a's in their middle name? Yeah they don't."
]


def generateDJText(pastSong,playlist):
	text = random.choice(templateDJTexts)
	text = re.sub("PAST_SONG_NAME", pastSong.name, text)
	text = re.sub("PAST_SONG_ARTIST", pastSong.artists[0], text)
	text = re.sub("PAST_SONG_ALBUM", pastSong.album, text)

	text = re.sub("SONG_NAME", playlist.songs[0].name, text)
	text = re.sub("SONG_ARTIST", playlist.songs[0].artists[0], text)
	text = re.sub("SONG_ALBUM", playlist.songs[0].album, text)

	text = re.sub("PLAYLIST_NAME", playlist.name, text)
	text = re.sub("PLAYLIST_DESC", playlist.description, text)
	text = re.sub("PLAYLIST_OWNER", playlist.owner, text)

	text = re.sub("SONG_GENRE", random.choice(playlist.songs[0].genres), text)
	text = re.sub("PAST_SONG_GENRE", random.choice(pastSong.genres), text)

	return text





def getWelcomeText(playlist):
	#return "Welcome to GCS Discord radio."
	return "Welcome to GCS Discord radio. Today we'll be listening to "+playlist.name+" by "+playlist.owner+". To start off the night, here's "+playlist.songs[0].name+" by "+playlist.songs[0].artists[0]+". Enjoy."


def writeDJAudio(fn,pastSong=None,playlist=None,text=None,debug=False):
	if(pastSong==None and text==None) or (pastSong!=None and text!=None):
		raise Exception("Please provide either song or text")

	if(text and debug):
		print("Generating DJ for raw text")
	elif(debug):
		print("Generating DJ for song:",pastSong.name,"->",playlist.songs[0].name)

	if(pastSong):
		text = generateDJText(pastSong,playlist)

	tts = gTTS(text)
	tts.save(fn)
	speech = AudioSegment.from_mp3(fn)
	speech = speech + 5
	speech.export(fn, format="mp3")
