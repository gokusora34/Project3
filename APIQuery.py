import requests
api_key = "A5XGJKIF1F4259FR"

def fetch_stock_data(symbol, time_series_function):
    url = f"https://www.alphavantage.co/query"
    params = {
        'function': time_series_function,
        'symbol': symbol,
        'apikey': api_key
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("error fetching data")
        return None

#Taking user input for stock symbol   
symbol = input("Enter the stock symbol: ").upper() 
time_series_function = "TIME_SERIES_DAILY"

stock_data = fetch_stock_data(symbol, time_series_function)

if stock_data:
    print(stock_data)