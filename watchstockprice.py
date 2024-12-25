import requests
import sqlite3
from datetime import datetime
from datetime import timezone
import os

fiat="EUR"
os.system(". ./env.sh")
key=os.environ['COINBASE_KEY']
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

parameters = {
  'start':'1',
  'limit':'5000',
  'convert':fiat
}

headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': key
}

def getCurrenciesLatest():
    response = requests.request("GET", url, headers=headers, params=parameters)
    #print(response.text)
    return response.json()

def getRate(rdict, currency):
    for cur in rdict['data']:
        if cur['symbol']==currency:
            return cur['quote'][fiat]['price']

def getRateRangeToday(cFrom, cTo):
    cur=conn.cursor()
    cur.execute("select min(low), max(high) from rates where fcur=? and tcur=? and date = date('now')", (cFrom, cTo))
    (min, max)=cur.fetchone()
    conn.commit()
    return (min, max)

def registerRate(fcur, tcur, price):
    (min, max)=getRateRangeToday(fcur, tcur)
    if min:
        if price<min:
            updateMinPrice(fcur, tcur, price)
        elif price>max:
            updateMaxPrice(fcur, tcur, price)
    else:
        insRates(fcur, tcur, price)

def insRates(fcur, tcur, price):
    cur=conn.cursor()
    cur.execute("insert into rates (date, fcur, tcur, open, low, high) values (date('now'), ?, ?, ?, ?, ?)", (fcur, tcur, price, price, price))
    conn.commit()

def insRatesTouple(fcur, tcur, tpl):
    #print(f"insRatesTouple({fcur}, {tcur}, {tpl})")
    cur=conn.cursor()
    cur.execute("insert into rates_backup select * from rates where fcur=? and tcur=? and date=?", (fcur, tcur) + (tpl[0],))
    conn.commit()
    cur=conn.cursor()
    cur.execute("delete from rates where fcur=? and tcur=? and date=?", (fcur, tcur) + (tpl[0],))
    conn.commit()
    cur=conn.cursor()
    cur.execute("insert into rates (fcur, tcur, date, open, high, low, close, adjclose, volume) values (?, ?, ?, ?, ?, ?, ?, ?, ?)", (fcur, tcur) + tpl)
    conn.commit()

def updateMinPrice(fcur, tcur, price):
    cur=conn.cursor()
    cur.execute("update rates set low=? where date=date('now') and fcur=? and tcur=?", (price, fcur, tcur))
    conn.commit()

def updateMaxPrice(fcur, tcur, price):
    cur=conn.cursor()
    cur.execute("update rates set high=? where date=date('now') and fcur=? and tcur=?", (price, fcur, tcur))
    conn.commit()

def getRateRange(cFrom, cTo, days):
    cur=conn.cursor()
    cur.execute("select min(low), max(high) from rates where fcur=? and tcur=? and date > date('now', ?)", (cFrom, cTo, "-"+str(days)+" day"))
    (min, max)=cur.fetchone()
    conn.commit()
    return (min, max)

def cmpRateRange(cFrom, cTo, days, price):
    (min, max)=getRateRange(cFrom, cTo, days)
    if min and price < min:
        return -1
    elif min and price > max:
        return 1
    return 0

def inRates(fcur, tcur, period):
    #print(f"inRates({fcur}, {tcur}, {period})")
    cur=conn.cursor()
    cur.execute("select volume from rates where fcur=? and tcur=? and date = date(?, 'unixepoch')", (fcur, tcur, period))
    #print("select volume from rates where fcur='%s' and tcur='%s' and date = date('%s', 'unixepoch')" % (fcur, tcur, period))
    try:
        volume=cur.fetchone()[0]
    except:
        return False
    conn.commit()
    if volume:
        return True
    else:
        return False

def checkRatesDBY(fcur, tcur):
    #print(f"checkRatesDBY({fcur}, {tcur})")
    now = datetime.utcnow()
    daystart = datetime(now.year,now.month,now.day, tzinfo=timezone.utc)
    period1=int(daystart.timestamp())-2*24*3600
    period2=period1+24*3600-1
    if not inRates(fcur, tcur, period1):
        updateRates(fcur, tcur, period1, period2)

def updateRates(fcur, tcur, period1, period2):
    #print(f"updateRates({fcur}, {tcur}, {period1}, {period2})")
    yahoourl="https://query1.finance.yahoo.com/v7/finance/download/"
    url=yahoourl + tcur + "-" + fcur
    params = {
        "period1": period1,
        "period2": period2,
        "interval": "1d",
        "events": "history",
        "includeAdjustedClose": "true"
    }
    headers = {
        'User-agent': 'Mozilla/5.0'
    }
    r=requests.get(url, params=params, headers=headers)
    lines=r.text.splitlines()
    nrlines=len(lines)
    for j in range(1, nrlines):
        line=lines[j]
        la=line.split(',')
        tpl=(la[0],)
        for i in range(1, len(la)-1):
            tpl=tpl+(float(la[i]), )
        tpl=tpl+(int(la[len(la)-1]), )
        insRatesTouple(fcur, tcur, tpl)

#curl -v "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage?chat_id=$TELEGRAM_CHANNEL_ID&text=$omsg"
def sendTelegramMessage(msg):
    TELEGRAM_TOKEN=os.environ['TELEGRAM_TOKEN']
    TELEGRAM_CHANNEL_ID=os.environ['TELEGRAM_CHANNEL_ID']
    teleurl="https://api.telegram.org/bot"+TELEGRAM_TOKEN+"/sendMessage"
    teleparam = {
        'chat_id': TELEGRAM_CHANNEL_ID,
        'text': msg
    }
    response = requests.request("GET", teleurl, params=teleparam)

print(f"Program start at {datetime.now()}")
conn=sqlite3.connect("currencies.db")
rdict=getCurrenciesLatest()
for cur in ['ETH', 'BTC', 'BCH', 'BTG', 'BSV', 'LTC', 'XRP', 'DOGE']:
    price = getRate(rdict, cur)
    print(fiat+"-"+cur+"="+str(price))
    xrange=cmpRateRange(fiat, cur, 7, price)
    #print("Range: "+str(xrange))
    if xrange==-1:
        msg="Price for "+cur+" is below 7 day range: "+str(price)
        sendTelegramMessage(msg)
    if xrange==1:
        msg="Price for "+cur+" is above 7 day range: "+str(price)
        sendTelegramMessage(msg)
    registerRate(fiat, cur, price)
    checkRatesDBY(fiat, cur)
conn.close()
