import os
import pyautogui as pya
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api, json
import requests
import datetime

#подключение к группе вк
token = open('key.txt', 'rb').read().decode('utf-8') #получения токена для доступа к группе из отдельного файла
vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

#построение кнопки на клавиатуре
def get_but(text, color):
    return {
                "action": {
                    "type": "text",
                    "payload": "{\"button\": \"" + "1" + "\"}",
                    "label": f"{text}"
                },
                "color": f"{color}"
            }


#клавиатуры:
#########################################################################################
keyboard1 = {
    "one_time" : False,
    "buttons" : [
        [get_but('генерация прогноза', 'default')],
        [get_but('автоторговля', 'default')]
    ]
}
keyboard1 = json.dumps(keyboard1, ensure_ascii = False).encode('utf-8')
keyboard2 = {
    "one_time" : False,
    "buttons" : [
        [get_but('Apple', 'default'), get_but('Intel', 'default')],
        [get_but('Газпром', 'default'), get_but('Яндекс', 'default')],
        [get_but('другое', 'primary')]
    ]
}
keyboard2 = json.dumps(keyboard2, ensure_ascii = False).encode('utf-8')
##########################################################################################


def getList(name): #получение ключевых слов для определения процента связанности и настроения
    gazp=open(name+'.txt', 'rb').read().decode('utf-8')
    gazp=gazp.split(',')
    for i in range(len(gazp)):
        gazp[i] = gazp[i].split('_')
        gazp[i][1] = int(gazp[i][1])
        gazp[i][0] = gazp[i][0].replace(' ', '')
    return gazp

def getNewsList(date): #получение списка сегодняшних новостей
    rq=requests
    date=date.replace('-','')
    txt=rq.get('https://ria.ru/'+date).content.decode('utf-8')
    a=txt.find('<span class="m-email"></span></div><div c')
    b=txt.find('Архив</a></div></div></div><div class="footer__copyright"><div class="footer__copyright-col">')
    txt=txt[a:b]
    txt=txt.split('content=')
    return txt

def getYe(m): #получение даты, которая была m-ное количество дней назад
    date_format = '%d.%m.%Y'
    date = datetime.datetime.now()
    date = date + datetime.timedelta(days=0-m)
    date = str(date.date()).replace('-','')
    return date

def generatePrognoz(company): #генерация прогноза
    gazppoint=0
    for m in range(7):
        date=getYe(m)
        new=getNewsList(date)
        for u in range(1,len(new)):
            news=new[u]
            k=1
            news=news.replace('ё','е')
            gazp=getList(company)
            for i in range(len(gazp)):
                if gazp[i][0] in news:
                    k=k*(1-(gazp[i][1]/100))
                    print(gazp[i][0])
            bad=open('bad.txt', 'rb').read().decode('utf-8')
            bad=bad.split(',')
            for i in range(len(bad)):
                bad[i] = bad[i].split('_')
                bad[i][1] = int(bad[i][1])
                bad[i][0] = bad[i][0].replace(' ', '')
            good=open('good.txt', 'rb').read().decode('utf-8')
            good=good.split(',')
            for i in range(len(good)):
                good[i] = good[i].split('_')
                good[i][1] = int(good[i][1])
                good[i][0] = good[i][0].replace(' ', '')
            k=1-k
            print('Эта новость связана с газпромом с вероятностью:', k)
            for i in range(len(good)):
                if good[i][0] in news:
                    gazppoint=gazppoint+(good[i][1]*k)
                    print('Хорошее слово', good[i][0])
            for i in range(len(bad)):
                if bad[i][0] in news:
                    gazppoint=gazppoint-(bad[i][1]*k)
                    print('Плохое слово', bad[i][0])
            print('инфополе', gazppoint)
    return gazppoint

def sender(id, text): #отправка сообщений и клавиатур
    vk_session.method('messages.send', {'user_id' : id, 'message' : text, 'random_id' : 0, 'keyboard' : keyboard})

###сам бот###
while True:
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.from_user and not (event.from_me):
                    mes = event.text.lower()
                    iid = event.user_id
                    if mes == 'начать':
                        keyboard = str(keyboard1.decode('utf-8'))
                        sender(iid, 'Выберите опцию.')
                    elif mes == 'генерация прогноза':
                        keyboard = str(keyboard2.decode('utf-8'))
                        sender(iid, 'Выберите ценную бумагу')
                    elif mes == 'газпром':
                        keyboard = str(keyboard1.decode('utf-8'))
                        inf=generatePrognoz('gazp')
                        sender(iid, 'Инфополе: ' + str(inf))
                    elif mes == 'яндекс':
                        keyboard = str(keyboard1.decode('utf-8'))
                        inf=generatePrognoz('yand')
                        sender(iid, 'Инфополе: ' + str(inf))
                    elif mes == 'apple':
                        keyboard = str(keyboard1.decode('utf-8'))
                        inf=generatePrognoz('appl')
                        sender(iid, 'Инфополе: ' + str(inf))
                    elif mes == 'intel':
                        keyboard = str(keyboard1.decode('utf-8'))
                        inf=generatePrognoz('intel')
                        sender(iid, 'Инфополе: ' + str(inf))
                    elif mes == 'автоторговля':
                        pass #пока недоступно
    except Exception as e:
        print(e)
