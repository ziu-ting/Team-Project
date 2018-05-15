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


# 胖狗狗的白白肚肚 https://goo.gl/WEjQQK API
PAGE_ACCESS_TOKEN = "EAAB09UKvWGsBAFsrGU5hpRfJRQHMFPMSHNV8D9TvIKpqvhLkkKCUJgIhJHQZABsqadPckRxeBxsadZAq6RSMeBHdskcwP0hnLyKEoWsWXCQWx1hrrXZAz6PXeKQnTkYpPOhPoFJtDXf3z60U6N6PlBl9ZBXAnJWlM03ZBl9JqhAZDZD"
GM_API_KEY = 'AIzaSyA35lPzOmBYaGtsGnu1BtuZiWqZcLpYdQk'


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

                        # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                        # are sent as attachments and must be handled accordingly. 
                        post_facebook_message_text(message['sender']['id'], message['message']['text']) 
 

        return HttpResponse()


def message_contents(fbid, sentence):
    
    # recevied_message = ""
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    

    # print("===========" + sentence + "=================")
    # GM_id = GMap_place_idsearch(sentence)
    # print("===========" + GM_id + "=================")
    # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":GMap_place_detailssearch(GM_id)[2]}})
    # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":GMap_place_detailssearch(sentence)[2]}})
    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"輸入的文字為：" + sentence}})
    
    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
    # post_facebook_message_media(fbid, GMap_map(sentence)) 



# 建立可回應至FB之函數(文字)
def post_facebook_message_text(fbid, recevied_message):

	# 抓取傳送者名稱
	# 使用：user_details['first_name']
    user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid
    user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':PAGE_ACCESS_TOKEN}
    user_details = requests.get(user_details_url, user_details_params).json()

    message_contents(fbid, recevied_message)


def post_facebook_message_media(fbid, imgurl):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"attachment":{"type":"image", "payload":{"url":imgurl}}}})
    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"},data = response_msg)
    # print(status.json())

# Google Static Maps
def GMap_map(center):

    endpoint = "https://maps.googleapis.com/maps/api/staticmap?"
    GM_API_KEY = 'AIzaSyA35lPzOmBYaGtsGnu1BtuZiWqZcLpYdQk'

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
    GM_API_KEY = 'AIzaSyA35lPzOmBYaGtsGnu1BtuZiWqZcLpYdQk'

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

    print (request_trans)

    respone = urllib.request.urlopen(request_trans).read()
    directions = json.loads(respone.decode('utf-8'))

    results = directions['results']
    # response = results[0]['name'] + '的地址是：' + results[0]['formatted_address']

    # print ('===results=====' + results[0])
    
    response = results[0]['place_id']

    print ('===response===' + response)

    # print (results[0]['name'] + '的地址是：' + results[0]['formatted_address'])
    return response


# Google Places API Web Service Details
def GMap_place_detailssearch(query):
    
    endpoint = "https://maps.googleapis.com/maps/api/place/details/json?"
    GM_API_KEY = 'AIzaSyA35lPzOmBYaGtsGnu1BtuZiWqZcLpYdQk'

    G_language = 'zh-TW'
    nav_request = 'placeid={}&language={}&key={}'.format(query, G_language, GM_API_KEY)
    request = endpoint + nav_request

    print(request)

    respone = urllib.request.urlopen(request).read()
    directions = json.loads(respone.decode('utf-8'))


    result = directions['result']


    # google可抓取類別：名稱、電話、地址、營業時間、評價、網站、googlemap頁面

    P_name = result['name']

    if 'formatted_phone_number' in result :
        P_phone = result['formatted_phone_number']
    else :
        P_phone = '您所查詢的地點暫無電話資訊！'

    if 'formatted_address' in result :
        P_address = result['formatted_phone_number']
    else :
        P_address = '您所查詢的地點暫無地址資訊！'

    # 營業時間回傳值為list
    if 'opening_hours' in result :
        P_time = ''
        for i in range(0,7):
            P_time += re['opening_hours']['weekday_text'][i] + '\n'
    else :
        P_time = '您所查詢的地點暫無營業時間資訊！'
    
    if 'rating' in result :
        P_grade = result['rating']
    else :
        P_grade = '您所查詢的地點暫無評價資訊！'

    if 'website' in result :
        P_web = result['website']
    else :
        P_web = '您所查詢的地點暫無網站資訊！'

    P_GMweb = result['url']

    response = [ P_name, P_phone, P_address, P_time, P_grade, P_web, P_GMweb ]

    print (response)

    return response
    # return result
