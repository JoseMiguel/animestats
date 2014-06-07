class Anime:
	rank = None
	name = None
	year = None
	url = None
	rating = None
	def __init__(self,rank,name,rating,url):
		self.rank = int(rank)
		self.name = str(name)
		self.rating = float(rating)
		self.url = str(url)
