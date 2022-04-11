from SimpleQIWI import *
import os
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api, json
import time
import requests
def payment_history_last(my_login, api_access_token, rows_num, next_TxnId, next_TxnDate):
    s = requests.Session()
    s.headers['authorization'] = 'Bearer ' + api_access_token  
    parameters = {'rows': rows_num, 'nextTxnId': next_TxnId, 'nextTxnDate': next_TxnDate}
    h = s.get('https://edge.qiwi.com/payment-history/v2/persons/' + my_login + '/payments', params = parameters)
    return h.json()

api = QApi(token=open('qtoken.txt', 'rb').read().decode('utf-8'), phone='+79031819779')
a=api.payments
print(type(a.get('data')[0].get('total').get('amount')))

#подключение к группе вк
token = open('key.txt', 'rb').read().decode('utf-8') #получения токена для доступа к группе из отдельного файла
vk_session = vk_api.VkApi(token=token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def sender(id, text): #отправка сообщений
    vk_session.method('messages.send', {'user_id' : id, 'message' : text, 'random_id' : 0})

while True:
    try:
        a=api.payments.get('data')
        for q in range(len(a)):
            sums=os.listdir('sums')
            comments=os.listdir('comments')
            for i in range(len(comments)):
                if a[q].get('comment') == open('comments/' + comments[i], 'rb').read().decode('utf-8') and a[q].get('total').get('amount') == int(open('sums/' + sums[i], 'rb').read().decode('utf-8')):
                    toPay=int(open('sums/' + sums[i], 'rb').read().decode('utf-8'))
                    tek=int(open('balances/' + sums[i], 'rb').read().decode('utf-8'))
                    open('balances/' + sums[i], 'wb').write(str(toPay+tek).encode('utf-8'))
                    sender(int(sums[i][:-4]), 'пополнение на сумму: ' + str(toPay))
                    os.remove('comments/' + comments[i])
                    os.remove('sums/' + sums[i])
                    print(1)
    except:
        time.sleep(5)
    time.sleep(1)
