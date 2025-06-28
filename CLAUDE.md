# CLAUDE.md

This file provides guidance to Claude Code when working with the nautilus_zerodha project.

## Project Overview

The `nautilus_zerodha` project is a Nautilus Trader adapter for the Zerodha KiteConnect API. It provides integration between Nautilus Trader's trading framework and Zerodha's brokerage services.

## Architecture

### Core Components

1. **api.py** - The low-level async API client
   - Handles all HTTP requests to Zerodha KiteConnect API
   - Manages authentication and rate limiting
   - Provides async methods for all API endpoints

2. **config.py** - Configuration classes
   - `ZerodhaAdapterConfig` - Main configuration class
   - Contains API credentials (api_key, access_token)
   - Environment and connection settings

3. **providers.py** - Instrument provider
   - `ZerodhaInstrumentProvider` - Translates Zerodha instruments to Nautilus format
   - First implementation priority
   - Fetches and caches instrument data

4. **data.py** - Data client (future implementation)
   - `ZerodhaDataClient` - Manages live WebSocket data
   - Historical data downloads
   - Real-time market data streaming

5. **execution.py** - Execution client (future implementation)
   - `ZerodhaExecutionClient` - Order management
   - Order placement, modification, cancellation
   - Position and portfolio tracking

6. **factories.py** - Nautilus integration factories
   - `ZerodhaLiveDataClientFactory`
   - `ZerodhaLiveExecClientFactory`
   - Required for TradingNode integration

### Package Structure

```
nautilus_zerodha/
├── __init__.py           # Package initialization, expose key classes
├── api.py               # Async API client for Zerodha
├── config.py            # Configuration classes
├── providers.py         # Instrument provider implementation
├── data.py              # Data client (future)
├── execution.py         # Execution client (future)
├── factories.py         # Nautilus factory classes
└── common/              # Shared utilities
    ├── __init__.py
    └── enums.py         # Zerodha-specific enums and constants
```

## Development Workflow

### Implementation Priority
1. **api.py** - Basic API client with authentication
2. **config.py** - Configuration classes
3. **providers.py** - Instrument provider (primary goal)
4. **data.py** - Live data client
5. **execution.py** - Execution client
6. **factories.py** - Nautilus integration

### Key Dependencies
- `nautilus-trader` - Core trading framework
- `aiohttp` - Async HTTP client for API calls
- `pytest` - Testing framework
- `pytest-asyncio` - Async testing support

### Testing Strategy
- Unit tests for each component
- Mock Zerodha API responses
- Integration tests with live API (sandbox)
- Performance tests for data streaming

## Integration with traderunner

The adapter is designed to be imported and used by the `traderunner` application:

```python
from nautilus_zerodha import ZerodhaInstrumentProvider
from nautilus_zerodha.config import ZerodhaAdapterConfig
```

## Important Notes

- All API interactions should be async
- Proper error handling for API rate limits
- Secure credential management
- Nautilus-compliant data types and formats
- Thread-safe design for live trading

## Future Enhancements

- WebSocket reconnection logic
- Advanced order types support
- Portfolio synchronization
- Risk management integration
- Performance monitoring and metrics