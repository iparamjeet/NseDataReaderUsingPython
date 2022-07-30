import NseIndia

nse = NseIndia.NSE()

print(nse.equity_market_categories)
nse.equity_market_data("NIFTY 50")
#print(len(nse.equity_market_data('Securities in F&O', symbol_list=True)))

#nse.equity_market_data("NIFTY 50", symbol_list=True)
#print(nse.holidays_categories)

#print(nse.pre_market_categories)
#nse.pre_market_data("Nifty Bank")