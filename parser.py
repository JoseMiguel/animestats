from anime import Anime
import urllib.request
from bs4 import BeautifulSoup
from collections import defaultdict

class AnimeParser:
	def __init__(self):
		self.ann_base_url = "http://www.animenewsnetwork.com"
		self.ann_rank_url = "http://www.animenewsnetwork.com/encyclopedia/ratings-anime.php?top50=best_bayesian&n=1000"

	def getAllRank(self):
		html = urllib.request.urlopen(self.ann_rank_url)
		soupRank = BeautifulSoup(html)
		animeList = []
		for tr in soupRank.findAll('tr', {"bgcolor":"#EEEEEE"}):
			(rank,name,rating,_) = map( lambda w: w.contents[0], tr.findAll('td'))
			soupName = BeautifulSoup(str(name))
			name = name.text
			url = (soupName.find('a',href=True)['href'])
			animeList.append(Anime(rank,name,rating, self.ann_base_url + url))
		
		return animeList

	def getAnimeDate(self,anime):
		html = urllib.request.urlopen(anime.url)
		soup = BeautifulSoup(html)
		vintageDiv = soup.find('div',{'id':'infotype-7'})
		if ( vintageDiv.find('div') != None ):
			date = str(vintageDiv.find('div').text)
		else:
			date = str(vintageDiv.find('span').text)

		anime.year = int(date[:4])
		
def run():
	ap = AnimeParser()
	animeList = ap.getAllRank()
	for anime in animeList:
		ap.getAnimeDate(anime)
		print(anime.name,anime.year)

	bucket = defaultdict(list)
	for x in animeList:
		bucket[x.year].append(x)

	for year, animes in bucket.items():
		filePerYear = open(str(year)+".csv", 'w')
		filePerYear.write("Rank,Name,URL\n")
		for anime in animes:
			filePerYear.write(str(anime.rank) + "," + anime.name+ "," + anime.url +"\n")

		filePerYear.close()

run()
