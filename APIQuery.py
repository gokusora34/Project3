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
            return [], []
        time_series_key = f"Time Series ({interval})"
    elif time_series_function == "TIME_SERIES_DAILY":
        time_series_key = "Time Series (Daily)"
    elif time_series_function == "TIME_SERIES_WEEKLY":
        time_series_key = "Weekly Time Series"
    elif time_series_function == "TIME_SERIES_MONTHLY":
        time_series_key = "Monthly Time Series"
    else:
        print("Unknown time series function")
        return [], []

    if time_series_key not in data:
        print(f"Error: Could not retrieve expected data from the API for {interval}. Check your input and try again.")
        return [], []

    time_series_data = data[time_series_key]
    dates = []
    closing_prices = []

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
                closing_prices.append(float(value["4. close"]))
        except ValueError as e:
            print(f"Error parsing date: {e}")

    if not dates or not closing_prices:
        print("No data found within the specified date range.")
        return [], []

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
    
def generate_chart(dates, closing_prices, symbol, chart_type, time_series_function):
    if not dates or not closing_prices:
        print("No data to generate a chart.")
        return

    plt.figure(figsize=(12, 6))  # Adjusted figure size for better readability

    if chart_type == "bar":
        plt.bar(dates, closing_prices, label='Closing Price')
    else:
        plt.plot(dates, closing_prices, label='Closing Price', marker='o')

    plt.title(f"Stock Prices for {symbol}")
    plt.xlabel("Date and Time" if time_series_function == "TIME_SERIES_INTRADAY" else "Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)

    # Dynamically adjust x-axis ticks based on the time range
    if time_series_function == "TIME_SERIES_INTRADAY":
        plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=2))  # Show tick every 2 hours
        plt.gca().xaxis.set_minor_locator(mdates.MinuteLocator(interval=30))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
    else:
        # Determine the length of the date range to adjust the ticks
        num_dates = len(dates)

        if num_dates <= 10:
            # If less than or equal to 10 dates, show all
            plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        elif num_dates <= 60:
            # If dates span about 2 months, show weekly ticks
            plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        elif num_dates <= 365:
            # If dates span up to a year, show monthly ticks
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        else:
            # If more than a year, show quarterly ticks
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

    plt.xticks(rotation=45)  # Rotate labels for better readability
    plt.tight_layout()  # Adjust layout to fit everything

    # Save the chart as a PNG
    chart_filename = "stock_chart.png"
    plt.savefig(chart_filename)

    # Create an HTML file to open the image in a browser
    html_content = f"""
    <html>
    <head><title>Stock Chart for {symbol}</title></head>
    <body>
        <h1>Stock Chart for {symbol}</h1>
        <img src="{chart_filename}" alt="Stock Chart">
    </body>
    </html>
    """
    
    html_filename = "stock_chart.html"
    with open(html_filename, "w") as file:
        file.write(html_content)
    
    # Use webbrowser to open the HTML file in the default browser
    file_path = os.path.abspath(html_filename)
    webbrowser.open(f"file://{file_path}")

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
        return
    
    #Fetch the stock data
    stock_data = fetch_stock_data(symbol, time_series_function, interval=interval)
    if stock_data:
        dates, closing_prices = parse_time_series(stock_data, time_series_function, start_date, end_date, interval)
        generate_chart(dates, closing_prices, symbol, chart_type, time_series_function)

if __name__ == "__main__":
    main()