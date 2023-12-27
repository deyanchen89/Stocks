import yfinance as yf
import multiprocessing
from multiprocessing import Process
import csv

price_level = 1

def load_files():
	files = ['./NASDAQ.txt','NYSE.txt','AMEX.txt']
	symbols = []
	for file in files:
		with open(file) as f:
			lines = f.readlines()
			for l in lines[1:]:
				s = l.split()[0]
				ticker = yf.Ticker(s)
				price = ticker.history(period='2d')
				if len(price) == 2:
					symbols.append(s)
	with open('./symbols.csv','w') as f:
		writer = csv.writer(f)
		writer.writerow(symbols)

def load_symbols():
	with open('./symbols.csv', 'r') as f:
		reader = csv.reader(f, delimiter=',')
		for s in reader:
			return s

def load_nasdaq():
	symbols = []
	with open('./nasdaq.csv') as f:
		reader = csv.reader(f, delimiter=',')
		for s in reader:
			if s[0] != 'Symbol':
				symbols.append(s[0])
	return symbols

def analyze_data(s,raise_stock, drop_stock):
	print(s)
	global price_level
	ticker = yf.Ticker(s)
	try:
		price_data = ticker.history(period="2d")
		if price_data['Volume'].iloc[0] > 0 and \
			price_data['Volume'].iloc[1] > 0 and \
			price_data['Close'].iloc[1] >= price_level:
				open_price = round(price_data['Open'].iloc[-1], 2)
				high_price = round(price_data['High'].iloc[-1],2)
				low_price = round(price_data['Low'].iloc[-1], 2)
				close_price = round(price_data['Close'].iloc[-1],2)
				if close_price > open_price: 
					close_open_delta = close_price - open_price
					open_low_delta = open_price - low_price
					high_close_delta = high_price - close_price
					if open_low_delta > 0 and \
						close_open_delta > 0 and \
						high_close_delta > 0 and \
						open_low_delta >= close_open_delta * 2 and \
						high_close_delta < 0.2 * close_open_delta:
						raise_stock.append(s)
				if close_price < open_price:
					open_close_delta = open_price - close_price
					close_low_delta = close_price - low_price
					high_open_delta = high_price - open_price
					if open_close_delta > 0 and \
						close_low_delta > 0 and \
						high_open_delta > 0 and  \
						close_low_delta >= open_close_delta * 2  and \
						high_open_delta < 0.2 * open_close_delta:
						drop_stock.append(s)
	except:
		pass

def save_to_file(rss, dss):
	green = './green.txt'
	red = './red.txt'
	if rss:
		with open(green, 'w') as f:
			for s in rss:
				f.write(s)
				f.write('\n')
	if dss:
		with open(red, 'w') as f:
			for s in dss:
				f.write(s)
				f.write('\n')

def run():
	symbols = load_symbols()
	raise_stock = multiprocessing.Manager().list()
	drop_stock = multiprocessing.Manager().list()
	pool = multiprocessing.Pool(processes=5)
	pool.starmap(analyze_data, [(s, raise_stock, drop_stock) for s in symbols])
	pool.close()
	pool.join()
	print('raise_stock: ', raise_stock, '\n')
	print('drop_stock: ', drop_stock)
	save_to_file(raise_stock, drop_stock)	
if __name__ == "__main__":
	run()
	
