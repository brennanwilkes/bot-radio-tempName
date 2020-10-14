from gtts import gTTS
from pydub import AudioSegment
import re
import random

templateDJTexts = [
	"You're listening to GCS discord radio. Next up, SONG_NAME, by SONG_ARTIST",
	"That was PAST_SONG_NAME. Here's SONG_NAME",
	"From PAST_SONG_ARTIST we move to the sweet tunes of SONG_ARTIST"
]


def generateDJText(pastSong,playlist):
	text = random.choice(templateDJTexts)
	text = re.sub("PAST_SONG_NAME", pastSong.name, text)
	text = re.sub("PAST_SONG_ARTIST", pastSong.artists[0], text)
	text = re.sub("PAST_SONG_ALBUM", pastSong.album, text)

	text = re.sub("SONG_NAME", playlist.songs[0].name, text)
	text = re.sub("SONG_ARTIST", playlist.songs[0].artists[0], text)
	text = re.sub("SONG_ALBUM", playlist.songs[0].album, text)

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
