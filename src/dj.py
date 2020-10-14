from gtts import gTTS
from pydub import AudioSegment
import re
import random
from dateutil import parser
from datetime import datetime
from googleCloud import writeGoogleAudio

templateDJTexts = [
	"You're listening to GCS radio. Next up, SONG_NAME, by SONG_ARTIST.",
	"That was PAST_SONG_NAME. Here's SONG_NAME.",
	"From PAST_SONG_ARTIST we move to the sweet tunes of SONG_ARTIST.",
	"These tunes brought to you by PLAYLIST_OWNER.",
	"You're listening to PLAYLIST_NAME on GCS radio.",
	"Do you like SONG_ARTIST? I hope so, because it's SONG_NAME up next.",
	"If you liked that song you can find it and much more on PAST_SONG_ARTIST's album PAST_SONG_ALBUM.",
	"Coming up next from SONG_ARTIST's album SONG_ALBUM, we've got SONG_NAME.",
	"This next one is specially requested by PLAYLIST_OWNER.",
	"Here at GCS radio we love SONG_ARTIST's album SONG_ALBUM, so here's SONG_NAME",
	"Incase you forgot, that was PAST_SONG_NAME by PAST_SONG_ARTIST off of PAST_SONG_ALBUM.",
	"Here's SONG_NAME",
	"More SONG_ARTIST next",
	"Did you know that PAST_SONG_ARTIST has 16 a's in their middle name? Yeah they don't.",
	"This radio is sponsored by NordVPN. Staying safe online is an ever growing difficulty and you could be exploited by hackers. NordVPN allows you to change your IP address, making you harder to track, securing your privacy. Check out the link in the discord to get 20% off for the first two months and thank you to NordVPN for sponsoring this radio.",
	"Today's radio broadcast is sponsored by Raid Shadow Legends, one of the biggest mobile role-playing games of 2019 and it's totally free! Currently almost 10 million users have joined Raid over the last six months, and it's one of the most impressive games in its class with detailed models, environments and smooth 60 frames per second animations! So what are you waiting for? Go to the discord, click on the stories with michael channel and you'll get 50,000 silver and a free epic champion as part of the new player program to start your journey! Good luck and I'll see you there!",
	"Enjoying GCS radio? We have plenty more PAST_SONG_GENRE to come",
	"That song came out in PAST_SONG_RELEASE",
	"Moving on to music from SONG_RELEASE",
	"Next, some SONG_GENRE music",
	"PAST_SONG_ARTIST's album PAST_SONG_ALBUM has lots of other PAST_SONG_GENRE on it too.",
	"Want to request a song? Call in now with dollarsign request in the chat",
	"It is currently TIME",
	"And we're back with more SONG_GENRE just for you",
	"Another classic from SONG_RELEASE, SONG_NAME by SONG_ARTIST",
	"I'm your host, bot dot radio dot temp name, broadcasting live on GCS radio",
	"You'll be getting a healthy serving of SONG_GENRE tonight, but let's start with some SONG_ARTIST",
	"Next up one of my personal favourites, SONG_NAME",
	"It's your favourite host bot dot radio dot temp name, broadcasting live on GCS radio",
	"We're live again in 5. 4. 3, 2, 1",
	"Playing the best mix of both PAST_SONG_GENRE and SONG_GENRE, it's GCS radio",
	"The best SONG_GENRE station on the air, GCS radio live",
	"The songs you want to hear, when you want to hear them, GCS radio live",
	"Songs you didn't even know you wanted to hear, coming your way",
	"The good vibes just keep coming with music from SONG_ARTIST up next",
	"One of my personal favourites, PAST_SONG_NAME, great tune."
]


def generateDJText(pastSong,playlist):
	text = random.choice(templateDJTexts)
	text = re.sub("PAST_SONG_NAME", pastSong.name, text)
	text = re.sub("PAST_SONG_ARTIST", pastSong.artists[0], text)
	text = re.sub("PAST_SONG_ALBUM", pastSong.album, text)
	#text = re.sub("PAST_SONG_RELEASE", parser.parse(str(pastSong.release)).year, text)

	curSong = playlist.songs[0]

	text = re.sub("SONG_NAME", curSong.name, text)
	text = re.sub("SONG_ARTIST", curSong.artists[0], text)
	text = re.sub("SONG_ALBUM", curSong.album, text)
	#text = re.sub("SONG_RELEASE", parser.parse(str(curSong.release)).year, text)

	text = re.sub("PLAYLIST_NAME", playlist.name, text)
	text = re.sub("PLAYLIST_DESC", playlist.description, text)
	text = re.sub("PLAYLIST_OWNER", playlist.owner, text)

	text = re.sub("SONG_GENRE", random.choice(curSong.genres if curSong.genres else ["cool music"]), text)
	text = re.sub("PAST_SONG_GENRE", random.choice(pastSong.genres if pastSong.genres else ["cool music"]), text)

	text = re.sub("TIME", datetime.now().strftime("%I %M %p"), text)
	text = re.sub("live", "lIve", text)

	return text





def getWelcomeText(playlist):
	#return "Welcome to GCS radio."
	return "Welcome to GCS radio. Today we'll be listening to "+playlist.name+" by "+playlist.owner+". To start off the night, here's "+playlist.songs[0].name+" by "+playlist.songs[0].artists[0]+". Enjoy."


def writeDJAudio(fn,voice="en-US-Wavenet-D",pastSong=None,playlist=None,text=None,debug=False):
	if(pastSong==None and text==None) or (pastSong!=None and text!=None):
		raise Exception("Please provide either song or text")

	if(text and debug):
		print("Generating DJ for raw text with ",voice)
	elif(debug and len(playlist.songs) > 0):
		print("Generating DJ for song:",pastSong.name,"->",playlist.songs[0].name,"with",voice)
	else:
		print("Playlist is empty")

	if(pastSong):
		text = generateDJText(pastSong,playlist)

	writeGoogleAudio(voice,fn,text)
	#tts = gTTS(text)
	#tts.save(fn)
	#speech = AudioSegment.from_mp3(fn)
	#speech = speech + 5
	#speech.export(fn, format="mp3")
