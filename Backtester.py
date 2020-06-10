# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 19:55:36 2020

@author: Colin
"""
import pandas as pd
#%%
from WindPy import w
w.start()
w.isconnected()
#%%
"""Store a single unit of data"""
class TickData:
    def __init__(self, code, timestamp, last_price=0, total_volume=0):
        self.code = code
        self.timestamp = timestamp
        self.open_price = 0
        self.last_price = 0
        self.total_volume = 0
        
#%%
"""Store final tickdata & Retrieve data"""
class MarketData:
    def __init__(self):
        self.__recent_ticks__ = dict()
    
    def add_last_price(self, time, code, price, volume):
        tick_data = TickData(code, time, price, volume)
        self.__recent_ticks__[code] = tick_data
    
    def get_existing_tick_data(self, time, code):
        if not code in self.__recent_ticks__:
            tick_data = TickData(code, time)
            self.__recent_ticks__[code] = tick_data
    
    def add_open_price(self, time, code, price):
        tick_data = self.get_existing_tick_data(code, time)
        tick_data.open_price = price
        
        return self.__recent_ticks__[code]
    
    def get_last_price(self, code):
        return self.__recent_ticks__[code].last_price
    
    def get_open_price(self, code):
        return self.__recent_ticks__[code].open_price
    
    def get_timestamp(self, code):
        return self.__recent_ticks__[code].timestamp
    
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
    def __init__(self, timestamp, code, qty, is_buy, is_market_order, price = 0):
        self.timestamp = timestamp
        self.code = code
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
        self.code = None
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
    
    def send_market_order(self, code, qty, is_buy, timestamp):
        if not self.event_sendorder is None:
            order = Order(timestamp, code, qty, is_buy, True)
            self.event_sendorder(order)

#%%
"""Main strategy of trading"""
"""Based on Strategy class"""
class MyStrategy(Strategy):
    def __init__(self, code, lookback_intervals = 0):
        Strategy.__init__(self)
        self.code = code
        self.lookback_intervals = lookback_intervals
        self.prices = pd.DataFrame()
        self.is_long, self.is_short = False, False
        
    def event_position(self, positions):
        if self.code in positions:
            position = positions[self.code]
            self.is_long = True if position.net > 0 else False
            self.is_short = True if position.net < 0 else False
            
    def event_tick(self, market_data):
        self.store_prices(market_data)
        if len(self.prices) < self.lookback_intervals:
            return
    
    def store_prices(self, market_data):
        timestamp = market_data.get_timestamp(self.code)
        self.prices.loc[timestamp, "close"] = market_data.get_last_price(self.code)
        self.prices.loc[timestamp, "open"] = market_data.get_open_price(self.code)
    
    
    """Then def your own strategy here"""
    
    
    """After you finished your Strategy coding, send the order to the engine"""
    def on_buy_signal(self, timestamp):
        if not self.is_long:
            self.send_market_order(self.code, 100, False, timestamp)
    
    def on_sell_signal(self, timestamp):
        if not self.is_short:
            self.send_market_order(self.code, 100, False, timestamp)
#%%
class Backtester:
    def __init__(self, code, start_date, end_date):
        self.target_code = code
        self.start_dt = start_date
        self.end_dt = end_date
        self.strategy = None
        self.unfilled_orders = []
        self.position = dict()
        self.current_prices = None
        self.rpnl, self.upnl = pd.DataFrame(), pd.DataFrame()
    
    def get_timestamp(self):
        return self.current_prices.get_timestamp(self.target_code)
    
    def get_trade_date(self):
        timestamp = self.get_timestamp()
        return timestamp.strftime("%Y-%m-%d")
    
    def update_filled_position(self, code, qty, is_buy, price, timestamp):
        position = self.get_position(code)
        position.event_fill(timestamp, is_buy, qty, price)
        self.strategy.event_position(self.positions)
        self.rpnl.loc[timestamp, "rpnl"] = position.realized_pnl
        print (self.get_trade_date(), 
               "Filled:", "Buy" if is_buy else "Sell", 
               qty, code, "at", price)
        
    def get_position(self, code):
        if code not in self.positions:
            position = Position()
            position.code = code
            self.positions[code] = position
        
        return self.positions[code]
    
    def eventhandle_order(self, order):
        self.filled_orders.append(order)
        
        print(self.get_trade_date(), 
              "Received order:", 
              "Buy" if order.is_buy else "Sell", order.qty, 
              order.code)
        
    def match_order_book(self, prices):
        if len(self.unfilled_orders) > 0:
            self.unfilled_orders = [order for order in self.unfilled_orders
                                    if self.is_order_unmatched(order, prices)]
            
    def is_order_unmatched(self, order, prices):
        code = order.code
        timestamp = prices.get_timestamp(code)
        
        if order.is_market_order and timestamp > order.timestamp:
            order.is_filled = True
            open_price = prices.get_open_price(code)
            order.filled_timestamp = timestamp
            order.filled_price = open_price
            self.update_filled_position(code, order.qty, order.is_buy, open_price, timestamp)
            self.strategy.event_order(order)
            return False
        return True
    
    def print_position_status(self, code, prices):
        if code in self.positions:
            position = self. positions[code]
            close_price = prices.get_last_price(code)
            position.update_unrealized_pnl(close_price)
            self.upnl.loc[self.get_timestamp(), "upnl"] = position.unrealized_pnl
            
            print(self.get_trade_date(), 
                  "Net:", position.net, 
                  "Value:", position.position_value, 
                  "Upnl:", position.unrealized_pnl, 
                  "Rpnl:", position.realized_pnl)
            
    def eventhandle_tick(self, prices):
        self.current_prices = prices
        self.strategy.event_tick(prices)
        self.match_order_book(prices)
        self.print_position_status(self.target_code, prices)
        
    def start_backtester(self):
        self.strategy = MyStrategy(self.target_code)
        self.strategy.event_sendorder = self.eventhandle_order
        
        mds = MarketDataSource()
        mds.event_tick = self.eventhandle_tick
        mds.ticker = self.target_code
        mds.start, mds.end = self.start_dt, self.end_dt
        
        print("Backtesting Started......")
        mds.start_market_simulation()
        print("Completed")
        
            




















    
