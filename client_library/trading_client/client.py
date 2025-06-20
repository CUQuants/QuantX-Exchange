import requests
from typing import List, Dict, Optional, Callable
import websockets
import asyncio
import threading
import json

class TradingClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000", token: Optional[str] = None):
        self.base_url = base_url
        self.session = requests.Session()
        if token:
            self.set_token(token)

    def set_token(self, token: str):
        """Set the authentication token for the session."""
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def login(self, username: str, password: str) -> bool:
        """Logs in to the exchange and stores the token."""
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/token",
                data={"username": username, "password": password}
            )
            response.raise_for_status()
            token_data = response.json()
            self.set_token(token_data["access_token"])
            return True
        except requests.exceptions.RequestException as e:
            print(f"Login failed: {e}")
            return False

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        """Helper method to make requests to the API."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, params=params, json=data)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return {"error": str(e)}

    def get_all_market_data(self) -> List[Dict]:
        """Retrieves market data for all available symbols."""
        return self._request("GET", "/market/data")

    def get_market_data(self, symbol: str) -> Dict:
        """Retrieves detailed market data for a specific symbol."""
        return self._request("GET", f"/market/data/{symbol.upper()}")

    def get_order_book(self, symbol: str) -> Dict:
        """Retrieves the order book for a specific symbol."""
        return self._request("GET", f"/market/orderbook/{symbol.upper()}")

    def get_recent_trades(self, symbol: str, limit: int = 50) -> List[Dict]:
        """Retrieves the most recent trades for a specific symbol."""
        params = {"limit": limit}
        return self._request("GET", f"/market/trades/{symbol.upper()}", params=params)

    # Account Methods
    def get_account_balance(self) -> Dict:
        """Retrieves the current trading balance for the authenticated user."""
        return self._request("GET", "/account/balance")

    def get_account_positions(self) -> List[Dict]:
        """Retrieves all current positions for the authenticated user."""
        return self._request("GET", "/account/positions")

    def get_account_trades(self, limit: int = 100) -> List[Dict]:
        """Retrieves the trade history for the authenticated user."""
        params = {"limit": limit}
        return self._request("GET", "/account/trades", params=params)

    def get_account_orders(self, status: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Retrieves the order history for the authenticated user."""
        params = {"limit": limit}
        if status:
            params["status"] = status
        return self._request("GET", "/account/orders", params=params)

    # Trading Methods
    def create_order(self, symbol: str, side: str, order_type: str, quantity: int, price: Optional[float] = None) -> Dict:
        """Creates a new order."""
        order_data = {
            "symbol": symbol,
            "side": side,
            "order_type": order_type,
            "quantity": quantity,
            "price": price
        }
        return self._request("POST", "/trading/orders", data=order_data)

    def cancel_order(self, order_id: int) -> Dict:
        """Cancels an open order."""
        return self._request("DELETE", f"/trading/orders/{order_id}")

    # WebSocket Methods
    def start_websocket(self, message_handler: Callable[[Dict], None]):
        """Starts a WebSocket client to receive real-time updates."""
        ws_url = self.base_url.replace("http", "ws") + "/ws"
        
        def run_loop():
            asyncio.run(self._ws_handler(ws_url, message_handler))

        ws_thread = threading.Thread(target=run_loop, daemon=True)
        ws_thread.start()
        print(f"WebSocket client started, connected to {ws_url}")

    async def _ws_handler(self, ws_url: str, message_handler: Callable[[Dict], None]):
        """Handles the WebSocket connection and message receiving."""
        try:
            async with websockets.connect(ws_url) as websocket:
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    message_handler(data)
        except Exception as e:
            print(f"WebSocket error: {e}")

if __name__ == '__main__':
    # Example usage:
    client = TradingClient()

    print("Fetching all market data...")
    all_markets = client.get_all_market_data()
    print(all_markets)

    print("\nFetching market data for BTCUSD...")
    btc_market = client.get_market_data("BTCUSD")
    print(btc_market)

    print("\nFetching order book for BTCUSD...")
    order_book = client.get_order_book("BTCUSD")
    print(order_book)

    print("\nFetching recent trades for BTCUSD...")
    recent_trades = client.get_recent_trades("BTCUSD", limit=5)
    print(recent_trades)

    # WebSocket Example
    def my_trade_handler(trade_data):
        print(f"\n--- New Trade via WebSocket ---")
        print(f"Received trade: {trade_data}")

    print("\nStarting WebSocket to listen for new trades...")
    client.start_websocket(my_trade_handler)

    # Keep the main thread alive to see WebSocket messages
    print("Main thread will sleep for 60 seconds to wait for WebSocket messages...")
    print("Try creating a new order/trade in another window to see updates.")
    threading.Event().wait(60)
    print("\nExample finished.") 