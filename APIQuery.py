import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import webbrowser
import os

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
            print("Error: Interval must be specified for intraday data (1min, 5min, 15min, 30min, or 60min).")
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
        if "Note" in data:
            print("Note from API:", data["Note"])
        if "Error Message" in data:
            print("error from API:", data["Error Message"])
        return data
    else:
        print("error fetching data")
        return None

#Parse JSON data to get the dates and closing prices
def parse_time_series(data, time_series_function, start_date, end_date, interval=None):
    if time_series_function == "TIME_SERIES_INTRADAY":
        if interval is None:
            print("Error: Interval must be specified for intraday data.")
            return [], [], [], [], []
        time_series_key = f"Time Series ({interval})"
    elif time_series_function == "TIME_SERIES_DAILY":
        time_series_key = "Time Series (Daily)"
    elif time_series_function == "TIME_SERIES_WEEKLY":
        time_series_key = "Weekly Time Series"
    elif time_series_function == "TIME_SERIES_MONTHLY":
        time_series_key = "Monthly Time Series"
    else:
        print("Unknown time series function")
        return [], [], [], [], []

    if time_series_key not in data:
        print(f"Error: Could not retrieve expected data from the API for {interval}. Check your input and try again.")
        return [], [], [], [], []

    time_series_data = data[time_series_key]
    dates = []
    opens = []
    highs = []
    lows = []
    closes = []

    start = datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.strptime(end_date, '%Y-%m-%d').date()

    for date, value in time_series_data.items():
        try:
            if time_series_function == "TIME_SERIES_INTRADAY":
                current_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date()  # Convert to date only
            else:
                current_date = datetime.strptime(date, '%Y-%m-%d').date()

            if start <= current_date <= end:
                dates.append(current_date)
                opens.append(float(value["1. open"]))
                highs.append(float(value["2. high"]))
                lows.append(float(value["3. low"]))
                closes.append(float(value["4. close"]))
        except ValueError as e:
            print(f"Error parsing date: {e}")

    if not dates or not closes:
        print("No data found within the specified date range.")
        return [], [], [], [], []

    dates, opens, highs, lows, closes = zip(*sorted(zip(dates, opens, highs, lows, closes)))
    return dates, opens, highs, lows, closes

#Validating user date input
def validate_dates(start_date, end_date):
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        if start > end:
            print("Error: Start date cannot come after the end date")
            return False
        if end > datetime.now():
            print("Error: End date cannot be in the future.")
            return False
        return True
    except ValueError:
        print("Error: Invalid date format. Please use YYYY-MM-DD.")
        return False
    
def generate_chart(dates, opens, highs, lows, closes, symbol, chart_type, time_series_function, start_date, end_date):
    if not dates:
        print("No data to generate a chart.")
        return

    plt.figure(figsize=(12, 6))  # Adjusted figure size for better readability

    if chart_type == "bar":
        plt.bar(dates, opens, label='Open', alpha=0.6)
        plt.bar(dates, highs, label='High', alpha=0.6)
        plt.bar(dates, lows, label='Low', alpha=0.6)
        plt.bar(dates, closes, label='Close', alpha=0.6)
    else:
        plt.plot(dates, opens, label='Open', marker='o', linestyle='-', alpha=0.8)
        plt.plot(dates, highs, label='High', marker='^', linestyle='-', alpha=0.8)
        plt.plot(dates, lows, label='Low', marker='v', linestyle='-', alpha=0.8)
        plt.plot(dates, closes, label='Close', marker='s', linestyle='-', alpha=0.8)

    plt.title(f"Stock Prices for {symbol} ({start_date} to {end_date})")
    plt.xlabel("Date and Time" if time_series_function == "TIME_SERIES_INTRADAY" else "Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)

    if len(dates) <= 10:
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    elif len(dates) <= 60:
        plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    elif len(dates) <= 365:
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    else:
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

    plt.xticks(rotation=45)
    plt.tight_layout()

    chart_filename = "stock_chart.png"
    plt.savefig(chart_filename)

    html_content = f"""
    <html>
    <head><title>Stock Chart for {symbol} ({start_date} to {end_date})</title></head>
    <body>
        <h1>Stock Chart for {symbol} ({start_date} to {end_date})</h1>
        <img src="{chart_filename}" alt="Stock Chart">
    </body>
    </html>
    """
    
    html_filename = "stock_chart.html"
    with open(html_filename, "w") as file:
        file.write(html_content)
    
    file_path = os.path.abspath(html_filename)
    webbrowser.open(f"file://{file_path}")

def main():
    while True:
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
        time_series_function = None
        #Default value for interval
        interval = None

        choice = input("Enter the number corresponding to your choice: ")
        if choice == "1":
            time_series_function = "TIME_SERIES_INTRADAY"
            #If user chooses intraday, they must choose an interval
            interval = input("Enter interval (1min, 5min, 15min, 30min, 60min): ")
        elif choice == "2":
            time_series_function = "TIME_SERIES_DAILY"
        elif choice == "3":
            time_series_function = "TIME_SERIES_WEEKLY"
        elif choice == "4":
            time_series_function = "TIME_SERIES_MONTHLY"
        else:
            print("Invalid choice, defaulted to Daily")
            time_series_function = "TIME_SERIES_DAILY"

        #Asking user for the date range
        start_date = input("Enter start date (YYYY-MM-DD): ")
        end_date = input("Enter end date (YYYY-MM-DD): ")

        if not validate_dates(start_date, end_date):
            continue
        
        #Fetch the stock data
        stock_data = fetch_stock_data(symbol, time_series_function, interval=interval)
        if stock_data:
            dates, opens, highs, lows, closes = parse_time_series(stock_data, time_series_function, start_date, end_date, interval)
            generate_chart(dates, opens, highs, lows, closes, symbol, chart_type, time_series_function, start_date, end_date)

        #Ask user if they want to continue
        cont = input("Do you want to check another stock? (yes/no): ").lower()
        if cont != "yes":
            print("Thank you for testing Project 03: Stock Data Visualizer!")
            break

if __name__ == "__main__":
    main()