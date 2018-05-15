from django.shortcuts import render
from django.views import generic
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from hanziconv import HanziConv
from django.conf import settings
import json, requests, re, random, os
import urllib.request
import jieba
import jieba.posseg
import jieba.analyse
import sys
import importlib
import googlemaps
import time


# from flask import Flask, request, session, g, redirect, url_for, abort, \
#     render_template, flash 
# 結巴所在目錄
# sys.path.append(r'd:\moyege\work\@project\1221google_map\chatbot\chatbot\lib\site-packages')

# Create your views here.

# 胖狗狗的白白肚肚 https://goo.gl/WEjQQK API
PAGE_ACCESS_TOKEN = "EAAEQtzvtPZCYBAI0bHgO5a1eesqAZAl2V7CDiYYu2IxfTqpF46h9wXYCK4EIXZBiQzoi2oqIIloUkXpWD8ZAalStVsiKf4MdqaUrj0ylWpoSSpcuJZCf3J1lae7dJluE0kKiUOmacqj6wmb16tVtkAbG4fvDMDd5vGrAOw1ZCDagZDZD"


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
    "乘車":["搭乘","搭","車子","公車","坐","站","到","多久","多少時間"],
    "plane":["飛機", "航班", "延誤"],
    "高捷":["高捷","高雄捷運"]}
idcheck={}


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
D13 = len(dict["高捷"])

# 將toolong檔案內文字轉換
# ?
toolongf_v = [line.strip().encode('utf-8') for line in open(r'C:\Users\MA303\Desktop\testbot0130\GooglemapBot\toolong.txt',encoding = 'utf8').readlines()]
idd=''
toiletlat=''
toiletlong=''

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
        global toiletlat,toiletlong,idd
        # print(incoming_message)
        # print(incoming_message['entry'][0]['messaging'])
        if 'message' in incoming_message['entry'][0]['messaging'][0]:
            if 'attachments' in incoming_message['entry'][0]['messaging'][0]['message']:
                if 'payload' in incoming_message['entry'][0]['messaging'][0]['message']['attachments'][0]:
                    if 'coordinates' in incoming_message['entry'][0]['messaging'][0]['message']['attachments'][0]['payload']:
                        toiletlat=incoming_message['entry'][0]['messaging'][0]['message']['attachments'][0]['payload']['coordinates']['lat']
                        toiletlong=incoming_message['entry'][0]['messaging'][0]['message']['attachments'][0]['payload']['coordinates']['long']
        print(toiletlong)
        print(toiletlat)
        print('-------------------------------------------------')
        #     toiletlat=incoming_message[0]['entry'][0]['messaging'][0]['message']['attachments'][0]['payload']['coordinates']['lat']

        # if incoming_message[0]['entry']['messaging']['message']['attachments']['payload']['coordinates']['lat']!=0:
        #     toiletlat=incoming_message[0]['entry']['messaging']['message']['attachments']['payload']['coordinates']['lat']

        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events 
                if 'message' in message:
                    # if 'attachments'in message:
                    #     if 'payload'in message['attachments'][0]:
                    #         if 'coordinates' in message['attachments'][0]['payload']:
                    #             if 'lat' in message['attachments'][0]['payload']['coordinates']:
                    #                 toiletlat=message['attachments'][0]['payload']['coordinates']['lat']

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
                        idd=message['sender']['id']
                        if idd!='1778286295798129':
                            post_facebook_message_text(message['sender']['id'], message['message']['text'])
                    elif toiletlong!='':
                        idd=message['sender']['id']
                        if idd!='1778286295798129':
                            post_facebook_message_text(message['sender']['id'], 'kkk')                


        return HttpResponse()
# @app.route(API_ROOT + FB_WEBHOOK, methods=['POST'])
# def fb_handle_message(self, request, *args, **kwargs):
#     message_entries = json.loads(request.data.decode('utf8'))['entry']
#     for entry in message_entries:
#         messagings = entry['messaging']
#         for message in messagings:
#             sender = message['sender']['id']
#             if message.get('message'):
#                 text = message['message']['text']
#                 print("{} says {}".format(sender, text))
#                 message2=text
#     return message2


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

last_state = ''
startstation=''
endstation=''
stationtime=''
print(last_state)
print(idd)
print('+++++++++++++++++++++++++++++') 
def check_dict(fbid, recevied_message):
    global last_state          
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
    if idd in idcheck:
        print("weiweiweiweiweiweiweiweiweiweiweiwei")
        for i1 in range(D1):
            print('dudududududududududududududududu')
            if idcheck[idd].find(dict["toilet"][i1]) >= 0 and ans <= 0:
                with open(r'C:\Users\MA303\Desktop\testbot0130\GooglemapBot\jsondata\toilet.json', 'r', encoding="utf-8") as f:
                    toiletdata = json.load(f)
                gmaps = googlemaps.Client(key='AIzaSyBa-fjzE3tQFWlybQD_cFfSlMsdks4AvxQ')
                global toiletlong,toiletlat
                toiletans = 0
                toiletcount=0
                if toiletlat=='' and toiletlong=='' and toiletcount==0:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'要用按鈕上的傳送位置我們才會知道喔!',"quick_replies":[
                    {
                        "content_type":"text",
                        "title":"Search",
                        "payload":"<POSTBACK_PAYLOAD>",
                    },
                      {
                        "content_type":"location"
                      }
                    ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    toiletcount+=1
                elif toiletlat!=''and toiletlong!='' :
                    a = toiletlat
                    b = toiletlong

                    long = len(toiletdata)

                    for i in range(long):
                                #print((float(data[i]['Latitude'])-a)**2+(float(data[i]['Longitude'])-b)**2,i)
                        if ((float(toiletdata[i]['Latitude'])-a)**2+(float(toiletdata[i]['Longitude'])-b)**2) < 0.000020295025:    #0.00000901度 = 1公尺 500m
                            print(toiletdata[i]['Name']+'，地址是'+toiletdata[i]['Address'])
                            # toiletans.append(toiletdata[i]['Name']+'，地址是'+toiletdata[i]['Address'])
                            # print(toiletans)
                            # print('成功')
                            toiletans=toiletans+1
                            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":toiletdata[i]['Name']+'，地址是'+toiletdata[i]['Address']}})
                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    if toiletans==0 :
                        # print('也成功')
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'不好意思，這附近沒有廁所餒'}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    last_state=''
                    toiletans=0
                    toiletlong=''
                    toiletlat=''
                    del idcheck[idd] 




            # response_text = "您附近的廁所有以下這些"


            # fb_handle_message()
            # if message2=="台北":
            #     response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"幫你找台北廁所"}})
            #     status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            # else:
            #     response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"有成功但是不是台北喔"}})
            #     status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

            ans=ans+1

    # 檢測有無交通資訊類別需求關鍵字
    # 未完成實際內容
        for i13 in range(D13):
            if idcheck[idd].find(dict["高捷"][i13]) >= 0 :
                global stationtime,startstation,endstation
                print('7777777777777777')
                print('startstation')
                print('7777777777777777')
                # station = []

                kaostation=['南岡山','橋頭火車站','橋頭糖廠','青埔','都會公園','後勁','楠梓加工區','油廠國小','世運','左營',
                '生態園區','巨蛋','凹子底','後驛','高雄車站','美麗島','中央公園','三多商圈','獅甲','凱旋',
                '前鎮高中','草衙','高雄國際機場','小港','西子灣','鹽埕埔','市議會','美麗島','信義國小',
                '文化中心','五塊厝','技擊館','衛武營','鳳山西站','鳳山','大東','鳳山國中','大寮']
                kaotime=['00','01','02','03','04','05','06','07','08','09',
                '10','11','12','13','14','15','16','17','18','19',
                '20','21','22','23','24']
                print('近來第一步')
            # response_text = "您附近的廁所有以下這些"
                # for Kaocount in range(0,1):
                #     station.append(recevied_message)
                #     print(station)
                if stationtime=='' and endstation!='':
                    kk=0
                    for Kaohour in range(25):
                        if recevied_message ==kaotime[Kaohour]:                            
                            stationtime=recevied_message
                            print(stationtime)
                            with open(r'C:\Users\MA303\Desktop\testbot0130\GooglemapBot\jsondata\時刻表\MRT_Kaohsiung.json', 'r', encoding="utf-8") as f:
                                dataKaoMRT = json.load(f)
                            today = time.strftime("%A")
                            Kaoa = len(dataKaoMRT)
                            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'以下為往【'+endstation+'】方向之班次在【'+stationtime+'點】停靠【'+startstation+'站】之時刻表：\n'}})
                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

                            print('以下為往【'+endstation+'】方向之班次在【'+stationtime+'點】停靠【'+startstation+'站】之時刻表：\n')
                            for Kaoi in range(Kaoa): #i=第幾筆資料
                                #找出使用者的現在位置(228取6)
                                if dataKaoMRT[Kaoi]["StationName"]["Zh_tw"] == startstation: 
                                    #判斷捷運的方向(6取3)
                                    if dataKaoMRT[Kaoi]["DestinationStationName"]["Zh_tw"] == endstation:
                                        #print(data[i]['StationName']['Zh_tw'], i)
                                        Kaob = len(dataKaoMRT[Kaoi]["Timetables"]) #b=總班次
                                        for Kaoj in range(Kaob):
                                        #print(b)
                                            #禮拜一到四、禮拜五和假日的時刻表不同，故要去判斷今天是星期幾(3取1)
                                            if today == ('Monday' or 'Tuesday' or 'Wednesday' or 'Thursday'):
                                                if Kaoi % 3 == 0:
                                                    Kaox = dataKaoMRT[Kaoi]['Timetables'][Kaoj]['ArrivalTime'].find(stationtime)
                                                    if 2 > Kaox >= 0:
                                                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'第'+ str(dataKaoMRT[Kaoi]['Timetables'][Kaoj]['Sequence'])+'班車: '+ str(dataKaoMRT[Kaoi]['Timetables'][Kaoj]['ArrivalTime'])}})
                                                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                                                        print('第', dataKaoMRT[Kaoi]['Timetables'][Kaoj]['Sequence'], '班車: ', dataKaoMRT[Kaoi]['Timetables'][Kaoj]['ArrivalTime'])
                                                else:
                                                    break

                                            elif today == ('Saturday' or 'Sunday'):
                                                if Kaoi % 3 == 1:
                                                    Kaox = dataKaoMRT[Kaoi]['Timetables'][Kaoj]['ArrivalTime'].find(stationtime)
                                                    if 2 > Kaox >= 0:
                                                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"第"+ str(dataKaoMRT[Kaoi]["Timetables"][Kaoj]["Sequence"])+"班車: "+ str(dataKaoMRT[Kaoi]["Timetables"][Kaoj]["ArrivalTime"])}})
                                                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                                                        print('第', dataKaoMRT[Kaoi]['Timetables'][Kaoj]['Sequence'], '班車: ', dataKaoMRT[Kaoi]['Timetables'][Kaoj]['ArrivalTime'])
                                                else:
                                                    break

                                            else:
                                                if Kaoi % 3 == 2:
                                                    Kaox = dataKaoMRT[Kaoi]['Timetables'][Kaoj]['ArrivalTime'].find(stationtime)
                                                    if 2 > Kaox >= 0:
                                                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'第'+ str(dataKaoMRT[Kaoi]['Timetables'][Kaoj]['Sequence'])+'班車: '+ str(dataKaoMRT[Kaoi]['Timetables'][Kaoj]['ArrivalTime'])}})
                                                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                                                        print('第', dataKaoMRT[Kaoi]['Timetables'][Kaoj]['Sequence'], '班車: ', dataKaoMRT[Kaoi]['Timetables'][Kaoj]['ArrivalTime'])
                                                else:
                                                    break
                            last_state = ''
                            del idcheck[idd]
                        else:
                            print('else 外')
                            if kk == 24:
                                print('else 裡')
                                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"搞毛阿整老子??時間觀念有問題阿??"}})
                                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                                print("555555555555555555")
                            kk+=1


                if endstation=='' and startstation!='':
                    kaonumber=len(kaostation)
                    kk=0
                    for kao in range(kaonumber):
                        if recevied_message == kaostation[kao]: 
                            endstation=recevied_message
                            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"您的乘車時間是幾點呢?(00-24)"}})
                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                            print(endstation)
                        else:
                            if kk == kaonumber-1:
                                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"搞毛阿整老子??沒這個站阿!!"}})
                                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                                print("555555555555555555")
                            kk+=1
                if startstation=='':
                    print('6666666666666666666666666')
                    kaonumber=len(kaostation)
                    kk=0
                    for kao in range(kaonumber): 
                        if recevied_message == kaostation[kao]:
                            startstation=recevied_message
                            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"那要在哪裡下車呢?"}})
                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                            print(startstation)
                        else:
                            if kk == kaonumber-1:
                                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"搞毛阿整老子??沒這個站阿!!"}})
                                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                                print("555555555555555555")
                            kk+=1
                


                    # if Kaocount == 0:
                    #     response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"那要在哪裡下車呢?"}})
                    #     status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    #     station.append(recevied_message)
                    #     print('成功第一步')
                    # else:
                    #     response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"您的乘車時間是幾點呢?(00-24)"}})
                    #     status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    #     station.append(recevied_message)
                    #     print('成功第二步')
                    # print(station)

                    # fb_handle_message()
                    # if message2=="台北":
                    #     response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"幫你找台北廁所"}})
                    #     status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    # else:
                    #     response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"有成功但是不是台北喔"}})
                    #     status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                
                ans=ans+1
        for i2 in range(D2):
            if sentence.find(dict["乘車"][i2]) >= 0 and ans <= 0:
                dle = sentence.find(dict["乘車"][i2])
                dle_long = len(dict["乘車"][i2])
                dle2 = dle + dle_long
                sentence = sentence[:dle] + sentence[dle2:]
                # response_text = "以下是" + recevied_message + "的交通資訊"
                if not last_state:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的交通資訊"}})
                    last_state = recevied_message
                else:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + last_state + "的交通資訊"}})
                    last_state = ''
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

                # 新增地址回覆（未測試完成）
                # BUG：
                # 1 - 中文地名無法讀取
                # 2 - 英文詞語間空格使回復網址錯誤(ex:taipei 101 顯示為 taipei 的地圖，101的詞語未收入)
                # 3 - 地址回傳最後會加上地點名稱
                # 4 - 未知error（可能非此部分造成）：raise URLError('no host given')　urllib.error.URLError: <urlopen error no host given>
                # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的位置資訊，\n" + GMap_place_search(sentence) + "\n" + "https://www.google.com.tw/maps/search/" + sentence}})
                # 未有地址回復版本（圖片+網址）
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的位置資訊，\n" + "https://www.google.com.tw/maps/search/" + sentence}})
                
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
    else :
        for i1 in range(D1):
            if sentence.find(dict["toilet"][i1]) >= 0 and ans <= 0:
            # response_text = "您附近的廁所有以下這些"
                last_state=recevied_message
                idcheck.update({idd:recevied_message})
                print('-----------------------------------------------------')
                print(idd)
                print('-----------------------------------------------------')
                print(idcheck)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"請開啟定位功能，讓我知道你在哪","quick_replies":[
                    {
                        "content_type":"text",
                        "title":"Search",
                        "payload":"<POSTBACK_PAYLOAD>",
                    },
                      {
                        "content_type":"location"
                      }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                # fb_handle_message()
                # if message2=="台北":
                #     response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"幫你找台北廁所"}})
                #     status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                # else:
                #     response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"有成功但是不是台北喔"}})
                #     status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

                ans=ans+1

    # 檢測有無交通資訊類別需求關鍵字
    # 未完成實際內容
        for i13 in range(D13):
            if sentence.find(dict["高捷"][i13]) >= 0 and ans <= 0:
            # response_text = "您附近的廁所有以下這些"
                last_state=recevied_message
                idcheck.update({idd:recevied_message})
                print(recevied_message)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"請問你要在哪裡上車?"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                # fb_handle_message()
                # if message2=="台北":
                #     response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"幫你找台北廁所"}})
                #     status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                # else:
                #     response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"有成功但是不是台北喔"}})
                #     status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

                ans=ans+1
        for i2 in range(D2):
            if sentence.find(dict["乘車"][i2]) >= 0 and ans <= 0:
                dle = sentence.find(dict["乘車"][i2])
                dle_long = len(dict["乘車"][i2])
                dle2 = dle + dle_long
                sentence = sentence[:dle] + sentence[dle2:]
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的交通資訊"}})
                # last_state=recevied_message
                # response_text = "以下是" + recevied_message + "的交通資訊"
                # if not last_state:
                #     response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的交通資訊"}})
                #     last_state = recevied_message
                # else:
                #     response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + last_state + "的交通資訊"}})
                #     last_state = ''
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

                # 新增地址回覆（未測試完成）
                # BUG：
                # 1 - 中文地名無法讀取
                # 2 - 英文詞語間空格使回復網址錯誤(ex:taipei 101 顯示為 taipei 的地圖，101的詞語未收入)
                # 3 - 地址回傳最後會加上地點名稱
                # 4 - 未知error（可能非此部分造成）：raise URLError('no host given')　urllib.error.URLError: <urlopen error no host given>
                # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的位置資訊，\n" + GMap_place_search(sentence) + "\n" + "https://www.google.com.tw/maps/search/" + sentence}})
                # 未有地址回復版本（圖片+網址）
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的位置資訊，\n" + "https://www.google.com.tw/maps/search/" + sentence}})
                
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
        # 優化:把last_state設成1.2.3.4.5來區別就不用字典

        #if recevied_message =='謝謝':
        #    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"不客氣"}})
        #    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        



            
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
	GM_API_KEY = 'AIzaSyA35lPzOmBYaGtsGnu1BtuZiWqZcLpYdQk'

	G_center = center.replace(' ', '+')
	G_zoom = "16"
	G_size = "250x250"
	G_markers = "color:red%7C"+ G_center

	nav_request = 'center={}&zoom={}&size={}&markers={}&key={}'.format(G_center, G_zoom, G_size, G_markers, GM_API_KEY)
	G_request = endpoint + nav_request
	return G_request

# Google Places API Web Service Search
def GMap_place_search(center):
    # Google Places API Web Service Search

    endpoint = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
    GM_API_KEY = 'AIzaSyA35lPzOmBYaGtsGnu1BtuZiWqZcLpYdQk'

    G_query = center.replace(' ', '+')
    G_language = 'zh-TW'

    # 輸出中文地址
    nav_request = 'query={}&language={}&key={}'.format(G_query, G_language, GM_API_KEY)
    # 輸出英文地址
    # nav_request = 'query={}&key={}'.format(G_query, GM_API_KEY)

    request = endpoint + nav_request
    respone = urllib.request.urlopen(request).read()
    directions = json.loads(respone.decode('utf-8'))

    results = directions['results']
    # response = results[0]['name'] + '的地址是：' + results[0]['formatted_address']
    response = results[0]['formatted_address']

    # print (results[0]['name'] + '的地址是：' + results[0]['formatted_address'])
    return response