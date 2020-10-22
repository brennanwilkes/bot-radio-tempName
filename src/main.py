import os

from requireHeaders import PREFIX_PATH, getTokenFromFile
from discordBot import DiscordClient
from globalSingleton import *
from spotifyConnection import SpotifyConnection

#check for audioCache dir
if not os.path.isdir(PREFIX_PATH+"/../audioCache"):
	os.mkdir(PREFIX_PATH+"/../audioCache")

#check for stations dir
if not os.path.isdir(PREFIX_PATH+"/../stations"):
	os.mkdir(PREFIX_PATH+"/../stations")

#Export google cloud API Key path variable
getTokenFromFile("google-cloud.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = PREFIX_PATH+"/auth/google-cloud.json"

#Create spotify singleton
spotifyConInstance.connect()

botClient = DiscordClient()
botClient.verbose = True
botClient.run(getTokenFromFile("discordToken"))
