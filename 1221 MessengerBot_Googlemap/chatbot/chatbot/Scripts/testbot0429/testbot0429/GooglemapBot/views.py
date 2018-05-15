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
dict={"location":["去","往哪","在哪裡","在哪","哪","位置","地址","地點","方向","怎麼走","走"],
    "toilet":["廁所","尿","大便","拉屎","屎","撇條","排遺","排泄","便便","便所","化妝室","洗手間","大號","尿急","棒賽","尿尿"],
    "營業時間":["營業時間","幾點關門","幾點","入場","關門","時間","開始","開放","幾號"],
    "電話":["電話","專線","號碼","連絡","聯絡"],
    "介紹":["簡介","特色","高度","長度","多高","多長","歷史","介紹","內容","文化","活動","官網","網站","資訊","限時","外送"],
    "價錢":["價格","票價","多少錢","錢","貴","便宜","花費","費用","花"],
    "wifi":["wifi","WIFI","Wifi","網路","上網","無線","Wi-Fi"],
    "菜單":["菜單","餐點","低消","飲料","葷","素","蛋奶素","食物","網站"],
    "評價":["評價","好吃","好玩","有趣"],
    "充電":["插座","充電","電源","電","手機","網站","網址","網頁"],
    "乘車":["搭乘","搭","車子","公車","坐","站","到","多久","多少時間"],
    "plane":["飛機", "航班", "延誤"],
    "高捷":["高捷","高雄捷運"],
    "高鐵":["高鐵","高速鐵路","高鐵票","高鐵的票"],
    "台鐵":["台鐵","臺鐵","火車","台灣鐵路","臺灣鐵路","莒光號","自強號","普悠瑪","坐太魯閣","搭太魯閣","台鐵票","臺鐵票","火車票"],
    "問題":["沒問題了","我還有問題","我有建議要說","Jerry能幫你什麼"],
    "演唱會":["演唱會"],
    "ATM":["ATM","atm","Atm","轉帳","領錢","提款","金融卡"],
    "你好":["你好","你好阿","你好嗎","你好哇","早安","午安","晚安","哈囉","嗨","你可以幹嘛","測試","test","hi","hello","哈摟","回答","你可以做什麼？","你好喔"]}

idcheck={}
longlat={}

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
D16 = len(dict["你好"])
D17 = len(dict["問題"])
D18 = len(dict["演唱會"])
D19 = len(dict["ATM"])

# 將toolong檔案內文字轉換
# ?
toolongf_v = [line.strip().encode('utf-8') for line in open(r'D:\Moyege\Work\@PROJECT\1221Google_map\chatbot\chatbot\Scripts\testbot0429\testbot0429\GooglemapBot\toolong.txt',encoding = 'utf8').readlines()]
idd=''
toiletlat=''
toiletlong=''
vba = []
nba = {}
wrongcheck=0
seq=0
seq_2=0
seq_3=0
seq_4=0
firsttime={}
user_payload=''
address_add_num = 0
else_add_num = 0
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
        global toiletlat,toiletlong,idd,seq,seq_2,seq_3,user_payload,seq_4
        # user_details_url_test = "https://graph.facebook.com/v2.6/me/messenger_profile?access_token="+PAGE_ACCESS_TOKEN
        # user_details_params_test = {'fields':'first_name,last_name,profile_pic,get_started,greeting', 'access_token':PAGE_ACCESS_TOKEN}
        # user_details_test = requests.get(user_details_url_test, user_details_params_test).json()
        # print(toiletlat)
        # print('latlatlatlatlatlatlatlatuuuuuuuuuuuuuuuuu')
        # print(toiletlong)
        # print("longlonglonglonglonglonglongppppppppppppppp")
        # print("\n\n\n")
        # print(incoming_message)
        # print("\n\n\n")
        # print(incoming_message['entry'][0]['messaging'])
        if 'message' in incoming_message['entry'][0]['messaging'][0]:
            if 'attachments' in incoming_message['entry'][0]['messaging'][0]['message']:
                if 'payload' in incoming_message['entry'][0]['messaging'][0]['message']['attachments'][0]:
                    if 'coordinates' in incoming_message['entry'][0]['messaging'][0]['message']['attachments'][0]['payload']:
                        seq = incoming_message['entry'][0]['messaging'][0]['message']['seq']
                        if seq != seq_2:
                            toiletlat=incoming_message['entry'][0]['messaging'][0]['message']['attachments'][0]['payload']['coordinates']['lat']
                            toiletlong=incoming_message['entry'][0]['messaging'][0]['message']['attachments'][0]['payload']['coordinates']['long']
                            seq_2 = seq
                        # latlist.append(toiletlat)
                        # longlist.append(toiletlong)
        if 'message' in incoming_message['entry'][0]['messaging'][0]:
            if 'quick_reply' in incoming_message['entry'][0]['messaging'][0]['message']:
                if seq != seq_4 :
                    user_payload=incoming_message['entry'][0]['messaging'][0]['message']['quick_reply']['payload']
                    seq_4 = seq


        # del latlist,longlist
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

                    # Print the message to the terminal

                    if 'text' in message ['message']:
                        # 顯示message此JSON檔內容
                            # {'timestamp':__, //作用未知
                            #  'message': 
                            #       {'mid': '__', //會變動，作用未知
                            #        'text': '__', //收到傳送的message訊息
                            #        'is_echo': True, //固定為True，作用未知
                            #        'app_id': __, //連結到的應用程式編號
                            #        'seq': __}, //會變動，作用未知
                            # 'sender': {'id': '__'}, //粉專ID
                            # 'recipient': {'id': '__'}} //訊息傳送者ID
                            # {'error': {
                            #   'code': 100, //固定，作用未知
                            #   'error_subcode': 2018001, //固定，作用未知
                            #   'message': '(#100) No matching user found', //固定，作用未知
                            #   'type': 'OAuthException', //固定，作用未知
                            #   'fbtrace_id': '__'}} //會變動，作用未知
                        # print(message)

                        # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                        # are sent as attachments and must be handled accordingly.
                        idd=message['sender']['id']
                        seq = incoming_message['entry'][0]['messaging'][0]['message']['seq']
                        if idd!='1778286295798129' and seq != seq_3:
                            # 避免傳送到自己的文字 idd=自己粉專id
                            post_facebook_message_text(message['sender']['id'], message['message']['text'])
                            print(idd)
                            seq_3 = seq
                    elif toiletlong!='':
                        # 可以接收文字以外訊息 kkk是無意義文字
                        idd=message['sender']['id']
                        if idd!='1778286295798129':
                            longlat.update({idd:[toiletlong,toiletlat]})
                            print(longlat)
                            print("testtesttesttesttesttesttesttesttesttest")
                            post_facebook_message_text(message['sender']['id'], 'kkk')
                            # del latlist[0],longlist[0]
                            print("非文字唷")                


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


# 檢測冗字(JIEBA) 將輸入文字斷成詞語
def jieba_check(long_sentence):
    allba = []
    global vba,nba
    print(type(nba))
    
    jieba.load_userdict(r"D:\Moyege\Work\@PROJECT\1221Google_map\chatbot\chatbot\Scripts\testbot0429\testbot0429\GooglemapBot\jieba.txt")
    vocabulary = jieba.posseg.cut(long_sentence)

    for iba in vocabulary:
        allba.append((iba.word))
        print(iba.word,iba.flag)
        if iba.flag == 'vbuy':
            vba.append(('買'))
        if  iba.flag == 'ns':
            nba.update({idd:iba.word})
            print(nba)
            print("這裡是nba這裡是nba這裡是nba這裡是nba這裡是nba這裡是nba這裡是nba這裡是nba這裡是nba")

    return allba

#last_state = ''
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
address_add_name = '' #給建議用
address_add_text = '' #給建議用
# def getstart(fbid,recevied_message,post_message_url):

#     if idd in firsttime:
#         print("用過了拉用過了拉")
#     else:
#         firsttime.update({idd:['used']})
#         response_msg = json.dumps({"recipient":{"id":fbid},"message":{"greeting":[
#         {
#              "locale":"default",
#              "text":"Hello!",
#         },
#         {
#             "locale":"zh_TW",
#             "text":"哈囉哈囉你好挖"
#         }
#         ]
#         }, 
#         "get_started":{"payload":"<GET_STARTED_PAYLOAD>"}
#         })
#         status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
def check_dict(fbid, recevied_message):
    global vba, nba,user_payload
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

    # sentence = jieba_check(recevied_message)
    #結巴會怪怪澳改(在哪ˋ)
    # getstart(fbid,recevied_message,post_message_url)
    sentence_ba=[]
    sentence_ba=jieba_check(recevied_message)
    sentence=recevied_message
    # 檢測是否為多輪回答


    if idd in idcheck:
        #要把二次傳的訊息加到idd裡面喔喔喔喔喔喔喔喔喔
        print("進idcheck了進idcheck了進idcheck了進idcheck了進idcheck了進idcheck了")
        print("\n\n\n")
        print(idcheck)
        print("\n\n\n")

        #廁所(收到使用者位置後)--------------------------------------------------徹底完成了 除了toilet json檔
        for i1 in range(D1):
            if idcheck[idd].find(dict["toilet"][i1]) >= 0 and ans <= 0:
                toilet(idd,post_message_url)
                ans += 2

        # 高捷多輪回答
        for i13 in range(D13):
            if idcheck[idd].find(dict["高捷"][i13]) >= 0 and ans<=0:
                kao(i13,fbid,post_message_url,recevied_message)
                ans += 2

        # 高鐵多輪回答 -------------台
        for i14 in range(D14):
            if idcheck[idd].find(dict["高鐵"][i14]) >= 0 and ans<=0 and '買' not in vba:
                thsr(i14,fbid,post_message_url,recevied_message)
                ans += 2

        # 臺鐵多輪回答----臺
        for i15 in range(D15):
            if idcheck[idd].find(dict["台鐵"][i15]) >= 0 and ans<=0 and '買' not in vba:
                tra(i15,fbid,post_message_url,recevied_message)
                ans += 2

        #ATM多輪回答
        for i19 in range(D19):
            if idcheck[idd].find(dict["ATM"][i19]) >= 0 and ans <= 0:
                ATM(idd,post_message_url)
                ans += 2

        # for i2 in range(D2):
        #     if sentence.find(dict["乘車"][i2]) >= 0 and ans <= 0:
        #         dle = sentence.find(dict["乘車"][i2])
        #         dle_long = len(dict["乘車"][i2])
        #         dle2 = dle + dle_long
        #         sentence = sentence[:dle] + sentence[dle2:]
        #         # response_text = "以下是" + recevied_message + "的交通資訊"
        #         if not last_state:
        #             response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的交通資訊"}})
        #             last_state = recevied_message
        #         else:
        #             response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + last_state + "的交通資訊"}})
        #             last_state = ''
        #         status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        #         ans = ans + 1

        # 檢測有無查價類別需求關鍵字
        # 未完成實際內容
        # for i3 in range(D3):
        #     if sentence.find(dict["價錢"][i3]) >= 0 and ans <= 0:
        #         dle = sentence.find(dict["價錢"][i3])
        #         dle_long = len(dict["價錢"][i3])
        #         dle2 = dle + dle_long
        #         sentence = sentence[:dle] + sentence[dle2:]
        #         # response_text = "以下是" + recevied_message + "的價錢資訊"
        #         response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的價錢資訊"}})
        #         status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        #         ans += 2

        # # 檢測有無查店家介紹類別需求關鍵字
        # # 未完成實際內容
        # for i7 in range(D7):
        #     if sentence.find(dict["介紹"][i7]) >= 0 and ans <= 0:
        #         dle = sentence.find(dict["介紹"][i7])
        #         dle_long = len(dict["介紹"][i7])
        #         dle2 = dle + dle_long
        #         sentence = sentence[:dle] + sentence[dle2:]
        #         # response_text = "以下是" + recevied_message + "的相關資訊"
        #         response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的相關資訊"}})
        #         status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        #         ans += 2

        # 檢測有無查wifi類別需求關鍵字
        for i8 in range(D8):
            if idcheck[idd].find(dict["wifi"][i8]) >= 0 and ans<=0:
                wifi(idd, post_message_url)
                ans += 2
     
        # # 檢測有無查店家菜單資訊類別需求關鍵字
        # # 未完成實際內容           
        # for i9 in range(D9):
        #     if sentence.find(dict["菜單"][i9]) >= 0 and ans <= 0:
        #         dle = sentence.find(dict["菜單"][i9])
        #         dle_long = len(dict["菜單"][i9])
        #         dle2 = dle + dle_long
        #         sentence = sentence[:dle] + sentence[dle2:]
        #         # response_text = "以下是" + recevied_message + "的菜單資訊"
        #         response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的菜單資訊"}})
        #         status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        #         ans += 2

        # # 檢測有無查充電類別需求關鍵字
        # # 未完成實際內容     
        # for i11 in range(D11):
        #     if sentence.find(dict["充電"][i11]) >= 0 and ans <= 0:
        #         dle = sentence.find(dict["充電"][i11])
        #         dle_long = len(dict["充電"][i11])
        #         dle2 = dle + dle_long
        #         sentence = sentence[:dle] + sentence[dle2:]
        #         # response_text = "以下是充電資訊"
        #         response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是充電資訊"}})
        #         status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        #         ans += 2


        # # 檢測有無查詢航班需求之關鍵字
        # # 雲端期末報告結合
        # # 應用IBM相關套件完成
        # for i12 in range(D12):
        #     if sentence.find(dict["plane"][i12]) >= 0 and ans <= 0:
        #         dle = sentence.find(dict["plane"][i12])
        #         dle_long = len(dict["plane"][i12])
        #         dle2 = dle + dle_long
        #         sentence = sentence[:dle] + sentence[dle2:]
        #         # response_text = "以下是充電資訊"
        #         response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下為航班延誤資訊：\n http://pysparkwebappredfinal.mybluemix.net/dsxinsights"}})
        #         status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        #         ans += 2

        for i17 in range(D17):
            if idcheck[idd].find(dict["問題"][i17]) >= 0 and ans <= 0:
                if user_payload != '':
                    global address_add_num,else_add_num,address_add_name,address_add_text
                    if address_add_name != '' and address_add_text == '':
                        address_add_text = recevied_message
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"謝謝學長~你是全天下最好的人^^"}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        response_msg = json.dumps({"recipient":{"id":1502184393150744},"message":{"text":"廢物，有人說地點建議:\n地點:" + address_add_name+"\n詳細資訊:"+address_add_text}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        anyQuestion(fbid,post_message_url)
                        del idcheck[idd]
                        user_payload = ''
                        address_add_num = 0
                        ans += 2
                    elif address_add_text == '' and address_add_name == '' and address_add_num == 1:
                        address_add_num = 2
                        address_add_name = recevied_message
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"請輸入其他描述"}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    elif user_payload=='<adress_suggest>' and address_add_name == '' and address_add_text == '' and address_add_num == 0:
                        address_add_num = 1
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"請輸入地點"}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    elif user_payload=='<else_suggest>':
                        if else_add_num==1:
                            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"謝謝學長~你是全天下最好的人^^"}})
                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                            response_msg = json.dumps({"recipient":{"id":1502184393150744},"message":{"text":"帥哥，有人說其他建議:\n" + recevied_message}})
                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                            anyQuestion(fbid,post_message_url)
                            del idcheck[idd]
                            user_payload = ''
                            else_add_num = 0
                            ans += 2
                        else:
                            else_add_num+=1
                            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"請說你的建議"}})
                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                else:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"謝謝學長~你是全天下最好的人^^"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":1502184393150744},"message":{"text":"廢物，有人說其他建議:\n" + recevied_message}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    anyQuestion(fbid,post_message_url)
                    del idcheck[idd]
                    ans += 2







    else:
        # 接收到廁所
        for i1 in range(D1):
            for b1 in range(len(sentence_ba)):
                if dict["toilet"][i1]==sentence_ba[b1] and ans <= 0:
                    idcheck.update({idd:dict["toilet"][i1]})
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"學長學長，你要問的地方是哪裡呀<3","quick_replies":[
                        # {
                        #      "content_type":"text",
                        #      "title":"搜尋",
                        #      "payload":"<POSTBACK_PAYLOAD>"
                        # },
                        {
                            "content_type":"location",
                            "title":"傳送地點"
                        }
                        ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1
                    b1 = len(sentence_ba)

        # 檢測有無查wifi類別需求關鍵字
        for i8 in range(D8):
            for b8 in range(len(sentence_ba)):
                if dict["wifi"][i8]==sentence_ba[b8] and ans <= 0:
                    idcheck.update({idd:dict["wifi"][i8]})
                    #message_contents(fbid,sentence,5,'網站，或許能給你一些幫助')
                    #anyQuestion(fbid,post_message_url)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"學長學長，你要問的地方是哪裡呀<3","quick_replies":[
                        {
                            "content_type":"location"
                        }
                        ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1
                    b8 = len(sentence_ba)

        # 檢測有無查wifi類別需求關鍵字
        for i19 in range(D19):
            for b19 in range(len(sentence_ba)):
                if dict["ATM"][i19]==sentence_ba[b19] and ans <= 0:
                    idcheck.update({idd:recevied_message})
                    #message_contents(fbid,sentence,5,'網站，或許能給你一些幫助')
                    #anyQuestion(fbid,post_message_url)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"學長跟我說說你要問的地方是哪裡吧","quick_replies":[
                        {
                            "content_type":"location"
                        }
                        ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1
                    b19 = len(sentence_ba)

        # 檢測有無查位置類別需求關鍵字（內容物為判斷地點位置）
        for i4 in range(D4):
            for b4 in range(len(sentence_ba)):
                if dict["location"][i4]==sentence_ba[b4] and ans <= 0:
                    if len(nba[idd]):
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + nba[idd] + "的位置資訊，\n" + "https://www.google.com.tw/maps/search/" + nba[idd]}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        post_facebook_message_media(fbid, GMap_map(nba[idd]))
                        message_contents(fbid,nba[idd],2,'地址')

                        vba = []
                        # del nba[idd]
                        ans += 1
                    else:
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"地圖找不到這個地方唷"}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        ans += 1

        # 接收到高捷
        for i13 in range(D13):
            for b13 in range(len(sentence_ba)):
                if dict["高捷"][i13]==sentence_ba[b13] and ans <= 0:
                    idcheck.update({idd:dict["高捷"][i13]})
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"請問你要在哪裡上車?(高捷)"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1

        # 接收到高鐵
        for i14 in range(D14):
            for b14 in range(len(sentence_ba)):
                if dict["高鐵"][i14]==sentence_ba[b14] and ans <= 0 and '買' in vba:
                    idcheck.update({idd:dict["高鐵"][i14]})
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"我沒買過高鐵票，但我可以給你它的連結～\nhttps://irs.thsrc.com.tw/IMINT/"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1
                    anyQuestion(fbid,post_message_url)
                    del idcheck[idd]
                    vba = []
                    del nba[idd]

                if dict["高鐵"][i14]==sentence_ba[b14] and ans <= 0:
                    print('沒有買的高鐵沒有買的高鐵沒有買的高鐵沒有買的高鐵沒有買的高鐵')
                    idcheck.update({idd:dict["高鐵"][i14]})
                    print(recevied_message)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"請問你要在哪裡上車?(高鐵)"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1

        # 接收到台鐵
        for i15 in range(D15):
            for b15 in range(len(sentence_ba)):
                if dict["台鐵"][i15]==sentence_ba[b15] and ans <= 0 and '買' in vba:
                    idcheck.update({idd:dict["台鐵"][i15]})
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"我沒買過台鐵票，但我可以給你它的連結～\nhttp://railway.hinet.net/Foreign/TW/index.html"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1
                    anyQuestion(fbid,post_message_url)
                    del idcheck[idd]
                    vba = []
                    del nba[idd]
                if dict["台鐵"][i15]==sentence_ba[b15] and ans <= 0:
                    idcheck.update({idd:dict["台鐵"][i15]})
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"請問你要在哪裡上車?(台鐵)"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1

        # for i2 in range(D2):
        #     if sentence.find(dict["乘車"][i2]) >= 0 and ans <= 0:
        #         dle = sentence.find(dict["乘車"][i2])
        #         dle_long = len(dict["乘車"][i2])
        #         dle2 = dle + dle_long
        #         sentence = sentence[:dle] + sentence[dle2:]
        #         response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的交通資訊"}})
        #         status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        #         anyQuestion(fbid,post_message_url)
        #         ans += 1

    # 檢測有無查價類別需求關鍵字
    # 未完成實際內容
        for i3 in range(D3):
            for b3 in range(len(sentence_ba)):
                if dict["價錢"][i3]==sentence_ba[b3] and ans <= 0 and idd in nba:
                    message_contents(fbid,nba[idd],5,'網站，或許能給你一些幫助')
                    # anyQuestion(fbid,post_message_url)
                    # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的菜單資訊"}})
                    # status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    b3 = len(sentence_ba)
                    ans += 1
                elif dict["價錢"][i3]==sentence_ba[b3] and ans <= 0 and idd not in nba:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"人家聽不懂你說什麼耶，還是你可以給人家一點建議呢~","quick_replies":[
                        {
                             "content_type":"text",
                             "title":"是",
                             "payload":"<QA_YES>"
                        },
                        {
                             "content_type":"text",
                             "title":"下次吧",
                             "payload":"<QA_NO>"
                        }
                        ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    b3 = len(sentence_ba)
                    ans += 1


    # 檢測有無查營業時間類別需求關鍵字
    # 未完成實際內容
        for i5 in range(D5):
            for b5 in range(len(sentence_ba)):
                if dict["營業時間"][i5]==sentence_ba[b5] and ans <= 0 and idd in nba:
                    message_contents(fbid,nba[idd],3,'營業時間')
                    # anyQuestion(fbid,post_message_url)
                    # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的菜單資訊"}})
                    # status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    b5 = len(sentence_ba)
                    ans += 1
                elif dict["營業時間"][i5]==sentence_ba[b5] and ans <= 0 and idd not in nba:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"人家聽不懂你說什麼耶，還是你可以給人家一點建議呢~","quick_replies":[
                        {
                             "content_type":"text",
                             "title":"是",
                             "payload":"<QA_YES>"
                        },
                        {
                             "content_type":"text",
                             "title":"下次吧",
                             "payload":"<QA_NO>"
                        }
                        ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    b5 = len(sentence_ba)
                    ans += 1

    # 檢測有無查營業電話類別需求關鍵字
    # 未完成實際內容
        for i6 in range(D6):               
            for b6 in range(len(sentence_ba)):
                if dict["電話"][i6]==sentence_ba[b6] and ans <= 0 and idd in nba:
                    message_contents(fbid,nba[idd],1,'電話')
                    # anyQuestion(fbid,post_message_url)
                    # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的菜單資訊"}})
                    # status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    b6 = len(sentence_ba)
                    ans += 1
                elif dict["電話"][i6]==sentence_ba[b6] and ans <= 0 and idd not in nba:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"人家聽不懂你說什麼耶，還是你可以給人家一點建議呢~","quick_replies":[
                        {
                             "content_type":"text",
                             "title":"是",
                             "payload":"<QA_YES>"
                        },
                        {
                             "content_type":"text",
                             "title":"下次吧",
                             "payload":"<QA_NO>"
                        }
                        ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    b6 = len(sentence_ba)
                    ans += 1

        # 檢測有無查店家介紹類別需求關鍵字
        # 未完成實際內容
        for i7 in range(D7):
            for b7 in range(len(sentence_ba)):
                if dict["介紹"][i7]==sentence_ba[b7] and ans <= 0 and idd in nba:
                    message_contents(fbid,nba[idd],5,'網站，或許能給你一些幫助')
                    # anyQuestion(fbid,post_message_url)
                    # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的菜單資訊"}})
                    # status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    b7 = len(sentence_ba)
                    ans += 1
                elif dict["介紹"][i7]==sentence_ba[b7] and ans <= 0 and idd not in nba:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"人家聽不懂你說什麼耶，還是你可以給人家一點建議呢~","quick_replies":[
                        {
                             "content_type":"text",
                             "title":"是",
                             "payload":"<QA_YES>"
                        },
                        {
                             "content_type":"text",
                             "title":"下次吧",
                             "payload":"<QA_NO>"
                        }
                        ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    b7 = len(sentence_ba)
                    ans += 1
     
        # 檢測有無查店家菜單資訊類別需求關鍵字
        # 未完成實際內容           
        for i9 in range(D9):
            for b9 in range(len(sentence_ba)):
                if dict["菜單"][i9]==sentence_ba[b9] and ans <= 0 and idd in nba:
                    message_contents(fbid,nba[idd],5,'網站，或許能給你一些幫助')
                    # anyQuestion(fbid,post_message_url)
                    # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的菜單資訊"}})
                    # status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    b9 = len(sentence_ba)
                    ans += 1
                elif dict["菜單"][i9]==sentence_ba[b9] and ans <= 0 and idd not in nba:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"人家聽不懂你說什麼耶，還是你可以給人家一點建議呢~","quick_replies":[
                        {
                             "content_type":"text",
                             "title":"是",
                             "payload":"<QA_YES>"
                        },
                        {
                             "content_type":"text",
                             "title":"下次吧",
                             "payload":"<QA_NO>"
                        }
                        ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    b10 = len(sentence_ba)
                    ans += 1

        # 檢測有無查店家評價類別需求關鍵字
        # 未完成實際內容      
        for i10 in range(D10):
            for b10 in range(len(sentence_ba)):
                if dict["評價"][i10]==sentence_ba[b10] and ans <= 0 and idd in nba:
                    message_contents(fbid,nba[idd],4,'評價')
                    # anyQuestion(fbid,post_message_url)
                    b10 = len(sentence_ba)
                # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的評價資訊"}})
                # status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1
                elif dict["評價"][i10]==sentence_ba[b10] and ans <= 0 and idd not in nba:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"人家聽不懂你說什麼耶，還是你可以給人家一點建議呢~","quick_replies":[
                        {
                             "content_type":"text",
                             "title":"是",
                             "payload":"<QA_YES>"
                        },
                        {
                             "content_type":"text",
                             "title":"下次吧",
                             "payload":"<QA_NO>"
                        }
                        ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    b10 = len(sentence_ba)
                    ans += 1


        # 檢測有無查充電類別需求關鍵字
        # 未完成實際內容     
        for i11 in range(D11):
            for b11 in range(len(sentence_ba)):
                if dict["充電"][i11]==sentence_ba[b11] and ans <= 0 and idd in nba:
                    message_contents(fbid,nba[idd],5,'網站，或許能給你一些幫助')
                    b11 = len(sentence_ba)
                    # anyQuestion(fbid,post_message_url)
                    # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是充電資訊"}})
                    # status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1
                elif dict["充電"][i11]==sentence_ba[b11] and ans <= 0 and idd not in nba:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"人家聽不懂你說什麼耶，還是你可以給人家一點建議呢~","quick_replies":[
                        {
                             "content_type":"text",
                             "title":"是",
                             "payload":"<QA_YES>"
                        },
                        {
                             "content_type":"text",
                             "title":"下次吧",
                             "payload":"<QA_NO>"
                        }
                        ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    b11 = len(sentence_ba)
                    ans += 1


        # 檢測有無查詢航班需求之關鍵字
        # 雲端期末報告結合
        # 應用IBM相關套件完成
        # for i12 in range(D12):
        #     if sentence.find(dict["plane"][i12]) >= 0 and ans <= 0:
        #         dle = sentence.find(dict["plane"][i12])
        #         dle_long = len(dict["plane"][i12])
        #         dle2 = dle + dle_long
        #         sentence = sentence[:dle] + sentence[dle2:]
        #         # response_text = "以下是充電資訊"
        #         response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下為航班延誤資訊：\n http://pysparkwebappredfinal.mybluemix.net/dsxinsights"}})
        #         status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        #         anyQuestion(fbid,post_message_url)
        #         ans += 1

        # for i18 in range(D18):
        #     for b18 in range(len(sentence_ba)):
        #         if dict["演唱會"][i18]==sentence_ba[b18] and ans <= 0 :
        #             show(fbid, post_message_url)
        #             ans += 1
        for i16 in range(D16):
            for b16 in range(len(sentence_ba)):
                if dict["你好"][i16]==sentence_ba[b16] and ans <= 0:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你好~很高興認識你^^\n我是你的旅遊小助手，\n可以幫你解決旅遊途中或生活上的疑難雜症唷。\n你可以問我廁所在哪、\n某個你想去你地方的地址、餐廳的評價、高鐵台鐵高捷怎麼搭、附近有沒有ATM或是wifi、甚至是最近的演唱會都能幫你找到喔~"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1

        #回答完問題後檢測使用者是否繼續問
        for i17 in range(D17):
            if sentence.find(dict["問題"][i17]) >= 0 and ans <= 0:
                # response_text = "以下是充電資訊"
                if recevied_message=="沒問題了":
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"太好了，下次別問了，好累zzzz"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                elif recevied_message=="我還有問題":
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"有問題去看醫生啦\n好啦有問題直接說:)"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                elif recevied_message=="我有建議要說":
                    idcheck.update({idd:recevied_message})
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"好的，為了能更完善的服務你\n我什麼都願意聽"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                else :
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"我是一個出門在外的好幫手,任何相關問題都可以問我看看~\n我能幫你找位置、廁所、停車場等等,也能幫你查評價、網址。\n有想知道的問問看就對了!!\n詳細資訊:\nhttps://www.facebook.com/profile.php?id=100000116123964"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                ans += 1
                recevied_message = ''
    if user_payload != '':
        if user_payload=='<QA_YES>':
            idcheck.update({idd:"我有建議要說"})
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"好的，為了能更完善的服務你\n我什麼都願意聽，請問你想給哪方面的建議呢?","quick_replies":[
                {
                     "content_type":"text",
                     "title":"地點",
                     "payload":"<adress_suggest>"
                },
                {
                     "content_type":"text",
                     "title":"其他建議",
                     "payload":"<else_suggest>"
                }
                ]}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        elif user_payload=='<QA_NO>':
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"好吧QQ，被肥宅當成工具人了"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            user_payload=''


    # if ans == 2:
    #     del idcheck[idd]
     
            
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


    
    #     if ans == 0:
    #         sentence = ''
    #         ans = 5
    #         print(ans)

    # if ans == 5 and sentence == '':
    #     vba = []
    #     nba = []
    #     response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"哩勒工蝦密，挖聽某"}})
    #     status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)







#--------------------------------------------(以下為各種函數)----------------------------------------------------

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





#高捷涵數
def kao(i13,fbid,post_message_url,recevied_message):
    global stationtime,startstation,endstation

    kaostation=['南岡山','橋頭火車站','橋頭糖廠','青埔','都會公園','後勁','楠梓加工區','油廠國小','世運','左營',
    '生態園區','巨蛋','凹子底','後驛','高雄車站','美麗島','中央公園','三多商圈','獅甲','凱旋',
    '前鎮高中','草衙','高雄國際機場','小港','西子灣','鹽埕埔','市議會','美麗島','信義國小',
    '文化中心','五塊厝','技擊館','衛武營','鳳山西站','鳳山','大東','鳳山國中','大寮']
    kaotime=['00','01','02','03','04','05','06','07','08','09',
    '10','11','12','13','14','15','16','17','18','19',
    '20','21','22','23','24']

    if stationtime=='' and endstation!='':
        kk=0
        for Kaohour in range(25):
            if recevied_message ==kaotime[Kaohour]:                            
                stationtime=recevied_message
                with open(r'D:\Moyege\Work\@PROJECT\1221Google_map\chatbot\chatbot\Scripts\testbot0429\testbot0429\GooglemapBot\jsondata\時刻表\MRT_Kaohsiung.json', 'r', encoding="utf-8") as f:
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
                            Kaob = len(dataKaoMRT[Kaoi]["Timetables"]) #b=總班次
                            for Kaoj in range(Kaob):
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
                #last_state = ''
                anyQuestion(fbid,post_message_url)
                del idcheck[idd]                
            else:
                if kk == 24:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"搞毛阿整老子??時間觀念有問題阿??"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                kk+=1


    if endstation=='' and startstation!='':
        kaonumber=len(kaostation)
        kk=0
        for kao in range(kaonumber):
            if recevied_message == kaostation[kao]: 
                endstation=recevied_message
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"您的乘車時間是幾點呢?(00-24)"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            else:
                if kk == kaonumber-1:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"搞毛阿整老子??沒這個站阿!!"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                kk+=1
    if startstation=='':
        kaonumber=len(kaostation)
        kk=0
        for kao in range(kaonumber): 
            if recevied_message == kaostation[kao]:
                startstation=recevied_message
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"那要往哪個方向呢?"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            else:
                if kk == kaonumber-1:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"搞毛阿整老子??沒這個站阿!!"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                kk+=1


#高鐵函數
def thsr(i14,fbid,post_message_url,recevied_message):
    global thsr_start,thsr_end,thsr_time_depart,thsr_time_arrive

    thsrstation=['南港','台北','板橋','桃園','新竹','苗栗','台中','彰化','雲林','嘉義',
    '台南','左營']
    thsrtime=['00','01','02','03','04','05','06','07','08','09',
    '10','11','12','13','14','15','16','17','18','19',
    '20','21','22','23','24']

    recevied_message = changeword(recevied_message)
    if thsr_time_depart=='' and thsr_end!='':
        kk=0
        for thsrhour in range(25):
            if recevied_message ==thsrtime[thsrhour]:                            
                thsr_time_depart=recevied_message
                thsr_time_arrive=''
                with open(r'D:\Moyege\Work\@PROJECT\1221Google_map\chatbot\chatbot\Scripts\testbot0429\testbot0429\GooglemapBot\jsondata\時刻表\HSR_180227.json', 'r', encoding="utf-8") as f:
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
                anyQuestion(fbid,post_message_url)
                del idcheck[idd]
                
            else:
                if kk == 24:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"搞毛阿整老子??高鐵時間觀念有問題阿??"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                kk+=1

    if thsr_end=='' and thsr_start!='':
        thsrnumber=len(thsrstation)
        kk=0
        for thsr in range(thsrnumber):
            if recevied_message == thsrstation[thsr]: 
                thsr_end=recevied_message
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"您的乘車時間是幾點呢?(00-24)"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            else:
                if kk == thsrnumber-1:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"搞毛阿整老子??沒這個高鐵站阿!!"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                kk+=1
    if thsr_start=='':
        thsrnumber=len(thsrstation)
        kk=0
        for thsr in range(thsrnumber): 
            if recevied_message == thsrstation[thsr]:
                thsr_start=recevied_message
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"那要在哪裡下車呢?"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            else:
                if kk == thsrnumber-1:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"搞毛阿整老子??沒這個高鐵站阿!!"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                kk+=1


#臺鐵函數
def tra(i15,fbid,post_message_url,recevied_message):
    global tra_start,tra_end,tra_time_depart,tra_time_arrive

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

    if tra_end=='' and tra_start!='':
        tranumber=len(trastation)
        kk=0
        for tra in range(tranumber):
            if recevied_message == trastation[tra]: 
                tra_end=recevied_message
                with open(r'D:\Moyege\Work\@PROJECT\1221Google_map\chatbot\chatbot\Scripts\testbot0429\testbot0429\GooglemapBot\jsondata\時刻表\Train_180223.json', 'r', encoding="utf-8") as f:
                    tradata = json.load(f)
                traa = len(tradata) #計算整個json檔有幾筆資料, 也就是總共有幾班列車, a=921

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
                    for traj in range(trab): #第i筆資料裡的StopTimes(時刻表)裡的第j筆資料
                        if tradata[trai]['StopTimes'][traj]['StationName']['Zh_tw'] == tra_start: #該班次會在上車車站停靠
                            trak = traj + 1 #避免列車行駛方向錯誤
                            for trak in range(trak, trab):
                                if tradata[trai]['StopTimes'][trak]['StationName']['Zh_tw'] == tra_end: #該班次會在下車車站停靠
                                    tralist1.append(str(tradata[trai]['DailyTrainInfo']['TrainNo'])) #將車次號碼存到list1
                                    tralist2.append(tradata[trai]['StopTimes'][traj]['DepartureTime']) #將上車車站的開車時間存到list2
                                    tralist3.append(tradata[trai]['StopTimes'][trak]['ArrivalTime']) #將下車車站的抵達時間存到list3

                trac = len(tralist1) #總共有幾班符合使用者需求的火車

                #將同一台火車的資料合併
                for trax in range(trac):
                    tralist4.append(tralist2[trax]+tralist3[trax]+tralist1[trax])

                #將資料以開車時間做排序後再把合併過的資料拆開來印出
                for tray in range(trac):
                    tralist4.sort()
                    print(tralist4[tray][10:]+'\t', tralist4[tray][0:5]+'\t', tralist4[tray][5:10])
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":tralist4[tray][10:]+'\t'+tralist4[tray][0:5]+'\t'+tralist4[tray][5:10]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                anyQuestion(fbid,post_message_url)
                del idcheck[idd]                
            else:
                if kk == tranumber-1:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"搞毛阿整老子??沒這個台鐵站阿!!"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                kk+=1
    if tra_start=='':
        tranumber=len(trastation)
        kk=0
        for tra in range(tranumber): 
            if recevied_message == trastation[tra]:
                tra_start=recevied_message
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"那要在哪裡下車呢?"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            else:
                if kk == tranumber-1:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"搞毛阿整老子??沒這個台鐵站阿!!"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                kk+=1



# Google Places API Web Service Search
# Google Places API Web Service Details
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

    if id_results != []:
        place_id = id_results[0]['place_id']


        #list out of range錯誤要解決

        ### detail search
        dt_nav_request = 'placeid={}&language={}&key={}'.format(place_id, G_language, GM_API_KEY)
        dt_request = "https://maps.googleapis.com/maps/api/place/details/json?" + dt_nav_request

        # print(dt_request)
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
            P_time = '暫無資訊！'
        
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
    else :
        response='0'
        return response


def message_contents(fbid, sentence, mci, mcs):
    
    # recevied_message = ""
    mcj=''
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN

    # google可抓取類別：名稱(0)、電話(1)、地址(2)、營業時間(3)、評價(4)、網站(5)、googlemap頁面(6)
    #GMap_place_detailssearch(sentence)[0]的[0]就是指名稱
    if GMap_place_detailssearch(sentence)!='0':
        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"這是"+GMap_place_detailssearch(sentence)[0]+"的"+mcs+'\n'+ GMap_place_detailssearch(sentence)[mci]}})
        # # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"輸入的文字為：" + sentence}})
        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        anyQuestion(fbid,post_message_url)


        mcj=GMap_place_detailssearch(sentence)[mci]
        print(mcj)
    else :
        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"找不到這個地方唷，還是你可以給人家一點建議呢~","quick_replies":[
            {
                 "content_type":"text",
                 "title":"是",
                 "payload":"<QA_YES>"
            },
            {
                 "content_type":"text",
                 "title":"下次吧",
                 "payload":"<QA_NO>"
            }
            ]}})
        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        print(nba)
        print("最後的nba最後的nba最後的nba最後的nba最後的nba最後的nba最後的nba")

    # del idcheck[idd]

def anyQuestion(fbid,post_message_url):
    global nba, vba
    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'還有什麼問題嗎?',"quick_replies":[
        {
            "content_type":"text",
            "title":"沒問題了",
            "payload":"<POSTBACK_PAYLOAD>",
        },
        {
            "content_type":"text",
            "title":"我還有問題",
            "payload":"<POSTBACK_PAYLOAD>",
        },
        {
            "content_type":"text",
            "title":"我有建議要說",
            "payload":"<POSTBACK_PAYLOAD>",
        },
        {
            "content_type":"text",
            "title":"Jerry能幫你什麼",
            "payload":"<POSTBACK_PAYLOAD>",
        }
        ]}})
    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
    del nba[idd]
    vba = []




#wifi函數
def wifi(fbid, post_message_url):
    with open(r'D:\Moyege\Work\@PROJECT\1221Google_map\chatbot\chatbot\Scripts\testbot0429\testbot0429\GooglemapBot\jsondata\wifi.json', 'r', encoding="utf-8") as f:
        wifidata = json.load(f)
    gmaps = googlemaps.Client(key='AIzaSyBa-fjzE3tQFWlybQD_cFfSlMsdks4AvxQ')

    global  longlat,toiletlat, toiletlong, wrongcheck
    wifians = 0
    wifinum = 0
    j = 1
    addressmap=''
    if fbid in longlat:
        wifiaddress=[]
        wifiaddress=[str(longlat[fbid][1])+', '+str(longlat[fbid][0])]
        a = longlat[fbid][1]
        b = longlat[fbid][0]

        long = len(wifidata)
        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'目前為你偵測到附近有Wifi的地方有:'}})
        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

        for i in range(long):
            if ((float(wifidata[i]['LATITUDE'])-a)**2+(float(wifidata[i]['LONGITUDE'])-b)**2) < 0.000020295025:    #0.00000901度 = 1公尺 500m
                #print(wifidata[i]['Name']+'，地址是'+wifidata[i]['Address'])
                wifians=wifians+1
                if j==1:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'1. 您傳送的位置'}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                j=j+1
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":str(j)+'. '+wifidata[i]['NAME']+'，地址是'+wifidata[i]['ADDR']}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                wifinum+=1 #地圖用
                wifiaddress.append(wifidata[i]['ADDR'])
        if wifians==0 :
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'不好意思，這附近沒有地方有Wifi餒，還是你可以給人家一點建議呢~',"quick_replies":[
            {
                 "content_type":"text",
                 "title":"是",
                 "payload":"<QA_YES>"
            },
            {
                 "content_type":"text",
                 "title":"下次吧",
                 "payload":"<QA_NO>"
            }
            ]}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            wrongcheck = -1
        if wifinum!=0:
            addressmap=soptsoptmap(wifinum,wifiaddress)
            response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"attachment":{"type":"image", "payload":{"url":addressmap}}}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"},data = response_msg)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'以上為您附近有wifi的地方，圖片為相對應編號的位置'}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            wrongcheck = -1
        wifians=0
        del longlat[fbid]
        toiletlat=''
        toiletlong=''
        anyQuestion(fbid,post_message_url)
        del idcheck[idd]
    elif wrongcheck > 0 :
        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'按下傳送地點我們才會知道喔！',"quick_replies":[
        # {
        #     "content_type":"text",
        #     "title":"搜尋",
        #     "payload":"<POSTBACK_PAYLOAD>",
        # },
            {
            "content_type":"location"
            }
        ]}})
        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
    wrongcheck+=1

#廁所函數
def toilet(fbid, post_message_url):
    with open(r'D:\Moyege\Work\@PROJECT\1221Google_map\chatbot\chatbot\Scripts\testbot0429\testbot0429\GooglemapBot\jsondata\toilet.json', 'r', encoding="utf-8") as f:
        toiletdata = json.load(f)
    gmaps = googlemaps.Client(key='AIzaSyBa-fjzE3tQFWlybQD_cFfSlMsdks4AvxQ')
    global  longlat,toiletlat, toiletlong, wrongcheck
    toiletans = 0
    toiletnum = 0
    j = 1
    addressmap=''
    if fbid in longlat:
        toiletaddress=[]
        toiletaddress=[str(longlat[fbid][1])+', '+str(longlat[fbid][0])]
        a = longlat[fbid][1]
        b = longlat[fbid][0]
        long = len(toiletdata)

        for i in range(long):
            if ((float(toiletdata[i]['Latitude'])-a)**2+(float(toiletdata[i]['Longitude'])-b)**2) < 0.000020295025:    #0.00000901度 = 1公尺 500m
                print(toiletdata[i]['Name']+'，地址是'+toiletdata[i]['Address'])
                toiletans=toiletans+1
                if j==1:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'1. 您傳送的位置'}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                j=j+1
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":str(j)+'. '+toiletdata[i]['Name']+'，地址是'+toiletdata[i]['Address']}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                toiletnum+=1 #地圖用
                toiletaddress.append(toiletdata[i]['Address'])
        if toiletans==0 :
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'不好意思，這附近沒有廁所餒，還是你可以給人家一點建議呢~',"quick_replies":[
            {
                 "content_type":"text",
                 "title":"是",
                 "payload":"<QA_YES>"
            },
            {
                 "content_type":"text",
                 "title":"下次吧",
                 "payload":"<QA_NO>"
            }
            ]}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            wrongcheck = -1
        if toiletnum!=0:
            addressmap=soptsoptmap(toiletnum,toiletaddress)
            response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"attachment":{"type":"image", "payload":{"url":addressmap}}}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"},data = response_msg)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'以上為您附近廁所的地址，圖片為相對應編號的位置'}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            wrongcheck = -1
            anyQuestion(fbid,post_message_url)
        toiletans=0
        del longlat[fbid]
        toiletlat=''
        toiletlong=''
        del idcheck[idd]
        
    elif wrongcheck > 0 :
        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'按下傳送地點我們才會知道喔！',"quick_replies":[
        # {
        #     "content_type":"text",
        #     "title":"搜尋",
        #     "payload":"<POSTBACK_PAYLOAD>",
        # },
            {
            "content_type":"location",
            "title":"傳送地點"
            }
        ]}})
        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
    wrongcheck+=1


def ATM(fbid, post_message_url):
    with open(r'D:\Moyege\Work\@PROJECT\1221Google_map\chatbot\chatbot\Scripts\testbot0429\testbot0429\GooglemapBot\jsondata\post_atm.json', 'r', encoding="utf-8") as f:
        atmdata = json.load(f)
    gmaps = googlemaps.Client(key='AIzaSyBa-fjzE3tQFWlybQD_cFfSlMsdks4AvxQ')
    global  longlat, toiletlat, toiletlong, wrongcheck
    atmans = 0
    atmnum = 0
    j = 1
    addressmap=''
    if fbid in longlat:
        atmaddress=[]
        atmaddress=[str(longlat[fbid][1])+', '+str(longlat[fbid][0])]
        a = longlat[fbid][1]
        b = longlat[fbid][0]

        long = len(atmdata)

        for i in range(long):
            if ((float(atmdata[i]['緯度'])-a)**2+(float(atmdata[i]['經度'])-b)**2) < 0.000020295025:    #0.00000901度 = 1公尺 500m
                print(atmdata[i]['局名']+'，地址是'+atmdata[i]['郵局地址'])
                atmans=atmans+1
                if j==1:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'1. 您傳送的位置'}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                j=j+1
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":atmdata[i]['局名']+'，地址是'+atmdata[i]['郵局地址']}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                atmnum+=1 #地圖用
                atmaddress.append(atmdata[i]['郵局地址'])
        if atmans==0 :
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'不好意思，這附近沒有ATM餒，還是你可以給人家一點建議呢~',"quick_replies":[
            {
                 "content_type":"text",
                 "title":"是",
                 "payload":"<QA_YES>"
            },
            {
                 "content_type":"text",
                 "title":"下次吧",
                 "payload":"<QA_NO>"
            }
            ]}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            wrongcheck = -1

        if atmnum!=0:
            addressmap=soptsoptmap(atmnum,atmaddress)
            response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"attachment":{"type":"image", "payload":{"url":addressmap}}}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"},data = response_msg)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'以上為您附近廁所的地址，圖片為相對應編號的位置'}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            wrongcheck = -1
        atmans=0
        del longlat[fbid]
        toiletlat=''
        toiletlong=''
        anyQuestion(fbid,post_message_url)
        del idcheck[idd]

    elif wrongcheck > 0:
        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'按下傳送地點我們才會知道喔！',"quick_replies":[
            {
            "content_type":"location"
            }
        ]}})
        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
    wrongcheck+=1


def show(fbid, post_message_url):
    with open(r'D:\Moyege\Work\@PROJECT\1221Google_map\chatbot\chatbot\Scripts\testbot0429\testbot0429\GooglemapBot\jsondata\演唱會.json', 'r', encoding="utf-8") as f:
        showdata = json.load(f)
        long = len(showdata)
        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'最近的演唱會有:'}})
        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

        for i in range(long):
            # print('名稱是'+showdata[i]['title']+'，時間是'+showdata[i]['showInfo']['time'][0])
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":showdata[i]['title']}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

def changeword(recevied_message):
    ls = list(recevied_message)
    print(ls)
    for icw in range(len(ls)):
        if ls[icw] == '臺':
            ls[icw] = '台'
        if ls[icw] == '點':
            ls[icw] = ''
        if ls[icw] == '一' or ls[icw] == '1':
            ls[icw] = '01'
        if ls[icw] == '二' or ls[icw] == '2':
            ls[icw] = '02'
        if ls[icw] == '三' or ls[icw] == '3':
            ls[icw] = '03'
        if ls[icw] == '四' or ls[icw] == '4':
            ls[icw] = '04'
        if ls[icw] == '五' or ls[icw] == '5':
            ls[icw] = '05'
        if ls[icw] == '六' or ls[icw] == '6':
            ls[icw] = '06'
        if ls[icw] == '七' or ls[icw] == '7':
            ls[icw] = '07'
        if ls[icw] == '八' or ls[icw] == '8':
            ls[icw] = '08'
        if ls[icw] == '九' or ls[icw] == '9':
            ls[icw] = '09'
        if ls[icw] == '十' or ls[icw] == '10':
            ls[icw] = '10'
        if ls[icw] == '十一' or ls[icw] == '11':
            ls[icw] = '11'
        if ls[icw] == '十二' or ls[icw] == '12':
            ls[icw] = '12'
        if ls[icw] == '十三' or ls[icw] == '13':
            ls[icw] = '13'
        if ls[icw] == '十四' or ls[icw] == '14':
            ls[icw] = '14'
        if ls[icw] == '十五' or ls[icw] == '15':
            ls[icw] = '15'
        if ls[icw] == '十六' or ls[icw] == '16':
            ls[icw] = '16'
        if ls[icw] == '十七' or ls[icw] == '17':
            ls[icw] = '17'
        if ls[icw] == '十八' or ls[icw] == '18':
            ls[icw] = '18'
        if ls[icw] == '十九' or ls[icw] == '19':
            ls[icw] = '19'
        if ls[icw] == '二十' or ls[icw] == '20':
            ls[icw] = '20'
        if ls[icw] == '二十一' or ls[icw] == '21':
            ls[icw] = '21'
        if ls[icw] == '二十二' or ls[icw] == '22':
            ls[icw] = '22'
        if ls[icw] == '二十三' or ls[icw] == '23':
            ls[icw] = '23'
        if ls[icw] == '二十四' or ls[icw] == '24':
            ls[icw] = '24'
    recevied_message = ''.join(ls)
    return recevied_message
def soptsoptmap(toiletnum,toiletaddress):
    # 多地點地圖顯示
    from urllib.parse import quote
    import urllib.request
    import json, string
        
    endpoint = "https://maps.googleapis.com/maps/api/staticmap?"
    GM_API_KEY = 'AIzaSyA35lPzOmBYaGtsGnu1BtuZiWqZcLpYdQk'

    # G_center = center.replace(' ', '+')

    num = toiletnum+1

    if num >= 1:
        
    #     G_zoom = "16"
    #     G_size = "250x250"
        G_size = "1000x1000"
        nav_request = 'size={}'.format(G_size)
    #     nav_request = 'zoom={}&size={}'.format(G_zoom, G_size)
    #     nav_request = ""
        
        for i in range(0,num):
            address=toiletaddress[i]
            G_center = address.replace(' ', '+')
            G_MarkerLabel = str(i + 1) + "%7C"
    #         G_markers = "size:tiny%7c" + "color:red%7C"+ "label:" + G_MarkerLabel + G_center
            G_markers = "color:red%7C"+ "label:" + G_MarkerLabel + "%7C" + G_center
            nav = '&markers={}'.format(G_markers)
            nav_request = nav_request + nav
        
        nav_request = nav_request + '&key=' + GM_API_KEY

    request_trans = urllib.parse.quote(nav_request, safe = string.printable)    
    G_request = endpoint + request_trans
    return (G_request)