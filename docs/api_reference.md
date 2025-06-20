# API Reference

This document provides a detailed reference for the QuantX Exchange REST API.

**Base URL**: `http://localhost:8000`

---

## Authentication

### `POST /api/auth/token`

Authenticates a user and returns a JWT access token. This token must be included in the `Authorization` header for all subsequent protected requests.

**Request Body:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "your.jwt.token",
  "token_type": "bearer"
}
```
**Header for Authenticated Requests:**
`Authorization: Bearer <your.jwt.token>`

---

## Account Management

*All endpoints require authentication.*

### `GET /api/account/balance`
Retrieves the current balance for the authenticated user.

### `GET /api/account/positions`
Fetches a list of all non-zero positions held by the user.

### `GET /api/account/trades`
Returns the user's trade history, limited to the last 100 trades by default.

### `GET /api/account/orders`
Gets a list of the user's orders. Can be filtered by status.
- **Query Parameter**: `status` (optional) - `open`, `partially_filled`, `filled`, `canceled`.

---

## Trading

*All endpoints require authentication.*

### `POST /api/trading/orders`
Places a new order on the exchange.

**Request Body:**
```json
{
  "symbol": "BTCUSD",
  "side": "buy",
  "order_type": "limit",
  "quantity": 1,
  "price": 50000.0
}
```
- `side`: "buy" or "sell"
- `order_type`: "limit" or "market"
- `price`: Required for `limit` orders.

### `DELETE /api/trading/orders/{order_id}`
Cancels an active order.

---

## Market Data

*These endpoints are public and do not require authentication.*

### `GET /api/market/data`
Retrieves market data for all available symbols.

### `GET /api/market/data/{symbol}`
Gets detailed market data for a specific symbol.

### `GET /api/market/orderbook/{symbol}`
Returns the current order book (bids and asks) for a symbol.

### `GET /api/market/trades/{symbol}`
Retrieves the most recent trades for a symbol (default limit is 50). 