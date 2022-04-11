import os
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api, json
import requests
import datetime
import random
import time

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
        [get_but('портфель', 'default')]
    ]
}
keyboard1 = json.dumps(keyboard1, ensure_ascii = False).encode('utf-8')
keyboard2 = {
    "one_time" : False,
    "buttons" : [
        [get_but('Apple', 'default'), get_but('Intel', 'default')],
        [get_but('Газпром', 'default'), get_but('Яндекс', 'default')],
        [get_but('назад', 'primary')]
    ]
}
keyboard2 = json.dumps(keyboard2, ensure_ascii = False).encode('utf-8')
keyboard3 = {
    "one_time" : False,
    "buttons" : [
        [get_but('пополнить', 'default'), get_but('вывести', 'default')],
        [get_but('купить', 'positive'), get_but('продать', 'negative')],
        [get_but('назад', 'secondary')]
    ]
}
keyboard3 = json.dumps(keyboard3, ensure_ascii = False).encode('utf-8')
##########################################################################################


def getList(name): #получение ключевых слов для определения процента связанности и настроения
    gazp=open(name+'.txt', 'rb').read().decode('utf-8')
    gazp=gazp.split(',')
    for i in range(len(gazp)):
        gazp[i] = gazp[i].split('_')
        gazp[i][1] = int(gazp[i][1])
        gazp[i][0] = gazp[i][0].replace(' ', '')
    return gazp

def getNewsList(date): #получение списка новостей по дате с сайта ria.ru
    txt=''
    rq=requests
    date=date.replace('-','')
    while len(txt) < 33100:
        txt=rq.get('https://ria.ru/'+date).content.decode('utf-8')
        if len(txt) < 3310:
            time.sleep(1)
        time.sleep(1)
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
    for m in range(30):
        date=getYe(m)
        print(date)
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
            print('Эта новость связана с бумагой с вероятностью:', k)
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

def getDiv(na): #получение дивидендной доходности компании
    rq=requests
    txt = rq.get('https://www.google.com/finance/quote/' + na).content.decode('utf-8')
    n=txt.find('%</div></div><div class="gyFHrc">')
    i=0
    st=''
    while txt[n-i-1] in '0123456789.,':
        st=txt[n-i-1]+st
        i+=1
    st=st.replace('.','')
    return int(st)/100

def getEarn(na): #получение доходов, расходов и чистой прибыли компаний
    rq=requests
    txt = rq.get('https://www.google.com/finance/quote/' + na).content.decode('utf-8')
    n=txt.find('</div></td><td class="QXDnM">')
    print(n)
    i=0
    st=''
    print(txt[n+29])
    while txt[n+i+29] in '0123456789.,-':
        st=st+txt[n+i+29]
        i+=1
    n=txt.rfind('</div></td><td class="QXDnM">')
    print(n)
    i=0
    st1=''
    print(txt[n+29])
    while txt[n+i+29] in '0123456789.,-':
        st1=st1+txt[n+i+29]
        i+=1
    if na == 'GAZP:MCX':
        st=st.replace('.','')
        st1=st1.replace('.','')
        st=int(st)*10
        st1=int(st1)/100
    else:
        st=st.replace('.','')
        st1=st1.replace('.','')
        st=int(st)/100
        st1=int(st1)/100
    return [st, st1, st-st1]

def getPrice(na): #получаем цену акции
    rq=requests
    txt=rq.get('https://www.google.com/finance/quote/' + na).content.decode('utf-8')
    n=txt.find('class="kf1m0"><div class="YMlKec fxKbKc">')
    i=0
    price=''
    while txt[n+42+i] in '1234567890.,':
        price=price+txt[n+42+i]
        i+=1
    price=price.replace(',','')
    price=price.replace('.','')
    return int(price)/100

def sender(id, text): #отправка сообщений и клавиатур
    vk_session.method('messages.send', {'user_id' : id, 'message' : text, 'random_id' : 0, 'keyboard' : keyboard})

wait = ['Ожидайте. Мы генерируем прогноз.', 'Ждите...', 'Это может занять пару минут', 'Потребуется немного времени. Ожидайте.', 'Принято в обработку']

###сам бот###
while True:
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.from_user and not (event.from_me):
                    mes = event.text.lower()
                    iid = event.user_id
                    if mes == 'начать' or mes == 'назад' or mes == 'выйти':
                        keyboard = str(keyboard1.decode('utf-8'))
                        sender(iid, 'Выберите опцию.')
                    elif mes == 'генерация прогноза':
                        keyboard = str(keyboard2.decode('utf-8'))
                        sender(iid, 'Выберите ценную бумагу')
                    elif mes == 'газпром':
                        keyboard = str(keyboard1.decode('utf-8'))
                        sender(iid, wait[random.randint(0, len(wait)-1)])
                        inf=generatePrognoz('gazp')
                        div=getDiv('GAZP:MCX')
                        earn=getEarn('GAZP:MCX')
                        price=getPrice('GAZP:MCX')
                        n=23673512900 #эмиссия
                        cap=n*price
                        cpe = cap/(cap-(earn[1]*1000000000))
                        print(cpe, earn[1], cap)
                        if inf > 0:
                            infe=inf*earn[0]/earn[2]*cpe
                        else:
                            infe=inf*earn[2]/earn[0]*cpe
                        if infe > 3:
                            itog = 'покупать'
                        elif infe > -3:
                            itog = 'держать'
                        else:
                            itog = 'продавать'
                        sender(iid, 'Прогноз готов!\n\nИнфополе: ' + str(round(inf, 2)) + '\n\n(информационная повестка, уровень волнений. 0 - нейтрально. Чем выше этот показатель, тем лучше настроения вокруг этой бумаги.\n\nЧистая прибыль: ' + str(earn[1]) +' млрд рублей\nДоход: ' + str(earn[0]) + ' млрд рублей\nДивидендная доходность: ' + str(div) + '% от стоимости бумаги\n\nИтоговый прогноз: ' + itog + '\n\nПрогноз сгенерирован автоматически и не является финансовой рекомендацией.')
                    elif mes == 'яндекс':
                        keyboard = str(keyboard1.decode('utf-8'))
                        sender(iid, wait[random.randint(0, len(wait)-1)])
                        inf=generatePrognoz('yand')
                        earn=getEarn('YNDX:MCX')
                        price=getPrice('YNDX:MCX')
                        n=323800479 #эмиссия
                        cap=n*price
                        cpe = cap/(cap-(earn[1]*1000000000))
                        print(cpe, earn[1], cap)
                        if inf > 0:
                            infe=inf*earn[0]/earn[2]*cpe
                        else:
                            infe=inf*earn[2]/earn[0]*cpe
                        if infe > 2:
                            itog = 'покупать'
                        elif infe > -2:
                            itog = 'держать'
                        else:
                            itog = 'продавать'
                        sender(iid, 'Прогноз готов!\n\nИнфополе: ' + str(round(inf, 2)) + '\n\n(информационная повестка, уровень волнений. 0 - нейтрально. Чем выше этот показатель, тем лучше настроения вокруг этой бумаги.\n\nЧистая прибыль: ' + str(earn[1]) +' млрд рублей\nДоход: ' + str(earn[0]) + ' млрд рублей\nДивиденды: не выплачиваются\n\nИтоговый прогноз: ' + itog + '\n\nПрогноз сгенерирован автоматически и не является финансовой рекомендацией.')
                    elif mes == 'apple':
                        keyboard = str(keyboard1.decode('utf-8'))
                        sender(iid, wait[random.randint(0, len(wait)-1)])
                        inf=generatePrognoz('appl')
                        earn=getEarn('AAPL:NASDAQ')
                        div=getDiv('AAPL:NASDAQ')
                        price=getPrice('AAPL:NASDAQ')
                        n=16319441000 #эмиссия
                        cap=n*price
                        cpe = cap/(cap-(earn[1]*1000000000))
                        if inf > 0:
                            infe=inf*earn[0]/earn[2]*cpe
                        else:
                            infe=inf*earn[2]/earn[0]*cpe
                        if infe > 1:
                            itog = 'покупать'
                        elif infe > -1:
                            itog = 'держать'
                        else:
                            itog = 'продавать'
                        sender(iid, 'Прогноз готов!\n\nИнфополе: ' + str(round(inf, 2)) + '\n\n(информационная повестка, уровень волнений. 0 - нейтрально. Чем выше этот показатель, тем лучше настроения вокруг этой бумаги.\n\nЧистая прибыль: ' + str(earn[1]) +' млрд долларов\nДоход: ' + str(earn[0]) + ' млрд долларов\nДивидендная доходность: ' + str(div) + '% от стоимости бумаги\n\nИтоговый прогноз: ' + itog + '\n\nПрогноз сгенерирован автоматически и не является финансовой рекомендацией.')
                    elif mes == 'intel':
                        keyboard = str(keyboard1.decode('utf-8'))
                        sender(iid, wait[random.randint(0, len(wait)-1)])
                        inf=generatePrognoz('intel')
                        earn=getEarn('INTC:NASDAQ')
                        div=getDiv('INTC:NASDAQ')
                        price=getPrice('INTC:NASDAQ')
                        n=4072000000 #эмиссия
                        cap=n*price
                        cpe = cap/(cap-(earn[1]*1000000000))
                        if inf > 0:
                            infe=inf*earn[0]/earn[2]*cpe
                        else:
                            infe=inf*earn[2]/earn[0]*cpe
                        if infe > 1:
                            itog = 'покупать'
                        elif infe > -1:
                            itog = 'держать'
                        else:
                            itog = 'продавать'
                        sender(iid, 'Прогноз готов!\n\nИнфополе: ' + str(round(inf, 2)) + '\n\n(информационная повестка, уровень волнений. 0 - нейтрально. Чем выше этот показатель, тем лучше настроения вокруг этой бумаги.\n\nЧистая прибыль: ' + str(earn[1]) +' млрд долларов\nДоход: ' + str(earn[0]) + ' млрд долларов\nДивидендная доходность: ' + str(div) + '% от стоимости бумаги\n\nИтоговый прогноз: ' + itog + '\n\nПрогноз сгенерирован автоматически и не является финансовой рекомендацией.')
    except Exception as e:
        print(e)
