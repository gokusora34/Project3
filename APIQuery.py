import requests
import matplotlib.pyplot as plt
from datetime import datetime

#API Key for Alpha Vantage Query
api_key = "A5XGJKIF1F4259FR"

def fetch_stock_data(symbol, time_series_function, interval=None, outputsize='compact', adjusted=True, extended_hours=True, month=None):
    url = f"https://www.alphavantage.co/query"
    params = {
        'function': time_series_function,
        'symbol': symbol,
        'apikey': api_key,
        'outputsize': 'full'
    }

    # These are the additional parameters for intraday (from the Alpha Vantage website)
    if time_series_function == "TIME_SERIES_INTRADAY":
        if interval is None:
            print("Error: Interval must be specified for intraday data (1 min, 5 min, 15min, 30min, or 60min).")
            return None
        params['interval'] = interval
        params['outputsize'] = outputsize
        params['adjusted'] = 'true' if adjusted else 'false'
        params['extended_hours'] = 'true' if extended_hours else 'false'
        if month:
               params['month'] = month

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("error fetching data")
        return None

#Parse JSON data to get the dates and closing prices
def parse_time_series(data, time_series_function, start_date, end_date, interval=None):
    # Check for the different time series function keys
    if time_series_function == "TIME_SERIES_INTRADAY":
        if interval is None:
            print("Error: Interval must be specified for intraday data.")
            return [], []
        time_series_key = f"Time Series ({interval})" #Dynamically set based on interval
    elif time_series_function == "Time_SERIES_DAILY":
        time_series_key = "Time Series (Daily)"
    elif time_series_function == "TIME_SERIES_WEEKLY":
        time_series_key = "Weekly Time Series"
    elif time_series_function == "TIME_SERIES_MONTHLY":
        time_series_key = "Monthly Time Series"
    else:
        print("Unknown Time series function")
        return [], []
    
    # Reponse for if key doesn't exist
    if time_series_key not in data:
        print(f"Error: Could not retrieve expected data from the API for {interval}. Check your input and try again.")
        return [], []

    time_series_data = data[time_series_key]

    dates = []
    closing_prices = []

    #Converts user input dates to datetime objects
    start = datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.strptime(end_date, '%Y-%m-%d').date()

    for date, value in time_series_data.items():
        if time_series_function == "TIME_SERIES_INTRADAY":
            current_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date() #Parse as date only
        else:
            current_date = datetime.strptime(date, '%Y-%m-%d').date()

        # Only add data within the user-specified date range
        if start <= current_date <= end:
            dates.append(datetime.strptime(date, '%Y-%m-%d %H:%M:%S') if time_series_function == "TIME_SERIES_INTRADAY" else datetime.strptime(date, '%Y-%m-%d'))
            closing_prices.append(float(value["4. close"]))

        #Chick if any data points were added
        if not dates or not closing_prices:
            print("No data found within the specified date range.")
            return [], []

    # Manually sorting the data by date for redundency
    dates, closing_prices = zip(*sorted(zip(dates, closing_prices)))

    return dates, closing_prices

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
    
def generate_chart(dates, closing_prices, symbol):
    plt.figure(figsize=(10,5))
    plt.plot(dates, closing_prices, label='Closing Price', marker='o')
    plt.title(f"Stock Prices for {symbol}")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Saves the chart as an image file and displays it
    plt.savefig("stock_chart.png")
    plt.show()

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
    #Default value for interval
    interval = None

    choice = input("Enter the number corresponding to your choice: ")
    if choice == "1":
        time_series_funciton = "TIME_SERIES_INTRADAY"
        #If user chooses intraday, they must choose an interval
        interval = input("Enter interval (1min, 5min, 15min, 30min, 60min): ")
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
    stock_data = fetch_stock_data(symbol, time_series_funciton, interval=interval)

    if stock_data:
        dates, closing_prices = parse_time_series(stock_data, time_series_funciton, start_date, end_date, interval)
        generate_chart(dates, closing_prices, symbol)

if __name__ == "__main__":
    main()