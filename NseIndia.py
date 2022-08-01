import requests
import pandas as pd
import json
import math


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


class NSE:
    pre_market_categories = ['NIFTY 50', 'Nifty Bank',
                             'Emerge', 'Securities in F&O', 'Others', 'ALL']
    equity_market_categories = [...]
    holidays_categories = ["clearing", "Trading"]

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}
        self.session = requests.Session()
        self.session.get("http://nseindia.com", headers=self.headers)

    def pre_market_data(self, category):
        pre_market_category = {"NIFTY 50": "NIFTY", "Nifty Bank": "BANKNIFTY", "Emerge": "SME", "Securities in F&O": "FO",
                               "Others": "OTHERS", "ALL": "ALL"}
        data = self.session.get(f"https://www.nseindia.com/api/market-data-pre-open?key={pre_market_category[category]}",
                                headers=self.headers).json()["data"]

        df = pd.DataFrame(data).to_excel("Data_pre_Equitymarket.xlsx")

        new_data = []
        for i in data:
            new_data.append(i["metadata"])
        df = pd.DataFrame(new_data)
        df = df.set_index("symbol", drop=True)
        return df

    def equity_market_data(self, category, symbol_list=False):
        pasaCat = category
        category = category.upper().replace(' ', '%20').replace('&', '%26')
        data = self.session.get(
            f"https://www.nseindia.com/api/equity-stockIndices?index={category}", headers=self.headers).json()["data"]

        # copy generated live-data to xl
        df = pd.DataFrame(data).to_excel("Data_liveEquityMarket.xlsx")

        # copy generated live-data to json file
        with open('Data_liveEquity.json', 'w') as f:
            json.dump(data, f)

        # calculate total change in NIFTY50
        total_change = 0
        total_percent_change = 0
        f = open('Data_liveEquity.json')
        res = json.load(f)
        for data in res:
            total_change += data['change']
            total_percent_change += data['pChange']
            if data['open'] == data['dayLow']:
                print('Take Long position in : ' + data['symbol'])

            if data['open'] == data['dayHigh']:
                print('Take Short position in : ' + data['symbol'])

        print('Total change in ' + str(pasaCat) + ' :' +
              str(math.floor(total_change-res[0]['change'])))
        print('Total change in ' + str(pasaCat) + ' percentage wise : ' +
              str(math.floor(total_percent_change-res[0]['pChange'])))

        # to format data in tabular form and print in consle as table
        df = pd.DataFrame(data)
        df = df.drop(["meta"], axis=1)
        df = df.set_index("symbol", drop=True)
        if symbol_list:
            return list(df.index)
        else:
            return df

    def about_holidays(self, category):
        data = self.session.get(
            f'https://www.nseindia.com/api/holiday-master?type={category.lower()}', headers=self.headers).json()
        df = pd.DataFrame(list(data.values())[0])
        return df

    def equity_info(self, symbol, trade_info=False):
        symbol = symbol.replace('', '%20').replace('&', '%26')
        url = 'https://www.nseindia.com/api/quote-equity?symbol=' + \
            symbol + ("&section=trade_info" if trade_info else "")
        data = self.session.get(url, headers=self.headers).json()
        return data

    def future_data(self, symbol, indices=False):
        symbol = symbol.replace(' ', '%20').replace('&', '%26')
        url = 'https://www.nseindia.com/api/quote-derivative?symbol=' + symbol
        data = self.session.get(url, headers=self.headers).json()
        lst = []
        for i in data["stocks"]:
            if i["metadata"]["instrumentType"] == ("Index Futures" if indices else "Stock Futures"):
                lst.append(i["metadata"])
        df = pd.DataFrame(lst)
        df = df.set_index("identifier", drop=True)
        return df

    def option_data(self, symbol, indices=False):
        symbol = symbol.replace(' ', '%20').replace('&', '%26')
        if not indices:
            url = 'https://www.nseindia.com/api/option-chain-equities?symbol=' + symbol
        else:
            url = 'https://www.nseindia.com/api/option-chain-indices?symbol=' + symbol
        data = self.session.get(url, headers=self.headers).json()[
            "records"]["data"]
        my_df = []
        for i in data:
            for k, v in i.items():
                if k == "CE" or k == "PE":
                    info = v
                    info["instrumentType"] = k
                    my_df.append(info)
        df = pd.DataFrame(my_df).to_excel("Data_optionChain.xlsx")
        df = pd.DataFrame(my_df)
        df = df.set_index("identifier", drop=True)
        return df
