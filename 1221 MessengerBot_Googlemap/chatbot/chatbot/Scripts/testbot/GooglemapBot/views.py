from django.shortcuts import render
from django.views import generic
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from hanziconv import HanziConv
from urllib.parse import quote
from requests_toolbelt import MultipartEncoder
import json, requests, re, random, os, sys, string, six, matplotlib, time, jieba, jieba.posseg , jieba.analyse, urllib.request
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 胖狗狗的白白肚肚 https://goo.gl/WEjQQK API
PAGE_ACCESS_TOKEN = "EAAB09UKvWGsBAFsrGU5hpRfJRQHMFPMSHNV8D9TvIKpqvhLkkKCUJgIhJHQZABsqadPckRxeBxsadZAq6RSMeBHdskcwP0hnLyKEoWsWXCQWx1hrrXZAz6PXeKQnTkYpPOhPoFJtDXf3z60U6N6PlBl9ZBXAnJWlM03ZBl9JqhAZDZD"
GM_API_KEY = 'AIzaSyA35lPzOmBYaGtsGnu1BtuZiWqZcLpYdQk'

FILE_SAVEPATH = r'D:\Moyege\Work\@PROJECT\1221Google_map\chatbot\chatbot\Scripts\testbot\GooglemapBot\jsondata'


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

                        # 檢測是否為使用者傳送給粉專 粉專ID = 1999667926988614
                        if message['recipient']['id'] == '1999667926988614':
                            print(message)
                            post_facebook_message_text(message['sender']['id'], message['message']['text']) 
 

        return HttpResponse()


def message_contents(fbid, sentence):
    
    # recevied_message = ""
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN

    # google可抓取類別：名稱(0)、電話(1)、地址(2)、營業時間(3)、評價(4)、網站(5)、googlemap頁面(6) 

    # locationpoint = ''
    # for i in range(len(GMap_place_detailssearch(sentence)[7])):
    #     locationpoint += str(GMap_place_detailssearch(sentence)[7][i]) + '\n'   
    # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":locationpoint}})
    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"輸入的文字為：" + sentence}})
    
    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

    with open(FILE_SAVEPATH + r'\menu.json', 'r', encoding="utf-8") as f:
        menudata = json.load(f)
    

    select_df = pd.DataFrame(menudata[0]['Menu'], columns=['name', 'price', 'notes'])

    # 使用者ID：fbid

    # post_facebook_message_media(fbid, GMap_map(sentence)) 

    # # PROBLEM
    # 1 重複回復
    # 2 
        # Exception ignored in: <bound method StringVar.__del__ of <tkinter.StringVar object at 0x0000000012AF2EB8>>
        # Traceback (most recent call last):
        #   File "C:\Users\user\Anaconda3\Lib\tkinter\__init__.py", line 251, in __del__
        #     if self._tk.getboolean(self._tk.call("info", "exists", self._name)):
        # RuntimeError: main thread is not in main loop
        # Error in atexit._run_exitfuncs:
        # Traceback (most recent call last):
        #   File "D:\Moyege\Work\@PROJECT\1221Google_map\chatbot\chatbot\lib\site-packages\matplotlib\_pylab_helpers.py", line 78, in destroy_all
        #     manager.destroy()
        #   File "D:\Moyege\Work\@PROJECT\1221Google_map\chatbot\chatbot\lib\site-packages\matplotlib\backends\_backend_tk.py", line 558, in destroy
        #     self.window.destroy()
        #   File "C:\Users\user\Anaconda3\Lib\tkinter\__init__.py", line 1892, in destroy
        #     for c in list(self.children.values()): c.destroy()
        #   File "D:\Moyege\Work\@PROJECT\1221Google_map\chatbot\chatbot\lib\site-packages\matplotlib\backends\_backend_tk.py", line 656, in destroy
        #     Tk.Frame.destroy(self, *args)
        #   File "C:\Users\user\Anaconda3\Lib\tkinter\__init__.py", line 2127, in destroy
        #     for c in list(self.children.values()): c.destroy()
        #   File "C:\Users\user\Anaconda3\Lib\tkinter\__init__.py", line 2128, in destroy
        #     self.tk.call('destroy', self._w)
    # post_facebook_message_file(fbid, panda_png(select_df, menudata[0]["StoreName"], FILE_SAVEPATH, fbid)) 


# 建立可回應至FB之函數(文字)
def post_facebook_message_text(fbid, recevied_message):

	# 抓取傳送者名稱
	# 使用：user_details['first_name']
    user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid
    user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':PAGE_ACCESS_TOKEN}
    user_details = requests.get(user_details_url, user_details_params).json()

    message_contents(fbid, recevied_message)

def post_facebook_message_file(fbid, filelocation):

    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    # response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"attachment":{"type":"file", "payload":{}}}, "filedata":(os.path.basename(filelocation), open(filelocation, "rb"), "image/png")})
    
    # encode nested json to avoid errors during multipart encoding process
    response_msg = {"recipient": json.dumps({"id":fbid}), "message": json.dumps({"attachment":{"type":"image", "payload":{}}}), "filedata":(os.path.basename(filelocation), open(filelocation, "rb"), "image/png")}
    
    # # # TODO：
    # # # 1.pip install requests_toolbelt
    # # # 2.from requests_toolbelt import MultipartEncoder

    # multipart encode the entire payload
    multipart_msg = MultipartEncoder(response_msg)

    print(multipart_msg)

    # multipart header from multipart_data
    multipart_header = {'Content-Type': multipart_msg.content_type}
    print(multipart_header)

    status = requests.post(post_message_url, headers = multipart_header, data = multipart_msg)


def post_facebook_message_media(fbid, imgurl):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"attachment":{"type":"image", "payload":{"url":imgurl}}}})
    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"},data = response_msg)
    # print(status.json())


def panda_png(dataframe, title, filenpath, fbid):

    # # # import  matplotlib, time
    # # # import pandas as pd
    # # # import numpy as np
    # # # import matplotlib.pyplot as plt
    ax_title = render_mpl_table(dataframe, header_columns=0, col_width=2.5).set_title(title, fontsize=20)
    fig = ax_title.get_figure()
    fig.tight_layout()
    # filelocation = r'D:\Moyege\Work\@PROJECT\1221Google_map\chatbot\chatbot\Scripts\testbot\GooglemapBot\jsondata'
    filenpath += '\\'  + fbid + time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.png'
    fig.savefig(filenpath)
    plt.close('all')

    return filenpath


def render_mpl_table(data, col_width=2.0, row_height=0.625, font_size=14,
                     header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0, 0, 1, 1], header_columns=0,
                     ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in  six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])

    return ax




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

    # 回傳地點經緯度
    geometry = id_results[0]['geometry']
    location = geometry['location']
    place = [location['lat'], location['lng']]

    # 回復地點ID
    place_id = id_results[0]['place_id']

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

    response = [ P_name, P_phone, P_address, P_time, P_grade, P_web, P_GMweb , place]

    return response

