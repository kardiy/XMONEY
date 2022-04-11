import os
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api, json
import requests
import datetime
import random
import time
from SimpleQIWI import *
import pyqiwi
from tinkoff.invest import Client, RequestError, OrderDirection, OrderType, CandleInterval

itoken=open('itoken.txt','rb').read().decode('utf-8')

with Client(itoken) as client:
            #r=client.users.get_accounts()
    r = client.instruments.currencies()
    #r = client.market_data.last_price(
        #figi='BBG0013HJJ31',
        #price=1,
        #time=datetime.datetime.now()
        #)
    print(r)
           
def buyPaper(ffg,s):
    global itoken
    try:
        with Client(itoken) as client:
            #r=client.users.get_accounts()
            r = client.orders.post_order(
                order_id=str(datetime.datetime.utcnow().timestamp()),
                figi=ffg,
                quantity=s,
                account_id='2061859449',
                direction=OrderDirection.ORDER_DIRECTION_BUY,
                order_type=OrderType.ORDER_TYPE_MARKET
            )
            return True
    except:
        return False

def sellPaper(ffg,s):
    global itoken
    with Client(itoken) as client:
        #r=client.users.get_accounts()
        r = client.orders.post_order(
            order_id=str(datetime.datetime.utcnow().timestamp()),
            figi=ffg,
            quantity=s,
            account_id='2061859449',
            direction=OrderDirection.ORDER_DIRECTION_SELL,
            order_type=OrderType.ORDER_TYPE_MARKET
        )
        print(r)
    

#подключение к группе вк
token = open('key.txt', 'rb').read().decode('utf-8') #получения токена для доступа к группе из отдельного файла
vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

#QIWI
qtoken = open('qtoken.txt', 'rb').read().decode('utf-8')
phone = '+79031819779'
api = QApi(token=qtoken, phone=phone)
print(api.balance)

    
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

def sender(id, text): #отправка сообщений и клавиатур
    vk_session.method('messages.send', {'user_id' : id, 'message' : text, 'random_id' : 0, 'keyboard' : keyboard})

def nullWays(arr, iid): #удаление элементов из массива
    i=0
    while i < len(arr):
        if arr[i] == iid:
            arr.pop(i)
        else:
            i+=1
    return arr

###########################################################################################
keyboard1 = {
    "one_time" : False,
    "buttons" : [
        [get_but('доллар', 'secondary'),get_but('евро', 'secondary')],
        [get_but('отменить', 'default')]
    ]
}
keyboard1 = json.dumps(keyboard1, ensure_ascii = False).encode('utf-8')
keyboard2 = {
    "one_time" : False,
    "buttons" : [
        [get_but('отменить', 'secondary')]
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
###########################################################################################

def buildKey(): #построение рандомного ключа
    symbols='qwertyuioplkjhgfdsazxcvbnm1234567890'
    string=''
    for i in range(30):
        string=string+symbols[random.randint(0,len(symbols)-1)]
    return string

#получение оператора
def mobile_operator(phone_number):
    s = requests.Session()
    res = s.post('https://qiwi.com/mobile/detect.action', data = {'phone': phone_number })
    s.headers['Accept'] = 'application/json'
    s.headers['Content-Type'] = 'application/x-www-form-urlencoded'
    return res.json()['message']

# Оплата мобильного телефона, взято с официального сайта qiwi
def send_mobile(api_access_token, prv_id, to_account, comment, sum_pay):
    s = requests.Session()
    s.headers['Accept'] = 'application/json'
    s.headers['Content-Type'] = 'application/json'
    s.headers['authorization'] = 'Bearer ' + api_access_token
    postjson = {"id":"","sum": {"amount":"","currency":"643"},"paymentMethod": {"type":"Account","accountId":"643"},"comment":"","fields": {"account":""}}
    postjson['id'] = str(int(time.time() * 1000))
    postjson['sum']['amount'] = sum_pay
    postjson['fields']['account'] = to_account
    postjson['comment'] = comment
    res = s.post('https://edge.qiwi.com/sinap/api/v2/terms/'+prv_id+'/payments', json = postjson)
    return res.json()

def card_system(card_number): #получение провайдера карты
    s = requests.Session()
    res = s.post('https://qiwi.com/card/detect.action', data = {'cardNumber': card_number })
    return res.json()['message']

def send_card(api_access_token, payment_data): #отправка денег на карте
    # payment_data - dictionary with all payment data
    s = requests.Session()
    s.headers['Accept'] = 'application/json'
    s.headers['Content-Type'] = 'application/json'
    s.headers['authorization'] = 'Bearer ' + api_access_token
    postjson = {"id":"","sum": {"amount":"","currency":"643"},"paymentMethod": {"type":"Account","accountId":"643"},"fields": {"account":""}}
    postjson['id'] = str(int(time.time() * 1000))
    postjson['sum']['amount'] = payment_data.get('sum')
    postjson['fields']['account'] = payment_data.get('to_card')
    prv_id = payment_data.get('prv_id')
    if payment_data.get('prv_id') in ['1960', '21012']:
        postjson['fields']['rem_name'] = payment_data.get('rem_name')
        postjson['fields']['rem_name_f'] = payment_data.get('rem_name_f')
        postjson['fields']['reg_name'] = payment_data.get('reg_name')
        postjson['fields']['reg_name_f'] = payment_data.get('reg_name_f')
        postjson['fields']['rec_city'] = payment_data.get('rec_address')
        postjson['fields']['rec_address'] = payment_data.get('rec_address')
        
    res = s.post('https://edge.qiwi.com/sinap/api/v2/terms/' + prv_id + '/payments', json = postjson)
    return res.json()

def getP(na):
    rq=requests
    txt = rq.get('https://www.google.com/finance/quote/' + na).content.decode('utf-8')
    n=txt.find('data-target="RUB" data-last-price="')
    i=0
    price=''
    while txt[n+35+i] in '1234567890.,':
        price=price+txt[n+35+i]
        i+=1
    price=price.replace(',','')
    price=price.split('.')
    return int(price[0])+(int(price[1])/(10**len(price[1])))
print(getP('CNY-RUB'))
def buyWallute(kodek, iid, keyboard2, keyboard3, mes,s):
    s=s*1000
    curs = getP(kodek)
    price=(s*curs)/100*115
    ball=float(open('balances/' + str(iid) + '.txt', 'rb').read().decode('utf-8'))
    global keyboard
    if ball >= price:
        keyboard = str(keyboard3.decode('utf-8'))
        ball=ball-price
        open('balances/' + str(iid) + '.txt', 'wb').write(str(ball).encode('utf-8'))
        sender(iid, 'Поздравляем! Вы купили ' + mes + ' долларов за ' + str(price) + ' рублей')
        dball=float(open(kodek + '/' + str(iid) + '.txt', 'rb').read().decode('utf-8'))
        dball=dball+s
        open(kodek + '/' + str(iid) + '.txt', 'wb').write(str(dball).encode('utf-8'))
    else:
        keyboard = str(keyboard2.decode('utf-8'))
        sender(iid, 'Увы, невозможно совершить покупку, так как на вашем счёте недостаточно средств')
        
def sellWallute(kodek, iid, keyboard2, keyboard3, mes,s):
    s=s*1000
    curs = getP(kodek)
    price=(s*curs)-(s*curs/100*15)
    dball=float(open(kodek + '/' + str(iid) + '.txt', 'rb').read().decode('utf-8'))
    if dball >= s:
        keyboard = str(keyboard3.decode('utf-8'))
        ball=float(open('balances/' + str(iid) + '.txt', 'rb').read().decode('utf-8'))
        ball=ball+price
        open('balances/' + str(iid) + '.txt', 'wb').write(str(ball).encode('utf-8'))
        sender(iid, 'Поздравляем! Вы продали ' + mes + ' долларов за ' + str(price) + ' рублей')
        dball=dball-s
        open(kodek + '/' + str(iid) + '.txt', 'wb').write(str(dball).encode('utf-8'))
    else:
        keyboard = str(keyboard2.decode('utf-8'))
        sender(iid, 'Увы, невозможно совершить продажу, так как на вашем счёте недостаточно средств')
        
toPay=[]
toPayS=[]
toPayM=[]
toTake=[]

toSell=[]
toBuy=[]
#запросы на закупки:
stD=[] #долларов
stE=[] #евро

btD=[]
btE=[]

while True:
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.from_user and not (event.from_me):
                    mes = event.text.lower()
                    iid = event.user_id
                    if iid in toPay or iid in toPayS or iid in toTake or iid in stD or iid in stE or iid in btD or iid in btE:
                        if mes == 'отменить':
                            toPay=nullWays(toPay, iid)
                            toPayS=nullWays(toPayS, iid)
                            toTake=nullWays(toTake, iid)
                            stD=nullWays(stD, iid)
                            stE=nullWays(stE, iid)
                            btD=nullWays(btD, iid)
                            btE=nullWays(btE, iid)
                            keyboard = str(keyboard3.decode('utf-8'))
                            sender(iid, 'отменено')
                        else:
                            if iid in toTake:
                                s=int(mes)
                                i=0
                                while i < len(toTake):
                                    if toTake[i] == iid:
                                        toTake.pop(i)
                                    else:
                                        i+=1
                                open('sums/' + str(iid) + '.txt', 'wb').write(mes.encode('utf-8'))
                                comment=buildKey()
                                open('comments/' + str(iid) + '.txt', 'wb').write(comment.encode('utf-8'))
                                keyboard = str(keyboard3.decode('utf-8'))
                                sender(iid, 'Пополните наш QIWI-кошелёк по ссылке qiwi.com/n/MRKARDIY на сумму ' + mes + '₽ (платёж не пройдёт, если указать другую сумму). В комментарии к переводу вставьте следующий ключ: ' + comment)
                            elif iid in toPay:
                                try:
                                    s=int(mes)
                                    if s < 10:
                                        sender(iid, 'Минимальная сумма платежа 10 рублей')
                                    else:
                                        ball=float(open('balances/' + str(iid) + '.txt', 'rb').read().decode('utf-8'))
                                        if ball >= s:
                                            i=0
                                            while i < len(toPay):
                                                if toPay[i] == iid:
                                                    toPay.pop(i)
                                                else:
                                                    i+=1
                                            toPayS.append(iid)
                                            toPayM.append(s)
                                            keyboard = str(keyboard2.decode('utf-8'))
                                            sender(iid, 'Вывод осуществляется на банковские карты, QIWI-кошельки и на балансы SIM-карт. Укажите номер QIWI кошелька в формате +71112223344, номер телефона в том же формате с приставкой n+71112223344 или номер карты.')
                                        else:
                                            keyboard = str(keyboard2.decode('utf-8'))
                                            sender(iid, 'Недостато средств для совершения операции')
                                except:
                                    keyboard = str(keyboard2.decode('utf-8'))
                                    sender(iid, 'Некорректная сумма платежа')
                            elif iid in toPayS:
                                i=0
                                while i < len(toPayS):
                                    if toPayS[i] == iid:
                                        tp=toPayM[i]
                                        toPayS.pop(i)
                                        toPayM.pop(i)
                                    else:
                                        i+=1
                                keyboard = str(keyboard3.decode('utf-8'))
                                if mes[0] == '+':
                                    try:
                                        api.pay(account=mes[1:], amount=tp)
                                        ee=str(float(open('balances/' + str(iid) + '.txt', 'rb').read().decode('utf-8'))-tp)
                                        open('balances/' + str(iid) + '.txt', 'wb').write(ee.encode('utf-8'))
                                        sender(iid, 'Вывод поступил в обработку. Ожидайте пополнения счёта')
                                    except Exception as e:
                                        sender(iid, e)
                                elif mes[0] == 'n':
                                    try:
                                        send_mobile(qtoken, mobile_operator(mes[1:]), mes[3:], 'Перевод от XMoney', tp)
                                        ee=str(float(open('balances/' + str(iid) + '.txt', 'rb').read().decode('utf-8'))-tp)
                                        open('balances/' + str(iid) + '.txt', 'wb').write(ee.encode('utf-8'))
                                        sender(iid, 'Вывод поступил в обработку. Ожидайте пополнения счёта')
                                    except Exception as e:
                                        sender(iid, e)
                                else:
                                    try:
                                        if tp > 99:
                                            send_card(qtoken, {'sum': ((tp-50)/102)*100, 'to_card': mes, 'prv_id': card_system(mes), 'rem_name': 'a', 'rem_name_f': 'b', 'reg_name': 'a', 'reg_name_f': 'b', 'rec_address': '10001'})
                                            ee=str(float(open('balances/' + str(iid) + '.txt', 'rb').read().decode('utf-8'))-tp)
                                            open('balances/' + str(iid) + '.txt', 'wb').write(ee.encode('utf-8'))
                                            sender(iid, 'Вывод поступил в обработку. Ожидайте пополнения счёта')
                                        else:
                                            sender(iid, 'Минимальная сумма вывода на карту - 100 рублей')
                                    except Exception as e:
                                        sender(iid, e)
                            if iid in stD or iid in stE or iid in btD or iid in btE:
                                try:
                                    s=int(mes)
                                    if s > 0:
                                        if iid in stD:
                                            try:
                                                buyPaper('BBG0013HJJ31',s)
                                                stD=nullWays(stD, iid)
                                                buyWallute('USD-RUB', iid, keyboard2, keyboard3, mes,s)
                                            except:
                                                keyboard = str(keyboard2.decode('utf-8'))
                                                sender(iid, '')
                                        if iid in stE:
                                            stE=nullWays(stE, iid)
                                            buyWallute('EUR-RUB', iid, keyboard2, keyboard3, mes,s)
                                        if iid in btD:
                                            btD=nullWays(btD, iid)
                                            sellWalute('USD-RUB', iid, keyboard2, keyboard3, mes,s)
                                        if iid in btE:
                                            btE=nullWays(btE, iid)
                                            sellWalute('EUR-RUB', iid, keyboard2, keyboard3, mes,s)
                                    else:
                                        keyboard = str(keyboard2.decode('utf-8'))
                                        sender(iid, 'Натуральное число')
                                except:
                                    keyboard = str(keyboard2.decode('utf-8'))
                                    sender(iid, 'Некорректная сумма')
                    else:
                        if mes == 'портфель':
                            try:
                                ball=float(open('balances/' + str(iid) + '.txt', 'rb').read().decode('utf-8'))
                            except:
                                open('balances/' + str(iid) + '.txt', 'wb').write(b'0')
                                ball=0
                            try:
                                dball=float(open('USD-RUB/' + str(iid) + '.txt', 'rb').read().decode('utf-8'))
                            except:
                                open('USD-RUB/' + str(iid) + '.txt', 'wb').write(b'0')
                                dball=0
                            try:
                                eball=float(open('EUR-RUB/' + str(iid) + '.txt', 'rb').read().decode('utf-8'))
                            except:
                                open('EUR-RUB/' + str(iid) + '.txt', 'wb').write(b'0')
                                eball=0
                            keyboard = str(keyboard3.decode('utf-8'))
                            sender(iid, 'Баланс в рублях: ' + str(ball) + '\nБаланс в долларах: ' + str(dball) + '\nБаланс в евро: ' + str(eball))
                        elif mes == 'вывести':
                            keyboard = str(keyboard2.decode('utf-8'))
                            sender(iid, 'Укажите сумму в рублях, которую хотите вывести')
                            toPay.append(iid)
                        elif mes == 'пополнить':
                            keyboard = str(keyboard2.decode('utf-8'))
                            sender(iid, 'Укажите сумму в рублях, которую хотите зачислить на счёт')
                            toTake.append(iid)
                        elif mes == 'купить':
                            toSell=nullWays(toSell, iid)
                            toBuy.append(iid)
                            keyboard = str(keyboard1.decode('utf-8'))
                            sender(iid, 'Что Вы хотите купить?')
                        elif mes == 'продать':
                            toBuy=nullWays(toBuy, iid)
                            toSell.append(iid)
                            keyboard = str(keyboard1.decode('utf-8'))
                            sender(iid, 'Что Вы хотите продать?')
                        elif iid in toBuy:
                            if mes == 'отменить':
                                toBuy=nullWays(toBuy, iid)
                                keyboard = str(keyboard3.decode('utf-8'))
                                sender(iid, 'Покупка отменена')
                            elif mes == 'доллар':
                                toBuy=nullWays(toBuy, iid)
                                keyboard = str(keyboard2.decode('utf-8'))
                                sender(iid, 'Курс доллара: ' + str(getP('USD-RUB')) + '. Комиссия 15%. Сколько лотов этой валюты Вы хотите купить?')
                                stD.append(iid)
                            elif mes == 'евро':
                                toBuy=nullWays(toBuy, iid)
                                keyboard = str(keyboard2.decode('utf-8'))
                                sender(iid, 'Курс евро: ' + str(getP('EUR-RUB')) + '. Комиссия 15%. Сколько лотов этой валюты Вы хотите купить?')
                                stE.append(iid)
                        elif iid in toSell:
                            if mes == 'отменить':
                                toSell=nullWays(toSell, iid)
                                keyboard = str(keyboard3.decode('utf-8'))
                                sender(iid, 'Продажа отменена')
                            elif mes == 'доллар':
                                toSell=nullWays(toSell, iid)
                                keyboard = str(keyboard2.decode('utf-8'))
                                sender(iid, 'Курс доллара: ' + str(getP('USD-RUB')) + '. Комиссия 15%. Сколько лотов этой валюты Вы хотите продать?')
                                btD.append(iid)
                            elif mes == 'евро':
                                toSell=nullWays(toSell, iid)
                                keyboard = str(keyboard2.decode('utf-8'))
                                sender(iid, 'Курс евро: ' + str(getP('EUR-RUB')) + '. Комиссия 15%. Сколько лотов этой валюты Вы хотите продать?')
                                btE.append(iid)
                        
    except Exception as e:
        print(e)
