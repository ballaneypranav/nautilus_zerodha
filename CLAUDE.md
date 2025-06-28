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
- Don't remove ic imports/calls - those are for debugging

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