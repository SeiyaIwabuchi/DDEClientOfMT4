# -*- coding: utf-8 -*-
from flask import Flask, request
import datetime
import time
from typing import List, Dict
import sys
import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mpl_finance
import numpy as np
from forbiddenfruit import curse
import threading
import pickle
import math

localDatetime:datetime.datetime = None

class CandleStick:
    #高値安値の更新はティックが更新されるたびに更新する
    #作成は時間単位で行う
    yinYangConvList:list = ["陰","無","陽"]
    def __init__(self,period:datetime.timedelta,high:float=0,low:float=0,opening:float=0,closeing:float=0):
        self.high:float = high
        self.low:float = low
        self.opening:float = opening
        self.closing:float = closeing
        self.period:datetime.timedelta = period
        self.startTime:datetime.datetime = datetime.datetime.now()
        self.endTime:datetime.datetime = None
        self.yinYang:int = None
        
    def update(self,price):
        self.high = max(self.high,price) if self.high != None else price
        self.low = min(self.low,price) if self.low != None else price
        self.closing = price
        if self.opening == None:
            self.opening = price

    def close(self):
        if self.opening == self.closing:
            self.yinYang = 0
        elif self.opening < self.closing:
            self.yinYang = 1
        elif self.opening > self.closing:
            self.yinYang = -1
        self.endTime = datetime.datetime.now()

    def print(self):
        self.close()
        print("種類:{} 時間:{} 始値:{} 高値:{} 安値:{} 終値:{} 陰陽:{}".format(self.period,self.startTime,self.opening,self.high,self.low,self.closing,self.yinYangConvList[self.yinYang+1]))


class CandleType:
    seconds5 = datetime.timedelta(seconds=5)
    seconds30 = datetime.timedelta(seconds=30)
    minutes1 = datetime.timedelta(minutes=1)
    minutes5 = datetime.timedelta(minutes=5)
    minutes15 = datetime.timedelta(minutes=15)
    minutes30 = datetime.timedelta(minutes=30)
    hours1 = datetime.timedelta(hours=1)
    hours4 = datetime.timedelta(hours=4)
    hours6 = datetime.timedelta(hours=6)
    hours12 = datetime.timedelta(hours=12)
    days1 = datetime.timedelta(days=1)

class CandleManager:
    def __init__(self):
        self.candleSticks:Dict[datetime.timedelta,List[CandleStick]] = {}

    def getLatest(self,sticks:list) -> CandleStick:
            #ここで1つも要素がないときはIndexErrorとなるが警告のみ
            try:
                return sticks[len(sticks)-1]
            except IndexError:
                print("Add at least one element.",file=sys.stderr)

    def tickUpdate(self):
        #ある足全部に対して更新をかける
        if tick.nowPrice != None:
            for sticks in self.candleSticks.values():
                self.getLatest(sticks).update(tick.nowPrice)
                if self.getLatest(sticks).startTime > datetime.datetime.now():
                    self.getLatest(sticks).startTime = datetime.datetime.now()
    
    def getNowTotalSeconds(self):#0時から何秒を返す
        now = datetime.datetime.now()
        return datetime.timedelta(hours=now.hour,minutes=now.minute,seconds=now.second).total_seconds()

    def stickCreate(self):
        time.sleep(3)
        oldDatetime = datetime.datetime.now()
        while True:
            if oldDatetime.second < datetime.datetime.now().second or datetime.datetime.now().second == 0:
                oldDatetime = datetime.datetime.now()
                for sticks in self.candleSticks.values():
                    if self.getNowTotalSeconds() % self.getLatest(sticks).period.total_seconds() == 0: #0時から経過した秒を期間の秒で割った余りが0なら
                        tmpStick = self.getLatest(sticks)
                        #今の足をクローズする
                        tmpStick.closing = tick.nowPrice
                        tmpStick.close()
                        #tmpStick.print()
                        #足リストに新しく足を追加する
                        sticks.append(CandleStick(tmpStick.period,high=tick.nowPrice,low=tick.nowPrice,opening=tick.nowPrice,closeing=tick.nowPrice))
                        #print("newStick:{}".format(tmpStick.period))
            time.sleep(1)
    
    def candleStickGenerator(self,period:datetime.timedelta):
        self.candleSticks[period] = []
        self.candleSticks[period].append(CandleStick(period,high=tick.nowPrice,low=tick.nowPrice,opening=tick.nowPrice,closeing=tick.nowPrice))

class Tick:
    def __init__(self):
        self.nowPrice:float = None
    def update(self,price:float):
        self.nowPrice = price

class MovingAverage:
    """
    グラフ表示を前提としたクラス
    """
    def __init__(self,period:int):
        self.result:Dict[datetime.datetime,float] = {}
        self.period = period
    
    def update(self,candleList):
        #print("Update MA")
        candleList:List[CandleStick]
        if len(candleList) >= self.period:
            sum = 0
            for cand in candleList[len(candleList)-self.period:]:
                sum += cand.closing
            self.result[candleList[len(candleList)-1].startTime] = sum/self.period
        elif len(candleList) < self.period:
            sum = 0
            for cand in candleList:
                sum += cand.closing
            self.result[candleList[len(candleList)-1].startTime] = sum/len(candleList)
        #print("Update MV now is {MVPrice}".format(MVPrice=self.result[len(self.result)-1] if len(self.result) >= 1 else None))
        #print(self.result)

def chartUpdate():
    time.sleep(3)
    fig, axtap = plt.subplots(ncols=len(cm.candleSticks),figsize=(16,9),dpi=120,num=1)
    oldTickPrice = tick.nowPrice
    oldUpdateTime = datetime.datetime.now()
    while True:
        if oldTickPrice != tick.nowPrice or datetime.datetime.now() >= oldUpdateTime + datetime.timedelta(seconds=5):

            oldTickPrice = tick.nowPrice
            oldUpdateTime = datetime.datetime.now()

            #plt.cla()            
            #plt.clf()
            #plt.close()
            fig, axtap = plt.subplots(ncols=len(cm.candleSticks),figsize=(16,9),clear=True,dpi=110,num=1)

            axList = list(axtap)
            dataList = []

            candlePeriod:datetime.timedelta

            for index,(candlePeriod,candleSticks) in enumerate(cm.candleSticks.items()):
                cs:List[CandleStick] = cm.candleSticks[candlePeriod]
                cs = cs[len(cs)-60 if len(cs) >= 60 else 0:]
                dataList.append(list())
                for t in cs:
                    tms = [mdates.date2num(t.startTime),t.opening,t.high,t.low,t.closing]
                    dataList[len(dataList)-1].append(tms)
                try:
                    mpl_finance.candlestick_ohlc(axList[index], dataList[len(dataList)-1], width=candlePeriod.total_seconds()/1.5/pow(10,5), alpha=0.5, colorup='b', colordown='r')
                    try:
                        for mvObj in mvDict[candlePeriod]:
                                mvObj.update(cm.candleSticks[candlePeriod])
                                axList[index].plot(mdates.date2num(list(mvObj.result.keys())[len(cs)-60 if len(cs) >= 60 else 0:]),list(mvObj.result.values())[len(cs)-60 if len(cs) >= 60 else 0:])
                    except KeyError:
                        #print("Not found MA:{}".format(candlePeriod))
                        pass
                    axList[index].xaxis_date()
                    axList[index].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
                    #axList[index].grid(True)
                    axList[index].set_xlabel("Date")
                    axList[index].set_ylabel("Price")
                    axList[index].set_title("USD-JPY {}:{}:{}".format(int(candlePeriod.total_seconds()//3600),int(candlePeriod.total_seconds()//60),int(candlePeriod.total_seconds()%60)))
                    axList[index].frameon = True
                except TypeError:
                    #print("Skip figure draw.")
                    pass

            """cs1:List[CandleStick] = cm.candleSticks[CandleType.seconds5]
            cs1 = cs1[len(cs1)-120 if len(cs1) >= 120 else 0:]
            data1 = []
            for t in cs1:
                tms = [mdates.date2num(t.startTime),t.opening,t.high,t.low,t.closing]
                data1.append(tms)

            mpl_finance.candlestick_ohlc(ax1, data1, width=0.00003, alpha=0.5, colorup='b', colordown='r')
            ax1.xaxis_date()
            ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M:%S"))
            ax1.grid(True)
            ax1.set_xlabel("Date")
            ax1.set_ylabel("Price")
            ax1.set_title("USD-JPY {} {}".format("5sec",datetime.datetime.now()))

            cs2:List[CandleStick] = cm.candleSticks[CandleType.minutes1]
            cs2 = cs2[len(cs2)-120 if len(cs2) >= 120 else 0:]
            data2 = []
            for t in cs2:
                tms = [mdates.date2num(t.startTime),t.opening,t.high,t.low,t.closing]
                data2.append(tms)


            mpl_finance.candlestick_ohlc(ax2, data2, width=0.00065, alpha=0.5, colorup='b', colordown='r')
            ax2.xaxis_date()
            ax2.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M:%S"))
            ax2.grid(True)
            ax2.set_xlabel("Date")
            ax2.set_ylabel("Price")
            ax2.set_title("USD-JPY {} {}".format("1min",datetime.datetime.now()))"""


        plt.pause(0.001)

def setLocalDatetime(datetimeText):
    global localDatetime
    localDatetime = datetime.datetime.strptime(datetimeText,"%Y.%m.%d %H:%M:%S")

def getLocalDatetime(self, tz=None):
    return localDatetime

def runLocalDatetime():
    global localDatetime
    #while True:
    #print("nowDatetime:{}".format(localDatetime))
    #time.sleep(1)
    localDatetime += datetime.timedelta(seconds=1)

app = Flask(__name__)
tick = Tick()
cm = CandleManager()
mvDict:Dict[datetime.timedelta,List[MovingAverage]] = {}

@app.route("/")
def root():
    return 'OK'



@app.route("/sendTick")
def sendTick():
    #MT4からティックの更新を受信
    ask  = float(request.args.get('ask'))
    bid  = float(request.args.get('bid'))
    datetimeText:str = request.args.get('datetime')
    datetimeText = datetimeText.replace("%20"," ")
    setLocalDatetime(datetimeText)

    #print("Receive Tick:{datetime}".format(datetime=datetime.datetime.now()))
    #print("ASK:{ask}".format(ask=ask))
    #print("BID:{bid}".format(bid=bid))
    #システム側のティックを更新
    tick.update(ask)
    #足の更新
    cm.tickUpdate()
    return "OK"

backTest = False

if __name__ == '__main__':
    try:
        if backTest:
            localDatetime = datetime.datetime.now()
            curse(datetime.datetime, 'now', classmethod(getLocalDatetime))
        try:
            with open("./data.bin","rb") as bin:
                cm = pickle.load(bin)
        except FileNotFoundError:
            cm.candleStickGenerator(CandleType.minutes1)
            cm.candleStickGenerator(CandleType.seconds30)
            cm.candleStickGenerator(CandleType.seconds5)
            mvDict[CandleType.seconds5] = []
            mvDict[CandleType.seconds5].append(MovingAverage(20)) #5秒足の期間12の平均移動戦
            mvDict[CandleType.seconds5].append(MovingAverage(100)) #5秒足の期間12の平均移動戦
            mvDict[CandleType.seconds30] = []
            mvDict[CandleType.seconds30].append(MovingAverage(20)) #5秒足の期間12の平均移動戦
            mvDict[CandleType.seconds30].append(MovingAverage(100)) #5秒足の期間12の平均移動戦
            mvDict[CandleType.minutes1] = []
            mvDict[CandleType.minutes1].append(MovingAverage(20)) #5秒足の期間12の平均移動戦
            mvDict[CandleType.minutes1].append(MovingAverage(100)) #5秒足の期間12の平均移動戦
        stickProcess = threading.Thread(target=cm.stickCreate)
        stickProcess.daemon = True
        stickProcess.start()
        #clockThread = threading.Thread(target=runLocalDatetime)
        #clockThread.daemon = True
        #clockThread.start()
        chartThread = threading.Thread(target=chartUpdate)
        chartThread.daemon = True
        chartThread.start()
        #追加したい足のインスタンスを生成しCandleMagerに追加する。
        app.run(debug=False, host='0.0.0.0', port=80)
    finally:
        #with open("./data.bin","wb") as bin:
            #pickle.dump(cm,bin)
        pass