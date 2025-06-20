# QuantX Exchange

QuantX Exchange is a full-featured, simulated trading platform developed for financial engineering and market microstructure experimentation. It provides a robust backend, a complete API for trading and data access, and a convenient Python client library for interaction.

## Features

- **Complete Trading API**: REST endpoints for account management, market data, and order management.
- **Matching Engine**: A functional limit order book with a FIFO matching algorithm for processing market and limit orders.
- **Real-time Updates**: WebSocket support for broadcasting live trade data to connected clients.
- **User & Account Management**: Includes endpoints for checking balances, positions, and trade history.
- **Secure Authentication**: User authentication is handled via JWT, with API keys for programmatic access.
- **Python Client Library**: A pip-installable client library (`quantx_exchange_client`) to easily connect to and interact with the exchange.
- **CLI User Management**: A command-line script for easily creating and managing user accounts.

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, Uvicorn
- **Database**: SQLite (default), compatible with PostgreSQL
- **Client Library**: Requests, WebSockets
- **Security**: Passlib for hashing, PyJWT for tokens

## Project Structure

```
QuantX-Exchange/
├── backend/
│   ├── api/              # API endpoint definitions (auth, account, trading)
│   ├── matching_engine/  # Core order matching logic
│   ├── models/           # SQLAlchemy database models and initialization
│   ├── __init__.py
│   └── app.py            # Main FastAPI application
├── client_library/
│   ├── trading_client/   # The client library source code
│   ├── README.md
│   └── setup.py
├── docs/                 # (Optional) For detailed documentation
├── examples/
│   └── client_example.py # Demonstrates client library usage
├── scripts/
│   └── manage_users.py   # CLI tool for creating users
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Setup and Installation

### Prerequisites

- Python 3.9+
- Git

### Installation Steps

1.  **Clone the Repository**
    ```bash
    git clone <your-repository-url>
    cd QuantX-Exchange
    ```

2.  **Set Up a Virtual Environment**
    It's highly recommended to use a virtual environment to manage dependencies.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

---

## How to Run

### 1. Start the Exchange Backend

With your virtual environment activated, run the main application from the project root:
```bash
python run_exchange.py
```
This will start the Uvicorn server, initialize the database (`cu_quants_exchange.db`), and make the API available at `http://localhost:8000`.

- **API Docs**: View and interact with all API endpoints via the auto-generated documentation at [http://localhost:8000/docs](http://localhost:8000/docs).
- **WebSocket**: The real-time feed is available at `ws://localhost:8000/ws`.

### 2. Create a User Account

Before you can trade, you need a user account. Use the provided script to create one:
```bash
python scripts/manage_users.py <your_username> <your_email>
```
The script will prompt you to enter and confirm a password. It will then output your **API Key** and **API Secret**.

**⚠️ Important**: The API Secret is only shown once. Make sure to save it in a secure location.

### 3. Use the Python Client

The `client_library` is a pip-installable package. For development, you can use it directly as the path is already configured in the example script.

To see a full example of authenticating, fetching account data, placing, and canceling an order, run the example script:
```bash
python examples/client_example.py
```
The script will prompt you for the username and password you just created.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
