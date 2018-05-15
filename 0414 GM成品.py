
# coding: utf-8

# In[1]:

# 多地點地圖顯示

from urllib.parse import quote
import urllib.request
import json, string
    
endpoint = "https://maps.googleapis.com/maps/api/staticmap?"
GM_API_KEY = 'AIzaSyA35lPzOmBYaGtsGnu1BtuZiWqZcLpYdQk'

# G_center = center.replace(' ', '+')

num = int(input("請輸入地點數量"))

if num >= 1:
    
#     G_zoom = "16"
#     G_size = "250x250"
    G_size = "1000x1000"
    nav_request = 'size={}'.format(G_size)
#     nav_request = 'zoom={}&size={}'.format(G_zoom, G_size)
#     nav_request = ""
    
    for i in range(0,num):
        G_center = input('請輸入查詢位置').replace(' ', '+')
        G_MarkerLabel = str(i + 1) + "%7C"
#         G_markers = "size:tiny%7c" + "color:red%7C"+ "label:" + G_MarkerLabel + G_center
        G_markers = "size:big%7ccolor:red%7C"+ "label:" + G_MarkerLabel + "%7C" + G_center
        nav = '&markers={}'.format(G_markers)
        nav_request = nav_request + nav
    
    nav_request = nav_request + '&key=' + GM_API_KEY

request_trans = urllib.parse.quote(nav_request, safe = string.printable)    
G_request = endpoint + request_trans
print (G_request)


# In[ ]:

# 雷達搜尋（多點地點）
# 搜尋結果須結合ＩＤ轉換

from urllib.parse import quote
import urllib.request
import json, string


GM_API_KEY = 'AIzaSyA35lPzOmBYaGtsGnu1BtuZiWqZcLpYdQk'

G_query = input("請輸入地點").replace(' ', '+')
G_language = 'zh-TW'


id_nav_request = 'query={}&key={}'.format(G_query, GM_API_KEY)
# id_nav_request = 'query={}&language={}&key={}'.format(G_query, G_language, GM_API_KEY)
id_request = "https://maps.googleapis.com/maps/api/place/textsearch/json?" + id_nav_request
 
request_trans = urllib.parse.quote(id_request, safe = string.printable)

print(id_request)
print(request_trans)

respone = urllib.request.urlopen(request_trans).read()
id_directions = json.loads(respone.decode('utf-8'))

print(id_directions)

id_results = id_directions['results']
geometry = id_results[0]['geometry']
location = geometry['location']
place = [location['lat'], location['lng']]
print(place)

### rada search

rada_location = str(place[0]) + ',' + str(place[1])
radius = 1000
rada_keyword = input("請輸入地點").replace(' ', '+')

rada_nav_request = 'location={}&radius={}&keyword={}&key={}'.format(rada_location, radius, rada_keyword, GM_API_KEY)
rada_request = "https://maps.googleapis.com/maps/api/place/radarsearch/json?" + rada_nav_request

rada_request_trans = urllib.parse.quote(rada_request, safe = string.printable)

# print(rada_request)
# print(rada_request_trans)



respone = urllib.request.urlopen(rada_request_trans).read()
rada_directions = json.loads(respone.decode('utf-8'))
print(rada_directions['results'][key])


# In[3]:

# ＩＤ轉換

from urllib.parse import quote
import urllib.request
import json, string


GM_API_KEY = 'AIzaSyA35lPzOmBYaGtsGnu1BtuZiWqZcLpYdQk'

# G_query = input("請輸入地點").replace(' ', '+')
G_language = 'zh-TW'


# id_nav_request = 'query={}&key={}'.format(G_query, GM_API_KEY)
# # id_nav_request = 'query={}&language={}&key={}'.format(G_query, G_language, GM_API_KEY)
# id_request = "https://maps.googleapis.com/maps/api/place/textsearch/json?" + id_nav_request
 
# request_trans = urllib.parse.quote(id_request, safe = string.printable)

# print(id_request)
# print(request_trans)

# respone = urllib.request.urlopen(request_trans).read()
# id_directions = json.loads(respone.decode('utf-8'))

# id_results = id_directions['results']
# place_id = id_results[0]['place_id']

### detail search

p_id = input("ID：")
dt_nav_request = 'placeid={}&language={}&key={}'.format(p_id, G_language, GM_API_KEY)
# dt_nav_request = 'placeid={}&language={}&key={}'.format(place_id, G_language, GM_API_KEY)
dt_request = "https://maps.googleapis.com/maps/api/place/details/json?" + dt_nav_request


respone = urllib.request.urlopen(dt_request).read()
dt_directions = json.loads(respone.decode('utf-8'))

result = dt_directions['result']
# google可抓取類別：名稱(0)、電話(1)、地址(2)、營業時間(3)、評價(4)、網站(5)、googlemap頁面(6)

P_name = result['name']

if 'formatted_phone_number' in result :
    P_phone = result['formatted_phone_number']
else :
    P_phone = '您所查詢的地點暫無電話資訊！'

if 'formatted_address' in result :
    P_address = result['formatted_address']
else :
    P_address = '您所查詢的地點暫無地址資訊！'

# 營業時間回傳值為list
if 'opening_hours' in result :
    P_time = ''
    for i in range(0,7):
        P_time += result['opening_hours']['weekday_text'][i] + '\n'
else :
    P_time = '您所查詢的地點暫無營業時間資訊！'
    
if 'rating' in result :
    P_grade = str(result['rating'])
else :
    P_grade = '您所查詢的地點暫無評價資訊！'

if 'website' in result :
    P_web = result['website']
else :
    P_web = '您所查詢的地點暫無網站資訊！'

P_GMweb = result['url']

response = [ P_name, P_phone, P_address, P_time, P_grade, P_web, P_GMweb ]

print(response)

