# WebSocket Feed

The QuantX Exchange provides a real-time WebSocket feed for broadcasting live trade data.

**Endpoint**: `ws://localhost:8000/ws`

## How to Connect

You can connect to the WebSocket endpoint using any standard WebSocket client. The connection does not require authentication, but it is a one-way feed from the server to the client.

The server will push updates automatically whenever a trade is executed by the matching engine.

## Message Format

All messages are sent as JSON strings. Currently, the only message type is `trade`.

### Trade Message

This message is broadcasted every time a trade occurs on the exchange.

**Example:**
```json
{
  "type": "trade",
  "symbol": "BTCUSD",
  "price": 50000.0,
  "quantity": 1,
  "value": 50000.0,
  "timestamp": "2023-10-27T10:00:00.000Z"
}
```

- `type`: The type of message (always "trade" for now).
- `symbol`: The symbol of the instrument that was traded.
- `price`: The price at which the trade was executed.
- `quantity`: The quantity traded.
- `value`: The total value of the trade (`price` * `quantity`).
- `timestamp`: The UTC timestamp of the trade.

## Future Enhancements

In the future, the WebSocket feed may be expanded to include other channels, such as:
- **Order Book Updates**: Real-time changes to the order book.
- **User-Specific Feeds**: Authenticated feeds for updates on a user's own orders. 