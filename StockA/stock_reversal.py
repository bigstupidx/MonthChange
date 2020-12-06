# -*- coding:utf-8 -*-
import numpy as np
import pandas as pd
import os
from datetime import datetime
from datetime import timedelta
import stock_info

'''
月线反转3.0的技术指标公式的几个条件：
1.日线收盘价站上年线
2.一月内曾创50日新高
3.50日的RPS大于85
4.一月内收盘价站上年线的天数大于3，小于30
5.最高价距离120日内的最高价不到10%
'''



def app():
    stocklist = stock_info.get_stock()
    #stocklist = ['603518','000001']
    now = datetime.now()
    startdate = now - timedelta(days=25)
    startdate = startdate.strftime('%Y%m%d')
    #print startdate
    startdate = int(startdate)
    rps_file = '..\\data\\stock_rps.csv'
    rps_file = pd.read_csv(rps_file,converters={u'stockid':str}, usecols=[0,1,3])
    #reversal = pd.DataFrame({'date':[],'stockid':[],'reversal':[],'reversal30':[]})
    reversal = pd.DataFrame()
    for id in stocklist:
        #print 'id: ', id,
        marketvaluefile = '..\\data\\xueqiu\\'+id+'.csv'
        if os.path.isfile(marketvaluefile) == False:
            continue
        #"date","volume","open","high","low","close","ma5","ma10","ma20","ma30","pe","market_capital","chg","percent","turnoverrate","amount","volume_post","amount_post","timestamp"
        try:
            marketvalue = pd.read_csv(marketvaluefile,converters={u'stockid':str}, usecols=[0,3,5])
        except Exception as e:
            continue
        marketvalue['stockid'] = id
        marketvalue = marketvalue.tail(305)
        #marketvalue = marketvalue.rename(columns={'DATE':'date','STOCKID':'stockid','TCLOSE':'close','HIGH':'high'})
        rps = rps_file[rps_file['stockid'].isin([id])].copy()
        #print(rps.dtypes)
        #print(marketvalue.dtypes)
        marketvalue = pd.merge(marketvalue, rps, on=['date','stockid'], how='left')
       #print(marketvalue.head())
        #年线
        marketvalue['close_year'] = marketvalue['close'].rolling(250).mean()
        #print marketvalue.tail()
        #1.日线收盘价站上年线
        marketvalue['condition1'] = marketvalue[['close','close_year']].apply(lambda x: 1 if x[0]>x[1] else 0, axis=1)
        #50日新高
        marketvalue['high50'] = marketvalue['high'].rolling(50).max()
        #2.一月内曾创50日新高
        marketvalue['t1'] = marketvalue[['high','high50']].apply(lambda x: 1 if x[0]>=x[1] else 0, axis=1)
        marketvalue['t2'] = marketvalue['t1'].rolling(30).sum()
        marketvalue['condition2'] = marketvalue['t2'].apply(lambda x: 1 if x>0 else 0)
        marketvalue.drop(['t1','t2'],axis=1,inplace=True)
        #3.50日的RPS大于85
        marketvalue['condition3'] = marketvalue['rps50'].apply(lambda x: 1 if x>=85 else 0)
        
        #4.一月内收盘价站上年线的天数大于3，小于30
        marketvalue['t1'] = marketvalue['condition1'].rolling(30).sum()
        marketvalue['condition4'] = marketvalue['t1'].apply(lambda x: 1 if x>=3 and x<30 else 0)
        marketvalue.drop('t1',axis=1,inplace=True)
        #120新高
        marketvalue['high120'] = marketvalue['high'].rolling(120).max()
        #5.最高价距离120日内的最高价不到10%
        marketvalue['condition5'] = marketvalue[['high','high120']].apply(lambda x: 1 if x[0]/x[1]>0.9 else 0, axis=1)
        #月线反转3
        marketvalue['reversal_t'] = marketvalue[['condition1','condition2','condition3','condition4','condition5']].apply(lambda x: 1 if x[0]==1 and x[1]==1 and x[2]==1 and x[3]==1 and x[4]==1 else 0, axis=1)
        #marketvalue.drop(['condition1','condition2','condition3','condition4','condition5'],axis=1,inplace=True)
        marketvalue['reversal30_t'] = marketvalue['reversal_t'].rolling(30).sum()
        marketvalue['reversal'] = marketvalue[['reversal_t','reversal30_t']].apply(lambda x:1 if x[0]==1 and x[1]==1 else 0, axis=1)
        marketvalue['reversal30'] = marketvalue['reversal'].rolling(30).sum()
        marketvalue.drop(['reversal_t','reversal30_t'],axis=1,inplace=True)
        marketvalue = marketvalue[marketvalue['date']>startdate]
        #marketvalue = marketvalue[['date','stockid','reversal','reversal30']]
        #print(marketvalue.head())
        #pd.DataFrame({'stockid':id,'current':[current[2]],'last':[last[2]]})
        reversal = pd.concat([reversal,marketvalue],ignore_index=True)
        print('stock: ' + id + ' get value succeed')

    reversal['max_date'] = reversal['date'].max()
    reversal['recent'] = reversal[['date','max_date']].apply(lambda x: 1 if x[0]==x[1] else 0, axis=1)
    reversal.drop('max_date',axis=1,inplace=True)
    reversal.to_csv('..\\data\\stock_reversal.csv', index=False)
    #reversal.to_csv('test.csv', index=False)
    print('succeed')
        
if __name__=='__main__':
    app()
