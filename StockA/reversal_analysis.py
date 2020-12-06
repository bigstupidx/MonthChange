# -*- coding: utf-8 -*-

import pandas as pd
#import sendmail

def app():
    filename = '..\\data\\stock_reversal.csv'
    df = pd.read_csv(filename,converters={u'stockid':str})
    rlt = df[(df['reversal30']==1) & (df['reversal']==1)]
    
    filename = '..\\data\\stock_growth.csv'
    data = pd.read_csv(filename,converters={u'stockid':str},usecols=[0,1,3])
    growth = data.groupby(['stockid']).head(3).copy()
    growth['shift1'] = growth.groupby(['stockid'])['net_profit_growth'].shift(-1)
    growth['shift2'] = growth.groupby(['stockid'])['net_profit_growth'].shift(-2)
    growth.dropna(how='any',inplace=True)
    growth['growth_3season'] = growth[['net_profit_growth','shift1','shift2']].apply(lambda x:1 if x[0]>=0.2 and (x[0]>=x[1] or x[1]>=x[2]) else 0,axis=1)
    #growth = growth[(growth['growth_3season']==1)&(growth['net_profit_growth']>=0.2)]
    rlt = pd.merge(rlt,growth,on=['stockid'],how='inner')

    filename = '..\\data\\stock_jjcg.csv'
    jjcg = pd.read_csv(filename,converters={u'stockid':str},usecols=[2,8,16])
    jjcg = jjcg[(jjcg['SCSTC27']>=0.03)&(jjcg['EXCHANGE'].isin(['CNSESZ','CNSESH']))]
    rlt = pd.merge(rlt,jjcg,on=['stockid'],how='inner')


    filename = '..\\data\\stock.csv'
    stock = pd.read_csv(filename,converters={u'stockid':str,u'onboard_date':str},usecols=[0,1,2,3,4])
    #stock = stock[(stock[u'onboard_date']>=20150101)&(stock[u'onboard_date']<=20180314)]#&(stock[u'type'].isin(['沪市A股','深市A股','中小板']))]
    rlt = pd.merge(rlt,stock,on=['stockid'],how='inner')
    rlt = rlt.sort_values(by=['industry','date'])
    
    rlt = rlt[['date','stockid','name','industry','onboard_date','type','report_date','net_profit_growth','shift1','shift2','growth_3season','EXCHANGE','SCSTC27','close','high','rps50','close_year','high50','high120','reversal','reversal30','recent']]

    rlt.to_csv('..\\data\\reversal_analysis.csv',index=False)
    
    #sendmail.sendmail()
    
if __name__ == '__main__':
    app()
