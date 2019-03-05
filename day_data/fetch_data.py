import sys, os
from concurrent.futures.thread import ThreadPoolExecutor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import tushare as ts
from sqlalchemy import create_engine
import time

ts.set_token('9c4af04257e55b3f490d14ac46c00cd71383ed0846d8e10694907926')
pro = ts.pro_api()

startDate = '20100101'
endDate = time.strftime('%Y%m%d', time.localtime(time.time()))

database = 'mysql+pymysql://root:hefei168lj@localhost/malason?charset=utf8'
engine = create_engine(database)


def fetch_trade_cal():
    trade_cal = pro.trade_cal(exchange='', start_date=startDate, end_date=endDate)
    trade_cal.to_sql('m_fd_data_trade_cal', engine, if_exists='replace')


def fetch_stock():
    data = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    data.to_sql('m_fd_data_cn_stock_list', engine, if_exists='replace')


def fetch_task(symbol):
    df = ts.pro_bar(pro_api=pro, ts_code=symbol, adj='qfq', start_date=startDate, end_date=endDate)
    if df is not None:
        df.to_sql('m_fd_data_' + symbol, engine, index=False, if_exists='replace')


def batch_fetch_data():
    data = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    with ThreadPoolExecutor(10) as executor:
        for item in data['ts_code']:
            executor.submit(fetch_task, item)


fetch_trade_cal()
fetch_stock()
batch_fetch_data()
