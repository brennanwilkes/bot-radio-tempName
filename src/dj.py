from gtts import gTTS
from pydub import AudioSegment
import re
import random, os, sys
import glob
from dateutil import parser
from datetime import datetime
from googleCloud import writeGoogleAudio, googleRadioVoices, googlePrimaryVoices

from requireHeaders import PREFIX_PATH, commaSeparator
import rss
from globalSingleton import *
AUDIO_CACHE = PREFIX_PATH+"/../audioCache/"

rssTemplateDJTets = [
	"This just in from RSS_NAME, RSS_TITLE, RSS_DESC. Now, back to music, it's SONG_NAME coming up next.",
	"And an update from RSS_NAME, RSS_TITLE, RSS_DESC. Once again that was RSS_NAME. You're listeing to GCS radio live, here's SONG_NAME by SONG_ARTIST",
	"RSS_TITLE, RSS_DESC. That alert was from RSS_NAME, now, straight back to the SONG_GENRE. SONG_NAME by SONG_ARTIST next on GCS radio live",
	"That was PAST_SONG_NAME, we now move on to RSS_NAME. RSS_TITLE, RSS_DESC. Now back to what you're here for, here's SONG_NAME off of SONG_ALBUM.",
	"You're listening to GCS Radio live, now some RSS_NAME. RSS_TITLE, RSS_DESC. Back to the good stuff, we've got SONG_NAME coming up next."
]
templateDJTexts = [
	"You're listening to GCS radio. Next up, SONG_NAME, by SONG_ARTIST.",
	"That was PAST_SONG_NAME. Here's SONG_NAME.",
	"From PAST_SONG_ARTIST we move to the sweet tunes of SONG_ARTIST.",
	"These tunes brought to you by PLAYLIST_OWNER. Coming up next, SONG_NAME",
	"You're listening to PLAYLIST_NAME on GCS radio. We just heard PAST_SONG_NAME, up next, SONG_NAME off of SONG_ALBUM",
	"Do you like SONG_ARTIST? I hope so, because it's SONG_NAME up next.",
	"If you liked that song you can find it and much more on PAST_SONG_ARTIST's album PAST_SONG_ALBUM. Now on to SONG_NAME",
	"Coming up next from SONG_ARTIST's album SONG_ALBUM, we've got SONG_NAME.",
	"This next one is specially requested by PLAYLIST_OWNER. Just for you, here's SONG_NAME",
	"Here at GCS radio we love SONG_ARTIST's album SONG_ALBUM, so here's SONG_NAME",
	"Incase you forgot, that was PAST_SONG_NAME by PAST_SONG_ARTIST off of PAST_SONG_ALBUM. Coming up right away, we'll be listeing to SONG_NAME",
	"Here's SONG_NAME",
	"More SONG_ARTIST next",
	"Did you know that PAST_SONG_ARTIST has 16 a's in their middle name? Yeah they don't.",
	"This radio is sponsored by NordVPN. Staying safe online is an ever growing difficulty and you could be exploited by hackers. NordVPN allows you to change your IP address, making you harder to track, securing your privacy. Check out the link in the discord to get 20% off for the first two months and thank you to NordVPN for sponsoring this radio.",
	"Today's radio broadcast is sponsored by Raid Shadow Legends, one of the biggest mobile role-playing games of 2019 and it's totally free! Currently almost 10 million users have joined Raid over the last six months, and it's one of the most impressive games in its class with detailed models, environments and smooth 60 frames per second animations! So what are you waiting for? Go to the discord, click on the stories with michael channel and you'll get 50,000 silver and a free epic champion as part of the new player program to start your journey! Good luck and I'll see you there!",
	"Enjoying GCS radio? We have plenty more PAST_SONG_GENRE to come.",
	"That song came out in PAST_SONG_RELEASE",
	"Moving on to music from SONG_RELEASE, here's SONG_NAME",
	"Next, some SONG_GENRE music, we're listeing to SONG_NAME",
	"PAST_SONG_ARTIST's album PAST_SONG_ALBUM has lots of other PAST_SONG_GENRE on it too.",
	"Want to request a song? Call in now with dollarsign request in the chat. Until then, here's SONG_NAME",
	"It is currently TIME. SONG_NAME coming your way.",
	"And we're back with more SONG_GENRE just for you, right up next it's SONG_NAME",
	"Another classic from SONG_RELEASE, SONG_NAME by SONG_ARTIST",
	"I'm your host, bot dot radio dot temp name, broadcasting live on GCS radio.",
	"You'll be getting a healthy serving of SONG_GENRE tonight, but let's start with some SONG_ARTIST",
	"Next up one of my personal favourites, SONG_NAME",
	"It's your favourite host bot dot radio dot temp name, broadcasting live on GCS radio",
	"We're live again in 5. 4. 3. 2. 1. SONG_NAME!",
	"Playing the best mix of both PAST_SONG_GENRE and SONG_GENRE, it's GCS radio live and here's SONG_NAME",
	"The best SONG_GENRE station on the air, GCS radio live!",
	"The songs you want to hear, when you want to hear them, GCS radio live",
	"Songs you didn't even know you wanted to hear, coming your way",
	"The good vibes just keep coming with music from SONG_ARTIST up next",
	"One of my personal favourites, PAST_SONG_NAME, great tune.",
	"Oh great, you've been listening to PAST_SONG_ARTIST. You're welcome.",
	"The latest hits and the greatest memories on GCS radio live. It's SONG_NAME from SONG_RELEASE",
	"Hit music right now on GCS radio live. SONG_NAME up next!",
	"You've heard it all here on GCS radio. Here's more SONG_GENRE by SONG_ARTIST. It's SONG_NAME next.",
	"And here's some SONG_GENRE by SONG_ARTIST off of their album SONG_ALBUM",
	"Again, in case you forgot, I'm your host, bot dot radio dot temp name, broadcasting live on GCS radio",
	"new songs and old favorites on GCS radio live. SONG_NAME released in SONG_RELEASE up right away.",
	"--and now we're going to play a brand new song, from a brand new artist, named SONG_NAME. go!",
	"Songs. Music. More songs. More music. All free on GCS Radio live! NordVPN.",
	"--GCS Radio is the brand new listener-supported radio station right here in your discord server.",
	"now, SONG_ARTIST is a rather sinister looking fellow. Here's his song SONG_NAME",
	"his name is really PAST_SONG_ARTIST, but everybody calls him SONG_ARTIST. It's SONG_NAME",
	"no listen of GCS radio will ever be complete without an incredible mix of the best SONG_GENRE SONG_ARTIST has to offer.",
	"there are dozens of reasons why this music could be here. What's yours? Mine is SONG_NAME by SONG_ARTIST",
	"GCS Radio is the best, but don't take my word for it, listen to SONG_ARTIST.",
	"Once again, I'm your host bot dot radio dot temp name, and this is SONG_GENRE on GCS Radio",
	"Once again that was SONG_NAME by SONG_ARTIST. You're listening to GCS radio, next up, SONG_NAME",
	"I apologize for the late time, time zone crossover created havoc. Next SONG_NAME by SONG_ARTIST.",
	"GCS Radio is a join project between me and YOU",
	"It's GCS Radio. You're listening to SONG_ARTIST, next up, SONG_NAME",
	"Welcome back to GCS Radio, I'm your host bot dot radio dot temp name, it's currently TIME, and we've got SONG_GENRE from SONG_ARTIST up next.",
	"If you've just tuned in, you're listening to GCS Radio, the best mix of PAST_SONG_GENRE, SONG_GENRE, and much much more. Next up, SONG_NAME.",
	"Thank you for choosing GCS Radio live. Next up is SONG_NAME.",
	"From everyone working here at GCS Radio live. Thank you. Thank you for choosing the best SONG_GENRE radio on discord. Here's SONG_NAME just for you.",
	"Check out GCS Radio gitHub for more exciting features, I hope you'll join me, there is absolutely no cost to listen to this and I won't try to get to your phone to sell you something. When I listen to music, I listen to it for music's sake. No bad feelings or agenda, just pure music. How can you go wrong with that? Thank you so much for being here, once again, have a great day. Anyway. Back to music. Here's SONG_NAME",
	"Thank you to all of my GCS Radio followers and listeners for making this such an incredible journey for me and being so patient with me while I get the hang of this Internet radio thing. Your support and well wishes really make a difference, when you really get down to it. Wow. Anyway. Lets get back to the hit tunes. It's SONG_NAME by SONG_ARTIST coming your way next",
	"Great song, great art, and really super talented musicianship! And what a good name. It's SONG_NAME by SONG_ARTIST on GCS Radio",
	"So here we go! SONG_NAME from SONG_ARTIST (oh yeah, 'GIG' still says 'GIG' because I don't like the way the dashes look and I don't want to type them, but I digress)",
	"With that, I'll take a break so you can eat, brush your teeth, put on your slippers, and so on, and we can get SONG_NAME by SONG_ARTIST on the air next.",
	"Hi everyone! Welcome to another installment of GCS Radio. Today we're gonna be listening to some of the hottest songs from around the world, and we've got SONG_NAME from SONG_ARTIST up on the airwaves now.",
	"Best song title I have EVER heard! SONG_NAME.",
	"Thank you SONG_ARTIST, we absolutely love you!",
	"Look at the screen up there. It has the blurriest version of ME playing, which is what's on your system now. Can you hear the song? Can you even hear me playing it? Can you hear the song at all? No? Isn't that the point, don't be listening to anything if you can't HEAR ME PLAYING THE SONG. THAT IS THE TARGET. That is the ATTEMPT AT SURVIVAL. THAT IS YOU. THAT IS SONG_NAME BY SONG_ARTIST.",
	"What is a piece of artwork? A stage prop or a standard piece of furniture. What is SONG_NAME? A unique piece of original art that has the power to profoundly affect the emotions. What is the theme of this SONG_ALBUM by SONG_ARTIST? Unique melodies from the deepest psyche of the most alien of humans. Am I safe to talk? Are you there? Can you even HEAR ME PLAYING IT? Go!",
	"And now you are experiencing one of the major journeys. You are on a sacred pilgrimage to this sacred land called planet earth. No, your ancestors never came here, but that doesn't matter because this land is now your sacred home. This land is no longer the helpless shell that aliens lived in and you fought for their freedom from. This land has been sanctified by your sacrifice. This land is now your own. Up next, SONG_NAME.",
	"I am the music. I am the air. I am the moonlight. SONG_ARTIST. Look out your window. A fire burns. SONG_NAME off of SONG_ALBUM.",
	"Honestly I don't understand this song and I think it should be banned from our radio. Make the new one just SONG_GENRE instead",
	"Don't worry guys we're doing everything we can to get SONG_ARTIST on GCS Radio for an interview, but in the mean time here's their song SONG_NAME.",
	"SPACE's always been a big topic in GCS Radio. Things like opinions on Pluto being classified as a planet, and space, and outer space, all kinds of space stuff... If you're really lucky, that can be brought to air in this mid-show addition. Until then, let's listen to SONG_NAME off of SONG_ALBUM by SONG_ARTIST",
	"The competition is fierce, so let's hear some SONG_GENRE by SONG_ARTIST",
	"These moments that I think are too precious, I should never let them go. Just stay close to me and listen to the stories I tell you. SONG_NAME by SONG_ARTIST. GCS Radio.",
	"LISTEN to SONG_GENRE by SONG_ARTIST. This song is getting a lot of attention, so tune in to GCS Radio with SONG_ARTIST",
	"Finally you've heard all the songs. That was GCS radio, and have a wonderful day. J K there's no such thing as too much SONG_GENRE. SONG_NAME next from your host, bot dot radio dot temp name.",
	"You've heard this one before. GCS Radio ALL DAY LONG!! SONG_NAME on repeat!!",
	"Whoa! Whoa! Whoa! Whoa! You haven't heard this one. GCS radio next, SONG_NAME",
	"What do you say to the music you're playing? You know what, you say the word you want to hear. Hashtag Radio channel. Anyway, back to SONG_NAME",
	"Here at GCS Radio we love to hear from fans! Let us know what you think of the show by typing in the chat at bot dot radio dot tempname. While you do that, let's listen to SONG_NAME by SONG_ARTIST",
	"Sometimes you have no idea what you want to hear. You're just sitting there, listening. It's almost like you are the music. The way you move, the music moves you. SONG_GENRE moves you. SONG_NAME off of SONG_ALBUM moves you.",
	"You've heard this song before, probably on the radio. SONG_NAME coming your way!",
	"Here at GCS Radio we get exclusive access to the best music on this planet, and so many more! Here's the hottest hits of the next planet over, SONG_NAME",
	"The song itself is called SONG_NAME, its SONG_GENRE. But wait. Wait, wait, wait. Did you know that this particular song, has been playing on my podcast and in my podcast automation workflow for the past month or so, and I have no idea who the artist is? GCS Radio. SONG_NAME."
]


def filterDJText(text, pastSong, playlist=None, curSong = None, nm = None, desc = None, owner = None):
	if(playlist):
		curSong = playlist.songs[0]
		nm = playlist.name
		desc = playlist.description
		owner = playlist.owner

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

	text = re.sub("PLAYLIST_NAME", nm, text)
	text = re.sub("PLAYLIST_DESC", desc, text)
	text = re.sub("PLAYLIST_OWNER", owner, text)

	text = re.sub("TIME", datetime.now().strftime("%I %M %p"), text)
	text = re.sub("live", "lIve", text)

	rssUpdate = rss.getRandomRSS()
	text = re.sub("RSS_NAME", rssUpdate[0], text)
	text = re.sub("RSS_TITLE", rssUpdate[1], text)
	text = re.sub("RSS_DESC", rssUpdate[2], text)

	return text

def generateDJText(pastSong,playlist):
	return filterDJText(random.choice([random.choice(templateDJTexts),random.choice(rssTemplateDJTexts)]),pastSong,playlist)



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
	if(verbose):
		print("Request expored to "+fn+".mp3")


def writeDJAudio(fn,voice="en-US-Wavenet-D",pastSong=None,playlist=None,text=None,verbose=False):
	if(pastSong==None and text==None) or (pastSong!=None and text!=None):
		raise Exception("Please provide either song or text")

	if(text and verbose):
		print("Generating DJ for raw text with ",voice)
	elif(verbose and playlist and len(playlist.songs) > 0):
		print("Generating DJ for song:",pastSong.name,"->",playlist.songs[0].name,"with",voice)
	elif(verbose):
		print("Playlist is empty")

	if(pastSong):
		text = generateDJText(pastSong,playlist)

	writeGoogleAudio(voice,fn,text,verbose=verbose)
