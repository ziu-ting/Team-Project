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
import urllib.request
import jieba
import jieba.posseg
import jieba.analyse
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
    "toilet":["廁所","尿","大便","拉屎","屎","撇條","排遺","排泄","便便","便所","化妝室","洗手間","大號","尿急","棒賽"],
    "營業時間":["營業時間","幾點關門","幾點","入場","關門","時間","開始","開放","幾號"],
    "電話":["電話","專線","號碼","連絡","聯絡"],
    "介紹":["簡介","特色","高度","長度","多高","多長","歷史","介紹","內容","文化","活動","官網","網站","資訊","限時","外送","附近"],
    "價錢":["價格","票價","多少錢","錢","貴","便宜","花費","費用","花"],
    "wifi":["wifi","WIFI","Wifi","網路","上網","無線"],
    "菜單":["菜單","餐點","低消","飲料","葷","素","蛋奶素","食物"],
    "評價":["評價","好吃","好玩","有趣"],
    "充電":["插座","充電","電源","電","手機"],
    "乘車":["搭乘","搭","車子","公車","坐","站","到","多久","多少時間"],
    "plane":["飛機", "航班", "延誤"],
    "高捷":["高捷","高雄捷運"],
    "高鐵":["高鐵","高速鐵路"],
    "台鐵":["台鐵","臺鐵","火車","台灣鐵路","臺灣鐵路","莒光號","自強號","普悠瑪","坐太魯閣","搭太魯閣"],
    "紫庭":["台灣科技大學"]}
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
D14 = len(dict["高鐵"])
D15 = len(dict["台鐵"])
D16 = len(dict["紫庭"])

# 將toolong檔案內文字轉換
# ?
toolongf_v = [line.strip().encode('utf-8') for line in open(r'D:\Moyege\Work\@PROJECT\1221Google_map\chatbot\chatbot\Scripts\testbot0326-20180327T043427Z-001\testbot0130\GooglemapBot\toolong.txt',encoding = 'utf8').readlines()]
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
                            # 避免傳送到自己的文字 idd=自己粉專id
                            post_facebook_message_text(message['sender']['id'], message['message']['text'])
                    elif toiletlong!='':
                        # 可以接收文字以外訊息 kkk是無意義文字
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
thsr_start=''
thsr_end=''
thsr_time_arrive=''
thsr_time_depart=''
tra_start=''
tra_end=''
tra_time_arrive=''
tra_time_depart=''
# print(last_state)
# print(idd)
# print('+++++++++++++++++++++++++++++') 
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
        #廁所(收到使用者位置後)
        for i1 in range(D1):
            if idcheck[idd].find(dict["toilet"][i1]) >= 0 and ans <= 0:
                toilet(i1,fbid,post_message_url)
                ans+=1

    # 檢測有無交通資訊類別需求關鍵字
    # 未完成實際內容
        for i13 in range(D13):
            if idcheck[idd].find(dict["高捷"][i13]) >= 0 and ans<=0:
                kao(i13,fbid,post_message_url,recevied_message)
                ans=ans+1

        for i14 in range(D14):
            if idcheck[idd].find(dict["高鐵"][i14]) >= 0 and ans<=0:
                thsr(i14,fbid,post_message_url,recevied_message)
                ans=ans+1

        for i15 in range(D15):
            if idcheck[idd].find(dict["台鐵"][i15]) >= 0 and ans<=0:
                global tra_start,tra_end,tra_time_depart,tra_time_arrive
                print('7777777777888888888777777')
                print('tra_start')
                print('777777777788888888777777')
                # station = []

                trastation=['基隆','新豐','員林','永康','三坑','竹北','永靖','大橋','八堵','北新竹',
                '社頭','臺南','七堵','新竹','田中','保安','百福','三姓橋','二水','仁德','五堵','香山',
                '林內','中洲','汐止','崎頂','石榴','大湖','汐科','竹南','斗六','路竹','南港','造橋',
                '斗南','岡山','松山','豐富','石龜','橋頭','臺北','苗栗','大林','楠梓','萬華','南勢',
                '民雄','新左營','板橋','銅鑼','嘉北','左營','浮洲','三義','嘉義','高雄','樹林','泰安',
                '水上','鳳山','南樹林','后里','南靖','後庄','山佳','豐原','後壁','九曲堂','鶯歌','潭子',
                '新營','六塊厝','桃園','太原','柳營','屏東','內壢','臺中','林鳳營','中壢','大慶','隆田','埔心',
                '烏日','拔林','楊梅','新烏日','善化','富岡','成功','南科','新富','彰化','新市','北湖','花壇',
                '湖口','大村','基隆','談文','大山','後龍','龍港','白沙屯','新埔','通霄','苑裡','日南','大甲',
                '臺中港','清水','沙鹿','龍井','大肚','追分','彰化','八堵','羅東','南平','暖暖','冬山','鳳林',
                '四腳亭','新馬','萬榮','瑞芳','蘇澳新站','光復','猴硐','永樂','大富','三貂嶺','東澳','富源',
                '牡丹','南澳','瑞穗','雙溪','武塔','三民','貢寮','漢本','玉里','福隆','和平','東里','石城',
                '和仁','東竹','大里','崇德','富里','大溪','新城','池上','龜山','景美','海端','外澳','北埔',
                '關山','頭城','花蓮','瑞和','頂埔','吉安','瑞源','礁溪','志學','鹿野','四城','平和','山里',
                '宜蘭','壽豐','臺東','二結','豐田','中里','蘇澳新','蘇澳','屏東','歸來','麟洛','西勢','竹田',
                '潮州','崁頂','南州','鎮安','林邊','佳冬','東海','枋寮','加祿','內獅','枋山','古莊','大武',
                '瀧溪','金崙','太麻里','知本','康樂','臺東','三貂嶺','大華','十分','望古','嶺腳','平溪','菁桐','新竹',
                '北新竹','千甲','新莊','竹中','上員','榮華','竹東','橫山','九讚頭','合興','富貴','內灣','二水','源泉',
                '濁水','龍泉','集集','水里','車埕','成功','追分','中洲','長榮大學','沙崙','竹中','六家','瑞芳','海科館',
                '八斗子']
                print('來來第一步')
            # response_text = "您附近的廁所有以下這些"
                # for Kaocount in range(0,1):
                #     station.append(recevied_message)
                #     print(station)
                if tra_end=='' and tra_start!='':
                    tranumber=len(trastation)
                    kk=0
                    for tra in range(tranumber):
                        if recevied_message == trastation[tra]: 
                            tra_end=recevied_message
                            with open(r'D:\Moyege\Work\@PROJECT\1221Google_map\chatbot\chatbot\Scripts\testbot0326-20180327T043427Z-001\testbot0130\GooglemapBot\jsondata\時刻表\Train_180223.json', 'r', encoding="utf-8") as f:
                                tradata = json.load(f)
                            traa = len(tradata) #計算整個json檔有幾筆資料, 也就是總共有幾班列車, a=921
                            #print(a)

                            print('以下為從【'+tra_start+'】前往【'+tra_end+'】的所有班次：\n')
                            print('車次\t'+'開車時間\t'+'抵達時間')
                            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'以下為從【'+tra_start+'】前往【'+tra_end+'】的所有班次：\n'}})
                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'車次\t'+'開車時間\t'+'抵達時間'}})
                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

                            tralist1 = []
                            tralist2 = []
                            tralist3 = []
                            tralist4 = []

                            for trai in range(traa):
                                trab = len(tradata[trai]['StopTimes']) #計算第i班列車有幾個停靠站
                                #print(b)
                                for traj in range(trab): #第i筆資料裡的StopTimes(時刻表)裡的第j筆資料
                                    if tradata[trai]['StopTimes'][traj]['StationName']['Zh_tw'] == tra_start: #該班次會在上車車站停靠
                                        trak = traj + 1 #避免列車行駛方向錯誤
                                        for trak in range(trak, trab):
                                            if tradata[trai]['StopTimes'][trak]['StationName']['Zh_tw'] == tra_end: #該班次會在下車車站停靠
                                                tralist1.append(str(tradata[trai]['DailyTrainInfo']['TrainNo'])) #將車次號碼存到list1
                                                tralist2.append(tradata[trai]['StopTimes'][traj]['DepartureTime']) #將上車車站的開車時間存到list2
                                                tralist3.append(tradata[trai]['StopTimes'][trak]['ArrivalTime']) #將下車車站的抵達時間存到list3

                            #print(list1)
                            #print(list2)
                            #print(list3)

                            trac = len(tralist1) #總共有幾班符合使用者需求的火車
                            #print(c)

                            #將同一台火車的資料合併
                            for trax in range(trac):
                                tralist4.append(tralist2[trax]+tralist3[trax]+tralist1[trax])

                            #將資料以開車時間做排序後再把合併過的資料拆開來印出
                            for tray in range(trac):
                                tralist4.sort()
                                print(tralist4[tray][10:]+'\t', tralist4[tray][0:5]+'\t', tralist4[tray][5:10])
                                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":tralist4[tray][10:]+'\t'+tralist4[tray][0:5]+'\t'+tralist4[tray][5:10]}})
                                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                                print(endstation)
                        else:
                            if kk == tranumber-1:
                                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"搞毛阿整老子??沒這個台鐵站阿!!"}})
                                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                                print("5555555500000005555555555")
                            kk+=1
                if tra_start=='':
                    print('6666666666666666666666666')
                    tranumber=len(trastation)
                    kk=0
                    for tra in range(tranumber): 
                        if recevied_message == trastation[tra]:
                            tra_start=recevied_message
                            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"那要在哪裡下車呢?"}})
                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                            print(thsr_start)
                        else:
                            if kk == tranumber-1:
                                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"搞毛阿整老子??沒這個台鐵站阿!!"}})
                                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                                print("556655665566")
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
        for i16 in range(D16):
            if sentence.find(dict["紫庭"][i16]) >= 0 and ans <= 0:
            # response_text = "您附近的廁所有以下這些"
                last_state=recevied_message
                # idcheck.update({idd:recevied_message})
                # print('-----------------------------------------------------')
                # print(idd)
                # print('-----------------------------------------------------')
                # print(idcheck)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"紫庭紫庭"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                message_contents(fbid, recevied_message)
                # fb_handle_message()
                # if message2=="台北":
                #     response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"幫你找台北廁所"}})
                #     status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                # else:
                #     response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"有成功但是不是台北喔"}})
                #     status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

                ans=ans+1
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
        for i14 in range(D14):
            if sentence.find(dict["高鐵"][i14]) >= 0 and ans <= 0:
            # response_text = "您附近的廁所有以下這些"
                last_state=recevied_message
                idcheck.update({idd:recevied_message})
                print(recevied_message)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"請問你要在哪裡上車?(高鐵)"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                # fb_handle_message()
                # if message2=="台北":
                #     response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"幫你找台北廁所"}})
                #     status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                # else:
                #     response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"有成功但是不是台北喔"}})
                #     status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

                ans=ans+1
        for i15 in range(D15):
            if sentence.find(dict["台鐵"][i15]) >= 0 and ans <= 0:
            # response_text = "您附近的廁所有以下這些"
                last_state=recevied_message
                idcheck.update({idd:recevied_message})
                print(recevied_message)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"請問你要在哪裡上車?(台鐵)"}})
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

def toilet(i1, fbid, post_message_url):
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
            if ((float(toiletdata[i]['Latitude'])-a)**2+(float(toiletdata[i]['Longitude'])-b)**2) < 0.000020295025:    #0.00000901度 = 1公尺 500m
                print(toiletdata[i]['Name']+'，地址是'+toiletdata[i]['Address'])
                toiletans=toiletans+1
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":toiletdata[i]['Name']+'，地址是'+toiletdata[i]['Address']}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        if toiletans==0 :
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'不好意思，這附近沒有廁所餒'}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        toiletans=0
        toiletlong=''
        toiletlat=''
        del idcheck[idd]


def kao(i13,fbid,post_message_url,recevied_message):
    global stationtime,startstation,endstation

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
def thsr(i14,fbid,post_message_url,recevied_message):
    global thsr_start,thsr_end,thsr_time_depart,thsr_time_arrive

    thsrstation=['南港','台北','板橋','桃園','新竹','苗栗','台中','彰化','雲林','嘉義',
    '台南','左營']
    thsrtime=['00','01','02','03','04','05','06','07','08','09',
    '10','11','12','13','14','15','16','17','18','19',
    '20','21','22','23','24']
    if thsr_time_depart=='' and thsr_end!='':
        kk=0
        for thsrhour in range(25):
            if recevied_message ==thsrtime[thsrhour]:                            
                thsr_time_depart=recevied_message
                thsr_time_arrive=''
                print(thsr_time_depart)
                with open(r'D:\Moyege\Work\@PROJECT\1221Google_map\chatbot\chatbot\Scripts\testbot0326-20180327T043427Z-001\testbot0130\GooglemapBot\jsondata\時刻表\HSR_180227.json', 'r', encoding="utf-8") as f:
                    data = json.load(f)
                today = time.strftime("%A")
                thsra = len(data)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'以下是【出發時間】為【'+thsr_time_depart+'點】'+'從【'+thsr_start+'】前往【'+thsr_end+'】的所有班次：\n'}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'車次\t'+'出發時間\t'+'抵達時間'}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                print('車次\t'+'出發時間\t'+'抵達時間')

                list1 = []
                list2 = []
                list3 = []
                list4 = []
                 
                for thsri in range(thsra):
                    thsrb = len(data[thsri]['StopTimes']) #計算第i班高鐵有幾個停靠站
                    #print(b)
                    for thsrj in range(thsrb): #第i班列車的StopTimes(時刻表)裡的第j筆資料
                        if data[thsri]['StopTimes'][thsrj]['StationName']['Zh_tw'] == thsr_start: #該班次會在上車車站停靠
                            thsrk = thsrj + 1
                            for thsrk in range(thsrk,thsrb):
                                if data[thsri]['StopTimes'][thsrk]['StationName']['Zh_tw'] == thsr_end: #該班次會在下車車站停靠
                                    if thsr_time_arrive.strip() == '': #以下車時間的空值與否來判斷出發時間是否有值，並以此時間作為搜尋條件
                                        thsrm = data[thsri]['StopTimes'][thsrj]['ArrivalTime'].find(thsr_time_depart) #在data[i]['StopTimes'][j]['ArrivalTime']裡找尋和depart_time相符的值在第幾位，並存到m
                                        #print(m)
                                        if 2 > thsrm >= 0: #若無符合內容，m會等於-1，反之為0或1
                                            list1.append(str(data[thsri]['DailyTrainInfo']['TrainNo'])) #將車次號碼存到list1；因為車號是int，故需轉為str
                                            list2.append(data[thsri]['StopTimes'][thsrj]['DepartureTime']) #將上車車站的出發時間存到list2
                                            list3.append(data[thsri]['StopTimes'][thsrk]['ArrivalTime']) #將下車車站的抵達時間存到list3
                                    elif thsr_time_depart.strip() == '': #以上車時間的空值與否來判斷抵達時間是否有值，並以此時間作為搜尋條件
                                        thsrm = data[thsri]['StopTimes'][thsrk]['ArrivalTime'].find(thsr_time_arrive)
                                        #print(m)
                                        if 2 > thsrm >= 0:
                                            list1.append(str(data[thsri]['DailyTrainInfo']['TrainNo']))
                                            list2.append(data[thsri]['StopTimes'][thsrj]['DepartureTime'])
                                            list3.append(data[thsri]['StopTimes'][thsrk]['ArrivalTime'])
                                    else: #若兩者皆有值，便以出發時間作為搜尋條件
                                        thsrm = data[thsri]['StopTimes'][thsrj]['ArrivalTime'].find(thsr_time_depart)
                                        #print(m)
                                        if 2 > thsrm >= 0:
                                            list1.append(str(data[thsri]['DailyTrainInfo']['TrainNo']))
                                            list2.append(data[thsri]['StopTimes'][thsrj]['DepartureTime'])
                                            list3.append(data[thsri]['StopTimes'][thsrk]['ArrivalTime'])       
                                                 
                thsrc = len(list1)
                                                 
                for thsrx in range(thsrc):
                    list4.append(list2[thsrx]+list3[thsrx]+list1[thsrx])

                for thsry in range(thsrc):
                    list4.sort()
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":list4[thsry][10:]+'\t'+list4[thsry][0:5]+'\t'+list4[thsry][5:10]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    print(list4[thsry][10:]+'\t',list4[thsry][0:5]+'\t',list4[thsry][5:10])
                last_state = ''
                del idcheck[idd]
            else:
                print('else 外')
                if kk == 24:
                    print('else 裡')
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"搞毛阿整老子??高鐵時間觀念有問題阿??"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    print("555555555555555555")
                kk+=1


    if thsr_end=='' and thsr_start!='':
        thsrnumber=len(thsrstation)
        kk=0
        for thsr in range(thsrnumber):
            if recevied_message == thsrstation[thsr]: 
                thsr_end=recevied_message
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"您的乘車時間是幾點呢?(00-24)"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                print(endstation)
            else:
                if kk == thsrnumber-1:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"搞毛阿整老子??沒這個高鐵站阿!!"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    print("5555555500000005555555555")
                kk+=1
    if thsr_start=='':
        print('6666666666666666666666666')
        thsrnumber=len(thsrstation)
        kk=0
        for thsr in range(thsrnumber): 
            if recevied_message == thsrstation[thsr]:
                thsr_start=recevied_message
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"那要在哪裡下車呢?"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                print(thsr_start)
            else:
                if kk == thsrnumber-1:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"搞毛阿整老子??沒這個高鐵站阿!!"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    print("556655665566")
                kk+=1

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
# Google Places API Web Service Details
def GMap_place_detailssearch(center):


    ### id search
    GM_API_KEY = 'AIzaSyA35lPzOmBYaGtsGnu1BtuZiWqZcLpYdQk'

    G_query = center.replace(' ', '+')
    G_language = 'zh-TW'

    id_nav_request = 'query={}&language={}&key={}'.format(G_query, G_language, GM_API_KEY)
    id_request = "https://maps.googleapis.com/maps/api/place/textsearch/json?" + id_nav_request

    print(id_request)
    # url中不可包含中文等無法處理之字→需轉換成「%XX」
    # urllib.parse.quote(string, safe='/', encoding=None, errors=None)
    # https://www.zhihu.com/question/22899135       https://docs.python.org/3/library/urllib.parse.html#url-quoting。    
    request_trans = urllib.parse.quote(id_request, safe = string.printable)
    respone = urllib.request.urlopen(request_trans).read()
    id_directions = json.loads(respone.decode('utf-8'))

    id_results = id_directions['results']
    place_id = id_results[0]['place_id']
    print("111111111111111111111111111111111111111111111111111111111111111111111111111111")
    print(place_id)
    print("111111111111111111111111111111111111111111111111111111111111111111111111111111")

    ### detail search
    dt_nav_request = 'placeid={}&language={}&key={}'.format(place_id, G_language, GM_API_KEY)
    dt_request = "https://maps.googleapis.com/maps/api/place/details/json?" + dt_nav_request

    print(dt_request)
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

    return response
def message_contents(fbid, sentence):
    
    # recevied_message = ""
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN

    # google可抓取類別：名稱(0)、電話(1)、地址(2)、營業時間(3)、評價(4)、網站(5)、googlemap頁面(6)    
    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"在Google Map上查詢：\n" + GMap_place_detailssearch(sentence)[6]}})
    # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"輸入的文字為：" + sentence}})
    
    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)