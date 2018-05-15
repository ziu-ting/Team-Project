# Google Static Maps
# specific location
#https://maps.googleapis.com/maps/api/staticmap?parameters

import menu
import urllib.request

endpoint = "https://maps.googleapis.com/maps/api/staticmap?"
API_KEY = 'AIzaSyA35lPzOmBYaGtsGnu1BtuZiWqZcLpYdQk'

# G_center = input('Please input the map center :').replace(' ', '+')
center_input = menu.test
G_center = center_input.replace(' ', '+')

print(center_input)

G_zoom = "16"
G_size = "250x250"
G_markers = "color:red%7C"+ G_center


nav_request = 'center={}&zoom={}&size={}&markers={}&key={}'.format(G_center, G_zoom, G_size, G_markers, API_KEY)
G_request = endpoint + nav_request
# print(request)

# respone = urllib.request.urlopen(request).read()
