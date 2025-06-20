# QuantX Exchange Client

This is the official Python client for the QuantX Exchange API. It provides a simple and convenient way to interact with the exchange's market data, trading, and account management features.

## Installation

To install the client, navigate to the `client_library` directory and run:

```bash
pip install .
```

## Usage

Here's a quick example of how to use the client to fetch market data:

```python
from trading_client.client import TradingClient

# Initialize the client
client = TradingClient()

# Get all market data
all_markets = client.get_all_market_data()
print(all_markets)

# Get data for a specific symbol
btc_market = client.get_market_data("BTCUSD")
print(btc_market)
``` 