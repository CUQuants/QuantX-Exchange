import sys
import os
import getpass
import time

# Add the client_library to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from client_library.trading_client.client import TradingClient

def run_examples():
    """
    Demonstrates how to use the TradingClient to interact with the QuantX Exchange API.
    """
    client = TradingClient(base_url="http://127.0.0.1:8000")
    
    print("--- 1. User Authentication ---")
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")

    if not client.login(username, password):
        print("Authentication failed. Please check your credentials or create a user with 'scripts/manage_users.py'")
        return
    
    print("✅ Successfully authenticated.")

    print("\n--- 2. Fetching Account Balance ---")
    balance = client.get_account_balance()
    if 'error' not in balance:
        print(f"Current balance: {balance.get('balance')}")
    else:
        print(f"Error fetching balance: {balance.get('error')}")

    print("\n--- 3. Placing a New Order ---")
    symbol = "BTCUSD"
    print(f"Placing a new LIMIT BUY order for 1 {symbol} at $50,000...")
    
    try:
        new_order = client.create_order(
            symbol=symbol,
            side="buy",
            order_type="limit",
            quantity=1,
            price=50000.0
        )
        if 'error' not in new_order:
            order_id = new_order.get('id')
            print(f"✅ Order placed successfully! Order ID: {order_id}")
            
            # Give the system a moment to process
            time.sleep(1)

            print(f"\n--- 4. Canceling the Order ---")
            print(f"Canceling order {order_id}...")
            cancel_status = client.cancel_order(order_id)
            if 'error' not in cancel_status:
                print(f"✅ Order {order_id} canceled successfully.")
            else:
                print(f"Error canceling order: {cancel_status.get('error')}")

        else:
            print(f"Error placing order: {new_order.get('error')}")
            
    except Exception as e:
        print(f"An unexpected error occurred during trading: {e}")

if __name__ == "__main__":
    run_examples() 