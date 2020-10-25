import feedparser, random, re

class RSSFeed:
	def __init__(self,name,url):
		self.name = name
		self.url = url
	def get(self,upTo=5):
		feed = feedparser.parse(self.url)
		entry = random.choice(feed.entries[:upTo])
		return [self.name,
			re.sub('<[^<]+?>', '', entry["title"]).replace("\n"," "),
			re.sub('<[^<]+?>', '', entry["summary"]).replace("\n"," "),
			re.sub('<[^<]+?>', '', entry["published"]).replace("\n"," ")]
	def debug(self):
		return(feedparser.parse(self.url).entries[0])


bbcN = RSSFeed("BBC News","http://feeds.bbci.co.uk/news/world/rss.xml")
bbcS = RSSFeed("BBC Sports","https://feeds.bbci.co.uk/sport/rss.xml")
bbcB = RSSFeed("BBC Business","http://feeds.bbci.co.uk/news/business/rss.xml")
bbcT = RSSFeed("BBC Technology","http://feeds.bbci.co.uk/news/technology/rss.xml")
bbcA = RSSFeed("BBC Arts","http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml")
weather = RSSFeed("Vancouver Weather","https://weather.gc.ca/rss/city/bc-74_e.xml")
ctv = RSSFeed("CTV News","https://bc.ctvnews.ca/rss/ctv-news-vancouver-1.822352")
traffic = RSSFeed("Vancouver Traffic","https://www.drivebc.ca/api/events/region/mainland?format=rss")

def getRandomRSS():
	return random.choice([
		random.choice([bbcN,bbcS,bbcB,bbcT,bbcA]),
		weather,
		ctv,
		traffic]).get()
