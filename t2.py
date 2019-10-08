import json
import requests
import datetime
import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, timezone
from pandas import DataFrame, Series, to_datetime, concat
from mpl_finance import candlestick_ohlc

if __name__ == '__main__':
    response = json.loads(requests.get("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc?periods=60&after=1557172800&before=1557176340").text)

    # 7番目の要素はdocsに記載がないので何なのか不明
    df = DataFrame(response['result']['60'], columns=['date','open','high','low','close','volume','unknown']).dropna().drop(columns=['volume','unknown'])
    # print(df.head(3))
    #         date    open    high     low   close
    # 0  1557432000  664434  665011  663901  664755
    # 1  1557432060  664826  664826  663800  663834
    # 2  1557432120  663834  664117  663723  664069

    # レスポンスのタイムスタンプがUnixTimestamp形式なのでdatetime型に変換し、pandas.DatetimeIndexを設定する
    df['date'] = to_datetime(df['date'], unit='s', utc=True)
    df.set_index('date', inplace=True)
    df.index = df.index.tz_convert('Asia/Tokyo')
    # print(df.head(3))
    #                             open    high     low   close
    # date                                                     
    # 2019-05-10 05:00:00+09:00  664434  665011  663901  664755
    # 2019-05-10 05:01:00+09:00  664826  664826  663800  663834
    # 2019-05-10 05:02:00+09:00  663834  664117  663723  664069

    plt.style.use('ggplot')

    ax = plt.subplot()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M', tz=timezone(timedelta(hours=9))))

    # candlestick_ohlc の第二引数に渡すタプルイテレータを生成
    # @see https://github.com/matplotlib/mpl_finance/blob/master/mpl_finance.py
    quotes = zip(mdates.date2num(df.index), df['open'], df['high'], df['low'], df['close'])
    candlestick_ohlc(ax, quotes, width=(1/24/len(df))*0.7, colorup='g', colordown='r')

    plt.show()