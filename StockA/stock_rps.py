# -*- coding:utf-8 -*-
import numpy as np
import pandas as pd
import os
from datetime import datetime
from datetime import timedelta
import stock_info

'''
RPS
'''


def getPercentile(data,percent,percentile):
    rlt = np.nan
    for i in range(len(percent)):
        if percent[i] == 1:
            rlt = 1 
            break
        elif data>=percentile[i]:
            rlt = percent[i]
            break
    return rlt

def app():
    stocklist = stock_info.get_stock()
    #stocklist = stocklist[:2]
    now = datetime.now()
    startdate = now - timedelta(days=50)
    startdate = startdate.strftime('%Y%m%d')
    #print startdate
    startdate = int(startdate)
    #priceReletive = pd.DataFrame({'date':[],'stockid':[],'close':[],'vol':[],'close250':[],'close50':[],'vol50':[]})
    priceReletive = pd.DataFrame()
    for id in stocklist:
        #print 'id: ', id,
        marketvaluefile = '..\\data\\xueqiu\\'+id+'.csv'
        if os.path.isfile(marketvaluefile) == False:
            continue
        #"date","volume","open","high","low","close","ma5","ma10","ma20","ma30","pe","market_capital","chg","percent","turnoverrate","amount","volume_post","amount_post","timestamp"
        try:
            marketvalue = pd.read_csv(marketvaluefile, usecols=[0,1,3,4,5])
        except Exception as e:
            continue
        marketvalue = marketvalue.tail(305)
        marketvalue = marketvalue.rename(columns={'volume':'vol'})
        marketvalue['stockid'] = id
        #marketvalue['date'] = marketvalue['time'].apply(lambda x: int(datetime.strptime(x,'%a %b %d %H:%M:%S %z %Y').strftime('%Y%m%d')))
        marketvalue['close250'] = marketvalue['close'].shift(250)
        marketvalue['close50'] = marketvalue['close'].shift(50)
        marketvalue['high1'] = marketvalue['high'].shift(1)
        marketvalue['vol50'] = marketvalue['vol'].rolling(50).mean()
        
        marketvalue = marketvalue[marketvalue['date'] > startdate]
        priceReletive = pd.concat([priceReletive,marketvalue],ignore_index=True)
        print('stock: ' + id + ' get value succeed')
    
    #print priceReletive
    priceReletive['max_date'] = priceReletive['date'].max()
    priceReletive['recent'] = priceReletive[['date','max_date']].apply(lambda x: 1 if x[0]==x[1] else 0, axis=1)
    priceReletive.drop('max_date',axis=1,inplace=True)
    priceReletive['date'] = priceReletive['date'].apply(lambda x: str(x))
    priceReletive['variance250'] = (priceReletive['close']-priceReletive['close250'])/priceReletive['close250']
    priceReletive['variance50'] = (priceReletive['close']-priceReletive['close50'])/priceReletive['close50']
    priceReletive['var_vol'] = (priceReletive['vol']-priceReletive['vol50'])/priceReletive['vol50']
    priceReletive['var_vol_shift1'] = priceReletive['var_vol'].shift(1)
    priceReletive['var_vol_shift2'] = priceReletive['var_vol'].shift(2)
    priceReletive['var_vol_shift3'] = priceReletive['var_vol'].shift(3)
    priceReletive['var_vol_shift4'] = priceReletive['var_vol'].shift(4)
    priceReletive['var_vol_shift5'] = priceReletive['var_vol'].shift(5)
    priceReletive['vol_indicator'] = priceReletive[['var_vol','var_vol_shift1','var_vol_shift2','var_vol_shift3','var_vol_shift4','var_vol_shift5']].apply(lambda x: 1 if x[0]>=30 and x[1]<30 and x[2]<30 and x[3]<30 and x[4]<30 and x[5]<30  else 1, axis=1)
    priceReletive['up_indicator'] = priceReletive[['high1','low']].apply(lambda x: 1 if x[0]<x[1] else 1, axis=1)
    #print priceReletive
    date_list = list(set(priceReletive['date'].values))
    date_list.sort()
    #rps = pd.DataFrame({'date':[],'stockid':[],'rps250':[],'rps50':[],'rps_vol50':[],'recent':[]})
    rps = pd.DataFrame()
    
    p = list(range(99, 0, -1))
    #print(date_list)
    for d in date_list:
        rps_t = priceReletive[priceReletive['date']==d].copy()
        pt = np.nanpercentile(rps_t['variance250'], p)
        #print(pt)
        rps_t['rps250']=rps_t['variance250'].apply(getPercentile,percent=p,percentile=pt)
        pt = np.nanpercentile(rps_t['variance50'], p)
        rps_t['rps50']=rps_t['variance50'].apply(getPercentile,percent=p,percentile=pt)
        rps_t = rps_t[['date','stockid','rps250','rps50','var_vol','var_vol_shift1','var_vol_shift2','var_vol_shift3','var_vol_shift4','var_vol_shift5','vol_indicator','up_indicator','recent']]
        rps = pd.concat([rps,rps_t],ignore_index=True)
    
    #print(rps.head())
    rps.to_csv('..\\data\\stock_rps.csv', index=False)
    print('succeed')
        
if __name__=='__main__':
    app()
