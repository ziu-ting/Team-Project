
# coding: utf-8

# In[1]:

import requests
res = requests.get('http://www.ntust.edu.tw/home.php')
res.encoding = 'utf8'
print(type(res))
print(res.status_code)
print(res.headers)
print(res.encoding)
print(res.text)


# In[6]:

import requests
#from urllib.parse import quote
params = {
    'q':'台科',
    'oq':'台科',
    'aqs':'chrome..69i57j0j69i65l3j69i61.1004j0j7',
    'sourceid':'chrome',
    'ie':'UTF-8'
}
res = requests.get("https://www.google.com.tw/search", params=params)
#res = requests.get("https://www.google.com.tw/search?q=" + quote('台科'))
res.text


# In[16]:

import requests
from bs4 import BeautifulSoup
data = {
    'StartStation':'977abb69-413a-4ccf-a109-0272c24fd490',
    'EndStation':'f2519629-5973-4d08-913b-479cce78a356',
    'SearchDate':'2017/07/07',
    'SearchTime':'15:00',
    'SearchWay':'DepartureInMandarin',
    'RestTime':'',
    'EarlyOrLater':''
}

r = requests.session().post('http://www.thsrc.com.tw/tw/TimeTable/SearchResult', data=data)
soup = BeautifulSoup(r.text)

string=''
for j in soup.select('section.result_table')[0].select('tr')[1].select('th'):
    string += j.text + '\t'
print(string)
for i in soup.select('section.result_table')[0].select('tr')[2:]:
    string=''
    if len(i.select('table.touch_table')) != 0:
        for j in i.select('table.touch_table')[0].select('td'):
            string += j.text.replace(' ', '').replace('\n', '') + '\t'
        print(string)


# In[18]:

import requests
from bs4 import BeautifulSoup
data = {
    's1elect':'BR01-019',
    'action':'query',
    's2elect':'BR08-012',
    'submit': '確定'
}
r = requests.session().post('http://web.metro.taipei/c/2stainfo_new.asp', data=data)
r.encoding='utf-8'
soup = BeautifulSoup(r.text)
for i in soup.select('div')[0].select('tr'):
    string = ''
    for j in i.select('td'):
        string += j.text + '\t'
    print(string)


# In[19]:

import csv
import requests
import string
from bs4 import BeautifulSoup

E = [0, 1, 2, 4, 7, 8, 14]

for i in string.ascii_uppercase[:7]:
    csv.writer(open('course/' + i + '.csv', 'w', encoding='utf8', newline='')).writerow(['課程代碼', '通識向度', '課程名稱', '學分', '授課教師','上課星期節次', '備註'])

data = {
    '__EVENTTARGET': '',
    '__EVENTARGUMENT': '',
    '__LASTFOCUS': '',
    '__VIEWSTATE': '/wEPDwUJOTI2MTk1Mzg4D2QWAgIBD2QWBAIlD2QWBGYPZBYCZg9kFgJmD2QWAgIBD2QWAmYPZBYCZg8PFgIeB1Zpc2libGVoZBYGAgIPZBYIZg9kFgJmDxAPFggeCkRhdGFNZW1iZXIFCUVkdV9Pcmdhbh4NRGF0YVRleHRGaWVsZAURQ29sbGVnZURlcGFydG1lbnQeDkRhdGFWYWx1ZUZpZWxkBQJOTx4LXyFEYXRhQm91bmRnZBAVNQnkuI3pgbjmk4cW6Kit6KiI5a246ZmiLeW7uuevieezuyLoqK3oqIjlrbjpmaIt5Ym15oSP6Kit6KiI5a245aOr54+tHOioreioiOWtuOmZoi3oqK3oqIjnoJTnqbbmiYAf6Kit6KiI5a246ZmiLeW3peWVhualreioreioiOezuyvoqK3oqIjlrbjpmaIt5Ym15oSP6Kit6KiI5a245aOr5a245L2N5a2456iLMeaHieeUqOenkeaKgOWtuOmZoi3mh4nnlKjnp5HmioDlrbjlo6vlrbjkvY3lrbjnqIsx5oeJ55So56eR5oqA5a246ZmiLemGq+WtuOW3peeoi+WtuOWjq+WtuOS9jeWtuOeoiyjmh4nnlKjnp5HmioDlrbjpmaIt6Yar5a245bel56iL56CU56m25omAMeaHieeUqOenkeaKgOWtuOmZoi3oibLlvanoiIfnhafmmI7np5HmioDnoJTnqbbmiYBA5oeJ55So56eR5oqA5a246ZmiLeiJsuW9qeW9seWDj+iIh+eFp+aYjuenkeaKgOWtuOWjq+WtuOS9jeWtuOeoiyjmh4nnlKjnp5HmioDlrbjpmaIt5oeJ55So56eR5oqA56CU56m25omAJeaHieeUqOenkeaKgOWtuOmZoi3kuI3liIbns7vlrbjlo6vnj6005oeJ55So56eR5oqA5a246ZmiLeaZuuaFp+iyoeeUouasiuWtuOWjq+WtuOS9jeWtuOeoizrmh4nnlKjnp5HmioDlrbjpmaIt5oeJ55So56eR5oqA56CU56m25omA5p2Q5paZ56eR5oqA5a2456iLIuaHieeUqOenkeaKgOWtuOmZoi3lsIjliKnnoJTnqbbmiYAc6Zu76LOH5a246ZmiLeizh+ioiuW3peeoi+ezuxzpm7vos4flrbjpmaIt6Zu76LOH5a245aOr54+tHOmbu+izh+WtuOmZoi3pm7vmqZ/lt6XnqIvns7si6Zu76LOH5a246ZmiLeWFiembu+W3peeoi+eglOeptuaJgBzpm7vos4flrbjpmaIt6Zu75a2Q5bel56iL57O7JeS6uuaWh+ekvuacg+WtuOmZoi3kurrmlofnpL7mnIPlrbjnp5El5Lq65paH56S+5pyD5a246ZmiLeW4q+izh+WfueiCsuS4reW/gyLkurrmlofnpL7mnIPlrbjpmaIt5oeJ55So5aSW6Kqe57O7H+S6uuaWh+ekvuacg+WtuOmZoi3pgJrorZjlrbjnp5Ec5Lq65paH56S+5pyD5a246ZmiLemrlOiCsuWupDHkurrmlofnpL7mnIPlrbjpmaIt5pW45L2N5a2457+S6IiH5pWZ6IKy56CU56m25omANOaZuuaFp+iyoeeUouWtuOmZoi3mmbrmhafosqHnlKLmrIrlrbjlo6vlrbjkvY3lrbjnqIsi5pm65oWn6LKh55Si5a246ZmiLeWwiOWIqeeglOeptuaJgDHmmbrmhafosqHnlKLlrbjpmaIt56eR5oqA566h55CG5a245aOr5a245L2N5a2456iLKOaZuuaFp+iyoeeUouWtuOmZoi3np5HmioDnrqHnkIbnoJTnqbbmiYAc566h55CG5a246ZmiLeS8gealreeuoeeQhuezuyvnrqHnkIblrbjpmaIt6LKh5YuZ6YeR6J6N5a245aOr5a245L2N5a2456iLIueuoeeQhuWtuOmZoi3osqHli5nph5Hono3noJTnqbbmiYAc566h55CG5a246ZmiLeW3pealreeuoeeQhuezuxDnrqHnkIblrbjpmaItTUJBHOeuoeeQhuWtuOmZoi3nrqHnkIblrbjlo6vnj60c566h55CG5a246ZmiLeeuoeeQhueglOeptuaJgBznrqHnkIblrbjpmaIt6LOH6KiK566h55CG57O7K+euoeeQhuWtuOmZoi3np5HmioDnrqHnkIblrbjlo6vlrbjkvY3lrbjnqIsi566h55CG5a246ZmiLeenkeaKgOeuoeeQhueglOeptuaJgCjlt6XnqIvlrbjpmaIt6Ieq5YuV5YyW5Y+K5o6n5Yi256CU56m25omAHOW3peeoi+WtuOmZoi3lt6XnqIvlrbjlo6vnj60c5bel56iL5a246ZmiLeWMluWtuOW3peeoi+ezuxzlt6XnqIvlrbjpmaIt54ef5bu65bel56iL57O7N+W3peeoi+WtuOmZoi3ntqDog73nlKLmpa3mqZ/pm7vlt6XnqIvlrbjlo6vlrbjkvY3lrbjnqIsc5bel56iL5a246ZmiLeapn+aisOW3peeoi+ezuyLlt6XnqIvlrbjpmaIt5p2Q5paZ56eR5oqA56CU56m25omAMeW3peeoi+WtuOmZoi3pq5jpmo7np5HmioDnoJTnmbznoqnlo6vlrbjkvY3lrbjnqIsc5bel56iL5a246ZmiLei3qOezu+aJgOWtuOeoizrlt6XnqIvlrbjpmaIt5bel56iL5oqA6KGT56CU56m25omA5oqA6IG35bCI5qWt55m85bGV5a2456iLJeW3peeoi+WtuOmZoi3mnZDmlpnnp5HlrbjoiIflt6XnqIvns7sDQUxMFTUETlVMTAQ0LUFEBDQtQ0QENC1ERQQ0LURUBDQtRFgEMC1BVAQwLUJCBDAtQkUEMC1DSQQwLUNYBDAtRU4EMC1IQwQwLUlCBDAtTVMEMC1QQQQyLUNTBDItRUMEMi1FRQQyLUVPBDItRVQENS1DQwQ1LUVQBDUtRkwENS1HRQQ1LVBFBDUtVkUENi1JQgQ2LVBBBDYtVEIENi1UTQQzLUJBBDMtRkIEMy1GTgQzLUlNBDMtTUEEMy1NQgQzLU1HBDMtTUkEMy1UQgQzLVRNBDEtQUMEMS1DRQQxLUNIBDEtQ1QEMS1HWAQxLU1FBDEtTVMEMS1SRAQxLVJTBDEtVFYEMS1UWAFfFCsDNWdnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnFgFmZAIBD2QWAmYPEA8WCB8BBQlFZHVfT3JnYW4fAgUGUGVyaW9kHwMFAk5PHwRnZBAVAQnkuI3pgbjmk4cVAQROVUxMFCsDAWcWAWZkAgIPZBYCZg8QDxYIHwEFCUVkdV9Pcmdhbh8CBQVncmFkZR8DBQJOTx8EZ2QQFQEJ5LiN6YG45pOHFQEETlVMTBQrAwFnFgFmZAIDD2QWAmYPEA8WCB8BBQlFZHVfT3JnYW4fAgUFQ2xhc3MfAwUCTk8fBGdkEBUBCeS4jemBuOaThxUBBE5VTEwUKwMBZxYBZmQCAw9kFghmD2QWAmYPEA8WCB8BBQlFZHVfT3JnYW4fAgURQ29sbGVnZURlcGFydG1lbnQfAwUCTk8fBGdkEBU1CeS4jemBuOaThxboqK3oqIjlrbjpmaIt5bu656+J57O7IuioreioiOWtuOmZoi3libXmhI/oqK3oqIjlrbjlo6vnj60c6Kit6KiI5a246ZmiLeioreioiOeglOeptuaJgB/oqK3oqIjlrbjpmaIt5bel5ZWG5qWt6Kit6KiI57O7K+ioreioiOWtuOmZoi3libXmhI/oqK3oqIjlrbjlo6vlrbjkvY3lrbjnqIsx5oeJ55So56eR5oqA5a246ZmiLeaHieeUqOenkeaKgOWtuOWjq+WtuOS9jeWtuOeoizHmh4nnlKjnp5HmioDlrbjpmaIt6Yar5a245bel56iL5a245aOr5a245L2N5a2456iLKOaHieeUqOenkeaKgOWtuOmZoi3phqvlrbjlt6XnqIvnoJTnqbbmiYAx5oeJ55So56eR5oqA5a246ZmiLeiJsuW9qeiIh+eFp+aYjuenkeaKgOeglOeptuaJgEDmh4nnlKjnp5HmioDlrbjpmaIt6Imy5b2p5b2x5YOP6IiH54Wn5piO56eR5oqA5a245aOr5a245L2N5a2456iLKOaHieeUqOenkeaKgOWtuOmZoi3mh4nnlKjnp5HmioDnoJTnqbbmiYAl5oeJ55So56eR5oqA5a246ZmiLeS4jeWIhuezu+WtuOWjq+ePrTTmh4nnlKjnp5HmioDlrbjpmaIt5pm65oWn6LKh55Si5qyK5a245aOr5a245L2N5a2456iLOuaHieeUqOenkeaKgOWtuOmZoi3mh4nnlKjnp5HmioDnoJTnqbbmiYDmnZDmlpnnp5HmioDlrbjnqIsi5oeJ55So56eR5oqA5a246ZmiLeWwiOWIqeeglOeptuaJgBzpm7vos4flrbjpmaIt6LOH6KiK5bel56iL57O7HOmbu+izh+WtuOmZoi3pm7vos4flrbjlo6vnj60c6Zu76LOH5a246ZmiLembu+apn+W3peeoi+ezuyLpm7vos4flrbjpmaIt5YWJ6Zu75bel56iL56CU56m25omAHOmbu+izh+WtuOmZoi3pm7vlrZDlt6XnqIvns7sl5Lq65paH56S+5pyD5a246ZmiLeS6uuaWh+ekvuacg+WtuOenkSXkurrmlofnpL7mnIPlrbjpmaIt5bir6LOH5Z+56IKy5Lit5b+DIuS6uuaWh+ekvuacg+WtuOmZoi3mh4nnlKjlpJboqp7ns7sf5Lq65paH56S+5pyD5a246ZmiLemAmuitmOWtuOenkRzkurrmlofnpL7mnIPlrbjpmaIt6auU6IKy5a6kMeS6uuaWh+ekvuacg+WtuOmZoi3mlbjkvY3lrbjnv5LoiIfmlZnogrLnoJTnqbbmiYA05pm65oWn6LKh55Si5a246ZmiLeaZuuaFp+iyoeeUouasiuWtuOWjq+WtuOS9jeWtuOeoiyLmmbrmhafosqHnlKLlrbjpmaIt5bCI5Yip56CU56m25omAMeaZuuaFp+iyoeeUouWtuOmZoi3np5HmioDnrqHnkIblrbjlo6vlrbjkvY3lrbjnqIso5pm65oWn6LKh55Si5a246ZmiLeenkeaKgOeuoeeQhueglOeptuaJgBznrqHnkIblrbjpmaIt5LyB5qWt566h55CG57O7K+euoeeQhuWtuOmZoi3osqHli5nph5Hono3lrbjlo6vlrbjkvY3lrbjnqIsi566h55CG5a246ZmiLeiyoeWLmemHkeiejeeglOeptuaJgBznrqHnkIblrbjpmaIt5bel5qWt566h55CG57O7EOeuoeeQhuWtuOmZoi1NQkEc566h55CG5a246ZmiLeeuoeeQhuWtuOWjq+ePrRznrqHnkIblrbjpmaIt566h55CG56CU56m25omAHOeuoeeQhuWtuOmZoi3os4foqIrnrqHnkIbns7sr566h55CG5a246ZmiLeenkeaKgOeuoeeQhuWtuOWjq+WtuOS9jeWtuOeoiyLnrqHnkIblrbjpmaIt56eR5oqA566h55CG56CU56m25omAKOW3peeoi+WtuOmZoi3oh6rli5XljJblj4rmjqfliLbnoJTnqbbmiYAc5bel56iL5a246ZmiLeW3peeoi+WtuOWjq+ePrRzlt6XnqIvlrbjpmaIt5YyW5a245bel56iL57O7HOW3peeoi+WtuOmZoi3nh5/lu7rlt6XnqIvns7s35bel56iL5a246ZmiLee2oOiDveeUoualreapn+mbu+W3peeoi+WtuOWjq+WtuOS9jeWtuOeoixzlt6XnqIvlrbjpmaIt5qmf5qKw5bel56iL57O7IuW3peeoi+WtuOmZoi3mnZDmlpnnp5HmioDnoJTnqbbmiYAx5bel56iL5a246ZmiLemrmOmajuenkeaKgOeglOeZvOeiqeWjq+WtuOS9jeWtuOeoixzlt6XnqIvlrbjpmaIt6Leo57O75omA5a2456iLOuW3peeoi+WtuOmZoi3lt6XnqIvmioDooZPnoJTnqbbmiYDmioDogbflsIjmpa3nmbzlsZXlrbjnqIsl5bel56iL5a246ZmiLeadkOaWmeenkeWtuOiIh+W3peeoi+ezuwNBTEwVNQROVUxMBDQtQUQENC1DRAQ0LURFBDQtRFQENC1EWAQwLUFUBDAtQkIEMC1CRQQwLUNJBDAtQ1gEMC1FTgQwLUhDBDAtSUIEMC1NUwQwLVBBBDItQ1MEMi1FQwQyLUVFBDItRU8EMi1FVAQ1LUNDBDUtRVAENS1GTAQ1LUdFBDUtUEUENS1WRQQ2LUlCBDYtUEEENi1UQgQ2LVRNBDMtQkEEMy1GQgQzLUZOBDMtSU0EMy1NQQQzLU1CBDMtTUcEMy1NSQQzLVRCBDMtVE0EMS1BQwQxLUNFBDEtQ0gEMS1DVAQxLUdYBDEtTUUEMS1NUwQxLVJEBDEtUlMEMS1UVgQxLVRYAV8UKwM1Z2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2cWAWZkAgEPZBYCZg8QDxYIHwEFCUVkdV9Pcmdhbh8CBQZQZXJpb2QfAwUCTk8fBGdkEBUBCeS4jemBuOaThxUBBE5VTEwUKwMBZxYBZmQCAg9kFgJmDxAPFggfAQUJRWR1X09yZ2FuHwIFBWdyYWRlHwMFAk5PHwRnZBAVAQnkuI3pgbjmk4cVAQROVUxMFCsDAWcWAWZkAgMPZBYCZg8QDxYIHwEFCUVkdV9Pcmdhbh8CBQVDbGFzcx8DBQJOTx8EZ2QQFQEJ5LiN6YG45pOHFQEETlVMTBQrAwFnFgFmZAIED2QWCGYPZBYCZg8QDxYIHwEFCUVkdV9Pcmdhbh8CBRFDb2xsZWdlRGVwYXJ0bWVudB8DBQJOTx8EZ2QQFTUJ5LiN6YG45pOHFuioreioiOWtuOmZoi3lu7rnr4nns7si6Kit6KiI5a246ZmiLeWJteaEj+ioreioiOWtuOWjq+ePrRzoqK3oqIjlrbjpmaIt6Kit6KiI56CU56m25omAH+ioreioiOWtuOmZoi3lt6XllYbmpa3oqK3oqIjns7sr6Kit6KiI5a246ZmiLeWJteaEj+ioreioiOWtuOWjq+WtuOS9jeWtuOeoizHmh4nnlKjnp5HmioDlrbjpmaIt5oeJ55So56eR5oqA5a245aOr5a245L2N5a2456iLMeaHieeUqOenkeaKgOWtuOmZoi3phqvlrbjlt6XnqIvlrbjlo6vlrbjkvY3lrbjnqIso5oeJ55So56eR5oqA5a246ZmiLemGq+WtuOW3peeoi+eglOeptuaJgDHmh4nnlKjnp5HmioDlrbjpmaIt6Imy5b2p6IiH54Wn5piO56eR5oqA56CU56m25omAQOaHieeUqOenkeaKgOWtuOmZoi3oibLlvanlvbHlg4/oiIfnhafmmI7np5HmioDlrbjlo6vlrbjkvY3lrbjnqIso5oeJ55So56eR5oqA5a246ZmiLeaHieeUqOenkeaKgOeglOeptuaJgCXmh4nnlKjnp5HmioDlrbjpmaIt5LiN5YiG57O75a245aOr54+tNOaHieeUqOenkeaKgOWtuOmZoi3mmbrmhafosqHnlKLmrIrlrbjlo6vlrbjkvY3lrbjnqIs65oeJ55So56eR5oqA5a246ZmiLeaHieeUqOenkeaKgOeglOeptuaJgOadkOaWmeenkeaKgOWtuOeoiyLmh4nnlKjnp5HmioDlrbjpmaIt5bCI5Yip56CU56m25omAHOmbu+izh+WtuOmZoi3os4foqIrlt6XnqIvns7sc6Zu76LOH5a246ZmiLembu+izh+WtuOWjq+ePrRzpm7vos4flrbjpmaIt6Zu75qmf5bel56iL57O7Iumbu+izh+WtuOmZoi3lhYnpm7vlt6XnqIvnoJTnqbbmiYAc6Zu76LOH5a246ZmiLembu+WtkOW3peeoi+ezuyXkurrmlofnpL7mnIPlrbjpmaIt5Lq65paH56S+5pyD5a2456eRJeS6uuaWh+ekvuacg+WtuOmZoi3luKvos4fln7nogrLkuK3lv4Mi5Lq65paH56S+5pyD5a246ZmiLeaHieeUqOWkluiqnuezux/kurrmlofnpL7mnIPlrbjpmaIt6YCa6K2Y5a2456eRHOS6uuaWh+ekvuacg+WtuOmZoi3pq5TogrLlrqQx5Lq65paH56S+5pyD5a246ZmiLeaVuOS9jeWtuOe/kuiIh+aVmeiCsueglOeptuaJgDTmmbrmhafosqHnlKLlrbjpmaIt5pm65oWn6LKh55Si5qyK5a245aOr5a245L2N5a2456iLIuaZuuaFp+iyoeeUouWtuOmZoi3lsIjliKnnoJTnqbbmiYAx5pm65oWn6LKh55Si5a246ZmiLeenkeaKgOeuoeeQhuWtuOWjq+WtuOS9jeWtuOeoiyjmmbrmhafosqHnlKLlrbjpmaIt56eR5oqA566h55CG56CU56m25omAHOeuoeeQhuWtuOmZoi3kvIHmpa3nrqHnkIbns7sr566h55CG5a246ZmiLeiyoeWLmemHkeiejeWtuOWjq+WtuOS9jeWtuOeoiyLnrqHnkIblrbjpmaIt6LKh5YuZ6YeR6J6N56CU56m25omAHOeuoeeQhuWtuOmZoi3lt6Xmpa3nrqHnkIbns7sQ566h55CG5a246ZmiLU1CQRznrqHnkIblrbjpmaIt566h55CG5a245aOr54+tHOeuoeeQhuWtuOmZoi3nrqHnkIbnoJTnqbbmiYAc566h55CG5a246ZmiLeizh+ioiueuoeeQhuezuyvnrqHnkIblrbjpmaIt56eR5oqA566h55CG5a245aOr5a245L2N5a2456iLIueuoeeQhuWtuOmZoi3np5HmioDnrqHnkIbnoJTnqbbmiYAo5bel56iL5a246ZmiLeiHquWLleWMluWPiuaOp+WItueglOeptuaJgBzlt6XnqIvlrbjpmaIt5bel56iL5a245aOr54+tHOW3peeoi+WtuOmZoi3ljJblrbjlt6XnqIvns7sc5bel56iL5a246ZmiLeeHn+W7uuW3peeoi+ezuzflt6XnqIvlrbjpmaIt57ag6IO955Si5qWt5qmf6Zu75bel56iL5a245aOr5a245L2N5a2456iLHOW3peeoi+WtuOmZoi3mqZ/morDlt6XnqIvns7si5bel56iL5a246ZmiLeadkOaWmeenkeaKgOeglOeptuaJgDHlt6XnqIvlrbjpmaIt6auY6ZqO56eR5oqA56CU55m856Kp5aOr5a245L2N5a2456iLHOW3peeoi+WtuOmZoi3ot6jns7vmiYDlrbjnqIs65bel56iL5a246ZmiLeW3peeoi+aKgOihk+eglOeptuaJgOaKgOiBt+WwiOalreeZvOWxleWtuOeoiyXlt6XnqIvlrbjpmaIt5p2Q5paZ56eR5a246IiH5bel56iL57O7A0FMTBU1BE5VTEwENC1BRAQ0LUNEBDQtREUENC1EVAQ0LURYBDAtQVQEMC1CQgQwLUJFBDAtQ0kEMC1DWAQwLUVOBDAtSEMEMC1JQgQwLU1TBDAtUEEEMi1DUwQyLUVDBDItRUUEMi1FTwQyLUVUBDUtQ0MENS1FUAQ1LUZMBDUtR0UENS1QRQQ1LVZFBDYtSUIENi1QQQQ2LVRCBDYtVE0EMy1CQQQzLUZCBDMtRk4EMy1JTQQzLU1BBDMtTUIEMy1NRwQzLU1JBDMtVEIEMy1UTQQxLUFDBDEtQ0UEMS1DSAQxLUNUBDEtR1gEMS1NRQQxLU1TBDEtUkQEMS1SUwQxLVRWBDEtVFgBXxQrAzVnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZxYBZmQCAQ9kFgJmDxAPFggfAQUJRWR1X09yZ2FuHwIFBlBlcmlvZB8DBQJOTx8EZ2QQFQEJ5LiN6YG45pOHFQEETlVMTBQrAwFnFgFmZAICD2QWAmYPEA8WCB8BBQlFZHVfT3JnYW4fAgUFZ3JhZGUfAwUCTk8fBGdkEBUBCeS4jemBuOaThxUBBE5VTEwUKwMBZxYBZmQCAw9kFgJmDxAPFggfAQUJRWR1X09yZ2FuHwIFBUNsYXNzHwMFAk5PHwRnZBAVAQnkuI3pgbjmk4cVAQROVUxMFCsDAWcWAWZkAgEPZBYCZg9kFgJmD2QWAgIBD2QWAmYPZBYCZg8PFgIfAGhkZAItD2QWAmYPZBYCZg9kFgQCAQ8QZGQWAGQCAw8QZGQWAGQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgcFB0FjYjAxMDEFB0FjYjYxMDEFB0FjYjYxMDIFB0JDSDAxMDEFCUNoZWNrYm94MwUKQ2hlY2tib3hfRwUKQ2hlY2tib3hfQ+uCwQWDUPnxGtKyzlOpMMI9Or4l',
    '__VIEWSTATEGENERATOR': 'E915CB73',
    '__EVENTVALIDATION': '/wEWIwKUy5KWAwL2q8D8CgLM9PumDwLbwqJnAtvWyYkGArGS9rMFAoqms9AKAr6QrdYMAr/MoaAHAq6dkvUKAtLd/qAJAruMlvkDAur23IwNArbvmZUJAoD+udsJAqOG6aIDAu/woqsPAo22OQLg4fq/BgKs2re4AgKsmt66CgL/oILYBwLUrJXtBQL/oIrXCgKaiqjsBAKO29LaCAKo/pC1DAK9oL7oBwK6oL7oBwK7oL7oBwKA5NfcCQKU4+PeCQKU49PeCQLYm+qMCwLFounGCAOO+d/KAOUh5Qsgn5g3b9A2DXIc',
    'semester_list': '1061 (一百零六學年度第一學期)',
    'Acb0101': 'on',
    'BCH0101': 'on',
    'Ctb0101': '',
    'Ctb0201': '',
    'Ctb0301': '',
    'Checkbox_G': 'on',
    'QuerySend': '送出查詢'
}

sess = requests.session()
soup = BeautifulSoup(sess.post('http://140.118.31.215/querycourse/ChCourseQuery/QueryCondition.aspx', data=data).text, "html5lib")
for i in soup.select('table')[1].select('tr')[1:]:
    csv.writer(open('course/' + i.select('td')[1].text + '.csv', 'a', encoding='utf8', newline='')).writerow([i.select('td')[j].text for j in E])


# In[2]:

import csv
a=[1,2,3,4,5]
with open('test.csv', 'w', encoding='utf8') as file:
    for i in range(5):
        csv.writer(file).writerow(a)


# In[ ]:



