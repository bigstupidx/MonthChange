#!bin/sh
cd StockA
python stock_info.py                          #获取A股列表
python stock_jjcg.py 2019-09-30         #获取基金持股，参数为季度的最后一天，程序会获取近两个季度的基金持股数据并合并
python stock_reprice.py                      #雪球下载前复权日线
python stock_rps.py                            #计算RPS
python stock_reversal.py                     #计算月线反转
python reversal_analysis.py                 #过滤基金持股>=3%
python stock_kline.py                         #画K线图
python reversal_html.py                      #生成html文档，便于查看