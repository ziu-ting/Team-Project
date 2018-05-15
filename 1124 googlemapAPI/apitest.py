# Traditional Video -> http://youtu.be/UrrWxyq1Z48
# Directions API Test
# Driving

import urllib.request
import json

endpoint = 'https://maps.googleapis.com/maps/api/directions/json?'
API_KEY = 'AIzaSyA35lPzOmBYaGtsGnu1BtuZiWqZcLpYdQk' 

origin = input('Where are you ? ').replace(' ', '+')
destination = input('Where do you want to go ? ').replace(' ', '+')

nav_request = 'origin={}&destination={}&key={}'.format(origin, destination, API_KEY)
request = endpoint + nav_request
respone = urllib.request.urlopen(request).read()

directions = json.loads(respone.decode('utf-8'))
# print (directions)

# directions.keys()
routes = directions['routes']
##legs->walking distance ; summary->how far?
# routes[0].keys()
# routes[0]['legs']
legs = routes[0]['legs']
# len(legs)
# legs[0]['distance']['text']

print ('This distance between " ' + legs[0]['start_address'] + ' " and " ' + legs[0]['end_address'] + ' " is ' + legs[0]['distance']['text'] + ' , and it will take you ' + legs[0]['duration']['text'] + " .")