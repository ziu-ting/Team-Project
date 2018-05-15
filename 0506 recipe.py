
# coding: utf-8

# In[ ]:

from bs4 import BeautifulSoup
from urllib.parse import quote
import requests, urllib, string, json
import pandas as pd

# # # 函數使用說明：
# 1.查詢店家在json檔內（已建檔）
# # Input:飲料 ；Output:「阿水的菜單」panda
# 2.查詢店家在菜單吧有資料 https://menubar.tw
# # Inpur:四季甜湯 ； Output:「四季甜湯的菜單」panda https://menubar.tw/menu/UBctmU4u1oPD
# 3.查詢店家無資料
# # Input:四季甜點 ； Output:「沒有結果喔」string
# # # 若菜單吧的商品簡介包含字串 會顯示有結果(2) 須注意例外處理(ex:你好)


def recipe_query(restaurant):
    with open(r'D:\Moyege\Work\@PROJECT\1221Google_map\chatbot\chatbot\Scripts\testbot\GooglemapBot\jsondata\menu.json', 'r', encoding="utf-8") as f:
        menudata = json.load(f)

    jsonlong = len(menudata)

    restaurant_query = 'q={}'.format(restaurant.replace(' ', '+'))
    query_url = 'https://menubar.tw/search?' + urllib.parse.quote(restaurant_query, safe = string.printable)
    
    storecount = 0
    for i in range(jsonlong):
        menu_string = ''
        if restaurant == menudata[i]['StoreName'] or restaurant == menudata[i]['StoreType']:
            menu_json_df = pd.DataFrame(menudata[0]['Menu'], columns=['name', 'price', 'notes'])
            storecount += 1

    if storecount ==0:

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7,zh-CN;q=0.6,ja;q=0.5',
            'Connection': 'keep-alive',
            'Cookie': 'connect.sid=s%3A7DMyh3BHjlt-NyrewTnZSYKQX7nA40Bp.kGy3QL9WN1h0aNdh95jenBbLDM6YmUg8l6h9ZlchP7g; _ga=GA1.2.2000943914.1524469648; _gid=GA1.2.1645056648.1524469648',
            'Host': 'menubar.tw',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }

        origin_res = requests.get(query_url, headers = headers)
        origin_soup = BeautifulSoup(origin_res.text, 'html.parser')


        if restaurant =="你好" or origin_soup.select('li.breadcrumb-item.active')[0].select('b')[0].text == str(0):
            warntext = "沒有結果喔"
            return warntext
        else:
            links =  [a.attrs.get('href') for a in origin_soup.select('div.card-body')[1].select('h4')[0].select('a')]

            menu_links = 'https://menubar.tw' + str(links).strip("'[]'")

            print(menu_links)

            res = requests.get(menu_links, headers = headers)
            soup = BeautifulSoup(res.text, 'html.parser')

            name = []
            price = []
            td_count = 1
            for i in soup.select('table')[1].select('tr'):
                if i.select('td') != '': 
                    for k in i.select('td'):
                        if td_count%2 ==1:
                            name.append(k.text.strip(" \n"))
                        else:
                            price.append(k.text.strip(" \n"))
                        td_count +=1

            menu_dict = { "name": name, "price & note" : price}
            menu_query_df =  pd.DataFrame(menu_dict, columns=['name', 'price & note'])
    
            return menu_query_df
    else:
        return menu_json_df


q = input()
recipe_query(q)


# In[ ]:



