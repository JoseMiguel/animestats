from statistics import *
import urllib.request
from urllib.parse import urlparse
import operator
from anime import Anime
from bs4 import BeautifulSoup
from collections import defaultdict
import sys, getopt

class AnimeParser:
	def __init__(self):
		self.ann_base_url = "http://www.animenewsnetwork.com"
		self.ann_rank_url = "http://www.animenewsnetwork.com/encyclopedia/ratings-anime.php?top50=best_bayesian&n=500"
#		self.ann_preview = "https://www.animenewsnetwork.com/preview-guide/2014/summer/.76162"
#		self.ann_preview = "http://www.animenewsnetwork.com/preview-guide/2014/the-spring-anime"
		self.ann_preview = "http://www.animenewsnetwork.com/preview-guide/2014/fall/.79245"

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
		print('Recolecting reviews...')
		try:
			for tr in animeTable.findAll('td'):
				name = (tr.find('b').text)
				url =  str(tr.find('a',href=True)['href'])
				if url[0] != '/':
					url = '/' + url

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
					print('Adding:', name)
					newAnimes.append([mean(ratings),name,ratings])
					print('Counting:', len(newAnimes))
		except:
			pass

		fileReview = open('review.tsv','w')
		fileReview.write('nro\tmean\tname\tstd\n')
		index = 1
		for anime in newAnimes:
			ratings = anime[2]
			if len(ratings) >= 2:
				std = stdev(ratings)
			else:
				std = .0
			fileReview.write(str(index) + '\t' +str(anime[0]) +'\t'+ anime[1] + '\t'+  str(std) + '\n')
			index = index + 1
		fileReview.close()
		print("output: review.tsv")

def runRank(allRank):
	ap = AnimeParser()
	animeList = ap.getAllRank()

	fileSummary = open('summary.tsv','w')
	fileSummary.write("Nro\tName\tURL\n")
	index = 1
	for anime in animeList:
		fileSummary.write(str(index) + '\t' + anime.name+ "\t" + anime.url +"\n")
		index = index + 1

	print('ouput file: summary.tsv')
	fileSummary.close()
	print(allRank)
	if allRank:
		for anime in animeList:
			ap.getAnimeDate(anime)
		bucket = defaultdict(list)
		for x in animeList:
			bucket[x.year].append(x)

		for year, animes in bucket.items():
			filePerYear = open(str(year)+".tsv", 'w')
			filePerYear.write("Rank\tName\tURL\n")
			for anime in animes:
				filePerYear.write(str(anime.rank) + "\t" + anime.name+ "\t" + anime.url +"\n")

			filePerYear.close()

def runPreview():
	ap = AnimeParser()
	ap.getPreview()

def main(args):
	if len(args) > 1:
		if args[1] == 'review':
			runPreview()
		elif args[1] == 'ranking':
			if len(args) > 2:
				if args[2] == 'all':
					runRank(True)
			else:
				runRank(False)

	else:
		print('Need arguments: review or ranking')

if __name__ == "__main__":
   main(sys.argv)
