import requests
from datetime import datetime

#API Key for Alpha Vantage Query
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

#Validating user date input
def validate_dates(start_date, end_date):
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        if start > end:
            print("Error: Start date cannot come after the end date")
            return False
        return True
    except ValueError:
        print("Error: Invalid date format. Please use YYYY-MM-DD.")
        return False
    
def main():
#Taking user input for stock symbol   
    symbol = input("Enter the stock symbol: ").upper() 

    #Asking user for chart type
    chart_type = input("Enter chart type (line, bar): ").lower()

    #Ask user for time series function
    print("Choose a time series function: ")
    print("1. Intraday")
    print("2. Daily")
    print("3. Weekly")
    print("4. Monthly")

    #Default time series to invalid value
    time_series_funciton = None

    choice = input("Enter the number corresponding to your choice: ")
    if choice == "1":
        time_series_funciton = "TIME_SERIES_INTRADAY"
    elif choice == "2":
        time_series_funciton = "TIME_SERIES_DAILY"
    elif choice == "3":
        time_series_funciton = "TIME_SERIES_WEEKLY"
    elif choice == "4":
        time_series_funciton = "TIME_SERIES_MONTHLY"
    else:
        print("Invalid choice, defaulted to Daily")
        time_series_funciton = "TIME_SERIES_DAILY"

    #Asking user for the date range
    start_date = input("Enter start date (YYYY-MM-DD): ")
    end_date = input("Enter end date (YYYY-MM-DD): ")

    if not validate_dates(start_date, end_date):
        return
    
    #Fetch the stock data
    stock_data = fetch_stock_data(symbol, time_series_funciton)

    if stock_data:
        print(stock_data)

if __name__ == "__main__":
    main()