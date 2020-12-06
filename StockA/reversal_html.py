# -*- coding: utf-8 -*-

import pandas as pd

content_head = u'''<!DOCTYPE html>
<html>
<head>
	<title>月线反转</title>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <style type="text/css">
        img {width="600" height="300"}
    </style>
</head>
<body>
	<div align="center">
    <table border="1">
		
        '''
#date,stockid,name,onboard_date,type,industry,report_date,net_profit_growth,shift1,shift2,gap_dates
content_tail = '''
</div>
</body>
</html>'''

pricegap_filename = '..\\data\\reversal_analysis.csv'
#date,stockid,name,industry,onboard_date,type,report_date,net_profit_growth,shift1,shift2,growth_3season,EXCHANGE,SCSTC27,close,high,rps50,close_year,high50,high120,reversal,reversal30,recent
data = pd.read_csv(pricegap_filename, converters={u'stockid':str,u'date':str,u'onboard_date':str,u'report_date':str,u'gap_dates':str},usecols=[0,1,2,3,4,5,6,7,8,9,21])
data = data[['date','stockid','name','industry','type','onboard_date','report_date','net_profit_growth','shift1','shift2','recent']]
data = data.sort_values(by=['date','stockid'],ascending=False)
data = data.rename(columns={'date':'信号日期','stockid':'代码','name':'名称','industry':'行业'})
recent = data.recent.values
data.drop('recent',axis=1,inplace=True)
data['net_profit_growth'] = data['net_profit_growth'].apply(lambda x: format(x,'.2%'))
data['shift1'] = data['shift1'].apply(lambda x: format(x,'.2%'))
data['shift2'] = data['shift2'].apply(lambda x: format(x,'.2%'))
#data['gap_dates'] = data['gap_dates'].str.replace(';','; <br>')
data = data[['信号日期','代码','名称','行业']]

table_head = '<table border="1"><tr><th>'+'</th><th>'.join(data.columns.values)+'</th></tr>\r\n' #<th>K line</th>'+'\r\n'
table_tail = '</table>'

table_content = ''
for row in range(len(data)):
    stockid = data.iloc[row,1]#data['代码'].values[row]
    #print(stockid)
    if recent[row] == 1:
        table_row = '<tr><td><b>'+'</b></td><td><b>'.join(data.iloc[row,:].values)+'</td></tr><tr><td colspan="11"><img src="data/kline/'+stockid+'.png" width="600" height="300"></td></tr>'+'\r\n'
    else:
        table_row = '<tr><td>'+'</td><td>'.join(data.iloc[row,:].values)+'</td></tr><tr><td colspan="11"><img src="data/kline/'+stockid+'.png" width="600" height="300"></td></tr>'+'\r\n'
    table_content = table_content + table_row

content_middle1 = table_head + table_content + table_tail

table_content = ''
for row in range(len(data)):
    stockid = data.iloc[row,1]#data['代码'].values[row]
    #print(stockid)
    if recent[row] == 1:
        table_row = '<tr><td><b>'+'</b></td><td><b>'.join(data.iloc[row,:].values)+'</td></tr>'+'\r\n'
    else:
        table_row = '<tr><td>'+'</td><td>'.join(data.iloc[row,:].values)+'</td></tr>'+'\r\n'
    table_content = table_content + table_row

content_middle2 = table_head + table_content + table_tail

html  = content_head + content_middle1 + content_middle2 + content_tail

with open("..\\reversal.html", "w", encoding='utf-8') as f:
    f.write(html)