import yfinance as yf

def sort_by_dividend_yield(tickers):
  # Retrieve financial data for each stock
  stock_data = {}
  for ticker in tickers:
    try:
      stock_info = yf.Ticker(ticker).info
    except:
      print('error1')
    if stock_info is not None:
      try:
        stock_data[ticker] = stock_info['dividendYield']
      except:
        print('error2')

  # Sort the stocks by dividend yield
  sorted_stocks = sorted(stock_data.items(), key=lambda x: x[1], reverse=True)

  # Extract the tickers from the sorted list
  sorted_tickers = [ticker for ticker, dividend_yield in sorted_stocks]

  return sorted_stocks

# Test the function with the sample array
tickers = ['ALB', 'BRO', 'TGT', 'ESS', 'MDT', 'SYY', 'NUE', 'ECL', 'VFC', 'SWK', 'WST', 'MMM', 'CLX', 'HRL', 'ADP', 'BF-B', 'GD', 'GPC', 'WMT', 'PEP', 'JNJ', 'MCD', 'CINF', 'ADM', 'CVX', 'XOM', 'TROW', 'CAH', 'AMCR', 'GWW', 'LOW', 'IBM', 'DOV', 'ABBV', 'WBA', 'O', 'FRT', 'CHD', 'CB', 'CL', 'ITW', 'ATO', 'KO', 'PNR', 'SPGI', 'MKC', 'CTAS', 'EXPD', 'ABT', 'SHW', 'BDX', 'AOS', 'ED', 'PPG', 'NEE', 'EMR', 'BEN', 'AFL', 'ROP', 'LIN', 'KMB', 'PG', 'CAT', 'APD']
sorted_stocks = sort_by_dividend_yield(tickers)

# Print each ticker and its dividend yield on a separate line
for ticker, dividend_yield in sorted_stocks:
  print(f"{ticker}: {dividend_yield}")
