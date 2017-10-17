# my_trading
Python module to handle cryptocurrency trading portfolio. No automatic link to any wallet.

Disclaimer: use it at YOUR OWN RISK. I am NOT responsible for any loss or damage due to the use of this module.
This module provides with some functions to retrieve public data using the APIs provided by these websites:
- from https://www.coindesk.com/api/
- from https://www.bittrex.com/Home/Api

Functions are of different kind:
- get (from internet)
- print (to screen)
- read (from file)
- save (to file)
- others (such as those to compute trends and analyze positions)

How to use it:
- use init() after importing the module, in order to read the codes and names of the currencies.
- use add_entry_to_ledger() to populate the ledger
- use update_portfolio() to update the portfolio (and save to file), based on the ledger
- use print_balance() to print a report on the current balance of the portfolio, including trend and percentage of portfolio for each currency, translated in Euro
- use analyze_position() to generate a report on the profit and loss for the closed and open positions (collapsed for each coin), translated in Euro

*Note*: it is also possible to define a list of preferred currencies, even if they are not in the portfolio, in the following format:
preferred = ['BTC', 'XMR', 'LTC', 'XRP', 'DASH', 'BCC', 'ETH'] # first coin must be 'BTC'. The codes are taken from bittrex, so Bitcoin is BTC and Bitcoin Cash is BCC.

If you want to try it first, you can copy the example ledger.csv in the same directory where you put my_trading.py.

        Output (either on screen or on file):
        ┌--------------------------------------┐
        | Portfolio Balance                    |
        └--------------------------------------┘

        Coin  - Name         |   Amount   |   Rate    |   Trend |  Equiv.    | Port.%
        EUR   - Euro         |   26.30000 |    1.0000 |   +0.00%| €    26.30 |  0.55%
        XMR   - Monero       |   10.00000 |   80.7888 |   -0.60%| €   807.89 | 17.03%
        BTC   - Bitcoin      |    0.27000 | 4828.2252 |   +0.10%| €  1303.62 | 27.49%
        BCC   - Bitcoin Cash |    0.00000 |  266.8333 |   -1.11%| €     0.00 |  0.00%
        DASH  - Dash         |    5.30000 |  261.0448 |   -0.74%| €  1383.54 | 29.17%
        XRP   - Ripple       | 5000.00000 |    0.2443 |   +8.20%| €  1221.54 | 25.76%
        Total: € 4742.89

        ┌--------------------------------------┐
        | Analysis of positions                |
        └--------------------------------------┘

        Closed positions:
        Coin  - Name         |   Closed   |   P/L 
        BCC   - Bitcoin Cash | 11/10/2017 | €  -435.80

        Open positions:
        Coin  - Name         |   Amount   |   P/L 
        EUR   - Euro         |   26.30000 | €    +0.00
        XMR   - Monero       |   10.00000 | €  -165.11
        BTC   - Bitcoin      |    0.27000 | €  +314.39
        DASH  - Dash         |    5.30000 | €  -118.87
        XRP   - Ripple       | 5000.00000 | €  +160.92

*Note*: it is possible to duplicate the output to a output.txt file, by defining global variable duplicate_output = True.
