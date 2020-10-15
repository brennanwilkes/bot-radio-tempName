import os

from requireHeaders import PREFIX_PATH, requireFile
from discordBot import DiscordClient

#check for audioCache dir
if not os.path.isdir(PREFIX_PATH+"/../audioCache"):
	os.mkdir(PREFIX_PATH+"/../audioCache")

#Export google cloud API Key path variable
requireFile("google-cloud.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = PREFIX_PATH+"/auth/google-cloud.json"


botClient = DiscordClient()
botClient.verbose = False
botClient.run(requireFile("discordToken"))
