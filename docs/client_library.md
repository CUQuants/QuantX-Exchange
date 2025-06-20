# Python Client Library Guide

The `quantx_exchange_client` is a Python package that provides a convenient wrapper around the QuantX Exchange REST API and WebSocket feed.

## Installation

You can install the client library as a package by navigating to the `client_library` directory and running:
```bash
pip install .
```
For development, you can also import it directly, as shown in the `examples/client_example.py` script.

## Getting Started

First, initialize the client:
```python
from client_library.trading_client.client import TradingClient

client = TradingClient(base_url="http://127.0.0.1:8000")
```

## Authentication

To access protected endpoints, you must log in.

### `client.login(username, password)`
Authenticates with the exchange and saves the session token internally. Returns `True` on success.
```python
if client.login("my_user", "my_password"):
    print("Login successful!")
```

## Methods

### Account Management

- `client.get_account_balance()`: Returns the user's account balance.
- `client.get_account_positions()`: Fetches a list of the user's current positions.
- `client.get_account_trades(limit=100)`: Retrieves the user's trade history.
- `client.get_account_orders(status=None, limit=100)`: Gets a list of user orders, with an optional status filter (`'open'`, `'filled'`, etc.).

### Trading

- `client.create_order(symbol, side, order_type, quantity, price=None)`: Creates a new order.
  ```python
  client.create_order(
      symbol="BTCUSD",
      side="buy",
      order_type="limit",
      quantity=1,
      price=50000.0
  )
  ```
- `client.cancel_order(order_id)`: Cancels an existing order.

### Market Data

- `client.get_all_market_data()`: Returns data for all symbols.
- `client.get_market_data(symbol)`: Gets data for a specific symbol.
- `client.get_order_book(symbol)`: Fetches the order book for a symbol.
- `client.get_recent_trades(symbol, limit=50)`: Retrieves recent trades for a symbol.

### WebSocket Client

- `client.start_websocket(message_handler)`: Starts a WebSocket client in a separate thread to listen for real-time updates.

You must provide a callback function (`message_handler`) to process incoming messages.
```python
def handle_my_trades(trade_data):
    print(f"New trade received: {trade_data}")

client.start_websocket(handle_my_trades)

# Keep the main thread alive to see messages
import time
time.sleep(60)
```
This will print any live trades that occur on the exchange. 