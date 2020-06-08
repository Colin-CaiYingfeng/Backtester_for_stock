# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 19:55:36 2020

@author: Colin
"""
import pandas as pd
from WindPy import w
w.start()
w.isconnected()
#%%
"""Store a single unit of data"""
class TickData:
    def __init__(self, symbol, timestamp, last_price=0, total_volume=0):
        self.symbol = symbol
        self.timestamp = timestamp
        self.open_price = 0
        self.last_price = 0
        self.total_volume = 0
        
#%%
"""Store final tickdata & Retrieve data"""
class MarketData:
    def __init__(self):
        self.__recent_ticks__ = dict()
    
    def add_last_price(self, time, symbol, price, volume):
        tick_data = TickData(symbol, time, price, volume)
        self.__recent_ticks__[symbol] = tick_data
    
    def get_existing_tick_data(self, time, symbol):
        if not symbol in self.__recent_ticks__:
            tick_data = TickData(symbol, time)
            self.__recent_ticks__[symbol] = tick_data
    
    def add_open_price(self, time, symbol, price):
        tick_data = self.get_existing_tick_data(symbol, time)
        tick_data.open_price = price
        
        return self.__recent_ticks__[symbol]
    
    def get_last_price(self, symbol):
        return self.__recent_ticks__[symbol].last_price
    
    def get_open_price(self, symbol):
        return self.__recent_ticks__[symbol].open_price
    
    def get_timestamp(self, symbol):
        return self.__recent_ticks__[symbol].timestamp
    
#%%
"""Get data from Wind"""
class MarketDataSource:
    def __init__(self):
        self.event_tick = None
        self.ticker, self.source = None, None
        self.start, self.end = None, None
        self.md = MarketData()
        
    def start_market_simulation(self):
        error, data = w.wsd(self.ticker, "open, close, volume", self.start, self.end, "Fill=Previous;PriceAdj=F", usedf = True)
        
        for time, row in data.iterrows():
            self.md.add_last_price(time, self.ticker, row["close"], row["volume"])
            self.md_add_open_price(time, self.ticker, row["open"])
        
        if not self.event_tick is None:
            self.event_tick(self.md)
    
#%%
class Order:
    def __init__(self, timestamp, symbol, qty, is_buy, is_market_order, price = 0):
        self.timestamp = timestamp
        self.symbol = symbol
        self.qty = qty
        self.price = price
        self.is_buy = is_buy
        self.is_market_order = is_market_order
        self.is_filled = False
        self.filled_price = 0
        self.filled_time = None
        self.filled.qty = 0

#%%
class Position:
    def __init__(self):
        self.symbol = None
        self.buys, self.sells, self.net = 0, 0, 0
        self.realized_pnl = 0
        self.unrealized_pnl = 0
        self.position_value = 0
    
    def event_fill(self, timestamp, is_buy, qty, price):
        if is_buy:
            self.buys += qty
        else:
            self.sells += qty
        
        self.net = self.buys - self.sells
        changed_value = qty * price * (-1 if is_buy else 1)
        self.position_value += changed_value
        
        if self.net == 0:
            self.realized_pnl = self.position_value
            
    def update_unrealized_pnl(self, price):
        if self.net == 0:
            self.unrealized_pnl = 0
        else:
            self.unrealized_pnl = price * self.net + self.position_value
        
        return self.unrealized_pnl
                
#%%
""" Base strategy engine"""
class Strategy:
    def __init__(self):
        self.event_sendorder = None
        
    def event_tick(self, market_data):
        pass
    
    def event_order(self, order):
        pass
    
    def event_position(self, position):
        pass
    
    def send_market_order(self, symbol, qty, is_buy, timestamp):
        if not self.event_sendorder is None:
            order = Order(timestamp, symbol, qty, is_buy, True)
            self.event_sendorder(order)

#%%
"""Main strategy of trading"""






















    
