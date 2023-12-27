# -*- coding: utf-8 -*-
import yfinance as yf
import multiprocessing
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
			symbols.append(s)
	return symbols

def formatting():
	sym = set()
	symbols = load_nasdaq()
	for e in symbols:
		if '^' in e:
			ek = e.split('^')[0]
			sym.add(ek.strip())
		elif '/' in e:
			ek = e.split('/')[0]
			sym.add(ek.strip())
		else:
			sym.add(e.strip())

	with open('./nasdaq.csv','w') as f:
		writer = csv.writer(f)
		writer.writerow(sym)			
				
def load_nasdaq():
	with open('./nasdaq.csv','r') as f:
		reader = csv.reader(f, delimiter=',')
		return(list(reader)[0])

def round_data(data):
	# price = [open, close, high, low]
	price = []
	for i in range(4, -1, -1):
		day = []
		for k in ['Open', 'Close', 'High', 'Low']:
			day.append(round(data[k].iloc[i], 2))
		price.append(day)
	return price

def get_data(s,stocks):
	"""
	stock = {   "day0": [open, close, high, low], 
	 			"day1": [open, close, high, low], 
	 			"day2": [open, close, high, low], 
	 			"day3": [open, close, high, low], 
	 			"day4": [open, close, high, low], 
	 }
	 """
	global price_level
	ticker = yf.Ticker(s)
	try:
		price_data = ticker.history(period="5d")
		if not price_data.empty:
			if price_data['Volume'].iloc[-1] > 0 and \
				price_data['Volume'].iloc[-2] > 0 and \
				price_data['Close'].iloc[-1] >= price_level:
					price = round_data(price_data)
					stocks[s] = {
								'day0': price[0],
								'day1': price[1],
								'day2': price[2],
								'day3': price[3],
								'day4': price[4]
					}
	except:
		pass

def get_t(stocks, post=True):
	t = []
	for s, stock_data in stocks.items():
		day0 = stock_data['day0']
		day1 = stock_data['day1']
		day2 = stock_data['day2']
		day3 = stock_data['day3']
		day4 = stock_data['day4']
		if day0[0] > day0[1]:
			index = 1
		if day0[0] < day0[1]:
			index = 0
		body = abs(day0[1]-day0[0])
		shadow = abs(day0[3]-day0[index])
		head = abs(day0[2]-day0[abs(index-1)])
		if post and day4[1] > day3[1] and \
			day3[1] > day2[1] and \
			day2[1] > day1[1] and \
			shadow >= body * 1.5 and \
			head < body * 0.5:
				t.append(s)
	return t


def get_dtts(stocks, post=True):
	DTTS=[]
	'''
	解读：
	1.股票在下跌回调过程中,  接近底部位置
	2.有一根绿K线实体, 把前一根红K的实体完全覆盖
	3.买盘成功扭转劣势, 多头绿K实体越长, 反转力度越强
	操作：
	1. 绿K的第二天成交量放大(很重要), 并且价格上涨（最好隔空上涨）， 多头攻势信号强劲。
	技术：
	1. 绿吃红， 高点破前高， 低点破前低
	2. 隔天要出量
	3. 出量的那一天， 高点有破， 低点没有破
	'''
	for s, stock_data in stocks.items():
		day0 = stock_data['day0']
		day1 = stock_data['day1']
		day2 = stock_data['day2']
		day3 = stock_data['day3']
		day4 = stock_data['day4']
		if post and day4[1] > day3[1] and \
			day3[1] > day2[1] and \
			day2[1] > day1[1] and \
			day0[1] > day0[0] and day1[1] < day1[0] and \
			day0[1] > day1[0] and day0[0] < day1[1] :
				DTTS.append(s)
		
	return DTTS

def save_to_file(dtts=None):
	_dtts = './dtts.txt'
	_t = './t.txt'
	if dtts:
		with open(_dtts, 'w') as f:
			for s in dtts[0]:
				f.write(s)
				f.write('\n')
		with open(_t, 'w') as f:
			for s in dtts[1]:
				f.write(s)
				f.write('\n')

def run():
	symbols = load_nasdaq()
	stocks = multiprocessing.Manager().dict()
	pool = multiprocessing.Pool(processes=5)
	pool.starmap(get_data, [(s, stocks) for s in symbols])
	pool.close()
	pool.join()
	DTTS = get_dtts(stocks)
	T = get_t(stocks)
	save_to_file(dtts=[DTTS,T])	
if __name__ == "__main__":
	run()