from gtts import gTTS
from pydub import AudioSegment


def getWelcomeText(playlist):
	return "Welcome to GCS Discord radio. Today we'll be listening to "+playlist.name+" by "+playlist.owner+". To start off the night, here's "+playlist.songs[0].name+" by "+playlist.songs[0].artists[0]+". Enjoy."

def generateDJText(song):
	pass



def writeDJAudio(fn,song=None,text=None,debug=False):
	if(song==None and text==None) or (song!=None and text!=None):
		raise Exception("Please provide either song or text, not both, not neither")

	if(text and debug):
		print("Generating DJ for raw text")
	elif(debug):
		print("Generating DJ for song:",song.name)

	#radioSay = "You're listening to GCS discord radio. Next up, "+self.playlist.songs[0].name+" by "+self.playlist.songs[0].artists[0]
	tts = gTTS(text)
	tts.save(fn)
	song = AudioSegment.from_mp3(fn)
	song = song + 5
	song.export(fn, format="mp3")
