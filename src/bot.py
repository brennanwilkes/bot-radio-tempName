import re
from importlib import util
import json


#Relative path to this file
PREFIX_PATH = re.compile("(.*)/[^/]*").match("./"+__file__).group(1)

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

#p.updateYoutubeIDs(True)
for s in p.songs:
	s.downloadAudio()



#print(p.name)
#print(p.owner)



#print(json.dumps(p.songs[0].getYoutubeSearch(),indent=4))

#print(p.songs[0].duration)

#print(json.dumps(q["tracks"]["items"][0], indent=4))
#test.printPlaylist(q)
