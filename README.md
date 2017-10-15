# my_trading
Python module to handle cryptocurrency trading portfolio. No automatic link to any wallet.

Disclaimer: use it at YOUR OWN RISK. I am NOT responsible for any loss or damage due to the use of this module.
This module provides with some functions to retrieve public data using the APIs provided by these websites:
- https://www.coindesk.com/api/
- from https://www.bittrex.com/Home/Api

Functions are of different kind:
- get (from internet)
- print (to screen)
- read (from file)
- save (to file)
- others (such as those to compute trends)

How to use it:
- use init() after importing the module, in order to read the codes and names of the currencies.
- use add_entry_to_ledger() to populate the ledger
- use update_portfolio() to update the portfolio (and save to file), based on the ledger
- use print_balance() to print a report on the current balance of the portfolio, including trend and percentage of portfolio for each currency, translated in Euro.

Note: it is also possible to define a list of preferred currencies, even if they are not in the portfolio, in the following format:
preferred = ['BTC', 'XMR', 'LTC', 'XRP', 'DASH', 'BCC', 'ETH'] # first coin must be 'BTC'. The codes are taken from bittrex, so Bitcoin is BTC and Bitcoin Cash is BCC.

