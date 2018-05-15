
# coding: utf-8

# In[ ]:

import json
import datetime
import requests

link = 'https://tw.news.yahoo.com/%E7%8B%A0%E5%BF%83%E6%AF%8D%E6%82%B6%E6%AD%BB3%E5%AC%B0%E5%85%92-%E8%97%8F%E5%B1%8D%E5%86%B0%E7%AE%B119%E5%B9%B4%E4%B9%85-033047080.html'

r = requests.get(link)

string = r.text

start = string.find('"publishDate":') + 15

# print(len('"publishDate":"'))

end = string.find('",', start)

string = string[start:end]

string = string.split(', ')[1]

print(string)

dt = datetime.datetime.strptime(string, "%d %m %Y %H:%M:%S GMT")

dt += datetime.timedelta(hours=8)

print(dt)


# In[ ]:



