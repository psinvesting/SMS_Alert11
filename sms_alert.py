!pip install requests
!pip install twilio
import pandas as pd
import requests
import time
from twilio.rest import Client
import datetime
import pytz
from datetime import datetime, timedelta

# Twilio configuration
TWILIO_ACCOUNT_SID = 'AC3d9321926463f58138250b1c4ac732c6'
TWILIO_AUTH_TOKEN = 'deb3aec65ecb3ae85944bb18acc4e004'
TWILIO_PHONE_NUMBER = '+19282501419'
TO_PHONE_NUMBER = '+919866040333'

# Delta Exchange API endpoint
SYMBOLS_API_URL = 'https://api.india.delta.exchange/v2/products'
DELTA_API_URL = 'https://api.india.delta.exchange/v2/history/candles'

# Function to fetch all trading pairs
def fetch_trading_pairs():
    #response = requests.get(SYMBOLS_API_URL)
    headers = {
    'Accept': 'application/json'
    }

    r = requests.get('https://api.india.delta.exchange/v2/products', params={

    }, headers = headers)
    data = r.json()
    #print(data.keys())
    #print(r.json())
    result_data = data.get('result', [])
    # Create the DataFrame from the 'result' data
    d1 = pd.DataFrame(result_data)
    contracts = d1['symbol'][d1['contract_type']=="perpetual_futures"].tolist()
    return contracts

##################################################################
# Function to fetch candle data
def fetch_candle_data(symbol, resolution, start, end):
    sym=fetch_trading_pairs()
    #print(sym)
    headers = {
    'Accept': 'application/json'
    }
    params = {
        'symbol': symbol,
        'resolution': '15m',
        #'limit': limit,
        'start' : start_time,
        'end' : end_time,
    }

    try:
        response = requests.get('https://api.india.delta.exchange/v2/history/candles', headers=headers, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        result_data = data.get('result', [])
        df = pd.DataFrame(result_data)

        if not df.empty and 'volume' in df.columns:
            return df
        else:
            return pd.DataFrame()  # Return an empty DataFrame if no data is found
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame()

def check_volume_increase(symbol, current_volume):
    # Define the time range for the last 24 hours
    end_time = int(datetime.now().timestamp())
    start_time = int((datetime.now() - timedelta(days=1)).timestamp())

    # Fetch historical candle data for the last 24 hours
    df = fetch_candle_data(symbol, '15m', start_time, end_time)

    if not df.empty:
        # Check if the current volume is greater than any of the last 15-minute candle volumes
        if any(current_volume > df['volume']):
            print(f"Symbol: {symbol}, Current Volume: {current_volume}")
# Function to send SMS alert
def send_alert(message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=TO_PHONE_NUMBER
    )
# Main execution block
end_time = int(datetime.now().timestamp())
start_time = int((datetime.now() - timedelta(days=1)).timestamp())
trading_pairs = fetch_trading_pairs()  # Assuming this function is defined elsewhere
for symbol in trading_pairs:
    # Fetch the current candle data to get the latest volume
    current_data = fetch_candle_data(symbol, '15m', start_time, end_time)
    if not current_data.empty and len(current_data) > 1:
        current_volume = current_data['volume'].iloc[-2:-1].tolist()  # Get the volume of the previous candle
        previous_volumes = current_data['volume'].iloc[-97:-1].tolist()  # Get all previous volumes before the last two
        # Debugging output
        #print(f"current_volume for {symbol}: {current_volume}")
        #print(f"Previous volumes: {previous_volumes}")
    #if not current_data.empty:
        # Debugging output
        #current_volume = current_data['volume'].iloc[-2]  # Get the latest volume
        #previous_volumes = current_data['volume'].iloc[:-1].tolist()  # Get all previous volumes
        #previous_volumes = current_data['volume'].iloc[-97:-2].tolist()  # Get the last 96 previous
        #print(f"Current volume for {symbol}: {current_volume}")
        #print(f"Previous volumes {symbol}: {previous_volumes}")
        min_current_volume = max(current_volume) if current_volume else 0  # Handle empty case
        #print(f"Min current volume for {symbol}: {min_current_volume}")
        max_previous_volume = max(previous_volumes) if previous_volumes else 0  # Handle empty case
        #print(f"Max previous volume for {symbol}: {max_previous_volume}")
        #print(previous_volumes)
    #Check if the current volume is greater than the maximum of previous volumes
        #if current_volume > max(previous_volumes) #previous_volumes and
        #if current_volume > max_previous_volume:  # Compare current volume with max of previous volumes
        if min_current_volume > max_previous_volume:
           #print(f": {symbol}: {current_volume}")
            send_alert(f"Alert! for {symbol} Volume: {min_current_volume}.")
time.sleep(900)  # Wait for 15 minutes before checking again
