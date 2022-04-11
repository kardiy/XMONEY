gazppoint=0
import requests
def getList(name):
    gazp=open(name+'.txt', 'rb').read().decode('utf-8')
    gazp=gazp.split(',')
    for i in range(len(gazp)):
        gazp[i] = gazp[i].split('_')
        gazp[i][1] = int(gazp[i][1])
        gazp[i][0] = gazp[i][0].replace(' ', '')
    return gazp
ini=1000000
new=requests.get('https://iz.ru/'+str(ini)).content.decode('utf-8').lower()
s=new.find('article:author')
news=new[:s]
while len(new) != 99274:
    if s != -1:
        k=1
        news=news.replace('ё','е')
        gazp=getList('yand')
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
        print('инфополе', gazppoint, ini)
    ini+=1
    new=requests.get('https://iz.ru/'+str(ini)).content.decode('utf-8').lower()
    s=new.find('article:author')
    news=new[:s]
    print(s)
print(ini)
