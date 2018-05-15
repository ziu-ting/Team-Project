
# coding: utf-8

# In[2]:

import urllib, string, json
from urllib.parse import quote


def GMap_placeid(store_id):
    GM_API_KEY = 'AIzaSyA35lPzOmBYaGtsGnu1BtuZiWqZcLpYdQk'
    G_language = 'zh-TW'

    dt_nav_request = 'placeid={}&language={}&key={}'.format(store_id, G_language, GM_API_KEY)
    dt_request = "https://maps.googleapis.com/maps/api/place/details/json?" + dt_nav_request
    dt_request_trans = urllib.parse.quote(dt_request, safe = string.printable)
    respone = urllib.request.urlopen(dt_request_trans).read()
    
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

    id_response = [ P_name, P_phone, P_address, P_time, P_grade, P_web, P_GMweb]

    return id_response


def GMap_place_detailssearch(center):
    ### id search
    GM_API_KEY = 'AIzaSyA35lPzOmBYaGtsGnu1BtuZiWqZcLpYdQk'

    G_query = center.replace(' ', '+')
    G_language = 'zh-TW'

    id_nav_request = 'query={}&language={}&key={}'.format(G_query, G_language, GM_API_KEY)
    id_request = "https://maps.googleapis.com/maps/api/place/textsearch/json?" + id_nav_request

    # url中不可包含中文等無法處理之字→需轉換成「%XX」
    # urllib.parse.quote(string, safe='/', encoding=None, errors=None)
    # https://www.zhihu.com/question/22899135       https://docs.python.org/3/library/urllib.parse.html#url-quoting。    
    request_trans = urllib.parse.quote(id_request, safe = string.printable)
    respone = urllib.request.urlopen(request_trans).read()
    id_directions = json.loads(respone.decode('utf-8'))

    id_results = id_directions['results']

    if len(id_results) != 0 :

        # 回傳地點經緯度
        geometry = id_results[0]['geometry']
        location = geometry['location']
        place = [location['lat'], location['lng']]

        # 回復地點ID
        place_id = id_results[0]['place_id']

        dt_nav_request = 'placeid={}&language={}&key={}'.format(place_id, G_language, GM_API_KEY)
        dt_request = "https://maps.googleapis.com/maps/api/place/details/json?" + dt_nav_request
        dt_request_trans = urllib.parse.quote(dt_request, safe = string.printable)
        
        respone = urllib.request.urlopen(dt_request_trans).read()
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

        response = [ P_name, P_phone, P_address, P_time, P_grade, P_web, P_GMweb , place]
        
        return response

    else:
        user = input("請選取你所在的位置")
        user_location = GMap_place_detailssearch(user)[7]
        ### rada search

        rada_location = str(user_location[0]) + ',' + str(user_location[1])
        radius = 500

        rada_nav_request = 'location={}&radius={}&keyword={}&key={}'.format(rada_location, radius,  G_query, GM_API_KEY)
        rada_request = "https://maps.googleapis.com/maps/api/place/radarsearch/json?" + rada_nav_request

        rada_request_trans = urllib.parse.quote(rada_request, safe = string.printable)
        respone = urllib.request.urlopen(rada_request_trans).read()
        rada_directions = json.loads(respone.decode('utf-8'))
        
        if len(rada_directions['results']) == 0:
            warntext = "您所在的區域附近500公尺內暫時沒有你想搜尋的店家喔"
            return warntext
        else:
            query_long = len(rada_directions['results'])
            if len(rada_directions['results']) > 5:
                query_long = 5
            T_name = ''
            T_phone = ''
            T_address = ''
            T_time = ''
            T_grade = ''
            T_web = ''
            T_GMweb = ''

            for i in range(query_long):
                store_id = rada_directions['results'][i]['place_id']
                T_name += str(GMap_placeid(store_id)[0]) + '\n'
                T_phone += str(GMap_placeid(store_id)[0]) + "的電話為：" + str(GMap_placeid(store_id)[1]) + '\n'
                T_address += str(GMap_placeid(store_id)[0]) + "的地址為：" + str(GMap_placeid(store_id)[2]) + '\n'
                T_time += str(GMap_placeid(store_id)[0]) + "的營業時間為：\n" + str(GMap_placeid(store_id)[3]) + '\n'
                T_grade += str(GMap_placeid(store_id)[0]) + "的評分為：" + str(GMap_placeid(store_id)[4]) + '\n'
                T_web += str(GMap_placeid(store_id)[0]) + "的網站為：" + str(GMap_placeid(store_id)[5]) + '\n'
                T_GMweb += str(GMap_placeid(store_id)[0]) + "的Google Map搜尋結果為：" + str(GMap_placeid(store_id)[6]) + '\n'

            T_response = [T_name,T_phone,T_address,T_time,T_grade,T_web,T_GMweb]
            return T_response
                
q = input("請輸入欲查詢地點")
# google可抓取類別：名稱(0)、電話(1)、地址(2)、營業時間(3)、評價(4)、網站(5)、googlemap頁面(6)、經緯度(7)(多點無)
print(GMap_place_detailssearch(q)[1])

