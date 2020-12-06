# -*- coding: utf-8 -*-

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime
#from datetime import timedelta
from urllib import request
import stock_info
import json
    
def app():
    print('starting...')
    args = sys.argv
    if(len(args)>1):
        arg = args[1]
        if isinstance(arg,str) and len(arg)==6:
            stocklist = [arg]
        elif isinstance(arg,list):
            stocklist = arg
        else:
            print('no valid stockid provided! str or list is needed')
            return
    else:
        allstocklist = stock_info.get_stock(allvalues=True)
        stock_cnt = len(allstocklist) + 50
        now = datetime.now() 
        today = int(now.strftime('%Y%m%d'))
        yyplrq_file = '..\\data\\stock_yyplrq.csv'
        #NO,COMPANYCODE,DECLAREDATE,ACNAME,MEMORD1,publishdate,EXCHANGE,stockid,MEMORD6,SNAME,CODE,NAME
        if os.path.isfile(yyplrq_file):
            publishdate = pd.read_csv(yyplrq_file,usecols=[5,7],converters={'stockid':str})
        else:
            publishdate = pd.DataFrame()
        if(publishdate.empty):
            new_yyplrq = get_yyplrq(stock_cnt)
            if(new_yyplrq.empty):
                print('no new report published!')
                return
            else:
                #allstocklist = stock_info.get_stock(allvalues=True)
                yyplrq = new_yyplrq
                yyplrq['publishdate'] = yyplrq['publishdate'].apply(int)
                yyplrq = yyplrq[yyplrq['publishdate']>today]
                yyplrq = list(yyplrq['stockid'])
                stocklist = list(set(allstocklist).difference(set(yyplrq)))
        else:        
            publishdate = publishdate[publishdate['publishdate']<=today]
            stocklist = list(publishdate['stockid'])
            if(len(stocklist)==0):
                print('no new report published!')
                return
            else:
                #更新预约披露日期
                new_yyplrq=get_yyplrq(stock_cnt)
    
    rlt = None
    for stockid in stocklist:
        rlt = get_finance(stockid)
        if(rlt):
            break        
    
    if rlt == None:
        get_stock_growth(stocklist)
        get_stock_equity(stocklist)
        #更新预约披露日期文件
        filename = '..\\data\\stock_yyplrq.csv'
        new_yyplrq.to_csv(filename,index=False)
        print('stock_yyplrq.csv is updated!')
    
    print('ending...')

def get_yyplrq(count):
    filename = '..\\data\\stock_yyplrq.csv'
    count = str(count)
    url = 'http://quotes.money.163.com/hs/marketdata/service/yyplrq.php?count='+count+'&sort=PUBLISHDATE&order=asc'
    with request.urlopen(url) as f:
        data = json.load(f)
    data = data['list']
    fc = pd.DataFrame(data) 
    if fc.empty:
        fc = pd.DataFrame(columns=['ACNAME','CODE','COMPANYCODE','DECLAREDATE','EXCHANGE','MEMORD1','MEMORD6','NAME','NO','publishdate','SNAME','stockid']) 
    else:
        fc = fc.rename(columns={'SYMBOL':'stockid','PUBLISHDATE':'publishdate'})
        fc['publishdate'] = fc['publishdate'].str.replace('-','')
        fc.drop_duplicates('CODE',inplace=True)
    print('get yyplrq list success')
    return fc
    
def get_stock_growth(stocklist=None): 
    if stocklist == None:
        print('no stockid provided!')
        return
    if isinstance(stocklist , list)==False:
        print('no stocklist provided!')
        return
    rlts = pd.DataFrame()
    for stockid in stocklist:
            
        print('get_stock_growth ...'+stockid+'...',end='')
        filename_source = '..\\data\\finance\\lrb\\lrb_'+stockid+'.csv'
        filename_target = '..\\data\\stock_growth.csv'
        if os.path.isfile(filename_source)==False:
            print('failed, no source file exists!')
            return
        fc = pd.read_csv(filename_source,index_col=u'报告日期')
        #fc = fc[fc[u'报告日期'].isin([u'营业总收入(万元)',u'营业收入(万元)',u'净利润(万元)'])]
        fc = fc.loc[[u'营业总收入(万元)',u'营业收入(万元)',u'营业成本(万元)',u'净利润(万元)',u'归属于母公司所有者的净利润(万元)'],:]
        fc = fc.T
        fc = fc[:-1]  #csv最后一列是空的，转换之后就是最后一行，需要去除
        fc = fc.rename(columns={u'基本每股收益':'eps',
                                u'归属于母公司所有者的净利润(万元)':'own_net_profits',
                                u'净利润(万元)':'net_profits',
                                u'营业总收入(万元)':'gross_revenue',
                                u'营业总成本(万元)':'business_cost',
                                u'营业收入(万元)':'operating_income',
                                u'营业成本(万元)':'operating_cost'
                                })
        fc['report_date'] = fc.index    
        fc['report_date_ly_end'] = fc['report_date'].apply(lambda x:str(int(x[:4])-1)+'-12-31')
        
        ly = fc[['report_date','net_profits','gross_revenue','own_net_profits']].copy()
        ly = ly.rename(columns={u'net_profits':'net_profits_ly','gross_revenue':'gross_revenue_ly','own_net_profits':'own_net_profits_ly'}) 
        ly['report_date'] = ly['report_date'].apply(lambda x: str(int(x[:4])+1)+x[4:])
        fc = fc.merge(ly,on=['report_date'],how='left')
        
        lrb_ly_end = fc[['report_date',u'own_net_profits']].copy()
        lrb_ly_end = lrb_ly_end.rename(columns={'report_date':'report_date_ly_end',u'own_net_profits':'own_net_profits_ly_end'})        
        fc = pd.merge(fc,lrb_ly_end,how='left',on='report_date_ly_end')
        
        fc['gross_revenue_growth'] = fc[[u'gross_revenue',u'gross_revenue_ly']].apply(lambda x:np.nan if x[1]==np.nan or x[1]==0 else (x[0]-x[1])/abs(x[1]),axis=1)
        fc['net_profit_growth']    = fc[[u'net_profits',u'net_profits_ly'    ]].apply(lambda x:np.nan if x[1]==np.nan or x[1]==0 else (x[0]-x[1])/abs(x[1]),axis=1)
        fc['rolling_net_profits'] = fc[['report_date',u'own_net_profits',u'own_net_profits_ly','own_net_profits_ly_end']].apply(lambda x: x[1] if x[0][-5:]=='12-31' 
                                                                                                                                      else (np.nan if (x[2]==np.nan or x[3]==np.nan) 
                                                                                                                                                   else x[1]+(x[3]-x[2]))
                                                                                                                       ,axis=1)
        #毛利率
        fc['gross_margin'] = fc[['operating_income','operating_cost']].apply(lambda x:np.nan if x[0]==np.nan or x[0]==0 else (x[0]-x[1])/x[0],axis=1)
        fc['stockid'] = stockid
        fc = fc[['stockid','report_date','gross_revenue_growth','net_profit_growth','rolling_net_profits','gross_margin']]
        
        rlts = pd.concat([rlts,fc],ignore_index=True,sort=False)
        print('succeed!')
        
    if rlts.empty:
        return
    elif os.path.isfile(filename_target):
        existing_content = pd.read_csv(filename_target,converters={'stockid':str})
        existing_content = existing_content[~(existing_content['stockid'].isin(stocklist))]
        rlts = pd.concat([rlts,existing_content],ignore_index=True,sort=False)
        rlts.to_csv(filename_target,index=False)
    else:
        rlts.to_csv(filename_target,index=False)

def get_stock_equity(stocklist=None): 
    if stocklist == None:
        print('no stockid provided!')
        return
    if isinstance(stocklist , list)==False:
        print('no stocklist provided!')
        return
    rlts = pd.DataFrame()
    for stockid in stocklist:
        print('get_stock_equity ...'+stockid+'...',end='')
        filename_source = '..\\data\\finance\\zcfzb\\zcfzb_'+stockid+'.csv'
        filename_target = '..\\data\\stock_equity.csv'
        if os.path.isfile(filename_source)==False:
            print('failed, no source file exists!')
            return
        fc = pd.read_csv(filename_source,index_col=u'报告日期')
        fc = fc.loc[[u'资产总计(万元)',u'负债合计(万元)',u'归属于母公司股东权益合计(万元)',u'流动资产合计(万元)',u'流动负债合计(万元)',u'存货(万元)',u'应收账款(万元)'],:]
        fc = fc.T
        fc = fc[:-1]  #csv最后一列是空的，转换之后就是最后一行，需要去除
        fc['report_date'] = fc.index
        fc = fc.rename(columns={u'资产总计(万元)':'total_assets',
                                u'负债合计(万元)':'total_liabilities',
                                u'归属于母公司股东权益合计(万元)':'equity',
                                u'流动资产合计(万元)':'current_assets',
                                u'流动负债合计(万元)':'current_liabilities',
                                u'存货(万元)':'inventories',
                                u'应收账款(万元)':'account_receivable'
                                }) 
            
        ly = fc[['report_date',u'equity','total_assets']].copy()
        ly = ly.rename(columns={u'equity':'equity_ly','total_assets':'total_assets_ly'}) 
        ly['report_date'] = ly['report_date'].apply(lambda x: str(int(x[:4])+1)+x[4:])
        fc = fc.merge(ly,on=['report_date'],how='left')
        fc['report_date_ly_end'] = fc['report_date'].apply(lambda x:str(int(x[:4])-1)+'-12-31')
        
        ly_end = fc[['report_date',u'equity','total_assets']].copy()
        ly_end = ly_end.rename(columns={'report_date':'report_date_beginning',u'equity':u'equity_beginning','total_assets':'total_assets_beginning'})
        fc['report_date_beginning'] = fc['report_date'].apply(lambda x: str(int(x[:4])-1)+'-12-31')
        fc = fc.merge(ly_end,on=['report_date_beginning'],how='left')
        
        #u'加权平均净资产'
        fc['average_equity'] = fc[[u'equity',u'equity_beginning']].apply(lambda x: np.nan if x[1]==np.nan or x[1]==0 else (x[0]+x[1])/2,axis=1)
        #u'滚动加权平均净资产'
        fc['rolling_equity'] = fc[[u'equity',u'equity_ly']].apply(lambda x: np.nan if x[1]==np.nan or x[1]==0 else (x[0]+x[1])/2,axis=1)
        #u'加权平均总资产'
        fc['average_asset'] = fc[[u'total_assets',u'total_assets_beginning']].apply(lambda x: np.nan if x[1]==np.nan or x[1]==0 else (x[0]+x[1])/2,axis=1)
        #u'滚动加权平均总资产'
        fc['rolling_asset'] = fc[[u'total_assets',u'total_assets_ly']].apply(lambda x: np.nan if x[1]==np.nan or x[1]==0 else (x[0]+x[1])/2,axis=1)
        #资产负债率
        fc['asset_liability_ratio'] = fc[['total_assets','total_liabilities']].apply(lambda x:np.nan if x[0]==np.nan or x[0]==0 else x[1]/x[0],axis=1)
        #流动比率
        fc['current_ratio'] = fc[['current_liabilities','current_assets']].apply(lambda x:np.nan if x[0]==np.nan or x[0]==0 else x[1]/x[0],axis=1)
        #速动比率
        fc['quick_ratio'] = fc[['current_liabilities','current_assets','inventories']].apply(lambda x:np.nan if x[0]==np.nan or x[0]==0 else (x[1]-x[2])/x[0],axis=1)
        #(存货+应收账款)/流动资产
        fc['inv_ar_ratio'] = fc[['current_assets','inventories','account_receivable']].apply(lambda x:np.nan if x[0]==np.nan or x[0]==0 else (x[1]+x[2])/x[0],axis=1)
        
        fc['stockid'] = stockid
        fc = fc[['stockid','report_date','average_equity','rolling_equity','average_asset','rolling_asset','asset_liability_ratio','current_ratio','quick_ratio','inv_ar_ratio']]
        rlts = pd.concat([rlts,fc],ignore_index=True,sort=False)
        print('succeed!')
    
    if rlts.empty:
        return
    elif os.path.isfile(filename_target):
        existing_content = pd.read_csv(filename_target,converters={'stockid':str})
        existing_content = existing_content[~(existing_content['stockid'].isin(stocklist))]
        rlts = pd.concat([rlts,existing_content],ignore_index=True,sort=False)
        rlts.to_csv(filename_target,index=False)
    else:
        rlts.to_csv(filename_target,index=False)
        
    
def get_finance(stockid=None):  
    if stockid == None:
        print('no stockid provided!')
        return
    
    #http://quotes.money.163.com/service/xjllb_601398.html
    print(stockid)
    items = ['zcfzb','lrb','xjllb']
    for i in items:
        url = 'http://quotes.money.163.com/service/'+i+'_'+stockid+'.html'
        filename = '..\\data\\finance\\'+i+'\\'+i+'_'+stockid+'.csv'
        try:
            with request.urlopen(url) as f:
                data = f.read().decode("gbk").encode("utf-8")#.decode("utf-8")
                #print(data[:1000])
                data = data.replace(b'--',b'')
                data = data.replace(b' ',b'')
            with open(filename, 'wb') as file:
                file.write(data)            
            print('        '+i+' ... succeed')
        except Exception as e:
            print('        '+i+' ... failed', e)
            return stockid


if __name__ == '__main__':
    app()