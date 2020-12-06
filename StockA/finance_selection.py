# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mpl_finance as mpf
from matplotlib.pylab import date2num
from datetime import datetime
from matplotlib import dates as mdates
from matplotlib import ticker as mticker

    
finance_filename = '..\\data\\finance_analysis.csv'
stock_selection = pd.read_csv(finance_filename, converters={u'stockid':str},usecols=[0,1,2,5])
#print(stock_selection.dtypes)
cnt = len(stock_selection)
#cnt = 1
ax_rows = (cnt+1)//2

#fig = plt.figure(facecolor='#07000d',figsize=(2,4))


for i in range(cnt):
    fig = plt.figure(facecolor='#07000d',figsize=(16,8))
    stockid = stock_selection.stockid.values[i]
    #print(stock_selection.industry.values[i])
    fig_title = stockid + '(' +stock_selection.name.values[i]+') - '+stock_selection.industry.values[i]
    selected_stock=stock_selection[stock_selection['stockid']==stockid]
    print(str(i+1)+'/'+str(cnt)+' - stockid:'+stockid)

    # pefile = '..\\data\\pe\\'+stockid+'.csv'
    # pe_data = pd.read_csv(pefile, converters={u'stockid':str,u'日期':str},usecols=[0,4],nrows=400)
    # pe_data = pe_data.rename(columns={'日期':'date','PE':'pe'})
    # pe_data['median_pe'] = pe_data['pe'].median()
    # pe_data['pe_quantile20'] = pe_data['pe'].quantile(0.2)
    # pe_data['pe_quantile80'] = pe_data['pe'].quantile(0.8)
    
    filename = '..\\data\\xueqiu\\'+stockid+'.csv'
    # 对tushare获取到的数据转换成candlestick_ohlc()方法可读取的格式
    #date,volume,open,high,low,close,ma5,ma10,ma20,ma30,pe,market_capital,chg,percent,turnoverrate,amount,volume_post,amount_post,timestamp
    data = pd.read_csv(filename, converters={u'stockid':str,u'date':str},usecols=[0,1,2,3,4,5,7,8,9,10])
    #data['ma10'] = data['close'].rolling(10).mean()
    #data['ma50'] = data['close'].rolling(50).mean()
    #data = pd.merge(data,selected_stock,how='left',on=['date'])
    data['median_pe'] = data['pe'].median()
    data['pe_quantile20'] = data['pe'].quantile(0.2)
    data['pe_quantile80'] = data['pe'].quantile(0.8)
    data = data.tail(250)
    
    # data = pd.merge(data,pe_data,how='left',on=['date'])
    # data['pe'] =  data['pe'].apply(lambda x: 0 if x==np.nan else x)
    

    data['date_id'] = np.arange(len(data))
    date_tickers = data.date.values
    data_ohlc = data[['date_id','open','high','low','close']] 
    # 将时间转换为数字
    #date_time = [datetime.strptime(x,'%Y%m%d') for x in data['date']]
    #data['date_time'] = date2num(date_time)
    #data_ohlc = data[['date_time','open','high','low','close']] 

    # 创建子图
    # if i%2 == 0:
        # ax = plt.subplot2grid((ax_rows*2,16), (i//2,0), rowspan=2, colspan=4, facecolor='#07000d')
    # else:
        # ax = plt.subplot2grid((ax_rows*2,16), (i//2,1), rowspan=2, colspan=4, facecolor='#07000d')
    #ax = fig.add_subplot(ax_rows,2,i+1,facecolor='#07000d')
    ax = plt.subplot2grid((2,4), (0,0), rowspan=2, colspan=4, facecolor='#07000d')
    

    mpf.candlestick_ohlc(ax, data_ohlc.values, width=.6, colorup='#ff1717', colordown='#53c156')
    #mpf.candlestick_ohlc(ax,data_ohlc,width=1.5,colorup='r',colordown='green')
    ax.plot(data.date_id.values,data.ma10.values,'#e1edf9',label='ma10', linewidth=1.5)
    ax.plot(data.date_id.values,data.ma20.values,'#4ee6fd',label='ma20', linewidth=1.5)
    ax.plot(data.date_id.values,data.ma30.values,'#5998ff',label='ma30', linewidth=1.5)
    ax.grid(True, color='w')
    ax.xaxis.set_major_locator(mticker.MaxNLocator(10))
    #ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    #ax.xaxis.set_major_formatter(mticker.FuncFormatter(format_date))
    ax.set_xticklabels(date_tickers)
    ax.yaxis.label.set_color("r")
    ax.spines['bottom'].set_color("w")
    ax.spines['top'].set_color("w")
    ax.spines['left'].set_color("w")
    ax.spines['right'].set_color("w")
    ax.tick_params(axis='y', colors='r')
    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
    ax.tick_params(axis='x', colors='r')
    plt.title(fig_title,color='r')

    #绘制成交量
    volumeMin = 0
    axv = ax.twinx()
    axv.bar(data.date_id.values, data.volume.values, facecolor='#00ffe8', alpha=.4)
    axv.axes.yaxis.set_ticklabels([])
    axv.grid(False)
    ###Edit this to 3, so it's a bit larger
    axv.set_ylim(0, 3*data.volume.values.max())
    axv.spines['bottom'].set_color("w")
    axv.spines['top'].set_color("w")
    axv.spines['left'].set_color("w")
    axv.spines['right'].set_color("w")
    axv.tick_params(axis='x', colors='r')
    axv.tick_params(axis='y', colors='r')
    
    #绘制PE
    axpe = ax.twinx()
    #axpe.fill_between(data.date_id.values,volumeMin, data.volume.values, facecolor='#00ffe8', alpha=.4)
    axpe.plot(data.date_id.values, data.pe.values, color='#00ffe8', alpha=.6,linewidth=1.5)
    axpe.plot(data.date_id.values, data.median_pe.values, color='#5998ff', alpha=.8,linewidth=2)
    axpe.plot(data.date_id.values, data.pe_quantile20.values, color='#5998ff', alpha=.8,linewidth=2)
    axpe.plot(data.date_id.values, data.pe_quantile80.values, color='#5998ff', alpha=.8,linewidth=2)
    axpe.axes.yaxis.set_ticklabels([])
    axpe.grid(False)
    ###Edit this to 3, so it's a bit larger
    axpe.set_ylim(-2*data.pe.max(), data.pe.max())
    axpe.spines['bottom'].set_color("w")
    axpe.spines['top'].set_color("w")
    axpe.spines['left'].set_color("w")
    axpe.spines['right'].set_color("w")
    axpe.tick_params(axis='x', colors='r')
    axpe.tick_params(axis='y', colors='r')


    plt.subplots_adjust(left=.09, bottom=0.14, right=.94, top=.95, wspace=.20, hspace=0.3)
    plt.savefig('..\\data\\finance_selection\\'+stockid+'.png')
    #plt.show()
    plt.close()


#begin html
content_head = u'''<!DOCTYPE html>
<html>
<head>
	<title>基本面选股</title>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <style type="text/css">
        img {width="600" height="300"}
    </style>
</head>
<body>
	<table border="1">
        '''
#date,stockid,name,onboard_date,type,industry,report_date,net_profits_yoy,shift1,shift2,gap_dates
content_tail = '''	<table>
</body>
</html>'''

filename = '..\\data\\finance_analysis.csv'
data = pd.read_csv(filename, converters={u'stockid':str,u'date':str,u'onboard_date':str,u'report_date':str})
#stockid,name,onboard_date,type,industry,report_date,
#gross_margin,gross_revenue_yoy,
#growth_yearly_shift0,growth_yearly_shift1,growth_yearly_shift2,
#growth_season_shift0,growth_season_shift1,
#asset_liability_ratio,current_ratio,quick_ratio,rolling_net_profits,average_equity,roe

data['gross_margin'] = data['gross_margin'].apply(lambda x: format(x,'.2%'))
data['case'] = data['case'].apply(str)
#data['gross_revenue_yoy'] = data['gross_revenue_yoy'].apply(lambda x: format(x,'.2%'))
data['growth_yearly'] = data[['growth_yearly_shift0','growth_yearly_shift1','growth_yearly_shift2']].apply(lambda x: format(x[2],'.2%')+' -> '+format(x[1],'.2%')+' -> '+format(x[0],'.2%'),axis=1)
data['growth_season'] = data[['growth_season_shift0','growth_season_shift1']].apply(lambda x: format(x[1],'.2%')+' -> '+format(x[0],'.2%'),axis=1)
# data['growth_yearly_shift0'] = data['growth_yearly_shift0'].apply(lambda x: format(x,'.2%'))
# data['growth_yearly_shift1'] = data['growth_yearly_shift1'].apply(lambda x: format(x,'.2%'))
# data['growth_yearly_shift2'] = data['growth_yearly_shift2'].apply(lambda x: format(x,'.2%'))
# data['growth_season_shift0'] = data['growth_season_shift0'].apply(lambda x: format(x,'.2%'))
# data['growth_season_shift1'] = data['growth_season_shift1'].apply(lambda x: format(x,'.2%'))
data['asset_liability_ratio'] = data['asset_liability_ratio'].apply(lambda x: format(x,'.2%'))
data['current_ratio'] = data['current_ratio'].apply(lambda x: format(x,'.1f'))
data['quick_ratio'] = data['quick_ratio'].apply(lambda x: format(x,'.1f'))
#data['rolling_net_profits'] = data['rolling_net_profits'].apply(lambda x: format(x,'0,.1f'))
#data['average_equity'] = data['average_equity'].apply(lambda x: format(x,'0,.1f'))
data['roe'] = data['roe'].apply(lambda x: format(x,'.2%'))
data['gross_revenue_growth_std'] = data['gross_revenue_growth_std'].apply(lambda x: format(x,'.1%'))

data.drop(['growth_yearly_shift0','growth_yearly_shift1','growth_yearly_shift2','growth_season_shift1','growth_season_shift0','rolling_net_profits','rolling_equity'],axis=1,inplace=True)
data = data[['stockid','name','industry','case','onboard_date','type','report_date','roe','gross_margin','asset_liability_ratio','current_ratio','quick_ratio','growth_yearly','growth_season','gross_revenue_growth_std']]
data = data.rename(columns={'stockid':'代码',
                            'name':'名称',
                            'industry':'行业',
                            'gross_margin':'毛利率',
                            #'gross_revenue_yoy':'营业收入增长率',
                            'asset_liability_ratio':'资产负债率',
                            'current_ratio':'流动比率',
                            'quick_ratio':'速动比率',
                            'growth_yearly':'三年利润增长率<p>(前->后)',
                            'growth_season':'两个季度利润增长率<p>(前->后)',
                            'gross_revenue_growth_std':'标准差'
                            })




table_head = '<tr><th>'+'</th><th>'.join(data.columns.values)+'</th><th>K line</th></tr>'+'\r\n'

table_content = ''
for row in range(len(data)):
    stockid = data['代码'].values[row]
    table_row = '<tr><td>'+'</td><td>'.join(data.loc[row,:].values)+'</td><td><img src="data/finance_selection/'+stockid+'.png" width="600" height="300"></td></tr>'+'\r\n'
    table_content = table_content + table_row

content_middle = table_head + table_content

html  = content_head + content_middle + content_tail

with open("..\\finance_selection.html", "w", encoding='utf-8') as f:
    f.write(html) 