#!/usr/bin/python

##################
# TRADING MODULE FOR CRYPTOCURRENCIES
##################
#
# HOW TO USE THIS MODULE:
# use init() function after importing the module, to retrieve currencies and portfolio
# use add_entry_to_ledger() function to populate the ledger
# use update_portfolio() function to update the portfolio, based on the ledger
#
# Functions are of different kind:
# get (from internet), print (to screen), read (from file), save (to file)
# additional functions to duplicate print to file and to generate headers

# v0.11 - 20/10
# - added cached_previous() to avoid requesting a data already collected

# Functions to be developed:
#
# historical.csv could get very big, so it should store values of a specific period (e.g. month)
# store temporary data in global variables, such as current and
# previous exchange rates, trends
# add an API key to retrieve info
# create classes for entries in portfolio and ledger
# it might be useful to have also yesterday trend

# imported modules used in the functions of this module
import requests
import json
import csv
import time
import datetime

# global variables defined here can be modified:
# note that the codes are taken from bittrex, so Bitcoin is BTC and Bitcoin Cash is BCC
preferred = ['BTC', 'XMR', 'LTC', 'XRP', 'DASH', 'BCC', 'ETH'] # first coin must be 'BTC'
duplicate_output = True # allows adv_print to duplicate output to output.txt

# global variables defined here are used to store temporary data for the functions:
currency_rates = [] # stores rows of rates to be saved, format: [[coin1, 'EUR', eurbtc, current_date, current_time], ...]
currency_pairs = [] # stores pairs of coin codes and names, format: [[coin_code, coin_name], ...]
currency_codes = [] # stores coin codes, format:[coin1, coin2, ...]
currency_cache = [] # format [[code, name, current, previous, trend], ...]
portfolio = [] # stores a list of coins in the portfolio, format: [[coin, amount, rate, euroeq, percentage_of_portfolio], ...]
portfolio_total = 0 # stores the total amount of the porfolio in EUR
ledger = [] # stores a list of movements, format: [[COIN, AMOUNT, RATE, DATE], ...]
# e.g. [['EUR', -97.30, 1.00, '12/09/2017'], ...]
currency_trends = [] # format [[trend, coin], ...]
r_coin = 'BTC'
m_coin = 'EUR'
internet_state = 'online'

### imports a list of currency codes and names traded in bittrex portal
def get_currency_pairs():
    """Get a list of currency codes and names from bittrex.com"""
    # variables used by function
    key1 = 'Currency'
    key2 = 'CurrencyLong'
    url ='https://bittrex.com/api/v1.1/public/getcurrencies'
    global currency_pairs
    global currency_codes
    # check if online or offline
    global internet_state
    if internet_state == 'offline':
        read_currency_pairs()
        return
    # retrieving currency list
    try :
        page = requests.get(url)
    except :
        print('\nCurrently cannot get currencies from bittrex.com\n')
        internet_state = 'offline'
        read_currency_pairs()
    else :
        page_content = json.loads(page.content)
        result = page_content['result']
        # creating a list of pairs [coin code, name]
        currency_pairs = [[x.get(key1, None), x.get(key2, None)[:13]] for x in result]
        currency_pairs.append(['EUR', 'Euro'])
        # creating a list of coin codes
        currency_codes = [x.get(key1, None) for x in result]
        currency_codes.append('EUR')
        print ('{0} cryptocurrencies retrived from the database of bittrex.com'.format(len(currency_codes)))
        save_currency_pairs()

def save_currency_pairs():
    """Save currency pairs retrived with .get_currency_pairs() function in a csv file"""
    ### currency_pairs.csv format: code, name
    filename = 'currency_pairs.csv'
    with open(filename, 'w', newline = '') as csvfile:
        spamwriter = csv.writer(csvfile)
        for row in currency_pairs:
            spamwriter.writerow(row)
    print ('{0} cryptocurrencies codes and names written to {1}'.format(len(currency_pairs), filename))

def read_currency_pairs():
    """Read currency pairs from currency_pairs.csv file"""
    global currency_pairs
    global currency_codes
    currency_pairs = []
    currency_codes = []
    filename = 'currency_pairs.csv'
    ### reading from currency_pairs.csv format: code, name
    with open(filename, 'r', newline = '') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            currency_pairs.append(row)
    currency_pairs.append(['EUR', 'Euro'])
    # creating a list of coin codes
    currency_codes = [x[0] for x in currency_pairs]
    currency_codes.append('EUR')
    print ('{0} cryptocurrencies read from {1}'.format(len(currency_pairs), filename))

def cached_ticker(coin1, coin2 = 'EUR'):
    """check if there is in cache a value for the ticker in the last n minutes"""
    #variables
    global currency_rates
    # currency_rates format: [[coin1, coin2, rate, current_date, current_time], ...]
    global current_date
    global current_time
    current_date = datetime.date.today().isoformat()
    a = time.strftime('%X')
    try :
        current_sec = eval(a[0:2])*60*60+eval(a[3:5])*60+eval(a[6:8])
    except:
        current_sec = 0
    for row in currency_rates:
        if row[3] == current_date:
            if row[0] == coin1:
                if row[1] == coin2:
                    a = row[4]
                    try:
                        b = eval(a[0:2])*60*60+eval(a[3:5])*60+eval(a[6:8])-900
                    except:
                        b = 86400
                    if current_sec > b:
                        return row[2]
    return 0        

def get_ticker(coin1, coin2 = 'EUR'):
    """Get a ticker for a pair of currencies, when this can't be retrieved, it returns 0.
    When the internet_state is offline, it uses the information from latest_rate()."""
    # check if this is EUR identity
    if coin1 == 'EUR' and coin2 == 'EUR' :
        return 1
    # check if the coin1 is exchanged in bittrex market
    if currency_name(coin1) == 'No match':
        return -1
    # check if online or offline
    global internet_state
    if internet_state == 'offline':
        return latest_rate(coin1)
    # check if there is a chached value of the last 15 minutes
    ca = cached_ticker(coin1, coin2)
    if ca > 0 :
        return ca
    #variables
    global currency_rates
    global current_date
    global current_time
    current_date = datetime.date.today().isoformat()
    current_time = time.strftime('%X')
    if coin2 == 'EUR' :
        if coin1 == 'BTC' :
            ## retrieve Bitcoin to Euro exchange rate from coindesk.com
            url = 'https://api.coindesk.com/v1/bpi/currentprice/EUR.json'
            try :
                page = requests.get(url)
            except :
                print('Cannot retrieve ticker from coindesk.com')
                internet_state = 'offline'
                return 0
            else :
                page_content = json.loads(page.content)
                info = page_content.get('bpi')
                info = info.get('EUR')
                ticker = info.get('rate_float', None)
                currency_rates.append([coin1, coin2, ticker, current_date, current_time])
                return ticker
        else :
            return get_ticker(coin1, 'BTC') * get_ticker('BTC', coin2);
    elif coin2 == 'BTC' :
        url = 'https://bittrex.com/api/v1.1/public/getticker?market=' + coin2 + '-' + coin1
        try :
            page = requests.get(url)
        except :
            print('Cannot retrieve ticker from bittrex.com')
            internet_state = 'offline'
            return 0
        else :
            page_content = json.loads(page.content)
            success = page_content['success']
            if success :
                ticker = page_content['result']
                try :
                    ticker = ticker.get('Last', None)
                    currency_rates.append([coin1, coin2, ticker, current_date, current_time])
                except:
                    ticker = 0
                return ticker
            else :
                return 0
    else :
        return 0;

def cached_previous(coin1, coin2 = 'EUR'):
    """check if there is in cache a value for the previous day closure"""
    #variables
    global currency_rates
    # currency_rates format: [[coin1, coin2, rate, current_date, current_time], ...]
    yesterday=(datetime.date.today()-datetime.timedelta(1)).isoformat()
    for row in currency_rates:
        if row[3] == yesterday:
            if row[0] == coin1:
                if row[1] == coin2:
                    # print (coin1,coin2,'cached')
                    return row[2]
    # print (coin1,coin2,'not cached yet')
    return 0        

### get the previous day exchange rate for a pair of currencies
def get_previous_day(coin1, coin2 = 'EUR'):
    """Get the previous day closure exchange rate for a pair of currencies,
    when it can't be retrieved, it returns 0."""
    # check if this is EUR identity
    if coin1 == 'EUR' and coin2 == 'EUR' :
        return 1
    # check if online or offline
    global internet_state
    if internet_state == 'offline':
        return 0
    #check if already cached
    c = cached_previous(coin1,coin2)
    if c:
        return c
    # variables
    global currency_rates
    yesterday = (datetime.date.today()-datetime.timedelta(1)).isoformat()
    # check coins
    if coin2 == 'EUR' :
        if coin1 == 'BTC' :
            ## retrieve Bitcoin to Euro exchange rate from coindesk.com
            url = 'https://api.coindesk.com/v1/bpi/historical/close.json?currency=EUR&for=yesterday'
            try :
                page = requests.get(url)
            except :
                print('Cannot retrieve info about previous day from coindesk.com')
                return 0
            else :
                page_content = json.loads(page.content)
                info = page_content.get('bpi')
                info = info.get(yesterday, None)
                currency_rates.append([coin1, coin2, info, yesterday, '23:59:59'])
                return info
        else :
            return get_previous_day(coin1, 'BTC') * get_previous_day('BTC', coin2);
    elif coin2 == 'BTC' :
        url = 'https://bittrex.com/api/v1.1/public/getmarketsummary?market={0}-{1}'.format(coin2, coin1)
        try :
            page = requests.get(url)
        except :
            print('Cannot retrieve info about previous day from bittrex.com')
            return 0
        else :
            page_content = json.loads(page.content)
            success = page_content['success']
            if success :
                ticker = page_content['result'][0]
                info = ticker.get('PrevDay', None)
                currency_rates.append([coin1, coin2, info, yesterday, '23:59:59'])
                return info
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
    # variables
    global current_date
    global currency_rates
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
    ### print the last exhange values 
    output = heading ('Last exchange rates')
    output += 'Coin          |  Market    | Last exchange rate\n'
    output += '--------------+------------+-------------------\n'
    for row in currency_rates :
        coin1 = row[0]
        coin2 = row[1]
        rate = row[2]
        output += '{3:.<13}| {0:>6}-{1:3} | Last: {2:10.5f}\n'.format(coin1, coin2, rate, currency_name(coin1))
    output += '--------------+------------+-------------------\n'
    adv_print(output)

def currency_name(code):
    """Return a currency name, given the code"""
    if currency_pairs == []:
        get_currency_pairs()
    for c in currency_pairs:
        if c[0] == code:
            return c[1]
    return 'No match';

def print_preferred_coins():	
    """Print a list of preferred currencies in a code name pair"""
    if currency_pairs == []:
        print('Retrieving currency pairs first.')
        get_currency_pairs()
    output = heading('Preferred coins')
    output += 'Coin   | Name        \n'
    output += '-------+-------------\n'
    for i in preferred:
        output += '{0:6} | {1:20}\n'.format(i, currency_name(i))
    output += '-------+-------------\n'
    print(output);

def save_rates(coin1 = None, coin2 = 'EUR', wa = 'a'):
    """Save currency rates retrived with .get_currency_rates() function in a csv file"""
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
    # if not yet read, then read rates from file
    if currency_rates == []:
        read_rates()
    # if coin not specified, then ask
    if coin == None:
        coin1 = input("Type the currency you want to retrive (e.g. 'BTC') --> ").upper()
    else:
        coin1 = coin
    # look for records of a specific coin
    # currency_rates format: [[coin1, coin2, eurbtc, current_date, current_time], ...]
    output = heading ('Historical exchange rates')
    output += 'Date: {0}\n'.format(datetime.date.today().isoformat())
    output += 'Coin: {0:6} - {1:20}\n'.format(coin1, currency_name(coin1))
    output += '   Market   | Exch. rate |    Date    |  Time\n'
    output += '------------+------------+------------+---------\n'
    i = 0
    for row in currency_rates :
        if coin1 == row[0] :
            i += 1
            coin2 = row[1]
            rate = row[2]
            output += ' {0:>6}-{1:3} | {2:10.5f} | {3} | {4}\n'.format(row[0], coin2.upper(), rate, row[3], row[4])
    output += '------------+------------+------------+---------\n'
    if i == 0:
        print('No historical values stored for coin: {0:6} - {1:20}'.format(coin1, currency_name(coin1)))
        return
    if internet_state == 'online':
        output += 'Trend is: {0:>+7.2%}\n'.format(trend(coin1))
    else :
        output += 'Offline mode, trend not available.\n'
    adv_print(output)

def latest_rate(coin1, coin2 = 'EUR'):
    """get the latest rate stored for a certain pair of coins"""
    # variables used here
    last = -1
    i = -1
    # if not yet read, then read rates from file
    if currency_rates == [] :
        read_rates()
    for row in currency_rates :
        i = i + 1
        if coin1 == row[0] :
            last = i
    if last == -1:
        return 0
    else:
        return currency_rates[last][2]

def trend(coin1, coin2 = 'EUR', formatting = 'percentage'):
    """Returns the current trend of a specific pair of currencies,
    with reference to the closure of yesterday."""
    previous = get_previous_day(coin1, coin2)
    # if the previous day con't be retrieved, then return 0 or 'N/A'
    if previous == 0 :
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
    # check if online or offline
    if internet_state == 'offline':
        print('Offline mode. Trend not available.')
        return 
    output = heading('Trend of the preferred currencies')
    output += 'Date: {0}\n'.format(datetime.date.today().isoformat())
    output += 'Coin   | Name         |   Trend\n'
    output += '-------+--------------+---------\n'
    for i in preferred:
        output += '{0:6} | {1:13}| {2:>+7.2%}\n'.format(i, currency_name(i), trend(i))
    output += '-------+--------------+---------\n'
    adv_print(output)

def print_currencies_trend():
    """print the trend of the currencies being retrieved"""
    # check if online or offline
    if internet_state == 'offline':
        print('Offline mode. Trend not available.')
        return 
    output = heading('Trend of the currencies being retrieved')
    output += 'Date: {0}\n'.format(datetime.date.today().isoformat())
    output += 'Coin   | Name         |   Trend\n'
    output += '-------+--------------+---------\n'
    for row in currency_rates:
        i = row[0]
        output += '{0:6} | {1:13}| {2:>+7.2%}\n'.format(i, currency_name(i), trend(i))
    output += '-------+--------------+---------\n'
    adv_print(output)
  
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
    with open(filename, 'r', newline = '') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            coin = row[0]
            amount = eval(row[1])
            rate = eval(row[2])
            euroeq = eval(row[3])
            perc_of_portfolio = eval(row[4])
            portfolio.append([coin, amount, rate, euroeq, perc_of_portfolio])
    print('Portfolio read from {0}.'.format(filename));

def print_balance(update = True):
    """Print balance of portfolio, based in Euro.
    update = True --> retrieve updated exchange rates,
    update = False --> use stored exchange rates."""
    ### to be modified:
    # variables
    global portfolio
    global portfolio_total
    output = heading('Portfolio Balance')
    if portfolio == []:
        try :
            read_portfolio()
        except :
            print('No portfolio present yet.')
            return
    # check if online or offline
    if internet_state == 'offline':
        output += 'Currently offline, using last stored exchange rates.\n'
    # this first iteration is to compute portofolio_total, which will be used later to compute percentage
    output += 'Date: {0}\n'.format(datetime.date.today().isoformat())
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
    if portfolio_total == 0:
        portfolio_total = 0.000001
    output += 'Coin  - Name         |   Amount   |   Rate    |   Trend |  Equiv.    | Port.%\n'
    output += '---------------------+------------+-----------+---------+------------+-------\n'
    for row in portfolio:
        coin = row[0]
        amount = row[1]
        rate = row[2]
        euroeq = row[3]
        perc_of_portfolio = euroeq / portfolio_total
        row[4] = perc_of_portfolio
        output += '{0:6}- {1:13}| {2:10.5f} | {3:9.4f} | {4:>+8.2%}| € {5:8.2f} | {6:>6.2%}\n' \
              .format(coin, currency_name(coin), amount, rate, trend(coin), euroeq, perc_of_portfolio)
    output += '---------------------+------------+-----------+---------+------------+-------\n'
    output += 'Total: € {0:7.2f}\n'.format(portfolio_total)
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

def print_ledger():
    """Print ledger"""
    if ledger == []:
        try :
            read_ledger()
        except :
            print('No ledger present yet.')
            return
    output = heading('Ledger')
    output += 'Coin  - Name         |   Amount   |   Rate    |   Date\n'
    output += '---------------------+------------+-----------+----------\n'
    ### ledger format: coin, amount, rate, date
    for row in ledger:
        coin = row[0]
        output += '{0:6}- {1:13}| {2:10.5f} | {3:9.4f} | {4}\n' \
              .format(coin, currency_name(coin), row[1], row[2], row[3])
    output += '---------------------+------------+-----------+----------\n'
    if ledger != []:
        adv_print(output)

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

    # variables used by this function
    # portfolio format: [coin, amount, rate, euroeq, percentage_of_portfolio]
    # ledger format: [coin, amount, rate, date]
    # analysis format: [coin, amount, euroeq, date]
    global portfolio
    global ledger
    output = heading('Analysis of positions')
    output += 'Date: {0}\n'.format(datetime.date.today().isoformat())
    analysis = []
    total_closed = 0
    total_open = 0
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
    output += 'Closed positions:\n'
    output += 'Coin  - Name         |   Closed   |   P/L \n'
    output += '---------------------+------------+-----------\n'
    for rowa in analysis:
        if rowa[1] == 0:
            total_closed = total_closed - rowa[2]
            output += '{0:6}- {1:13}| {2} | € {3:>+8.2f}\n' \
                     .format(rowa[0], currency_name(rowa[0]), rowa[3], -rowa[2])
    output += '---------------------+------------+-----------\n'
    output += 'Total P/L on closed positions: € {0:>+8.2f}\n'.format(total_closed)
    # then output open positions
    output += '\nOpen positions:\n'
    output += 'Coin  - Name         |   Amount   |   P/L \n'
    output += '---------------------+------------+-----------\n'
    for rowa in analysis:
        if rowa[1] != 0:
            pl = rowa[1] * get_ticker(rowa[0], 'EUR') - rowa[2]
            total_open = total_open + pl
            output += '{0:6}- {1:13}| {2:>10.5f} | € {3:+8.2f}\n' \
                     .format(rowa[0], currency_name(rowa[0]), rowa[1], pl)
    output += '---------------------+------------+-----------\n'
    output += 'Total P/L on open positions: € {0:>+8.2f}\n'.format(total_open)
    adv_print(output)

def best_and_worst(n = 5):
    """Evaluate trend of the currencies in the market and returns the best and worst n coins"""
    # check if online or offline
    if internet_state == 'offline':
        print('Offline mode. Trend not available.')
        return 
    # variables
    global currency_trends
    currency_trends = [] # format [[trend, coin], ...]
    i=0
    l=0
    l=len(currency_pairs)
    print ('...computing trend of {0} coins...'.format(l))
    for c in currency_pairs:
        coin = c[0]
        currency_trends.append([trend(coin), coin])
        i=i+1
        if divmod(i,10)[1] == 0:
            print(i,end=' ')
    currency_trends.sort()
    currency_trends.reverse()
    output = heading('Best and worst trends (1D)')
    output += 'Date: {0}\n'.format(datetime.date.today().isoformat())
    output += 'Best trending coins:\n'
    output += 'Coin   | Name         |   Trend\n'
    output += '-------+--------------+------------\n'
    for c in range(n):
        i = currency_trends[c]
        output += '{0:6} | {1:13}| {2:>+10.2%}\n'.format(i[1], currency_name(i[1]), i[0])
    output += '-------+--------------+------------\n'
    output += 'Worst trending coins:\n'
    output += 'Coin   | Name         |   Trend\n'
    output += '-------+--------------+------------\n'
    for c in range(len(currency_trends)-n,len(currency_trends)):
        i = currency_trends[c]
        output += '{0:6} | {1:13}| {2:>+10.2%}\n'.format(i[1], currency_name(i[1]), i[0])
    output += '-------+--------------+------------\n'
    adv_print(output)

def heading(text, heading_level = 1, length = 40):
    """Print a text formatted as a specific heading"""
    ### currently implemented heading level 1 only
    output = '\n┌' + '-' * (length - 2) + '┐\n'
    output += '| ' + text + ' ' * (length - len(text) - 3) + '|\n'
    output += '└' + '-' * (length - 2) + '┘\n\n'
    return output

def adv_print(text):
    print(text)
    if duplicate_output:
        with open("Output.txt", "a", encoding="utf-8") as text_file:
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

    
