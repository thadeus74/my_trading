# This is where I put the things to do about current functions

- functions:
  - buy/sell function, to use current ticker to create entries in ledger and update portfolio

- visualization:
  - inside analyze_coinmarketcap() order the output

- information model:
  - add a first row to the ledger, with the keys, then one column with key 'operation' with these values: 'deposit', 'sell', buy', 'fee', 'withdrowal'
  - more than one portfolio (thus operations should be referred to a portfolio id or sequence number)
  - historical.csv could get very big, so it should store values of a specific period (e.g. month)
  - store temporary data in global variables, such as current and
  - create classes for entries in portfolio and ledger

- information gathering:
  - check if "IsActive":false on currency_pairs when retrieving coin codes and names
  - add an API key to retrieve info

- analysis: 
  - it might be useful to have also yesterday trend
  - increasing and decreasing series, such as one coin going up or down for 3 consecutive days
  - previous exchange rates, trends
