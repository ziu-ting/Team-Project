# yomamabot/fb_yomamabot/views.py
import json, requests, random, re
from pprint import pprint

from django.views import generic
from django.http.response import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from hanziconv import HanziConv


#  ------------------------ Fill this with your page access token! -------------------------------
PAGE_ACCESS_TOKEN = "EAACA0ZBlCezkBABTc4TZBv0AWRwqOmpoOIqNBJW7u6cGkB5HYDeGHTQ1qR9bhOdQMaeFxxITsUt6OERke6Yb2rYKE9bXmxHZAJXgdiy0aRsoKWVRY2F15xDlbGgQ3BKenZCUxSR9M2U03J14qZC1sZByjIIyxsQS1uADZAVoNeLhwZDZD"
VERIFY_TOKEN = "20171013"

# jokes = { 'jerry': ["""jerry is a handsome guy""", ], 
#          'jerrywu':      ["""jerrywu is a good teacher""", ], 
#          'weiwei': ["""weiweichao is not only a turtle but also a Goblin""",] }


jerry = ChatBot("jerry")
jerry.set_trainer(ChatterBotCorpusTrainer)
jerry.train("D:\\Moyege\\Work\\@PROJECT\\1028QAtest\\jerry_DB.json")  


# Helper function
def post_facebook_message(fbid, recevied_message):
    # Remove all punctuations, lower case the text and split it based on space
    tokens = re.sub(r"[^a-zA-Z0-9\s]",' ',recevied_message).lower().split()
    joke_text = ''
    # for token in tokens:
        # if token in jokes:

        # y = jerry.get_response(x)
        y = jerry.get_response(tokens)
        y = HanziConv.toTraditional(y.text)

        # joke_text = random.choice(jokes[token])
        joke_text = random.choice(y)
        # joke_text = y

        # break
    # if not joke_text:
    #     joke_text = "I didn't understand! Send 'jerry', 'jerrywu', 'weiwei' for a answer!" 

    user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid 
    user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':PAGE_ACCESS_TOKEN} 
    user_details = requests.get(user_details_url, user_details_params).json() 
    joke_text = 'Yo '+user_details['first_name']+'..! ' + joke_text
                   
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":joke_text}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    pprint(status.json())

# Create your views here.
class ChatbotView(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')
        
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
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
                    pprint(message)    
                    # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                    # are sent as attachments and must be handled accordingly. 
                    post_facebook_message(message['sender']['id'], message['message']['text'])    
        return HttpResponse()    

                      