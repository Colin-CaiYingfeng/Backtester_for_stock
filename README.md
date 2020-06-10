# Backtester  
A stock backtest frame work.  
用于日频股票策略回测，数据来源Wind。
  
## Features
-----------
使用事件驱动引擎，模拟价格馈送、指令匹配、交易委托账本管理及账户头寸更新，用于防止`look-ahead bias`。  
  
### 1. TickData类  
   从市场数据源几首的单个数据单元，包括股票代码`code`，时间戳`timestamp`，开盘价`open_price`， 最终价格`last_price`， 总成交量`total_volume`。  
  
### 2. MarketData类  
   用于储存最终的tick数据，并支持检索数据。  
  
### 3. MarketDataSource类  
   从外部数据源获取市场历史数据，提供开始时间`start`， 结束时间`end`， 和股票代码`ticker`参数。  
   本框架使用Wind的api `WindPy`获取数据，并保存每日开盘价和收盘价，之后调用函数的`event_ticker`变量。  
   可以修改数据源为`Datareader`(`Google Finance`和`Yahoo! Finance`)、`tushare`等数据接口。  
  
### 4. Order类  
   模拟交易策略发送到服务器的委托。  
   每个指令应包含时间戳、编号、数量、价格和指令大小。  
   因为是做日频交易数据回测，所以仅采用市价指令，如果要做分钟级、tick级回测，可添加限价和日内止损指令。  
   指令完成后系统会更新成交时间、数量和价格。  
  
### 5. Position类  
   用于追踪当前的市场头寸和账户余额。  
   `position_value`变量用于描述账户头寸，初始值为可用现金余额，使用全局变量`start_position_value`作为初始输入。  
   买入股票时，证券价值计入该变量；卖出股票时，证券价值从该变量扣除。  
  
### 6. Stragety类  
   策略实现的基础。  
   当新的tick数据到达时，调用`event_tick`方法；头寸更新时调用`event_position`方法；策略发送order时，调用`send_market_order`方法。  
  
### 7. MyStragety类  
   继承自`Stragety`类。  
   用于编写自己的交易策略，每当新的tick传入，就作为dataframe的对象储存，`event_tick`方法随即被重写，执行交易逻辑决定以计算策略参数。  
   使用`lookback_intervals`储存数据，值表示最多储存前推多少天的数据。  
   定义`on_buy_signal`和`on_sell_signal`发出交易信号，变量应包含代码、数量和时间戳。  
  
### 8. Backtester类  
   回测实现的事件驱动引擎。  
   使用`start_backtest`方式初始化交易策略，`eventhandle_order`方法定义该策略的指令处理程序，设置并运行市场数据源函数。  
   接收数据时，使用eventhandle_tick方法处理数据并传入策略中。  
   之后调用`match_order_book`方法与`is_order_unmatch`方法，根据当前市场价格，匹配系统中的待成交指令。没有待成交指令时`is_order_unmatch`返回`True`，否则返回`False`。匹配指令时，调用`update_filled_position`方法更新头寸值，并通知`Strategy`对象更新头寸；匹配到指令之后，用`is_order_unmatched`方法通知`Strategy`对象。  
   
### 9. 运行回测系统  
   首先调用`start_backtest`方法。
   ``` python
   backtester = Backtester("code", dt.datetime(yyyy, m, d), dt.datetime(yyyy, m,d))
   backtester.start_backtest()
   ```  
     
   已实现的损益和浮动盈亏储存在rpnl和upnl中，两个变量都是dataframe类型。  
   可以绘制收益率曲线。
   ``` python
   import matplotlib.pyplot as plt
   return_rate = backtester.rpl / start_position_value
   return_rate.plot()
   plt.show()
   ```
   
