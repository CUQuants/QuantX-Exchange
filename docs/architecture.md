# System Architecture

The QuantX Exchange is built on a modern, modular architecture designed for performance and scalability. It consists of several key components that work together to provide a complete trading experience.

## Core Components

### 1. FastAPI Backend (`backend/`)

The core of the exchange is a Python application built with the **FastAPI** framework. It is responsible for:
- **Serving the REST API**: Exposing all endpoints for trading, account management, and market data.
- **Handling User Authentication**: Managing JWT and API key authentication.
- **Coordinating with Other Components**: Acting as the central hub that connects the API layer with the matching engine and database.

### 2. Matching Engine (`backend/matching_engine/`)

The matching engine is the heart of the exchange, responsible for processing orders and executing trades. It features:
- **In-Memory Order Books**: It maintains separate, sorted lists for buy and sell orders to ensure fast matching.
- **FIFO Matching Logic**: Orders are matched based on price-time priority (First-In, First-Out). The highest-priced buys are matched with the lowest-priced sells.
- **Asynchronous Processing**: The engine runs in its own asynchronous loop, allowing it to process orders without blocking the main application.

### 3. Database (`backend/models/`)

Data persistence is handled by a SQL database, managed via **SQLAlchemy ORM**.
- **Default Database**: The application uses **SQLite** by default for easy setup and development.
- **Production Ready**: It can be easily configured to use **PostgreSQL** or another robust SQL database for production environments.
- **Models**: The `models.py` file defines the schema for all tables, including `User`, `Order`, `Trade`, and `Position`.

### 4. WebSocket Manager (`backend/websocket_manager.py`)

Real-time communication is managed by the WebSocket handler, which:
- **Manages Connections**: Keeps track of all active client connections.
- **Broadcasts Updates**: Receives messages from the matching engine (e.g., when a trade occurs) and broadcasts them to all connected clients.

## Data Flow Diagram

### Order Placement

```
User (Client) -> FastAPI Backend -> Matching Engine -> Database
      |                  |                  |             |
      |---(Place Order)-->|                  |             |
      |                  |---(Add Order)--->|             |
      |                  |                  |--(Match?)-->| (Update Orders/Trades)
      |                  |<--(Order Update)--|             |
      |<--(Confirmation)--|                  |             |
```

### Real-Time Updates

```
Matching Engine -> WebSocket Manager -> User (Client)
       |                   |                 |
       |----(Broadcast)---->|                 |
       |                   |----(Push)------->|
``` 