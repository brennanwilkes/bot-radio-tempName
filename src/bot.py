import re
import importlib

#Relative path to this file
PREFIX_PATH = re.compile("(.*)/[^/]*").match("./"+__file__).group(1)

#Import spotifyConnection object
spec = importlib.util.spec_from_file_location("spotifyConnection.py", PREFIX_PATH+"/spotifyConnection.py")
getModule = importlib.util.module_from_spec(spec)
spec.loader.exec_module(getModule)
spotifyConnection = getModule.spotifyConnection








test = spotifyConnection()
q = test.loadPlaylist("https://open.spotify.com/playlist/0NkBcnxyLMeUXKXww80lFV?si=okRaEV_wTnqJnMbmQEBrXA")
test.printPlaylist(q)
