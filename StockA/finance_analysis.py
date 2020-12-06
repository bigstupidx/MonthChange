# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta
# case 1: 最近3年净利润增长率>=20%， 且最近3年营业收入增长率>=15%，且不是3年净利润增长率连续降低，且最近一个季度净利润增长率>=20%和最近一个季度营业收入增长率>=15%
# case 2: 最近3年净利润增长率连续加速（今年>去年>前年）， 且最近一个季度净利润增长率>=20%和最近一个季度营业收入增长率>=15%
# case 3: 连续6个季度净利润增长率>=50%， 且连续6个季度营业收入增长率>=30%
# case 4: 12个季度(3年)营业收入增长率的标准差<=0.06(代表稳健增长，增长率在正负6%内波动), 且最近一个季度净利润增长率>=20%和最近一个季度营业收入增长率>=15%

# 不存在 - 最近3个季度净利润增长率持续走低
# (存货+应收账款)/流动资产 < 50%
# ROE >= 17%
# 毛利率 >= 25%（非银金融及银行除外）​
# 资产负债率 < 60%（非银金融及银行除外）
# 流动比率 >= 2，速动比率 >= 1（非银金融及银行除外）

def finance_analysis(finance_date=None):
    filename = '..\\data\\stock_equity.csv'
    zcfzb = pd.read_csv(filename,converters={u'stockid':str},usecols=[0,1,3,6,7,8,9])
    if finance_date!=None:
        zcfzb = zcfzb[zcfzb['report_date']<=str(finance_date)].copy()
    zcfzb = zcfzb.groupby(['stockid']).head(1).copy()
    zcfzb.drop(['report_date'],axis=1,inplace=True)

    
    filename = '..\\data\\stock_growth.csv'
    growth = pd.read_csv(filename,converters={u'stockid':str})
    if finance_date!=None:
        growth = growth[growth['report_date']<=str(finance_date)].copy()
    lrb = growth[['stockid','report_date','rolling_net_profits','gross_margin']].groupby(['stockid'],as_index=False,sort=False).head(1).copy()
    #上市3年以上
    growth_yearly = growth.loc[growth['report_date'].str.contains('12-31'),['stockid','net_profit_growth','gross_revenue_growth']].copy()
    #growth_yearly = growth_yearly[['stockid','net_profit_growth','gross_revenue_growth']]
    growth_yearly = growth_yearly.groupby(['stockid']).head(3).copy()
    growth_yearly['growth_yearly_shift1'] = growth_yearly.groupby(['stockid'])['net_profit_growth'].shift(-1)
    growth_yearly['growth_yearly_shift2'] = growth_yearly.groupby(['stockid'])['net_profit_growth'].shift(-2)
    growth_yearly['gross_revenue_growth_shift1'] = growth_yearly.groupby(['stockid'])['gross_revenue_growth'].shift(-1)
    growth_yearly['gross_revenue_growth_shift2'] = growth_yearly.groupby(['stockid'])['gross_revenue_growth'].shift(-2)
    growth_yearly = growth_yearly.rename(columns={'net_profit_growth':'growth_yearly_shift0','gross_revenue_growth':'gross_revenue_growth_shift0'})
    growth_yearly.dropna(how='any',inplace=True)
    #print(growth_yearly.head())
    #上市3年以下
    #growth = growth[['stockid','net_profit_growth']]
    growth_season = growth[['stockid','net_profit_growth','gross_revenue_growth']].groupby(['stockid']).head(6).copy()
    growth_season['growth_season_shift1'] = growth_season.groupby(['stockid'])['net_profit_growth'].shift(-1)
    growth_season['growth_season_shift2'] = growth_season.groupby(['stockid'])['net_profit_growth'].shift(-2)
    growth_season['growth_season_shift3'] = growth_season.groupby(['stockid'])['net_profit_growth'].shift(-3)
    growth_season['growth_season_shift4'] = growth_season.groupby(['stockid'])['net_profit_growth'].shift(-4)
    growth_season['growth_season_shift5'] = growth_season.groupby(['stockid'])['net_profit_growth'].shift(-5)
    growth_season['gross_revenue_season_shift1'] = growth_season.groupby(['stockid'])['gross_revenue_growth'].shift(-1)
    growth_season['gross_revenue_season_shift2'] = growth_season.groupby(['stockid'])['gross_revenue_growth'].shift(-2)
    growth_season['gross_revenue_season_shift3'] = growth_season.groupby(['stockid'])['gross_revenue_growth'].shift(-3)
    growth_season['gross_revenue_season_shift4'] = growth_season.groupby(['stockid'])['gross_revenue_growth'].shift(-4)
    growth_season['gross_revenue_season_shift5'] = growth_season.groupby(['stockid'])['gross_revenue_growth'].shift(-5)
    growth_season = growth_season.rename(columns={'net_profit_growth':'growth_season_shift0','gross_revenue_growth':'gross_revenue_season_shift0'})
    growth_season.dropna(how='any',inplace=True)
    
    growth_std = growth[['stockid','gross_revenue_growth']].groupby(['stockid']).head(12).copy()
    growth_std = growth_std.groupby(['stockid']).std()
    #growth_std['stockid'] = growth_std.index
    growth_std.reset_index(level=0,inplace=True)
    growth_std = growth_std.rename(columns={'gross_revenue_growth':'gross_revenue_growth_std'})


    filename = '..\\data\\stock.csv'
    stock = pd.read_csv(filename,converters={u'stockid':str,u'onboard_date':str})
    if finance_date!=None:
        onboard_date = (datetime.strptime(finance_date,'%Y-%m-%d')-timedelta(365)).strftime('%Y%m%d')
        stock = stock[stock['onboard_date']<onboard_date].copy()
    stock = pd.merge(stock,growth_yearly,on=['stockid'],how='left')
    #print(stock.head())
    stock = pd.merge(stock,growth_season,on=['stockid'],how='left')
    stock = pd.merge(stock,zcfzb,on=['stockid'],how='left')
    stock = pd.merge(stock,lrb,on=['stockid'],how='left')
    stock = pd.merge(stock,growth_std,on=['stockid'],how='left')
    #print(stock.dtypes)
    stock['roe'] = stock['rolling_net_profits']/stock['rolling_equity']
    stock['has_yearly'] = stock[['growth_yearly_shift0','growth_yearly_shift1','growth_yearly_shift2']].apply(lambda x: 0 if (x[0]==np.nan or x[1]==np.nan or x[2]==np.nan) else 1, axis=1)
    
    stock['case'] = stock[['has_yearly',
                           'growth_yearly_shift0','growth_yearly_shift1','growth_yearly_shift2',
                           'gross_revenue_growth_shift0','gross_revenue_growth_shift1','gross_revenue_growth_shift2',
                           'growth_season_shift0','growth_season_shift1','growth_season_shift2','growth_season_shift3','growth_season_shift4','growth_season_shift5',
                           'gross_revenue_season_shift0','gross_revenue_season_shift1','gross_revenue_season_shift2','gross_revenue_season_shift3','gross_revenue_season_shift4','gross_revenue_season_shift5',
                           'gross_revenue_growth_std'
                           ]
                         ].apply(
                         lambda x: 1 if (((x[0]==1) & (x[1]>=0.2) & (x[2]>=0.2) & (x[3]>=0.2) & (x[4]>=0.15) & (x[5]>=0.15) & (x[6]>=0.15) & (x[7]>=0.2) & (x[13]>=0.15)) and not ((x[1]<x[2]) & (x[2]<x[3])))
                              else (2 if ((x[0]==1) & (x[1]>=x[2]) & (x[2]>=x[3]) & (x[1]>=0.2) & (x[7]>=0.2) & (x[13]>=0.15))
                              else (3 if ((x[7]>=0.5) & (x[8]>=0.5) & (x[9]>=0.5) & (x[10]>=0.5) & (x[11]>=0.5) & (x[12]>=0.5)
                                                  & (x[13]>=0.3) & (x[14]>=0.3) & (x[15]>=0.3) & (x[16]>=0.3) & (x[17]>=0.3) & (x[18]>=0.3))
                              else (4 if ((x[19]<=0.06) & (x[7]>=0.2) & (x[13]>=0.15))
                              else 0))),
                     axis=1
                         )
    stock = stock[stock['case']>0].copy()
    stock['growth_issue'] = stock[['growth_season_shift0','growth_season_shift1','growth_season_shift2']].apply(lambda x: 1 if (x[0]<x[1]) & (x[1]<x[2]) else 0,axis=1) #最近3个季度净利润增长率持续走低
    stock = stock[stock['growth_issue']==0].copy() 
    stock = stock[stock['inv_ar_ratio']<0.5].copy() #(存货+应收账款)/流动资产 < 50%
    stock = stock[stock['roe']>=0.17].copy() 
    stock = stock[(stock['gross_margin']>=0.25)|(stock['industry'].isin(['非银金融','银行']))].copy()  #毛利率
    stock = stock[((stock['current_ratio']>=2)&(stock['quick_ratio']>=1))|(stock['industry'].isin(['非银金融','银行']))].copy()  #流动比率，速动比率
    stock = stock[(stock['asset_liability_ratio']<0.6)|(stock['industry'].isin(['非银金融','银行']))].copy()   #资产负债率

    
    stock = stock[['case','stockid','name','onboard_date','type','industry','report_date','roe','gross_margin','growth_yearly_shift0','growth_yearly_shift1','growth_yearly_shift2','growth_season_shift0','growth_season_shift1','asset_liability_ratio','current_ratio','quick_ratio','rolling_net_profits','rolling_equity','gross_revenue_growth_std']].copy()
    return stock

def app():
    finance_stock = finance_analysis()
    finance_stock.to_csv('..\\data\\finance_analysis.csv',index=False)
    finance_stock[['stockid']].to_csv('..\\data\\selected_stockid.txt',index=False,header=False)
    
if __name__ == '__main__':
    app()