from gtts import gTTS
from pydub import AudioSegment
import re
import random, os, sys
import glob
from dateutil import parser
from datetime import datetime
from googleCloud import writeGoogleAudio, googleRadioVoices, googlePrimaryVoices

from requireHeaders import PREFIX_PATH, commaSeparator
from globalSingleton import *
AUDIO_CACHE = PREFIX_PATH+"/../audioCache/"


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
	"We're live again in 5. 4. 3. 2. 1.",
	"Playing the best mix of both PAST_SONG_GENRE and SONG_GENRE, it's GCS radio",
	"The best SONG_GENRE station on the air, GCS radio live",
	"The songs you want to hear, when you want to hear them, GCS radio live",
	"Songs you didn't even know you wanted to hear, coming your way",
	"The good vibes just keep coming with music from SONG_ARTIST up next",
	"One of my personal favourites, PAST_SONG_NAME, great tune.",
	"Oh great, you've been listening to PAST_SONG_ARTIST. You're welcome.",
	"The latest hits and the greatest memories on GCS radio live",
	"Hit music right now on GCS radio live",
	"You've heard it all here on GCS radio. Here's more SONG_GENRE by SONG_ARTIST. It's SONG_NAME next.",
	"And here's some SONG_GENRE by SONG_ARTIST off of their album SONG_ALBUM",
	"Again, in case you forgot, I'm your host, bot dot radio dot temp name, broadcasting live on GCS radio",

]


def filterDJText(text, pastSong, playlist):
	curSong = playlist.songs[0]

	text = re.sub("PAST_SONG_NAME", pastSong.name, text)
	text = re.sub("PAST_SONG_ARTIST", commaSeparator(pastSong.artists), text)
	text = re.sub("PAST_SONG_ALBUM", pastSong.album, text)
	text = re.sub("PAST_SONG_RELEASE", str(parser.parse(pastSong.release if (pastSong!=None and len(pastSong.release)>=2) else "2020").year), text)
	text = re.sub("PAST_SONG_GENRE", random.choice(pastSong.genres if pastSong.genres else ["cool music"]), text)

	text = re.sub("SONG_NAME", curSong.name, text)
	text = re.sub("SONG_ARTIST", commaSeparator(curSong.artists), text)
	text = re.sub("SONG_ALBUM", curSong.album, text)
	text = re.sub("SONG_RELEASE", str(parser.parse(curSong.release if (curSong!=None and len(curSong.release)>=2) else "2020").year), text)
	text = re.sub("SONG_GENRE", random.choice(curSong.genres if curSong.genres else ["cool music"]), text)

	text = re.sub("PLAYLIST_NAME", playlist.name, text)
	text = re.sub("PLAYLIST_DESC", playlist.description, text)
	text = re.sub("PLAYLIST_OWNER", playlist.owner, text)

	text = re.sub("TIME", datetime.now().strftime("%I %M %p"), text)
	text = re.sub("live", "lIve", text)

	return text

def generateDJText(pastSong,playlist):
	return filterDJText(random.choice(templateDJTexts),pastSong,playlist)



def getWelcomeText(playlist):
	#return "Welcome to GCS radio."
	return "Welcome to GCS radio. Today we'll be listening to "+playlist.name+" by "+playlist.owner+". To start off the night, here's "+playlist.songs[0].name+" by "+commaSeparator(playlist.songs[0].artists)+". Enjoy."

def writeDJRequestAudio(fn,req,message,voice="en-US-Wavenet-D",verbose=False):

	reqText1 = "This just in on phone line "+str(random.randint(1, 6))+". This is GCS radio, you're live on air."
	reqText2 = "My name is "+message.author.nick+". Huge fan! Can you play "+req.name+" please?"
	reqText3 = "Absolutely "+message.author.nick+". Anything for a fan. Coming up next."


	writeDJAudio(AUDIO_CACHE+"req1",voice=voice,text=reqText1,verbose=verbose)
	availableVoices = googlePrimaryVoices.copy()
	if voice in availableVoices:
		availableVoices.remove(voice)
	writeDJAudio(AUDIO_CACHE+"req2",voice=random.choice(availableVoices),text=reqText2,verbose=verbose)
	writeDJAudio(AUDIO_CACHE+"req3",voice=voice,text=reqText3,verbose=verbose)

	req1 = AudioSegment.from_mp3(glob.glob(AUDIO_CACHE+"req1"+".*")[0])
	req2 = AudioSegment.from_mp3(glob.glob(AUDIO_CACHE+"req2"+".*")[0])
	req3 = AudioSegment.from_mp3(glob.glob(AUDIO_CACHE+"req3"+".*")[0])

	fullReq = req1 + req2 + req3
	fullReq.export(fn+".mp3", format="mp3")


def writeDJAudio(fn,voice="en-US-Wavenet-D",pastSong=None,playlist=None,text=None,verbose=False):
	if(pastSong==None and text==None) or (pastSong!=None and text!=None):
		raise Exception("Please provide either song or text")

	if(text and verbose):
		print("Generating DJ for raw text with ",voice)
	elif(verbose and len(playlist.songs) > 0):
		print("Generating DJ for song:",pastSong.name,"->",playlist.songs[0].name,"with",voice)
	elif(verbose):
		print("Playlist is empty")

	if(pastSong):
		text = generateDJText(pastSong,playlist)

	writeGoogleAudio(voice,fn,text,verbose=verbose)
