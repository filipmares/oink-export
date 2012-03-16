import csv
import json
import logging
import urllib2
import sys
import getopt


def get_json_from_csv(filename, fieldnames):
	file_contents = open(filename, 'r')
	reader = csv.DictReader( file_contents, fieldnames = fieldnames)
	return json.loads(json.dumps( [ row for row in reader ]))

def is_same_item_and_place(rating, review):
	return review['foursquare'] == rating['foursquare'] and \
	review['name'] == rating['name'] and \
	review['foursquare'] != 'fsqr_id' and \
	review['foursquare']

def get_oinks_with_location(ratings, reviews):
	#merged entries with location info will be appended to this
	ratings_array = []	

	#find reviews and add them to the rating
	for rating in ratings:
		rating['review'] = None
		for review in reviews:
			if is_same_item_and_place(rating, review):
				rating['review'] = review['review']
				ratings_array.append(rating)

		if rating['foursquare'] and not rating['review'] and rating['foursquare'] != 'fsqr_id':
			ratings_array.append(rating)	

	return ratings_array

def get_oinks_with_location_information(oinks, foursquare_url):
	#add foursqare data to entires
	for oink in oinks:
		response = urllib2.urlopen(foursquare_url)
		response_json = json.loads(response.read())

		location = response_json['response']['venue']['location']
		
		oink['place'] = response_json['response']['venue']['name']
		print 'Getting foursquare info for ' + oink['place']

		try:
			oink['address'] = location['address']
		except:
			logging.info('no address')
		try:	
			oink['lat'] = location['lat']
			oink['lng'] = location['lng']
		except:
			logging.info('no lat lng')
		
		try: 
			oink['postalCode'] = location['postalCode']
		except:
			logging.info('no postal code')

		try:	
			oink['city'] = location['city']
		except:
			logging.info('no city')
		try:
			oink['state'] = location['state']
		except:
			logging.info('no state')

		try:
			oink['country'] = location['country']
		except:
			logging.info('no country')

	return oinks

def export(argv=None):

	if argv == None:
		try:
			argv = sys.argv[1:]
		except:
			return "No arguments given"
	else:
		argv = argv.split()

	try:
		opts, args = getopt.getopt(argv, "", ["token="])
		
		for opt, arg in opts:
			if opt == '--token':
				URL = 'https://api.foursquare.com/v2/venues/'
				OAUTH = '?oauth_token=' + arg
	except:
		return 'No token found'
		
	#get and convert items added
	items_added_json = get_json_from_csv('items_added.csv', ( "id","name","love","like", "ho_hum", "dislike", "tags", "place", "foursquare" ))

	#get and convert ratings
	ratings_json = get_json_from_csv('ratings.csv', ( "rating", "name", "place", "foursquare" ))

	#get and convert reviews
	reviews_json = get_json_from_csv('reviews.csv', ( "review", "review_likes", "name", "place", "foursquare" ) )

	#get the reviews with location
	oinks_with_location = get_oinks_with_location(ratings_json, reviews_json)

	foursquare_url = URL + oink['foursquare'] + OAUTH
	oinks_with_location_information = get_oinks_with_location_information(oinks_with_location, foursquare_url)

	#write JSON to file
	FILE = open("oink_export.json","w")
	FILE.writelines(json.dumps(oinks_with_location_information, sort_keys = True, indent = 4 ))
	FILE.close()


if __name__ == '__main__':
	sys.exit(export())
