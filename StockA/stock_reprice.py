# -*- coding: utf-8 -*-




import sys#,os
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta
#from urllib import request
import json
import stock_info
import asyncio, aiohttp
import time
    
def app(stockid=None,startdate=None,enddate=None):
    if len(sys.argv) >= 2:
        stocklist = [sys.argv[1]]
    elif stockid != None:
        if isinstance(stockid,list):
            stocklist = stockid
        else:
            stocklist = [stockid]
    else:
        stocklist = stock_info.get_stock(allvalues=True)
    #stocklist = stocklist[:2]   
    
    
    
    if startdate != None and enddate != None:
        startdate = str(int(datetime.strptime(startdate,'%Y%m%d').timestamp()*1000))
        enddate = str(int(datetime.strptime(enddate,'%Y%m%d').timestamp()*1000))
    else:
        today = datetime.today()
        #print(today)
        startdate = str(int((today-timedelta(days=730)).timestamp()*1000))
        enddate = str(int(today.timestamp()*1000))
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_reprice(stocklist,startdate,enddate))
    print('All completed!')
    
async def get_reprice(stocklist,startdate,enddate):
    Session_Cookie = "device_id=e9672e27eb35f961597bd83b0458b8e8;"
    Session_headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763',
        'Cookie': Session_Cookie,
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN',
        'Host': 'xueqiu.com'
    }
    
    pool = 500
    sem = asyncio.Semaphore(pool)
    async with aiohttp.ClientSession() as session: #给所有的请求，创建同一个session
        Cookie = 'xq_a_token=d831cd39b53563679545656fba1f4efd8e48faa0;'
        resp = await session.get('https://xueqiu.com',headers=Session_headers)
        if resp.status != 200:
            print('Can NOT connect to xueqiu.com!')
            return
        resp_headers = resp.headers
        for k, v in resp_headers.items():
            if k == 'Set-Cookie' and v.startswith('xq_a_token'):
                Cookie = v[:v.find(';')+1]
        #print(Cookie)
        headers = {
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763',
            'Cookie': Cookie,
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN',
            'Host': 'stock.xueqiu.com'
        }
        tasks = [control_sem(sem, stockid, session,startdate,enddate,headers) for stockid in stocklist]
        await asyncio.wait(tasks)


async def control_sem(sem, stockid, session,startdate,enddate,headers=None):#限制信号量
    async with sem:
        await get_content(session,stockid,startdate,enddate,headers=headers)


async def get_content(session,stockid,startdate,enddate,headers=None):
    filename = '..\\data\\xueqiu\\'+stockid+'.csv'
    #https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol=SZ000568&begin=1566478112274&period=day&type=before&count=-142&indicator=kline,pe,market_capital,ma
    #https://xueqiu.com/stock/forchartk/stocklist.json?symbol=SH600756&period=1day&type=before&begin=1504103095436&end=1567175095436&_=1567175095436
    if stockid[:2] == 'SH' or stockid[:2] == 'SZ': #指数
        url = 'https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol='+stockid+'&period=day&type=before&begin='+startdate+'&end='+enddate+'&indicator=kline,pe,market_capital,ma'
    elif stockid[:1] == '6':
        url = 'https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol=SH'+stockid+'&period=day&type=before&begin='+startdate+'&end='+enddate+'&indicator=kline,pe,market_capital,ma'
    else:
        url = 'https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol=SZ'+stockid+'&period=day&type=before&begin='+startdate+'&end='+enddate+'&indicator=kline,pe,market_capital,ma'
    #print(url)
    async with session.get(url,headers=headers,allow_redirects=False) as resp:
        data = await resp.json()
        #data = json.loads(data)
        #print(data)
        data = data['data']
        df = pd.DataFrame(data['item'])
        if df.empty:
            return
        df.columns = data['column']
        #"time":"Wed Nov 09 00:00:00 +0800 2016"
        #df['date']=df['time'].apply(lambda x: datetime.strptime(x,'%a %b %d %H:%M:%S %z %Y').strftime('%Y%m%d'))
        df['date']=df['timestamp'].apply(lambda x: datetime.fromtimestamp(x/1000).strftime('%Y%m%d'))
        df = df[["date","volume","open","high","low","close","ma5","ma10","ma20","ma30","pe","market_capital","chg","percent","turnoverrate","amount","volume_post","amount_post","timestamp"]]
        df.to_csv(filename,index=False)
    print('get stock '+stockid)
    #asyncio.sleep(0.1)


if __name__ == '__main__':
    app()