from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from hanziconv import HanziConv

jerry = ChatBot("jerry")
jerry.set_trainer(ChatterBotCorpusTrainer)
jerry.train("D:\\Moyege\\Work\\@PROJECT\\1028QAtest\\jerry_DB.json")  

def inputTest():
    x = input("請說話:")
    # x:token
    y = jerry.get_response(x)
    y = HanziConv.toTraditional(y.text)

    print (type (x))
    print (type (y))
    print (y)

while (True):
    inputTest()