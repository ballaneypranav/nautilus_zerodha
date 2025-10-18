# CLAUDE.md

This file provides guidance to Claude Code when working with the nautilus_zerodha project.

## Project Overview

The `nautilus_zerodha` project is a Nautilus Trader adapter for the Zerodha KiteConnect API. It provides integration between Nautilus Trader's trading framework and Zerodha's brokerage services.

## Integration with TradeRunner ✨

This adapter is **fully integrated** with the traderunner application via the `NautilusFactory` class. Authentication is handled seamlessly - no manual token copying required!

**Usage from TradeRunner:**
```bash
cd ../traderunner
hatch run python main.py nautilus test-instruments  # Automatic auth + 8,387+ instruments
```

**Programmatic Usage:**
```python
from traderunner.cli import get_app_instance
from traderunner.integrations import NautilusFactory

app = get_app_instance()
factory = NautilusFactory(app)
provider = factory.create_instrument_provider()  # Auto-authenticated!
await provider.load_all_async(filters={'exchange': 'NSE'})
```

**Key Integration Features:**
- ✅ Automatic authentication via TradeRunner's OAuth flow
- ✅ Token validation and refresh handled transparently
- ✅ Exchange-level filtering (NSE, BSE, NFO, BFO, etc.)
- ✅ 8,387+ NSE instruments successfully loaded
- ✅ Rich CLI output with tables and panels

## Architecture

### Core Components

1. **api.py** - The low-level async API client
   - Uses official `kiteconnect` Python SDK for API calls
   - Manages authentication via API key and access token
   - Currently implements `get_all_instruments_async()` for fetching instruments
   - Authentication validated on initialization via `validate_access_token()`

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
└── common/              # Shared utilities (not yet implemented)
    ├── __init__.py
    ├── enums.py         # Zerodha-specific enums and constants
    └── instrument.py    # Instrument-related utilities
```

### Authentication Flow

The authentication flow in api.py:14-23 works as follows:

1. Create `ZerodhaAdapterConfig` with `api_key` and `access_token`
2. `ZerodhaAPIClient.__init__()` creates a `KiteConnect` instance with the API key
3. Sets the access token on the KiteConnect instance
4. Calls `validate_access_token()` which fetches the user profile to verify the token
5. If validation succeeds, sets `self.authenticated = True`
6. If validation fails, raises `RuntimeError`

**Important:** The access token must be obtained separately (via OAuth flow). This adapter does not handle the OAuth flow - it expects a valid access token to be provided.

### Filtering Instruments

The `load_all_async()` method supports optional filtering via the `filters` parameter (providers.py:210-214):

```python
# Load only NSE equity instruments
await provider.load_all_async(filters={
    'exchange': 'NSE',
    'instrument_type': 'EQ'
})

# Load multiple instrument types
await provider.load_all_async(filters={
    'exchange': ['NSE', 'BSE'],
    'instrument_type': ['EQ', 'FUT']
})
```

The `_matches_filters()` method (providers.py:230-240) supports both single values and lists of values for filtering.

### Instrument Mapping Architecture

The `ZerodhaInstrumentProvider` in providers.py:173-264 maps Zerodha instruments to Nautilus instrument types:

**Zerodha → Nautilus Type Mapping:**
- `instrument_type: "EQ"` → `Equity` (stocks on NSE/BSE)
- `instrument_type: "FUT"` → `FuturesContract` (index/equity futures)
- `instrument_type: "CE"` → `OptionsContract` with `OptionKind.CALL`
- `instrument_type: "PE"` → `OptionsContract` with `OptionKind.PUT`

**Key Field Mappings:**
- `tradingsymbol` → `Symbol` (e.g., "INFY", "NIFTY25JAN25FUT")
- `exchange` → `Venue` (e.g., "NSE", "NFO", "BFO")
- `tick_size` → `price_increment` and `price_precision`
- `lot_size` → `size_increment` and `multiplier`
- `expiry` → `expiration_ns` (for derivatives, converted to nanoseconds)
- `strike` → `strike_price` (for options)

**Zerodha Raw Instrument Format:**
```python
{
    'exchange': 'BFO',
    'exchange_token': '824914',
    'expiry': datetime.date(2025, 7, 8),
    'instrument_token': 211177989,
    'instrument_type': 'FUT',
    'last_price': 0.0,
    'lot_size': 20,
    'name': 'SENSEX',
    'segment': 'BFO-FUT',
    'strike': 0.0,
    'tick_size': 0.05,
    'tradingsymbol': 'SENSEX25708FUT'
}
```

## Development Workflow

### Project Configuration

The project uses setuptools with pyproject.toml for package management:
- Python 3.8+ required (pyproject.toml:12)
- Black line length: 88 characters (pyproject.toml:31-33)
- isort configured with black profile (pyproject.toml:35-37)
- mypy type checking enabled with strict settings (pyproject.toml:39-43)

### Key Commands

**Installation:**
```bash
# Install package in development mode
pip install -e .

# Install with development dependencies (recommended)
pip install -e ".[dev]"
```

**Testing:**
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_providers.py

# Run with verbose output
python -m pytest -v

# Run with async support (required for this project)
python -m pytest -v --asyncio-mode=auto

# Run tests with coverage
pytest --cov=nautilus_zerodha tests/
```

**Code Quality:**
```bash
# Format code with black
black nautilus_zerodha/

# Sort imports
isort nautilus_zerodha/

# Type checking
mypy nautilus_zerodha/
```

### Implementation Priority
1. **api.py** - Basic API client with authentication (✓ IMPLEMENTED)
2. **config.py** - Configuration classes (✓ IMPLEMENTED)
3. **providers.py** - Instrument provider (✓ IMPLEMENTED - primary goal)
4. **data.py** - Live data client (TODO)
5. **execution.py** - Execution client (TODO)
6. **factories.py** - Nautilus integration (TODO)

### Key Dependencies
- `nautilus-trader` - Core trading framework
- `kiteconnect` - Official Zerodha KiteConnect SDK (used by api.py for synchronous API calls)
- `aiohttp` - Async HTTP client (declared in pyproject.toml but not actively used yet)
- `pandas` - Data manipulation (used in providers.py for timestamp handling)
- `icecream` - Debugging output (used throughout for development debugging - DO NOT REMOVE `ic` calls)
- `pytest` - Testing framework (dev dependency)
- `pytest-asyncio` - Async testing support (dev dependency)
- `black` - Code formatting (dev dependency)
- `isort` - Import sorting (dev dependency)
- `mypy` - Type checking (dev dependency)

### Testing Strategy
- Unit tests for each component (in tests/ directory)
- Mock Zerodha API responses
- Integration tests with live API (sandbox)
- Performance tests for data streaming

## Integration with traderunner

The adapter is designed to be imported and used by the `traderunner` application:

```python
from nautilus_zerodha import ZerodhaInstrumentProvider, ZerodhaAPIClient, ZerodhaAdapterConfig

# Create configuration
config = ZerodhaAdapterConfig(
    api_key="your_api_key",
    access_token="your_access_token"
)

# Create API client
client = ZerodhaAPIClient(config)

# Create instrument provider
provider = ZerodhaInstrumentProvider(client)

# Load instruments
await provider.load_all_async()

# Find specific instrument
instrument = provider.find(InstrumentId.from_str("INFY.NSE"))
```

See implementation_guide.md for detailed usage patterns.

## Important Notes

### Current Implementation State
- **api.py**: Fully functional implementation using `kiteconnect` SDK. The `get_all_instruments_async()` supports exchange-level filtering for efficient API calls. Note: Uses synchronous `kiteconnect` SDK wrapped in async methods.
- **providers.py**: Fully implemented with support for EQ, FUT, CE, and PE instrument types. Includes comprehensive error handling and logging.
- **config.py**: Two config classes defined - `ZerodhaAdapterConfig` (inherits from `NautilusConfig`) and `ZerodhaInstrumentProviderConfig` (inherits from `InstrumentProviderConfig`)
- **data.py, execution.py, factories.py**: Empty stub files - not yet implemented
- **common/enums.py, common/instrument.py**: Empty stub files - not yet implemented
- **tests/**: Test files exist but are empty - no tests written yet

### Development Guidelines

**Code Style:**
- All API interactions should be async (even if wrapping sync calls)
- Use type hints consistently (mypy is configured in pyproject.toml:40-43)
- **Don't remove `ic` imports/calls** - those are for debugging with icecream library
- Follow black formatting (line-length = 88, target Python 3.8+)

**Nautilus Integration:**
- Nautilus-compliant data types and formats (use `Price`, `Quantity`, `InstrumentId`, etc.)
- Timestamps must be in nanoseconds for Nautilus (`ts_event`, `ts_init`, `expiration_ns`, `activation_ns`)
- Use `INR` currency constant from `nautilus_trader.model.currencies` for all Indian instruments
- Configuration classes should inherit from Nautilus base classes (`NautilusConfig`, `InstrumentProviderConfig`)

**Error Handling:**
- The `_create_nautilus_instrument()` method (providers.py:51-171) handles all type conversions and error cases
- Log warnings for unsupported instrument types, missing fields, or invalid data
- Return `None` from `_create_nautilus_instrument()` on errors (don't crash the entire load)
- Use proper exception types (`RuntimeError` for auth failures, etc.)

**Security:**
- Never hardcode credentials
- Credentials should come from config or environment variables
- Proper error handling for API rate limits (not yet implemented)

### Known Limitations
- `load_async()` and `load_ids_async()` methods in providers.py load all instruments instead of specific ones (optimization TODO)
- WebSocket support not yet implemented
- No live data streaming or execution capabilities yet
- The `kiteconnect` SDK used in api.py is synchronous - async methods are wrappers around sync calls
- No test coverage yet - test files are empty stubs
- Instrument indices (NIFTY 50, etc.) with tick_size=0.0 are skipped (validation error)

### Debugging

**Icecream Debug Output:**
- The project uses `icecream` library for debug output (imported as `ic`)
- Debug statements in providers.py:217-219 show raw instrument data and converted Nautilus instruments
- Do NOT remove `ic` imports or calls - they're intentional for development

**Common Issues:**
- **Authentication Errors:** Ensure access token is valid and not expired. The token must be obtained through Zerodha's OAuth flow separately.
- **Type Conversion Errors:** Check providers.py `_create_nautilus_instrument()` logs for warnings about missing fields or invalid data
- **Missing Instruments:** If instruments aren't loading, check the filtering logic in `_matches_filters()` and ensure raw data format matches expected structure
- **Async Issues:** Remember that `kiteconnect` SDK is sync - all async methods are wrappers

## Nautilus Documentation Guidelines

### CRITICAL: Never Read Entire nautilus_docs Directory

**NEVER read the entire nautilus_docs directory without targeted searching.** The directory contains extensive documentation that must be searched efficiently using keywords.

### Documentation Structure

- `nautilus_docs/keywords.txt` - Complete keyword list for searching
- `nautilus_docs/code/` - Code snippets with structured format
- `nautilus_docs/manual/` - Comprehensive documentation (api_reference, concepts, dev_guide, getting_started, integrations, tutorials)

### Search Strategy

1. **Think of relevant keywords** before searching
2. **Use Grep tool** to search for specific keywords in nautilus_docs
3. **Read only relevant files** found through keyword searches
4. **Use multiple keyword combinations** for comprehensive coverage

### Code Snippet Format

Code snippets in `nautilus_docs/code/` follow this format:
```
TITLE: Processing Pandas DataFrame into NautilusTrader QuoteTick Objects (Python)
DESCRIPTION: This code block initializes a QuoteTickDataWrangler for the EUR/USD instrument using a test instrument provider...
SOURCE: docs/getting_started/backtest_high_level.ipynb
LANGUAGE: Python
KEYWORDS: FX,QuoteTick,QuoteTickDataWrangler,TestInstrumentProvider,data handling,data type:tick,data:wrangling,instrument,library:pandas
CODE:
```
# Process quotes using a wrangler
EURUSD = TestInstrumentProvider.default_fx_ccy("EUR/USD")
wrangler = QuoteTickDataWrangler(EURUSD)
ticks = wrangler.process(df)
ticks[0:2]
```
```

### Available Keywords

account, account ID, account state, account type, activation price, active blocks, actor, ActorConfig, adapters, add, add_exec_algorithm, add_instrument, add_strategy, add_synthetic, add_venue, algorithm:execution, algorithm:TWAP, all, allowance, annotations, API, API client, API credentials, apt-get, architecture, Arrow, assertion, asset type, async, attributes, authentication, backtest, BacktestDataConfig, BacktestEngine, BacktestEngineConfig, backtesting, BacktestNode, BacktestResult, BacktestRunConfig, BacktestVenueConfig, bail, balance, bar, Bar, BarAggregation, BarType, batch, behavior, benchmark, beta, Betfair, Binance, BinanceBar, BinanceFuturesMarkPriceUpdate, BinanceOrderBookDeltaDataLoader, BinanceTicker, binary data, binary options, blockchain, blocks, bond, build, build process, build speed, building, Bybit, BybitOrderBookDeltaDataLoader, bytes, C API, cache, CacheConfig, calculation, capacity, cargo, cargo test, cargo-nextest, Cargo.toml, case, cash account, certificate, chaining, change_formula, clang, class definition, clean, CLI, client order ID, client:data, client:execution, client:factory, ClientId, ClientOrderId, clock, close position, code quality, codspeed, Coinbase, commission, compatibility, compilation, component, components, composite bar, compression, configuration, configuration:environment-variables, constants, constructor, constructors, consumer, continuous, continuous timer, convention, conversion, copyright, correctness, cost estimation, count, Cranelift, create, CREATE DATABASE, crypto, cryptocurrency, CryptoPerpetual, CSV, CSVTickDataLoader, currency, CurrencyPair, Currenex, customdataclass, customization, Data, data catalog, data format, data handling, data partitioning, data quality, data streaming, data subscription, data type:custom, data type:delta, data type:historical, data type:live, data type:market-data, data type:order-book, data type:order-book-delta, data type:order-book-depth, data type:tick, data types, data:add, data:aggregation, data:export, data:loading, data:persistence, data:sample, data:wrangling, DatabaseConfig, Databento, DatabentoDataLoader, DataClient, DataEngine, DataFusion, dataset, dataset condition, dataset range, datasets, DataType, datetime, DBN, DBNStore, debugging, decorator, decoupled communication, definition, delta, demo, dependencies, derivatives, derive, dev:API-design, dev:best-practice, dev:build, dev:cli, dev:coding-standards, dev:dependencies, dev:documentation, dev:environment, dev:environment:virtual, dev:error-handling, dev:extras, dev:imports, dev:installation, dev:package-index, dev:package-index:github, dev:package-index:pypi, dev:package-management, dev:profiling, dev:recompile, dev:release-type:binary, dev:release-type:development, dev:release-type:pre-release, dev:release-type:stable, dev:source-build, dev:testing, dev:tooling, dev:verification, development, DEX, diagram, direct access, directional trading, directory management, directory path, discover instruments, discovery, display, display options, dispose, DockerizedIBGateway, documentation, documentation:API-goals, documentation:API-reference, dYdX, DYDXOrderTags, EMACross, EMACrossConfig, EMACrossTWAP, EMACrossTWAPConfig, emulation, encoding, engine, enum, enums, equity, errors, Ethereum, event handling, example, example output, exchange, exec_spawn_id, ExecAlgorithmId, execution, execution instructions, execution state, ExecutionClient, expect, expiry, exposure, external stream, FAILED, failure seed, feature flag, feature flags, feature:128-bit, feature:64-bit, feature:adaptive-bar-ordering, feature:advanced-orders, feature:debug-mode, feature:early-return, feature:hedge-mode, feature:high-precision, feature:multi-venue, feature:new, feature:new_checked, feature:order-fill-simulation, feature:pending-update, feature:post-only, feature:rollover-interest, feature:shared-data, feature:standard-precision, feature:type-filter, features, fee model, field access, fields, file format, file naming, file path, file system, FillModel, find, FOK, forex, format, formatting, formula, from_bytes, from_dict, from_env, from_file, function, functions, funder, future, futures, futures chain, FX, FXRolloverInterestModule, gateway, generate, generic event, generics, get, get_record_count, git, Greeks, GreeksCalculator, GreeksData, GTC, GTD, gzip, handler, handler:on_bar, handler:on_data, handler:on_event, handler:on_historical_data, handler:on_instrument, handler:on_load, handler:on_order, handler:on_order_accepted, handler:on_order_book, handler:on_order_canceled, handler:on_order_filled, handler:on_position_changed, handler:on_position_closed, handler:on_position_opened, handler:on_quote_tick, handler:on_save, handler:on_signal, handler:on_start, handler:on_stop, handler:on_trade_tick, header, historical data, HistoricInteractiveBrokersClient, HTTP client, hypersync, IB_VENUE, IBContract, IDE, IDE support, IDE:AstroNvim, IDE:Neovim, image, imbalance, impl, ImportableStrategyConfig, indicator, indicator:MACD, inheritance, init_logging, initial margin, initialization, inline block, inspection, install, instrument, instrument class, instrument ID, instrument provider, instrument:synthetic, instrument_greeks, InstrumentId, InstrumentProvider, InstrumentProviderConfig, integration, integration:Betfair, integration:Databento, integration:Interactive-Brokers, Interactive Brokers, InteractiveBrokersDataClientConfig, InteractiveBrokersExecClientConfig, InteractiveBrokersInstrumentProviderConfig, interface, inverse, IOC, is_emulated, ISO 8601, iteration, JSON, json, key structure, key-value store, L2, L3, language:lua, language:rust, LD_LIBRARY_PATH, leverage, library:anyhow, library:numpy, library:pandas, library:pytz, library:rstest, library:thiserror, license, lifecycle, lightweight messaging, limit order, limitations, linear, Linux, list, list_datasets, list_publishers, list_schemas, live, live dashboard, live trading, LiveDataClient, LiveDataClientConfig, LiveExecClientConfig, LiveExecutionClient, LiveMarketDataClient, load all, load by ID, localization, locked balance, log level, Logger, logging, LoggingConfig, LogGuard, LSP, MACDStrategy, maintenance margin, make, make_price, make_qty, mapping, margin, margin account, margin mode, mark price, markdown, market data, market order, MBO, MBP, memory, memray, message bus, MessageBusConfig, metadata, MIC, mnemonic, module, modules, Money, msgpack, multiple instances, multiple runs, naming conventions, nanosecond, nanoseconds, nautilus_model, nightly, normalization, OHLCV, OOP, option, options, options chain, order, order execution, order expiry, order fills, order management, order modification, order report, order state, order type:conditional, order type:emulated, order type:limit, order type:limit-if-touched, order type:long-term, order type:market, order type:market-if-touched, order type:market-to-limit, order type:primary, order type:short-term, order type:stop, order type:stop-limit, order type:stop-market, order type:trailing-stop, order type:trailing-stop-limit, order type:trailing-stop-market, order types, order:cancel, order:create, order:modify, order_id_tag, OrderBookDelta, OrderBookDeltaDataWrangler, OrderBookDepth10, OrderBookImbalance, OrderFactory, OrderSide, panics, parameterization, parameterized tests, parent, Parquet, ParquetDataCatalog, patch, path, pathlib, PerContractFeeModel, performance, perpetuals, persistence, PgAdmin, pickle, PnL, Polymarket, portfolio, portfolio ID, PortfolioAnalyzer, PortfolioStatistic, position, Position, position ID, position mode, position report, position_ids, PositionId, PositionSide, post_only, PostgreSQL, PowerShell, pre-commit, price, Price, PriceType, private key, probabilistic fill, process lifecycle, producer, product type, proptest, psql, publish-subscribe, publishers, pull, PyArrow, pyclass, PyO3, pyo3, pytest, Quantity, quantity, query, QuoteTick, QuoteTickDataWrangler, raw_symbol, re-exports, read_table, realized PnL, reconciliation, record count, Redis, reduce_only, register, register_parquet, register_serializable_type, replay, reporting & analysis, reproducibility, request_aggregated_bars, RequestInstrument, reset, resolve, resource management, Result, results, RFC 3339, RFC 4122, risk engine, rotation, routing, row limit, RPC, rpc, rstest, run, rust-analyzer, SAFETY, scheduling, schema, schemas, SCREAMING_SNAKE_CASE, script, security, serialization, SessionContext, setup, shutil, signal, signature type, simulation, skip-worktree, slippage, slippage protection, smart contract, snapshot, spot, spot trading, spread calculation, SPX, SQL, stable, standalone, standard bar, start, start service, state management, statistic:win-rate, statistics, status, status check, stock, stop, stop limit order, stop order, strategy, strategy:EMA-cross, StrategyConfig, StrategyId, streams, string conversion, struct, structs, strum, stubs, style guide, subaccount, supported features, supported types, supported venues, symbol, symbol:EURUSD, symbology, sync, tables, Tardis, TardisCSVDataLoader, tech:database, tech:docker, tech:docker-compose, tech:http-client, tech:jupyter, tech:redis, technology, template, test, test structure, testing, TestInstrumentProvider, testnet, Text, throttler, tick, time range, TimeEvent, TimeInForce, timer, timestamp, timezone, to_dict, TOBQuoterConfig, tokio, trade status, trades, TradeTick, TradeTickDataWrangler, trading logic, TradingNode, TradingNodeConfig, trailing stop order, trait, trigger, TriggerType, ts_event, ts_init, TSLA, TWAP, TWAPExecAlgorithm, type hints, TypeVar, underlying, unique ID, Uniswap V3, unix, unsafe, update, UTC, UUID, validation, variants, venue, venue filter, venue:simulated, version, versions, VSCode, wallet, warnings, WebSocket, Windows, WinRate, workspace, ZST

## Future Enhancements

- WebSocket reconnection logic
- Advanced order types support
- Portfolio synchronization
- Risk management integration
- Performance monitoring and metrics