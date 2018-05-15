from django.shortcuts import render
from django.views import generic
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from hanziconv import HanziConv
from django.conf import settings
from urllib.parse import quote
import json, requests, re, random, os, sys, string
import jieba, jieba.posseg , jieba.analyse
import urllib.request


# 結巴所在目錄
sys.path.append(r'd:\moyege\work\@project\1221google_map\chatbot\chatbot\lib\site-packages')

GM_API_KEY = 'AIzaSyA35lPzOmBYaGtsGnu1BtuZiWqZcLpYdQk'
# 胖狗狗的白白肚肚 https://goo.gl/WEjQQK API
PAGE_ACCESS_TOKEN = "EAAB09UKvWGsBAFsrGU5hpRfJRQHMFPMSHNV8D9TvIKpqvhLkkKCUJgIhJHQZABsqadPckRxeBxsadZAq6RSMeBHdskcwP0hnLyKEoWsWXCQWx1hrrXZAz6PXeKQnTkYpPOhPoFJtDXf3z60U6N6PlBl9ZBXAnJWlM03ZBl9JqhAZDZD"


# # 對應關鍵字直接回覆
# jokes = {
#          'stupid': ["""Yo' Mama is so stupid, she needs a recipe to make ice cubes.""",
#                     """Yo' Mama is so stupid, she thinks DNA is the National Dyslexics Association."""]}

# 建立除冗字與相關類型判斷關鍵字之字典
dict={"location":["去","往哪","哪","位置","地址","地點","方向","怎麼走","走"],
    "toilet":["廁所","尿","大便","拉屎","屎","撇條","排遺","排泄","便便","便所","化妝室","洗手間"],
    "營業時間":["營業時間","幾點關門","幾點","入場","關門","時間","開始","開放","幾號"],
    "電話":["電話","專線","號碼","連絡","聯絡"],
    "介紹":["簡介","特色","高度","長度","多高","多長","歷史","介紹","內容","文化","活動","官網","網站","資訊","限時","外送","附近"],
    "價錢":["價格","票價","多少錢","錢","貴","便宜","花費","費用","花"],
    "wifi":["wifi","WIFI","網路","上網","無線"],
    "菜單":["菜單","餐點","低消","飲料","葷","素","蛋奶素","食物"],
    "評價":["評價","好吃","好玩","有趣"],
    "充電":["插座","充電","電源","電","手機"],
    "乘車":["搭乘","搭","車子","公車","捷運","站","到","多久","多少時間"],
    "plane":["飛機", "航班", "延誤"]}


# D1, D2, D3, D4, D5, D6, D7, D8, D9, D10, D11= 0
# toolong = 0

# 指定變數為字典內各項的元素數量，以逐步檢測
# toolong = len(dict["unnecessary"])
D1 = len(dict["toilet"])
D2 = len(dict["乘車"])
D3 = len(dict["價錢"])
D4 = len(dict["location"])
D5 = len(dict["營業時間"])
D6 = len(dict["電話"])
D7 = len(dict["介紹"])
D8 = len(dict["wifi"])
D9 = len(dict["菜單"])
D10 = len(dict["評價"])
D11 = len(dict["充電"])
D12 = len(dict["plane"])

# 將toolong檔案內文字轉換
# ?
toolongf_v = [line.strip().encode('utf-8') for line in open(r'D:\Moyege\Work\@PROJECT\1221Google_map\chatbot\chatbot\Scripts\testbot\GooglemapBot\toolong.txt',encoding = 'utf8').readlines()]



class GMBotView(generic.View):
		# 在class based views 里面，args 有两个元素，一个是self, 第二个才是request
		# *args是接受很多的值，在Python叫做tuple。
		# **kwargs是接受dictionary。

    def get(self, request, *args, **kwargs):
    	# Verify Token = botprojecttest
    	if self.request.GET['hub.verify_token'] == 'botprojecttest':
    		return HttpResponse(self.request.GET['hub.challenge'])
    	else:
    		return HttpResponse('Error, invalid token')

	# The get method is the same as before.. omitted here for brevity
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    # 將接收到的文字內容以Json形式讀取，而後轉為字串
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events 
                if 'message' in message:
                    # Print the message to the terminal

                    if 'text' in message ['message']:
                        # 顯示message此JSON檔內容
                        	# {'timestamp':__, //作用未知
                        	#  'message': 
                        	# 		{'mid': '__', //會變動，作用未知
                        	# 		 'text': '__', //收到傳送的message訊息
                        	# 		 'is_echo': True, //固定為True，作用未知
                        	#		 'app_id': __, //連結到的應用程式編號
                        	#		 'seq': __}, //會變動，作用未知
                        	# 'sender': {'id': '__'}, //粉專ID
                        	# 'recipient': {'id': '__'}} //訊息傳送者ID
                        	# {'error': {
                        	# 	'code': 100, //固定，作用未知
                        	# 	'error_subcode': 2018001, //固定，作用未知
                        	# 	'message': '(#100) No matching user found', //固定，作用未知
                        	# 	'type': 'OAuthException', //固定，作用未知
                        	# 	'fbtrace_id': '__'}} //會變動，作用未知
                        # print(message)

                        # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                        # are sent as attachments and must be handled accordingly. 
                        post_facebook_message_text(message['sender']['id'], message['message']['text']) 
 

        return HttpResponse()


def jieba_check(long_sentence):
    # 檢測冗字(JIEBA)

    # 將輸入文字斷成詞語
    vocabulary = jieba.posseg.cut(long_sentence)

    # 將斷開的詞語加入
    received_v = []
    for i in vocabulary:
        received_v.append((i.word))

    toolongf_v_long=len(toolongf_v)
    received_v_long=len(received_v)
    m=0
    n=0

    for m in range(received_v_long):
        for n in range(toolongf_v_long):
            if received_v[m]==toolongf_v[n].decode('utf8') :
                received_v[m]=None

    jiebaed = ''
    for i in received_v:
        if i:
            jiebaed+=i

    return jiebaed

def check_dict(fbid, recevied_message):
    
    ans = 0
    # recevied_message = ""
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    
    # # 檢測冗字
    # for t in range(toolong):
    #     if recevied_message.find(dict["unnecessary"][t]) >= 0 :
    #         dle = recevied_message.find(dict["unnecessary"][t])
    #         dle_long = len(dict["unnecessary"][t])
    #         dle2 = dle + dle_long
    #         recevied_message = recevied_message[:dle] + recevied_message[dle2:]

    sentence = jieba_check(recevied_message)


    
    # 檢測有無廁所類別需求關鍵字
    # 未完成實際內容
    for i1 in range(D1):
        if sentence.find(dict["toilet"][i1]) >= 0 and ans <= 0:
            # response_text = "您附近的廁所有以下這些"
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"您附近的廁所有以下這些"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            ans=ans+1

    # 檢測有無交通資訊類別需求關鍵字
    # 未完成實際內容
    for i2 in range(D2):
        if sentence.find(dict["乘車"][i2]) >= 0 and ans <= 0:
            dle = sentence.find(dict["乘車"][i2])
            dle_long = len(dict["乘車"][i2])
            dle2 = dle + dle_long
            sentence = sentence[:dle] + sentence[dle2:]
            # response_text = "以下是" + recevied_message + "的交通資訊"
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的交通資訊"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            ans = ans + 1

    # 檢測有無查價類別需求關鍵字
    # 未完成實際內容
    for i3 in range(D3):
        if sentence.find(dict["價錢"][i3]) >= 0 and ans <= 0:
            dle = sentence.find(dict["價錢"][i3])
            dle_long = len(dict["價錢"][i3])
            dle2 = dle + dle_long
            sentence = sentence[:dle] + sentence[dle2:]
            # response_text = "以下是" + recevied_message + "的價錢資訊"
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的價錢資訊"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            ans = ans + 1

    # 檢測有無查位置類別需求關鍵字（內容物為判斷地點位置）
    for i4 in range(D4):
        if sentence.find(dict["location"][i4]) >= 0 and ans <= 0:
            dle = sentence.find(dict["location"][i4])
            dle_long = len(dict["location"][i4])
            dle2 = dle + dle_long
            sentence = sentence[:dle] + sentence[dle2:]
            # response_text = "以下是" + recevied_message + "的位置資訊，\n" + "https://www.google.com.tw/maps/search/" + recevied_message

            # 新增地址回覆（測試完成）
            # BUG：（0221已解決 url無法使用中文字元）
            # 1 - 中文地名無法讀取
            # 2 - 英文詞語間空格使回復網址錯誤(ex:taipei 101 顯示為 taipei 的地圖，101的詞語未收入)
            # 3 - 地址回傳最後會加上地點名稱
            # 4 - 未知error（可能非此部分造成）：raise URLError('no host given')　urllib.error.URLError: <urlopen error no host given>

            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的位置資訊，\n" + GMap_place_detailssearch(sentence)[2]}})
            # 未有地址回復版本（圖片+網址）
            # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的位置資訊，\n" + "https://www.google.com.tw/maps/search/" + sentence}})
            
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            post_facebook_message_media(fbid, GMap_map(sentence)) 
            ans = ans + 1

    # 檢測有無查營業時間類別需求關鍵字
    # 未完成實際內容
    for i5 in range(D5):
        if sentence.find(dict["營業時間"][i5]) >= 0 and ans <= 0:
            dle = sentence.find(dict["營業時間"][i5])
            dle_long = len(dict["營業時間"][i5])
            dle2 = dle + dle_long
            sentence = sentence[:dle] + sentence[dle2:]
            # response_text = recevied_message + "的營業時間是"
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":sentence + "的營業時間是"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            ans = ans + 1

    # 檢測有無查營業電話類別需求關鍵字
    # 未完成實際內容
    for i6 in range(D6):
        if sentence.find(dict["電話"][i6]) >= 0 and ans <= 0:
            dle = sentence.find(dict["電話"][i6])
            dle_long = len(dict["電話"][i6])
            dle2 = dle + dle_long
            sentence = sentence[:dle] + sentence[dle2:]
            # response_text = recevied_message + "的電話是"
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":sentence + "的電話是"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            ans = ans + 1

    # 檢測有無查店家介紹類別需求關鍵字
    # 未完成實際內容
    for i7 in range(D7):
        if sentence.find(dict["介紹"][i7]) >= 0 and ans <= 0:
            dle = sentence.find(dict["介紹"][i7])
            dle_long = len(dict["介紹"][i7])
            dle2 = dle + dle_long
            sentence = sentence[:dle] + sentence[dle2:]
            # response_text = "以下是" + recevied_message + "的相關資訊"
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的相關資訊"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            ans = ans + 1

    # 檢測有無查wifi類別需求關鍵字
    # 未完成實際內容
    for i8 in range(D8):
        if sentence.find(dict["wifi"][i8]) >= 0 and ans <= 0:
            dle = sentence.find(dict["wifi"][i8])
            dle_long = len(dict["wifi"][i8])
            dle2 = dle + dle_long
            sentence = sentence[:dle] + sentence[dle2:]
            # response_text = "以下是" + recevied_message + "的wifi資訊"
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的wifi資訊"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            ans = ans + 1
 
    # 檢測有無查店家菜單資訊類別需求關鍵字
    # 未完成實際內容           
    for i9 in range(D9):
        if sentence.find(dict["菜單"][i9]) >= 0 and ans <= 0:
            dle = sentence.find(dict["菜單"][i9])
            dle_long = len(dict["菜單"][i9])
            dle2 = dle + dle_long
            sentence = sentence[:dle] + sentence[dle2:]
            # response_text = "以下是" + recevied_message + "的菜單資訊"
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的菜單資訊"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            ans = ans + 1

    # 檢測有無查店家評價類別需求關鍵字
    # 未完成實際內容       
    for i10 in range(D10):
        if sentence.find(dict["評價"][i10]) >= 0 and ans <= 0:
            dle = sentence.find(dict["評價"][i10])
            dle_long = len(dict["評價"][i10])
            dle2 = dle + dle_long
            sentence = sentence[:dle] + sentence[dle2:]
            # response_text = "以下是" + recevied_message + "的評價資訊"
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的評價資訊"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            ans = ans + 1

    # 檢測有無查充電類別需求關鍵字
    # 未完成實際內容     
    for i11 in range(D11):
        if sentence.find(dict["充電"][i11]) >= 0 and ans <= 0:
            dle = sentence.find(dict["充電"][i11])
            dle_long = len(dict["充電"][i11])
            dle2 = dle + dle_long
            sentence = sentence[:dle] + sentence[dle2:]
            # response_text = "以下是充電資訊"
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是充電資訊"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            ans = ans + 1


    # 檢測有無查詢航班需求之關鍵字
    # 雲端期末報告結合
    # 應用IBM相關套件完成
    for i12 in range(D12):
        if sentence.find(dict["plane"][i12]) >= 0 and ans <= 0:
            dle = sentence.find(dict["plane"][i12])
            dle_long = len(dict["plane"][i12])
            dle2 = dle + dle_long
            sentence = sentence[:dle] + sentence[dle2:]
            # response_text = "以下是充電資訊"
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下為航班延誤資訊：\n http://pysparkwebappredfinal.mybluemix.net/dsxinsights"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            ans = ans + 1
            
    # # Jerry
    # if ans == 0:
    #     jerry = ChatBot("jerry",storage_adapter="chatterbot.storage.SQLStorageAdapter",database=os.path.join(settings.BASE_DIR,'fb_Chatbot/chat/test'))
    #     jerry.set_trainer(ChatterBotCorpusTrainer)
    #     # D:\\Moyege\\Work\\@PROJECT\\1221Google_map\\chatbot\\chatbot\\Scripts\\testbot\\GooglemapBot\\chat
    #     jerry.train("D:\\Moyege\\Work\\@PROJECT\\1221Google_map\\chatbot\\chatbot\\Scripts\\testbot\\GooglemapBot\\chat\\jerry_DB.json") 
    #     tokens = re.sub(r"[^a-zA-Z0-9\s]",' ',recevied_message).lower().split()
    #     joke_text = ''
    #     # print (recevied_message)
    #     # print (type (recevied_message))
    #     # print (tokens)
    #     # print (type (tokens))
    #     y = jerry.get_response(recevied_message)
    #     y = HanziConv.toTraditional(y.text)
    #     # print(y)
    #     joke_text = y
    #     # joke_text = 'Yo ..! ' + joke_text
    #     post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    #     response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你好!" + joke_text}})
    #     status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
    # return response_text


# 單獨處理error：raise URLError('no host given')     urllib.error.URLError: <urlopen error no host given>
#將中文等字元轉換成url可處理之字元 
    # url中不可包含中文等無法處理之字→需轉換成「%XX」
    # urllib.parse.quote(string, safe='/', encoding=None, errors=None)
    # https://www.zhihu.com/question/22899135       https://docs.python.org/3/library/urllib.parse.html#url-quoting
# def url_trans(input_word):

#     space_processed = input_word.replace(' ', '+')
#     chinese_processed = urllib.parse.quote(space_processed, safe = string.printable)

#     return chinese_processed
    

# 建立可回應至FB之函數(文字)
def post_facebook_message_text(fbid, recevied_message):

	# 抓取傳送者名稱
	# 使用：user_details['first_name']
    user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid
    user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':PAGE_ACCESS_TOKEN}
    user_details = requests.get(user_details_url, user_details_params).json()

	# Remove all punctuations, lower case the text and split it based on space
	# # 將預設回復的字串處理並以空格為斷開依據
	# tokens = re.sub(r"[^a-zA-Z0-9\s]",' ',recevied_message).lower().split()
 #    joke_text = ''
 #    # 有對應關鍵字
 #    for token in tokens:
 #        if token in jokes:
 #            joke_text = random.choice(jokes[token])
 #            break
 #    # 無對應關鍵字
 #    if not joke_text:
 #        joke_text = "I didn't understand! Send 'stupid', 'fat', 'dumb' for a Yo Mama joke!"   
    
    # joke_text = 'Yo '+user_details['first_name']+'..!' + joke_text

    # response_text = "嗨！" + user_details['first_name'] + ", 您搜尋的地點為：「" + recevied_message + "」。\n以下為您顯示相關地圖："
    # response_text = "嗨" + ", 您搜尋的地點為：「" + recevied_message + "」。以下為您顯示相關地圖："

    # print(response_text)

    check_dict(fbid, recevied_message)

    # FUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUCK!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ===UnboundLocalError: local variable 'response_text' referenced before assignment.===
    # 碼神建議:在前面已經使用的時候，未進行變數的宣告。>> 未進入判斷後進行的宣告

    # post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    # response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":check_dict(recevied_message)}})
    # status = requests.post(post_message_url, headers = {"Content-Type": "application/json"},data = response_msg)

    # print(status.json())


# "recipient":{
  #   "id":"1254459154682919"
  # },
  # "message":{
  #   "attachment":{
  #     "type":"image", 
  #     "payload":{
  #       "url":"http://www.messenger-rocks.com/image.jpg", 
  #       "is_reusable":true
def post_facebook_message_media(fbid, imgurl):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"attachment":{"type":"image", "payload":{"url":imgurl}}}})
    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"},data = response_msg)
    # print(status.json())

# Google Static Maps
def GMap_map(center):

	endpoint = "https://maps.googleapis.com/maps/api/staticmap?"

	G_center = center.replace(' ', '+')
	G_zoom = "16"
	G_size = "250x250"
	G_markers = "color:red%7C"+ G_center

	nav_request = 'center={}&zoom={}&size={}&markers={}&key={}'.format(G_center, G_zoom, G_size, G_markers, GM_API_KEY)
	G_request = endpoint + nav_request
	return G_request


# Google Places API Web Service Search
def GMap_place_idsearch(center):

    endpoint = "https://maps.googleapis.com/maps/api/place/textsearch/json?"

    G_query = center.replace(' ', '+')
    G_language = 'zh-TW'

    nav_request = 'query={}&language={}&key={}'.format(G_query, G_language, GM_API_KEY)

    request = endpoint + nav_request
    # url中不可包含中文等無法處理之字→需轉換成「%XX」
    # urllib.parse.quote(string, safe='/', encoding=None, errors=None)
    # https://www.zhihu.com/question/22899135       https://docs.python.org/3/library/urllib.parse.html#url-quoting。    
    request_trans = urllib.parse.quote(request, safe = string.printable)


    # 新增標頭檔偽裝伺服器 (Error：'latin-1' codec can't encode character '\u015f' in position 54: ordinal not in range(256))
    # header = {'user-agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/\537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}
    # req = urllib.request.Request(request_trans, headers = header)
    # respone = urllib.request.urlopen(req).read()


    respone = urllib.request.urlopen(request_trans).read()
    directions = json.loads(respone.decode('utf-8'))

    results = directions['results']
    # response = results[0]['name'] + '的地址是：' + results[0]['formatted_address']
    
    response = results[0]['place_id']

    # print (results[0]['name'] + '的地址是：' + results[0]['formatted_address'])
    return response


# Google Places API Web Service Details
def GMap_place_detailssearch(place_id):
    
    endpoint = "https://maps.googleapis.com/maps/api/place/details/json?"
    G_language = 'zh-TW'
    nav_request = 'placeid={}&language={}&key={}'.format(GMap_place_idsearch(place_id), G_language, GM_API_KEY)
    request = endpoint + nav_request
    request_trans = urllib.parse.quote(request, safe = string.printable)
    respone = urllib.request.urlopen(request_trans).read()
    directions = json.loads(respone.decode('utf-8'))
    results = directions['results']

    # google可抓取類別：名稱、電話、地址、營業時間、評價、網站、googlemap頁面

    P_name = results[0]['name']

    if len(results[0]['formatted_phone_number']) > 0 :
        P_phone = results[0]['formatted_phone_number']
    else :
        P_phone = None

    if len(results[0]['formatted_address']) > 0 :
        P_address = results[0]['formatted_address']
    else :
        P_address = None

    # 營業時間回傳值為list
    if len(results[0]['opening_hours']['weekday_text']) > 0 :
        P_time = results[0]['opening_hours']['weekday_text']
    else :
        P_time = None

    if len(results[0]['rating']) > 0 :
        P_grade = results[0]['rating']
    else :
        P_grade = None

    if len(results[0]['website']) > 0 :
        P_web = results[0]['website']
    else :
        P_web = None

    P_GMweb = results[0]['url']

    return P_name, P_phone, P_address, P_time, P_grade, P_web, P_GMweb
