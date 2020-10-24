import os, json, glob

from requireHeaders import PREFIX_PATH, getTokenFromFile
from discordBot import DiscordClient
from station import Station
from globalSingleton import *
from spotifyConnection import SpotifyConnection

#check for audioCache dir
if not os.path.isdir(PREFIX_PATH+"/../audioCache"):
	os.mkdir(PREFIX_PATH+"/../audioCache")
else:
	filesToDelete = glob.glob(PREFIX_PATH+"/../audioCache/*-dj*") + glob.glob(PREFIX_PATH+"/../audioCache/*.NA") + glob.glob(PREFIX_PATH+"/../audioCache/*.part")
	for fn in filesToDelete:
		if os.path.isfile(fn):
			os.remove(fn)

#check for stations dir
if not os.path.isdir(PREFIX_PATH+"/../stations"):
	os.mkdir(PREFIX_PATH+"/../stations")
else:
	for filename in os.listdir(PREFIX_PATH+"/../stations/"):
		if filename.endswith(".json"):
			try:
				s = Station(loadFromFile=PREFIX_PATH+"/../stations/"+filename)
			except Exception as e:
				print(e)
			else:
				stations.append(s)



#Export google cloud API Key path variable
getTokenFromFile("google-cloud.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = PREFIX_PATH+"/auth/google-cloud.json"

#Create spotify singleton
spotifyConInstance.connect()

botClient = DiscordClient()
botClient.verbose = True
botClient.run(getTokenFromFile("discordToken"))
