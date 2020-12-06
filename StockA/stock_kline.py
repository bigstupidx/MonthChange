# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mpl_finance as mpf
from matplotlib.pylab import date2num
from datetime import datetime
from matplotlib import dates as mdates
from matplotlib import ticker as mticker

def app():   
    pricegap_filename = '..\\data\\reversal_analysis.csv'
    reversal = pd.read_csv(pricegap_filename, converters={u'stockid':str,u'date':str},usecols=[0,1,2,3,5])

    cnt = len(reversal)
    #cnt = 1

    
    for i in range(cnt):
        stockid = reversal.stockid.values[i]
        fig_title = stockid + '(' +reversal.name.values[i]+') - '+reversal.industry.values[i]
        reversal_stock=reversal[reversal['stockid']==stockid]
        create_kline(stockid,fig_title,reversal_stock)

def create_kline(stockid=None,fig_title=None,reversal_stock=None):

    
    #"date","volume","open","high","low","close","ma5","ma10","ma20","ma30","pe","market_capital","chg","percent","turnoverrate","amount","volume_post","amount_post","timestamp"
    filename = '..\\data\\xueqiu\\'+stockid+'.csv'
    # 对tushare获取到的数据转换成candlestick_ohlc()方法可读取的格式
    data = pd.read_csv(filename, converters={u'stockid':str,u'date':str},usecols=[0,1,2,3,4,5,7,8,9])
    #data['ma10'] = data['close'].rolling(10).mean()
    data['ma50'] = data['close'].rolling(50).mean()
    data['shift_close'] = data['close'].shift(1)
    data['color'] = data[['shift_close','close']].apply(lambda x: '#ff1717' if x[1]>=x[0] else '#53c156',axis=1)
    data = data.tail(180)
    data = pd.merge(data,reversal_stock,how='left',on=['date'])
    #print(data.head())

    data['date_id'] = np.arange(len(data))
    date_tickers = data.date.values
    date_count = len(data)
    xticks = list(range(0,date_count,18))
    xlabels = [date_tickers[x] for x in xticks]
    xticks.append(date_count-1)
    xlabels.append(date_tickers[-1])
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
    fig = plt.figure(figsize=(16,9))
    ax  = plt.subplot2grid((3,4), (0,0), rowspan=2, colspan=4)
    axv = plt.subplot2grid((3,4), (2,0), rowspan=1, colspan=4, sharex=ax)
    

    mpf.candlestick_ohlc(ax, data_ohlc.values, width=.6, colorup='#ff1717', colordown='#53c156')
    #mpf.candlestick_ohlc(ax,data_ohlc,width=1.5,colorup='r',colordown='green')
    ax.plot(data.date_id.values,data.ma10.values,'#e1edf9',label='ma10', linewidth=1.5)
    ax.plot(data.date_id.values,data.ma20.values,'#4ee6fd',label='ma20', linewidth=1.5)
    ax.plot(data.date_id.values,data.ma30.values,'#5998ff',label='ma30', linewidth=1.5)
    ax.grid(True, color='lightgray')
    #ax.xaxis.set_major_locator(mticker.MaxNLocator(10))
    #ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    #ax.xaxis.set_major_formatter(mticker.FuncFormatter(format_date))
    #ax.set_xticklabels(date_tickers)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xlabels)
    # ax.yaxis.label.set_color("r")
    # ax.spines['bottom'].set_color("w")
    # ax.spines['top'].set_color("w")
    # ax.spines['left'].set_color("w")
    # ax.spines['right'].set_color("w")
    # ax.tick_params(axis='y', colors='r')
    #plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
    #ax.tick_params(axis='x', colors='r')
    ax.set_title(fig_title)

    #绘制成交量
    #volumeMin = 0
    
    #axv.fill_between(data.date_id.values,volumeMin, data.volume.values, facecolor='#00ffe8', alpha=.4)
    axv.bar(data.date_id.values, data.volume.values, color=data.color.values)
    #axv.set_xticklabels([])
    axv.set_yticklabels([])
    axv.grid(True, color='lightgray')
    ###Edit this to 3, so it's a bit larger
    #axv.set_ylim(0, 3*data.volume.values.max())
    # axv.spines['bottom'].set_color("w")
    # axv.spines['top'].set_color("w")
    # axv.spines['left'].set_color("w")
    # axv.spines['right'].set_color("w")
    axv.tick_params(axis='x', colors='w')
    # axv.tick_params(axis='y', colors='r')

    ax.annotate(data.loc[data['stockid']==stockid,'date'].values[0],(data.loc[data['stockid']==stockid,'date_id'].values[0],data.loc[data['stockid']==stockid,'high'].values[0]),
            xytext=(0.85, 0.9), textcoords='axes fraction',
            arrowprops=dict(facecolor='white', shrink=0.05),
            fontsize=10, color = 'r',
            horizontalalignment='right', verticalalignment='bottom')
    #plt.subplots_adjust(left=.09, bottom=0.14, right=.94, top=.95, wspace=.20, hspace=0.3)
    plt.savefig('..\\data\\kline\\'+stockid+'.png')
    #plt.show()
    plt.close()
 

if __name__=='__main__' :
    app()