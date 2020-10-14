import re
from importlib import util
import json
import sys, os


#Relative path to this file
PREFIX_PATH = sys.path[0]

def importSrcFile(fn):
	'''
	input: path from src/ of file
	returns: import object of the file
	'''
	spec = util.spec_from_file_location(fn, PREFIX_PATH+"/"+fn)
	getModule = util.module_from_spec(spec)
	spec.loader.exec_module(getModule)
	return getModule

#check for audioCache dir
if not os.path.isdir(PREFIX_PATH+"/../audioCache"):
	os.mkdir(PREFIX_PATH+"/../audioCache")

#Export google cloud API Key path variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = PREFIX_PATH+"/auth/google-cloud.json"

#Import spotifyConnection object
spotifyConnection = importSrcFile("spotifyConnection.py").spotifyConnection

#Import playlist object
importData = importSrcFile("playlist.py")
playlist = importData.playlist
song = importData.song

#Import discord bot
discordClient = importSrcFile("discordBot.py")
BotClient = discordClient.MyClient()
BotClient.run(discordClient.token())
