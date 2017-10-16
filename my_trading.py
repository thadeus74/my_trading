#!/usr/bin/python

########
### TRADING MODULE FOR CRYPTOCURRENCIES

### v0.8 - 2017-10-16 - added heading() to print a text with heading style
# added adv_print() to provide advanced printing with duplicate output to output.txt

# use init() function after importing the module, to retrieve currencies and portfolio
# use add_entry_to_ledger() function to populate the ledger
# use update_portfolio() function to update the portfolio, based on the ledger

### Functions to be developed:
###
### store temporary data in global variables, such as current and
### previous exchange rates, trends
### add an API key to retrieve info
### create classes for entries in portfolio and ledger

### Functions are of different kind:
### get (from internet), print (to screen), read (from file), save (to file)

### imported modules
import requests
import json
import csv
import time
import datetime

### variables defined here
preferred = ['BTC', 'XMR', 'LTC', 'XRP', 'DASH', 'BCC', 'ETH'] # first coin must be 'BTC'
# note that the codes are taken from bittrex, so Bitcoin is BTC and Bitcoin Cash is BCC
currency_rates = [] # stores rows of rates to be saved, format: [[r_coin, m_coin, eurbtc, current_date, current_time], ...]
currency_pairs = [] # stores pairs of coin codes and names, format: [[coin_code, coin_name], ...]
currency_codes = [] # stores coin codes, format:[coin1, coin2, ...]
portfolio = [] # stores a list of coins in the portfolio, format: [[coin, amount, rate, euroeq, percentage_of_portfolio], ...]
portfolio_total = 0 # stores the total amount of the porfolio in EUR
ledger = [] # stores a list of movements, format: [[COIN, AMOUNT, RATE, DATE], ...]
# e.g. [['EUR', -97.30, 1.00, '12/09/2017'], ...]
debug_verbose = False # change to True to print some debug info when running the functions
duplicate_output = True # allows adv_print to duplicate output to output.txt

### imports a list of currency codes and names traded in bittrex portal
def get_currency_pairs():
    """Get a list of currency codes and names from bittrex.com"""
    # variables used by function
    key1 = 'Currency'
    key2 = 'CurrencyLong'
    url ='https://bittrex.com/api/v1.1/public/getcurrencies'
    global currency_pairs
    global currency_codes
    # retrieving currency list
    try :
        page = requests.get(url)
    except :
        print('\nException retrieving currencies from bittrex.com\n')
        read_currency_pairs()
    else :
        page_content = json.loads(page.content)
        result = page_content['result']
        # creating a list of pairs [coin code, name]
        currency_pairs = [[x.get(key1, None), x.get(key2, None)] for x in result]
        currency_pairs.append(['EUR', 'Euro'])
        # creating a list of coin codes
        currency_codes = [x.get(key1, None) for x in result]
        currency_codes.append('EUR')
        print ('{0} cryptocurrencies retrived from the database of bittrex.com'.format(len(currency_codes)))

def save_currency_pairs():
    """Save currency pairs retrived with .get_currency_pairs() function in a csv file"""
    ### currency_pairs.csv format: code, name
    with open('currency_pairs.csv', 'w', newline = '') as csvfile:
        spamwriter = csv.writer(csvfile)
        for row in currency_pairs:
            spamwriter.writerow(row)

def read_currency_pairs():
    """Read historical currency pairs from currency_pairs.csv file"""
    # variables
    global currency_pairs
    global currency_codes
    currency_pairs = []
    currency_codes = []
    filename = 'currency_pairs.csv'
    i=0
    ### reading from currency_pairs.csv format: code, name
    with open(filename, 'r', newline = '') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            currency_pairs.append(row)
            i=i+1
    currency_pairs.append(['EUR', 'Euro'])
    # creating a list of coin codes
    currency_codes = [x[0] for x in currency_pairs]
    currency_codes.append('EUR')
    print ('{0} cryptocurrencies read from {1}'.format(i, filename))

### get a ticker for a pair of currencies
def get_ticker(coin1, coin2):
    """Get a ticker for a pair of currencies, when this cant' be retrieved, it returns 0."""
    if coin2 == 'EUR' :
        if coin1 == 'BTC' :
            ## retrieve Bitcoin to Euro exchange rate from coindesk.com
            url = 'https://api.coindesk.com/v1/bpi/currentprice/EUR.json'
            try :
                page = requests.get(url)
            except :
                print('\nException retrieving ticker from coindesk.com\n')
                return 0
            else :
                page_content = json.loads(page.content)
                info = page_content.get('bpi')
                info = info.get('EUR')
                info = info.get('rate_float', None)
                return info
        elif coin1 == 'EUR' :
            return 1
        else :
            return get_ticker(coin1, 'BTC') * get_ticker('BTC', coin2);
    elif coin2 == 'BTC' :
        url = 'https://bittrex.com/api/v1.1/public/getticker?market=' + coin2 + '-' + coin1
        try :
            page = requests.get(url)
        except :
            print('\nException retrieving ticker from bittrex.com\n')
            return 0
        else :
            page_content = json.loads(page.content)
            success = page_content['success']
            if success :
                ticker = page_content['result']
                return ticker.get('Last', None)
            else :
                return 0
    else :
        return 0;

### get the previous day exchange rate for a pair of currencies
def get_previous_day(coin1, coin2):
    """Get the previous day closure exchange rate for a pair of currencies,
    when it can't be retrieved, it returns 0."""
    if coin2 == 'EUR' :
        if coin1 == 'BTC' :
            ## retrieve Bitcoin to Euro exchange rate from coindesk.com
            url = 'https://api.coindesk.com/v1/bpi/historical/close.json?currency=EUR&for=yesterday'
            try :
                page = requests.get(url)
            except :
                print('\nException retrieving info about previous day from coindesk.com\n')
                return 0
            else :
                page_content = json.loads(page.content)
                info = page_content.get('bpi')
                yesterday=(datetime.date.today()-datetime.timedelta(1)).isoformat()
                info = info.get(yesterday, None)
                return info
        elif coin1 == 'EUR' :
            return 1
        else :
            return get_previous_day(coin1, 'BTC') * get_previous_day('BTC', coin2);
    elif coin2 == 'BTC' :
        url = 'https://bittrex.com/api/v1.1/public/getmarketsummary?market={0}-{1}'.format(coin2, coin1)
        if debug_verbose :
            print (url)
        try :
            page = requests.get(url)
        except :
            print('\nException retrieving info about previous day from bittrex.com\n')
            return 0
        else :
            page_content = json.loads(page.content)
            success = page_content['success']
            if success :
                ticker = page_content['result'][0]
                return ticker.get('PrevDay', None)
            else :
                return 0
    else :
        return 0;

### print a ticker for a pair of currencies
def print_ticker(coin1, coin2):
	"""Print a ticker for a pair of currencies"""
	ticker = get_ticker(coin1, coin2)
	if ticker == False :
		print('No match found for {0} and {1}'.format(coin1, coin2))
	else :
	    print('{0:6} - {1:4} ==> Last: {2:.5f}'.format(coin1, coin2, ticker))
	return;

### import and print a list of currencies traded in bittrex portal
def get_currency_rates(max_coins = 6, preference = False):
    """Get the list of the first 'max_coins' currencies and their last exchange value against 'r_coin'."""
    ### variables used by function
    r_coin = 'BTC'
    m_coin = 'EUR'
    global preferred
    global currency_rates
    global currency_codes
    ### retrieving a list of coins
    if preference :
        interesting_coins = preferred[1:max_coins]
    else :
        get_currency_pairs()
        interesting_coins = currency_codes[1:max_coins]
    ### retrieving the last exhange values between each currency and EUR
    print('List of last exchange rate between each coin and {0}:'.format(m_coin))
    eurbtc = get_ticker(r_coin, m_coin)
    print('{3:.<12}: {0:>6}-{1:3} ==> Last: {2:10.5f}'.format(r_coin, m_coin, eurbtc, currency_name(r_coin)))
    current_date = datetime.date.today().isoformat()
    current_time = time.strftime('%X')
    currency_rates =[[r_coin, m_coin, eurbtc, current_date, current_time]]
    for coin in interesting_coins :
        a = get_ticker(coin, r_coin)
        if a == False :
            print('No match found for ' + coin + ' and ' + r_coin)
        else :
            print('{3:.<12}: {0:>6}-{1:3} ==> Last: {2:10.5f}'.format(coin, m_coin, a*eurbtc, currency_name(coin)))
            currency_rates.append([coin, m_coin, a*eurbtc, current_date, current_time])

### import a list of currencies traded in bittrex portal with their current rates
def get_current_rates(max_coins = 6, preference = False):
    """Get the list of the first 'max_coins' currencies and their last exchange value against 'r_coin'."""
    #
    ### variables used by function
    r_coin = 'BTC'
    m_coin = 'EUR'
    global preferred
    global currency_rates
    global currency_codes
    ### retrieving a list of coins
    if preference :
        interesting_coins = preferred[1:max_coins]
    else :
        get_currency_pairs()
        interesting_coins = currency_codes[1:max_coins]
    #
    ### retrieving the last exhange values between each currency and EUR
    eurbtc = get_ticker(r_coin, m_coin)
    current_date = datetime.date.today().isoformat()
    current_time = time.strftime('%X')
    currency_rates =[[r_coin, m_coin, eurbtc, current_date, current_time]]
    for coin in interesting_coins :
        a = get_ticker(coin, r_coin)
        if a != False :
            currency_rates.append([coin, m_coin, a*eurbtc, current_date, current_time])

### print a list of currencies traded in bittrex portal
def print_current_rates():
	"""Print the list of currencies and rates retrieved with get_current_rates()"""
	#
	### variables used by function
	global currency_rates
	#
	### print the last exhange values 
	print('Below is the list of last exchange rates:')
	for row in currency_rates :
            coin = row[0]
            m_coin = row[1]
            rate = row[2]
            print('{3:.<12}: {0:>6}-{1:3} ==> Last: {2:10.5f}'.format(coin, m_coin, rate, currency_name(coin)))

def currency_name(code):
	"""Return a currency name, given the code"""
	global currency_pairs
	for c in currency_pairs:
		if c[0] == code:
			return c[1]
	return 'No match';

def print_preferred_coins():	
    """Print a list of preferred currencies in a code name pair"""
    global preferred
    output = ''
    for i in preferred:
        output = output + '{0:6} - {1:20}\n'.format(i, currency_name(i))
    print(output);

def save_rates(coin1 = None, coin2 = None, wa = 'a'):
    """Save currency rates retrived with .get_currency_rates() function in a csv file"""
    # variables
    global currency_rates
    if wa == 'w' :
        if input('Are you sure you want to overwrite the file? (y/n)') == 'y':
            print('Nothing has been saved to file.')
            return
    if coin1 == None :
        filename = 'historical.csv'
        ### historical.csv format: coin, m_coin, rate, date, time
        with open(filename, 'a', newline = '') as csvfile :
            spamwriter = csv.writer(csvfile)
            for row in currency_rates:
                spamwriter.writerow(row)
    else :
        if coin2 == None :
            coin2 = 'EUR'
        filename = coin1.lower() + '-' + coin2.lower() + '.csv'
        ### coin1-coin2.csv format: coin, m_coin, rate, date, time
        with open(filename, wa, newline = '') as csvfile :
            spamwriter = csv.writer(csvfile)
            for row in currency_rates:
                if row[0] == coin1:
                    if row[1] == coin2:
                        spamwriter.writerow(row)
    print('Saved to {0}.'.format(filename));

def read_rates():
    """Read historical currency rates from historical.csv file"""
    # variables
    global currency_rates
    currency_rates = []
    ### historical.csv format: coin, m_coin, rate, date, time
    with open('historical.csv', 'r', newline = '') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            a = row[0:2]+[eval(row[2])]+row[3:5]
            currency_rates.append(a)

def print_historical(coin = None):
    """Show historical data for a specific currency"""
    # variables
    global currency_rates
    # if not yet read, then read rates from file
    if currency_rates == []:
        read_rates()
    # if coin not specified, then ask
    if coin == None:
        b = input("Type the currency you want to retrive (e.g. 'BTC') --> ")
    else:
        b = coin
    # look for records of a specific coin
    print('Trend is: {0:>+7.2%}'.format(trend(coin)));

def trend(coin1, coin2 = 'EUR', formatting = 'percentage'):
    """Returns the current trend of a specific pair of currencies,
    with reference to the closure of yesterday.
    (default of coin2 is 'EUR')"""
    previous = get_previous_day(coin1, coin2)
    # if the previous day con't be retrieved, then return 0 or 'N/A'
    if previous == 0 :
        if debug_verbose :
            print('previous day is 0')
        if formatting == 'percentage':
            return 0
        else :
            return 'N/A'
    current = get_ticker(coin1, coin2)
    tr = (current - previous) / previous
    going = None
    if formatting == 'percentage':
        return tr
    else :
        if tr > 0:
            going = 'up'
        elif tr == 0:
            going = 'steady'
        else :
            going = 'down'
        return going;

def print_preferred_trend():
    """print the trend of preferred currencies"""
    ### variables
    global preferred
    output = 'Trend of the preferred currencies:\nCoin   - Name         |   Trend'
    for i in preferred:
        output = output + '{0:6} - {1:13}: {2:>+7.2%}\n'.format(i, currency_name(i), trend(i))
    print(output)

def print_currencies_trend():
    """print the trend of the currencies being retrieved"""
    ### variables
    global currency_rates
    output = 'Trend of the currencies being retrieved:\nCoin   - Name         |   Trend'
    for row in currency_rates:
        i = row[0]
        output = output + '{0:6} - {1:13}: {2:>+7.2%}\n'.format(i, currency_name(i), trend(i))
    print(output)
  
def save_portfolio():
    """Save portfolio in portfolio.csv file"""
    # variables
    global portfolio
    filename = 'portfolio.csv'
    ### portfolio.csv format: coin, amount, rate, euroeq, perc_of_portfolio
    with open(filename, 'w', newline = '') as csvfile :
        spamwriter = csv.writer(csvfile)
        for row in portfolio:
                spamwriter.writerow(row)
    print('Portfolio saved to {0}.'.format(filename));

def read_portfolio(verbose = 'yes_print'):
    """Read portfolio from portfolio.csv file"""
    # variables
    global portfolio
    portfolio = []
    filename = 'portfolio.csv'
    ### portfolio.csv format: coin, amount, rate, euroeq, perc_of_portfolio
    if verbose == 'yes_print':
        print('Portfolio:\nCoin   - Name         |   Amount')
    with open(filename, 'r', newline = '') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            coin = row[0]
            amount = eval(row[1])
            rate = eval(row[2])
            euroeq = eval(row[3])
            perc_of_portfolio = eval(row[4])
            portfolio.append([coin, amount, rate, euroeq, perc_of_portfolio])
            if verbose == 'yes_print':
                print('{0:6} - {1:13}| {2:10.5f}'.format(coin, currency_name(coin), amount))
    print('Portfolio read from {0}.'.format(filename));

def print_balance(update = True):
    """Print balance of portfolio, based in Euro.
    update = True to retrieve updated exchange rates,
    update = False to use stored exchange rates."""
    # variables
    global portfolio
    global portfolio_total
    output = heading('Portfolio Balance')
    if portfolio == []:
        try :
            read_portfolio('no_print')
        except :
            print('No portfolio present yet.')
    # this first iteration is to compute portofolio_total, which will be used later to compute percentage
    portfolio_total = 0
    for row in portfolio:
        coin = row[0]
        amount = row[1]
        rate = row[2]
        if update == True or rate == 0:
            rate = get_ticker(coin, 'EUR')
            row[2] = rate
        euroeq = amount * rate
        row[3] = euroeq
        portfolio_total = portfolio_total + euroeq
    output = output + 'Coin  - Name         |   Amount   |   Rate    |   Trend |  Equiv.    | Port.%\n'
    for row in portfolio:
        coin = row[0]
        amount = row[1]
        rate = row[2]
        euroeq = row[3]
        perc_of_portfolio = euroeq / portfolio_total
        row[4] = perc_of_portfolio
        output = output + '{0:6}- {1:13}| {2:10.5f} | {3:9.4f} | {4:>+8.2%}| € {5:8.2f} | {6:>6.2%}\n' \
              .format(coin, currency_name(coin), amount, rate, trend(coin), euroeq, perc_of_portfolio)
    output = output + 'Total: € {0:7.2f}\n'.format(portfolio_total)
    if portfolio != []:
        adv_print(output)
        save_portfolio()

def add_entry_to_ledger(coin, amount, rate, date = ''):
    """Add an entry to the ledger. Date is in the format yyyy-mm-dd"""
    # variables
    filename = 'ledger.csv'
    if date == '':
        date = datetime.date.today().isoformat()
    ### ledger.csv format: coin, amount, rate, date
    rowl = [coin.upper(), amount, rate, date]
    with open(filename, 'a', newline = '') as csvfile :
        spamwriter = csv.writer(csvfile)
        spamwriter.writerow(rowl)
    print('Added entry to {0}.'.format(filename));
    update_portfolio(rowl, False)
    
def read_ledger():
    """Read ledger from ledger.csv"""
    # variables
    global ledger
    ledger = []
    filename = 'ledger.csv'
    ### ledger.csv format: coin, amount, rate, date
    with open(filename, 'r', newline = '') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            a = row[0:1]+[eval(row[1])]+[eval(row[2])]+[row[3]]
            ledger.append(a)
    print('Ledger read from {0}.'.format(filename))

def update_portfolio(single_entry = None, confirm_write = False):
    """Update portfolio using ledger entries"""
    # portfolio format: [coin, amount, rate, euroeq, percentage_of_portfolio]
    # ledger format: [coin, amount, rate, date]
    if confirm_write:
        if input('This operation will overwrite all previous data stored in portfolio.csv. Ok (y/n)?') == 'n':
            print ('Portfolio not updated.')
            return;
    global portfolio
    global ledger
    if single_entry == None:
        portfolio = []
        for rowl in ledger:
            # find the correct item in portfolio
            coin = rowl[0]
            found = False
            for rowp in portfolio:
                if rowp[0] == coin:
                    found = True
                    # update the item in portfolio
                    rowp[1] = rowp[1] + rowl[1]
            if found == False:
                portfolio.append(rowl[0:2]+[0,0,0])
    else:
        rowl = single_entry
        # find the correct item in portfolio
        coin = rowl[0]
        found = False
        for rowp in portfolio:
            if rowp[0] == coin:
                found = True
                # update the item in portfolio
                rowp[1] = rowp[1] + rowl[1]
        if found == False:
            portfolio.append(rowl[0:2]+[0,0,0])
    save_portfolio()
    
def analyze_positions(summary = 'collapsed'):
    """Analize the open and closed positions in the portfolio"""
    # this first version is 'collapsed' and computes a sum of all the entries
    # related to a certain currency, it does not consider each closure of a position
    # but only the final balance

    # portfolio format: [coin, amount, rate, euroeq, percentage_of_portfolio]
    # ledger format: [coin, amount, rate, date]
    # analysis format: [coin, amount, euroeq, date]
    global portfolio
    global ledger
    output = heading('Analysis of positions')
    analysis = []
    for rowl in ledger:
        coin = rowl[0]
        found = False
        # find the correct item in analysis
        for rowa in analysis:
            if rowa[0] == coin:
                found = True
                # update the item in analysis
                rowa[1] = rowa[1] + rowl[1]
                rowa[2] = rowa[2] + rowl[1] * rowl[2]
                rowa[3] = rowl[3]
        if found == False:
            analysis.append(rowl[0:2]+[rowl[1] * rowl[2]] + [rowl[3]])
    # first ouput closed positions
    output = output + 'Closed positions:\n'
    output = output + 'Coin  - Name         |   Closed   |   P/L \n'
    for rowa in analysis:
        if rowa[1] == 0:
            output = output + '{0:6}- {1:13}| {2} | € {3:>+8.2f}\n' \
                     .format(rowa[0], currency_name(rowa[0]), rowa[3], -rowa[2])
    # the output open positions
    output = output + '\nOpen positions:\n'
    output = output + 'Coin  - Name         |   Amount   |   P/L \n'
    for rowa in analysis:
        if rowa[1] != 0:
            pl = rowa[1] * get_ticker(rowa[0], 'EUR') - rowa[2]
            output = output + '{0:6}- {1:13}| {2:>10.5f} | € {3:+8.2f}\n' \
                     .format(rowa[0], currency_name(rowa[0]), rowa[1], pl)
    adv_print(output)
    
def heading(text, heading_level = 1, length = 40):
    """Print a text formatted as a specific heading"""
    ### currently implemented heading level 1 only
    output = '┌' + '-' * (length - 2) + '┐\n'
    output = output + '| ' + text + ' ' * (length - len(text) - 3) + '|\n'
    output = output + '└' + '-' * (length - 2) + '┘\n\n'
    return output

def adv_print(text):
    global duplicate_output
    print(text)
    if duplicate_output:
        with open("Output.txt", "a") as text_file:
            text_file.write(text)

def init():
    """Initialize the module variables, read ledger, read portfolio and print balance"""
    get_currency_pairs()
    global ledger
    try :
        read_ledger()
    except :
        print('No ledger present yet.')
    print_balance(True)

def daily_routine():
    """Performs a serie of functions togheter, for a daily routine. Ledger must be already present."""
    get_currency_pairs()
    read_ledger()
    print_balance(True)
    analyze_positions(True)

    
