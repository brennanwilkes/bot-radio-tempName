import re
from importlib import util
import json
import sys


#Relative path to this file
PREFIX_PATH = sys.path[0]

def importSrcFile(fn):
	spec = util.spec_from_file_location(fn, PREFIX_PATH+"/"+fn)
	getModule = util.module_from_spec(spec)
	spec.loader.exec_module(getModule)
	return getModule


#Import spotifyConnection object
spotifyConnection = importSrcFile("spotifyConnection.py").spotifyConnection

#Import playlist object
importData = importSrcFile("playlist.py")
playlist = importData.playlist
song = importData.song







test = spotifyConnection()
q = test.loadPlaylist("https://open.spotify.com/playlist/0NkBcnxyLMeUXKXww80lFV?si=okRaEV_wTnqJnMbmQEBrXA")

p = playlist(q)

print(p.name)
print(p.owner)

for s in p.songs:
	print(s.name)

#print(json.dumps(q, indent=4))
#test.printPlaylist(q)
