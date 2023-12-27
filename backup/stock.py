import yfinance as yf
from multiprocessing import Process
import csv

price_level = 3

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
	symbols = []
	with open('./symbols.csv', 'r') as f:
		reader = csv.reader(f, delimiter=',')
		for s in reader:
			return s

def get_data():
	global price_level
	raise_stock = {}
	drop_stock = {}
	symbols = load_symbols()
	for s in symbols:
		try:
			ticker = yf.Ticker(s)
			if ticker.info['country'] == 'United States':
				price_data = ticker.history(period="2d")
				print(s)
				if price_data['Volume'][0] > 0 and \
				   price_data['Volume'][1] > 0 and \
				   price_data['Close'][1] >= price_level:
					open_price = round(price_data['Open'][1], 2)
					high_price = round(price_data['High'][1],2)
					low_price = round(price_data['Low'][1], 2)
					close_price = round(price_data['Close'][1],2)
					if close_price > open_price:
						raise_stock[s] = {}
						raise_stock[s]['open'] = open_price
						raise_stock[s]['high'] = high_price
						raise_stock[s]['low'] = low_price
						raise_stock[s]['close'] = close_price
					if close_price < open_price:
						drop_stock[s] = {}
						drop_stock[s]['open'] = open_price
						drop_stock[s]['high'] = high_price
						drop_stock[s]['low'] = low_price
						drop_stock[s]['close'] = close_price
		except Exception as e:
			continue
	return raise_stock, drop_stock

def analyze_data():
	raise_stock, drop_stock = get_data()
	rss, dss = [],[]
	for symbol, price in raise_stock.items():
		close_open_delta = price['close'] - price['open']
		open_low_delta = price['open'] - price['low']
		high_close_delta = price['high'] - price['close']
		if open_low_delta > 0 and \
		   close_open_delta > 0 and \
		   high_close_delta > 0 and \
		   open_low_delta >= close_open_delta * 2 and \
		   high_close_delta < 0.2 * close_open_delta:
			rss.append(symbol)
	for symbol, price in drop_stock.items():
		open_close_delta = price['open'] - price['close']
		close_low_delta = price['close'] - price['low']
		high_open_delta = price['high'] - price['open']
		if open_close_delta > 0 and \
		   close_low_delta > 0 and \
		   high_open_delta > 0 and  \
		   close_low_delta >= open_close_delta * 2  and \
		   high_open_delta < 0.2 * open_close_delta:
			dss.append(symbol)
	return rss, dss

def main():
	rss, dss = analyze_data()
	if rss:
		with open('./green.txt', 'w') as f:
			for s in rss:
				f.write(s)
				f.write('\n')
	if dss:
		with open('./red.txt', 'w') as f:
			for s in dss:
				f.write(s)
				f.write('\n')

if __name__ == "__main__":
	main()
	
