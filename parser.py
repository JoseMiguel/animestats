from statistics import *
import urllib.request
import operator
from anime import Anime
from bs4 import BeautifulSoup
from collections import defaultdict

class AnimeParser:
	def __init__(self):
		self.ann_base_url = "http://www.animenewsnetwork.com"
		self.ann_rank_url = "http://www.animenewsnetwork.com/encyclopedia/ratings-anime.php?top50=best_bayesian&n=1000"
		self.ann_preview = "http://www.animenewsnetwork.com/preview-guide/2014/the-spring-anime"

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
		if ( vintageDiv == None):
			anime.year = str('Unknown')
		elif( vintageDiv.find('div') != None ):
			date = str(vintageDiv.find('div').text)
			anime.year = int(date[:4])
		else:
			date = str(vintageDiv.find('span').text)
			anime.year = int(date[:4])

	def getPreview(self):
		html = urllib.request.urlopen(self.ann_preview)
		soup = BeautifulSoup(html)
		animeTable = soup.find('table')
		newAnimes = []
		for tr in animeTable.findAll('td'):
			name = (tr.find('b').text)
			url =  str(tr.find('a',href=True)['href'])
			html = urllib.request.urlopen(self.ann_base_url + url)
			review = BeautifulSoup(html)
			ratings = []
			for p in review.findAll('p'):
				ratingStr = p.text[:50]
				if ratingStr.find('Rating:') != -1:
					for t in ratingStr.split():
						try:
							ratings.append(float(t))
							break
						except:
							pass
			if ( ratings ):
				newAnimes.append([mean(ratings),name,ratings])

		sorted(newAnimes)
		for anime in newAnimes:
			ratings = anime[2]
			if len(ratings) >= 2:
				std = stdev(ratings)
			else:
				std = .0
			print(anime[0],'|', anime[1], std)
			

def runRank():
	ap = AnimeParser()
	animeList = ap.getAllRank()
	for anime in animeList:
		ap.getAnimeDate(anime)
		print(anime.name,anime.year)

	bucket = defaultdict(list)
	for x in animeList:
		bucket[x.year].append(x)

	for year, animes in bucket.items():
		filePerYear = open(str(year)+".tsv", 'w')
		filePerYear.write("Rank,Name,URL\n")
		for anime in animes:
			filePerYear.write(str(anime.rank) + "\t" + anime.name+ "\t" + anime.url +"\n")

		filePerYear.close()

def runPreview():
	ap = AnimeParser()
	ap.getPreview()


runPreview()
