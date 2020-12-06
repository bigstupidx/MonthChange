# -*- coding: utf-8 -*-

#基金持股
##import os

import numpy as np
import pandas as pd
from urllib import request
import json, sys

    
def app():
    if len(sys.argv)>1:
        report_season = sys.argv[1]
    else:
        print('please input parameter - report season\nformat like \'python stock_jjcg.py 2018-12-31\'')
        return
    end = str(report_season)
    if end[5:7]=='03':
        shift1 = str(int(end[:4])-1)+'-12-31'
        shift2 = str(int(end[:4])-1)+'-09-30'
    elif end[5:7]=='06':
        shift1 = str(int(end[:4]))+'-03-31'
        shift2 = str(int(end[:4])-1)+'-12-31'
    elif end[5:7]=='09':
        shift1 = str(int(end[:4]))+'-06-30'
        shift2 = str(int(end[:4]))+'-03-31'
    elif end[5:7]=='12':
        shift1 = str(int(end[:4]))+'-09-30'
        shift2 = str(int(end[:4]))+'-06-30'
    else:
        print('please input parameter - report season\nformat like \'python stock_jjcg.py 2018-12-31\'') 
        return
        
    #基金持股
    filename = '..\\data\\stock_jjcg.csv'
    jjcg1 = get_jjcg(shift1,end)
    jjcg2 = get_jjcg(shift2,shift1)
    jjcg = pd.concat([jjcg1,jjcg2],ignore_index=True)
    jjcg = jjcg.replace('--','')
    max_date= jjcg.groupby('stockid',as_index=False)['REPORTDATE'].max()
    jjcg = pd.merge(jjcg,max_date,on=['stockid','REPORTDATE'],how='inner')
    jjcg.to_csv(filename,index=False)
    print('get jjcg list success')
    
def get_jjcg(start,end):
    jjcg = pd.DataFrame()
    page = 0
    while(True):
        url='http://quotes.money.163.com/hs/marketdata/service/jjcgph.php?host=/hs/marketdata/service/jjcgph.php&page='+str(page)+'&query=start:'+start+';end:'+end+'&fields=RN,SYMBOL,SNAME,REPORTDATE,SHULIANG,SHULIANGBIJIAO,GUSHU,GUSHUBIJIAO,SHIZHI,SCSTC27&sort=SCSTC27&order=desc&count=5000&type=query'
        #print(url)
        with request.urlopen(url) as f:
            data = json.load(f)
        data = data['list']
        if len(data)==0:
            break
        fc = pd.DataFrame(data) 
        fc = fc.rename(columns={'SYMBOL':'stockid'})
        jjcg = pd.concat([jjcg,fc],ignore_index=True)
        print('page '+str(page)+' done')
        page = page + 1
    return jjcg
    





if __name__ == '__main__':
    app()