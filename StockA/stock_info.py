# -*- coding: utf-8 -*-

##import os
import numpy as np
import pandas as pd
#import tushare as ts
from datetime import datetime
from datetime import timedelta
from urllib import request
import json,os
import stock_finance
    
def app():
    print('starting...')
    filename = '..\\data\\stock.csv'
    
    #fc = ts.get_stock_basics()
    #fc.to_csv(filename)
    #print('completed!')
    
    stocklist_sh = getstockid_sh()
    stocklist_sz = getstockid_sz()
    frames = [stocklist_sh,stocklist_sz]
    df = pd.concat(frames,ignore_index=True,sort=False)
    df = df.rename(columns = {u'公司代码':'stockid',u'公司简称':'name',u'上市日期':'onboard_date'})
    df[u'onboard_date'] = df[u'onboard_date'].apply(lambda x:x.replace('-',''))
    df[u'type'] = df[u'stockid'].apply(getstocktype)
    
    #sina财经对沪深股票进行的行业分类
    industry = get_industry()
    df = pd.merge(df,industry,on='stockid',how='left')
    df.to_csv(filename, encoding='utf-8', index=False)
    #filename = 'data\\stock_industry.csv'
    #industry = ts.get_industry_classified()
    #industry.to_csv(filename,index=False)
    #print('get stock industry list success')
    #sina财经提供的概念分类
    #filename = 'data\\stock_concept.csv'
    #concept = ts.get_concept_classified()
    #concept.to_csv(filename,index=False)
    #print('get stock concept list success')
    
    #检查是否新股票，如果是新的，需要下载财务报表
    stocklist = list(df['stockid'])
    new_stock = []
    for stockid in stocklist:
        filename_source = '..\\data\\finance\\zcfzb\\zcfzb_'+stockid+'.csv'
        if os.path.isfile(filename_source)==False:
            new_stock.append(stockid)
    if new_stock:
        for stockid in new_stock:
            stock_finance.get_finance(stockid)        
        stock_finance.get_stock_growth(new_stock)
        stock_finance.get_stock_equity(new_stock)
    
    

def getstocktype(item):
    type = ''
    if item[0:2] == '60':
        type = u'沪市A股'
    elif item[0:3] == '000' or item[0:3] == '001':
        type = u'深市A股'
    elif item[0:3] == '002':
        type = u'中小板'
    elif item[0:3] == '300':
        type = u'创业板'
    return type
#'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763'
#'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'
def getstockid_sh():
    Cookie = "PHPStat_First_Time_10000011=1480161374807; PHPStat_Cookie_Global_User_Id=_ck16112619561419557385655696251; PHPStat_Return_Time_10000011=1480161374807; PHPStat_Msrc_10000011=%3A%3Amarket_type_free_search%3A%3A%3A%3Asogou%3A%3A%25e4%25b8%258a%25e8%25af%2581%25e4%25ba%25a4%25e6%2598%2593%25e6%2589%2580%3A%3A%3A%3A%3A%3Awww.sogou.com%3A%3A%3A%3Apmf_from_free_search; PHPStat_Msrc_Type_10000011=pmf_from_free_search; PHPStat_Main_Website_10000011=_ck16112619561419557385655696251%7C10000011%7C%7C%7C; _trs_uv=1fx0_532_ivz5v6iw; yfx_c_g_u_id_10000042=_ck17031216131110943557825628978; VISITED_COMPANY_CODE=%5B%22601288%22%5D; VISITED_STOCK_CODE=%5B%22601288%22%5D; seecookie=%5B601288%5D%3A%u519C%u4E1A%u94F6%u884C; yfx_mr_10000042=%3A%3Amarket_type_free_search%3A%3A%3A%3Abaidu%3A%3A%3A%3A%3A%3A%3A%3Awww.baidu.com%3A%3A%3A%3Apmf_from_free_search; yfx_mr_f_10000042=%3A%3Amarket_type_free_search%3A%3A%3A%3Abaidu%3A%3A%3A%3A%3A%3A%3A%3Awww.baidu.com%3A%3A%3A%3Apmf_from_free_search; yfx_key_10000042=; yfx_f_l_v_t_10000042=f_t_1489306390978__r_t_1526085647662__v_t_1526087096063__r_c_10; VISITED_MENU=%5B%228536%22%2C%228451%22%2C%228535%22%2C%228466%22%2C%228532%22%2C%228525%22%2C%229729%22%2C%228352%22%2C%228464%22%2C%228473%22%2C%228528%22%5D"
    url = "http://query.sse.com.cn/security/stock/downloadStockListFile.do?csrcCode=&stockCode=&areaName=&stockType=1"
    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
        'Cookie': Cookie,
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Host': 'query.sse.com.cn',
        'Referer': 'http://www.sse.com.cn/assortment/stock/list/share/'
    }
    try:
        req = request.Request(url,None,headers)
        response = request.urlopen(req)
        df = pd.read_csv(response, encoding='gbk', sep='\s+',converters={u'公司代码':str})    
        print('get sh stock list -- succeed')
        df = df[[u'公司代码',u'公司简称',u'上市日期']]
        return df        
    except Exception as e:
        print('get sh stock list -- failed', e)
    
    
def getstockid_sz():
    #url = 'http://www.szse.cn/szseWeb/ShowReport.szse?SHOWTYPE=xlsx&CATALOGID=1110&tab1PAGENO=1&ENCODE=1&TABKEY=tab1'
    url = 'http://www.szse.cn/api/report/ShowReport?SHOWTYPE=xlsx&CATALOGID=1110&TABKEY=tab1'
    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Host': 'www.szse.cn',
        'Referer': 'http://www.szse.cn/market/stock/list/index.html'
    }
    sz_filename = '..\\data\\stock_sz.xlsx'
    try:
        req = request.Request(url,None,headers)
        response = request.urlopen(req)
        if response.status==200:
            data = response.read()
            with open(sz_filename,'wb') as f:
                f.write(data)
            df = pd.read_excel(sz_filename,converters={u'公司代码':str,u'A股代码':str},thousands=',')
            df = df[pd.notnull(df[u'A股代码'])]
            #df[u'A股总股本']=df[u'A股总股本']/10000
            #df[u'A股流通股本']=df[u'A股流通股本']/10000
            print('get sz stock list -- succeed')
            df = df.rename(columns={u'A股上市日期':u'上市日期'})
            df = df[[u'公司代码',u'公司简称',u'上市日期']]
            return df
    except Exception as e:
        print('get sz stock list -- failed', e)
    
def get_stock(allvalues=False):
    filename = '..\\data\\stock.csv'
    fc = pd.read_csv(filename,usecols=[0,2],converters={u'stockid':str})
    if allvalues==False:
        today = datetime.today()
        startdate = today - timedelta(365)
        startdate = int(startdate.strftime('%Y%m%d'))
        #print(startdate)
        #print(fc.head())
        fc = fc[fc[u'onboard_date']<startdate]
    #print(fc.head())
    fc = list(fc[u'stockid'])
    return fc
def get_industry():
    filename = '..\\data\\stock_gszl.csv'
    '''file_mapping = 'data\\industry_mapping.csv'
    industry_mapping = pd.read_csv(file_mapping)
    row_count = len(industry_mapping.index)
    industry = pd.DataFrame()
    for i in range(row_count):
        plant_id = industry_mapping.iloc[i,0]
        plant_name = industry_mapping.iloc[i,1]
        #url = 'http://quotes.money.163.com/hs/service/diyrank.php?host=http%3A%2F%2Fquotes.money.163.com%2Fhs%2Fservice%2Fdiyrank.php&page=0&query=PLATE_IDS%3Ahy002007&fields=NO%2CSYMBOL%2CNAME&count=200&type=query'
        url = 'http://quotes.money.163.com/hs/service/diyrank.php?host=http%3A%2F%2Fquotes.money.163.com%2Fhs%2Fservice%2Fdiyrank.php&page=0&query=PLATE_IDS%3A'+plant_id+'&fields=NO%2CSYMBOL%2CNAME&count=500&type=query'
        with request.urlopen(url) as f:
            data = json.load(f)
        pagecount = data['pagecount']
        data = data['list']
        fc = pd.DataFrame(data)
        fc = fc.rename(columns={'NAME':'name','SYMBOL':'stockid'})
        fc['industry'] = plant_name
        industry = pd.concat([industry,fc],ignore_index=True)
        if pagecount>1:
             print(plant_id,'--','--partial failed')
    industry.to_csv(filename,index=False)'''
    url = 'http://quotes.money.163.com/hs/marketdata/service/gszl.php?host=/hs/marketdata/service/gszl.php&page=0&count=0'
    with request.urlopen(url) as f:
        data = json.load(f)
    count = data['total']
    url = 'http://quotes.money.163.com/hs/marketdata/service/gszl.php?host=/hs/marketdata/service/gszl.php&page=0&fields=NO,SYMBOL,SNAME,COMPANYNAME,ITPROFILE21,ITPROFILE26,CINDUSTRY2,CODE&sort=ITPROFILE21&order=asc&count='+count+'&type=query'
    with request.urlopen(url) as f:
        data = json.load(f)
    data = data['list']
    fc = pd.DataFrame(data) 
    fc.to_csv(filename,index=False)       
    fc = fc.rename(columns={'SYMBOL':'stockid','CINDUSTRY2':'industry'})
    fc = fc[['stockid','industry']]
    print('get stock industry list success')
    return fc


if __name__ == '__main__':
    app()