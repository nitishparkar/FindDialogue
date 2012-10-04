from google.appengine.ext import db


class  BBTIndex(db.Model):
	"""
	Maps words to a list of occurrences => [season, episode, line]
	Words serve as Key Name
	"""
	occurrences = db.TextProperty(required=True)


class BigBangTheory(db.Model):
	"""
	Contains transcripts
	Key Name = str(season) + str(episode) 
	"""
	title = db.StringProperty(required=True)
	transcript = db.TextProperty(required=True)
