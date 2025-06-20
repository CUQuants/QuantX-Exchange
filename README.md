# QuantX-Server

QuantX-Server is the backend engine for the Quantex exchange, developed and operated exclusively by CU Quants. It powers a private, single-instrument market for **CU Quants Attendance Futures (CQAF)** — a synthetic asset that reflects member participation levels across meetings and events.

This system is not intended for public deployment. It is maintained for internal use within CU Quants for the purposes of market simulation, strategy development, and microstructure experimentation.

## Features

- Centralized limit order book with FIFO matching logic
- Single-instrument market (CQAF)
- REST API for order management and data access
- Optional WebSocket feed for real-time market data
- Authentication via JWT tokens
- Logging and audit trail for all trades and events
- FastAPI + PostgreSQL stack
- Docker-compatible deployment architecture

## Usage

Only authorized CU Quants infrastructure should run this server.

To simulate trading or access the exchange, use the [`quantx-client`](https://github.com/cuquants/quantx-client) SDK. API credentials and keys are provisioned through club infrastructure.

## Development

### Prerequisites

- Python 3.9+
- PostgreSQL
- Docker (optional)
- Git

### Local Setup

```bash
git clone https://github.com/cuquants/quantx-server.git
cd quantx-server
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload
```

### Docker
```bash
docker-compose up --build
```

### Authentication
All endpoints require a valid JWT token obtained from CU Quants administration.

### License
MIT License — for CU Quants internal use only.

### Contact
```
cuquants@colorado.edu
```
