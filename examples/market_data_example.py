import sys
import os

# Add the client_library to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from client_library.trading_client.client import TradingClient

def run_examples():
    """
    Demonstrates how to use the TradingClient to interact with the QuantX Exchange API.
    """
    # Make sure the backend is running before executing this script.
    client = TradingClient(base_url="http://127.0.0.1:8000")

    print("--- 1. Fetching All Market Data ---")
    all_market_data = client.get_all_market_data()
    if isinstance(all_market_data, dict) and "error" in all_market_data:
        print(f"Error: {all_market_data['error']}")
        print("Please ensure the QuantX Exchange backend is running.")
        return
        
    if all_market_data:
        print(f"Successfully fetched data for {len(all_market_data)} markets.")
        # Print details for the first market as an example
        print(f"Example market data: {all_market_data[0]}")
    else:
        print("No market data available. The database may be empty.")

    print("\n--- 2. Fetching Market Data for a Specific Symbol (e.g., BTCUSD) ---")
    # Assuming 'BTCUSD' is a symbol that might exist.
    # If not, this will gracefully handle the error.
    symbol = "BTCUSD" 
    market_data_symbol = client.get_market_data(symbol)
    if market_data_symbol and 'error' not in market_data_symbol:
        print(f"Data for {symbol}: {market_data_symbol}")
    else:
        print(f"Could not fetch data for {symbol}. It may not exist in the database.")
        print(f"Server response: {market_data_symbol.get('error', 'Unknown error')}")


    print(f"\n--- 3. Fetching Order Book for {symbol} ---")
    order_book = client.get_order_book(symbol)
    if order_book and 'error' not in order_book:
        print(f"Order book for {symbol}:")
        print(f"  Bids: {len(order_book.get('bids', []))} levels")
        print(f"  Asks: {len(order_book.get('asks', []))} levels")
        # Print top bid/ask if they exist
        if order_book.get('bids'):
            print(f"  Top Bid: {order_book['bids'][0]}")
        if order_book.get('asks'):
            print(f"  Top Ask: {order_book['asks'][0]}")
    else:
        print(f"Could not fetch order book for {symbol}.")


    print(f"\n--- 4. Fetching Recent Trades for {symbol} ---")
    recent_trades = client.get_recent_trades(symbol, limit=10)
    if recent_trades and 'error' not in recent_trades:
        print(f"Found {len(recent_trades)} recent trades for {symbol}.")
        if recent_trades:
            print(f"Example trade: {recent_trades[0]}")
    else:
        print(f"No recent trades found for {symbol}.")

if __name__ == "__main__":
    run_examples() 