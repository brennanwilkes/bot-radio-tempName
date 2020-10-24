import os, sys, glob, random
import dj
from globalSingleton import *

from song import Song
from requireHeaders import PREFIX_PATH, commaSeparator
MAIN_PATH = PREFIX_PATH+"/.."


class Playlist:

	songs = []
	collaborative = False
	description = ""
	name = ""
	owner = ""

	def __init__(self, playlistJSON):

		self.collaborative = playlistJSON["collaborative"]
		self.description = playlistJSON["description"]
		self.name = playlistJSON["name"]
		self.owner = playlistJSON["owner"]["display_name"]

		self.songs = []
		for songJSON in playlistJSON["tracks"]["items"]:
			self.songs.append(Song(songJSON["track"]))
		self.currentSong = None

	def insertSong(self,newSong,message,voice,fn,verbose=False):
		self.songs.insert(0,newSong)
		self.prepareNextSongs(1,verbose=verbose,override=True)
		if(verbose):
			print("Preparing DJ request audio for "+self.currentSong.name+" -> "+newSong.name)
		dj.writeDJRequestAudio(self.currentSong.fileName+"-dj-"+newSong.youtubeID,newSong,message,voice=voice,verbose=verbose)


	def prepareNextSongs(self, num=1, verbose=False, override=False, voice="en-AU-Wavenet-B",welcome=False, prevFn=None):
		if((not prevFn) and (self.currentSong != None)):
			prevFn = self.currentSong.fileName

		for i in range(min(len(self.songs),num)):
			if(verbose): print("Preparing "+str(i+1)+"/"+str(min(len(self.songs),num)))
			if(i >= len(self.songs)):
				break

			suc = self.songs[i].prepare(verbose=verbose, override=override)
			if(suc):
				if (i==0 and welcome):
					djFn = self.songs[i].fileName+"-welcome-dj"
				else:
					if(prevFn and i==0):
						djFn = prevFn+"-dj-"+self.songs[i].youtubeID
					else:
						djFn = self.songs[i-1].fileName+"-dj-"+self.songs[i].youtubeID

				if override or not glob.glob(djFn+".*"):
					if(i == 0 and welcome):
						if(verbose):
							print("Preparing DJ welcome audio")
						text = dj.getWelcomeText(self)
					else:
						if(verbose):
							print("Preparing DJ audio for "+self.songs[i-1].name+" -> "+self.songs[i].name)
						text = dj.filterDJText(random.choice(dj.templateDJTexts), self.songs[i-1], curSong = self.songs[i], nm = self.name, desc = self.description, owner = self.owner)
					dj.writeGoogleAudio(voice,djFn,text,verbose=verbose)

			else:
				self.songs.pop(i)

	def getNextSong(self,remove=True):
		if(not remove):
			return self.songs[0]

		self.currentSong = self.songs[0]
		return self.songs.pop(0)
