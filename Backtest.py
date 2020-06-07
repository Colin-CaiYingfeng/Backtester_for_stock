# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 19:55:36 2020

@author: Colin
"""
import pandas as pd
#%%
'''Store a single unit of data'''
class TickData:
    def __init__(self, symbol, timestamp, last_price=0, total_volume=0):
        self.symbol = symbol
        self.timestamp = timestamp
        self.open_price = 0
        self.last_price = 0
        self.total_volume = 0
        
#%%
'''Store final tickdata & Retrieve data'''
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





























    