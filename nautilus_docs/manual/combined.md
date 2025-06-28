file path: ./integrations/tardis.md
# Tardis

Tardis provides granular data for cryptocurrency markets including tick-by-tick order book snapshots & updates,
trades, open interest, funding rates, options chains and liquidations data for leading crypto exchanges.

NautilusTrader provides an integration with the Tardis API and data formats, enabling seamless access.
The capabilities of this adapter include:

- `TardisCSVDataLoader`: Reads Tardis-format CSV files and converts them into Nautilus data.
- `TardisMachineClient`: Supports live streaming and historical replay of data from the Tardis Machine WebSocket server - converting messages into Nautilus data.
- `TardisHttpClient`: Requests instrument definition metadata from the Tardis HTTP API, parsing it into Nautilus instrument definitions.
- `TardisDataClient`: Provides a live data client for subscribing to data streams from a Tardis Machine WebSocket server.
- `TardisInstrumentProvider`: Provides instrument definitions from Tardis through the HTTP instrument metadata API.
- **Data pipeline functions**: Enables replay of historical data from Tardis Machine and writes it to the Nautilus Parquet format, including direct catalog integration for streamlined data management (see below).

:::info
A Tardis API key is required for the adapter to operate correctly. See also [environment variables](#environment-variables).
:::

## Overview

This adapter is implemented in Rust, with optional Python bindings for ease of use in Python-based workflows.
It does not require any external Tardis client library dependencies.

:::info
There is **no** need for additional installation steps for `tardis`.
The core components of the adapter are compiled as static libraries and automatically linked during the build process.
:::

## Tardis documentation

Tardis provides extensive user [documentation](https://docs.tardis.dev/).
We recommend also referring to the Tardis documentation in conjunction with this NautilusTrader integration guide.

## Supported formats

Tardis provides *normalized* market data—a unified format consistent across all supported exchanges.
This normalization is highly valuable because it allows a single parser to handle data from any [Tardis-supported exchange](#venues), reducing development time and complexity.
As a result, NautilusTrader will not support exchange-native market data formats, as it would be inefficient to implement separate parsers for each exchange at this stage.

The following normalized Tardis formats are supported by NautilusTrader:

| Tardis format                                                                                                               | Nautilus data type                                                   |
|:----------------------------------------------------------------------------------------------------------------------------|:---------------------------------------------------------------------|
| [book_change](https://docs.tardis.dev/api/tardis-machine#book_change)                                                       | `OrderBookDelta`                                                     |
| [book_snapshot_*](https://docs.tardis.dev/api/tardis-machine#book_snapshot_-number_of_levels-_-snapshot_interval-time_unit) | `OrderBookDepth10`                                                   |
| [quote](https://docs.tardis.dev/api/tardis-machine#book_snapshot_-number_of_levels-_-snapshot_interval-time_unit)           | `QuoteTick`                                                          |
| [quote_10s](https://docs.tardis.dev/api/tardis-machine#book_snapshot_-number_of_levels-_-snapshot_interval-time_unit)       | `QuoteTick`                                                          |
| [trade](https://docs.tardis.dev/api/tardis-machine#trade)                                                                   | `Trade`                                                              |
| [trade_bar_*](https://docs.tardis.dev/api/tardis-machine#trade_bar_-aggregation_interval-suffix)                            | `Bar`                                                                |
| [instrument](https://docs.tardis.dev/api/instruments-metadata-api)                                                          | `CurrencyPair`, `CryptoFuture`, `CryptoPerpetual`, `OptionContract` |
| [derivative_ticker](https://docs.tardis.dev/api/tardis-machine#derivative_ticker)                                           | *Not yet supported*                                                  |
| [disconnect](https://docs.tardis.dev/api/tardis-machine#disconnect)                                                         | *Not applicable*                                                     |

**Notes:**

- [quote](https://docs.tardis.dev/api/tardis-machine#book_snapshot_-number_of_levels-_-snapshot_interval-time_unit) is an alias for [book_snapshot_1_0ms](https://docs.tardis.dev/api/tardis-machine#book_snapshot_-number_of_levels-_-snapshot_interval-time_unit).
- [quote_10s](https://docs.tardis.dev/api/tardis-machine#book_snapshot_-number_of_levels-_-snapshot_interval-time_unit) is an alias for [book_snapshot_1_10s](https://docs.tardis.dev/api/tardis-machine#book_snapshot_-number_of_levels-_-snapshot_interval-time_unit).
- Both quote, quote\_10s, and one-level snapshots are parsed as `QuoteTick`.

:::info
See also the Tardis [normalized market data APIs](https://docs.tardis.dev/api/tardis-machine#normalized-market-data-apis).
:::

## Bars

The adapter will automatically convert [Tardis trade bar interval and suffix](https://docs.tardis.dev/api/tardis-machine#trade_bar_-aggregation_interval-suffix) to Nautilus `BarType`s.
This includes the following:

| Tardis suffix                                                                                                | Nautilus bar aggregation    |
|:-------------------------------------------------------------------------------------------------------------|:----------------------------|
| [ms](https://docs.tardis.dev/api/tardis-machine#trade_bar_-aggregation_interval-suffix) - milliseconds       | `MILLISECOND`               |
| [s](https://docs.tardis.dev/api/tardis-machine#trade_bar_-aggregation_interval-suffix) - seconds             | `SECOND`                    |
| [m](https://docs.tardis.dev/api/tardis-machine#trade_bar_-aggregation_interval-suffix) - minutes             | `MINUTE`                    |
| [ticks](https://docs.tardis.dev/api/tardis-machine#trade_bar_-aggregation_interval-suffix) - number of ticks | `TICK`                      |
| [vol](https://docs.tardis.dev/api/tardis-machine#trade_bar_-aggregation_interval-suffix) - volume size       | `VOLUME`                    |

## Symbology and normalization

The Tardis integration ensures seamless compatibility with NautilusTrader’s crypto exchange adapters
by consistently normalizing symbols. Typically, NautilusTrader uses the native exchange naming conventions
provided by Tardis. However, for certain exchanges, raw symbols are adjusted to adhere to the Nautilus symbology normalization, as outlined below:

### Common Rules

- All symbols are converted to uppercase.
- Market type suffixes are appended with a hyphen for some exchanges (see [exchange-specific normalizations](#exchange-specific-normalizations)).
- Original exchange symbols are preserved in the Nautilus instrument definitions `raw_symbol` field.

### Exchange-Specific Normalizations

- **Binance**: Nautilus appends the suffix `-PERP` to all perpetual symbols.
- **Bybit**: Nautilus uses specific product category suffixes, including `-SPOT`, `-LINEAR`, `-INVERSE`, `-OPTION`.
- **dYdX**: Nautilus appends the suffix `-PERP` to all perpetual symbols.
- **Gate.io**: Nautilus appends the suffix `-PERP` to all perpetual symbols.

For detailed symbology documentation per exchange:

- [Binance symbology](./binance.md#symbology)
- [Bybit symbology](./bybit.md#symbology)
- [dYdX symbology](./dydx.md#symbology)

## Venues

Some exchanges on Tardis are partitioned into multiple venues.
The table below outlines the mappings between Nautilus venues and corresponding Tardis exchanges, as well as the exchanges that Tardis supports:

| Nautilus venue          | Tardis exchange(s)                                    |
|:------------------------|:------------------------------------------------------|
| `ASCENDEX`              | `ascendex`                                            |
| `BINANCE`               | `binance`, `binance-dex`, `binance-european-options`, `binance-futures`, `binance-jersey`, `binance-options` |
| `BINANCE_DELIVERY`      | `binance-delivery` (*COIN-margined contracts*)        |
| `BINANCE_US`            | `binance-us`                                          |
| `BITFINEX`              | `bitfinex`, `bitfinex-derivatives`                    |
| `BITFLYER`              | `bitflyer`                                            |
| `BITGET`                | `bitget`, `bitget-futures`                            |
| `BITMEX`                | `bitmex`                                              |
| `BITNOMIAL`             | `bitnomial`                                           |
| `BITSTAMP`              | `bitstamp`                                            |
| `BLOCKCHAIN_COM`        | `blockchain-com`                                      |
| `BYBIT`                 | `bybit`, `bybit-options`, `bybit-spot`                |
| `COINBASE`              | `coinbase`                                            |
| `COINBASE_INTX`         | `coinbase-international`                              |
| `COINFLEX`              | `coinflex` (*for historical research*)                |
| `CRYPTO_COM`            | `crypto-com`, `crypto-com-derivatives`                |
| `CRYPTOFACILITIES`      | `cryptofacilities`                                    |
| `DELTA`                 | `delta`                                               |
| `DERIBIT`               | `deribit`                                             |
| `DYDX`                  | `dydx`                                                |
| `DYDX_V4`               | `dydx-v4`                                             |
| `FTX`                   | `ftx`, `ftx-us` (*historical research*)               |
| `GATE_IO`               | `gate-io`, `gate-io-futures`                          |
| `GEMINI`                | `gemini`                                              |
| `HITBTC`                | `hitbtc`                                              |
| `HUOBI`                 | `huobi`, `huobi-dm`, `huobi-dm-linear-swap`, `huobi-dm-options` |
| `HUOBI_DELIVERY`        | `huobi-dm-swap`                                       |
| `HYPERLIQUID`           | `hyperliquid`                                         |
| `KRAKEN`                | `kraken`, `kraken-futures`                            |
| `KUCOIN`                | `kucoin`, `kucoin-futures`                            |
| `MANGO`                 | `mango`                                               |
| `OKCOIN`                | `okcoin`                                              |
| `OKEX`                  | `okex`, `okex-futures`, `okex-options`, `okex-spreads`, `okex-swap` |
| `PHEMEX`                | `phemex`                                              |
| `POLONIEX`              | `poloniex`                                            |
| `SERUM`                 | `serum` (*historical research*)                       |
| `STARATLAS`             | `staratlas`                                           |
| `UPBIT`                 | `upbit`                                               |
| `WOO_X`                 | `woo-x`                                               |

## Environment variables

The following environment variables are used by Tardis and NautilusTrader.

- `TM_API_KEY`: API key for the Tardis Machine.
- `TARDIS_API_KEY`: API key for NautilusTrader Tardis clients.
- `TARDIS_MACHINE_WS_URL` (optional): WebSocket URL for the `TardisMachineClient` in NautilusTrader.
- `TARDIS_BASE_URL` (optional): Base URL for the `TardisHttpClient` in NautilusTrader.
- `NAUTILUS_CATALOG_PATH` (optional): Root directory for writing replay data in the Nautilus catalog.

## Running Tardis Machine historical replays

The [Tardis Machine Server](https://docs.tardis.dev/api/tardis-machine) is a locally runnable server
with built-in data caching, providing both tick-level historical and consolidated real-time cryptocurrency market data through HTTP and WebSocket APIs.

You can perform complete Tardis Machine WebSocket replays of historical data and output the results
in Nautilus Parquet format, using either Python or Rust. Since the function is implemented in Rust,
performance is consistent whether run from Python or Rust, letting you choose based on your preferred workflow.

The end-to-end `run_tardis_machine_replay` data pipeline function utilizes a specified [configuration](#configuration) to execute the following steps:

- Connect to the Tardis Machine server.
- Request and parse all necessary instrument definitions from the [Tardis instruments metadata](https://docs.tardis.dev/api/instruments-metadata-api) HTTP API.
- Stream all requested instruments and data types for the specified time ranges from the Tardis Machine server.
- For each instrument, data type and date (UTC), generate a `.parquet` file in the Nautilus format.
- Disconnect from the Tardis Marchine server, and terminate the program.

:::note
You can request data for the first day of each month without an API key. For all other dates, a Tardis Machine API key is required.
:::

This process is optimized for direct output to a Nautilus Parquet data catalog.
Ensure that the `NAUTILUS_CATALOG_PATH` environment variable is set to the root `/catalog/` directory.
Parquet files will then be organized under `/catalog/data/` in the expected subdirectories corresponding to data type and instrument.

If no `output_path` is specified in the configuration file and the `NAUTILUS_CATALOG_PATH` environment variable is unset, the system will default to the current working directory.

### Procedure

First, ensure the `tardis-machine` docker container is running. Use the following command:

```bash
docker run -p 8000:8000 -p 8001:8001 -e "TM_API_KEY=YOUR_API_KEY" -d tardisdev/tardis-machine
```

This command starts the `tardis-machine` server without a persistent local cache, which may affect performance.
For improved performance, consider running the server with a persistent volume. Refer to the [Tardis Docker documentation](https://docs.tardis.dev/api/tardis-machine#docker) for details.

### Configuration

Next, ensure you have a configuration JSON file available.

**Configuration JSON format**

| Field               | Type              | Description                                                                         | Default                                                                                               |
|:--------------------|:------------------|:------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------|
| `tardis_ws_url`     | string (optional) | The Tardis Machine WebSocket URL.                                                   | If `null` then will use the `TARDIS_MACHINE_WS_URL` env var.                                          |
| `normalize_symbols` | bool (optional)   | If Nautilus [symbol normalization](#symbology-and-normalization) should be applied. | If `null` then will default to `true`.                                                                |
| `output_path`       | string (optional) | The output directory path to write Nautilus Parquet data to.                        | If `null` then will use the `NAUTILUS_CATALOG_PATH` env var, otherwise the current working directory. |
| `options`           | JSON[]            | An array of [ReplayNormalizedRequestOptions](https://docs.tardis.dev/api/tardis-machine#replay-normalized-options) objects.                                                                 |

An example configuration file, `example_config.json`, is available [here](https://github.com/nautechsystems/nautilus_trader/blob/develop/crates/adapters/tardis/bin/example_config.json):

```json
{
  "tardis_ws_url": "ws://localhost:8001",
  "output_path": null,
  "options": [
    {
      "exchange": "bitmex",
      "symbols": [
        "xbtusd",
        "ethusd"
      ],
      "data_types": [
        "trade"
      ],
      "from": "2019-10-01",
      "to": "2019-10-02"
    }
  ]
}
```

### Python Replays

To run a replay in Python, create a script similar to the following:

```python
import asyncio

from nautilus_trader.core import nautilus_pyo3


async def run():
    config_filepath = Path("YOUR_CONFIG_FILEPATH")
    await nautilus_pyo3.run_tardis_machine_replay(str(config_filepath.resolve()))


if __name__ == "__main__":
    asyncio.run(run())
```

### Rust Replays

To run a replay in Rust, create a binary similar to the following:

```rust
use std::{env, path::PathBuf};

use nautilus_adapters::tardis::replay::run_tardis_machine_replay_from_config;

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::DEBUG)
        .init();

    let config_filepath = PathBuf::from("YOUR_CONFIG_FILEPATH");
    run_tardis_machine_replay_from_config(&config_filepath).await;
}
```

Make sure to enable Rust logging by exporting the following environment variable:

```bash
export RUST_LOG=debug
```

A working example binary can be found [here](https://github.com/nautechsystems/nautilus_trader/blob/develop/crates/adapters/tardis/bin/example_replay.rs).

This can also be run using cargo:

```bash
cargo run --bin tardis-replay <path_to_your_config>
```

## Loading Tardis CSV data

Tardis-format CSV data can be loaded using either Python or Rust. The loader reads the CSV text data
from disk and parses it into Nautilus data. Since the loader is implemented in Rust, performance remains
consistent regardless of whether you run it from Python or Rust, allowing you to choose based on your preferred workflow.

You can also optionally specify a `limit` parameter for the `load_*` functions/methods to control the maximum number of rows loaded.

:::note
Loading mixed-instrument CSV files is challenging due to precision requirements and is not recommended. Use single-instrument CSV files instead (see below).
:::

### Loading CSV Data in Python

You can load Tardis-format CSV data in Python using the `TardisCSVDataLoader`.
When loading data, you can optionally specify the instrument ID but must specify both the price precision, and size precision.
Providing the instrument ID improves loading performance, while specifying the precisions is required, as they cannot be inferred from the text data alone.

To load the data, create a script similar to the following:

```python
from nautilus_trader.adapters.tardis import TardisCSVDataLoader
from nautilus_trader.model import InstrumentId


instrument_id = InstrumentId.from_str("BTC-PERPETUAL.DERIBIT")
loader = TardisCSVDataLoader(
    price_precision=1,
    size_precision=0,
    instrument_id=instrument_id,
)

filepath = Path("YOUR_CSV_DATA_PATH")
limit = None

deltas = loader.load_deltas(filepath, limit)
```

### Loading CSV Data in Rust

You can load Tardis-format CSV data in Rust using the loading functions found [here](https://github.com/nautechsystems/nautilus_trader/blob/develop/crates/adapters/tardis/src/csv/mod.rs).
When loading data, you can optionally specify the instrument ID but must specify both the price precision and size precision.
Providing the instrument ID improves loading performance, while specifying the precisions is required, as they cannot be inferred from the text data alone.

For a complete example, see the [example binary here](https://github.com/nautechsystems/nautilus_trader/blob/develop/crates/adapters/tardis/bin/example_csv.rs).

To load the data, you can use code similar to the following:

```rust
use std::path::Path;

use nautilus_adapters::tardis;
use nautilus_model::identifiers::InstrumentId;

#[tokio::main]
async fn main() {
    // You must specify precisions and the CSV filepath
    let price_precision = 1;
    let size_precision = 0;
    let filepath = Path::new("YOUR_CSV_DATA_PATH");

    // Optionally specify an instrument ID and/or limit
    let instrument_id = InstrumentId::from("BTC-PERPETUAL.DERIBIT");
    let limit = None;

    // Consider propagating any parsing error depending on your workflow
    let _deltas = tardis::csv::load_deltas(
        filepath,
        price_precision,
        size_precision,
        Some(instrument_id),
        limit,
    )
    .unwrap();
}
```

## Requesting instrument definitions

You can request instrument definitions in both Python and Rust using the `TardisHttpClient`.
This client interacts with the [Tardis instruments metadata API](https://docs.tardis.dev/api/instruments-metadata-api) to request and parse instrument metadata into Nautilus instruments.

The `TardisHttpClient` constructor accepts optional parameters for `api_key`, `base_url`, and `timeout_secs` (default is 60 seconds).

The client provides methods to retrieve either a specific `instrument`, or all `instruments` available on a particular exchange.
Ensure that you use Tardis’s lower-kebab casing convention when referring to a [Tardis-supported exchange](https://api.tardis.dev/v1/exchanges).

:::note
A Tardis API key is required to access the instruments metadata API.
:::

### Requesting Instruments in Python

To request instrument definitions in Python, create a script similar to the following:

```python
import asyncio

from nautilus_trader.core import nautilus_pyo3


async def run():
    http_client = nautilus_pyo3.TardisHttpClient()

    instrument = await http_client.instrument("bitmex", "xbtusd")
    print(f"Received: {instrument}")

    instruments = await http_client.instruments("bitmex")
    print(f"Received: {len(instruments)} instruments")


if __name__ == "__main__":
    asyncio.run(run())
```

### Requesting Instruments in Rust

To request instrument definitions in Rust, use code similar to the following.
For a complete example, see the [example binary here](https://github.com/nautechsystems/nautilus_trader/blob/develop/crates/adapters/tardis/bin/example_http.rs).

```rust
use nautilus_adapters::tardis::{enums::Exchange, http::client::TardisHttpClient};

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::DEBUG)
        .init();

    let client = TardisHttpClient::new(None, None, None).unwrap();

    // Nautilus instrument definitions
    let resp = client.instruments(Exchange::Bitmex).await;
    println!("Received: {resp:?}");

    let resp = client.instrument(Exchange::Bitmex, "ETHUSDT").await;
    println!("Received: {resp:?}");
}
```

## Instrument provider

The `TardisInstrumentProvider` requests and parses instrument definitions from Tardis through the HTTP instrument metadata API.
Since there are multiple [Tardis-supported exchanges](#venues), when loading all instruments,
you must filter for the desired venues using an `InstrumentProviderConfig`:

```python
from nautilus_trader.config import InstrumentProviderConfig

# See supported venues https://nautilustrader.io/docs/nightly/integrations/tardis#venues
venues = {"BINANCE", "BYBIT"}
filters = {"venues": frozenset(venues)}
instrument_provider_config = InstrumentProviderConfig(load_all=True, filters=filters)
```

You can also load specific instrument definitions in the usual way:

```python
from nautilus_trader.config import InstrumentProviderConfig

instrument_ids = [
    InstrumentId.from_str("BTCUSDT-PERP.BINANCE"),  # Will use the 'binance-futures' exchange
    InstrumentId.from_str("BTCUSDT.BINANCE"),  # Will use the 'binance' exchange
]
instrument_provider_config = InstrumentProviderConfig(load_ids=instrument_ids)
```

:::note
Instruments must be available in the cache for all subscriptions.
For simplicity, it’s recommended to load all instruments for the venues you intend to subscribe to.
:::

## Live data client

The `TardisDataClient` enables integration of a Tardis Machine with a running NautilusTrader system.
It supports subscriptions to the following data types:

- `OrderBookDelta` (L2 granularity from Tardis, includes all changes or full-depth snapshots)
- `OrderBookDepth10` (L2 granularity from Tardis, provides snapshots up to 10 levels)
- `QuoteTick`
- `TradeTick`
- `Bar` (trade bars with [Tardis-supported bar aggregations](#bars))

### Data WebSockets

The main `TardisMachineClient` data WebSocket manages all stream subscriptions received during the initial connection phase,
up to the duration specified by `ws_connection_delay_secs`. For any additional subscriptions made
after this period, a new `TardisMachineClient` is created. This approach optimizes performance by
allowing the main WebSocket to handle potentially hundreds of subscriptions in a single stream if
they are provided at startup.

When an initial subscription delay is set with `ws_connection_delay_secs`, unsubscribing from any
of these streams will not actually remove the subscription from the Tardis Machine stream, as selective
unsubscription is not supported by Tardis. However, the component will still unsubscribe from message
bus publishing as expected.

All subscriptions made after any initial delay will behave normally, fully unsubscribing from the
Tardis Machine stream when requested.

:::tip
If you anticipate frequent subscription and unsubscription of data, it is recommended to set
`ws_connection_delay_secs` to zero. This will create a new client for each initial subscription,
allowing them to be later closed individually upon unsubscription.
:::

## Limitations and considerations

The following limitations and considerations are currently known:

- Historical data requests are not supported, as each would require a minimum one-day replay from the Tardis Machine, potentially with a filter. This approach is neither practical nor efficient.


---

file path: ./integrations/bybit.md
# Bybit

:::info
We are currently working on this integration guide.
:::

Founded in 2018, Bybit is one of the largest cryptocurrency exchanges in terms
of daily trading volume, and open interest of crypto assets and crypto
derivative products. This integration supports live market data ingest and order
execution with Bybit.

## Installation

To install NautilusTrader with Bybit support:

```bash
pip install --upgrade "nautilus_trader[bybit]"
```

To build from source with all extras (including Bybit):

```bash
uv sync --all-extras
```

## Examples

You can find live example scripts [here](https://github.com/nautechsystems/nautilus_trader/tree/develop/examples/live/bybit/).

## Overview

This guide assumes a trader is setting up for both live market data feeds, and trade execution.
The Bybit adapter includes multiple components, which can be used together or separately depending
on the use case.

- `BybitHttpClient`: Low-level HTTP API connectivity.
- `BybitWebSocketClient`: Low-level WebSocket API connectivity.
- `BybitInstrumentProvider`: Instrument parsing and loading functionality.
- `BybitDataClient`: A market data feed manager.
- `BybitExecutionClient`: An account management and trade execution gateway.
- `BybitLiveDataClientFactory`: Factory for Bybit data clients (used by the trading node builder).
- `BybitLiveExecClientFactory`: Factory for Bybit execution clients (used by the trading node builder).

:::note
Most users will simply define a configuration for a live trading node (as below),
and won't need to necessarily work with these lower level components directly.
:::

## Bybit documentation

Bybit provides extensive documentation for users which can be found in the [Bybit help center](https://www.bybit.com/en/help-center).
It’s recommended you also refer to the Bybit documentation in conjunction with this NautilusTrader integration guide.

## Products

A product is an umbrella term for a group of related instrument types.

:::note
Product is also referred to as `category` in the Bybit v5 API.
:::

The following product types are supported on Bybit:

- Spot cryptocurrencies
- Perpetual contracts
- Perpetual inverse contracts
- Futures contracts
- Futures inverse contracts

Options contracts are not currently supported (will be implemented in a future version)

## Symbology

To distinguish between different product types on Bybit, Nautilus uses specific product category suffixes for symbols:

- `-SPOT`: Spot cryptocurrencies
- `-LINEAR`: Perpetual and futures contracts
- `-INVERSE`: Inverse perpetual and inverse futures contracts
- `-OPTION`: Options contracts (not currently supported)

These suffixes must be appended to the Bybit raw symbol string to identify the specific product type
for the instrument ID. For example:

- The Ether/Tether spot currency pair is identified with `-SPOT`, such as `ETHUSDT-SPOT`.
- The BTCUSDT perpetual futures contract is identified with `-LINEAR`, such as `BTCUSDT-LINEAR`.
- The BTCUSD inverse perpetual futures contract is identified with `-INVERSE`, such as `BTCUSD-INVERSE`.

## Capability Matrix

Bybit offers a flexible combination of trigger types, enabling a broader range of Nautilus orders.
All the order types listed below can be used as *either* entries or exits, except for trailing stops
(which utilize a position-related API).

### Order Types

| Order Type             | Spot | Linear | Inverse | Notes                    |
|------------------------|------|--------|---------|--------------------------|
| `MARKET`               | ✓    | ✓      | ✓       |                          |
| `LIMIT`                | ✓    | ✓      | ✓       |                          |
| `STOP_MARKET`          | ✓    | ✓      | ✓       |                          |
| `STOP_LIMIT`           | ✓    | ✓      | ✓       |                          |
| `MARKET_IF_TOUCHED`    | ✓    | ✓      | ✓       |                          |
| `LIMIT_IF_TOUCHED`     | ✓    | ✓      | ✓       |                          |
| `TRAILING_STOP_MARKET` | -    | ✓      | ✓       | Not supported for Spot.  |

### Execution Instructions

| Instruction   | Spot | Linear | Inverse | Notes                             |
|---------------|------|--------|---------|-----------------------------------|
| `post_only`   | ✓    | ✓      | ✓       | Only supported on `LIMIT` orders. |
| `reduce_only` | -    | ✓      | ✓       | Not supported for Spot products.  |

### Time-in-Force Options

| Time-in-Force | Spot | Linear | Inverse | Notes                        |
|---------------|------|--------|---------|------------------------------|
| `GTC`         | ✓    | ✓      | ✓       | Good Till Canceled.          |
| `GTD`         | -    | -      | -       | *Not supported*.             |
| `FOK`         | ✓    | ✓      | ✓       | Fill or Kill.                |
| `IOC`         | ✓    | ✓      | ✓       | Immediate or Cancel.         |

### Advanced Order Features

| Feature            | Spot | Linear | Inverse | Notes                                  |
|--------------------|------|--------|---------|----------------------------------------|
| Order Modification | ✓    | ✓      | ✓       | Price and quantity modification.       |
| Bracket/OCO Orders | ✓    | ✓      | ✓       | UI only; API users implement manually. |
| Iceberg Orders     | ✓    | ✓      | ✓       | Max 10 per account, 1 per symbol.      |

### Configuration Options

The following execution client configuration options affect order behavior:

| Option                       | Default | Description                                          |
|------------------------------|---------|------------------------------------------------------|
| `use_gtd`                    | `False` | GTD is not supported; orders are remapped to GTC for local management. |
| `use_ws_trade_api`           | `False` | If `True`, uses WebSocket for order requests instead of HTTP. |
| `use_http_batch_api`         | `False` | If `True`, uses HTTP batch API when WebSocket trading is enabled. |
| `futures_leverages`          | `None`  | Dict to set leverage for futures symbols. |
| `position_mode`              | `None`  | Dict to set position mode for USDT perpetual and inverse futures. |
| `margin_mode`                | `None`  | Sets margin mode for the account. |

### Product-Specific Limitations

The following limitations apply to SPOT products, as positions are not tracked on the venue side:

- `reduce_only` orders are *not supported*.
- Trailing stop orders are *not supported*.

### Trailing Stops

Trailing stops on Bybit do not have a client order ID on the venue side (though there is a `venue_order_id`).
This is because trailing stops are associated with a netted position for an instrument.
Consider the following points when using trailing stops on Bybit:

- `reduce_only` instruction is available
- When the position associated with a trailing stop is closed, the trailing stop is automatically "deactivated" (closed) on the venue side
- You cannot query trailing stop orders that are not already open (the `venue_order_id` is unknown until then)
- You can manually adjust the trigger price in the GUI, which will update the Nautilus order

## Configuration

The product types for each client must be specified in the configurations.

### Data Clients

If no product types are specified then all product types will be loaded and available.

### Execution Clients

Because Nautilus does not support a "unified" account, the account type must be either cash **or** margin.
This means there is a limitation that you cannot specify SPOT with any of the other derivative product types.

- `CASH` account type will be used for SPOT products.
- `MARGIN` account type will be used for all other derivative products.

The most common use case is to configure a live `TradingNode` to include Bybit
data and execution clients. To achieve this, add a `BYBIT` section to your client
configuration(s):

```python
from nautilus_trader.adapters.bybit import BYBIT
from nautilus_trader.adapters.bybit import BybitProductType
from nautilus_trader.live.node import TradingNode

config = TradingNodeConfig(
    ...,  # Omitted
    data_clients={
        BYBIT: {
            "api_key": "YOUR_BYBIT_API_KEY",
            "api_secret": "YOUR_BYBIT_API_SECRET",
            "base_url_http": None,  # Override with custom endpoint
            "product_types": [BybitProductType.LINEAR]
            "testnet": False,
        },
    },
    exec_clients={
        BYBIT: {
            "api_key": "YOUR_BYBIT_API_KEY",
            "api_secret": "YOUR_BYBIT_API_SECRET",
            "base_url_http": None,  # Override with custom endpoint
            "product_types": [BybitProductType.LINEAR]
            "testnet": False,
        },
    },
)
```

Then, create a `TradingNode` and add the client factories:

```python
from nautilus_trader.adapters.bybit import BYBIT
from nautilus_trader.adapters.bybit import BybitLiveDataClientFactory
from nautilus_trader.adapters.bybit import BybitLiveExecClientFactory
from nautilus_trader.live.node import TradingNode

# Instantiate the live trading node with a configuration
node = TradingNode(config=config)

# Register the client factories with the node
node.add_data_client_factory(BYBIT, BybitLiveDataClientFactory)
node.add_exec_client_factory(BYBIT, BybitLiveExecClientFactory)

# Finally build the node
node.build()
```

### API Credentials

There are two options for supplying your credentials to the Bybit clients.
Either pass the corresponding `api_key` and `api_secret` values to the configuration objects, or
set the following environment variables:

For Bybit live clients, you can set:

- `BYBIT_API_KEY`
- `BYBIT_API_SECRET`

For Bybit demo clients, you can set:

- `BYBIT_DEMO_API_KEY`
- `BYBIT_DEMO_API_SECRET`

For Bybit testnet clients, you can set:

- `BYBIT_TESTNET_API_KEY`
- `BYBIT_TESTNET_API_SECRET`

:::tip
We recommend using environment variables to manage your credentials.
:::

When starting the trading node, you'll receive immediate confirmation of whether your
credentials are valid and have trading permissions.


---

file path: ./integrations/ib.md
# Interactive Brokers

Interactive Brokers (IB) is a trading platform providing market access across a wide range of financial instruments, including stocks, options, futures, currencies, bonds, funds, and cryptocurrencies. NautilusTrader offers an adapter to integrate with IB using their [Trader Workstation (TWS) API](https://ibkrcampus.com/ibkr-api-page/trader-workstation-api/) through their Python library, [ibapi](https://github.com/nautechsystems/ibapi).

The TWS API serves as an interface to IB's standalone trading applications: TWS and IB Gateway. Both can be downloaded from the IB website. If you haven't installed TWS or IB Gateway yet, refer to the [Initial Setup](https://ibkrcampus.com/ibkr-api-page/trader-workstation-api/#tws-download) guide. In NautilusTrader, you'll establish a connection to one of these applications via the `InteractiveBrokersClient`.

Alternatively, you can start with a [dockerized version](https://github.com/gnzsnz/ib-gateway-docker) of the IB Gateway, which is particularly useful when deploying trading strategies on a hosted cloud platform. This requires having [Docker](https://www.docker.com/) installed on your machine, along with the [docker](https://pypi.org/project/docker/) Python package, which NautilusTrader conveniently includes as an extra package.

:::note
The standalone TWS and IB Gateway applications require manually inputting username, password, and trading mode (live or paper) at startup. The dockerized version of the IB Gateway handles these steps programmatically.
:::

## Installation

To install NautilusTrader with Interactive Brokers (and Docker) support:

```bash
pip install --upgrade "nautilus_trader[ib,docker]"
```

To build from source with all extras (including IB and Docker):

```bash
uv sync --all-extras
```

:::note
Because IB does not provide wheels for `ibapi`, NautilusTrader [repackages](https://pypi.org/project/nautilus-ibapi/) it for release on PyPI.
:::

## Examples

You can find live example scripts [here](https://github.com/nautechsystems/nautilus_trader/tree/develop/examples/live/interactive_brokers/).

## Getting Started

Before implementing your trading strategies, please ensure that either TWS (Trader Workstation) or IB Gateway is currently running. You have the option to log in to one of these standalone applications using your personal credentials or alternatively, via `DockerizedIBGateway`.

### Connection Methods

There are two primary ways to connect to Interactive Brokers:

1. **Connect to an existing TWS or IB Gateway instance**
2. **Use the dockerized IB Gateway (recommended for automated deployments)**

### Default Ports

Interactive Brokers uses different default ports depending on the application and trading mode:

| Application | Paper Trading | Live Trading |
|-------------|---------------|--------------|
| TWS         | 7497          | 7496         |
| IB Gateway  | 4002          | 4001         |

### Establish Connection to an Existing Gateway or TWS

When connecting to a pre-existing Gateway or TWS, specify the `ibg_host` and `ibg_port` parameters in both the `InteractiveBrokersDataClientConfig` and `InteractiveBrokersExecClientConfig`:

```python
from nautilus_trader.adapters.interactive_brokers.config import InteractiveBrokersDataClientConfig
from nautilus_trader.adapters.interactive_brokers.config import InteractiveBrokersExecClientConfig

# Example for TWS paper trading (default port 7497)
data_config = InteractiveBrokersDataClientConfig(
    ibg_host="127.0.0.1",
    ibg_port=7497,
    ibg_client_id=1,
)

exec_config = InteractiveBrokersExecClientConfig(
    ibg_host="127.0.0.1",
    ibg_port=7497,
    ibg_client_id=1,
    account_id="DU123456",  # Your paper trading account ID
)
```

### Establish Connection to DockerizedIBGateway

For automated deployments, the dockerized gateway is recommended. Supply `dockerized_gateway` with an instance of `DockerizedIBGatewayConfig` in both client configurations. The `ibg_host` and `ibg_port` parameters are not needed as they're managed automatically.

```python
from nautilus_trader.adapters.interactive_brokers.config import DockerizedIBGatewayConfig
from nautilus_trader.adapters.interactive_brokers.gateway import DockerizedIBGateway

gateway_config = DockerizedIBGatewayConfig(
    username="your_username",  # Or set TWS_USERNAME env var
    password="your_password",  # Or set TWS_PASSWORD env var
    trading_mode="paper",      # "paper" or "live"
    read_only_api=True,        # Set to False to allow order execution
    timeout=300,               # Startup timeout in seconds
)

# This may take a short while to start up, especially the first time
gateway = DockerizedIBGateway(config=gateway_config)
gateway.start()

# Confirm you are logged in
print(gateway.is_logged_in(gateway.container))

# Inspect the logs
print(gateway.container.logs())
```

### Environment Variables

To supply credentials to the Interactive Brokers Gateway, either pass the `username` and `password` to the `DockerizedIBGatewayConfig`, or set the following environment variables:

- `TWS_USERNAME` - Your IB account username
- `TWS_PASSWORD` - Your IB account password
- `TWS_ACCOUNT` - Your IB account ID (used as fallback for `account_id`)

### Connection Management

The adapter includes robust connection management features:

- **Automatic reconnection**: Configurable via `IB_MAX_CONNECTION_ATTEMPTS` environment variable
- **Connection timeout**: Configurable via `connection_timeout` parameter (default: 300 seconds)
- **Connection watchdog**: Monitors connection health and triggers reconnection if needed
- **Graceful error handling**: Comprehensive error handling for various connection scenarios

## Overview

The Interactive Brokers adapter provides a comprehensive integration with IB's TWS API. The adapter includes several major components:

### Core Components

- **`InteractiveBrokersClient`**: The central client that executes TWS API requests using `ibapi`. Manages connections, handles errors, and coordinates all API interactions.
- **`InteractiveBrokersDataClient`**: Connects to the Gateway for streaming market data including quotes, trades, and bars.
- **`InteractiveBrokersExecutionClient`**: Handles account information, order management, and trade execution.
- **`InteractiveBrokersInstrumentProvider`**: Retrieves and manages instrument definitions, including support for options and futures chains.
- **`HistoricInteractiveBrokersClient`**: Provides methods for retrieving instruments and historical data, useful for backtesting and research.

### Supporting Components

- **`DockerizedIBGateway`**: Manages dockerized IB Gateway instances for automated deployments.
- **Configuration Classes**: Comprehensive configuration options for all components.
- **Factory Classes**: Create and configure client instances with proper dependencies.

### Supported Asset Classes

The adapter supports trading across all major asset classes available through Interactive Brokers:

- **Equities**: Stocks, ETFs, and equity options
- **Fixed Income**: Bonds and bond funds
- **Derivatives**: Futures, options, and warrants
- **Foreign Exchange**: Spot FX and FX forwards
- **Cryptocurrencies**: Bitcoin, Ethereum, and other digital assets
- **Commodities**: Physical commodities and commodity futures
- **Indices**: Index products and index options

## The Interactive Brokers Client

The `InteractiveBrokersClient` serves as the central component of the IB adapter, overseeing a range of critical functions. These include establishing and maintaining connections, handling API errors, executing trades, and gathering various types of data such as market data, contract/instrument data, and account details.

To ensure efficient management of these diverse responsibilities, the `InteractiveBrokersClient` is divided into several specialized mixin classes. This modular approach enhances manageability and clarity.

### Client Architecture

The client uses a mixin-based architecture where each mixin handles a specific aspect of the IB API:

#### Connection Management (`InteractiveBrokersClientConnectionMixin`)

- Establishes and maintains socket connections to TWS/Gateway
- Handles connection timeouts and reconnection logic
- Manages connection state and health monitoring
- Supports configurable reconnection attempts via `IB_MAX_CONNECTION_ATTEMPTS` environment variable

#### Error Handling (`InteractiveBrokersClientErrorMixin`)

- Processes all API errors and warnings
- Categorizes errors by type (client errors, connectivity issues, request errors)
- Handles subscription and request-specific error scenarios
- Provides comprehensive error logging and debugging information

#### Account Management (`InteractiveBrokersClientAccountMixin`)

- Retrieves account information and balances
- Manages position data and portfolio updates
- Handles multi-account scenarios
- Processes account-related notifications

#### Contract/Instrument Management (`InteractiveBrokersClientContractMixin`)

- Retrieves contract details and specifications
- Handles instrument searches and lookups
- Manages contract validation and verification
- Supports complex instrument types (options chains, futures chains)

#### Market Data Management (`InteractiveBrokersClientMarketDataMixin`)

- Handles real-time and historical market data subscriptions
- Processes quotes, trades, and bar data
- Manages market data type settings (real-time, delayed, frozen)
- Handles tick-by-tick data and market depth

#### Order Management (`InteractiveBrokersClientOrderMixin`)

- Processes order placement, modification, and cancellation
- Handles order status updates and execution reports
- Manages order validation and error handling
- Supports complex order types and conditions

### Key Features

- **Asynchronous Operation**: All operations are fully asynchronous using Python's asyncio
- **Robust Error Handling**: Comprehensive error categorization and handling
- **Connection Resilience**: Automatic reconnection with configurable retry logic
- **Message Processing**: Efficient message queue processing for high-throughput scenarios
- **State Management**: Proper state tracking for connections, subscriptions, and requests

:::tip
To troubleshoot TWS API incoming message issues, consider starting at the `InteractiveBrokersClient._process_message` method, which acts as the primary gateway for processing all messages received from the API.
:::

## Symbology

The `InteractiveBrokersInstrumentProvider` supports three methods for constructing `InstrumentId` instances, which can be configured via the `symbology_method` enum in `InteractiveBrokersInstrumentProviderConfig`.

### Symbology Methods

#### 1. Simplified Symbology (`IB_SIMPLIFIED`) - Default

When `symbology_method` is set to `IB_SIMPLIFIED` (the default setting), the system uses intuitive, human-readable symbology rules:

**Format Rules by Asset Class:**

- **Forex**: `{symbol}/{currency}.{exchange}`
  - Example: `EUR/USD.IDEALPRO`
- **Stocks**: `{localSymbol}.{primaryExchange}`
  - Spaces in localSymbol are replaced with hyphens
  - Example: `BF-B.NYSE`, `SPY.ARCA`
- **Futures**: `{localSymbol}.{exchange}`
  - Individual contracts use single digit years
  - Example: `ESM4.CME`, `CLZ7.NYMEX`
- **Continuous Futures**: `{symbol}.{exchange}`
  - Represents front month, automatically rolling
  - Example: `ES.CME`, `CL.NYMEX`
- **Options on Futures (FOP)**: `{localSymbol}.{exchange}`
  - Format: `{symbol}{month}{year} {right}{strike}`
  - Example: `ESM4 C4200.CME`
- **Options**: `{localSymbol}.{exchange}`
  - All spaces removed from localSymbol
  - Example: `AAPL230217P00155000.SMART`
- **Indices**: `^{localSymbol}.{exchange}`
  - Example: `^SPX.CBOE`, `^NDX.NASDAQ`
- **Bonds**: `{localSymbol}.{exchange}`
  - Example: `912828XE8.SMART`
- **Cryptocurrencies**: `{symbol}/{currency}.{exchange}`
  - Example: `BTC/USD.PAXOS`, `ETH/USD.PAXOS`

#### 2. Raw Symbology (`IB_RAW`)

Setting `symbology_method` to `IB_RAW` enforces stricter parsing rules that align directly with the fields defined in the IB API. This method provides maximum compatibility across all regions and instrument types:

**Format Rules:**

- **CFDs**: `{localSymbol}={secType}.IBCFD`
- **Commodities**: `{localSymbol}={secType}.IBCMDTY`
- **Default for Other Types**: `{localSymbol}={secType}.{exchange}`

**Examples:**

- `IBUS30=CFD.IBCFD`
- `XAUUSD=CMDTY.IBCMDTY`
- `AAPL=STK.SMART`

This configuration ensures explicit instrument identification and supports instruments from any region, especially those with non-standard symbology where simplified parsing may fail.

### MIC Venue Conversion

The adapter supports converting Interactive Brokers exchange codes to Market Identifier Codes (MIC) for standardized venue identification:

#### `convert_exchange_to_mic_venue`

When set to `True`, the adapter automatically converts IB exchange codes to their corresponding MIC codes:

```python
instrument_provider_config = InteractiveBrokersInstrumentProviderConfig(
    convert_exchange_to_mic_venue=True,  # Enable MIC conversion
    symbology_method=SymbologyMethod.IB_SIMPLIFIED,
)
```

**Examples of MIC Conversion:**

- `CME` → `XCME` (Chicago Mercantile Exchange)
- `NASDAQ` → `XNAS` (Nasdaq Stock Market)
- `NYSE` → `XNYS` (New York Stock Exchange)
- `LSE` → `XLON` (London Stock Exchange)

#### `symbol_to_mic_venue`

For custom venue mapping, use the `symbol_to_mic_venue` dictionary to override default conversions:

```python
instrument_provider_config = InteractiveBrokersInstrumentProviderConfig(
    convert_exchange_to_mic_venue=True,
    symbol_to_mic_venue={
        "ES": "XCME",  # All ES futures/options use CME MIC
        "SPY": "ARCX", # SPY specifically uses ARCA
    },
)
```

### Supported Instrument Formats

The adapter supports various instrument formats based on Interactive Brokers' contract specifications:

#### Futures Month Codes

- **F** = January, **G** = February, **H** = March, **J** = April
- **K** = May, **M** = June, **N** = July, **Q** = August
- **U** = September, **V** = October, **X** = November, **Z** = December

#### Supported Exchanges by Asset Class

**Futures Exchanges:**

- `CME`, `CBOT`, `NYMEX`, `COMEX`, `KCBT`, `MGE`, `NYBOT`, `SNFE`

**Options Exchanges:**

- `SMART` (IB's smart routing)

**Forex Exchanges:**

- `IDEALPRO` (IB's forex platform)

**Cryptocurrency Exchanges:**

- `PAXOS` (IB's crypto platform)

**CFD/Commodity Exchanges:**

- `IBCFD`, `IBCMDTY` (IB's internal routing)

### Choosing the Right Symbology Method

- **Use `IB_SIMPLIFIED`** (default) for most use cases - provides clean, readable instrument IDs
- **Use `IB_RAW`** when dealing with complex international instruments or when simplified parsing fails
- **Enable `convert_exchange_to_mic_venue`** when you need standardized MIC venue codes for compliance or data consistency

## Instruments & Contracts

In Interactive Brokers, a NautilusTrader `Instrument` corresponds to an IB [Contract](https://ibkrcampus.com/ibkr-api-page/trader-workstation-api/#contracts). The adapter handles two types of contract representations:

### Contract Types

#### Basic Contract (`IBContract`)

- Contains essential contract identification fields
- Used for contract searches and basic operations
- Cannot be directly converted to a NautilusTrader `Instrument`

#### Contract Details (`IBContractDetails`)

- Contains comprehensive contract information including:
  - Order types supported
  - Trading hours and calendar
  - Margin requirements
  - Price increments and multipliers
  - Market data permissions
- Can be converted to a NautilusTrader `Instrument`
- Required for trading operations

### Contract Discovery

To search for contract information, use the [IB Contract Information Center](https://pennies.interactivebrokers.com/cstools/contract_info/).

### Loading Instruments

There are two primary methods for loading instruments:

#### 1. Using `load_ids` (Recommended)
Use `symbology_method=SymbologyMethod.IB_SIMPLIFIED` (default) with `load_ids` for clean, intuitive instrument identification:

```python
from nautilus_trader.adapters.interactive_brokers.config import InteractiveBrokersInstrumentProviderConfig
from nautilus_trader.adapters.interactive_brokers.config import SymbologyMethod

instrument_provider_config = InteractiveBrokersInstrumentProviderConfig(
    symbology_method=SymbologyMethod.IB_SIMPLIFIED,
    load_ids=frozenset([
        "EUR/USD.IDEALPRO",    # Forex
        "SPY.ARCA",            # Stock
        "ESM24.CME",           # Future
        "BTC/USD.PAXOS",       # Crypto
        "^SPX.CBOE",           # Index
    ]),
)
```

#### 2. Using `load_contracts` (For Complex Instruments)
Use `load_contracts` with `IBContract` instances for complex scenarios like options/futures chains:

```python
from nautilus_trader.adapters.interactive_brokers.common import IBContract

# Load options chain for specific expiry
options_chain_expiry = IBContract(
    secType="IND",
    symbol="SPX",
    exchange="CBOE",
    build_options_chain=True,
    lastTradeDateOrContractMonth='20240718',
)

# Load options chain for date range
options_chain_range = IBContract(
    secType="IND",
    symbol="SPX",
    exchange="CBOE",
    build_options_chain=True,
    min_expiry_days=0,
    max_expiry_days=30,
)

# Load futures chain
futures_chain = IBContract(
    secType="CONTFUT",
    exchange="CME",
    symbol="ES",
    build_futures_chain=True,
)

instrument_provider_config = InteractiveBrokersInstrumentProviderConfig(
    load_contracts=frozenset([
        options_chain_expiry,
        options_chain_range,
        futures_chain,
    ]),
)
```

### IBContract Examples by Asset Class

```python
from nautilus_trader.adapters.interactive_brokers.common import IBContract

# Stocks
IBContract(secType='STK', exchange='SMART', primaryExchange='ARCA', symbol='SPY')
IBContract(secType='STK', exchange='SMART', primaryExchange='NASDAQ', symbol='AAPL')

# Bonds
IBContract(secType='BOND', secIdType='ISIN', secId='US03076KAA60')
IBContract(secType='BOND', secIdType='CUSIP', secId='912828XE8')

# Individual Options
IBContract(secType='OPT', exchange='SMART', symbol='SPY',
           lastTradeDateOrContractMonth='20251219', strike=500, right='C')

# Options Chain (loads all strikes/expirations)
IBContract(secType='STK', exchange='SMART', primaryExchange='ARCA', symbol='SPY',
           build_options_chain=True, min_expiry_days=10, max_expiry_days=60)

# CFDs
IBContract(secType='CFD', symbol='IBUS30')
IBContract(secType='CFD', symbol='DE40EUR', exchange='SMART')

# Individual Futures
IBContract(secType='FUT', exchange='CME', symbol='ES',
           lastTradeDateOrContractMonth='20240315')

# Futures Chain (loads all expirations)
IBContract(secType='CONTFUT', exchange='CME', symbol='ES', build_futures_chain=True)

# Options on Futures (FOP) - Individual
IBContract(secType='FOP', exchange='CME', symbol='ES',
           lastTradeDateOrContractMonth='20240315', strike=4200, right='C')

# Options on Futures Chain (loads all strikes/expirations)
IBContract(secType='CONTFUT', exchange='CME', symbol='ES',
           build_options_chain=True, min_expiry_days=7, max_expiry_days=60)

# Forex
IBContract(secType='CASH', exchange='IDEALPRO', symbol='EUR', currency='USD')
IBContract(secType='CASH', exchange='IDEALPRO', symbol='GBP', currency='JPY')

# Cryptocurrencies
IBContract(secType='CRYPTO', symbol='BTC', exchange='PAXOS', currency='USD')
IBContract(secType='CRYPTO', symbol='ETH', exchange='PAXOS', currency='USD')

# Indices
IBContract(secType='IND', symbol='SPX', exchange='CBOE')
IBContract(secType='IND', symbol='NDX', exchange='NASDAQ')

# Commodities
IBContract(secType='CMDTY', symbol='XAUUSD', exchange='SMART')
```

### Advanced Configuration Options

```python
# Options chain with custom exchange
IBContract(
    secType="STK",
    symbol="AAPL",
    exchange="SMART",
    primaryExchange="NASDAQ",
    build_options_chain=True,
    options_chain_exchange="CBOE",  # Use CBOE for options instead of SMART
    min_expiry_days=7,
    max_expiry_days=45,
)

# Futures chain with specific months
IBContract(
    secType="CONTFUT",
    exchange="NYMEX",
    symbol="CL",  # Crude Oil
    build_futures_chain=True,
    min_expiry_days=30,
    max_expiry_days=180,
)
```

### Continuous Futures

For continuous futures contracts (using `secType='CONTFUT'`), the adapter creates instrument IDs using just the symbol and venue:

```python
# Continuous futures examples
IBContract(secType='CONTFUT', exchange='CME', symbol='ES')  # → ES.CME
IBContract(secType='CONTFUT', exchange='NYMEX', symbol='CL') # → CL.NYMEX

# With MIC venue conversion enabled
instrument_provider_config = InteractiveBrokersInstrumentProviderConfig(
    convert_exchange_to_mic_venue=True,
)
# Results in:
# ES.XCME (instead of ES.CME)
# CL.XNYM (instead of CL.NYMEX)
```

**Continuous Futures vs Individual Futures:**

- **Continuous**: `ES.CME` - Represents the front month contract, automatically rolls
- **Individual**: `ESM4.CME` - Specific March 2024 contract

:::note
When using `build_options_chain=True` or `build_futures_chain=True`, the `secType` and `symbol` should be specified for the underlying contract. The adapter will automatically discover and load all related derivative contracts within the specified expiry range.
:::

## Historical Data & Backtesting

The `HistoricInteractiveBrokersClient` provides comprehensive methods for retrieving historical data from Interactive Brokers for backtesting and research purposes.

### Supported Data Types

- **Bar Data**: OHLCV bars with various aggregations (time-based, tick-based, volume-based)
- **Tick Data**: Trade ticks and quote ticks with microsecond precision
- **Instrument Data**: Complete contract specifications and trading rules

### Historical Data Client

```python
from nautilus_trader.adapters.interactive_brokers.historical.client import HistoricInteractiveBrokersClient
from ibapi.common import MarketDataTypeEnum

# Initialize the client
client = HistoricInteractiveBrokersClient(
    host="127.0.0.1",
    port=7497,
    client_id=1,
    market_data_type=MarketDataTypeEnum.DELAYED_FROZEN,  # Use delayed data if no subscription
    log_level="INFO"
)

# Connect to TWS/Gateway
await client.connect()
```

### Retrieving Instruments

```python
from nautilus_trader.adapters.interactive_brokers.common import IBContract

# Define contracts
contracts = [
    IBContract(secType="STK", symbol="AAPL", exchange="SMART", primaryExchange="NASDAQ"),
    IBContract(secType="STK", symbol="MSFT", exchange="SMART", primaryExchange="NASDAQ"),
    IBContract(secType="CASH", symbol="EUR", currency="USD", exchange="IDEALPRO"),
]

# Request instrument definitions
instruments = await client.request_instruments(contracts=contracts)
```

### Retrieving Historical Bars

```python
import datetime

# Request historical bars
bars = await client.request_bars(
    bar_specifications=[
        "1-MINUTE-LAST",    # 1-minute bars using last price
        "5-MINUTE-MID",     # 5-minute bars using midpoint
        "1-HOUR-LAST",      # 1-hour bars using last price
        "1-DAY-LAST",       # Daily bars using last price
    ],
    start_date_time=datetime.datetime(2023, 11, 1, 9, 30),
    end_date_time=datetime.datetime(2023, 11, 6, 16, 30),
    tz_name="America/New_York",
    contracts=contracts,
    use_rth=True,  # Regular Trading Hours only
    timeout=120,   # Request timeout in seconds
)
```

### Retrieving Historical Ticks

```python
# Request historical tick data
ticks = await client.request_ticks(
    tick_types=["TRADES", "BID_ASK"],  # Trade ticks and quote ticks
    start_date_time=datetime.datetime(2023, 11, 6, 9, 30),
    end_date_time=datetime.datetime(2023, 11, 6, 16, 30),
    tz_name="America/New_York",
    contracts=contracts,
    use_rth=True,
    timeout=120,
)
```

### Bar Specifications

The adapter supports various bar specifications:

#### Time-Based Bars

- `"1-SECOND-LAST"`, `"5-SECOND-LAST"`, `"10-SECOND-LAST"`, `"15-SECOND-LAST"`, `"30-SECOND-LAST"`
- `"1-MINUTE-LAST"`, `"2-MINUTE-LAST"`, `"3-MINUTE-LAST"`, `"5-MINUTE-LAST"`, `"10-MINUTE-LAST"`, `"15-MINUTE-LAST"`, `"20-MINUTE-LAST"`, `"30-MINUTE-LAST"`
- `"1-HOUR-LAST"`, `"2-HOUR-LAST"`, `"3-HOUR-LAST"`, `"4-HOUR-LAST"`, `"8-HOUR-LAST"`
- `"1-DAY-LAST"`, `"1-WEEK-LAST"`, `"1-MONTH-LAST"`

#### Price Types

- `LAST` - Last traded price
- `MID` - Midpoint of bid/ask
- `BID` - Bid price
- `ASK` - Ask price

### Complete Example

```python
import asyncio
import datetime
from nautilus_trader.adapters.interactive_brokers.common import IBContract
from nautilus_trader.adapters.interactive_brokers.historical.client import HistoricInteractiveBrokersClient
from nautilus_trader.persistence.catalog import ParquetDataCatalog


async def download_historical_data():
    # Initialize client
    client = HistoricInteractiveBrokersClient(
        host="127.0.0.1",
        port=7497,
        client_id=5,
    )

    # Connect
    await client.connect()
    await asyncio.sleep(2)  # Allow connection to stabilize

    # Define contracts
    contracts = [
        IBContract(secType="STK", symbol="AAPL", exchange="SMART", primaryExchange="NASDAQ"),
        IBContract(secType="CASH", symbol="EUR", currency="USD", exchange="IDEALPRO"),
    ]

    # Request instruments
    instruments = await client.request_instruments(contracts=contracts)

    # Request historical bars
    bars = await client.request_bars(
        bar_specifications=["1-HOUR-LAST", "1-DAY-LAST"],
        start_date_time=datetime.datetime(2023, 11, 1, 9, 30),
        end_date_time=datetime.datetime(2023, 11, 6, 16, 30),
        tz_name="America/New_York",
        contracts=contracts,
        use_rth=True,
    )

    # Request tick data
    ticks = await client.request_ticks(
        tick_types=["TRADES"],
        start_date_time=datetime.datetime(2023, 11, 6, 14, 0),
        end_date_time=datetime.datetime(2023, 11, 6, 15, 0),
        tz_name="America/New_York",
        contracts=contracts,
    )

    # Save to catalog
    catalog = ParquetDataCatalog("./catalog")
    catalog.write_data(instruments)
    catalog.write_data(bars)
    catalog.write_data(ticks)

    print(f"Downloaded {len(instruments)} instruments")
    print(f"Downloaded {len(bars)} bars")
    print(f"Downloaded {len(ticks)} ticks")

    # Disconnect
    await client.disconnect()

# Run the example
if __name__ == "__main__":
    asyncio.run(download_historical_data())
```

### Data Limitations

Be aware of Interactive Brokers' historical data limitations:

- **Rate Limits**: IB enforces rate limits on historical data requests
- **Data Availability**: Historical data availability varies by instrument and subscription level
- **Market Data Permissions**: Some data requires specific market data subscriptions
- **Time Ranges**: Maximum lookback periods vary by bar size and instrument type

### Best Practices

1. **Use Delayed Data**: For backtesting, `MarketDataTypeEnum.DELAYED_FROZEN` is often sufficient
2. **Batch Requests**: Group multiple instruments in single requests when possible
3. **Handle Timeouts**: Set appropriate timeout values for large data requests
4. **Respect Rate Limits**: Add delays between requests to avoid hitting rate limits
5. **Validate Data**: Always check data quality and completeness before backtesting

## Live Trading

Live trading with Interactive Brokers requires setting up a `TradingNode` that incorporates both `InteractiveBrokersDataClient` and `InteractiveBrokersExecutionClient`. These clients depend on the `InteractiveBrokersInstrumentProvider` for instrument management.

### Architecture Overview

The live trading setup consists of three main components:

1. **InstrumentProvider**: Manages instrument definitions and contract details
2. **DataClient**: Handles real-time market data subscriptions
3. **ExecutionClient**: Manages orders, positions, and account information

### InstrumentProvider Configuration

The `InteractiveBrokersInstrumentProvider` serves as the bridge for accessing financial instrument data from IB. It supports loading individual instruments, options chains, and futures chains.

#### Basic Configuration

```python
from nautilus_trader.adapters.interactive_brokers.config import InteractiveBrokersInstrumentProviderConfig
from nautilus_trader.adapters.interactive_brokers.config import SymbologyMethod
from nautilus_trader.adapters.interactive_brokers.common import IBContract

instrument_provider_config = InteractiveBrokersInstrumentProviderConfig(
    symbology_method=SymbologyMethod.IB_SIMPLIFIED,
    build_futures_chain=False,  # Set to True if fetching futures chains
    build_options_chain=False,  # Set to True if fetching options chains
    min_expiry_days=10,         # Minimum days to expiry for derivatives
    max_expiry_days=60,         # Maximum days to expiry for derivatives
    convert_exchange_to_mic_venue=False,  # Use MIC codes for venue mapping
    cache_validity_days=1,      # Cache instrument data for 1 day
    load_ids=frozenset([
        # Individual instruments using simplified symbology
        "EUR/USD.IDEALPRO",     # Forex
        "BTC/USD.PAXOS",        # Cryptocurrency
        "SPY.ARCA",             # Stock ETF
        "V.NYSE",               # Individual stock
        "ESM4.CME",             # Future contract (single digit year)
        "^SPX.CBOE",            # Index
    ]),
    load_contracts=frozenset([
        # Complex instruments using IBContract
        IBContract(secType='STK', symbol='AAPL', exchange='SMART', primaryExchange='NASDAQ'),
        IBContract(secType='CASH', symbol='GBP', currency='USD', exchange='IDEALPRO'),
    ]),
)
```

#### Advanced Configuration for Derivatives

```python
# Configuration for options and futures chains
advanced_config = InteractiveBrokersInstrumentProviderConfig(
    symbology_method=SymbologyMethod.IB_SIMPLIFIED,
    build_futures_chain=True,   # Enable futures chain loading
    build_options_chain=True,   # Enable options chain loading
    min_expiry_days=7,          # Load contracts expiring in 7+ days
    max_expiry_days=90,         # Load contracts expiring within 90 days
    load_contracts=frozenset([
        # Load SPY options chain
        IBContract(
            secType='STK',
            symbol='SPY',
            exchange='SMART',
            primaryExchange='ARCA',
            build_options_chain=True,
        ),
        # Load ES futures chain
        IBContract(
            secType='CONTFUT',
            exchange='CME',
            symbol='ES',
            build_futures_chain=True,
        ),
    ]),
)
```

### Integration with External Data Providers

The Interactive Brokers adapter can be used alongside other data providers for enhanced market data coverage. When using multiple data sources:

- Use consistent symbology methods across providers
- Consider using `convert_exchange_to_mic_venue=True` for standardized venue identification
- Ensure instrument cache management is handled properly to avoid conflicts

### Data Client Configuration

The `InteractiveBrokersDataClient` interfaces with IB for streaming and retrieving real-time market data. Upon connection, it configures the [market data type](https://ibkrcampus.com/ibkr-api-page/trader-workstation-api/#delayed-market-data) and loads instruments based on the `InteractiveBrokersInstrumentProviderConfig` settings.

#### Supported Data Types

- **Quote Ticks**: Real-time bid/ask prices and sizes
- **Trade Ticks**: Real-time trade prices and volumes
- **Bar Data**: Real-time OHLCV bars (1-second to 1-day intervals)
- **Market Depth**: Level 2 order book data (where available)

#### Market Data Types

Interactive Brokers supports several market data types:

- `REALTIME`: Live market data (requires market data subscriptions)
- `DELAYED`: 15-20 minute delayed data (free for most markets)
- `DELAYED_FROZEN`: Delayed data that doesn't update (useful for testing)
- `FROZEN`: Last known real-time data (when market is closed)

#### Basic Data Client Configuration

```python
from nautilus_trader.adapters.interactive_brokers.config import IBMarketDataTypeEnum
from nautilus_trader.adapters.interactive_brokers.config import InteractiveBrokersDataClientConfig

data_client_config = InteractiveBrokersDataClientConfig(
    ibg_host="127.0.0.1",
    ibg_port=7497,  # TWS paper trading port
    ibg_client_id=1,
    use_regular_trading_hours=True,  # RTH only for stocks
    market_data_type=IBMarketDataTypeEnum.DELAYED_FROZEN,  # Use delayed data
    ignore_quote_tick_size_updates=False,  # Include size-only updates
    instrument_provider=instrument_provider_config,
    connection_timeout=300,  # 5 minutes
    request_timeout=60,      # 1 minute
)
```

#### Advanced Data Client Configuration

```python
# Configuration for production with real-time data
production_data_config = InteractiveBrokersDataClientConfig(
    ibg_host="127.0.0.1",
    ibg_port=4001,  # IB Gateway live trading port
    ibg_client_id=1,
    use_regular_trading_hours=False,  # Include extended hours
    market_data_type=IBMarketDataTypeEnum.REALTIME,  # Real-time data
    ignore_quote_tick_size_updates=True,  # Reduce tick volume
    handle_revised_bars=True,  # Handle bar revisions
    instrument_provider=instrument_provider_config,
    dockerized_gateway=dockerized_gateway_config,  # If using Docker
    connection_timeout=300,
    request_timeout=60,
)
```

#### Configuration Options Explained

- **`use_regular_trading_hours`**: When `True`, only requests data during regular trading hours. Primarily affects bar data for stocks.
- **`ignore_quote_tick_size_updates`**: When `True`, filters out quote ticks where only the size changed (not price), reducing data volume.
- **`handle_revised_bars`**: When `True`, processes bar revisions from IB (bars can be updated after initial publication).
- **`connection_timeout`**: Maximum time to wait for initial connection establishment.
- **`request_timeout`**: Maximum time to wait for historical data requests.

### Execution Client Configuration

The `InteractiveBrokersExecutionClient` handles trade execution, order management, account information, and position tracking. It provides comprehensive order lifecycle management and real-time account updates.

#### Supported Functionality

- **Order Management**: Place, modify, and cancel orders
- **Order Types**: Market, limit, stop, stop-limit, trailing stop, and more
- **Account Information**: Real-time balance and margin updates
- **Position Tracking**: Real-time position updates and P&L
- **Trade Reporting**: Execution reports and fill notifications
- **Risk Management**: Pre-trade risk checks and position limits

#### Supported Order Types

The adapter supports most Interactive Brokers order types:

- **Market Orders**: `OrderType.MARKET`
- **Limit Orders**: `OrderType.LIMIT`
- **Stop Orders**: `OrderType.STOP_MARKET`
- **Stop-Limit Orders**: `OrderType.STOP_LIMIT`
- **Market-If-Touched**: `OrderType.MARKET_IF_TOUCHED`
- **Limit-If-Touched**: `OrderType.LIMIT_IF_TOUCHED`
- **Trailing Stop Market**: `OrderType.TRAILING_STOP_MARKET`
- **Trailing Stop Limit**: `OrderType.TRAILING_STOP_LIMIT`
- **Market-on-Close**: `OrderType.MARKET` with `TimeInForce.AT_THE_CLOSE`
- **Limit-on-Close**: `OrderType.LIMIT` with `TimeInForce.AT_THE_CLOSE`

#### Time-in-Force Options

- **Day Orders**: `TimeInForce.DAY`
- **Good-Till-Canceled**: `TimeInForce.GTC`
- **Immediate-or-Cancel**: `TimeInForce.IOC`
- **Fill-or-Kill**: `TimeInForce.FOK`
- **Good-Till-Date**: `TimeInForce.GTD`
- **At-the-Open**: `TimeInForce.AT_THE_OPEN`
- **At-the-Close**: `TimeInForce.AT_THE_CLOSE`

#### Basic Execution Client Configuration

```python
from nautilus_trader.adapters.interactive_brokers.config import InteractiveBrokersExecClientConfig
from nautilus_trader.config import RoutingConfig

exec_client_config = InteractiveBrokersExecClientConfig(
    ibg_host="127.0.0.1",
    ibg_port=7497,  # TWS paper trading port
    ibg_client_id=1,
    account_id="DU123456",  # Your IB account ID (paper or live)
    instrument_provider=instrument_provider_config,
    connection_timeout=300,
    routing=RoutingConfig(default=True),  # Route all orders through this client
)
```

#### Advanced Execution Client Configuration

```python
# Production configuration with dockerized gateway
production_exec_config = InteractiveBrokersExecClientConfig(
    ibg_host="127.0.0.1",
    ibg_port=4001,  # IB Gateway live trading port
    ibg_client_id=1,
    account_id=None,  # Will use TWS_ACCOUNT environment variable
    instrument_provider=instrument_provider_config,
    dockerized_gateway=dockerized_gateway_config,
    connection_timeout=300,
    routing=RoutingConfig(default=True),
)
```

#### Account ID Configuration

The `account_id` parameter is crucial and must match the account logged into TWS/Gateway:

```python
# Option 1: Specify directly in config
exec_config = InteractiveBrokersExecClientConfig(
    account_id="DU123456",  # Paper trading account
    # ... other parameters
)

# Option 2: Use environment variable
import os
os.environ["TWS_ACCOUNT"] = "DU123456"
exec_config = InteractiveBrokersExecClientConfig(
    account_id=None,  # Will use TWS_ACCOUNT env var
    # ... other parameters
)
```

#### Order Tags and Advanced Features

The adapter supports IB-specific order parameters through order tags:

```python
from nautilus_trader.adapters.interactive_brokers.common import IBOrderTags

# Create order with IB-specific parameters
order_tags = IBOrderTags(
    allOrNone=True,           # All-or-none order
    ocaGroup="MyGroup1",      # One-cancels-all group
    ocaType=1,                # Cancel with block
    activeStartTime="20240315 09:30:00 EST",  # GTC activation time
    activeStopTime="20240315 16:00:00 EST",   # GTC deactivation time
    goodAfterTime="20240315 09:35:00 EST",    # Good after time
)

# Apply tags to order (implementation depends on your strategy code)
```

### Complete Trading Node Configuration

Setting up a complete trading environment involves configuring a `TradingNodeConfig` with all necessary components. Here are comprehensive examples for different scenarios.

#### Paper Trading Configuration

```python
import os
from nautilus_trader.adapters.interactive_brokers.common import IB
from nautilus_trader.adapters.interactive_brokers.common import IB_VENUE
from nautilus_trader.adapters.interactive_brokers.config import InteractiveBrokersDataClientConfig
from nautilus_trader.adapters.interactive_brokers.config import InteractiveBrokersExecClientConfig
from nautilus_trader.adapters.interactive_brokers.config import InteractiveBrokersInstrumentProviderConfig
from nautilus_trader.adapters.interactive_brokers.config import IBMarketDataTypeEnum
from nautilus_trader.adapters.interactive_brokers.config import SymbologyMethod
from nautilus_trader.adapters.interactive_brokers.factories import InteractiveBrokersLiveDataClientFactory
from nautilus_trader.adapters.interactive_brokers.factories import InteractiveBrokersLiveExecClientFactory
from nautilus_trader.config import LiveDataEngineConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.config import RoutingConfig
from nautilus_trader.config import TradingNodeConfig
from nautilus_trader.live.node import TradingNode

# Instrument provider configuration
instrument_provider_config = InteractiveBrokersInstrumentProviderConfig(
    symbology_method=SymbologyMethod.IB_SIMPLIFIED,
    load_ids=frozenset([
        "EUR/USD.IDEALPRO",
        "GBP/USD.IDEALPRO",
        "SPY.ARCA",
        "QQQ.NASDAQ",
        "AAPL.NASDAQ",
        "MSFT.NASDAQ",
    ]),
)

# Data client configuration
data_client_config = InteractiveBrokersDataClientConfig(
    ibg_host="127.0.0.1",
    ibg_port=7497,  # TWS paper trading
    ibg_client_id=1,
    use_regular_trading_hours=True,
    market_data_type=IBMarketDataTypeEnum.DELAYED_FROZEN,
    instrument_provider=instrument_provider_config,
)

# Execution client configuration
exec_client_config = InteractiveBrokersExecClientConfig(
    ibg_host="127.0.0.1",
    ibg_port=7497,  # TWS paper trading
    ibg_client_id=1,
    account_id="DU123456",  # Your paper trading account
    instrument_provider=instrument_provider_config,
    routing=RoutingConfig(default=True),
)

# Trading node configuration
config_node = TradingNodeConfig(
    trader_id="PAPER-TRADER-001",
    logging=LoggingConfig(log_level="INFO"),
    data_clients={IB: data_client_config},
    exec_clients={IB: exec_client_config},
    data_engine=LiveDataEngineConfig(
        time_bars_timestamp_on_close=False,  # IB standard: use bar open time
        validate_data_sequence=True,         # Discard out-of-sequence bars
    ),
    timeout_connection=90.0,
    timeout_reconciliation=5.0,
    timeout_portfolio=5.0,
    timeout_disconnection=5.0,
    timeout_post_stop=2.0,
)

# Create and configure the trading node
node = TradingNode(config=config_node)
node.add_data_client_factory(IB, InteractiveBrokersLiveDataClientFactory)
node.add_exec_client_factory(IB, InteractiveBrokersLiveExecClientFactory)
node.build()
node.portfolio.set_specific_venue(IB_VENUE)

if __name__ == "__main__":
    try:
        node.run()
    finally:
        node.dispose()
```

#### Live Trading with Dockerized Gateway

```python
from nautilus_trader.adapters.interactive_brokers.config import DockerizedIBGatewayConfig

# Dockerized gateway configuration
dockerized_gateway_config = DockerizedIBGatewayConfig(
    username=os.environ.get("TWS_USERNAME"),
    password=os.environ.get("TWS_PASSWORD"),
    trading_mode="live",  # "paper" or "live"
    read_only_api=False,  # Allow order execution
    timeout=300,
)

# Data client with dockerized gateway
data_client_config = InteractiveBrokersDataClientConfig(
    ibg_client_id=1,
    use_regular_trading_hours=False,  # Include extended hours
    market_data_type=IBMarketDataTypeEnum.REALTIME,
    instrument_provider=instrument_provider_config,
    dockerized_gateway=dockerized_gateway_config,
)

# Execution client with dockerized gateway
exec_client_config = InteractiveBrokersExecClientConfig(
    ibg_client_id=1,
    account_id=os.environ.get("TWS_ACCOUNT"),  # Live account ID
    instrument_provider=instrument_provider_config,
    dockerized_gateway=dockerized_gateway_config,
    routing=RoutingConfig(default=True),
)

# Live trading node configuration
config_node = TradingNodeConfig(
    trader_id="LIVE-TRADER-001",
    logging=LoggingConfig(log_level="INFO"),
    data_clients={IB: data_client_config},
    exec_clients={IB: exec_client_config},
    data_engine=LiveDataEngineConfig(
        time_bars_timestamp_on_close=False,
        validate_data_sequence=True,
    ),
)
```

#### Multi-Client Configuration

For advanced setups, you can configure multiple clients with different purposes:

```python
# Separate data and execution clients with different client IDs
data_client_config = InteractiveBrokersDataClientConfig(
    ibg_host="127.0.0.1",
    ibg_port=7497,
    ibg_client_id=1,  # Data client uses ID 1
    market_data_type=IBMarketDataTypeEnum.REALTIME,
    instrument_provider=instrument_provider_config,
)

exec_client_config = InteractiveBrokersExecClientConfig(
    ibg_host="127.0.0.1",
    ibg_port=7497,
    ibg_client_id=2,  # Execution client uses ID 2
    account_id="DU123456",
    instrument_provider=instrument_provider_config,
    routing=RoutingConfig(default=True),
)
```

### Running the Trading Node

```python
def run_trading_node():
    """Run the trading node with proper error handling."""
    node = None
    try:
        # Create and build node
        node = TradingNode(config=config_node)
        node.add_data_client_factory(IB, InteractiveBrokersLiveDataClientFactory)
        node.add_exec_client_factory(IB, InteractiveBrokersLiveExecClientFactory)
        node.build()

        # Set venue for portfolio
        node.portfolio.set_specific_venue(IB_VENUE)

        # Add your strategies here
        # node.trader.add_strategy(YourStrategy())

        # Run the node
        node.run()

    except KeyboardInterrupt:
        print("Shutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if node:
            node.dispose()

if __name__ == "__main__":
    run_trading_node()
```

### Additional Configuration Options

#### Environment Variables

Set these environment variables for easier configuration:

```bash
export TWS_USERNAME="your_ib_username"
export TWS_PASSWORD="your_ib_password"
export TWS_ACCOUNT="your_account_id"
export IB_MAX_CONNECTION_ATTEMPTS="5"  # Optional: limit reconnection attempts
```

#### Logging Configuration

```python
# Enhanced logging configuration
logging_config = LoggingConfig(
    log_level="INFO",
    log_level_file="DEBUG",
    log_file_format="json",  # JSON format for structured logging
    log_component_levels={
        "InteractiveBrokersClient": "DEBUG",
        "InteractiveBrokersDataClient": "INFO",
        "InteractiveBrokersExecutionClient": "INFO",
    },
)
```

You can find additional examples here: <https://github.com/nautechsystems/nautilus_trader/tree/develop/examples/live/interactive_brokers>

## Troubleshooting

### Common Connection Issues

#### Connection Refused

- **Cause**: TWS/Gateway not running or wrong port
- **Solution**: Verify TWS/Gateway is running and check port configuration
- **Default Ports**: TWS (7497/7496), IB Gateway (4002/4001)

#### Authentication Errors

- **Cause**: Incorrect credentials or account not logged in
- **Solution**: Verify username/password and ensure account is logged into TWS/Gateway

#### Client ID Conflicts

- **Cause**: Multiple clients using the same client ID
- **Solution**: Use unique client IDs for each connection

#### Market Data Permissions

- **Cause**: Insufficient market data subscriptions
- **Solution**: Use `IBMarketDataTypeEnum.DELAYED_FROZEN` for testing or subscribe to required data feeds

### Error Codes

Interactive Brokers uses specific error codes. Common ones include:

- **200**: No security definition found
- **201**: Order rejected - reason follows
- **202**: Order cancelled
- **300**: Can't find EId with ticker ID
- **354**: Requested market data is not subscribed
- **2104**: Market data farm connection is OK
- **2106**: HMDS data farm connection is OK

### Performance Optimization

#### Reduce Data Volume

```python
# Reduce quote tick volume by ignoring size-only updates
data_config = InteractiveBrokersDataClientConfig(
    ignore_quote_tick_size_updates=True,
    # ... other config
)
```

#### Connection Management

```python
# Set reasonable timeouts
config = InteractiveBrokersDataClientConfig(
    connection_timeout=300,  # 5 minutes
    request_timeout=60,      # 1 minute
    # ... other config
)
```

#### Memory Management

- Use appropriate bar sizes for your strategy
- Limit the number of simultaneous subscriptions
- Consider using historical data for backtesting instead of live data

### Best Practices

#### Security

- Never hardcode credentials in source code
- Use environment variables for sensitive information
- Use paper trading for development and testing
- Set `read_only_api=True` for data-only applications

#### Development Workflow

1. **Start with Paper Trading**: Always test with paper trading first
2. **Use Delayed Data**: Use `DELAYED_FROZEN` market data for development
3. **Implement Proper Error Handling**: Handle connection losses and API errors gracefully
4. **Monitor Logs**: Enable appropriate logging levels for debugging
5. **Test Reconnection**: Test your strategy's behavior during connection interruptions

#### Production Deployment

- Use dockerized gateway for automated deployments
- Implement proper monitoring and alerting
- Set up log aggregation and analysis
- Use real-time data subscriptions only when necessary
- Implement circuit breakers and position limits

#### Order Management

- Always validate orders before submission
- Implement proper position sizing
- Use appropriate order types for your strategy
- Monitor order status and handle rejections
- Implement timeout handling for order operations

### Debugging Tips

#### Enable Debug Logging

```python
logging_config = LoggingConfig(
    log_level="DEBUG",
    log_component_levels={
        "InteractiveBrokersClient": "DEBUG",
    },
)
```

#### Monitor Connection Status

```python
# Check connection status in your strategy
if not self.data_client.is_connected:
    self.log.warning("Data client disconnected")
```

#### Validate Instruments

```python
# Ensure instruments are loaded before trading
instruments = self.cache.instruments()
if not instruments:
    self.log.error("No instruments loaded")
```

### Support and Resources

- **IB API Documentation**: [TWS API Guide](https://ibkrcampus.com/ibkr-api-page/trader-workstation-api/)
- **NautilusTrader Examples**: [GitHub Examples](https://github.com/nautechsystems/nautilus_trader/tree/develop/examples/live/interactive_brokers)
- **IB Contract Search**: [Contract Information Center](https://pennies.interactivebrokers.com/cstools/contract_info/)
- **Market Data Subscriptions**: [IB Market Data](https://www.interactivebrokers.com/en/trading/market-data.php)


---

file path: ./integrations/index.md
# Integrations

NautilusTrader uses modular *adapters* to connect to trading venues and data providers, translating raw APIs into a unified interface and normalized domain model.

The following integrations are currently supported:

| Name                                                                         | ID                    | Type                    | Status                                                  | Docs                                   |
| :--------------------------------------------------------------------------- | :-------------------- | :---------------------- | :------------------------------------------------------ | :------------------------------------- |
| [Betfair](https://betfair.com)                                               | `BETFAIR`             | Sports Betting Exchange | ![status](https://img.shields.io/badge/stable-green)    | [Guide](integrations/betfair.md)       |
| [Binance](https://binance.com)                                               | `BINANCE`             | Crypto Exchange (CEX)   | ![status](https://img.shields.io/badge/stable-green)    | [Guide](integrations/binance.md)       |
| [Binance US](https://binance.us)                                             | `BINANCE`             | Crypto Exchange (CEX)   | ![status](https://img.shields.io/badge/stable-green)    | [Guide](integrations/binance.md)       |
| [Binance Futures](https://www.binance.com/en/futures)                        | `BINANCE`             | Crypto Exchange (CEX)   | ![status](https://img.shields.io/badge/stable-green)    | [Guide](integrations/binance.md)       |
| [Bybit](https://www.bybit.com)                                               | `BYBIT`               | Crypto Exchange (CEX)   | ![status](https://img.shields.io/badge/stable-green)    | [Guide](integrations/bybit.md)         |
| [Coinbase International](https://www.coinbase.com/en/international-exchange) | `COINBASE_INTX`       | Crypto Exchange (CEX)   | ![status](https://img.shields.io/badge/stable-green)    | [Guide](integrations/coinbase_intx.md) |
| [Databento](https://databento.com)                                           | `DATABENTO`           | Data Provider           | ![status](https://img.shields.io/badge/stable-green)    | [Guide](integrations/databento.md)     |
| [dYdX](https://dydx.exchange/)                                               | `DYDX`                | Crypto Exchange (DEX)   | ![status](https://img.shields.io/badge/stable-green)    | [Guide](integrations/dydx.md)          |
| [Interactive Brokers](https://www.interactivebrokers.com)                    | `INTERACTIVE_BROKERS` | Brokerage (multi-venue) | ![status](https://img.shields.io/badge/stable-green)    | [Guide](integrations/ib.md)            |
| [OKX](https://okx.com)                                                       | `OKX`                 | Crypto Exchange (CEX)   | ![status](https://img.shields.io/badge/building-orange) | [Guide](integrations/okx.md)           |
| [Polymarket](https://polymarket.com)                                         | `POLYMARKET`          | Prediction Market (DEX) | ![status](https://img.shields.io/badge/stable-green)    | [Guide](integrations/polymarket.md)    |
| [Tardis](https://tardis.dev)                                                 | `TARDIS`              | Crypto Data Provider    | ![status](https://img.shields.io/badge/stable-green)    | [Guide](integrations/tardis.md)        |

- **ID**: The default client ID for the integrations adapter clients.
- **Type**: The type of integration (often the venue type).

## Status

- `building`: Under construction and likely not in a usable state.
- `beta`: Completed to a minimally working state and in a 'beta' testing phase.
- `stable`: Stabilized feature set and API, the integration has been tested by both developers and users to a reasonable level (some bugs may still remain).

## Implementation goals

The primary goal of NautilusTrader is to provide a unified trading system for
use with a variety of integrations. To support the widest range of trading
strategies, priority will be given to *standard* functionality:

- Requesting historical market data
- Streaming live market data
- Reconciling execution state
- Submitting standard order types with standard execution instructions
- Modifying existing orders (if possible on an exchange)
- Canceling orders

The implementation of each integration aims to meet the following criteria:

- Low-level client components should match the exchange API as closely as possible.
- The full range of an exchange's functionality (where applicable to NautilusTrader) should *eventually* be supported.
- Exchange specific data types will be added to support the functionality and return
  types which are reasonably expected by a user.
- Actions unsupported by an exchange or NautilusTrader will be logged as a warning or error when invoked.

## API unification

All integrations must conform to NautilusTrader’s system API, requiring normalization and standardization:

- Symbols should use the venue’s native symbol format unless disambiguation is required (e.g., Binance Spot vs. Binance Futures).
- Timestamps must use UNIX epoch nanoseconds. If milliseconds are used, field/property names should explicitly end with `_ms`.


---

file path: ./integrations/coinbase_intx.md
# Coinbase International

**This guide will walk you through using Coinbase International with NautilusTrader for data ingest and/or live trading**.

:::warning
The Coinbase International integration is currently in a beta testing phase.
Exercise caution and report any issues on GitHub.
:::

[Coinbase International Exchange](https://www.coinbase.com/en/international-exchange) provides non-US institutional clients with access to cryptocurrency perpetual futures and spot markets.
The exchange serves European and international traders by providing leveraged crypto derivatives, often restricted or unavailable in these regions.

Coinbase International brings a high standard of customer protection, a robust risk management framework and high-performance trading technology, including:

- Real-time 24/7/365 risk management.
- Liquidity from external market makers (no proprietary trading).
- Dynamic margin requirements and collateral assessments.
- Liquidation framework that meets rigorous compliance standards.
- Well-capitalized exchange to support tail market events.
- Collaboration with top-tier global regulators.

:::info
See the [Introducing Coinbase International Exchange](https://www.coinbase.com/en-au/blog/introducing-coinbase-international-exchange) blog article for more details.
:::

## Installation

:::note
No additional `coinbase_intx` installation is required; the adapter’s core components, written in Rust, are automatically compiled and linked during the build.
:::

## Examples

You can find live example scripts [here](https://github.com/nautechsystems/nautilus_trader/tree/develop/examples/live/coinbase_intx).
These examples demonstrate how to set up live market data feeds and execution clients for trading on Coinbase International.

## Overview

The following products are supported on the Coinbase International exchange:

- Perpetual Futures contracts
- Spot cryptocurrencies

This guide assumes a trader is setting up for both live market data feeds, and trade execution.
The Coinbase International adapter includes multiple components, which can be used together or
separately depending on the use case. These components work together to connect to Coinbase International’s APIs
for market data and execution.

- `CoinbaseIntxHttpClient`: REST API connectivity.
- `CoinbaseIntxWebSocketClient`: WebSocket API connectivity.
- `CoinbaseIntxInstrumentProvider`: Instrument parsing and loading functionality.
- `CoinbaseIntxDataClient`: A market data feed manager.
- `CoinbaseIntxExecutionClient`: An account management and trade execution gateway.
- `CoinbaseIntxLiveDataClientFactory`: Factory for Coinbase International data clients.
- `CoinbaseIntxLiveExecClientFactory`: Factory for Coinbase International execution clients.

:::note
Most users will simply define a configuration for a live trading node (described below),
and won't necessarily need to work with the above components directly.
:::

## Coinbase documentation

Coinbase International provides extensive API documentation for users which can be found in the [Coinbase Developer Platform](https://docs.cdp.coinbase.com/intx/docs/welcome).
We recommend also referring to the Coinbase International documentation in conjunction with this NautilusTrader integration guide.

## Data

### Instruments

On startup, the adapter automatically loads all available instruments from the Coinbase International REST API
and subscribes to the `INSTRUMENTS` WebSocket channel for updates. This ensures that the cache and clients requiring
up-to-date definitions for parsing always have the latest instrument data.

Available instrument types include:

- `CurrencyPair` (Spot cryptocurrencies)
- `CryptoPerpetual`

:::note
Index products have not yet been implemented.
:::

The following data types are available:

- `OrderBookDelta` (L2 market-by-price)
- `QuoteTick` (L1 top-of-book best bid/ask)
- `TradeTick`
- `Bar`
- `MarkPriceUpdate`
- `IndexPriceUpdate`

:::note
Historical data requests have not yet been implemented.
:::

### WebSocket market data

The data client connects to Coinbase International's WebSocket feed to stream real-time market data.
The WebSocket client handles automatic reconnection and re-subscribes to active subscriptions upon reconnecting.

## Execution

**The adapter is designed to trade one Coinbase International portfolio per execution client.**

### Selecting a Portfolio

To identify your available portfolios and their IDs, use the REST client by running the following script:

```bash
python nautilus_trader/adapters/coinbase_intx/scripts/list_portfolios.py
```

This will output a list of portfolio details, similar to the example below:

```bash
[{'borrow_disabled': False,
  'cross_collateral_enabled': False,
  'is_default': False,
  'is_lsp': False,
  'maker_fee_rate': '-0.00008',
  'name': 'hrp5587988499',
  'portfolio_id': '3mnk59ap-1-22',  # Your portfolio ID
  'portfolio_uuid': 'dd0958ad-0c9d-4445-a812-1870fe40d0e1',
  'pre_launch_trading_enabled': False,
  'taker_fee_rate': '0.00012',
  'trading_lock': False,
  'user_uuid': 'd4fbf7ea-9515-1068-8d60-4de91702c108'}]
```

### Configuring the Portfolio

To specify a portfolio for trading, set the `COINBASE_INTX_PORTFOLIO_ID` environment variable to
the desired `portfolio_id`. If you're using multiple execution clients, you can alternatively define
the `portfolio_id` in the execution configuration for each client.

## Capability Matrix

Coinbase International offers market, limit, and stop order types, enabling a broad range of strategies.

### Order Types

| Order Type             | Derivatives | Spot | Notes                                   |
|------------------------|-------------|------|-----------------------------------------|
| `MARKET`               | ✓           | ✓    | Must use `IOC` or `FOK` time-in-forc    |
| `LIMIT`                | ✓           | ✓    |                                         |
| `STOP_MARKET`          | ✓           | ✓    |                                         |
| `STOP_LIMIT`           | ✓           | ✓    |                                         |
| `MARKET_IF_TOUCHED`    | -           | -    | *Not supported*.                        |
| `LIMIT_IF_TOUCHED`     | -           | -    | *Not supported*.                        |
| `TRAILING_STOP_MARKET` | -           | -    | *Not supported*.                        |

### Execution Instructions

| Instruction   | Derivatives | Spot | Notes                                            |
|---------------|-------------|------|--------------------------------------------------|
| `post_only`   | ✓           | ✓    | Ensures orders only provide liquidity.           |
| `reduce_only` | ✓           | ✓    | Ensures orders only reduce existing positions.   |

### Time-in-Force Options

| Time-in-Force | Derivatives | Spot | Notes                                            |
|---------------|-------------|------|--------------------------------------------------|
| `GTC`         | ✓           | ✓    | Good Till Canceled.                              |
| `GTD`         | ✓           | ✓    | Good Till Date.                                  |
| `FOK`         | ✓           | ✓    | Fill or Kill.                                    |
| `IOC`         | ✓           | ✓    | Immediate or Cancel.                             |

### Advanced Order Features

| Feature            | Derivatives | Spot | Notes                                       |
|--------------------|-------------|------|---------------------------------------------|
| Order Modification | ✓           | ✓    | Price and quantity modification.             |
| Bracket/OCO Orders | ?           | ?    | Requires further investigation.              |
| Iceberg Orders     | ✓           | ✓    | Available via FIX protocol.                 |

### Configuration Options

The following execution client configuration options are available:

| Option                       | Default | Description                                          |
|------------------------------|---------|------------------------------------------------------|
| `portfolio_id`               | `None`  | Specifies the Coinbase International portfolio to trade. Required for execution. |
| `http_timeout_secs`          | `60`    | Default timeout for HTTP requests in seconds. |

### FIX Drop Copy Integration

The Coinbase International adapter includes a FIX (Financial Information eXchange) [drop copy](https://docs.cdp.coinbase.com/intx/docs/fix-msg-drop-copy) client.
This provides reliable, low-latency execution updates directly from Coinbase's matching engine.

:::note
This approach is necessary because execution messages are not provided over the WebSocket feed, and delivers faster and more reliable order execution updates than polling the REST API.
:::

The FIX client:

- Establishes a secure TCP/TLS connection and logs on automatically when the trading node starts.
- Handles connection monitoring and automatic reconnection and logon if the connection is interrupted.
- Properly logs out and closes the connection when the trading node stops.

The client processes several types of execution messages:

- Order status reports (canceled, expired, triggered).
- Fill reports (partial and complete fills).

The FIX credentials are automatically managed using the same API credentials as the REST and WebSocket clients.
No additional configuration is required beyond providing valid API credentials.

:::note
The REST client handles processing `REJECTED` and `ACCEPTED` status execution messages on order submission.
:::

### Account and Position Management

On startup, the execution client requests and loads your current account and execution state including:

- Available balances across all assets.
- Open orders.
- Open positions.

This provides your trading strategies with a complete picture of your account before placing new orders.

## Configuration

### Strategies

:::warning
Coinbase International has a strict specification for client order IDs.
Nautilus can meet the spec by using UUID4 values for client order IDs.
To comply, set the `use_uuid_client_order_ids=True` config option in your strategy configuration (otherwise, order submission will trigger an API error).

See the Coinbase International [Create order](https://docs.cdp.coinbase.com/intx/reference/createorder) REST API documentation for further details.
:::

An example configuration could be:

```python
from nautilus_trader.adapters.coinbase_intx import COINBASE_INTX, CoinbaseIntxDataClientConfig, CoinbaseIntxExecClientConfig
from nautilus_trader.live.node import TradingNode

config = TradingNodeConfig(
    ...,  # Further config omitted
    data_clients={
        COINBASE_INTX: CoinbaseIntxDataClientConfig(
            instrument_provider=InstrumentProviderConfig(load_all=True),
        ),
    },
    exec_clients={
        COINBASE_INTX: CoinbaseIntxExecClientConfig(
            instrument_provider=InstrumentProviderConfig(load_all=True),
        ),
    },
)

strat_config = TOBQuoterConfig(
    use_uuid_client_order_ids=True,  # <-- Necessary for Coinbase Intx
    instrument_id=instrument_id,
    external_order_claims=[instrument_id],
    ...,  # Further config omitted
)
```

Then, create a `TradingNode` and add the client factories:

```python
from nautilus_trader.adapters.coinbase_intx import COINBASE_INTX, CoinbaseIntxLiveDataClientFactory, CoinbaseIntxLiveExecClientFactory
from nautilus_trader.live.node import TradingNode

# Instantiate the live trading node with a configuration
node = TradingNode(config=config)

# Register the client factories with the node
node.add_data_client_factory(COINBASE_INTX, CoinbaseIntxLiveDataClientFactory)
node.add_exec_client_factory(COINBASE_INTX, CoinbaseIntxLiveExecClientFactory)

# Finally build the node
node.build()
```

### API Credentials

Provide credentials to the clients using one of the following methods.

Either pass values for the following configuration options:

- `api_key`
- `api_secret`
- `api_passphrase`
- `portfolio_id`

Or, set the following environment variables:

- `COINBASE_INTX_API_KEY`
- `COINBASE_INTX_API_SECRET`
- `COINBASE_INTX_API_PASSPHRASE`
- `COINBASE_INTX_PORTFOLIO_ID`

:::tip
We recommend using environment variables to manage your credentials.
:::

When starting the trading node, you'll receive immediate confirmation of whether your
credentials are valid and have trading permissions.

## Implementation notes

- **Heartbeats**: The adapter maintains heartbeats on both the WebSocket and FIX connections to ensure reliable connectivity.
- **Rate Limits**: The REST API client is configured to limit requests to the 40/second, as specified by Coinbase International.
- **Graceful Shutdown**: The adapter properly handles graceful shutdown, ensuring all pending messages are processed before disconnecting.
- **Thread Safety**: All adapter components are thread-safe, allowing them to be used from multiple threads concurrently.
- **Execution Model**: The adapter can be configured with a single Coinbase International portfolio per execution client. For trading multiple portfolios, you can create multiple execution clients.


---

file path: ./integrations/betfair.md
# Betfair

Founded in 2000, Betfair operates the world’s largest online betting exchange,
with its headquarters in London and satellite offices across the globe.

NautilusTrader provides an adapter for integrating with the Betfair REST API and
Exchange Streaming API.

## Installation

Install NautilusTrader with Betfair support via pip:

```bash
pip install --upgrade "nautilus_trader[betfair]"
```

To build from source with Betfair extras:

```bash
uv sync --all-extras
```

## Examples

You can find live example scripts [here](https://github.com/nautechsystems/nautilus_trader/tree/develop/examples/live/betfair/).

## Betfair documentation

For API details and troubleshooting, see the official [Betfair Developer Documentation](https://developer.betfair.com/en/get-started/).

## Application Keys

Betfair requires an Application Key to authenticate API requests. After registering and funding your account, obtain your key using the [API-NG Developer AppKeys Tool](https://apps.betfair.com/visualisers/api-ng-account-operations/).

:::info
See also the [Betfair Getting Started - Application Keys](https://betfair-developer-docs.atlassian.net/wiki/spaces/1smk3cen4v3lu3yomq5qye0ni/pages/2687105/Application+Keys) guide.
:::

## API credentials

Supply your Betfair credentials via environment variables or client configuration:

```bash
export BETFAIR_USERNAME=<your_username>
export BETFAIR_PASSWORD=<your_password>
export BETFAIR_APP_KEY=<your_app_key>
export BETFAIR_CERTS_DIR=<path_to_certificate_dir>
```

:::tip
We recommend using environment variables to manage your credentials.
:::

## Overview

The Betfair adapter provides three primary components:

- `BetfairInstrumentProvider`: loads Betfair markets and converts them into Nautilus instruments.
- `BetfairDataClient`: streams real-time market data from the Exchange Streaming API.
- `BetfairExecutionClient`: submits orders (bets) and tracks execution status via the REST API.

## Capability Matrix

Betfair operates as a betting exchange with unique characteristics compared to traditional financial exchanges:

### Order Types

| Order Type             | Betfair | Notes                               |
|------------------------|---------|-------------------------------------|
| `MARKET`               | -       | Not applicable to betting exchange. |
| `LIMIT`                | ✓       | Orders placed at specific odds.     |
| `STOP_MARKET`          | -       | *Not supported*.                    |
| `STOP_LIMIT`           | -       | *Not supported*.                    |
| `MARKET_IF_TOUCHED`    | -       | *Not supported*.                    |
| `LIMIT_IF_TOUCHED`     | -       | *Not supported*.                    |
| `TRAILING_STOP_MARKET` | -       | *Not supported*.                    |

### Execution Instructions

| Instruction   | Betfair | Notes                                   |
|---------------|---------|-----------------------------------------|
| `post_only`   | -       | Not applicable to betting exchange.     |
| `reduce_only` | -       | Not applicable to betting exchange.     |

### Time-in-Force Options

| Time-in-Force | Betfair | Notes                                   |
|---------------|---------|-----------------------------------------|
| `GTC`         | -       | Betting exchange uses different model.  |
| `GTD`         | -       | Betting exchange uses different model.  |
| `FOK`         | -       | Betting exchange uses different model.  |
| `IOC`         | -       | Betting exchange uses different model.  |

### Advanced Order Features

| Feature            | Betfair | Notes                                    |
|--------------------|---------|------------------------------------------|
| Order Modification | ✓       | Limited to non-exposure changing fields. |
| Bracket/OCO Orders | -       | *Not supported*.                         |
| Iceberg Orders     | -       | *Not supported*.                         |

### Configuration Options

The following execution client configuration options affect order behavior:

| Option                       | Default | Description                                          |
|------------------------------|---------|------------------------------------------------------|
| `calculate_account_state`    | `True`  | If `True`, calculates account state from events. |
| `request_account_state_secs` | `300`   | Interval for account state checks in seconds (0 disables). |
| `reconcile_market_ids_only`  | `False` | If `True`, only reconciles orders for configured market IDs. |
| `ignore_external_orders`     | `False` | If `True`, silently ignores orders not found in cache. |

## Configuration

Here is a minimal example showing how to configure a live `TradingNode` with Betfair clients:

```python
from nautilus_trader.adapters.betfair import BETFAIR
from nautilus_trader.adapters.betfair import BetfairLiveDataClientFactory
from nautilus_trader.adapters.betfair import BetfairLiveExecClientFactory
from nautilus_trader.config import TradingNodeConfig
from nautilus_trader.live.node import TradingNode

# Configure Betfair data and execution clients (using AUD account currency)
config = TradingNodeConfig(
    data_clients={BETFAIR: {"account_currency": "AUD"}},
    exec_clients={BETFAIR: {"account_currency": "AUD"}},
)

# Build the TradingNode with Betfair adapter factories
node = TradingNode(config)
node.add_data_client_factory(BETFAIR, BetfairLiveDataClientFactory)
node.add_exec_client_factory(BETFAIR, BetfairLiveExecClientFactory)
node.build()
```


---

file path: ./integrations/okx.md
# OKX

:::warning
The OKX integration is still under development and only supports linear perpetual instruments.
:::

:::info
We are currently working on this integration guide.
:::


---

file path: ./integrations/dydx.md
# dYdX

:::info
We are currently working on this integration guide.
:::

dYdX is one of the largest decentralized cryptocurrency exchanges in terms of daily trading volume
for crypto derivative products. dYdX runs on smart contracts on the Ethereum blockchain, and allows
users to trade with no intermediaries. This integration supports live market data ingestion and order
execution with dYdX v4, which is the first version of the protocol to be fully decentralized with no
central components.

## Installation

To install NautilusTrader with dYdX support:

```bash
pip install --upgrade "nautilus_trader[dydx]"
```

To build from source with all extras (including dYdX):

```bash
uv sync --all-extras
```

## Examples

You can find live example scripts [here](https://github.com/nautechsystems/nautilus_trader/tree/develop/examples/live/dydx/).

## Overview

This guide assumes a trader is setting up for both live market data feeds, and trade execution.
The dYdX adapter includes multiple components, which can be used together or separately depending
on the use case.

- `DYDXHttpClient`: Low-level HTTP API connectivity.
- `DYDXWebSocketClient`: Low-level WebSocket API connectivity.
- `DYDXAccountGRPCAPI`: Low-level gRPC API connectivity for account updates.
- `DYDXInstrumentProvider`: Instrument parsing and loading functionality.
- `DYDXDataClient`: A market data feed manager.
- `DYDXExecutionClient`: An account management and trade execution gateway.
- `DYDXLiveDataClientFactory`: Factory for dYdX data clients (used by the trading node builder).
- `DYDXLiveExecClientFactory`: Factory for dYdX execution clients (used by the trading node builder).

:::note
Most users will simply define a configuration for a live trading node (as below),
and won't need to necessarily work with these lower level components directly.
:::

## Symbology

Only perpetual contracts are available on dYdX. To be consistent with other adapters and to be
futureproof in case other products become available on dYdX, NautilusTrader appends `-PERP` for all
available perpetual symbols. For example, the Bitcoin/USD-C perpetual futures contract is identified
as `BTC-USD-PERP`. The quote currency for all markets is USD-C. Therefore, dYdX abbreviates it to USD.

## Short-term and long-term orders

dYdX makes a distinction between short-term orders and long-term orders (or stateful orders).
Short-term orders are meant to be placed immediately and belongs in the same block the order was received.
These orders stay in-memory up to 20 blocks, with only their fill amount and expiry block height being committed to state.
Short-term orders are mainly intended for use by market makers with high throughput or for market orders.

By default, all orders are sent as short-term orders. To construct long-term orders, you can attach a tag to
an order like this:

```python
from nautilus_trader.adapters.dydx import DYDXOrderTags

order: LimitOrder = self.order_factory.limit(
    instrument_id=self.instrument_id,
    order_side=OrderSide.BUY,
    quantity=self.instrument.make_qty(self.trade_size),
    price=self.instrument.make_price(price),
    time_in_force=TimeInForce.GTD,
    expire_time=self.clock.utc_now() + pd.Timedelta(minutes=10),
    post_only=True,
    emulation_trigger=self.emulation_trigger,
    tags=[DYDXOrderTags(is_short_term_order=False).value],
)
```

To specify the number of blocks that an order is active:

```python
from nautilus_trader.adapters.dydx import DYDXOrderTags

order: LimitOrder = self.order_factory.limit(
    instrument_id=self.instrument_id,
    order_side=OrderSide.BUY,
    quantity=self.instrument.make_qty(self.trade_size),
    price=self.instrument.make_price(price),
    time_in_force=TimeInForce.GTD,
    expire_time=self.clock.utc_now() + pd.Timedelta(seconds=5),
    post_only=True,
    emulation_trigger=self.emulation_trigger,
    tags=[DYDXOrderTags(is_short_term_order=True, num_blocks_open=5).value],
)
```

## Market orders

Market orders require specifying a price to for price slippage protection and use hidden orders.
By setting a price for a market order, you can limit the potential price slippage. For example,
if you set the price of $100 for a market buy order, the order will only be executed if the market price
is at or below $100. If the market price is above $100, the order will not be executed.

Some exchanges, including dYdX, support hidden orders. A hidden order is an order that is not visible
to other market participants, but is still executable. By setting a price for a market order, you can
create a hidden order that will only be executed if the market price reaches the specified price.

If the market price is not specified, a default value of 0 is used.

To specify the price when creating a market order:

```python
order = self.order_factory.market(
    instrument_id=self.instrument_id,
    order_side=OrderSide.BUY,
    quantity=self.instrument.make_qty(self.trade_size),
    time_in_force=TimeInForce.IOC,
    tags=[DYDXOrderTags(is_short_term_order=True, market_order_price=Price.from_str("10_000")).value],
)
```

## Stop limit and stop market orders

Both stop limit and stop market conditional orders can be submitted. dYdX only supports long-term orders
for conditional orders.

## Capability Matrix

dYdX supports perpetual futures trading with a comprehensive set of order types and execution features.

### Order Types

| Order Type             | Perpetuals | Notes                                   |
|------------------------|------------|-----------------------------------------|
| `MARKET`               | ✓          | Requires price for slippage protection. |
| `LIMIT`                | ✓          |                                         |
| `STOP_MARKET`          | ✓          | Long-term orders only.                  |
| `STOP_LIMIT`           | ✓          | Long-term orders only.                  |
| `MARKET_IF_TOUCHED`    | -          | *Not supported*.                        |
| `LIMIT_IF_TOUCHED`     | -          | *Not supported*.                        |
| `TRAILING_STOP_MARKET` | -          | *Not supported*.                        |

### Execution Instructions

| Instruction   | Perpetuals | Notes                                           |
|---------------|------------|-------------------------------------------------|
| `post_only`   | ✓          | Supported on all order types.                   |
| `reduce_only` | ✓          | Supported on all order types.                   |

### Time-in-Force Options

| Time-in-Force | Perpetuals | Notes                                           |
|---------------|------------|-------------------------------------------------|
| `GTC`         | ✓          | Good Till Canceled.                             |
| `GTD`         | ✓          | Good Till Date.                                 |
| `FOK`         | ✓          | Fill or Kill.                                   |
| `IOC`         | ✓          | Immediate or Cancel.                            |

### Advanced Order Features

| Feature            | Perpetuals | Notes                                           |
|--------------------|------------|-------------------------------------------------|
| Order Modification | ✓          | Short-term orders only; cancel-replace method.  |
| Bracket/OCO Orders | -          | *Not supported*.                                |
| Iceberg Orders     | -          | *Not supported*.                                |

### Configuration Options

The following execution client configuration options are available:

| Option                       | Default | Description                                          |
|------------------------------|---------|------------------------------------------------------|
| `subaccount`                 | `0`     | Subaccount number (venue creates subaccount 0 by default). |
| `wallet_address`             | `None`  | dYdX wallet address for the account. |
| `mnemonic`                   | `None`  | Mnemonic for generating private key for order signing. |
| `is_testnet`                 | `False` | If `True`, connects to testnet; if `False`, connects to mainnet. |

### Order Classification

dYdX classifies orders as either **short-term** or **long-term** orders:

- **Short-term orders**: Default for all orders; intended for high-frequency trading and market orders.
- **Long-term orders**: Required for conditional orders; use `DYDXOrderTags` to specify.

## Configuration

The product types for each client must be specified in the configurations.

### Execution Clients

The account type must be a margin account to trade the perpetual futures contracts.

The most common use case is to configure a live `TradingNode` to include dYdX
data and execution clients. To achieve this, add a `DYDX` section to your client
configuration(s):

```python
from nautilus_trader.live.node import TradingNode

config = TradingNodeConfig(
    ...,  # Omitted
    data_clients={
        "DYDX": {
            "wallet_address": "YOUR_DYDX_WALLET_ADDRESS",
            "is_testnet": False,
        },
    },
    exec_clients={
        "DYDX": {
            "wallet_address": "YOUR_DYDX_WALLET_ADDRESS",
            "subaccount": "YOUR_DYDX_SUBACCOUNT_NUMBER"
            "mnemonic": "YOUR_MNEMONIC",
            "is_testnet": False,
        },
    },
)
```

Then, create a `TradingNode` and add the client factories:

```python
from nautilus_trader.adapters.dydx import DYDXLiveDataClientFactory
from nautilus_trader.adapters.dydx import DYDXLiveExecClientFactory
from nautilus_trader.live.node import TradingNode

# Instantiate the live trading node with a configuration
node = TradingNode(config=config)

# Register the client factories with the node
node.add_data_client_factory("DYDX", DYDXLiveDataClientFactory)
node.add_exec_client_factory("DYDX", DYDXLiveExecClientFactory)

# Finally build the node
node.build()
```

### API Credentials

There are two options for supplying your credentials to the dYdX clients.
Either pass the corresponding `wallet_address` and `mnemonic` values to the configuration objects, or
set the following environment variables:

For dYdX live clients, you can set:

- `DYDX_WALLET_ADDRESS`
- `DYDX_MNEMONIC`

For dYdX testnet clients, you can set:

- `DYDX_TESTNET_WALLET_ADDRESS`
- `DYDX_TESTNET_MNEMONIC`

:::tip
We recommend using environment variables to manage your credentials.
:::

The data client is using the wallet address to determine the trading fees. The trading fees are used during back tests only.

### Testnets

It's also possible to configure one or both clients to connect to the dYdX testnet.
Simply set the `is_testnet` option to `True` (this is `False` by default):

```python
config = TradingNodeConfig(
    ...,  # Omitted
    data_clients={
        "DYDX": {
            "wallet_address": "YOUR_DYDX_WALLET_ADDRESS",
            "is_testnet": True,
        },
    },
    exec_clients={
        "DYDX": {
            "wallet_address": "YOUR_DYDX_WALLET_ADDRESS",
            "subaccount": "YOUR_DYDX_SUBACCOUNT_NUMBER"
            "mnemonic": "YOUR_MNEMONIC",
            "is_testnet": True,
        },
    },
)
```

### Parser Warnings

Some dYdX instruments are unable to be parsed into Nautilus objects if they
contain enormous field values beyond what can be handled by the platform.
In these cases, a *warn and continue* approach is taken (the instrument will not be available).

## Order books

Order books can be maintained at full depth or top-of-book quotes depending on the
subscription. The venue does not provide quotes, but the adapter subscribes to order
book deltas and sends new quotes to the `DataEngine` when there is a top-of-book price or size change.


---

file path: ./integrations/polymarket.md
# Polymarket

Founded in 2020, Polymarket is the world’s largest decentralized prediction market platform,
enabling traders to speculate on the outcomes of world events by buying and selling binary option contracts using cryptocurrency.

NautilusTrader provides a venue integration for data and execution via Polymarket's Central Limit Order Book (CLOB) API.
The integration leverages the [official Python CLOB client library](https://github.com/Polymarket/py-clob-client)
to facilitate interaction with the Polymarket platform.

NautilusTrader is designed to work with Polymarket's signature type 0, supporting EIP712 signatures from externally owned accounts (EOA).
This integration ensures that traders can execute orders securely and efficiently, using the most common on-chain signature method,
while NautilusTrader abstracts the complexity of signing and preparing orders for seamless execution.

## Installation

To install NautilusTrader with Polymarket support:

```bash
pip install --upgrade "nautilus_trader[polymarket]"
```

To build from source with all extras (including Polymarket):

```bash
uv sync --all-extras
```

## Examples

You can find live example scripts [here](https://github.com/nautechsystems/nautilus_trader/tree/develop/examples/live/polymarket/).

## Binary options

A [binary option](https://en.wikipedia.org/wiki/Binary_option) is a type of financial exotic option contract in which traders bet on the outcome of a yes-or-no proposition.
If the prediction is correct, the trader receives a fixed payout; otherwise, they receive nothing.

All assets traded on Polymarket are quoted and settled in **USDC.e (PoS)**, [see below](#usdce-pos) for more information.

## Polymarket documentation

Polymarket offers comprehensive resources for different audiences:

- [Polymarket Learn](https://learn.polymarket.com/): Educational content and guides for users to understand the platform and how to engage with it.
- [Polymarket CLOB API](https://docs.polymarket.com/#introduction): Technical documentation for developers interacting with the Polymarket CLOB API.

## Overview

This guide assumes a trader is setting up for both live market data feeds, and trade execution.
The Polymarket integration adapter includes multiple components, which can be used together or
separately depending on the use case.

- `PolymarketWebSocketClient`: Low-level WebSocket API connectivity (built on top of the Nautilus `WebSocketClient` written in Rust).
- `PolymarketInstrumentProvider`: Instrument parsing and loading functionality for `BinaryOption` instruments.
- `PolymarketDataClient`: A market data feed manager.
- `PolymarketExecutionClient`: A trade execution gateway.
- `PolymarketLiveDataClientFactory`: Factory for Polymarket data clients (used by the trading node builder).
- `PolymarketLiveExecClientFactory`: Factory for Polymarket execution clients (used by the trading node builder).

:::note
Most users will simply define a configuration for a live trading node (as below),
and won't need to necessarily work with these lower level components directly.
:::

## USDC.e (PoS)

**USDC.e** is a bridged version of USDC from Ethereum to the Polygon network, operating on Polygon's **Proof of Stake (PoS)** chain.
This enables faster, more cost-efficient transactions on Polygon while maintaining backing by USDC on Ethereum.

The contract address is [0x2791bca1f2de4661ed88a30c99a7a9449aa84174](https://polygonscan.com/address/0x2791bca1f2de4661ed88a30c99a7a9449aa84174) on the Polygon blockchain.
More information can be found in this [blog](https://polygon.technology/blog/phase-one-of-native-usdc-migration-on-polygon-pos-is-underway).

## Wallets and accounts

To interact with Polymarket via NautilusTrader, you’ll need a **Polygon**-compatible wallet (such as MetaMask).
The integration uses Externally Owned Account (EOA) signature types compatible with EIP712, meaning the wallet is directly owned by the trader/user.
This contrasts with the signature types used for Polymarket-administered wallets (such as those accessed via their user interface).

A single wallet address is supported per trader instance when using environment variables,
or multiple wallets could be configured with multiple `PolymarketExecutionClient` instances.

:::info
Ensure your wallet is funded with **USDC.e**, otherwise you will encounter the "not enough balance / allowance" API error when submitting orders.
:::

### Setting Allowances for Polymarket Contracts

Before you can start trading, you need to ensure that your wallet has allowances set for Polymarket's smart contracts.
You can do this by running the provided script located at `/adapters/polymarket/scripts/set_allowances.py`.

This script is adapted from a [gist](https://gist.github.com/poly-rodr/44313920481de58d5a3f6d1f8226bd5e) created by @poly-rodr.

:::note
You only need to run this script **once** per EOA wallet that you intend to use for trading on Polymarket.
:::

This script automates the process of approving the necessary allowances for the Polymarket contracts.
It sets approvals for the USDC token and Conditional Token Framework (CTF) contract to allow the
Polymarket CLOB Exchange to interact with your funds.

Before running the script, ensure the following prerequisites are met:

- Install the web3 Python package: `pip install --upgrade web3==5.28`
- Have a **Polygon**-compatible wallet funded with some MATIC (used for gas fees).
- Set the following environment variables in your shell:
  - `POLYGON_PRIVATE_KEY`: Your private key for the **Polygon**-compatible wallet.
  - `POLYGON_PUBLIC_KEY`: Your public key for the **Polygon**-compatible wallet.

Once you have these in place, the script will:

- Approve the maximum possible amount of USDC (using the `MAX_INT` value) for the Polymarket USDC token contract.
- Set the approval for the CTF contract, allowing it to interact with your account for trading purposes.

:::note
You can also adjust the approval amount in the script instead of using `MAX_INT`,
with the amount specified in *fractional units* of **USDC.e**, though this has not been tested.
:::

Ensure that your private key and public key are correctly stored in the environment variables before running the script.
Here's an example of how to set the variables in your terminal session:

```bash
export POLYGON_PRIVATE_KEY="YOUR_PRIVATE_KEY"
export POLYGON_PUBLIC_KEY="YOUR_PUBLIC_KEY"
```

Run the script using:

```bash
python nautilus_trader/adapters/polymarket/scripts/set_allowances.py
```

### Script Breakdown

The script performs the following actions:

- Connects to the Polygon network via an RPC URL (<https://polygon-rpc.com/>).
- Signs and sends a transaction to approve the maximum USDC allowance for Polymarket contracts.
- Sets approval for the CTF contract to manage Conditional Tokens on your behalf.
- Repeats the approval process for specific addresses like the Polymarket CLOB Exchange and Neg Risk Adapter.

This allows Polymarket to interact with your funds when executing trades and ensures smooth integration with the CLOB Exchange.

## API keys

To trade with Polymarket using an EOA wallet, follow these steps to generate your API keys:

1. Ensure the following environment variables are set:

- `POLYMARKET_PK`: Your private key for signing transactions.
- `POLYMARKET_FUNDER`: The wallet address (public key) on the **Polygon** network used for funding trades on Polymarket.

1. Run the script using:

   ```bash
   python nautilus_trader/adapters/polymarket/scripts/create_api_key.py
   ```

The script will generate and print API credentials, which you should save to the following environment variables:

- `POLYMARKET_API_KEY`
- `POLYMARKET_API_SECRET`
- `POLYMARKET_PASSPHRASE`

These can then be used for Polymarket client configurations:

- `PolymarketDataClientConfig`
- `PolymarketExecClientConfig`

## Configuration

When setting up NautilusTrader to work with Polymarket, it’s crucial to properly configure the necessary parameters, particularly the private key.

**Key parameters**

- `private_key`: This is the private key for your external EOA wallet (*not* the Polymarket wallet accessed through their GUI). This private key allows the system to sign and send transactions on behalf of the external account interacting with Polymarket. If not explicitly provided in the configuration, it will automatically source the `POLYMARKET_PK` environment variable.
- `funder`: This refers to the **USDC.e** wallet address used for funding trades. If not provided, will source the `POLYMARKET_FUNDER` environment variable.
- API credentials: You will need to provide the following API credentials to interact with the Polymarket CLOB:
  - `api_key`: If not provided, will source the `POLYMARKET_API_KEY` environment variable.
  - `api_secret`: If not provided, will source the `POLYMARKET_API_SECRET` environment variable.
  - `passphrase`: If not provided, will source the `POLYMARKET_PASSPHRASE` environment variable.

:::tip
We recommend using environment variables to manage your credentials.
:::

## Capability Matrix

Polymarket operates as a prediction market with limited order complexity compared to traditional exchanges.

### Order Types

| Order Type             | Binary Options | Notes                               |
|------------------------|----------------|-------------------------------------|
| `MARKET`               | ✓              | Executed as marketable limit order. |
| `LIMIT`                | ✓              |                                     |
| `STOP_MARKET`          | -              | *Not supported*.                    |
| `STOP_LIMIT`           | -              | *Not supported*.                    |
| `MARKET_IF_TOUCHED`    | -              | *Not supported*.                    |
| `LIMIT_IF_TOUCHED`     | -              | *Not supported*.                    |
| `TRAILING_STOP_MARKET` | -              | *Not supported*.                    |

### Execution Instructions

| Instruction   | Binary Options | Notes                                     |
|---------------|----------------|-------------------------------------------|
| `post_only`   | -              | *Not supported*.                          |
| `reduce_only` | -              | *Not supported*.                          |

### Time-in-Force Options

| Time-in-Force | Binary Options | Notes                                     |
|---------------|----------------|-------------------------------------------|
| `GTC`         | ✓              | Good Till Canceled.                       |
| `GTD`         | ✓              | Good Till Date.                           |
| `FOK`         | ✓              | Fill or Kill.                             |
| `IOC`         | ✓              | Immediate or Cancel (maps to FAK).        |

### Advanced Order Features

| Feature            | Binary Options | Notes                                |
|--------------------|----------------|--------------------------------------|
| Order Modification | -              | Cancellation functionality only.     |
| Bracket/OCO Orders | -              | *Not supported*.                     |
| Iceberg Orders     | -              | *Not supported*.                     |

### Configuration Options

The following execution client configuration options are available:

| Option                               | Default | Description                      |
|--------------------------------------|---------|----------------------------------|
| `signature_type`                     | `0`     | Polymarket signature type (EOA). |
| `funder`                             | `None`  | Wallet address for funding USDC transactions. |
| `generate_order_history_from_trades` | `False` | Experimental feature to generate order reports from trade history (*not recommended*). |
| `log_raw_ws_messages`                | `False` | If `True`, logs raw WebSocket messages (performance penalty from pretty JSON formatting). |

## Trades

Trades on Polymarket can have the following statuses:

- `MATCHED`: Trade has been matched and sent to the executor service by the operator, the executor service submits the trade as a transaction to the Exchange contract.
- `MINED`: Trade is observed to be mined into the chain, and no finality threshold is established.
- `CONFIRMED`: Trade has achieved strong probabilistic finality and was successful.
- `RETRYING`: Trade transaction has failed (revert or reorg) and is being retried/resubmitted by the operator.
- `FAILED`: Trade has failed and is not being retried.

Once a trade is initially matched, subsequent trade status updates will be received via the WebSocket.
NautilusTrader records the initial trade details in the `info` field of the `OrderFilled` event,
with additional trade events stored in the cache as JSON under a custom key to retain this information.

## Reconciliation

The Polymarket API returns either all **active** (open) orders or specific orders when queried by the
Polymarket order ID (`venue_order_id`). The execution reconciliation procedure for Polymarkert is as follows:

- Generate order reports for all instruments with active (open) orders, as reported by Polymarket.
- Generate position reports from contract balances reported by Polymarket, *per instruments available in the cache*.
- Compare these reports with Nautilus execution state.
- Generate missing orders to bring Nautilus execution state in line with positions reported by Polymarket.

**Note**: Polymarket does not directly provide data for orders which are no longer active.

:::warning
An optional execution client configuration, `generate_order_history_from_trades`, is currently under development.
It is not recommended for production use at this time.
:::

## WebSockets

The `PolymarketWebSocketClient` is built on top of the high-performance Nautilus `WebSocketClient` base class, written in Rust.

### Data

The main data WebSocket handles all `market` channel subscriptions received during the initial
connection sequence, up to `ws_connection_delay_secs`. For any additional subscriptions, a new `PolymarketWebSocketClient` is
created for each new instrument (asset).

### Execution

The main execution WebSocket manages all `user` channel subscriptions based on the Polymarket instruments
available in the cache during the initial connection sequence. When trading commands are issued for additional instruments,
a separate `PolymarketWebSocketClient` is created for each new instrument (asset).

:::note
Polymarket does not support unsubscribing from channel streams once subscribed.
:::

## Limitations and considerations

The following limitations and considerations are currently known:

- Order signing via the Polymarket Python client is slow, taking around one second.
- Post-only orders are not supported.
- Reduce-only orders are not supported.


---

file path: ./integrations/binance.md
# Binance

Founded in 2017, Binance is one of the largest cryptocurrency exchanges in terms
of daily trading volume, and open interest of crypto assets and crypto
derivative products. This integration supports live market data ingest and order
execution with Binance.

## Installation

To install NautilusTrader with Binance support:

```bash
pip install --upgrade "nautilus_trader[binance]"
```

To build from source with all extras (including Binance):

```bash
uv sync --all-extras
```

## Examples

You can find live example scripts [here](https://github.com/nautechsystems/nautilus_trader/tree/develop/examples/live/binance/).

## Overview

The Binance adapter supports the following product types:

- Spot markets (including Binance US)
- USDT-Margined Futures (perpetual and delivery)
- Coin-Margined Futures

:::note
Margin trading (cross & isolated) is not implemented at this time.
Contributions via [GitHub issue #2631](https://github.com/nautechsystems/nautilus_trader/issues/#2631)
or pull requests to add margin trading functionality are welcome.
:::

### Product Support Matrix

| Product Type                             | Supported | Notes                               |
|------------------------------------------|-----------|-------------------------------------|
| Spot Markets (incl. Binance US)          | ✓         |                                     |
| Margin Accounts (Cross & Isolated)       | ✗         | Margin trading not implemented      |
| USDT-Margined Futures (PERP & Delivery)  | ✓         |                                     |
| Coin-Margined Futures                    | ✓         |                                     |

This guide assumes a trader is setting up for both live market data feeds, and trade execution.
The Binance adapter includes multiple components, which can be used together or separately depending
on the use case.

- `BinanceHttpClient`: Low-level HTTP API connectivity.
- `BinanceWebSocketClient`: Low-level WebSocket API connectivity.
- `BinanceInstrumentProvider`: Instrument parsing and loading functionality.
- `BinanceSpotDataClient`/`BinanceFuturesDataClient`: A market data feed manager.
- `BinanceSpotExecutionClient`/`BinanceFuturesExecutionClient`: An account management and trade execution gateway.
- `BinanceLiveDataClientFactory`: Factory for Binance data clients (used by the trading node builder).
- `BinanceLiveExecClientFactory`: Factory for Binance execution clients (used by the trading node builder).

:::note
Most users will simply define a configuration for a live trading node (as below),
and won't need to necessarily work with these lower level components directly.
:::

## Data Types

To provide complete API functionality to traders, the integration includes several
custom data types:

- `BinanceTicker`: Represents data returned for Binance 24-hour ticker subscriptions, including comprehensive price and statistical information.
- `BinanceBar`: Represents data for historical requests or real-time subscriptions to Binance bars, with additional volume metrics.
- `BinanceFuturesMarkPriceUpdate`: Represents mark price updates for Binance Futures subscriptions.

See the Binance [API Reference](../api_reference/adapters/binance.md) for full definitions.

## Symbology

As per the Nautilus unification policy for symbols, the native Binance symbols are used where possible including for
spot assets and futures contracts. Because NautilusTrader is capable of multi-venue + multi-account
trading, it's necessary to explicitly clarify the difference between `BTCUSDT` as the spot and margin traded
pair, and the `BTCUSDT` perpetual futures contract (this symbol is used for *both* natively by Binance).

Therefore, Nautilus appends the suffix `-PERP` to all perpetual symbols.
E.g. for Binance Futures, the `BTCUSDT` perpetual futures contract symbol would be `BTCUSDT-PERP` within the Nautilus system boundary.

## Capability Matrix

The following tables detail the order types, execution instructions, and time-in-force options supported across different Binance account types:

### Order Types

| Order Type             | Spot | Margin | USDT Futures | Coin Futures | Notes                   |
|------------------------|------|--------|--------------|--------------|-------------------------|
| `MARKET`               | ✓    | ✓      | ✓            | ✓            |                         |
| `LIMIT`                | ✓    | ✓      | ✓            | ✓            |                         |
| `STOP_MARKET`          | -    | ✓      | ✓            | ✓            | Not supported for Spot. |
| `STOP_LIMIT`           | ✓    | ✓      | ✓            | ✓            |                         |
| `MARKET_IF_TOUCHED`    | -    | -      | ✓            | ✓            | Futures only.           |
| `LIMIT_IF_TOUCHED`     | ✓    | ✓      | ✓            | ✓            |                         |
| `TRAILING_STOP_MARKET` | -    | -      | ✓            | ✓            | Futures only.           |

### Execution Instructions

| Instruction   | Spot | Margin | USDT Futures | Coin Futures | Notes                                 |
|---------------|------|--------|--------------|--------------|---------------------------------------|
| `post_only`   | ✓    | ✓      | ✓            | ✓            | See restrictions below.               |
| `reduce_only` | -    | -      | ✓            | ✓            | Futures only; disabled in Hedge Mode. |

#### Post-Only Restrictions

Only *limit* order types support `post_only`.

| Order Type               | Spot | Margin | USDT Futures | Coin Futures | Notes                                                      |
|--------------------------|------|--------|--------------|--------------|------------------------------------------------------------|
| `LIMIT`                  | ✓    | ✓      | ✓            | ✓            | Uses `LIMIT_MAKER` for Spot/Margin, `GTX` TIF for Futures. |
| `STOP_LIMIT`             | -    | -      | ✓            | ✓            | Not supported for Spot/Margin.                             |

### Time-in-Force Options

| Time-in-Force | Spot | Margin | USDT Futures | Coin Futures | Notes                                           |
|---------------|------|--------|--------------|--------------|-------------------------------------------------|
| `GTC`         | ✓    | ✓      | ✓            | ✓            | Good Till Canceled.                             |
| `GTD`         | ✓*   | ✓*     | ✓            | ✓            | *Converted to GTC for Spot/Margin with warning. |
| `FOK`         | ✓    | ✓      | ✓            | ✓            | Fill or Kill.                                   |
| `IOC`         | ✓    | ✓      | ✓            | ✓            | Immediate or Cancel.                            |

### Advanced Order Features

| Feature            | Spot | Margin | USDT Futures | Coin Futures | Notes                                        |
|--------------------|------|--------|--------------|--------------|----------------------------------------------|
| Order Modification | ✓    | ✓      | ✓            | ✓            | Price and quantity for `LIMIT` orders only.  |
| Bracket/OCO Orders | ✓    | ✓      | ✓            | ✓            | One-Cancels-Other for stop loss/take profit. |
| Iceberg Orders     | ✓    | ✓      | ✓            | ✓            | Large orders split into visible portions.    |

### Configuration Options

The following execution client configuration options affect order behavior:

| Option                       | Default | Description                                          |
|------------------------------|---------|------------------------------------------------------|
| `use_gtd`                    | `True`  | If `True`, uses Binance GTD TIF; if `False`, remaps GTD to GTC for local management. |
| `use_reduce_only`            | `True`  | If `True`, sends `reduce_only` instruction to exchange; if `False`, always sends `False`. |
| `use_position_ids`           | `True`  | If `True`, uses Binance Futures hedging position IDs; if `False`, enables virtual positions. |
| `treat_expired_as_canceled`  | `False` | If `True`, treats `EXPIRED` execution type as `CANCELED` for consistent handling. |
| `futures_leverages`          | `None`  | Dict to set initial leverage per symbol for Futures accounts. |
| `futures_margin_types`       | `None`  | Dict to set margin type (isolated/cross) per symbol for Futures accounts. |

### Trailing Stops

Binance uses the concept of an activation price for trailing stops, as detailed in their [documentation](https://www.binance.com/en/support/faq/what-is-a-trailing-stop-order-360042299292).
This approach is somewhat unconventional. For trailing stop orders to function on Binance, the activation price should be set using the `activation_price` parameter.

Note that the activation price is **not** the same as the trigger/STOP price. Binance will always calculate the trigger price for the order based on the current market price and the callback rate provided by `trailing_offset`.
The activation price is simply the price at which the order will begin trailing based on the callback rate.

:::warning
For Binance trailing stop orders, you must use `activation_price` instead of `trigger_price`. Using `trigger_price` will result in an order rejection.
:::

When submitting trailing stop orders from your strategy, you have two options:

1. Use the `activation_price` to manually set the activation price.
2. Leave the `activation_price` as `None`, activating the trailing mechanism immediately.

You must also have at least *one* of the following:

- The `activation_price` for the order is set.
- (or) you have subscribed to quotes for the instrument you're submitting the order for (used to infer activation price).
- (or) you have subscribed to trades for the instrument you're submitting the order for (used to infer activation price).

## Configuration

The most common use case is to configure a live `TradingNode` to include Binance
data and execution clients. To achieve this, add a `BINANCE` section to your client
configuration(s):

```python
from nautilus_trader.adapters.binance import BINANCE
from nautilus_trader.live.node import TradingNode

config = TradingNodeConfig(
    ...,  # Omitted
    data_clients={
        BINANCE: {
            "api_key": "YOUR_BINANCE_API_KEY",
            "api_secret": "YOUR_BINANCE_API_SECRET",
            "account_type": "spot",  # {spot, margin, usdt_future, coin_future}
            "base_url_http": None,  # Override with custom endpoint
            "base_url_ws": None,  # Override with custom endpoint
            "us": False,  # If client is for Binance US
        },
    },
    exec_clients={
        BINANCE: {
            "api_key": "YOUR_BINANCE_API_KEY",
            "api_secret": "YOUR_BINANCE_API_SECRET",
            "account_type": "spot",  # {spot, margin, usdt_future, coin_future}
            "base_url_http": None,  # Override with custom endpoint
            "base_url_ws": None,  # Override with custom endpoint
            "us": False,  # If client is for Binance US
        },
    },
)
```

Then, create a `TradingNode` and add the client factories:

```python
from nautilus_trader.adapters.binance import BINANCE
from nautilus_trader.adapters.binance import BinanceLiveDataClientFactory
from nautilus_trader.adapters.binance import BinanceLiveExecClientFactory
from nautilus_trader.live.node import TradingNode

# Instantiate the live trading node with a configuration
node = TradingNode(config=config)

# Register the client factories with the node
node.add_data_client_factory(BINANCE, BinanceLiveDataClientFactory)
node.add_exec_client_factory(BINANCE, BinanceLiveExecClientFactory)

# Finally build the node
node.build()
```

### API Credentials

There are two options for supplying your credentials to the Binance clients.
Either pass the corresponding `api_key` and `api_secret` values to the configuration objects, or
set the following environment variables:

For Binance Spot/Margin live clients, you can set:

- `BINANCE_API_KEY`
- `BINANCE_API_SECRET`

For Binance Spot/Margin testnet clients, you can set:

- `BINANCE_TESTNET_API_KEY`
- `BINANCE_TESTNET_API_SECRET`

For Binance Futures live clients, you can set:

- `BINANCE_FUTURES_API_KEY`
- `BINANCE_FUTURES_API_SECRET`

For Binance Futures testnet clients, you can set:

- `BINANCE_FUTURES_TESTNET_API_KEY`
- `BINANCE_FUTURES_TESTNET_API_SECRET`

When starting the trading node, you'll receive immediate confirmation of whether your
credentials are valid and have trading permissions.

### Account Type

All the Binance account types will be supported for live trading. Set the `account_type`
using the `BinanceAccountType` enum. The account type options are:

- `SPOT`
- `MARGIN` (Margin shared between open positions)
- `ISOLATED_MARGIN` (Margin assigned to a single position)
- `USDT_FUTURE` (USDT or BUSD stablecoins as collateral)
- `COIN_FUTURE` (other cryptocurrency as collateral)

:::tip
We recommend using environment variables to manage your credentials.
:::

### Base URL Overrides

It's possible to override the default base URLs for both HTTP Rest and
WebSocket APIs. This is useful for configuring API clusters for performance reasons,
or when Binance has provided you with specialized endpoints.

### Binance US

There is support for Binance US accounts by setting the `us` option in the configs
to `True` (this is `False` by default). All functionality available to US accounts
should behave identically to standard Binance.

### Testnets

It's also possible to configure one or both clients to connect to the Binance testnet.
Simply set the `testnet` option to `True` (this is `False` by default):

```python
from nautilus_trader.adapters.binance import BINANCE

config = TradingNodeConfig(
    ...,  # Omitted
    data_clients={
        BINANCE: {
            "api_key": "YOUR_BINANCE_TESTNET_API_KEY",
            "api_secret": "YOUR_BINANCE_TESTNET_API_SECRET",
            "account_type": "spot",  # {spot, margin, usdt_future}
            "testnet": True,  # If client uses the testnet
        },
    },
    exec_clients={
        BINANCE: {
            "api_key": "YOUR_BINANCE_TESTNET_API_KEY",
            "api_secret": "YOUR_BINANCE_TESTNET_API_SECRET",
            "account_type": "spot",  # {spot, margin, usdt_future}
            "testnet": True,  # If client uses the testnet
        },
    },
)
```

### Aggregated Trades

Binance provides aggregated trade data endpoints as an alternative source of trades.
In comparison to the default trade endpoints, aggregated trade data endpoints can return all
ticks between a `start_time` and `end_time`.

To use aggregated trades and the endpoint features, set the `use_agg_trade_ticks` option
to `True` (this is `False` by default.)

### Parser Warnings

Some Binance instruments are unable to be parsed into Nautilus objects if they
contain enormous field values beyond what can be handled by the platform.
In these cases, a *warn and continue* approach is taken (the instrument will not
be available).

These warnings may cause unnecessary log noise, and so it's possible to
configure the provider to not log the warnings, as per the client configuration
example below:

```python
from nautilus_trader.config import InstrumentProviderConfig

instrument_provider=InstrumentProviderConfig(
    load_all=True,
    log_warnings=False,
)
```

### Futures Hedge Mode

Binance Futures Hedge mode is a position mode where a trader opens positions in both long and short
directions to mitigate risk and potentially profit from market volatility.

To use Binance Future Hedge mode, you need to follow the three items below:

- 1. Before starting the strategy, ensure that hedge mode is configured on Binance.
- 2. Set the `use_reduce_only` option to `False` in BinanceExecClientConfig (this is `True` by default).

    ```python
    from nautilus_trader.adapters.binance import BINANCE

    config = TradingNodeConfig(
        ...,  # Omitted
        data_clients={
            BINANCE: BinanceDataClientConfig(
                api_key=None,  # 'BINANCE_API_KEY' env var
                api_secret=None,  # 'BINANCE_API_SECRET' env var
                account_type=BinanceAccountType.USDT_FUTURE,
                base_url_http=None,  # Override with custom endpoint
                base_url_ws=None,  # Override with custom endpoint
            ),
        },
        exec_clients={
            BINANCE: BinanceExecClientConfig(
                api_key=None,  # 'BINANCE_API_KEY' env var
                api_secret=None,  # 'BINANCE_API_SECRET' env var
                account_type=BinanceAccountType.USDT_FUTURE,
                base_url_http=None,  # Override with custom endpoint
                base_url_ws=None,  # Override with custom endpoint
                use_reduce_only=False,  # Must be disabled for Hedge mode
            ),
        }
    )
    ```

- 3. When submitting an order, use a suffix (`LONG` or `SHORT` ) in the `position_id` to indicate the position direction.

    ```python
    class EMACrossHedgeMode(Strategy):
        ...,  # Omitted
        def buy(self) -> None:
            """
            Users simple buy method (example).
            """
            order: MarketOrder = self.order_factory.market(
                instrument_id=self.instrument_id,
                order_side=OrderSide.BUY,
                quantity=self.instrument.make_qty(self.trade_size),
                # time_in_force=TimeInForce.FOK,
            )

            # LONG suffix is recognized as a long position by Binance adapter.
            position_id = PositionId(f"{self.instrument_id}-LONG")
            self.submit_order(order, position_id)

        def sell(self) -> None:
            """
            Users simple sell method (example).
            """
            order: MarketOrder = self.order_factory.market(
                instrument_id=self.instrument_id,
                order_side=OrderSide.SELL,
                quantity=self.instrument.make_qty(self.trade_size),
                # time_in_force=TimeInForce.FOK,
            )
            # SHORT suffix is recognized as a short position by Binance adapter.
            position_id = PositionId(f"{self.instrument_id}-SHORT")
            self.submit_order(order, position_id)
    ```

## Order books

Order books can be maintained at full or partial depths depending on the
subscription. WebSocket stream throttling is different between Spot and Futures exchanges,
Nautilus will use the highest streaming rate possible:

Order books can be maintained at full or partial depths based on the subscription settings.
WebSocket stream update rates differ between Spot and Futures exchanges, with Nautilus using the
highest available streaming rate:

- **Spot**: 100ms
- **Futures**: 0ms (*unthrottled*)

There is a limitation of one order book per instrument per trader instance.
As stream subscriptions may vary, the latest order book data (deltas or snapshots)
subscription will be used by the Binance data client.

Order book snapshot rebuilds will be triggered on:

- Initial subscription of the order book data.
- Data websocket reconnects.

The sequence of events is as follows:

- Deltas will start buffered.
- Snapshot is requested and awaited.
- Snapshot response is parsed to `OrderBookDeltas`.
- Snapshot deltas are sent to the `DataEngine`.
- Buffered deltas are iterated, dropping those where the sequence number is not greater than the last delta in the snapshot.
- Deltas will stop buffering.
- Remaining deltas are sent to the `DataEngine`.

## Binance data differences

The `ts_event` field value for `QuoteTick` objects will differ between Spot and Futures exchanges,
where the former does not provide an event timestamp, so the `ts_init` is used (which means `ts_event` and `ts_init` are identical).

## Binance specific data

It's possible to subscribe to Binance specific data streams as they become available to the
adapter over time.

:::note
Bars are not considered 'Binance specific' and can be subscribed to in the normal way.
As more adapters are built out which need for example mark price and funding rate updates, then these
methods may eventually become first-class (not requiring custom/generic subscriptions as below).
:::

### BinanceFuturesMarkPriceUpdate

You can subscribe to `BinanceFuturesMarkPriceUpdate` (including funding rating info)
data streams by subscribing in the following way from your actor or strategy:

```python
from nautilus_trader.adapters.binance import BinanceFuturesMarkPriceUpdate
from nautilus_trader.model import DataType
from nautilus_trader.model import ClientId

# In your `on_start` method
self.subscribe_data(
    data_type=DataType(BinanceFuturesMarkPriceUpdate, metadata={"instrument_id": self.instrument.id}),
    client_id=ClientId("BINANCE"),
)
```

This will result in your actor/strategy passing these received `BinanceFuturesMarkPriceUpdate`
objects to your `on_data` method. You will need to check the type, as this
method acts as a flexible handler for all custom/generic data.

```python
from nautilus_trader.core import Data

def on_data(self, data: Data):
    # First check the type of data
    if isinstance(data, BinanceFuturesMarkPriceUpdate):
        # Do something with the data
```


---

file path: ./integrations/databento.md
# Databento

NautilusTrader provides an adapter for integrating with the Databento API and [Databento Binary Encoding (DBN)](https://databento.com/docs/standards-and-conventions/databento-binary-encoding) format data.
As Databento is purely a market data provider, there is no execution client provided - although a sandbox environment with simulated execution could still be set up.
It's also possible to match Databento data with Interactive Brokers execution, or to calculate traditional asset class signals for crypto trading.

The capabilities of this adapter include:

- Loading historical data from DBN files and decoding into Nautilus objects for backtesting or writing to the data catalog.
- Requesting historical data which is decoded to Nautilus objects to support live trading and backtesting.
- Subscribing to real-time data feeds which are decoded to Nautilus objects to support live trading and sandbox environments.

:::tip
[Databento](https://databento.com/signup) currently offers 125 USD in free data credits (historical data only) for new account sign-ups.

With careful requests, this is more than enough for testing and evaluation purposes.
We recommend you make use of the [/metadata.get_cost](https://databento.com/docs/api-reference-historical/metadata/metadata-get-cost) endpoint.
:::

## Overview

The adapter implementation takes the [databento-rs](https://crates.io/crates/databento) crate as a dependency,
which is the official Rust client library provided by Databento.

:::info
There is **no** need for an optional extra installation of `databento`, as the core components of the
adapter are compiled as static libraries and linked automatically during the build process.
:::

The following adapter classes are available:

- `DatabentoDataLoader`: Loads Databento Binary Encoding (DBN) data from files.
- `DatabentoInstrumentProvider`: Integrates with the Databento API (HTTP) to provide latest or historical instrument definitions.
- `DatabentoHistoricalClient`: Integrates with the Databento API (HTTP) for historical market data requests.
- `DatabentoLiveClient`: Integrates with the Databento API (raw TCP) for subscribing to real-time data feeds.
- `DatabentoDataClient`: Provides a `LiveMarketDataClient` implementation for running a trading node in real time.

:::info
As with the other integration adapters, most users will simply define a configuration for a live trading node (covered below),
and won't need to necessarily work with these lower level components directly.
:::

## Examples

You can find live example scripts [here](https://github.com/nautechsystems/nautilus_trader/tree/develop/examples/live/databento/).

## Databento documentation

Databento provides extensive documentation for new users which can be found in the [Databento new users guide](https://databento.com/docs/quickstart/new-user-guides).
We recommend also referring to the Databento documentation in conjunction with this NautilusTrader integration guide.

## Databento Binary Encoding (DBN)

Databento Binary Encoding (DBN) is an extremely fast message encoding and storage format for normalized market data.
The [DBN specification](https://databento.com/docs/standards-and-conventions/databento-binary-encoding) includes a simple, self-describing metadata header and a fixed set of struct definitions,
which enforce a standardized way to normalize market data.

The integration provides a decoder which can convert DBN format data to Nautilus objects.

The same Rust implemented Nautilus decoder is used for:

- Loading and decoding DBN files from disk
- Decoding historical and live data in real time

## Supported schemas

The following Databento schemas are supported by NautilusTrader:

| Databento schema | Nautilus data type                |
|:-----------------|:----------------------------------|
| MBO              | `OrderBookDelta`                  |
| MBP_1            | `(QuoteTick, Option<TradeTick>)`  |
| MBP_10           | `OrderBookDepth10`                |
| BBO_1S           | `QuoteTick`                       |
| BBO_1M           | `QuoteTick`                       |
| TBBO             | `(QuoteTick, TradeTick)`          |
| TRADES           | `TradeTick`                       |
| OHLCV_1S         | `Bar`                             |
| OHLCV_1M         | `Bar`                             |
| OHLCV_1H         | `Bar`                             |
| OHLCV_1D         | `Bar`                             |
| DEFINITION       | `Instrument` (various types)      |
| IMBALANCE        | `DatabentoImbalance`              |
| STATISTICS       | `DatabentoStatistics`             |
| STATUS           | `InstrumentStatus`                |

:::warning
NautilusTrader no longer supports Databento DBN v1 schema decoding.
You will need to migrate historical DBN v1 data to v2 or v3 for loading.
:::

:::info
See also the Databento [Schemas and data formats](https://databento.com/docs/schemas-and-data-formats) guide.
:::

## Instrument IDs and symbology

Databento market data includes an `instrument_id` field which is an integer assigned
by either the original source venue, or internally by Databento during normalization.

It's important to realize that this is different to the Nautilus `InstrumentId`
which is a string made up of a symbol + venue with a period separator i.e. `"{symbol}.{venue}"`.

The Nautilus decoder will use the Databento `raw_symbol` for the Nautilus `symbol` and an [ISO 10383 MIC](https://www.iso20022.org/market-identifier-codes) (Market Identifier Code)
from the Databento instrument definition message for the Nautilus `venue`.

Databento datasets are identified with a *dataset code* which is not the same
as a venue identifier. You can read more about Databento dataset naming conventions [here](https://databento.com/docs/api-reference-historical/basics/datasets).

Of particular note is for CME Globex MDP 3.0 data (`GLBX.MDP3` dataset code), the following
exchanges are all grouped under the `GLBX` venue. These mappings can be determined from the
instruments `exchange` field:

- `CBCM`: XCME-XCBT inter-exchange spread
- `NYUM`: XNYM-DUMX inter-exchange spread
- `XCBT`: Chicago Board of Trade (CBOT)
- `XCEC`: Commodities Exchange Center (COMEX)
- `XCME`: Chicago Mercantile Exchange (CME)
- `XFXS`: CME FX Link spread
- `XNYM`: New York Mercantile Exchange (NYMEX)

:::info
Other venue MICs can be found in the `venue` field of responses from the [metadata.list_publishers](https://databento.com/docs/api-reference-historical/metadata/metadata-list-publishers) endpoint.
:::

## Timestamps

Databento data includes various timestamp fields including (but not limited to):

- `ts_event`: The matching-engine-received timestamp expressed as the number of nanoseconds since the UNIX epoch.
- `ts_in_delta`: The matching-engine-sending timestamp expressed as the number of nanoseconds before `ts_recv`.
- `ts_recv`: The capture-server-received timestamp expressed as the number of nanoseconds since the UNIX epoch.
- `ts_out`: The Databento sending timestamp.

Nautilus data includes at *least* two timestamps (required by the `Data` contract):

- `ts_event`: UNIX timestamp (nanoseconds) when the data event occurred.
- `ts_init`: UNIX timestamp (nanoseconds) when the data object was created.

When decoding and normalizing Databento to Nautilus we generally assign the Databento `ts_recv` value to the Nautilus
`ts_event` field, as this timestamp is much more reliable and consistent, and is guaranteed to be monotonically increasing per instrument.
The exception to this are the `DatabentoImbalance` and `DatabentoStatistics` data types, which have fields for all timestamps as these types are defined specifically for the adapter.

:::info
See the following Databento docs for further information:

- [Databento standards and conventions - timestamps](https://databento.com/docs/standards-and-conventions/common-fields-enums-types#timestamps)
- [Databento timestamping guide](https://databento.com/docs/architecture/timestamping-guide)

:::

## Data types

The following section discusses Databento schema -> Nautilus data type equivalence
and considerations.

:::info
See Databento [schemas and data formats](https://databento.com/docs/schemas-and-data-formats).
:::

### Instrument definitions

Databento provides a single schema to cover all instrument classes, these are
decoded to the appropriate Nautilus `Instrument` types.

The following Databento instrument classes are supported by NautilusTrader:

| Databento instrument class | Code |  Nautilus instrument type    |
|----------------------------|------|------------------------------|
| Stock                      | `K`  | `Equity`                     |
| Future                     | `F`  | `FuturesContract`            |
| Call                       | `C`  | `OptionContract`             |
| Put                        | `P`  | `OptionContract`             |
| Future spread              | `S`  | `FuturesSpread`              |
| Option spread              | `T`  | `OptionSpread`               |
| Mixed spread               | `M`  | `OptionSpread`               |
| FX spot                    | `X`  | `CurrencyPair`               |
| Bond                       | `B`  | Not yet available            |

### MBO (market by order)

This schema is the highest granularity data offered by Databento, and represents
full order book depth. Some messages also provide trade information, and so when
decoding MBO messages Nautilus will produce an `OrderBookDelta` and optionally a
`TradeTick`.

The Nautilus live data client will buffer MBO messages until an `F_LAST` flag
is seen. A discrete `OrderBookDeltas` container object will then be passed to the
registered handler.

Order book snapshots are also buffered into a discrete `OrderBookDeltas` container
object, which occurs during the replay startup sequence.

### MBP-1 (market by price, top-of-book)

This schema represents the top-of-book only (quotes *and* trades). Like with MBO messages, some
messages carry trade information, and so when decoding MBP-1 messages Nautilus
will produce a `QuoteTick` and *also* a `TradeTick` if the message is a trade.

### OHLCV (bar aggregates)

The Databento bar aggregation messages are timestamped at the **open** of the bar interval.
The Nautilus decoder will normalize the `ts_event` timestamps to the **close** of the bar
(original `ts_event` + bar interval).

### Imbalance & Statistics

The Databento `imbalance` and `statistics` schemas cannot be represented as a built-in Nautilus data types,
and so they have specific types defined in Rust `DatabentoImbalance` and `DatabentoStatistics`.
Python bindings are provided via pyo3 (Rust) so the types behave a little differently to a built-in Nautilus
data types, where all attributes are pyo3 provided objects and not directly compatible
with certain methods which may expect a Cython provided type. There are pyo3 -> legacy Cython
object conversion methods available, which can be found in the API reference.

Here is a general pattern for converting a pyo3 `Price` to a Cython `Price`:

```python
price = Price.from_raw(pyo3_price.raw, pyo3_price.precision)
```

Additionally requesting for and subscribing to these data types requires the use of the
lower level generic methods for custom data types. The following example subscribes to the `imbalance`
schema for the `AAPL.XNAS` instrument (Apple Inc trading on the Nasdaq exchange):

```python
from nautilus_trader.adapters.databento import DATABENTO_CLIENT_ID
from nautilus_trader.adapters.databento import DatabentoImbalance
from nautilus_trader.model import DataType

instrument_id = InstrumentId.from_str("AAPL.XNAS")
self.subscribe_data(
    data_type=DataType(DatabentoImbalance, metadata={"instrument_id": instrument_id}),
    client_id=DATABENTO_CLIENT_ID,
)
```

Or requesting the previous days `statistics` schema for the `ES.FUT` parent symbol (all active E-mini S&P 500 futures contracts on the CME Globex exchange):

```python
from nautilus_trader.adapters.databento import DATABENTO_CLIENT_ID
from nautilus_trader.adapters.databento import DatabentoStatistics
from nautilus_trader.model import DataType

instrument_id = InstrumentId.from_str("ES.FUT.GLBX")
metadata = {
    "instrument_id": instrument_id,
    "start": "2024-03-06",
}
self.request_data(
    data_type=DataType(DatabentoStatistics, metadata=metadata),
    client_id=DATABENTO_CLIENT_ID,
)
```

## Performance considerations

When backtesting with Databento DBN data, there are two options:

- Store the data in DBN (`.dbn.zst`) format files and decode to Nautilus objects on every run
- Convert the DBN files to Nautilus objects and then write to the data catalog once (stored as Nautilus Parquet format on disk)

Whilst the DBN -> Nautilus decoder is implemented in Rust and has been optimized,
the best performance for backtesting will be achieved by writing the Nautilus
objects to the data catalog, which performs the decoding step once.

[DataFusion](https://arrow.apache.org/datafusion/) provides a query engine backend to efficiently load and stream
the Nautilus Parquet data from disk, which achieves extremely high through-put (at least an order of magnitude faster
than converting DBN -> Nautilus on the fly for every backtest run).

:::note
Performance benchmarks are currently under development.
:::

## Loading DBN data

You can load DBN files and convert the records to Nautilus objects using the
`DatabentoDataLoader` class. There are two main purposes for doing so:

- Pass the converted data to `BacktestEngine.add_data` directly for backtesting.
- Pass the converted data to `ParquetDataCatalog.write_data` for later streaming use with a `BacktestNode`.

### DBN data to a BacktestEngine

This code snippet demonstrates how to load DBN data and pass to a `BacktestEngine`.
Since the `BacktestEngine` needs an instrument added, we'll use a test instrument
provided by the `TestInstrumentProvider` (you could also pass an instrument object
which was parsed from a DBN file too).
The data is a month of TSLA (Tesla Inc) trades on the Nasdaq exchange:

```python
# Add instrument
TSLA_NASDAQ = TestInstrumentProvider.equity(symbol="TSLA")
engine.add_instrument(TSLA_NASDAQ)

# Decode data to legacy Cython objects
loader = DatabentoDataLoader()
trades = loader.from_dbn_file(
    path=TEST_DATA_DIR / "databento" / "temp" / "tsla-xnas-20240107-20240206.trades.dbn.zst",
    instrument_id=TSLA_NASDAQ.id,
)

# Add data
engine.add_data(trades)
```

### DBN data to a ParquetDataCatalog

This code snippet demonstrates how to load DBN data and write to a `ParquetDataCatalog`.
We pass a value of false for the `as_legacy_cython` flag, which will ensure the
DBN records are decoded as pyo3 (Rust) objects. It's worth noting that legacy Cython
objects can also be passed to `write_data`, but these need to be converted back to
pyo3 objects under the hood (so passing pyo3 objects is an optimization).

```python
# Initialize the catalog interface
# (will use the `NAUTILUS_PATH` env var as the path)
catalog = ParquetDataCatalog.from_env()

instrument_id = InstrumentId.from_str("TSLA.XNAS")

# Decode data to pyo3 objects
loader = DatabentoDataLoader()
trades = loader.from_dbn_file(
    path=TEST_DATA_DIR / "databento" / "temp" / "tsla-xnas-20240107-20240206.trades.dbn.zst",
    instrument_id=instrument_id,
    as_legacy_cython=False,  # This is an optimization for writing to the catalog
)

# Write data
catalog.write_data(trades)
```

:::info
See also the [Data concepts guide](../concepts/data.md).
:::

## Real-time client architecture

The `DatabentoDataClient` is a Python class which contains other Databento adapter classes.
There are two `DatabentoLiveClient`s per Databento dataset:

- One for MBO (order book deltas) real-time feeds
- One for all other real-time feeds

:::warning
There is currently a limitation that all MBO (order book deltas) subscriptions for a dataset have to be made at
node startup, to then be able to replay data from the beginning of the session. If subsequent subscriptions
arrive after start, then an error will be logged (and the subscription ignored).

There is no such limitation for any of the other Databento schemas.
:::

A single `DatabentoHistoricalClient` instance is reused between the `DatabentoInstrumentProvider` and `DatabentoDataClient`,
which makes historical instrument definitions and data requests.

## Configuration

The most common use case is to configure a live `TradingNode` to include a
Databento data client. To achieve this, add a `DATABENTO` section to your client
configuration(s):

```python
from nautilus_trader.adapters.databento import DATABENTO
from nautilus_trader.live.node import TradingNode

config = TradingNodeConfig(
    ...,  # Omitted
    data_clients={
        DATABENTO: {
            "api_key": None,  # 'DATABENTO_API_KEY' env var
            "http_gateway": None,  # Override for the default HTTP historical gateway
            "live_gateway": None,  # Override for the default raw TCP real-time gateway
            "instrument_provider": InstrumentProviderConfig(load_all=True),
            "instrument_ids": None,  # Nautilus instrument IDs to load on start
            "parent_symbols": None,  # Databento parent symbols to load on start
        },
    },
    ..., # Omitted
)
```

Then, create a `TradingNode` and add the client factory:

```python
from nautilus_trader.adapters.databento.factories import DatabentoLiveDataClientFactory
from nautilus_trader.live.node import TradingNode

# Instantiate the live trading node with a configuration
node = TradingNode(config=config)

# Register the client factory with the node
node.add_data_client_factory(DATABENTO, DatabentoLiveDataClientFactory)

# Finally build the node
node.build()
```

### Configuration parameters

- `api_key`: The Databento API secret key. If ``None`` then will source the `DATABENTO_API_KEY` environment variable.
- `http_gateway`: The historical HTTP client gateway override (useful for testing and typically not needed by most users).
- `live_gateway`: The raw TCP real-time client gateway override (useful for testing and typically not needed by most users).
- `parent_symbols`: The Databento parent symbols to subscribe to instrument definitions for on start. This is a map of Databento dataset keys -> to a sequence of the parent symbols, e.g. {'GLBX.MDP3', ['ES.FUT', 'ES.OPT']} (for all E-mini S&P 500 futures and options products).
- `instrument_ids`: The instrument IDs to request instrument definitions for on start.
- `timeout_initial_load`: The timeout (seconds) to wait for instruments to load (concurrently per dataset).
- `mbo_subscriptions_delay`: The timeout (seconds) to wait for MBO/L3 subscriptions (concurrently per dataset). After the timeout the MBO order book feed will start and replay messages from the initial snapshot and then all deltas.

:::tip
We recommend using environment variables to manage your credentials.
:::


---

file path: ./concepts/cache.md
# Cache

The `Cache` is a central in-memory database that automatically stores and manages all trading-related data.
Think of it as your trading system’s memory – storing everything from market data to order history to custom calculations.

The Cache serves multiple key purposes:

1. **Stores market data**:
   - Stores recent market history (e.g., order books, quotes, trades, bars).
   - Gives you access to both current and historical market data for your strategy.

2. **Tracks trading data**:
   - Maintains complete `Order` history and current execution state.
   - Tracks all `Position`s and `Account` information.
   - Stores `Instrument` definitions and `Currency` information.

3. **Stores custom data**:
   - Any user-defined objects or data can be stored in the `Cache` for later use.
   - Enables data sharing between different strategies.

## How Cache works

**Built-in types**:

- Data is automatically added to the `Cache` as it flows through the system.
- In live contexts, updates happen asynchronously - which means there might be a small delay between an event occurring and it appearing in the `Cache`.
- All data flows through the `Cache` before reaching your strategy’s callbacks – see the diagram below:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌───────────────────────┐
│                 │     │                 │     │                 │     │                       │
│                 │     │                 │     │                 │     │   Strategy callback:  │
│      Data       ├─────►   DataEngine    ├─────►     Cache       ├─────►                       │
│                 │     │                 │     │                 │     │   on_data(...)        │
│                 │     │                 │     │                 │     │                       │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └───────────────────────┘
```

### Basic example

Within a strategy, you can access the `Cache` through `self.cache`. Here’s a typical example:

:::note
Anywhere you find `self`, it refers mostly to the `Strategy` itself.
:::

```python
def on_bar(self, bar: Bar) -> None:
    # Current bar is provided in the parameter 'bar'

    # Get historical bars from Cache
    last_bar = self.cache.bar(self.bar_type, index=0)        # Last bar (practically the same as the 'bar' parameter)
    previous_bar = self.cache.bar(self.bar_type, index=1)    # Previous bar
    third_last_bar = self.cache.bar(self.bar_type, index=2)  # Third last bar

    # Get current position information
    if self.last_position_opened_id is not None:
        position = self.cache.position(self.last_position_opened_id)
        if position.is_open:
            # Check position details
            current_pnl = position.unrealized_pnl

    # Get all open orders for our instrument
    open_orders = self.cache.orders_open(instrument_id=self.instrument_id)
```

## Configuration

The `Cache`’s behavior and capacity can be configured through the `CacheConfig` class.
You can provide this configuration either to a `BacktestEngine` or a `TradingNode`, depending on your [environment context](architecture.md#environment-contexts).

Here's a basic example of configuring the `Cache`:

```python
from nautilus_trader.config import CacheConfig, BacktestEngineConfig, TradingNodeConfig

# For backtesting
engine_config = BacktestEngineConfig(
    cache=CacheConfig(
        tick_capacity=10_000,  # Store last 10,000 ticks per instrument
        bar_capacity=5_000,    # Store last 5,000 bars per bar type
    ),
)

# For live trading
node_config = TradingNodeConfig(
    cache=CacheConfig(
        tick_capacity=10_000,
        bar_capacity=5_000,
    ),
)
```

:::tip
By default, the `Cache` keeps the last 10,000 bars for each bar type and 10,000 trade ticks per instrument.
These limits provide a good balance between memory usage and data availability. Increase them if your strategy needs more historical data.
:::

### Configuration Options

The `CacheConfig` class supports these parameters:

```python
from nautilus_trader.config import CacheConfig

cache_config = CacheConfig(
    database: DatabaseConfig | None = None,  # Database configuration for persistence
    encoding: str = "msgpack",               # Data encoding format ('msgpack' or 'json')
    timestamps_as_iso8601: bool = False,     # Store timestamps as ISO8601 strings
    buffer_interval_ms: int | None = None,   # Buffer interval for batch operations
    use_trader_prefix: bool = True,          # Use trader prefix in keys
    use_instance_id: bool = False,           # Include instance ID in keys
    flush_on_start: bool = False,            # Clear database on startup
    drop_instruments_on_reset: bool = True,  # Clear instruments on reset
    tick_capacity: int = 10_000,             # Maximum ticks stored per instrument
    bar_capacity: int = 10_000,              # Maximum bars stored per each bar-type
)
```

:::note
Each bar type maintains its own separate capacity. For example, if you're using both 1-minute and 5-minute bars, each will store up to `bar_capacity` bars.
When `bar_capacity` is reached, the oldest data is automatically removed from the `Cache`.
:::

### Database Configuration

For persistence between system restarts, you can configure a database backend.

When is it useful to use persistence?

- **Long-running systems**: If you want your data to survive system restarts, upgrading, or unexpected failures, having a database configuration helps to pick up exactly where you left off.
- **Historical insights**: When you need to preserve past trading data for detailed post-analysis or audits.
- **Multi-node or distributed setups**: If multiple services or nodes need to access the same state, a persistent store helps ensure shared and consistent data.

```python
from nautilus_trader.config import DatabaseConfig

config = CacheConfig(
    database=DatabaseConfig(
        type="redis",      # Database type
        host="localhost",  # Database host
        port=6379,         # Database port
        timeout=2,         # Connection timeout (seconds)
    ),
)
```

## Using the Cache

### Accessing Market data

The `Cache` provides a comprehensive interface for accessing different types of market data, including order books, quotes, trades, bars.
All market data in the cache are stored with reverse indexing — meaning the most recent data is at index 0.

#### Bar(s) access

```python
# Get a list of all cached bars for a bar type
bars = self.cache.bars(bar_type)  # Returns List[Bar] or an empty list if no bars found

# Get the most recent bar
latest_bar = self.cache.bar(bar_type)  # Returns Bar or None if no such object exists

# Get a specific historical bar by index (0 = most recent)
second_last_bar = self.cache.bar(bar_type, index=1)  # Returns Bar or None if no such object exists

# Check if bars exist and get count
bar_count = self.cache.bar_count(bar_type)  # Returns number of bars in cache for the specified bar type
has_bars = self.cache.has_bars(bar_type)    # Returns bool indicating if any bars exist for the specified bar type
```

#### Quote ticks

```python
# Get quotes
quotes = self.cache.quote_ticks(instrument_id)                     # Returns List[QuoteTick] or an empty list if no quotes found
latest_quote = self.cache.quote_tick(instrument_id)                # Returns QuoteTick or None if no such object exists
second_last_quote = self.cache.quote_tick(instrument_id, index=1)  # Returns QuoteTick or None if no such object exists

# Check quote availability
quote_count = self.cache.quote_tick_count(instrument_id)  # Returns the number of quotes in cache for this instrument
has_quotes = self.cache.has_quote_ticks(instrument_id)    # Returns bool indicating if any quotes exist for this instrument
```

#### Trade ticks

```python
# Get trades
trades = self.cache.trade_ticks(instrument_id)         # Returns List[TradeTick] or an empty list if no trades found
latest_trade = self.cache.trade_tick(instrument_id)    # Returns TradeTick or None if no such object exists
second_last_trade = self.cache.trade_tick(instrument_id, index=1)  # Returns TradeTick or None if no such object exists

# Check trade availability
trade_count = self.cache.trade_tick_count(instrument_id)  # Returns the number of trades in cache for this instrument
has_trades = self.cache.has_trade_ticks(instrument_id)    # Returns bool indicating if any trades exist
```

#### Order Book

```python
# Get current order book
book = self.cache.order_book(instrument_id)  # Returns OrderBook or None if no such object exists

# Check if order book exists
has_book = self.cache.has_order_book(instrument_id)  # Returns bool indicating if an order book exists

# Get count of order book updates
update_count = self.cache.book_update_count(instrument_id)  # Returns the number of updates received
```

#### Price access

```python
from nautilus_trader.core.rust.model import PriceType

# Get current price by type; Returns Price or None.
price = self.cache.price(
    instrument_id=instrument_id,
    price_type=PriceType.MID,  # Options: BID, ASK, MID, LAST
)
```

#### Bar types

```python
from nautilus_trader.core.rust.model import PriceType, AggregationSource

# Get all available bar types for an instrument; Returns List[BarType].
bar_types = self.cache.bar_types(
    instrument_id=instrument_id,
    price_type=PriceType.LAST,  # Options: BID, ASK, MID, LAST
    aggregation_source=AggregationSource.EXTERNAL,
)
```

#### Simple example

```python
class MarketDataStrategy(Strategy):
    def on_start(self):
        # Subscribe to 1-minute bars
        self.bar_type = BarType.from_str(f"{self.instrument_id}-1-MINUTE-LAST-EXTERNAL")  # example of instrument_id = "EUR/USD.FXCM"
        self.subscribe_bars(self.bar_type)

    def on_bar(self, bar: Bar) -> None:
        bars = self.cache.bars(self.bar_type)[:3]
        if len(bars) < 3:   # Wait until we have at least 3 bars
            return

        # Access last 3 bars for analysis
        current_bar = bars[0]    # Most recent bar
        prev_bar = bars[1]       # Second to last bar
        prev_prev_bar = bars[2]  # Third to last bar

        # Get latest quote and trade
        latest_quote = self.cache.quote_tick(self.instrument_id)
        latest_trade = self.cache.trade_tick(self.instrument_id)

        if latest_quote is not None:
            current_spread = latest_quote.ask_price - latest_quote.bid_price
            self.log.info(f"Current spread: {current_spread}")
```

### Trading Objects

The `Cache` provides comprehensive access to all trading objects within the system, including:

- Orders
- Positions
- Accounts
- Instruments

#### Orders

Orders can be accessed and queried through multiple methods, with flexible filtering options by venue, strategy, instrument, and order side.

##### Basic Order Access

```python
# Get a specific order by its client order ID
order = self.cache.order(ClientOrderId("O-123"))

# Get all orders in the system
orders = self.cache.orders()

# Get orders filtered by specific criteria
orders_for_venue = self.cache.orders(venue=venue)                       # All orders for a specific venue
orders_for_strategy = self.cache.orders(strategy_id=strategy_id)        # All orders for a specific strategy
orders_for_instrument = self.cache.orders(instrument_id=instrument_id)  # All orders for an instrument
```

##### Order State Queries

```python
# Get orders by their current state
open_orders = self.cache.orders_open()          # Orders currently active at the venue
closed_orders = self.cache.orders_closed()      # Orders that have completed their lifecycle
emulated_orders = self.cache.orders_emulated()  # Orders being simulated locally by the system
inflight_orders = self.cache.orders_inflight()  # Orders submitted (or modified) to venue, but not yet confirmed

# Check specific order states
exists = self.cache.order_exists(client_order_id)            # Checks if an order with the given ID exists in the cache
is_open = self.cache.is_order_open(client_order_id)          # Checks if an order is currently open
is_closed = self.cache.is_order_closed(client_order_id)      # Checks if an order is closed
is_emulated = self.cache.is_order_emulated(client_order_id)  # Checks if an order is being simulated locally
is_inflight = self.cache.is_order_inflight(client_order_id)  # Checks if an order is submitted or modified, but not yet confirmed
```

##### Order Statistics

```python
# Get counts of orders in different states
open_count = self.cache.orders_open_count()          # Number of open orders
closed_count = self.cache.orders_closed_count()      # Number of closed orders
emulated_count = self.cache.orders_emulated_count()  # Number of emulated orders
inflight_count = self.cache.orders_inflight_count()  # Number of inflight orders
total_count = self.cache.orders_total_count()        # Total number of orders in the system

# Get filtered order counts
buy_orders_count = self.cache.orders_open_count(side=OrderSide.BUY)  # Number of currently open BUY orders
venue_orders_count = self.cache.orders_total_count(venue=venue)      # Total number of orders for a given venue
```

#### Positions

The `Cache` maintains a record of all positions and offers several ways to query them.

##### Position Access

```python
# Get a specific position by its ID
position = self.cache.position(PositionId("P-123"))

# Get positions by their state
all_positions = self.cache.positions()            # All positions in the system
open_positions = self.cache.positions_open()      # All currently open positions
closed_positions = self.cache.positions_closed()  # All closed positions

# Get positions filtered by various criteria
venue_positions = self.cache.positions(venue=venue)                       # Positions for a specific venue
instrument_positions = self.cache.positions(instrument_id=instrument_id)  # Positions for a specific instrument
strategy_positions = self.cache.positions(strategy_id=strategy_id)        # Positions for a specific strategy
long_positions = self.cache.positions(side=PositionSide.LONG)             # All long positions
```

##### Position State Queries

```python
# Check position states
exists = self.cache.position_exists(position_id)        # Checks if a position with the given ID exists
is_open = self.cache.is_position_open(position_id)      # Checks if a position is open
is_closed = self.cache.is_position_closed(position_id)  # Checks if a position is closed

# Get position and order relationships
orders = self.cache.orders_for_position(position_id)       # All orders related to a specific position
position = self.cache.position_for_order(client_order_id)  # Find the position associated with a specific order
```

##### Position Statistics

```python
# Get position counts in different states
open_count = self.cache.positions_open_count()      # Number of currently open positions
closed_count = self.cache.positions_closed_count()  # Number of closed positions
total_count = self.cache.positions_total_count()    # Total number of positions in the system

# Get filtered position counts
long_positions_count = self.cache.positions_open_count(side=PositionSide.LONG)              # Number of open long positions
instrument_positions_count = self.cache.positions_total_count(instrument_id=instrument_id)  # Number of positions for a given instrument
```

#### Accounts

```python
# Access account information
account = self.cache.account(account_id)       # Retrieve account by ID
account = self.cache.account_for_venue(venue)  # Retrieve account for a specific venue
account_id = self.cache.account_id(venue)      # Retrieve account ID for a venue
accounts = self.cache.accounts()               # Retrieve all accounts in the cache
```

#### Instruments and Currencies

##### Instruments

```python
# Get instrument information
instrument = self.cache.instrument(instrument_id) # Retrieve a specific instrument by its ID
all_instruments = self.cache.instruments()        # Retrieve all instruments in the cache

# Get filtered instruments
venue_instruments = self.cache.instruments(venue=venue)              # Instruments for a specific venue
instruments_by_underlying = self.cache.instruments(underlying="ES")  # Instruments by underlying

# Get instrument identifiers
instrument_ids = self.cache.instrument_ids()                   # Get all instrument IDs
venue_instrument_ids = self.cache.instrument_ids(venue=venue)  # Get instrument IDs for a specific venue
```

##### Currencies

```python
# Get currency information
currency = self.cache.load_currency("USD")  # Loads currency data for USD
```

---

### Custom Data

The `Cache` can also store and retrieve custom data types in addition to built-in market data and trading objects.
You can keep any user-defined data you want to share between system components (mostly Actors / Strategies).

#### Basic Storage and Retrieval

```python
# Call this code inside Strategy methods (`self` refers to Strategy)

# Store data
self.cache.add(key="my_key", value=b"some binary data")

# Retrieve data
stored_data = self.cache.get("my_key")  # Returns bytes or None
```

For more complex use cases, the `Cache` can store custom data objects that inherit from the `nautilus_trader.core.Data` base class.

:::warning
The `Cache` is not designed to be a full database replacement. For large datasets or complex querying needs, consider using a dedicated database system.
:::

## Best Practices and Common Questions

### Cache vs. Portfolio Usage

The `Cache` and `Portfolio` components serve different but complementary purposes in NautilusTrader:

**Cache**:

- Maintains the historical knowledge and current state of the trading system.
- Updates immediately for local state changes (initializing an order to be submitted)
- Updates asynchronously as external events occur (order is filled).
- Provides complete history of trading activity and market data.
- All data a strategy has received (events/updates) is stored in Cache.

**Portfolio**:

- Aggregated position/exposure and account information.
- Provides current state without history.

**Example**:

```python
class MyStrategy(Strategy):
    def on_position_changed(self, event: PositionEvent) -> None:
        # Use Cache when you need historical perspective
        position_history = self.cache.position_snapshots(event.position_id)

        # Use Portfolio when you need current real-time state
        current_exposure = self.portfolio.net_exposure(event.instrument_id)
```

### Cache vs. Strategy variables

Choosing between storing data in the `Cache` versus strategy variables depends on your specific needs:

**Cache Storage**:

- Use for data that needs to be shared between strategies.
- Best for data that needs to persist between system restarts.
- Acts as a central database accessible to all components.
- Ideal for state that needs to survive strategy resets.

**Strategy Variables**:

- Use for strategy-specific calculations.
- Better for temporary values and intermediate results.
- Provides faster access and better encapsulation.
- Best for data that only your strategy needs.

**Example**:

Example that clarifies how you might store data in the `Cache` so multiple strategies can access the same information.

```python
import pickle

class MyStrategy(Strategy):
    def on_start(self):
        # Prepare data you want to share with other strategies
        shared_data = {
            "last_reset": self.clock.timestamp_ns(),
            "trading_enabled": True,
            # Include any other fields that you want other strategies to read
        }

        # Store it in the cache with a descriptive key
        # This way, multiple strategies can call self.cache.get("shared_strategy_info")
        # to retrieve the same data
        self.cache.add("shared_strategy_info", pickle.dumps(shared_data))

```

How another strategy (running in parallel) can retrieve cached data above:

```python
import pickle

class AnotherStrategy(Strategy):
    def on_start(self):
        # Load the shared data from the same key
        data_bytes = self.cache.get("shared_strategy_info")
        if data_bytes is not None:
            shared_data = pickle.loads(data_bytes)
            self.log.info(f"Shared data retrieved: {shared_data}")
```


---

file path: ./concepts/backtesting.md
# Backtesting
Backtesting with NautilusTrader is a methodical simulation process that replicates trading
activities using a specific system implementation. This system is composed of various components
including the built-in engines, `Cache`, [MessageBus](message_bus.md), `Portfolio`, [Actors](actors.md), [Strategies](strategies.md), [Execution Algorithms](execution.md),
and other user-defined modules. The entire trading simulation is predicated on a stream of historical data processed by a
`BacktestEngine`. Once this data stream is exhausted, the engine concludes its operation, producing
detailed results and performance metrics for in-depth analysis.

It's important to recognize that NautilusTrader offers two distinct API levels for setting up and conducting backtests:

- **High-level API**: Uses a `BacktestNode` and configuration objects (`BacktestEngine`s are used internally).
- **Low-level API**: Uses a `BacktestEngine` directly with more "manual" setup.

## Choosing an API level

Consider using the **low-level** API when:

- Your entire data stream can be processed within the available machine resources (e.g., RAM).
- You prefer not to store data in the Nautilus-specific Parquet format.
- You have a specific need or preference to retain raw data in its original format (e.g., CSV, binary, etc.).
- You require fine-grained control over the `BacktestEngine`, such as the ability to re-run backtests on identical datasets while swapping out components (e.g., actors or strategies) or adjusting parameter configurations.

Consider using the **high-level** API when:

- Your data stream exceeds available memory, requiring streaming data in batches.
- You want to leverage the performance and convenience of the `ParquetDataCatalog` for storing data in the Nautilus-specific Parquet format.
- You value the flexibility and functionality of passing configuration objects to define and manage multiple backtest runs across various engines simultaneously.

## Low-level API

The low-level API centers around a `BacktestEngine`, where inputs are initialized and added manually via a Python script.
An instantiated `BacktestEngine` can accept the following:

- Lists of `Data` objects, which are automatically sorted into monotonic order based on `ts_init`.
- Multiple venues, manually initialized.
- Multiple actors, manually initialized and added.
- Multiple execution algorithms, manually initialized and added.

This approach offers detailed control over the backtesting process, allowing you to manually configure each component.

## High-level API

The high-level API centers around a `BacktestNode`, which orchestrates the management of multiple `BacktestEngine` instances,
each defined by a `BacktestRunConfig`. Multiple configurations can be bundled into a list and processed by the node in one run.

Each `BacktestRunConfig` object consists of the following:

- A list of `BacktestDataConfig` objects.
- A list of `BacktestVenueConfig` objects.
- A list of `ImportableActorConfig` objects.
- A list of `ImportableStrategyConfig` objects.
- A list of `ImportableExecAlgorithmConfig` objects.
- An optional `ImportableControllerConfig` object.
- An optional `BacktestEngineConfig` object, with a default configuration if not specified.

## Data

Data provided for backtesting drives the execution flow. Since a variety of data types can be used,
it's crucial that your venue configurations align with the data being provided for backtesting.
Mismatches between data and configuration can lead to unexpected behavior during execution.

NautilusTrader is primarily designed and optimized for order book data, which provides
a complete representation of every price level or order in the market, reflecting the real-time behavior of a trading venue.
This ensures the highest level of execution granularity and realism. However, if granular order book data is either not
available or necessary, then the platform has the capability of processing market data in the following descending order of detail:

1. **Order Book Data/Deltas (L3 market-by-order)**:
   - Providing comprehensive market depth and detailed order flow, with visibility of all individual orders.

2. **Order Book Data/Deltas (L2 market-by-price)**:
   - Providing market depth visibility across all price levels.

3. **Quote Ticks (L1 market-by-price)**:
   - Representing the "top of the book" by capturing only the best bid and ask prices and sizes.

4. **Trade Ticks**:
   - Reflecting actual executed trades, offering a precise view of transaction activity.

5. **Bars**:
   - Aggregating trading activity - typically over fixed time intervals, such as 1-minute, 1-hour, or 1-day.

### Choosing data: Cost vs. Accuracy

For many trading strategies, bar data (e.g., 1-minute) can be sufficient for backtesting and strategy development. This is
particularly important because bar data is typically much more accessible and cost-effective compared to tick or order book data.

Given this practical reality, Nautilus is designed to support bar-based backtesting with advanced features
that maximize simulation accuracy, even when working with lower granularity data.

:::tip
For some trading strategies, it can be practical to start development with bar data to validate core trading ideas.
If the strategy looks promising, but is more sensitive to precise execution timing (e.g., requires fills at specific prices
between OHLC levels, or uses tight take-profit/stop-loss levels), you can then invest in higher granularity data
for more accurate validation.
:::

## Venues

When initializing a venue for backtesting, you must specify its internal order `book_type` for execution processing from the following options:

- `L1_MBP`: Level 1 market-by-price (default). Only the top level of the order book is maintained.
- `L2_MBP`: Level 2 market-by-price. Order book depth is maintained, with a single order aggregated per price level.
- `L3_MBO`: Level 3 market-by-order. Order book depth is maintained, with all individual orders tracked as provided by the data.

:::note
The granularity of the data must match the specified order `book_type`. Nautilus cannot generate higher granularity data (L2 or L3) from lower-level data such as quotes, trades, or bars.
:::

:::warning
If you specify `L2_MBP` or `L3_MBO` as the venue’s `book_type`, all non-order book data (such as quotes, trades, and bars) will be ignored for execution processing.
This may cause orders to appear as though they are never filled. We are actively working on improved validation logic to prevent configuration and data mismatches.
:::

:::warning
When providing L2 or higher order book data, ensure that the `book_type` is updated to reflect the data's granularity.
Failing to do so will result in data aggregation: L2 data will be reduced to a single order per level, and L1 data will reflect only top-of-book levels.
:::

## Execution

### Bar Based Execution

Bar data provides a summary of market activity with four key prices for each time period (assuming bars are aggregated by trades):

- **Open**: opening price (first trade)
- **High**: highest price traded
- **Low**: lowest price traded
- **Close**: closing price (last trade)

While this gives us an overview of price movement, we lose some important details that we'd have with more granular data:

- We don't know in what order the market hit the high and low prices.
- We can't see exactly when prices changed within the time period.
- We don't know the actual sequence of trades that occurred.

This is why Nautilus processes bar data through a sophisticated system that attempts to maintain
the most realistic yet conservative market behavior possible, despite these limitations.
At its core, the platform always maintains an order book simulation - even when you provide less
granular data such as quotes, trades, or bars (although the simulation will only have a top level book).

#### Processing Bar Data

Even when you provide bar data, Nautilus maintains an internal order book for each instrument - just like a real venue would.

1. **Time Processing**:
   - Nautilus has a specific way of handling the timing of bar data *for execution* that's crucial for accurate simulation.
   - Bar timestamps (`ts_event`) are expected to represent the close time of the bar. This approach is most logical because it represents the moment when the bar is fully formed and its aggregation is complete.
   - The initialization time (`ts_init`) can be controlled using the `ts_init_delta` parameter in `BarDataWrangler`, which should typically be set to the bar's step size (timeframe) in nanoseconds.
   - The platform ensures all events happen in the correct sequence based on these timestamps, preventing any possibility of look-ahead bias in your backtests.

2. **Price Processing**:
   - The platform converts each bar's OHLC prices into a sequence of market updates.
   - These updates always follow the same order: Open → High → Low → Close.
   - If you provide multiple timeframes (like both 1-minute and 5-minute bars), the platform uses the more granular data for highest accuracy.

3. **Executions**:
   - When you place orders, they interact with the simulated order book just like they would on a real venue.
   - For MARKET orders, execution happens at the current simulated market price plus any configured latency.
   - For LIMIT orders working in the market, they'll execute if any of the bar's prices reach or cross your limit price (see below).
   - The matching engine continuously processes orders as OHLC prices move, rather than waiting for complete bars.

#### OHLC Prices Simulation

During backtest execution, each bar is converted into a sequence of four price points:

1. Opening price
2. High price *(Order between High/Low is configurable. See `bar_adaptive_high_low_ordering` below.)*
3. Low price
4. Closing price

The trading volume for that bar is **split evenly** among these four points (25% each). In marginal cases,
if the original bar's volume divided by 4 is less than the instrument's minimum `size_increment`,
we still use the minimum `size_increment` per price point to ensure valid market activity (e.g., 1 contract
for CME group exchanges).

How these price points are sequenced can be controlled via the `bar_adaptive_high_low_ordering` parameter when configuring a venue.

Nautilus supports two modes of bar processing:

1. **Fixed Ordering** (`bar_adaptive_high_low_ordering=False`, default)
   - Processes every bar in a fixed sequence: `Open → High → Low → Close`.
   - Simple and deterministic approach.

2. **Adaptive Ordering** (`bar_adaptive_high_low_ordering=True`)
   - Uses bar structure to estimate likely price path:
     - If Open is closer to High: processes as `Open → High → Low → Close`.
     - If Open is closer to Low: processes as `Open → Low → High → Close`.
   - [Research](https://gist.github.com/stefansimik/d387e1d9ff784a8973feca0cde51e363) shows this approach achieves ~75-85% accuracy in predicting correct High/Low sequence (compared to statistical ~50% accuracy with fixed ordering).
   - This is particularly important when both take-profit and stop-loss levels occur within the same bar - as the sequence determines which order is filled first.

Here's how to configure adaptive bar ordering for a venue, including account setup:

```python
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.model.enums import OmsType, AccountType
from nautilus_trader.model import Money, Currency

# Initialize the backtest engine
engine = BacktestEngine()

# Add a venue with adaptive bar ordering and required account settings
engine.add_venue(
    venue=venue,  # Your Venue identifier, e.g., Venue("BINANCE")
    oms_type=OmsType.NETTING,
    account_type=AccountType.CASH,
    starting_balances=[Money(10_000, Currency.from_str("USDT"))],
    bar_adaptive_high_low_ordering=True,  # Enable adaptive ordering of High/Low bar prices
)
```

### Slippage and Spread Handling

When backtesting with different types of data, Nautilus implements specific handling for slippage and spread simulation:

For L2 (market-by-price) or L3 (market-by-order) data, slippage is simulated with high accuracy by:

- Filling orders against actual order book levels.
- Matching available size at each price level sequentially.
- Maintaining realistic order book depth impact (per order fill).

For L1 data types (e.g., L1 order book, trades, quotes, bars), slippage is handled through:

**Initial fill slippage** (`prob_slippage`):

- Controlled by the `prob_slippage` parameter of the `FillModel`.
- Determines if the initial fill will occur one tick away from current market price.
- Example: With `prob_slippage=0.5`, a market BUY has 50% chance of filling one tick above the best ask price.

:::note
When backtesting with bar data, be aware that the reduced granularity of price information affects the slippage mechanism.
For the most realistic backtesting results, consider using higher granularity data sources such as L2 or L3 order book data when available.
:::

### Fill Model

The `FillModel` helps simulate order queue position and execution in a simple probabilistic way during backtesting.
It addresses a fundamental challenge: *even with perfect historical market data, we can't fully simulate how orders may have interacted with other
market participants in real-time*.

The `FillModel` simulates two key aspects of trading that exist in real markets regardless of data quality:

1. **Queue Position for Limit Orders**:
   - When multiple traders place orders at the same price level, the order's position in the queue affects if and when it gets filled.

2. **Market Impact and Competition**:
   - When taking liquidity with market orders, you compete with other traders for available liquidity, which can affect your fill price.

#### Configuration and Parameters

```python
from nautilus_trader.backtest.models import FillModel
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.backtest.engine import BacktestEngineConfig

# Create a custom fill model with your desired probabilities
fill_model = FillModel(
    prob_fill_on_limit=0.2,    # Chance a limit order fills when price matches (applied to bars/trades/quotes + L1/L2/L3 order book)
    prob_fill_on_stop=0.95,    # [DEPRECATED] Will be removed in a future version, use `prob_slippage` instead
    prob_slippage=0.5,         # Chance of 1-tick slippage (applied to bars/trades/quotes + L1 order book only)
    random_seed=None,          # Optional: Set for reproducible results
)

# Add the fill model to your engine configuration
engine = BacktestEngine(
    config=BacktestEngineConfig(
        trader_id="TESTER-001",
        fill_model=fill_model,  # Inject your custom fill model here
    )
)
```

**prob_fill_on_limit** (default: `1.0`)

- Purpose:
  - Simulates the probability of a limit order getting filled when its price level is reached in the market.
- Details:
  - Simulates your position in the order queue at a given price level.
  - Applies to all data types (e.g., L1/L2/L3 order book, quotes, trades, bars).
  - New random probability check occurs each time market price touches your order price (but does not move through it).
  - On successful probability check, fills entire remaining order quantity.

**Examples**:

- With `prob_fill_on_limit=0.0`:
  - Limit BUY orders never fill when best ask reaches the limit price.
  - Limit SELL orders never fill when best bid reaches the limit price.
  - This simulates being at the very back of the queue and never reaching the front.
- With `prob_fill_on_limit=0.5`:
  - Limit BUY orders have 50% chance of filling when best ask reaches the limit price.
  - Limit SELL orders have 50% chance of filling when best bid reaches the limit price.
  - This simulates being in the middle of the queue.
- With `prob_fill_on_limit=1.0` (default):
  - Limit BUY orders always fill when best ask reaches the limit price.
  - Limit SELL orders always fill when best bid reaches the limit price.
  - This simulates being at the front of the queue with guaranteed fills.

**prob_slippage** (default: `0.0`)

- Purpose:
  - Simulates the probability of experiencing price slippage when executing market orders.
- Details:
  - Only applies to L1 data types (e.g., quotes, trades, bars).
  - When triggered, moves fill price one tick against your order direction.
  - Affects all market-type orders (`MARKET`, `MARKET_TO_LIMIT`, `MARKET_IF_TOUCHED`, `STOP_MARKET`).
  - Not utilized with L2/L3 data where order book depth can determine slippage.

**Examples**:

- With `prob_slippage=0.0` (default):
  - No artificial slippage is applied, representing an idealized scenario where you always get filled at the current market price.
- With `prob_slippage=0.5`:
  - Market BUY orders have 50% chance of filling one tick above the best ask price, and 50% chance at the best ask price.
  - Market SELL orders have 50% chance of filling one tick below the best bid price, and 50% chance at the best bid price.
- With `prob_slippage=1.0`:
  - Market BUY orders always fill one tick above the best ask price.
  - Market SELL orders always fill one tick below the best bid price.
  - This simulates consistent adverse price movement against your orders.

**prob_fill_on_stop** (default: `1.0`)

- Stop order is just shorter name for stop-market order, that convert to market orders when market-price touches the stop-price.
- That means, stop order order-fill mechanics is simply market-order mechanics, that is controlled by the `prob_slippage` parameter.

:::warning
The `prob_fill_on_stop` parameter is deprecated and will be removed in a future version (use `prob_slippage` instead).
:::

#### How Simulation Varies by Data Type

The behavior of the `FillModel` adapts based on the order book type being used:

**L2/L3 Orderbook data**

With full order book depth, the `FillModel` focuses purely on simulating queue position for limit orders through `prob_fill_on_limit`.
The order book itself handles slippage naturally based on available liquidity at each price level.

- `prob_fill_on_limit` is active - simulates queue position.
- `prob_slippage` is not used - real order book depth determines price impact.

**L1 Orderbook data**

With only best bid/ask prices available, the `FillModel` provides additional simulation:

- `prob_fill_on_limit` is active - simulates queue position.
- `prob_slippage` is active - simulates basic price impact since we lack real depth information.

**Bar/Quote/Trade data**

When using less granular data, the same behaviors apply as L1:

- `prob_fill_on_limit` is active - simulates queue position.
- `prob_slippage` is active - simulates basic price impact.

#### Important Considerations

The `FillModel` has certain limitations to keep in mind:

- **Partial fills are supported** with L2/L3 order book data - when there is no longer any size available in the order book, no more fills will be generated and the order will remain in a partially filled state. This accurately simulates real market conditions where not enough liquidity is available at the desired price levels.
- With L1 data, slippage is limited to a fixed 1-tick, at which entire order's quantity is filled.

:::note
As the `FillModel` continues to evolve, future versions may introduce more sophisticated simulation of order execution dynamics, including:

- Partial fill simulation
- Variable slippage based on order size
- More complex queue position modeling

:::

## Account Types

When you attach a venue to the engine—either for live trading or a back‑test—you must pick one of three accounting modes by passing the `account_type` parameter:

| Account type           | Typical use-case                                         | What the engine locks                                                                                              |
| ---------------------- | -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------|
| Cash                   | Spot trading (e.g. BTC/USDT, stocks)                     | Notional value for every position a pending order would open.                                                      |
| Margin                 | Derivatives or any product that allows leverage          | Initial margin for each order plus maintenance margin for open positions.                                          |
| Betting                | Sports betting, book‑making                              | Stake required by the venue; no leverage.                                                                          |

Example of adding a `CASH` account for a backtest venue:

```python
from nautilus_trader.adapters.binance import BINANCE_VENUE
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.model.currencies import USDT
from nautilus_trader.model.enums import OmsType, AccountType
from nautilus_trader.model import Money, Currency

# Initialize the backtest engine
engine = BacktestEngine()

# Add a CASH account for the venue
engine.add_venue(
    venue=BINANCE_VENUE,  # Create or reference a Venue identifier
    oms_type=OmsType.NETTING,
    account_type=AccountType.CASH,
    starting_balances=[Money(10_000, USDT)],
)
```

### Cash Accounts

Cash accounts settle trades in full; there is no leverage and therefore no concept of margin.

### Margin Accounts

A *margin account* facilitates trading of instruments requiring margin, such as futures or leveraged products.
It tracks account balances, calculates required margins, and manages leverage to ensure sufficient collateral for positions and orders.

**Key Concepts**:

- **Leverage**: Amplifies trading exposure relative to account equity. Higher leverage increases potential returns and risks.
- **Initial Margin**: Collateral required to submit an order to open a position.
- **Maintenance Margin**: Minimum collateral required to maintain an open position.
- **Locked Balance**: Funds reserved as collateral, unavailable for new orders or withdrawals.

:::note
Reduce-only orders **do not** contribute to `balance_locked` in cash accounts,
nor do they add to initial margin in margin accounts—as they can only reduce existing exposure.
:::

### Betting Accounts

Betting accounts are specialised for venues where you stake an amount to win or lose a fixed payout (some prediction markets, sports books, etc.).
The engine locks only the stake required by the venue; leverage and margin are not applicable.


---

file path: ./concepts/index.md
# Concepts

Concept guides introduce and explain the foundational ideas, components, and best practices that underpin the NautilusTrader platform.
These guides are designed to provide both conceptual and practical insights, helping you navigate the system's architecture, strategies, data management, execution flow, and more.
Explore the following guides to deepen your understanding and make the most of NautilusTrader.

## [Overview](overview.md)

The **Overview** guide covers the main features and intended use cases for the platform.

## [Architecture](architecture.md)

The **Architecture** guide dives deep into the foundational principles, structures, and designs that underpin
the platform. It is ideal for developers, system architects, or anyone curious about the inner workings of NautilusTrader.

## [Actors](actors.md)

The `Actor` serves as the foundational component for interacting with the trading system.
The **Actors** guide covers capabilities and implementation specifics.

## [Strategies](strategies.md)

The `Strategy` is at the heart of the NautilusTrader user experience when writing and working with
trading strategies. The **Strategies** guide covers how to implement strategies for the platform.

## [Instruments](instruments.md)

The **Instruments** guide covers the different instrument definition specifications for tradable assets and contracts.

## [Data](data.md)

The NautilusTrader platform defines a range of built-in data types crafted specifically to represent
a trading domain. The **Data** guide covers working with both built-in and custom data.

## [Execution](execution.md)

NautilusTrader can handle trade execution and order management for multiple strategies and venues
simultaneously (per instance). The **Execution** guide covers components involved in execution, as
well as the flow of execution messages (commands and events).

## [Orders](orders.md)

The **Orders** guide provides more details about the available order types for the platform, along with
the execution instructions supported for each. Advanced order types and emulated orders are also covered.

## [Cache](cache.md)

The `Cache` is a central in-memory data store for managing all trading-related data.
The **Cache** guide covers capabilities and best practices of the cache.

## [Message Bus](message_bus.md)

The `MessageBus` is the core communication system enabling decoupled messaging patterns between components,
including point-to-point, publish/subscribe, and request/response.
The **Message Bus** guide covers capabilities and best practices of the `MessageBus`.

## [Portfolio](portfolio.md)

The `Portfolio` serves as the central hub for managing and tracking all positions across active strategies for the trading node or backtest.
It consolidates position data from multiple instruments, providing a unified view of your holdings, risk exposure, and overall performance.
Explore this section to understand how NautilusTrader aggregates and updates portfolio state to support effective trading and risk management.

## [Logging](logging.md)

The platform provides logging for both backtesting and live trading using a high-performance logger implemented in Rust.

## [Backtesting](backtesting.md)

Backtesting with NautilusTrader is a methodical simulation process that replicates trading
activities using a specific system implementation.

## [Live Trading](live.md)

Live trading in NautilusTrader enables traders to deploy their backtested strategies in real-time
without any code changes. This seamless transition ensures consistency and reliability, though there
are key differences between backtesting and live trading.

## [Adapters](adapters.md)

The NautilusTrader design allows for integrating data providers and/or trading venues through adapter implementations.
The **Adapters** guide covers requirements and best practices for developing new integration adapters for the platform.

:::note
The [API Reference](../api_reference/index.md) documentation should be considered the source of truth
for the platform. If there are any discrepancies between concepts described here and the API Reference,
then the API Reference should be considered the correct information. We are working to ensure that
concepts stay up-to-date with the API Reference and will be introducing doc tests in the near future
to help with this.
:::


---

file path: ./concepts/live.md
# Live Trading

Live trading in NautilusTrader enables traders to deploy their backtested strategies in a real-time
trading environment with no code changes. This seamless transition from backtesting to live trading
is a core feature of the platform, ensuring consistency and reliability. However, there are
key differences to be aware of between backtesting and live trading.

This guide provides an overview of the key aspects of live trading.

## Configuration

When operating a live trading system, configuring your execution engine and strategies properly is
essential for ensuring reliability, accuracy, and performance. The following is an overview of the
key concepts and settings involved for live configuration.

### TradingNodeConfig

The main configuration class for live trading systems is `TradingNodeConfig`,
which inherits from `NautilusKernelConfig` and provides live-specific config options:

```python
from nautilus_trader.config import TradingNodeConfig

config = TradingNodeConfig(
    trader_id="MyTrader-001",

    # Component configurations
    cache: CacheConfig(),
    message_bus: MessageBusConfig(),
    data_engine=LiveDataEngineConfig(),
    risk_engine=LiveRiskEngineConfig(),
    exec_engine=LiveExecEngineConfig(),
    portfolio=PortfolioConfig(),

    # Client configurations
    data_clients={
        "BINANCE": BinanceDataClientConfig(),
    },
    exec_clients={
        "BINANCE": BinanceExecClientConfig(),
    },
)
```

#### Core TradingNodeConfig Parameters

| Setting                  | Default            | Description                                        |
|--------------------------|--------------------|----------------------------------------------------|
| `trader_id`              | "TRADER-001"       | Unique trader identifier (name-tag format).        |
| `instance_id`            | `None`             | Optional unique instance identifier.               |
| `timeout_connection`     | 30.0               | Connection timeout in seconds.                     |
| `timeout_reconciliation` | 10.0               | Reconciliation timeout in seconds.                 |
| `timeout_portfolio`      | 10.0               | Portfolio initialization timeout.                  |
| `timeout_disconnection`  | 10.0               | Disconnection timeout.                             |
| `timeout_post_stop`      | 5.0                | Post-stop cleanup timeout.                         |

#### Cache Database Configuration

Configure data persistence with a backing database:

```python
from nautilus_trader.config import CacheConfig
from nautilus_trader.config import DatabaseConfig

cache_config = CacheConfig(
    database=DatabaseConfig(
        host="localhost",
        port=6379,
        username="nautilus",
        password="pass",
        timeout=2.0,
    ),
    encoding="msgpack",  # or "json"
    timestamps_as_iso8601=True,
    buffer_interval_ms=100,
    flush_on_start=False,
)
```

#### Message Bus Configuration

Configure message routing and external streaming:

```python
from nautilus_trader.config import MessageBusConfig
from nautilus_trader.config import DatabaseConfig

message_bus_config = MessageBusConfig(
    database=DatabaseConfig(timeout=2),
    timestamps_as_iso8601=True,
    use_instance_id=False,
    types_filter=[QuoteTick, TradeTick],  # Filter specific message types
    stream_per_topic=False,
    autotrim_mins=30,  # Automatic message trimming
    heartbeat_interval_secs=1,
)
```

### Multi-venue Configuration

Live trading systems often connect to multiple venues or market types. Here's an example of configuring both spot and futures markets for Binance:

```python
config = TradingNodeConfig(
    trader_id="MultiVenue-001",

    # Multiple data clients for different market types
    data_clients={
        "BINANCE_SPOT": BinanceDataClientConfig(
            account_type=BinanceAccountType.SPOT,
            testnet=False,
        ),
        "BINANCE_FUTURES": BinanceDataClientConfig(
            account_type=BinanceAccountType.USDT_FUTURE,
            testnet=False,
        ),
    },

    # Corresponding execution clients
    exec_clients={
        "BINANCE_SPOT": BinanceExecClientConfig(
            account_type=BinanceAccountType.SPOT,
            testnet=False,
        ),
        "BINANCE_FUTURES": BinanceExecClientConfig(
            account_type=BinanceAccountType.USDT_FUTURE,
            testnet=False,
        ),
    },
)
```

### Execution Engine configuration

The `LiveExecEngineConfig` sets up the live execution engine, managing order processing, execution events, and reconciliation with trading venues.
The following outlines the main configuration options.

By configuring these parameters thoughtfully, you can ensure that your trading system operates efficiently,
handles orders correctly, and remains resilient in the face of potential issues, such as lost events or conflicting data/information.

:::info
See also the `LiveExecEngineConfig` [API Reference](../api_reference/config#class-liveexecengineconfig) for further details.
:::

#### Reconciliation

**Purpose**: Ensures that the system state remains consistent with the trading venue by recovering any missed events, such as order and position status updates.

| Setting                        | Default | Description                                                                                       |
|--------------------------------|---------|---------------------------------------------------------------------------------------------------|
| `reconciliation`               | True    | Activates reconciliation at startup, aligning the system's internal state with the venue's state. |
| `reconciliation_lookback_mins` | None    | Specifies how far back (in minutes) the system requests past events to reconcile uncached state.  |

:::info
See also [Execution reconciliation](../concepts/execution#execution-reconciliation) for further details.
:::

#### Order filtering

**Purpose**: Manages which order events and reports should be processed by the system to avoid conflicts with other trading nodes and unnecessary data handling.

| Setting                            | Default | Description                                                                                                |
|------------------------------------|---------|------------------------------------------------------------------------------------------------------------|
| `filter_unclaimed_external_orders` | False   | Filters out unclaimed external orders to prevent irrelevant orders from impacting the strategy.            |
| `filter_position_reports`          | False   | Filters out position status reports, useful when multiple nodes trade the same account to avoid conflicts. |

#### In-flight order checks

**Purpose**: Regularly checks the status of in-flight orders (orders that have been submitted, modified or canceled but not yet confirmed) to ensure they are processed correctly and promptly.

| Setting                       | Default   | Description                                                                                                                         |
|-------------------------------|-----------|-------------------------------------------------------------------------------------------------------------------------------------|
| `inflight_check_interval_ms`  | 2,000 ms  | Determines how frequently the system checks in-flight order status.                                                                 |
| `inflight_check_threshold_ms` | 5,000 ms  | Sets the time threshold after which an in-flight order triggers a venue status check. Adjust if colocated to avoid race conditions. |
| `inflight_check_retries`      | 5 retries | Specifies the number of retry attempts the engine will make to verify the status of an in-flight order with the venue, should the initial attempt fail. |

#### Additional execution engine options

The following additional options provide further control over execution behavior:

| Setting                            | Default | Description                                                                                                |
|------------------------------------|---------|------------------------------------------------------------------------------------------------------------|
| `generate_missing_orders`          | True    | If `MARKET` order events will be generated during reconciliation to align position discrepancies.          |
| `snapshot_orders`                  | False   | If order snapshots should be taken on order events.                                                        |
| `snapshot_positions`               | False   | If position snapshots should be taken on position events.                                                  |
| `snapshot_positions_interval_secs` | None    | The interval (seconds) between position snapshots when enabled.                                            |
| `debug`                            | False   | Enable debug mode for additional execution logging.                                                        |

If an in-flight order’s status cannot be reconciled after exhausting all retries, the system resolves it by generating one of these events based on its status:

- `SUBMITTED` -> `REJECTED`: Assumes the submission failed if no confirmation is received.
- `PENDING_UPDATE` -> `CANCELED`: Treats a pending modification as canceled if unresolved.
- `PENDING_CANCEL` -> `CANCELED`: Assumes cancellation if the venue doesn’t respond.

This ensures the trading node maintains a consistent execution state even under unreliable conditions.

#### Open order checks

**Purpose**: Regularly verifies the status of open orders matches the venue, triggering reconciliation if discrepancies are found.

| Setting                    | Default | Description                                                                                                                          |
|----------------------------|---------|--------------------------------------------------------------------------------------------------------------------------------------|
| `open_check_interval_secs` | None    | Determines how frequently (in seconds) open orders are checked at the venue. Recommended: 5-10 seconds, considering API rate limits. |
| `open_check_open_only`     | True    | When enabled, only open orders are requested during checks; if disabled, full order history is fetched (resource-intensive).         |

#### Order book audit

**Purpose**: Ensures that the internal representation of *own order* books matches the venues public order books.

| Setting                         | Default | Description                                                                                                                                         |
|---------------------------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| `own_books_audit_interval_secs` | None    | Sets the interval (in seconds) between audits of own order books against public ones. Verifies synchronization and logs errors for inconsistencies. |

#### Memory management

**Purpose**: Periodically purges closed orders, closed positions, and account events from the in-memory cache to optimize resource usage and performance during extended / HFT operations.

| Setting                                | Default | Description                                                                                                                             |
|----------------------------------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------|
| `purge_closed_orders_interval_mins`    | None    | Sets how frequently (in minutes) closed orders are purged from memory. Recommended: 10-15 minutes. Does not affect database records. |
| `purge_closed_orders_buffer_mins`      | None    | Specifies how long (in minutes) an order must have been closed before purging. Recommended: 60 minutes to ensure processes complete. |
| `purge_closed_positions_interval_mins` | None    | Sets how frequently (in minutes) closed positions are purged from memory. Recommended: 10-15 minutes. Does not affect database records. |
| `purge_closed_positions_buffer_mins`   | None    | Specifies how long (in minutes) a position must have been closed before purging. Recommended: 60 minutes to ensure processes complete. |
| `purge_account_events_interval_mins`   | None    | Sets how frequently (in minutes) account events are purged from memory. Recommended: 10-15 minutes. Does not affect database records. |
| `purge_account_events_lookback_mins`   | None    | Specifies how long (in minutes) an account event must have occurred before purging. Recommended: 60 minutes. |

By configuring these memory management settings appropriately, you can prevent memory usage from growing
indefinitely during long-running / HFT sessions while ensuring that recently closed orders, closed positions, and account events
remain available in memory for any ongoing operations that might require them.

#### Queue management

**Purpose**: Handles the internal buffering of order events to ensure smooth processing and to prevent system resource overloads.

| Setting | Default  | Description                                                                                          |
|---------|----------|------------------------------------------------------------------------------------------------------|
| `qsize` | 100,000  | Sets the size of internal queue buffers, managing the flow of data within the engine.                |

### Strategy configuration

The `StrategyConfig` class outlines the configuration for trading strategies, ensuring that each strategy operates with the correct parameters and manages orders effectively.
The following outlines the main configuration options.

:::info
See also the `StrategyConfig` [API Reference](../api_reference/config#class-strategyconfig) for further details.
:::

#### Strategy identification

**Purpose**: Provides unique identifiers for each strategy to prevent conflicts and ensure proper tracking of orders.

| Setting                     | Default | Description                                                                                            |
|-----------------------------|---------|--------------------------------------------------------------------------------------------------------|
| `strategy_id`               | None    | A unique ID for the strategy, ensuring it can be distinctly identified.                                |
| `order_id_tag`              | None    | A unique tag for the strategy's orders, differentiating them from multiple strategies.                 |
| `use_uuid_client_order_ids` | False   | If UUID4's should be used for client order ID values (required for some venues such as Coinbase Intx). |

#### Order Management System (OMS) type

**Purpose**: Defines how the order management system handles position IDs, influencing how orders are processed and tracked.

| Setting    | Default | Description                                                                                                                  |
|------------|---------|------------------------------------------------------------------------------------------------------------------------------|
| `oms_type` | None    | Specifies the [OMS type](../concepts/execution#oms-configuration), for position ID handling and order processing flow. |

#### External order claims

**Purpose**: Enables the strategy to claim external orders based on specified instrument IDs, ensuring that relevant external orders are associated with the correct strategy.

| Setting                 | Default | Description                                                                                           |
|-------------------------|---------|-------------------------------------------------------------------------------------------------------|
| `external_order_claims` | None    | Lists instrument IDs for external orders the strategy should claim, aiding accurate order management. |

#### Contingent order management

**Purpose**: Automates the management of contingent orders, such as One-Updates-the-Other (OUO) and One-Cancels-the-Other (OCO) orders, ensuring they are handled correctly.

| Setting                    | Default | Description                                                                                          |
|----------------------------|---------|------------------------------------------------------------------------------------------------------|
| `manage_contingent_orders` | False   | If enabled, the strategy automatically manages contingent orders, reducing manual intervention.      |

#### Good Till Date (GTD) expiry management

**Purpose**: Ensures that orders with GTD time in force instructions are managed properly, with timers reactivated as necessary.

| Setting              | Default | Description                                                                                          |
|----------------------|---------|------------------------------------------------------------------------------------------------------|
| `manage_gtd_expiry`  | False   | If enabled, the strategy manages GTD expirations, ensuring orders remain active as intended.         |

## Execution reconciliation

Execution reconciliation is the process of aligning the external state of reality for orders and positions
(both closed and open) with the current system internal state built from events.
This process is primarily applicable to live trading, which is why only the `LiveExecutionEngine` has reconciliation capability.

There are two main scenarios for reconciliation:

- **Previous cached execution state**: Where cached execution state exists, information from reports is used to generate missing events to align the state
- **No previous cached execution state**: Where there is no cached state, all orders and positions that exist externally are generated from scratch

### Common reconciliation issues

- **Missing trade reports**: Some venues filter out older trades, causing incomplete reconciliation. Increase `reconciliation_lookback_mins` or ensure all events are cached locally.
- **Position mismatches**: If external orders predate the lookback window, positions may not align. Flatten the account before restarting the system to reset state.

:::tip
**Best practice**: Persist all execution events to the cache database to minimize reliance on venue history, ensuring full recovery even with short lookback windows.
:::

### Reconciliation configuration

Unless reconciliation is disabled by setting the `reconciliation` configuration parameter to false,
the execution engine will perform the execution reconciliation procedure for each venue.
Additionally, you can specify the lookback window for reconciliation by setting the `reconciliation_lookback_mins` configuration parameter.

:::tip
We recommend not setting a specific `reconciliation_lookback_mins`. This allows the requests made
to the venues to utilize the maximum execution history available for reconciliation.
:::

:::warning
If executions have occurred prior to the lookback window, any necessary events will be generated to align
internal and external states. This may result in some information loss that could have been avoided with a longer lookback window.

Additionally, some venues may filter or drop execution information under certain conditions, resulting
in further information loss. This would not occur if all events were persisted in the cache database.
:::

Each strategy can also be configured to claim any external orders for an instrument ID generated during
reconciliation using the `external_order_claims` configuration parameter.
This is useful in situations where, at system start, there is no cached state or it is desirable for
a strategy to resume its operations and continue managing existing open orders at the venue for an instrument.

:::info
See the `LiveExecEngineConfig` [API Reference](../api_reference/config#class-liveexecengineconfig) for further details.
:::

### Reconciliation procedure

The reconciliation procedure is standardized for all adapter execution clients and uses the following
methods to produce an execution mass status:

- `generate_order_status_reports`
- `generate_fill_reports`
- `generate_position_status_reports`

The system state is then reconciled with the reports, which represent external "reality":

- **Duplicate Check**:
  - Check for duplicate order IDs and trade IDs.
- **Order Reconciliation**:
  - Generate and apply events necessary to update orders from any cached state to the current state.
  - If any trade reports are missing, inferred `OrderFilled` events are generated.
  - If any client order ID is not recognized or an order report lacks a client order ID, external order events are generated.
- **Position Reconciliation**:
  - Ensure the net position per instrument matches the position reports returned from the venue.
  - If the position state resulting from order reconciliation does not match the external state, external order events will be generated to resolve discrepancies.

If reconciliation fails, the system will not continue to start, and an error will be logged.

:::tip
The current reconciliation procedure can experience state mismatches if the lookback window is
misconfigured or if the venue omits certain order or trade reports due to filter conditions.

If you encounter reconciliation issues, drop any cached state or ensure the account is flat at
system shutdown and startup.
:::


---

file path: ./concepts/instruments.md
# Instruments

The `Instrument` base class represents the core specification for any tradable asset/contract. There are
currently a number of subclasses representing a range of *asset classes* and *instrument classes* which are supported by the platform:

- `Equity` (generic Equity)
- `FuturesContract` (generic Futures Contract)
- `FuturesSpread` (generic Futures Spread)
- `OptionContract` (generic Option Contract)
- `OptionSpread` (generic Option Spread)
- `BinaryOption` (generic Binary Option instrument)
- `Cfd` (Contract for Difference instrument)
- `Commodity` (commodity instrument in a spot/cash market)
- `CurrencyPair` (represents a Fiat FX or Cryptocurrency pair in a spot/cash market)
- `CryptoOption` (Crypto Option instrument)
- `CryptoPerpetual` (Perpetual Futures Contract a.k.a. Perpetual Swap)
- `CryptoFuture` (Deliverable Futures Contract with Crypto assets as underlying, and for price quotes and settlement)
- `IndexInstrument` (generic Index instrument)
- `BettingInstrument` (Sports, gaming, or other betting)

## Symbology

All instruments should have a unique `InstrumentId`, which is made up of both the native symbol, and venue ID, separated by a period.
For example, on the Binance Futures crypto exchange, the Ethereum Perpetual Futures Contract has the instrument ID `ETHUSDT-PERP.BINANCE`.

All native symbols *should* be unique for a venue (this is not always the case e.g. Binance share native symbols between spot and futures markets),
and the `{symbol.venue}` combination *must* be unique for a Nautilus system.

:::warning
The correct instrument must be matched to a market dataset such as ticks or order book data for logically sound operation.
An incorrectly specified instrument may truncate data or otherwise produce surprising results.
:::

## Backtesting

Generic test instruments can be instantiated through the `TestInstrumentProvider`:

```python
from nautilus_trader.test_kit.providers import TestInstrumentProvider

audusd = TestInstrumentProvider.default_fx_ccy("AUD/USD")
```

Exchange specific instruments can be discovered from live exchange data using an adapters `InstrumentProvider`:

```python
from nautilus_trader.adapters.binance.spot.providers import BinanceSpotInstrumentProvider
from nautilus_trader.model import InstrumentId

provider = BinanceSpotInstrumentProvider(client=binance_http_client)
await provider.load_all_async()

btcusdt = InstrumentId.from_str("BTCUSDT.BINANCE")
instrument = provider.find(btcusdt)
```

Or flexibly defined by the user through an `Instrument` constructor, or one of its more specific subclasses:

```python
from nautilus_trader.model.instruments import Instrument

instrument = Instrument(...)  # <-- provide all necessary parameters
```

See the full instrument [API Reference](../api_reference/model/instruments.md).

## Live trading

Live integration adapters have defined `InstrumentProvider` classes which work in an automated way to cache the
latest instrument definitions for the exchange. Refer to a particular `Instrument`
object by passing the matching `InstrumentId` to data and execution related methods and classes that require one.

## Finding instruments

Since the same actor/strategy classes can be used for both backtest and live trading, you can
get instruments in exactly the same way through the central cache:

```python
from nautilus_trader.model import InstrumentId

instrument_id = InstrumentId.from_str("ETHUSDT-PERP.BINANCE")
instrument = self.cache.instrument(instrument_id)
```

It's also possible to subscribe to any changes to a particular instrument:

```python
self.subscribe_instrument(instrument_id)
```

Or subscribe to all instrument changes for an entire venue:

```python
from nautilus_trader.model import Venue

binance = Venue("BINANCE")
self.subscribe_instruments(binance)
```

When an update to the instrument(s) is received by the `DataEngine`, the object(s) will
be passed to the actors/strategies `on_instrument()` method. A user can override this method with actions
to take upon receiving an instrument update:

```python
from nautilus_trader.model.instruments import Instrument

def on_instrument(self, instrument: Instrument) -> None:
    # Take some action on an instrument update
    pass
```

## Precisions and increments

The instrument objects are a convenient way to organize the specification of an
instrument through *read-only* properties. Correct price and quantity precisions, as well as
minimum price and size increments, multipliers and standard lot sizes, are available.

:::note
Most of these limits are checked by the Nautilus `RiskEngine`, otherwise invalid
values for prices and quantities *can* result in the exchange rejecting orders.
:::

## Limits

Certain value limits are optional for instruments and can be `None`, these are exchange
dependent and can include:

- `max_quantity` (maximum quantity for a single order)
- `min_quantity` (minimum quantity for a single order)
- `max_notional` (maximum value of a single order)
- `min_notional` (minimum value of a single order)
- `max_price` (maximum valid quote or order price)
- `min_price` (minimum valid quote or order price)

:::note
Most of these limits are checked by the Nautilus `RiskEngine`, otherwise exceeding
published limits *can* result in the exchange rejecting orders.
:::

## Prices and quantities

Instrument objects also offer a convenient way to create correct prices
and quantities based on given values.

```python
instrument = self.cache.instrument(instrument_id)

price = instrument.make_price(0.90500)
quantity = instrument.make_qty(150)
```

:::tip
The above is the recommended method for creating valid prices and quantities,
such as when passing them to the order factory to create an order.
:::

## Margins and fees

Margin calculations are handled by the `MarginAccount` class. This section explains how margins work and introduces key concepts you need to know.

### When margins apply?

Each exchange (e.g., CME or Binance) operates with a specific account type that determines whether margin calculations are applicable.
When setting up an exchange venue, you'll specify one of these account types:

- `AccountType.MARGIN`: Accounts that use margin calculations, which are explained below.
- `AccountType.CASH`: Simple accounts where margin calculations do not apply.
- `AccountType.BETTING`: Accounts designed for betting, which also do not involve margin calculations.

### Vocabulary

To understand trading on margin, let’s start with some key terms:

**Notional Value**: The total contract value in the quote currency. It represents the full market value of your position. For example, with EUR/USD futures on CME (symbol 6E).

- Each contract represents 125,000 EUR (EUR is base currency, USD is quote currency).
- If the current market price is 1.1000, the notional value equals 125,000 EUR × 1.1000 (price of EUR/USD) = 137,500 USD.

**Leverage** (`leverage`): The ratio that determines how much market exposure you can control relative to your account deposit. For example, with 10× leverage, you can control 10,000 USD worth of positions with just 1,000 USD in your account.

**Initial Margin** (`margin_init`): The margin rate required to open a position. It represents the minimum amount of funds that must be available in your account to open new positions. This is only a pre-check — no funds are actually locked.

**Maintenance Margin** (`margin_maint`): The margin rate required to keep a position open. This amount is locked in your account to maintain the position. It is always lower than the initial margin. You can view the total blocked funds (sum of maintenance margins for open positions) using the following in your strategy:

```python
self.portfolio.balances_locked(venue)
```

**Maker/Taker Fees**: The fees charged by exchanges based on your order's interaction with the market:

- Maker Fee (`maker_fee`): A fee (typically lower) charged when you "make" liquidity by placing an order that remains on the order book. For example, a limit buy order below the current price adds liquidity, and the *maker* fee applies when it fills.
- Taker Fee (`taker_fee`): A fee (typically higher) charged when you "take" liquidity by placing an order that executes immediately. For instance, a market buy order or a limit buy above the current price removes liquidity, and the *taker* fee applies.

:::tip
Not all exchanges or instruments implement maker/taker fees. If absent, set both `maker_fee` and `taker_fee` to 0 for the `Instrument` (e.g., `FuturesContract`, `Equity`, `CurrencyPair`, `Commodity`, `Cfd`, `BinaryOption`, `BettingInstrument`).
:::

### Margin calculation formula

The `MarginAccount` class calculates margins using the following formulas:

```python
# Initial margin calculation
margin_init = (notional_value / leverage * margin_init) + (notional_value / leverage * taker_fee)

# Maintenance margin calculation
margin_maint = (notional_value / leverage * margin_maint) + (notional_value / leverage * taker_fee)
```

**Key Points**:

- Both formulas follow the same structure but use their respective margin rates (`margin_init` and `margin_maint`).
- Each formula consists of two parts:
  - **Primary margin calculation**: Based on notional value, leverage, and margin rate.
  - **Fee Adjustment**: Accounts for the maker/taker fee.

### Implementation details

For those interested in exploring the technical implementation:

- [nautilus_trader/accounting/accounts/margin.pyx](https://github.com/nautechsystems/nautilus_trader/blob/develop/nautilus_trader/accounting/accounts/margin.pyx)
- Key methods: `calculate_margin_init(self, ...)` and `calculate_margin_maint(self, ...)`

## Commissions

Trading commissions represent the fees charged by exchanges or brokers for executing trades.
While maker/taker fees are common in cryptocurrency markets, traditional exchanges like CME often
employ other fee structures, such as per-contract commissions.
NautilusTrader supports multiple commission models to accommodate diverse fee structures across different markets.

### Built-in Fee Models

The framework provides two built-in fee model implementations:

1. `MakerTakerFeeModel`: Implements the maker/taker fee structure common in cryptocurrency exchanges, where fees are
    calculated as a percentage of the trade value.
2. `FixedFeeModel`: Applies a fixed commission per trade, regardless of the trade size.

### Creating Custom Fee Models

While the built-in fee models cover common scenarios, you might encounter situations requiring specific commission structures.
NautilusTrader's flexible architecture allows you to implement custom fee models by inheriting from the base `FeeModel` class.

For example, if you're trading futures on exchanges that charge per-contract commissions (like CME), you can implement
a custom fee model. When creating custom fee models, we inherit from the `FeeModel` base class, which is implemented
in Cython for performance reasons. This Cython implementation is reflected in the parameter naming convention,
where type information is incorporated into parameter names using underscores (like `Order_order` or `Quantity_fill_qty`).

While these parameter names might look unusual to Python developers, they're a result of Cython's type system and help
maintain consistency with the framework's core components. Here's how you could create a per-contract commission model:

```python
class PerContractFeeModel(FeeModel):
    def __init__(self, commission: Money):
        super().__init__()
        self.commission = commission

    def get_commission(self, Order_order, Quantity_fill_qty, Price_fill_px, Instrument_instrument):
        total_commission = Money(self.commission * Quantity_fill_qty, self.commission.currency)
        return total_commission
```

This custom implementation calculates the total commission by multiplying a `fixed per-contract fee` by the `number
of contracts` traded. The `get_commission(...)` method receives information about the order, fill quantity, fill price
and instrument, allowing for flexible commission calculations based on these parameters.

Our new class `PerContractFeeModel` inherits class `FeeModel`, which is implemented in Cython,
so notice the Cython-style parameter names in the method signature:

- `Order_order`: The order object, with type prefix `Order_`.
- `Quantity_fill_qty`: The fill quantity, with type prefix `Quantity_`.
- `Price_fill_px`: The fill price, with type prefix `Price_`.
- `Instrument_instrument`: The instrument object, with type prefix `Instrument_`.

These parameter names follow NautilusTrader's Cython naming conventions, where the prefix indicates the expected type.
While this might seem verbose compared to typical Python naming conventions, it ensures type safety and consistency
with the framework's Cython codebase.

### Using Fee Models in Practice

To use any fee model in your trading system, whether built-in or custom, you specify it when setting up the venue.
Here's an example using the custom per-contract fee model:

```python
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.objects import Money, Currency

engine.add_venue(
    venue=venue,
    oms_type=OmsType.NETTING,
    account_type=AccountType.MARGIN,
    base_currency=USD,
    fee_model=PerContractFeeModel(Money(2.50, USD)),  # 2.50 USD per contract
    starting_balances=[Money(1_000_000, USD)],  # Starting with 1,000,000 USD balance
)
```

:::tip
When implementing custom fee models, ensure they accurately reflect the fee structure of your target exchange.
Even small discrepancies in commission calculations can significantly impact strategy performance metrics during backtesting.
:::

## Additional info

The raw instrument definition as provided by the exchange (typically from JSON serialized data) is also
included as a generic Python dictionary. This is to retain all information
which is not necessarily part of the unified Nautilus API, and is available to the user
at runtime by calling the `.info` property.

## Synthetic Instruments

The platform supports creating customized synthetic instruments, which can generate synthetic quote
and trades. These are useful for:

- Enabling `Actor` and `Strategy` components to subscribe to quote or trade feeds.
- Triggering emulated orders.
- Constructing bars from synthetic quotes or trades.

Synthetic instruments cannot be traded directly, as they are constructs that only exist locally
within the platform. They serve as analytical tools, providing useful metrics based on their component
instruments.

In the future, we plan to support order management for synthetic instruments, enabling trading of
their component instruments based on the synthetic instrument's behavior.

:::info
The venue for a synthetic instrument is always designated as `'SYNTH'`.
:::

### Formula

A synthetic instrument is composed of a combination of two or more component instruments (which
can include instruments from multiple venues), as well as a "derivation formula".
Utilizing the dynamic expression engine powered by the [evalexpr](https://github.com/ISibboI/evalexpr)
Rust crate, the platform can evaluate the formula to calculate the latest synthetic price tick
from the incoming component instrument prices.

See the `evalexpr` documentation for a full description of available features, operators and precedence.

:::tip
Before defining a new synthetic instrument, ensure that all component instruments are already defined and exist in the cache.
:::

### Subscribing

The following example demonstrates the creation of a new synthetic instrument with an actor/strategy.
This synthetic instrument will represent a simple spread between Bitcoin and
Ethereum spot prices on Binance. For this example, it is assumed that spot instruments for
`BTCUSDT.BINANCE` and `ETHUSDT.BINANCE` are already present in the cache.

```python
from nautilus_trader.model.instruments import SyntheticInstrument

btcusdt_binance_id = InstrumentId.from_str("BTCUSDT.BINANCE")
ethusdt_binance_id = InstrumentId.from_str("ETHUSDT.BINANCE")

# Define the synthetic instrument
synthetic = SyntheticInstrument(
    symbol=Symbol("BTC-ETH:BINANCE"),
    price_precision=8,
    components=[
        btcusdt_binance_id,
        ethusdt_binance_id,
    ],
    formula=f"{btcusdt_binance_id} - {ethusdt_binance_id}",
    ts_event=self.clock.timestamp_ns(),
    ts_init=self.clock.timestamp_ns(),
)

# Recommended to store the synthetic instruments ID somewhere
self._synthetic_id = synthetic.id

# Add the synthetic instrument for use by other components
self.add_synthetic(synthetic)

# Subscribe to quotes for the synthetic instrument
self.subscribe_quote_ticks(self._synthetic_id)
```

:::note
The `instrument_id` for the synthetic instrument in the above example will be structured as `{symbol}.{SYNTH}`, resulting in `'BTC-ETH:BINANCE.SYNTH'`.
:::

### Updating formulas

It's also possible to update a synthetic instrument formulas at any time. The following example
shows how to achieve this with an actor/strategy.

```
# Recover the synthetic instrument from the cache (assuming `synthetic_id` was assigned)
synthetic = self.cache.synthetic(self._synthetic_id)

# Update the formula, here is a simple example of just taking the average
new_formula = "(BTCUSDT.BINANCE + ETHUSDT.BINANCE) / 2"
synthetic.change_formula(new_formula)

# Now update the synthetic instrument
self.update_synthetic(synthetic)
```

### Trigger instrument IDs

The platform allows for emulated orders to be triggered based on synthetic instrument prices. In
the following example, we build upon the previous one to submit a new emulated order.
This order will be retained in the emulator until a trigger from synthetic quotes releases it.
It will then be submitted to Binance as a MARKET order:

```python
order = self.strategy.order_factory.limit(
    instrument_id=ETHUSDT_BINANCE.id,
    order_side=OrderSide.BUY,
    quantity=Quantity.from_str("1.5"),
    price=Price.from_str("30000.00000000"),  # <-- Synthetic instrument price
    emulation_trigger=TriggerType.DEFAULT,
    trigger_instrument_id=self._synthetic_id,  # <-- Synthetic instrument identifier
)

self.strategy.submit_order(order)
```

### Error handling

Considerable effort has been made to validate inputs, including the derivation formula for
synthetic instruments. Despite this, caution is advised as invalid or erroneous inputs may lead to
undefined behavior.

:::info
See the `SyntheticInstrument` [API reference](../../api_reference/model/instruments.md#class-syntheticinstrument-1)
for a detailed understanding of input requirements and potential exceptions.
:::


---

file path: ./concepts/message_bus.md
# Message Bus

The `MessageBus` is a fundamental part of the platform, enabling communication between system components
through message passing. This design creates a loosely coupled architecture where components can interact
without direct dependencies.

The *messaging patterns* include:

- Point-to-Point
- Publish/Subscribe
- Request/Response

Messages exchanged via the `MessageBus` fall into three categories:

- Data
- Events
- Commands

## Data and signal publishing

While the `MessageBus` is a lower-level component that users typically interact with indirectly,
`Actor` and `Strategy` classes provide convenient methods built on top of it:

```python
def publish_data(self, data_type: DataType, data: Data) -> None:
def publish_signal(self, name: str, value, ts_event: int | None = None) -> None:
```

These methods allow you to publish custom data and signals efficiently without needing to work directly with the `MessageBus` interface.

## Direct access

For advanced users or specialized use cases, direct access to the message bus is available within `Actor` and `Strategy`
classes through the `self.msgbus` reference, which provides the full message bus interface.

To publish a custom message directly, you can specify a topic as a `str` and any Python `object` as the message payload, for example:

```python

self.msgbus.publish("MyTopic", "MyMessage")
```

## Messaging styles

NautilusTrader is an **event-driven** framework where components communicate by sending and receiving messages.
Understanding the different messaging styles is crucial for building effective trading systems.

This guide explains the three primary messaging patterns available in NautilusTrader:

| **Messaging Style**                          | **Purpose**                                 | **Best For**                                          |
|:---------------------------------------------|:--------------------------------------------|:------------------------------------------------------|
| **MessageBus - Publish/Subscribe to topics** | Low-level, direct access to the message bus | Custom events, system-level communication             |
| **Actor-Based - Publish/Subscribe Data**     | Structured trading data exchange            | Trading metrics, indicators, data needing persistence |
| **Actor-Based - Publish/Subscribe Signal**   | Lightweight notifications                   | Simple alerts, flags, status updates                  |

Each approach serves different purposes and offers unique advantages. This guide will help you decide which messaging
pattern to use in your NautilusTrader applications.

### MessageBus publish/subscribe to topics

#### Concept

The `MessageBus` is the central hub for all messages in NautilusTrader. It enables a **publish/subscribe** pattern
where components can publish events to **named topics**, and other components can subscribe to receive those messages.
This decouples components, allowing them to interact indirectly via the message bus.

#### Key benefits and use cases

The message bus approach is ideal when you need:

- **Cross-component communication** within the system.
- **Flexibility** to define any topic and send any type of payload (any Python object).
- **Decoupling** between publishers and subscribers who don't need to know about each other.
- **Global Reach** where messages can be received by multiple subscribers.
- Working with events that don't fit within the predefined `Actor` model.
- Advanced scenarios requiring full control over messaging.

#### Considerations

- You must track topic names manually (typos could result in missed messages).
- You must define handlers manually.

#### Quick overview code

```python
from nautilus_trader.core.message import Event

# Define a custom event
class Each10thBarEvent(Event):
    TOPIC = "each_10th_bar"  # Topic name
    def __init__(self, bar):
        self.bar = bar

# Subscribe in a component (in Strategy)
self.msgbus.subscribe(Each10thBarEvent.TOPIC, self.on_each_10th_bar)

# Publish an event (in Strategy)
event = Each10thBarEvent(bar)
self.msgbus.publish(Each10thBarEvent.TOPIC, event)

# Handler (in Strategy)
def on_each_10th_bar(self, event: Each10thBarEvent):
    self.log.info(f"Received 10th bar: {event.bar}")
```

#### Full example

[MessageBus Example](https://github.com/nautechsystems/nautilus_trader/tree/develop/examples/backtest/example_09_messaging_with_msgbus)

### Actor-based publish/subscribe data

#### Concept

This approach provides a way to exchange trading specific data between `Actor`s in the system.
(note: each `Strategy` inherits from `Actor`). It inherits from `Data`, which ensures proper timestamping
and ordering of events - crucial for correct backtest processing.

#### Key Benefits and Use Cases

The Data publish/subscribe approach excels when you need:

- **Exchange of structured trading data** like market data, indicators, custom metrics, or option greeks.
- **Proper event ordering** via built-in timestamps (`ts_event`, `ts_init`) crucial for backtest accuracy.
- **Data persistence and serialization** through the `@customdataclass` decorator, integrating seamlessly with NautilusTrader's data catalog system.
- **Standardized trading data exchange** between system components.

#### Considerations

- Requires defining a class that inherits from `Data` or uses `@customdataclass`.

#### Inheriting from `Data` vs. using `@customdataclass`

**Inheriting from `Data` class:**

- Defines abstract properties `ts_event` and `ts_init` that must be implemented by the subclass. These ensure proper data ordering in backtests based on timestamps.

**The `@customdataclass` decorator:**

- Adds `ts_event` and `ts_init` attributes if they are not already present.
- Provides serialization functions: `to_dict()`, `from_dict()`, `to_bytes()`, `to_arrow()`, etc.
- Enables data persistence and external communication.

#### Quick overview code

```python
from nautilus_trader.core.data import Data
from nautilus_trader.model.custom import customdataclass

@customdataclass
class GreeksData(Data):
    delta: float
    gamma: float

# Publish data (in Actor / Strategy)
data = GreeksData(delta=0.75, gamma=0.1, ts_event=1_630_000_000_000_000_000, ts_init=1_630_000_000_000_000_000)
self.publish_data(GreeksData, data)

# Subscribe to receiving data  (in Actor / Strategy)
self.subscribe_data(GreeksData)

# Handler (this is static callback function with fixed name)
def on_data(self, data: Data):
    if isinstance(data, GreeksData):
        self.log.info(f"Delta: {data.delta}, Gamma: {data.gamma}")
```

#### Full example

[Actor-Based Data Example](https://github.com/nautechsystems/nautilus_trader/tree/develop/examples/backtest/example_10_messaging_with_actor_data)

### Actor-based publish/subscribe signal

#### Concept

**Signals** are a lightweight way to publish and subscribe to simple notifications within the actor framework.
This is the simplest messaging approach, requiring no custom class definitions.

#### Key Benefits and Use Cases

The Signal messaging approach shines when you need:

- **Simple, lightweight notifications/alerts** like "RiskThresholdExceeded" or "TrendUp".
- **Quick, on-the-fly messaging** without defining custom classes.
- **Broadcasting alerts or flags** as primitive data (`int`, `float`, or `str`).
- **Easy API integration** with straightforward methods (`publish_signal`, `subscribe_signal`).
- **Multiple subscriber communication** where all subscribers receive signals when published.
- **Minimal setup overhead** with no class definitions required.

#### Considerations

- Each signal can contain only **single value** of type: `int`, `float`, and `str`. That means no support for complex data structures or other Python types.
- In the `on_signal` handler, you can only differentiate between signals using `signal.value`, as the signal name is not accessible in the handler.

#### Quick overview code

```python
# Define signal constants for better organization (optional but recommended)
import types
from nautilus_trader.core.datetime import unix_nanos_to_dt
from nautilus_trader.common.enums import LogColor

signals = types.SimpleNamespace()
signals.NEW_HIGHEST_PRICE = "NewHighestPriceReached"
signals.NEW_LOWEST_PRICE = "NewLowestPriceReached"

# Subscribe to signals (in Actor/Strategy)
self.subscribe_signal(signals.NEW_HIGHEST_PRICE)
self.subscribe_signal(signals.NEW_LOWEST_PRICE)

# Publish a signal (in Actor/Strategy)
self.publish_signal(
    name=signals.NEW_HIGHEST_PRICE,
    value=signals.NEW_HIGHEST_PRICE,  # value can be the same as name for simplicity
    ts_event=bar.ts_event,  # timestamp from triggering event
)

# Handler (this is static callback function with fixed name)
def on_signal(self, signal):
    # IMPORTANT: We match against signal.value, not signal.name
    match signal.value:
        case signals.NEW_HIGHEST_PRICE:
            self.log.info(
                f"New highest price was reached. | "
                f"Signal value: {signal.value} | "
                f"Signal time: {unix_nanos_to_dt(signal.ts_event)}",
                color=LogColor.GREEN
            )
        case signals.NEW_LOWEST_PRICE:
            self.log.info(
                f"New lowest price was reached. | "
                f"Signal value: {signal.value} | "
                f"Signal time: {unix_nanos_to_dt(signal.ts_event)}",
                color=LogColor.RED
            )
```

#### Full example

[Actor-Based Signal Example](https://github.com/nautechsystems/nautilus_trader/tree/develop/examples/backtest/example_11_messaging_with_actor_signals)

### Summary and decision guide

Here's a quick reference to help you decide which messaging style to use:

#### Decision guide: Which style to choose?

| **Use Case**                                | **Recommended Approach**                                                        | **Setup required** |
|:--------------------------------------------|:--------------------------------------------------------------------------------|:-------------------|
| Custom events or system-level communication | `MessageBus` + Pub/Sub to topic                                                 | Topic + Handler management |
| Structured trading data                     | `Actor` + Pub/Sub Data + optional `@customdataclass` if serialization is needed | New class definition inheriting from `Data` (handler `on_data` is predefined) |
| Simple alerts/notifications                 | `Actor` + Pub/Sub Signal                                                        | Just signal name |

## External publishing

The `MessageBus` can be *backed* with any database or message broker technology which has an
integration written for it, this then enables external publishing of messages.

:::info
Redis is currently supported for all serializable messages which are published externally.
The minimum supported Redis version is 6.2 (required for [streams](https://redis.io/docs/latest/develop/data-types/streams/) functionality).
:::

Under the hood, when a backing database (or any other compatible technology) is configured,
all outgoing messages are first serialized, then transmitted via a Multiple-Producer Single-Consumer (MPSC) channel to a separate thread (implemented in Rust).
In this separate thread, the message is written to its final destination, which is presently Redis streams.

This design is primarily driven by performance considerations. By offloading the I/O operations to a separate thread,
we ensure that the main thread remains unblocked and can continue its tasks without being hindered by the potentially
time-consuming operations involved in interacting with a database or client.

### Serialization

Nautilus supports serialization for:

- All Nautilus built-in types (serialized as dictionaries `dict[str, Any]` containing serializable primitives).
- Python primitive types (`str`, `int`, `float`, `bool`, `bytes`).

You can add serialization support for custom types by registering them through the `serialization` subpackage.

```python
def register_serializable_type(
    cls,
    to_dict: Callable[[Any], dict[str, Any]],
    from_dict: Callable[[dict[str, Any]], Any],
):
    ...
```

- `cls`: The type to register.
- `to_dict`: The delegate to instantiate a dict of primitive types from the object.
- `from_dict`: The delegate to instantiate the object from a dict of primitive types.

## Configuration

The message bus external backing technology can be configured by importing the `MessageBusConfig` object and passing this to
your `TradingNodeConfig`. Each of these config options will be described below.

```python
...  # Other config omitted
message_bus=MessageBusConfig(
    database=DatabaseConfig(),
    encoding="json",
    timestamps_as_iso8601=True,
    buffer_interval_ms=100,
    autotrim_mins=30,
    use_trader_prefix=True,
    use_trader_id=True,
    use_instance_id=False,
    streams_prefix="streams",
    types_filter=[QuoteTick, TradeTick],
)
...
```

### Database config

A `DatabaseConfig` must be provided, for a default Redis setup on the local
loopback you can pass a `DatabaseConfig()`, which will use defaults to match.

### Encoding

Two encodings are currently supported by the built-in `Serializer` used by the `MessageBus`:

- JSON (`json`)
- MessagePack (`msgpack`)

Use the `encoding` config option to control the message writing encoding.

:::tip
The `msgpack` encoding is used by default as it offers the most optimal serialization and memory performance.
We recommend using `json` encoding for human readability when performance is not a primary concern.
:::

### Timestamp formatting

By default timestamps are formatted as UNIX epoch nanosecond integers. Alternatively you can
configure ISO 8601 string formatting by setting the `timestamps_as_iso8601` to `True`.

### Message stream keys

Message stream keys are essential for identifying individual trader nodes and organizing messages within streams.
They can be tailored to meet your specific requirements and use cases. In the context of message bus streams, a trader key is typically structured as follows:

```
trader:{trader_id}:{instance_id}:{streams_prefix}
```

The following options are available for configuring message stream keys:

#### Trader prefix

If the key should begin with the `trader` string.

#### Trader ID

If the key should include the trader ID for the node.

#### Instance ID

Each trader node is assigned a unique 'instance ID,' which is a UUIDv4. This instance ID helps distinguish individual traders when messages
are distributed across multiple streams. You can include the instance ID in the trader key by setting the `use_instance_id` configuration option to `True`.
This is particularly useful when you need to track and identify traders across various streams in a multi-node trading system.

#### Streams prefix

The `streams_prefix` string enables you to group all streams for a single trader instance or organize
messages for multiple instances. Configure this by passing a string to the `streams_prefix` configuration
option, ensuring other prefixes are set to false.

#### Stream per topic

Indicates whether the producer will write a separate stream for each topic. This is particularly
useful for Redis backings, which do not support wildcard topics when listening to streams.
If set to False, all messages will be written to the same stream.

:::info
Redis does not support wildcard stream topics. For better compatibility with Redis, it is recommended to set this option to False.
:::

### Types filtering

When messages are published on the message bus, they are serialized and written to a stream if a backing
for the message bus is configured and enabled. To prevent flooding the stream with data like high-frequency
quotes, you may filter out certain types of messages from external publication.

To enable this filtering mechanism, pass a list of `type` objects to the `types_filter` parameter in the message bus configuration,
specifying which types of messages should be excluded from external publication.

```python
from nautilus_trader.config import MessageBusConfig
from nautilus_trader.data import TradeTick
from nautilus_trader.data import QuoteTick

# Create a MessageBusConfig instance with types filtering
message_bus = MessageBusConfig(
    types_filter=[QuoteTick, TradeTick]
)

```

### Stream auto-trimming

The `autotrim_mins` configuration parameter allows you to specify the lookback window in minutes for automatic stream trimming in your message streams.
Automatic stream trimming helps manage the size of your message streams by removing older messages, ensuring that the streams remain manageable in terms of storage and performance.

:::info
The current Redis implementation will maintain the `autotrim_mins` as a maximum width (plus roughly a minute, as streams are trimmed no more than once per minute).
Rather than a maximum lookback window based on the current wall clock time.
:::

## External streams

The message bus within a `TradingNode` (node) is referred to as the "internal message bus".
A producer node is one which publishes messages onto an external stream (see [external publishing](#external-publishing)).
The consumer node listens to external streams to receive and publish deserialized message payloads on its internal message bus.

```
                  ┌───────────────────────────┐
                  │                           │
                  │                           │
                  │                           │
                  │      Producer Node        │
                  │                           │
                  │                           │
                  │                           │
                  │                           │
                  │                           │
                  │                           │
                  └─────────────┬─────────────┘
                                │
                                │
┌───────────────────────────────▼──────────────────────────────┐
│                                                              │
│                            Stream                            │
│                                                              │
└─────────────┬────────────────────────────────────┬───────────┘
              │                                    │
              │                                    │
┌─────────────▼───────────┐          ┌─────────────▼───────────┐
│                         │          │                         │
│                         │          │                         │
│     Consumer Node 1     │          │     Consumer Node 2     │
│                         │          │                         │
│                         │          │                         │
│                         │          │                         │
│                         │          │                         │
│                         │          │                         │
│                         │          │                         │
│                         │          │                         │
└─────────────────────────┘          └─────────────────────────┘
```

:::tip
Set the `LiveDataEngineConfig.external_clients` with the list of `client_id`s intended to represent the external streaming clients.
The `DataEngine` will filter out subscription commands for these clients, ensuring that the external streaming provides the necessary data for any subscriptions to these clients.
:::

### Example configuration

The following example details a streaming setup where a producer node publishes Binance data externally,
and a downstream consumer node publishes these data messages onto its internal message bus.

#### Producer node

We configure the `MessageBus` of the producer node to publish to a `"binance"` stream.
The settings `use_trader_id`, `use_trader_prefix`, and `use_instance_id` are all set to `False`
to ensure a simple and predictable stream key that the consumer nodes can register for.

```python
message_bus=MessageBusConfig(
    database=DatabaseConfig(timeout=2),
    use_trader_id=False,
    use_trader_prefix=False,
    use_instance_id=False,
    streams_prefix="binance",  # <---
    stream_per_topic=False,
    autotrim_mins=30,
),
```

#### Consumer node

We configure the `MessageBus` of the consumer node to receive messages from the same `"binance"` stream.
The node will listen to the external stream keys to publish these messages onto its internal message bus.
Additionally, we declare the client ID `"BINANCE_EXT"` as an external client. This ensures that the
`DataEngine` does not attempt to send data commands to this client ID, as we expect these messages to be
published onto the internal message bus from the external stream, to which the node has subscribed to the relevant topics.

```python
data_engine=LiveDataEngineConfig(
    external_clients=[ClientId("BINANCE_EXT")],
),
message_bus=MessageBusConfig(
    database=DatabaseConfig(timeout=2),
    external_streams=["binance"],  # <---
),
```


---

file path: ./concepts/strategies.md
# Strategies

The heart of the NautilusTrader user experience is in writing and working with
trading strategies. Defining a strategy involves inheriting the `Strategy` class and
implementing the methods required by the strategy's logic.

**Key capabilities**:

- All `Actor` capabilities
- Order management

**Relationship with actors**:
The `Strategy` class inherits from `Actor`, which means strategies have access to all actor functionality
plus order management capabilities.

:::tip
We recommend reviewing the [Actors](actors.md) guide before diving into strategy development.
:::

Strategies can be added to Nautilus systems in any [environment contexts](/concepts/architecture.md#environment-contexts) and will start sending commands and receiving
events based on their logic as soon as the system starts.

Using the basic building blocks of data ingest, event handling, and order management (which we will discuss
below), it's possible to implement any type of strategy including directional, momentum, re-balancing,
pairs, market making etc.

:::info
See the `Strategy` [API Reference](../api_reference/trading.md) for a complete description
of all available methods.
:::

There are two main parts of a Nautilus trading strategy:

- The strategy implementation itself, defined by inheriting the `Strategy` class
- The *optional* strategy configuration, defined by inheriting the `StrategyConfig` class

:::tip
Once a strategy is defined, the same source code can be used for backtesting and live trading.
:::

The main capabilities of a strategy include:

- Historical data requests
- Live data feed subscriptions
- Setting time alerts or timers
- Cache access
- Portfolio access
- Creating and managing orders and positions

## Strategy implementation

Since a trading strategy is a class which inherits from `Strategy`, you must define
a constructor where you can handle initialization. Minimally the base/super class needs to be initialized:

```python
from nautilus_trader.trading.strategy import Strategy

class MyStrategy(Strategy):
    def __init__(self) -> None:
        super().__init__()  # <-- the superclass must be called to initialize the strategy
```

From here, you can implement handlers as necessary to perform actions based on state transitions
and events.

:::warning
Do not call components such as `clock` and `logger` in the `__init__` constructor (which is prior to registration).
This is because the systems clock and logging subsystem have not yet been initialized.
:::

### Handlers

Handlers are methods within the `Strategy` class which may perform actions based on different types of events or on state changes.
These methods are named with the prefix `on_*`. You can choose to implement any or all of these handler
methods depending on the specific goals and needs of your strategy.

The purpose of having multiple handlers for similar types of events is to provide flexibility in handling granularity.
This means that you can choose to respond to specific events with a dedicated handler, or use a more generic
handler to react to a range of related events (using typical switch statement logic).
The handlers are called in sequence from the most specific to the most general.

#### Stateful actions

These handlers are triggered by lifecycle state changes of the `Strategy`. It's recommended to:

- Use the `on_start` method to initialize your strategy (e.g., fetch instruments, subscribe to data)
- Use the `on_stop` method for cleanup tasks (e.g., cancel open orders, close open positions, unsubscribe from data)

```python
def on_start(self) -> None:
def on_stop(self) -> None:
def on_resume(self) -> None:
def on_reset(self) -> None:
def on_dispose(self) -> None:
def on_degrade(self) -> None:
def on_fault(self) -> None:
def on_save(self) -> dict[str, bytes]:  # Returns user-defined dictionary of state to be saved
def on_load(self, state: dict[str, bytes]) -> None:
```

#### Data handling

These handlers receive data updates, including built-in market data and custom user-defined data.
You can use these handlers to define actions upon receiving data object instances.

```python
from nautilus_trader.core import Data
from nautilus_trader.model import OrderBook
from nautilus_trader.model import Bar
from nautilus_trader.model import QuoteTick
from nautilus_trader.model import TradeTick
from nautilus_trader.model import OrderBookDeltas
from nautilus_trader.model import InstrumentClose
from nautilus_trader.model import InstrumentStatus
from nautilus_trader.model.instruments import Instrument

def on_order_book_deltas(self, deltas: OrderBookDeltas) -> None:
def on_order_book(self, order_book: OrderBook) -> None:
def on_quote_tick(self, tick: QuoteTick) -> None:
def on_trade_tick(self, tick: TradeTick) -> None:
def on_bar(self, bar: Bar) -> None:
def on_instrument(self, instrument: Instrument) -> None:
def on_instrument_status(self, data: InstrumentStatus) -> None:
def on_instrument_close(self, data: InstrumentClose) -> None:
def on_historical_data(self, data: Data) -> None:
def on_data(self, data: Data) -> None:  # Custom data passed to this handler
def on_signal(self, signal: Data) -> None:  # Custom signals passed to this handler
```

#### Order management

These handlers receive events related to orders.
`OrderEvent` type messages are passed to handlers in the following sequence:

1. Specific handler (e.g., `on_order_accepted`, `on_order_rejected`, etc.)
2. `on_order_event(...)`
3. `on_event(...)`

```python
from nautilus_trader.model.events import OrderAccepted
from nautilus_trader.model.events import OrderCanceled
from nautilus_trader.model.events import OrderCancelRejected
from nautilus_trader.model.events import OrderDenied
from nautilus_trader.model.events import OrderEmulated
from nautilus_trader.model.events import OrderEvent
from nautilus_trader.model.events import OrderExpired
from nautilus_trader.model.events import OrderFilled
from nautilus_trader.model.events import OrderInitialized
from nautilus_trader.model.events import OrderModifyRejected
from nautilus_trader.model.events import OrderPendingCancel
from nautilus_trader.model.events import OrderPendingUpdate
from nautilus_trader.model.events import OrderRejected
from nautilus_trader.model.events import OrderReleased
from nautilus_trader.model.events import OrderSubmitted
from nautilus_trader.model.events import OrderTriggered
from nautilus_trader.model.events import OrderUpdated

def on_order_initialized(self, event: OrderInitialized) -> None:
def on_order_denied(self, event: OrderDenied) -> None:
def on_order_emulated(self, event: OrderEmulated) -> None:
def on_order_released(self, event: OrderReleased) -> None:
def on_order_submitted(self, event: OrderSubmitted) -> None:
def on_order_rejected(self, event: OrderRejected) -> None:
def on_order_accepted(self, event: OrderAccepted) -> None:
def on_order_canceled(self, event: OrderCanceled) -> None:
def on_order_expired(self, event: OrderExpired) -> None:
def on_order_triggered(self, event: OrderTriggered) -> None:
def on_order_pending_update(self, event: OrderPendingUpdate) -> None:
def on_order_pending_cancel(self, event: OrderPendingCancel) -> None:
def on_order_modify_rejected(self, event: OrderModifyRejected) -> None:
def on_order_cancel_rejected(self, event: OrderCancelRejected) -> None:
def on_order_updated(self, event: OrderUpdated) -> None:
def on_order_filled(self, event: OrderFilled) -> None:
def on_order_event(self, event: OrderEvent) -> None:  # All order event messages are eventually passed to this handler
```

#### Position management

These handlers receive events related to positions.
`PositionEvent` type messages are passed to handlers in the following sequence:

1. Specific handler (e.g., `on_position_opened`, `on_position_changed`, etc.)
2. `on_position_event(...)`
3. `on_event(...)`

```python
from nautilus_trader.model.events import PositionChanged
from nautilus_trader.model.events import PositionClosed
from nautilus_trader.model.events import PositionEvent
from nautilus_trader.model.events import PositionOpened

def on_position_opened(self, event: PositionOpened) -> None:
def on_position_changed(self, event: PositionChanged) -> None:
def on_position_closed(self, event: PositionClosed) -> None:
def on_position_event(self, event: PositionEvent) -> None:  # All position event messages are eventually passed to this handler
```

#### Generic event handling

This handler will eventually receive all event messages which arrive at the strategy, including those for
which no other specific handler exists.

```python
from nautilus_trader.core.message import Event

def on_event(self, event: Event) -> None:
```

#### Handler example

The following example shows a typical `on_start` handler method implementation (taken from the example EMA cross strategy).
Here we can see the following:

- Indicators being registered to receive bar updates
- Historical data being requested (to hydrate the indicators)
- Live data being subscribed to

```python
def on_start(self) -> None:
    """
    Actions to be performed on strategy start.
    """
    self.instrument = self.cache.instrument(self.instrument_id)
    if self.instrument is None:
        self.log.error(f"Could not find instrument for {self.instrument_id}")
        self.stop()
        return

    # Register the indicators for updating
    self.register_indicator_for_bars(self.bar_type, self.fast_ema)
    self.register_indicator_for_bars(self.bar_type, self.slow_ema)

    # Get historical data
    self.request_bars(self.bar_type)

    # Subscribe to live data
    self.subscribe_bars(self.bar_type)
    self.subscribe_quote_ticks(self.instrument_id)
```

### Clock and timers

Strategies have access to a `Clock` which provides a number of methods for creating
different timestamps, as well as setting time alerts or timers to trigger `TimeEvent`s.

:::info
See the `Clock` [API reference](../api_reference/common.md) for a complete list of available methods.
:::

#### Current timestamps

While there are multiple ways to obtain current timestamps, here are two commonly used methods as examples:

To get the current UTC timestamp as a tz-aware `pd.Timestamp`:

```python
import pandas as pd


now: pd.Timestamp = self.clock.utc_now()
```

To get the current UTC timestamp as nanoseconds since the UNIX epoch:

```python
unix_nanos: int = self.clock.timestamp_ns()
```

#### Time alerts

Time alerts can be set which will result in a `TimeEvent` being dispatched to the `on_event` handler at the
specified alert time. In a live context, this might be slightly delayed by a few microseconds.

This example sets a time alert to trigger one minute from the current time:

```python
import pandas as pd

# Fire a TimeEvent one minute from now
self.clock.set_time_alert(
    name="MyTimeAlert1",
    alert_time=self.clock.utc_now() + pd.Timedelta(minutes=1),
)
```

#### Timers

Continuous timers can be set up which will generate a `TimeEvent` at regular intervals until the timer expires
or is canceled.

This example sets a timer to fire once per minute, starting immediately:

```python
import pandas as pd

# Fire a TimeEvent every minute
self.clock.set_timer(
    name="MyTimer1",
    interval=pd.Timedelta(minutes=1),
)
```

### Cache access

The trader instances central `Cache` can be accessed to fetch data and execution objects (orders, positions etc).
There are many methods available often with filtering functionality, here we go through some basic use cases.

#### Fetching data

The following example shows how data can be fetched from the cache (assuming some instrument ID attribute is assigned):

```python
last_quote = self.cache.quote_tick(self.instrument_id)
last_trade = self.cache.trade_tick(self.instrument_id)
last_bar = self.cache.bar(bar_type)
```

#### Fetching execution objects

The following example shows how individual order and position objects can be fetched from the cache:

```python
order = self.cache.order(client_order_id)
position = self.cache.position(position_id)

```

:::info
See the `Cache` [API Reference](../api_reference/cache.md) for a complete description
of all available methods.
:::

### Portfolio access

The traders central `Portfolio` can be accessed to fetch account and positional information.
The following shows a general outline of available methods.

#### Account and positional information

```python
import decimal

from nautilus_trader.accounting.accounts.base import Account
from nautilus_trader.model import Venue
from nautilus_trader.model import Currency
from nautilus_trader.model import Money
from nautilus_trader.model import InstrumentId

def account(self, venue: Venue) -> Account

def balances_locked(self, venue: Venue) -> dict[Currency, Money]
def margins_init(self, venue: Venue) -> dict[Currency, Money]
def margins_maint(self, venue: Venue) -> dict[Currency, Money]
def unrealized_pnls(self, venue: Venue) -> dict[Currency, Money]
def realized_pnls(self, venue: Venue) -> dict[Currency, Money]
def net_exposures(self, venue: Venue) -> dict[Currency, Money]

def unrealized_pnl(self, instrument_id: InstrumentId) -> Money
def realized_pnl(self, instrument_id: InstrumentId) -> Money
def net_exposure(self, instrument_id: InstrumentId) -> Money
def net_position(self, instrument_id: InstrumentId) -> decimal.Decimal

def is_net_long(self, instrument_id: InstrumentId) -> bool
def is_net_short(self, instrument_id: InstrumentId) -> bool
def is_flat(self, instrument_id: InstrumentId) -> bool
def is_completely_flat(self) -> bool
```

:::info
See the `Portfolio` [API Reference](../api_reference/portfolio.md) for a complete description
of all available methods.
:::

#### Reports and analysis

The `Portfolio` also makes a `PortfolioAnalyzer` available, which can be fed with a flexible amount of data
(to accommodate different lookback windows). The analyzer can provide tracking for and generating of performance
metrics and statistics.

:::info
See the `PortfolioAnalyzer` [API Reference](../api_reference/analysis.md) for a complete description
of all available methods.
:::

:::info
See the [Portfolio statistics](../concepts/advanced/portfolio_statistics.md) guide.
:::

### Trading commands

NautilusTrader offers a comprehensive suite of trading commands, enabling granular order management
tailored for algorithmic trading. These commands are essential for executing strategies, managing risk,
and ensuring seamless interaction with various trading venues. In the following sections, we will
delve into the specifics of each command and its use cases.

:::info
The [Execution](../concepts/execution.md) guide explains the flow through the system, and can be helpful to read in conjunction with the below.
:::

#### Submitting orders

An `OrderFactory` is provided on the base class for every `Strategy` as a convenience, reducing
the amount of boilerplate required to create different `Order` objects (although these objects
can still be initialized directly with the `Order.__init__(...)` constructor if the trader prefers).

The component a `SubmitOrder` or `SubmitOrderList` command will flow to for execution depends on the following:

- If an `emulation_trigger` is specified, the command will *firstly* be sent to the `OrderEmulator`
- If an `exec_algorithm_id` is specified (with no `emulation_trigger`), the command will *firstly* be sent to the relevant `ExecAlgorithm`
- Otherwise, the command will *firstly* be sent to the `RiskEngine`

This example submits a `LIMIT` BUY order for emulation (see [OrderEmulator](advanced/emulated_orders.md)):

```python
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import TriggerType
from nautilus_trader.model.orders import LimitOrder


def buy(self) -> None:
    """
    Users simple buy method (example).
    """
    order: LimitOrder = self.order_factory.limit(
        instrument_id=self.instrument_id,
        order_side=OrderSide.BUY,
        quantity=self.instrument.make_qty(self.trade_size),
        price=self.instrument.make_price(5000.00),
        emulation_trigger=TriggerType.LAST_PRICE,
    )

    self.submit_order(order)
```

:::info
You can specify both order emulation and an execution algorithm.
:::

This example submits a `MARKET` BUY order to a TWAP execution algorithm:

```python
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model import ExecAlgorithmId


def buy(self) -> None:
    """
    Users simple buy method (example).
    """
    order: MarketOrder = self.order_factory.market(
        instrument_id=self.instrument_id,
        order_side=OrderSide.BUY,
        quantity=self.instrument.make_qty(self.trade_size),
        time_in_force=TimeInForce.FOK,
        exec_algorithm_id=ExecAlgorithmId("TWAP"),
        exec_algorithm_params={"horizon_secs": 20, "interval_secs": 2.5},
    )

    self.submit_order(order)
```

#### Canceling orders

Orders can be canceled individually, as a batch, or all orders for an instrument (with an optional side filter).

If the order is already *closed* or already pending cancel, then a warning will be logged.

If the order is currently *open* then the status will become `PENDING_CANCEL`.

The component a `CancelOrder`, `CancelAllOrders` or `BatchCancelOrders` command will flow to for execution depends on the following:

- If the order is currently emulated, the command will *firstly* be sent to the `OrderEmulator`
- If an `exec_algorithm_id` is specified (with no `emulation_trigger`), and the order is still active within the local system, the command will *firstly* be sent to the relevant `ExecAlgorithm`
- Otherwise, the order will *firstly* be sent to the `ExecutionEngine`

:::info
Any managed GTD timer will also be canceled after the command has left the strategy.
:::

The following shows how to cancel an individual order:

```python

self.cancel_order(order)

```

The following shows how to cancel a batch of orders:

```python
from nautilus_trader.model import Order


my_order_list: list[Order] = [order1, order2, order3]
self.cancel_orders(my_order_list)

```

The following shows how to cancel all orders:

```python

self.cancel_all_orders()

```

#### Modifying orders

Orders can be modified individually when emulated, or *open* on a venue (if supported).

If the order is already *closed* or already pending cancel, then a warning will be logged.
If the order is currently *open* then the status will become `PENDING_UPDATE`.

:::warning
At least one value must differ from the original order for the command to be valid.
:::

The component a `ModifyOrder` command will flow to for execution depends on the following:

- If the order is currently emulated, the command will *firstly* be sent to the `OrderEmulator`
- Otherwise, the order will *firstly* be sent to the `RiskEngine`

:::info
Once an order is under the control of an execution algorithm, it cannot be directly modified by a strategy (only canceled).
:::

The following shows how to modify the size of `LIMIT` BUY order currently *open* on a venue:

```python
from nautilus_trader.model import Quantity


new_quantity: Quantity = Quantity.from_int(5)
self.modify_order(order, new_quantity)

```

:::info
The price and trigger price can also be modified (when emulated or supported by a venue).
:::

## Strategy configuration

The main purpose of a separate configuration class is to provide total flexibility
over where and how a trading strategy can be instantiated. This includes being able
to serialize strategies and their configurations over the wire, making distributed backtesting
and firing up remote live trading possible.

This configuration flexibility is actually opt-in, in that you can actually choose not to have
any strategy configuration beyond the parameters you choose to pass into your
strategies' constructor. If you would like to run distributed backtests or launch
live trading servers remotely, then you will need to define a configuration.

Here is an example configuration:

```python
from decimal import Decimal
from nautilus_trader.config import StrategyConfig
from nautilus_trader.model import Bar, BarType
from nautilus_trader.model import InstrumentId
from nautilus_trader.trading.strategy import Strategy


# Configuration definition
class MyStrategyConfig(StrategyConfig):
    instrument_id: InstrumentId   # example value: "ETHUSDT-PERP.BINANCE"
    bar_type: BarType             # example value: "ETHUSDT-PERP.BINANCE-15-MINUTE[LAST]-EXTERNAL"
    fast_ema_period: int = 10
    slow_ema_period: int = 20
    trade_size: Decimal
    order_id_tag: str


# Strategy definition
class MyStrategy(Strategy):
    def __init__(self, config: MyStrategyConfig) -> None:
        # Always initialize the parent Strategy class
        # After this, configuration is stored and available via `self.config`
        super().__init__(config)

        # Custom state variables
        self.time_started = None
        self.count_of_processed_bars: int = 0

    def on_start(self) -> None:
        self.time_started = self.clock.utc_now()    # Remember time, when strategy started
        self.subscribe_bars(self.config.bar_type)   # See how configuration data are exposed via `self.config`

    def on_bar(self, bar: Bar):
        self.count_of_processed_bars += 1           # Update count of processed bars


# Instantiate configuration with specific values. By setting:
#   - InstrumentId - we parameterize the instrument the strategy will trade.
#   - BarType - we parameterize bar-data, that strategy will trade.
config = MyStrategyConfig(
    instrument_id=InstrumentId.from_str("ETHUSDT-PERP.BINANCE"),
    bar_type=BarType.from_str("ETHUSDT-PERP.BINANCE-15-MINUTE[LAST]-EXTERNAL"),
    trade_size=Decimal(1),
    order_id_tag="001",
)

# Pass configuration to our trading strategy.
strategy = MyStrategy(config=config)
```

When implementing strategies, it's recommended to access configuration values directly through `self.config`.
This provides clear separation between:

- Configuration data (accessed via `self.config`):
  - Contains initial settings, that define how the strategy works
  - Example: `self.config.trade_size`, `self.config.instrument_id`

- Strategy state variables (as direct attributes):
  - Track any custom state of the strategy
  - Example: `self.time_started`, `self.count_of_processed_bars`

This separation makes code easier to understand and maintain.

:::note
Even though it often makes sense to define a strategy which will trade a single
instrument. The number of instruments a single strategy can work with is only limited by machine resources.
:::

### Managed GTD expiry

It's possible for the strategy to manage expiry for orders with a time in force of GTD (*Good 'till Date*).
This may be desirable if the exchange/broker does not support this time in force option, or for any
reason you prefer the strategy to manage this.

To use this option, pass `manage_gtd_expiry=True` to your `StrategyConfig`. When an order is submitted with
a time in force of GTD, the strategy will automatically start an internal time alert.
Once the internal GTD time alert is reached, the order will be canceled (if not already *closed*).

Some venues (such as Binance Futures) support the GTD time in force, so to avoid conflicts when using
`managed_gtd_expiry` you should set `use_gtd=False` for your execution client config.

### Multiple strategies

If you intend running multiple instances of the same strategy, with different
configurations (such as trading different instruments), then you will need to define
a unique `order_id_tag` for each of these strategies (as shown above).

:::note
The platform has built-in safety measures in the event that two strategies share a
duplicated strategy ID, then an exception will be raised that the strategy ID has already been registered.
:::

The reason for this is that the system must be able to identify which strategy
various commands and events belong to. A strategy ID is made up of the
strategy class name, and the strategies `order_id_tag` separated by a hyphen. For
example the above config would result in a strategy ID of `MyStrategy-001`.

:::note
See the `StrategyId` [API Reference](../api_reference/model/identifiers.md) for further details.
:::


---

file path: ./concepts/architecture.md
# Architecture

Welcome to the architectural overview of NautilusTrader.

This guide dives deep into the foundational principles, structures, and designs that underpin
the platform. Whether you're a developer, system architect, or just curious about the inner workings
of NautilusTrader, this section covers:

- The design philosophy that drives decisions and shapes the system's evolution.
- The overarching system architecture providing a bird's-eye view of the entire system framework.
- How the framework is organized to facilitate modularity and maintainability.
- The code structure that ensures readability and scalability.
- A breakdown of component organization and interaction to understand how different parts communicate and collaborate.
- And finally, the implementation techniques that are crucial for performance, reliability, and robustness.

:::note
Throughout the documentation, the term *"Nautilus system boundary"* refers to operations within
the runtime of a single Nautilus node (also known as a "trader instance").
:::

## Design Philosophy

The major architectural techniques and design patterns employed by NautilusTrader are:

- [Domain driven design (DDD)](https://en.wikipedia.org/wiki/Domain-driven_design)
- [Event-driven architecture](https://en.wikipedia.org/wiki/Event-driven_programming)
- [Messaging patterns](https://en.wikipedia.org/wiki/Messaging_pattern) (Pub/Sub, Req/Rep, point-to-point)
- [Ports and adapters](https://en.wikipedia.org/wiki/Hexagonal_architecture_(software))
- [Crash-only design](https://en.wikipedia.org/wiki/Crash-only_software)

These techniques have been utilized to assist in achieving certain architectural quality attributes.

### Quality Attributes

Architectural decisions are often a trade-off between competing priorities. The
below is a list of some of the most important quality attributes which are considered
when making design and architectural decisions, roughly in order of 'weighting'.

- Reliability
- Performance
- Modularity
- Testability
- Maintainability
- Deployability

## System Architecture

The NautilusTrader codebase is actually both a framework for composing trading
 systems, and a set of default system implementations which can operate in various
[environment contexts](#environment-contexts).

![Architecture](https://github.com/nautechsystems/nautilus_trader/blob/develop/assets/architecture-overview.png?raw=true "architecture")

### Core Components

The platform is built around several key components that work together to provide a comprehensive trading system:

#### NautilusKernel

The central orchestration component responsible for:

- Initializing and managing all system components.
- Configuring the messaging infrastructure.
- Maintaining environment-specific behaviors.
- Coordinating shared resources and lifecycle management.
- Providing a unified entry point for system operations.

#### MessageBus

The backbone of inter-component communication, implementing:

- **Publish/Subscribe patterns**: For broadcasting events and data to multiple consumers.
- **Request/Response communication**: For operations requiring acknowledgment.
- **Command/Event messaging**: For triggering actions and notifying state changes.
- **Optional state persistence**: Using Redis for durability and restart capabilities.

#### Cache

High-performance in-memory storage system that:

- Stores instruments, accounts, orders, positions, and more.
- Provides performant fetching capabilities for trading components.
- Maintains consist state across the system.
- Supports both read and write operations with optimized access patterns.

#### DataEngine

Processes and routes market data throughout the system:

- Handles multiple data types (quotes, trades, bars, order books, custom data, and more).
- Routes data to appropriate consumers based on subscriptions.
- Manages data flow from external sources to internal components.

#### ExecutionEngine

Manages order lifecycle and execution:

- Routes trading commands to the appropriate adapter clients.
- Tracks order and position states.
- Coordinates with risk management systems.
- Handles execution reports and fills from venues.
- Handles reconciliation of external execution state.

#### RiskEngine

Provides comprehensive risk management:

- Pre-trade risk checks and validation.
- Position and exposure monitoring.
- Real-time risk calculations.
- Configurable risk rules and limits.

### Environment Contexts

An environment context in NautilusTrader defines the type of data and trading venue you are working
with. Understanding these contexts is crucial for effective backtesting, development, and live trading.

Here are the available environments you can work with:

- `Backtest`: Historical data with simulated venues.
- `Sandbox`: Real-time data with simulated venues.
- `Live`: Real-time data with live venues (paper trading or real accounts).

### Common Core

The platform has been designed to share as much common code between backtest, sandbox and live trading systems as possible.
This is formalized in the `system` subpackage, where you will find the `NautilusKernel` class,
providing a common core system 'kernel'.

The *ports and adapters* architectural style enables modular components to be integrated into the
core system, providing various hooks for user-defined or custom component implementations.

### Data and Execution Flow Patterns

Understanding how data and execution flow through the system is crucial for effective use of the platform:

#### Data Flow Pattern

1. **External Data Ingestion**: Market data enters via venue-specific `DataClient` adapters where it is normalized.
2. **Data Processing**: The `DataEngine` handles data processing for internal components.
3. **Caching**: Processed data is stored in the high-performance `Cache` for fast access.
4. **Event Publishing**: Data events are published to the `MessageBus`.
5. **Consumer Delivery**: Subscribed components (Actors, Strategies) receive relevant data events.

#### Execution Flow Pattern

1. **Command Generation**: User strategies create trading commands.
2. **Command Publishing**: Commands are sent through the `MessageBus`.
3. **Risk Validation**: The `RiskEngine` validates trading commands against configured risk rules.
4. **Execution Routing**: The `ExecutionEngine` routes commands to appropriate venues.
5. **External Submission**: The `ExecutionClient` submits orders to external trading venues.
6. **Event Flow Back**: Order events (fills, cancellations) flow back through the system.
7. **State Updates**: Portfolio and position states are updated based on execution events.

#### Component State Management

All components follow a finite state machine pattern with well-defined states:

- **PRE_INITIALIZED**: Component is created but not yet wired up to the system.
- **READY**: Component is configured and wired up, but not yet running.
- **RUNNING**: Component is actively processing messages and performing operations.
- **STOPPED**: Component has been gracefully stopped and is no longer processing.
- **DEGRADED**: Component is running but with reduced functionality due to errors.
- **FAULTED**: Component has encountered a critical error and cannot continue.
- **DISPOSED**: Component has been cleaned up and resources have been released.

### Messaging

To facilitate modularity and loose coupling, an extremely efficient `MessageBus` passes messages (data, commands and events) between components.

From a high level architectural view, it's important to understand that the platform has been designed to run efficiently
on a single thread, for both backtesting and live trading. Much research and testing
resulted in arriving at this design, as it was found the overhead of context switching between threads
didn't actually result in improved performance.

When considering the logic of how your algo trading will work within the system boundary, you can expect each component to consume messages
in a deterministic synchronous way (*similar* to the [actor model](https://en.wikipedia.org/wiki/Actor_model)).

:::note
Of interest is the LMAX exchange architecture, which achieves award winning performance running on
a single thread. You can read about their *disruptor* pattern based architecture in [this interesting article](https://martinfowler.com/articles/lmax.html) by Martin Fowler.
:::

## Framework organization

The codebase is organized with a layering of abstraction levels, and generally
grouped into logical subpackages of cohesive concepts. You can navigate to the documentation
for each of these subpackages from the left nav menu.

### Core / low-Level

- `core`: Constants, functions and low-level components used throughout the framework.
- `common`: Common parts for assembling the frameworks various components.
- `network`: Low-level base components for networking clients.
- `serialization`: Serialization base components and serializer implementations.
- `model`: Defines a rich trading domain model.

### Components

- `accounting`: Different account types and account management machinery.
- `adapters`: Integration adapters for the platform including brokers and exchanges.
- `analysis`: Components relating to trading performance statistics and analysis.
- `cache`: Provides common caching infrastructure.
- `data`: The data stack and data tooling for the platform.
- `execution`: The execution stack for the platform.
- `indicators`: A set of efficient indicators and analyzers.
- `persistence`: Data storage, cataloging and retrieval, mainly to support backtesting.
- `portfolio`: Portfolio management functionality.
- `risk`: Risk specific components and tooling.
- `trading`: Trading domain specific components and tooling.

### System implementations

- `backtest`: Backtesting componentry as well as a backtest engine and node implementations.
- `live`: Live engine and client implementations as well as a node for live trading.
- `system`: The core system kernel common between `backtest`, `sandbox`, `live` [environment contexts](#environment-contexts).

## Code structure

The foundation of the codebase is the `crates` directory, containing a collection of core Rust crates including a C foreign function interface (FFI) generated by `cbindgen`.

The bulk of the production code resides in the `nautilus_trader` directory, which contains a collection of Python/Cython subpackages and modules.

Python bindings for the Rust core are provided by statically linking the Rust libraries to the C extension modules generated by Cython at compile time (effectively extending the CPython API).

### Dependency flow

```
┌─────────────────────────┐
│                         │
│                         │
│     nautilus_trader     │
│                         │
│     Python / Cython     │
│                         │
│                         │
└────────────┬────────────┘
 C API       │
             │
             │
             │
 C API       ▼
┌─────────────────────────┐
│                         │
│                         │
│      nautilus_core      │
│                         │
│          Rust           │
│                         │
│                         │
└─────────────────────────┘
```

:::note
Both Rust and Cython are build dependencies. The binary wheels produced from a build do not require
Rust or Cython to be installed at runtime.
:::

### Type safety

The design of the platform prioritizes software correctness and safety at the highest level.

The Rust codebase in `nautilus_core` is always type safe and memory safe as guaranteed by the `rustc` compiler,
and so is *correct by construction* (unless explicitly marked `unsafe`, see the Rust section of the [Developer Guide](../developer_guide/rust.md)).

Cython provides type safety at the C level at both compile time, and runtime:

:::info
If you pass an argument with an invalid type to a Cython implemented module with typed parameters,
then you will receive a `TypeError` at runtime.
:::

If a function or method's parameter is not explicitly typed to accept `None`, passing `None` as an
argument will result in a `ValueError` at runtime.

:::warning
The above exceptions are not explicitly documented to prevent excessive bloating of the docstrings.
:::

### Errors and exceptions

Every attempt has been made to accurately document the possible exceptions which
can be raised from NautilusTrader code, and the conditions which will trigger them.

:::warning
There may be other undocumented exceptions which can be raised by Pythons standard
library, or from third party library dependencies.
:::

### Processes and threads

:::tip
For optimal performance and to prevent potential issues related to Python's memory
model and equality, it is highly recommended to run each trader instance in a separate process.
:::


---

file path: ./concepts/orders.md
# Orders

This guide provides further details about the available order types for the platform, along with
the execution instructions supported for each.

Orders are one of the fundamental building blocks of any algorithmic trading strategy.
NautilusTrader supports a broad set of order types and execution instructions, from standard to advanced,
exposing as much of a trading venue's functionality as possible. This enables traders to define instructions
and contingencies for order execution and management, facilitating the creation of virtually any trading strategy.

## Overview

All order types are derived from two fundamentals: *Market* and *Limit* orders. In terms of liquidity, they are opposites.
*Market* orders consume liquidity by executing immediately at the best available price, whereas *Limit*
orders provide liquidity by resting in the order book at a specified price until matched.

The order types available for the platform are (using the enum values):

- `MARKET`
- `LIMIT`
- `STOP_MARKET`
- `STOP_LIMIT`
- `MARKET_TO_LIMIT`
- `MARKET_IF_TOUCHED`
- `LIMIT_IF_TOUCHED`
- `TRAILING_STOP_MARKET`
- `TRAILING_STOP_LIMIT`

:::info
NautilusTrader provides a unified API for many order types and execution instructions, but not all venues support every option.
If an order contains an instruction or option that the target venue does not support, the system **should not** submit the order;
instead, it logs an error with a clear explanatory message.
:::

### Terminology

- An order is **aggressive** if its type is `MARKET` or if it executes as a *marketable* order (i.e., takes liquidity).
- An order is **passive** if it is not marketable (i.e., provides liquidity).
- An order is **active local** if it remains within the local system boundary in one of the following three non-terminal statuses:
  - `INITIALIZED`
  - `EMULATED`
  - `RELEASED`
- An order is **in-flight** when at one of the following statuses:
  - `SUBMITTED`
  - `PENDING_UPDATE`
  - `PENDING_CANCEL`
- An order is **open** when at one of the following (non-terminal) statuses:
  - `ACCEPTED`
  - `TRIGGERED`
  - `PENDING_UPDATE`
  - `PENDING_CANCEL`
  - `PARTIALLY_FILLED`
- An order is **closed** when at one of the following (terminal) statuses:
  - `DENIED`
  - `REJECTED`
  - `CANCELED`
  - `EXPIRED`
  - `FILLED`

## Execution instructions

Certain venues allow a trader to specify conditions and restrictions on
how an order will be processed and executed. The following is a brief
summary of the different execution instructions available.

### Time in force

The order's time in force specifies how long the order will remain open or active before any
remaining quantity is canceled.

- `GTC` **(Good Till Cancel)**: The order remains active until canceled by the trader or the venue.
- `IOC` **(Immediate or Cancel / Fill and Kill)**: The order executes immediately, with any unfilled portion canceled.
- `FOK` **(Fill or Kill)**: The order executes immediately in full or not at all.
- `GTD` **(Good Till Date)**: The order remains active until a specified expiration date and time.
- `DAY` **(Good for session/day)**: The order remains active until the end of the current trading session.
- `AT_THE_OPEN` **(OPG)**: The order is only active at the open of the trading session.
- `AT_THE_CLOSE`: The order is only active at the close of the trading session.

### Expire time

This instruction is to be used in conjunction with the `GTD` time in force to specify the time
at which the order will expire and be removed from the venue's order book (or order management system).

### Post-only

An order which is marked as `post_only` will only ever participate in providing liquidity to the
limit order book, and never initiating a trade which takes liquidity as an aggressor. This option is
important for market makers, or traders seeking to restrict the order to a liquidity *maker* fee tier.

### Reduce-only

An order which is set as `reduce_only` will only ever reduce an existing position on an instrument and
never open a new position (if already flat). The exact behavior of this instruction can vary between venues.

However, the behavior in the Nautilus `SimulatedExchange` is typical of a real venue.

- Order will be canceled if the associated position is closed (becomes flat).
- Order quantity will be reduced as the associated position's size decreases.

### Display quantity

The `display_qty` specifies the portion of a *Limit* order which is displayed on the limit order book.
These are also known as iceberg orders as there is a visible portion to be displayed, with more quantity which is hidden.
Specifying a display quantity of zero is also equivalent to setting an order as `hidden`.

### Trigger type

Also known as [trigger method](https://guides.interactivebrokers.com/tws/usersguidebook/configuretws/modify_the_stop_trigger_method.htm)
which is applicable to conditional trigger orders, specifying the method of triggering the stop price.

- `DEFAULT`: The default trigger type for the venue (typically `LAST` or `BID_ASK`).
- `LAST`: The trigger price will be based on the last traded price.
- `BID_ASK`: The trigger price will be based on the `BID` for buy orders and `ASK` for sell orders.
- `DOUBLE_LAST`: The trigger price will be based on the last two consecutive `LAST` prices.
- `DOUBLE_BID_ASK`: The trigger price will be based on the last two consecutive `BID` or `ASK` prices as applicable.
- `LAST_OR_BID_ASK`: The trigger price will be based on the `LAST` or `BID`/`ASK`.
- `MID_POINT`: The trigger price will be based on the mid-point between the `BID` and `ASK`.
- `MARK`: The trigger price will be based on the venue's mark price for the instrument.
- `INDEX`: The trigger price will be based on the venue's index price for the instrument.

### Trigger offset type

Applicable to conditional trailing-stop trigger orders, specifies the method of triggering modification
of the stop price based on the offset from the *market* (bid, ask or last price as applicable).

- `DEFAULT`: The default offset type for the venue (typically `PRICE`).
- `PRICE`: The offset is based on a price difference.
- `BASIS_POINTS`: The offset is based on a price percentage difference expressed in basis points (100bp = 1%).
- `TICKS`: The offset is based on a number of ticks.
- `PRICE_TIER`: The offset is based on a venue-specific price tier.

### Contingent orders

More advanced relationships can be specified between orders.
For example, child orders can be assigned to trigger only when the parent is activated or filled, or orders can be
linked so that one cancels or reduces the quantity of another. See the [Advanced Orders](#advanced-orders) section for more details.

## Order factory

The easiest way to create new orders is by using the built-in `OrderFactory`, which is
automatically attached to every `Strategy` class. This factory will take care
of lower level details - such as ensuring the correct trader ID and strategy ID are assigned, generation
of a necessary initialization ID and timestamp, and abstracts away parameters which don't necessarily
apply to the order type being created, or are only needed to specify more advanced execution instructions.

This leaves the factory with simpler order creation methods to work with, all the
examples will leverage an `OrderFactory` from within a `Strategy` context.

:::info
See the `OrderFactory` [API Reference](../api_reference/common.md#class-orderfactory) for further details.
:::

## Order Types

The following describes the order types which are available for the platform with a code example.
Any optional parameters will be clearly marked with a comment which includes the default value.

### Market

A *Market* order is an instruction by the trader to immediately trade
the given quantity at the best price available. You can also specify several
time in force options, and indicate whether this order is only intended to reduce
a position.

In the following example we create a *Market* order on the Interactive Brokers [IdealPro](https://ibkr.info/node/1708) Forex ECN
to BUY 100,000 AUD using USD:

```python
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model import InstrumentId
from nautilus_trader.model import Quantity
from nautilus_trader.model.orders import MarketOrder

order: MarketOrder = self.order_factory.market(
    instrument_id=InstrumentId.from_str("AUD/USD.IDEALPRO"),
    order_side=OrderSide.BUY,
    quantity=Quantity.from_int(100_000),
    time_in_force=TimeInForce.IOC,  # <-- optional (default GTC)
    reduce_only=False,  # <-- optional (default False)
    tags=["ENTRY"],  # <-- optional (default None)
)
```

:::info
See the `MarketOrder` [API Reference](../api_reference/model/orders.md#class-marketorder) for further details.
:::

### Limit

A *Limit* order is placed on the limit order book at a specific price, and will only
execute at that price (or better).

In the following example we create a *Limit* order on the Binance Futures Crypto exchange to SELL 20 ETHUSDT-PERP Perpetual Futures
contracts at a limit price of 5000 USDT, as a market maker.

```python
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model import InstrumentId
from nautilus_trader.model import Price
from nautilus_trader.model import Quantity
from nautilus_trader.model.orders import LimitOrder

order: LimitOrder = self.order_factory.limit(
    instrument_id=InstrumentId.from_str("ETHUSDT-PERP.BINANCE"),
    order_side=OrderSide.SELL,
    quantity=Quantity.from_int(20),
    price=Price.from_str("5_000.00"),
    time_in_force=TimeInForce.GTC,  # <-- optional (default GTC)
    expire_time=None,  # <-- optional (default None)
    post_only=True,  # <-- optional (default False)
    reduce_only=False,  # <-- optional (default False)
    display_qty=None,  # <-- optional (default None which indicates full display)
    tags=None,  # <-- optional (default None)
)
```

:::info
See the `LimitOrder` [API Reference](../api_reference/model/orders.md#class-limitorder) for further details.
:::

### Stop-Market

A *Stop-Market* order is a conditional order which once triggered, will immediately
place a *Market* order. This order type is often used as a stop-loss to limit losses, either
as a SELL order against LONG positions, or as a BUY order against SHORT positions.

In the following example we create a *Stop-Market* order on the Binance Spot/Margin exchange
to SELL 1 BTC at a trigger price of 100,000 USDT, active until further notice:

```python
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model.enums import TriggerType
from nautilus_trader.model import InstrumentId
from nautilus_trader.model import Price
from nautilus_trader.model import Quantity
from nautilus_trader.model.orders import StopMarketOrder

order: StopMarketOrder = self.order_factory.stop_market(
    instrument_id=InstrumentId.from_str("BTCUSDT.BINANCE"),
    order_side=OrderSide.SELL,
    quantity=Quantity.from_int(1),
    trigger_price=Price.from_int(100_000),
    trigger_type=TriggerType.LAST_PRICE,  # <-- optional (default DEFAULT)
    time_in_force=TimeInForce.GTC,  # <-- optional (default GTC)
    expire_time=None,  # <-- optional (default None)
    reduce_only=False,  # <-- optional (default False)
    tags=None,  # <-- optional (default None)
)
```

:::info
See the `StopMarketOrder` [API Reference](../api_reference/model/orders.md#class-stopmarketorder) for further details.
:::

### Stop-Limit

A *Stop-Limit* order is a conditional order which once triggered will immediately place
a *Limit* order at the specified price.

In the following example we create a *Stop-Limit* order on the Currenex FX ECN to BUY 50,000 GBP at a limit price of 1.3000 USD
once the market hits the trigger price of 1.30010 USD, active until midday 6th June, 2022 (UTC):

```python
import pandas as pd
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model.enums import TriggerType
from nautilus_trader.model import InstrumentId
from nautilus_trader.model import Price
from nautilus_trader.model import Quantity
from nautilus_trader.model.orders import StopLimitOrder

order: StopLimitOrder = self.order_factory.stop_limit(
    instrument_id=InstrumentId.from_str("GBP/USD.CURRENEX"),
    order_side=OrderSide.BUY,
    quantity=Quantity.from_int(50_000),
    price=Price.from_str("1.30000"),
    trigger_price=Price.from_str("1.30010"),
    trigger_type=TriggerType.BID_ASK,  # <-- optional (default DEFAULT)
    time_in_force=TimeInForce.GTD,  # <-- optional (default GTC)
    expire_time=pd.Timestamp("2022-06-06T12:00"),
    post_only=True,  # <-- optional (default False)
    reduce_only=False,  # <-- optional (default False)
    tags=None,  # <-- optional (default None)
)
```

:::info
See the `StopLimitOrder` [API Reference](../api_reference/model/orders.md#class-stoplimitorder) for further details.
:::

### Market-To-Limit

A *Market-To-Limit* order is submitted as a market order to execute at the current best market price.
If the order is only partially filled, the remainder of the order is canceled and re-submitted as a *Limit* order with
the limit price equal to the price at which the filled portion of the order executed.

In the following example we create a *Market-To-Limit* order on the Interactive Brokers [IdealPro](https://ibkr.info/node/1708) Forex ECN
to BUY 200,000 USD using JPY:

```python
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model import InstrumentId
from nautilus_trader.model import Quantity
from nautilus_trader.model.orders import MarketToLimitOrder

order: MarketToLimitOrder = self.order_factory.market_to_limit(
    instrument_id=InstrumentId.from_str("USD/JPY.IDEALPRO"),
    order_side=OrderSide.BUY,
    quantity=Quantity.from_int(200_000),
    time_in_force=TimeInForce.GTC,  # <-- optional (default GTC)
    reduce_only=False,  # <-- optional (default False)
    display_qty=None,  # <-- optional (default None which indicates full display)
    tags=None,  # <-- optional (default None)
)
```

:::info
See the `MarketToLimitOrder` [API Reference](../api_reference/model/orders.md#class-markettolimitorder) for further details.
:::

### Market-If-Touched

A *Market-If-Touched* order is a conditional order which once triggered will immediately
place a *Market* order. This order type is often used to enter a new position on a stop price,
or to take profits for an existing position, either as a SELL order against LONG positions,
or as a BUY order against SHORT positions.

In the following example we create a *Market-If-Touched* order on the Binance Futures exchange
to SELL 10 ETHUSDT-PERP Perpetual Futures contracts at a trigger price of 10,000 USDT, active until further notice:

```python
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model.enums import TriggerType
from nautilus_trader.model import InstrumentId
from nautilus_trader.model import Price
from nautilus_trader.model import Quantity
from nautilus_trader.model.orders import MarketIfTouchedOrder

order: MarketIfTouchedOrder = self.order_factory.market_if_touched(
    instrument_id=InstrumentId.from_str("ETHUSDT-PERP.BINANCE"),
    order_side=OrderSide.SELL,
    quantity=Quantity.from_int(10),
    trigger_price=Price.from_str("10_000.00"),
    trigger_type=TriggerType.LAST_PRICE,  # <-- optional (default DEFAULT)
    time_in_force=TimeInForce.GTC,  # <-- optional (default GTC)
    expire_time=None,  # <-- optional (default None)
    reduce_only=False,  # <-- optional (default False)
    tags=["ENTRY"],  # <-- optional (default None)
)
```

:::info
See the `MarketIfTouchedOrder` [API Reference](../api_reference/model/orders.md#class-marketiftouchedorder) for further details.
:::

### Limit-If-Touched

A *Limit-If-Touched* order is a conditional order which once triggered will immediately place
a *Limit* order at the specified price.

In the following example we create a *Limit-If-Touched* order to BUY 5 BTCUSDT-PERP Perpetual Futures contracts on the
Binance Futures exchange at a limit price of 30,100 USDT (once the market hits the trigger price of 30,150 USDT),
active until midday 6th June, 2022 (UTC):

```python
import pandas as pd
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model.enums import TriggerType
from nautilus_trader.model import InstrumentId
from nautilus_trader.model import Price
from nautilus_trader.model import Quantity
from nautilus_trader.model.orders import LimitIfTouchedOrder

order: LimitIfTouchedOrder = self.order_factory.limit_if_touched(
    instrument_id=InstrumentId.from_str("BTCUSDT-PERP.BINANCE"),
    order_side=OrderSide.BUY,
    quantity=Quantity.from_int(5),
    price=Price.from_str("30_100"),
    trigger_price=Price.from_str("30_150"),
    trigger_type=TriggerType.LAST_PRICE,  # <-- optional (default DEFAULT)
    time_in_force=TimeInForce.GTD,  # <-- optional (default GTC)
    expire_time=pd.Timestamp("2022-06-06T12:00"),
    post_only=True,  # <-- optional (default False)
    reduce_only=False,  # <-- optional (default False)
    tags=["TAKE_PROFIT"],  # <-- optional (default None)
)
```

:::info
See the `LimitIfTouched` [API Reference](../api_reference/model/orders.md#class-limitiftouchedorder-1) for further details.
:::

### Trailing-Stop-Market

A *Trailing-Stop-Market* order is a conditional order which trails a stop trigger price
a fixed offset away from the defined market price. Once triggered a *Market* order will
immediately be placed.

In the following example we create a *Trailing-Stop-Market* order on the Binance Futures exchange to SELL 10 ETHUSD-PERP COIN_M margined
Perpetual Futures Contracts activating at a price of 5,000 USD, then trailing at an offset of 1% (in basis points) away from the current last traded price:

```python
import pandas as pd
from decimal import Decimal
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model.enums import TriggerType
from nautilus_trader.model.enums import TrailingOffsetType
from nautilus_trader.model import InstrumentId
from nautilus_trader.model import Price
from nautilus_trader.model import Quantity
from nautilus_trader.model.orders import TrailingStopMarketOrder

order: TrailingStopMarketOrder = self.order_factory.trailing_stop_market(
    instrument_id=InstrumentId.from_str("ETHUSD-PERP.BINANCE"),
    order_side=OrderSide.SELL,
    quantity=Quantity.from_int(10),
    activation_price=Price.from_str("5_000"),
    trigger_type=TriggerType.LAST_PRICE,  # <-- optional (default DEFAULT)
    trailing_offset=Decimal(100),
    trailing_offset_type=TrailingOffsetType.BASIS_POINTS,
    time_in_force=TimeInForce.GTC,  # <-- optional (default GTC)
    expire_time=None,  # <-- optional (default None)
    reduce_only=True,  # <-- optional (default False)
    tags=["TRAILING_STOP-1"],  # <-- optional (default None)
)
```

:::info
See the `TrailingStopMarketOrder` [API Reference](../api_reference/model/orders.md#class-trailingstopmarketorder-1) for further details.
:::

### Trailing-Stop-Limit

A *Trailing-Stop-Limit* order is a conditional order which trails a stop trigger price
a fixed offset away from the defined market price. Once triggered a *Limit* order will
immediately be placed at the defined price (which is also updated as the market moves until triggered).

In the following example we create a *Trailing-Stop-Limit* order on the Currenex FX ECN to BUY 1,250,000 AUD using USD
at a limit price of 0.71000 USD, activating at 0.72000 USD then trailing at a stop offset of 0.00100 USD
away from the current ask price, active until further notice:

```python
import pandas as pd
from decimal import Decimal
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model.enums import TriggerType
from nautilus_trader.model.enums import TrailingOffsetType
from nautilus_trader.model import InstrumentId
from nautilus_trader.model import Price
from nautilus_trader.model import Quantity
from nautilus_trader.model.orders import TrailingStopLimitOrder

order: TrailingStopLimitOrder = self.order_factory.trailing_stop_limit(
    instrument_id=InstrumentId.from_str("AUD/USD.CURRENEX"),
    order_side=OrderSide.BUY,
    quantity=Quantity.from_int(1_250_000),
    price=Price.from_str("0.71000"),
    activation_price=Price.from_str("0.72000"),
    trigger_type=TriggerType.BID_ASK,  # <-- optional (default DEFAULT)
    limit_offset=Decimal("0.00050"),
    trailing_offset=Decimal("0.00100"),
    trailing_offset_type=TrailingOffsetType.PRICE,
    time_in_force=TimeInForce.GTC,  # <-- optional (default GTC)
    expire_time=None,  # <-- optional (default None)
    reduce_only=True,  # <-- optional (default False)
    tags=["TRAILING_STOP"],  # <-- optional (default None)
)
```

:::info
See the `TrailingStopLimitOrder` [API Reference](../api_reference/model/orders.md#class-trailingstoplimitorder-1) for further details.
:::

## Advanced Orders

The following guide should be read in conjunction with the specific documentation from the broker or venue
involving these order types, lists/groups and execution instructions (such as for Interactive Brokers).

### Order Lists

Combinations of contingent orders, or larger order bulks can be grouped together into a list with a common
`order_list_id`. The orders contained in this list may or may not have a contingent relationship with
each other, as this is specific to how the orders themselves are constructed, and the
specific venue they are being routed to.

### Contingency Types

- **OTO (One-Triggers-Other)** – a parent order that, once executed, automatically places one or more child orders.
  - *Full-trigger model*: child order(s) are released **only after the parent is completely filled**. Common at most retail equity/option brokers (e.g. Schwab, Fidelity, TD Ameritrade) and many spot-crypto venues (Binance, Coinbase).
  - *Partial-trigger model*: child order(s) are released **pro-rata to each partial fill**. Used by professional-grade platforms such as Interactive Brokers, most futures/FX OMSs, and Kraken Pro.

- **OCO (One-Cancels-Other)** – two (or more) linked live orders where executing one cancels the remainder.

- **OUO (One-Updates-Other)** – two (or more) linked live orders where executing one reduces the open quantity of the remainder.

:::info
These contingency types relate to ContingencyType FIX tag <1385> <https://www.onixs.biz/fix-dictionary/5.0.sp2/tagnum_1385.html>.
:::

#### One-Triggers-Other (OTO)

An OTO order involves two parts:

1. **Parent order** – submitted to the matching engine immediately.
2. **Child order(s)** – held *off-book* until the trigger condition is met.

##### Trigger models

| Trigger model       | When are child orders released?                                                                                                                  |
|---------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| **Full trigger**    | When the parent order’s cumulative quantity equals its original quantity (i.e., it is *fully* filled).                                           |
| **Partial trigger** | Immediately upon each partial execution of the parent; the child’s quantity matches the executed amount and is increased as further fills occur. |

:::info
The default backtest venue for NautilusTrader uses a *partial-trigger model* for OTO orders.
A future update will add configuration to opt-in to a *full-trigger model*.
:::

> **Why the distinction matters**
> *Full trigger* leaves a risk window: any partially filled position is live without its protective exit until the remaining quantity fills.
> *Partial trigger* mitigates that risk by ensuring every executed lot instantly has its linked stop/limit, at the cost of creating more order traffic and updates.

An OTO order can use any supported asset type on the venue (e.g. stock entry with option hedge, futures entry with OCO bracket, crypto spot entry with TP/SL).

| Venue / Adapter ID                           | Asset classes             | Trigger rule for child                      | Practical notes                                                   |
|----------------------------------------------|---------------------------|---------------------------------------------|-------------------------------------------------------------------|
| Binance / Binance Futures (`BINANCE`)        | Spot, perpetual futures   | **Partial or full** – fires on first fill.  | OTOCO/TP-SL children appear instantly; monitor margin usage.      |
| Bybit Spot (`BYBIT`)                         | Spot                      | **Full** – child placed after completion.   | TP-SL preset activates only once the limit order is fully filled. |
| Bybit Perps (`BYBIT`)                        | Perpetual futures         | **Partial and full** – configurable.        | “Partial-position” mode sizes TP-SL as fills arrive.              |
| Kraken Futures (`KRAKEN`)                    | Futures & perps           | **Partial and full** – automatic.           | Child quantity matches every partial execution.                   |
| OKX (`OKX`)                                  | Spot, futures, options    | **Full** – attached stop waits for fill.    | Position-level TP-SL can be added separately.                     |
| Interactive Brokers (`INTERACTIVE_BROKERS`)  | Stocks, options, FX, fut  | **Configurable** – OCA can pro-rate.        | `OcaType 2/3` reduces remaining child quantities.                 |
| Coinbase International (`COINBASE_INTX`)     | Spot & perps              | **Full** – bracket added post-execution.    | Entry plus bracket not simultaneous; added once position is live. |
| dYdX v4 (`DYDX`)                             | Perpetual futures (DEX)   | On-chain condition (size exact).            | TP-SL triggers by oracle price; partial fill not applicable.      |
| Polymarket (`POLYMARKET`)                    | Prediction market (DEX)   | N/A.                                        | Advanced contingency handled entirely at the strategy layer.      |
| Betfair (`BETFAIR`)                          | Sports betting            | N/A.                                        | Advanced contingency handled entirely at the strategy layer.      |

#### One-Cancels-Other (OCO)

An OCO order is a set of linked orders where the execution of **any** order (full *or partial*) triggers a best-efforts cancellation of the others.
Both orders are live simultaneously; once one starts filling, the venue attempts to cancel the unexecuted portion of the remainder.

#### One-Updates-Other (OUO)

An OUO order is a set of linked orders where execution of one order causes an immediate *reduction* of open quantity in the other order(s).
Both orders are live concurrently, and each partial execution proportionally updates the remaining quantity of its peer order on a best-effort basis.

### Bracket Orders

Bracket orders are an advanced order type that allows traders to set both take-profit and stop-loss
levels for a position simultaneously. This involves placing a parent order (entry order) and two child
orders: a take-profit `LIMIT` order and a stop-loss `STOP_MARKET` order. When the parent order is executed,
the child orders are placed in the market. The take-profit order closes the position with profits if
the market moves favorably, while the stop-loss order limits losses if the market moves unfavorably.

Bracket orders can be easily created using the [OrderFactory](../api_reference/common.md#class-orderfactory),
which supports various order types, parameters, and instructions.

:::warning
You should be aware of the margin requirements of positions, as bracketing a position will consume
more order margin.
:::

## Emulated Orders

### Introduction

Before diving into the technical details, it's important to understand the fundamental purpose of emulated orders
in Nautilus Trader. At its core, emulation allows you to use certain order types even when your trading venue
doesn't natively support them.

This works by having Nautilus locally mimic the behavior of these order types (such as `STOP_LIMIT` or `TRAILING_STOP` orders)
locally, while using only simple `MARKET` and `LIMIT` orders for actual execution on the venue.

When you create an emulated order, Nautilus continuously tracks a specific type of market price (specified by the
`emulation_trigger` parameter) and based on the order type and conditions you've set, will automatically submit
the appropriate fundamental order (`MARKET` / `LIMIT`) when the triggering condition is met.

For example, if you create an emulated `STOP_LIMIT` order, Nautilus will monitor the market price until your `stop`
price is reached, and then automatically submits a `LIMIT` order to the venue.

To perform emulation, Nautilus needs to know which **type of market price** it should monitor.
By default, it uses bid and ask prices (quotes), which is why you'll often see `emulation_trigger=TriggerType.DEFAULT`
in examples (this is equivalent to using `TriggerType.BID_ASK`). However, Nautilus supports various other price types,
that can guide the emulation process.

### Submitting order for emulation

The only requirement to emulate an order is to pass a `TriggerType` to the `emulation_trigger`
parameter of an `Order` constructor, or `OrderFactory` creation method. The following
emulation trigger types are currently supported:

- `NO_TRIGGER`: disables local emulation completely and order is fully submitted to the venue.
- `DEFAULT`: which is the same as `BID_ASK`.
- `BID_ASK`: emulated using quotes to trigger.
- `LAST`: emulated using trades to trigger.

The choice of trigger type determines how the order emulation will behave:

- For `STOP` orders, the trigger price of order will be compared against the specified trigger type.
- For `TRAILING_STOP` orders, the trailing offset will be updated based on the specified trigger type.
- For `LIMIT` orders, the limit price of order will be compared against the specified trigger type.

Here are all the available values you can set into `emulation_trigger` parameter and their purposes:

| Trigger Type      | Description                                                                                          | Common use cases                                                                                             |
|:------------------|:-----------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------|
| `NO_TRIGGER`      | Disables emulation completely. The order is sent directly to the venue without any local processing. | When you want to use the venue's native order handling, or for simple order types that don't need emulation. |
| `DEFAULT`         | Same as `BID_ASK`. This is the standard choice for most emulated orders.                             | General-purpose emulation when you want to work with the "default" type of market prices.                    |
| `BID_ASK`         | Uses the best bid and ask prices (quotes) to guide emulation.                                        | Stop orders, trailing stops, and other orders that should react to the current market spread.                |
| `LAST_PRICE`      | Uses the price of the most recent trade to guide emulation.                                          | Orders that should trigger based on actual executed trades rather than quotes.                               |
| `DOUBLE_LAST`     | Uses two consecutive last trade prices to confirm the trigger condition.                             | When you want additional confirmation of price movement before triggering.                                   |
| `DOUBLE_BID_ASK`  | Uses two consecutive bid/ask price updates to confirm the trigger condition.                         | When you want extra confirmation of quote movements before triggering.                                       |
| `LAST_OR_BID_ASK` | Triggers on either last trade price or bid/ask prices.                                               | When you want to be more responsive to any type of price movement.                                           |
| `MID_POINT`       | Uses the middle point between the best bid and ask prices.                                           | Orders that should trigger based on the theoretical fair price.                                              |
| `MARK_PRICE`      | Uses the mark price (common in derivatives markets) for triggering.                                  | Particularly useful for futures and perpetual contracts.                                                     |
| `INDEX_PRICE`     | Uses an underlying index price for triggering.                                                       | When trading derivatives that track an index.                                                                |

### Technical implementation

The platform makes it possible to emulate most order types locally, regardless
of whether the type is supported on a trading venue. The logic and code paths for
order emulation are exactly the same for all [environment contexts](/concepts/architecture.md#environment-contexts)
and utilize a common `OrderEmulator` component.

:::note
There is no limitation on the number of emulated orders you can have per running instance.
:::

### Life cycle

An emulated order will progress through the following stages:

1. Submitted by a `Strategy` through the `submit_order` method.
2. Sent to the `RiskEngine` for pre-trade risk checks (it may be denied at this point).
3. Sent to the `OrderEmulator` where it is *held* / emulated.
4. Once triggered, emulated order is transformed into a `MARKET` or `LIMIT` order and released (submitted to the venue).
5. Released order undergoes final risk checks before venue submission.

:::note
Emulated orders are subject to the same risk controls as *regular* orders, and can be
modified and canceled by a trading strategy in the normal way. They will also be included
when canceling all orders.
:::

:::info
An emulated order will retain its original client order ID throughout its entire life cycle, making it easy to query
through the cache.
:::

#### Held emulated orders

The following will occur for an emulated order now *held* by the `OrderEmulator` component:

- The original `SubmitOrder` command will be cached.
- The emulated order will be processed inside a local `MatchingCore` component.
- The `OrderEmulator` will subscribe to any needed market data (if not already) to update the matching core.
- The emulated order can be modified (by the trader) and updated (by the market) until *released* or canceled.

#### Released emulated orders

Once an emulated order is triggered / matched locally based on the arrival of data, the following
*release* actions will occur:

- The order will be transformed to either a `MARKET` or `LIMIT` order (see below table) through an additional `OrderInitialized` event.
- The orders `emulation_trigger` will be set to `NONE` (it will no longer be treated as an emulated order by any component).
- The order attached to the original `SubmitOrder` command will be sent back to the `RiskEngine` for additional checks since any modification/updates.
- If not denied, then the command will continue to the `ExecutionEngine` and on to the trading venue via an `ExecutionClient` as normal.

The following table lists which order types are possible to emulate, and
which order type they transform to when being released for submission to the
trading venue.

### Order types, which can be emulated

The following table lists which order types are possible to emulate, and
which order type they transform to when being released for submission to the
trading venue.

| Order type for emulation | Can emulate | Released type |
|:-------------------------|:------------|:--------------|
| `MARKET`                 |             | n/a           |
| `MARKET_TO_LIMIT`        |             | n/a           |
| `LIMIT`                  | ✓           | `MARKET`      |
| `STOP_MARKET`            | ✓           | `MARKET`      |
| `STOP_LIMIT`             | ✓           | `LIMIT`       |
| `MARKET_IF_TOUCHED`      | ✓           | `MARKET`      |
| `LIMIT_IF_TOUCHED`       | ✓           | `LIMIT`       |
| `TRAILING_STOP_MARKET`   | ✓           | `MARKET`      |
| `TRAILING_STOP_LIMIT`    | ✓           | `LIMIT`       |

### Querying

When writing trading strategies, it may be necessary to know the state of emulated orders in the system.
There are several ways to query emulation status:

#### Through the Cache

The following `Cache` methods are available:

- `self.cache.orders_emulated(...)`: Returns all currently emulated orders.
- `self.cache.is_order_emulated(...)`: Checks if a specific order is emulated.
- `self.cache.orders_emulated_count(...)`: Returns the count of emulated orders.

See the full [API reference](../../api_reference/cache) for additional details.

#### Direct order queries

You can query order objects directly using:

- `order.is_emulated`

If either of these return `False`, then the order has been *released* from the
`OrderEmulator`, and so is no longer considered an emulated order (or was never an emulated order).

:::warning
It's not advised to hold a local reference to an emulated order, as the order
object will be transformed when/if the emulated order is *released*. You should rely
on the `Cache` which is made for the job.
:::

### Persistence and recovery

If a running system either crashes or shuts down with active emulated orders, then
they will be reloaded inside the `OrderEmulator` from any configured cache database.
This ensures order state persistence across system restarts and recoveries.

### Best practices

When working with emulated orders, consider the following best practices:

1. Always use the `Cache` for querying or tracking emulated orders rather than storing local references
2. Be aware that emulated orders transform to different types when released
3. Remember that emulated orders undergo risk checks both at submission and release

:::note
Order emulation allows you to use advanced order types even on venues that don't natively support them,
making your trading strategies more portable across different venues.
:::


---

file path: ./concepts/overview.md
# Overview

## Introduction

NautilusTrader is an open-source, high-performance, production-grade algorithmic trading platform,
providing quantitative traders with the ability to backtest portfolios of automated trading strategies
on historical data with an event-driven engine, and also deploy those same strategies live, with no code changes.

The platform is *AI-first*, designed to develop and deploy algorithmic trading strategies within a highly performant
and robust Python-native environment. This helps to address the parity challenge of keeping the Python research/backtest
environment consistent with the production live trading environment.

NautilusTrader's design, architecture, and implementation philosophy prioritizes software correctness and safety at the
highest level, with the aim of supporting Python-native, mission-critical, trading system backtesting
and live deployment workloads.

The platform is also universal and asset-class-agnostic — with any REST API or WebSocket stream able to be integrated via modular
adapters. It supports high-frequency trading across a wide range of asset classes and instrument types
including FX, Equities, Futures, Options, Crypto and Betting, enabling seamless operations across multiple venues simultaneously.

## Features

- **Fast**: Core is written in Rust with asynchronous networking using [tokio](https://crates.io/crates/tokio).
- **Reliable**: Rust-powered type- and thread-safety, with optional Redis-backed state persistence.
- **Portable**: OS independent, runs on Linux, macOS, and Windows. Deploy using Docker.
- **Flexible**: Modular adapters mean any REST API or WebSocket stream can be integrated.
- **Advanced**: Time in force `IOC`, `FOK`, `GTC`, `GTD`, `DAY`, `AT_THE_OPEN`, `AT_THE_CLOSE`, advanced order types and conditional triggers. Execution instructions `post-only`, `reduce-only`, and icebergs. Contingency orders including `OCO`, `OUO`, `OTO`.
- **Customizable**: Add user-defined custom components, or assemble entire systems from scratch leveraging the [cache](cache.md) and [message bus](message_bus.md).
- **Backtesting**: Run with multiple venues, instruments and strategies simultaneously using historical quote tick, trade tick, bar, order book and custom data with nanosecond resolution.
- **Live**: Use identical strategy implementations between backtesting and live deployments.
- **Multi-venue**: Multiple venue capabilities facilitate market-making and statistical arbitrage strategies.
- **AI Training**: Backtest engine fast enough to be used to train AI trading agents (RL/ES).

![Nautilus](https://github.com/nautechsystems/nautilus_trader/blob/develop/assets/nautilus-art.png?raw=true "nautilus")
> *nautilus - from ancient Greek 'sailor' and naus 'ship'.*
>
> *The nautilus shell consists of modular chambers with a growth factor which approximates a logarithmic spiral.
> The idea is that this can be translated to the aesthetics of design and architecture.*

## Why NautilusTrader?

- **Highly performant event-driven Python**: Native binary core components.
- **Parity between backtesting and live trading**: Identical strategy code.
- **Reduced operational risk**: Enhanced risk management functionality, logical accuracy, and type safety.
- **Highly extendable**: Message bus, custom components and actors, custom data, custom adapters.

Traditionally, trading strategy research and backtesting might be conducted in Python
using vectorized methods, with the strategy then needing to be reimplemented in a more event-driven way
using C++, C#, Java or other statically typed language(s). The reasoning here is that vectorized backtesting code cannot
express the granular time and event dependent complexity of real-time trading, where compiled languages have
proven to be more suitable due to their inherently higher performance, and type safety.

One of the key advantages of NautilusTrader here, is that this reimplementation step is now circumvented - as the critical core components of the platform
have all been written entirely in [Rust](https://www.rust-lang.org/) or [Cython](https://cython.org/).
This means we're using the right tools for the job, where systems programming languages compile performant binaries,
with CPython C extension modules then able to offer a Python-native environment, suitable for professional quantitative traders and trading firms.

## Use Cases

There are three main use cases for this software package:

- Backtest trading systems on historical data (`backtest`).
- Simulate trading systems with real-time data and virtual execution (`sandbox`).
- Deploy trading systems live on real or paper accounts (`live`).

The project's codebase provides a framework for implementing the software layer of systems which achieve the above. You will find
the default `backtest` and `live` system implementations in their respectively named subpackages. A `sandbox` environment can
be built using the sandbox adapter.

:::note

- All examples will utilize these default system implementations.
- We consider trading strategies to be subcomponents of end-to-end trading systems, these systems
include the application and infrastructure layers.

:::

## Distributed

The platform is designed to be easily integrated into a larger distributed system.
To facilitate this, nearly all configuration and domain objects can be serialized using JSON, MessagePack or Apache Arrow (Feather) for communication over the network.

## Common Core

The common system core is utilized by all node [environment contexts](/concepts/architecture.md#environment-contexts) (`backtest`, `sandbox`, and `live`).
User-defined `Actor`, `Strategy` and `ExecAlgorithm` components are managed consistently across these environment contexts.

## Backtesting

Backtesting can be achieved by first making data available to a `BacktestEngine` either directly or via
a higher level `BacktestNode` and `ParquetDataCatalog`, and then running the data through the system with nanosecond resolution.

## Live Trading

A `TradingNode` can ingest data and events from multiple data and execution clients.
Live deployments can use both demo/paper trading accounts, or real accounts.

For live trading, a `TradingNode` can ingest data and events from multiple data and execution clients.
The platform supports both demo/paper trading accounts and real accounts. High performance can be achieved by running
asynchronously on a single [event loop](https://docs.python.org/3/library/asyncio-eventloop.html),
with the potential to further boost performance by leveraging the [uvloop](https://github.com/MagicStack/uvloop) implementation (available for Linux and macOS).

## Domain Model

The platform features a comprehensive trading domain model that includes various value types such as
`Price` and `Quantity`, as well as more complex entities such as `Order` and `Position` objects,
which are used to aggregate multiple events to determine state.

## Timestamps

All timestamps within the platform are recorded at nanosecond precision in UTC.

Timestamp strings follow ISO 8601 (RFC 3339) format with either 9 digits (nanoseconds) or 3 digits (milliseconds) of decimal precision,
(but mostly nanoseconds) always maintaining all digits including trailing zeros.
These can be seen in log messages, and debug/display outputs for objects.

A timestamp string consists of:

- Full date component always present: `YYYY-MM-DD`.
- `T` separator between date and time components.
- Always nanosecond precision (9 decimal places) or millisecond precision (3 decimal places) for certain cases such as GTD expiry times.
- Always UTC timezone designated by `Z` suffix.

Example: `2024-01-05T15:30:45.123456789Z`

For the complete specification, refer to [RFC 3339: Date and Time on the Internet](https://datatracker.ietf.org/doc/html/rfc3339).

## UUIDs

The platform uses Universally Unique Identifiers (UUID) version 4 (RFC 4122) for unique identifiers.
Our high-performance implementation leverages the `uuid` crate for correctness validation when parsing from strings,
ensuring input UUIDs comply with the specification.

A valid UUID v4 consists of:

- 32 hexadecimal digits displayed in 5 groups.
- Groups separated by hyphens: `8-4-4-4-12` format.
- Version 4 designation (indicated by the third group starting with "4").
- RFC 4122 variant designation (indicated by the fourth group starting with "8", "9", "a", or "b").

Example: `2d89666b-1a1e-4a75-b193-4eb3b454c757`

For the complete specification, refer to [RFC 4122: A Universally Unique IDentifier (UUID) URN Namespace](https://datatracker.ietf.org/doc/html/rfc4122).

## Data Types

The following market data types can be requested historically, and also subscribed to as live streams when available from a venue / data provider, and implemented in an integrations adapter.

- `OrderBookDelta` (L1/L2/L3)
- `OrderBookDeltas` (container type)
- `OrderBookDepth10` (fixed depth of 10 levels per side)
- `QuoteTick`
- `TradeTick`
- `Bar`
- `Instrument`
- `InstrumentStatus`
- `InstrumentClose`

The following `PriceType` options can be used for bar aggregations:

- `BID`
- `ASK`
- `MID`
- `LAST`

## Bar Aggregations

The following `BarAggregation` methods are available:

- `MILLISECOND`
- `SECOND`
- `MINUTE`
- `HOUR`
- `DAY`
- `WEEK`
- `MONTH`
- `TICK`
- `VOLUME`
- `VALUE` (a.k.a Dollar bars)
- `TICK_IMBALANCE`
- `TICK_RUNS`
- `VOLUME_IMBALANCE`
- `VOLUME_RUNS`
- `VALUE_IMBALANCE`
- `VALUE_RUNS`

The price types and bar aggregations can be combined with step sizes >= 1 in any way through a `BarSpecification`.
This enables maximum flexibility and now allows alternative bars to be aggregated for live trading.

## Account Types

The following account types are available for both live and backtest environments:

- `Cash` single-currency (base currency)
- `Cash` multi-currency
- `Margin` single-currency (base currency)
- `Margin` multi-currency
- `Betting` single-currency

## Order Types

The following order types are available (when possible on a venue):

- `MARKET`
- `LIMIT`
- `STOP_MARKET`
- `STOP_LIMIT`
- `MARKET_TO_LIMIT`
- `MARKET_IF_TOUCHED`
- `LIMIT_IF_TOUCHED`
- `TRAILING_STOP_MARKET`
- `TRAILING_STOP_LIMIT`

## Value Types

The following value types are backed by either 128-bit or 64-bit raw integer values, depending on the
[precision mode](../getting_started/installation.md#precision-mode) used during compilation.

- `Price`
- `Quantity`
- `Money`

### High-precision mode (128-bit)

When the `high-precision` feature flag is **enabled** (default), values use the specification:

| Type         | Raw backing | Max precision | Min value           | Max value          |
|:-------------|:------------|:--------------|:--------------------|:-------------------|
| `Price`      | `i128`      | 16            | -17,014,118,346,046 | 17,014,118,346,046 |
| `Money`      | `i128`      | 16            | -17,014,118,346,046 | 17,014,118,346,046 |
| `Quantity`   | `u128`      | 16            | 0                   | 34,028,236,692,093 |

### Standard-precision mode (64-bit)

When the `high-precision` feature flag is **disabled**, values use the specification:

| Type         | Raw backing | Max precision | Min value           | Max value          |
|:-------------|:------------|:--------------|:--------------------|:-------------------|
| `Price`      | `i64`       | 9             | -9,223,372,036      | 9,223,372,036      |
| `Money`      | `i64`       | 9             | -9,223,372,036      | 9,223,372,036      |
| `Quantity`   | `u64`       | 9             | 0                   | 18,446,744,073     |


---

file path: ./concepts/actors.md
# Actors

:::info
We are currently working on this concept guide.
:::

The `Actor` serves as the foundational component for interacting with the trading system.
It provides core functionality for receiving market data, handling events, and managing state within
the trading environment. The `Strategy` class inherits from Actor and extends its capabilities with
order management methods.

**Key capabilities**:

- Event subscription and handling
- Market data reception
- State management
- System interaction primitives

## Basic example

Just like strategies, actors support configuration through a very similar pattern.

```python
from nautilus_trader.config import ActorConfig
from nautilus_trader.model import InstrumentId
from nautilus_trader.model import Bar, BarType
from nautilus_trader.common.actor import Actor


class MyActorConfig(ActorConfig):
    instrument_id: InstrumentId   # example value: "ETHUSDT-PERP.BINANCE"
    bar_type: BarType             # example value: "ETHUSDT-PERP.BINANCE-15-MINUTE[LAST]-INTERNAL"
    lookback_period: int = 10


class MyActor(Actor):
    def __init__(self, config: MyActorConfig) -> None:
        super().__init__(config)

        # Custom state variables
        self.count_of_processed_bars: int = 0

    def on_start(self) -> None:
        # Subscribe to all incoming bars
        self.subscribe_bars(self.config.bar_type)   # You can access configuration directly via `self.config`

    def on_bar(self, bar: Bar):
        self.count_of_processed_bars += 1
```

## Data handling and callbacks

When working with data in Nautilus, it's important to understand the relationship between data
*requests/subscriptions* and their corresponding callback handlers. The system uses different handlers
depending on whether the data is historical or real-time.

### Historical vs real-time data

The system distinguishes between two types of data flow:

1. **Historical data** (from *requests*):
   - Obtained through methods like `request_bars()`, `request_quote_ticks()`, etc.
   - Processed through the `on_historical_data()` handler.
   - Used for initial data loading and historical analysis.

2. **Real-time data** (from *subscriptions*):
   - Obtained through methods like `subscribe_bars()`, `subscribe_quote_ticks()`, etc.
   - Processed through specific handlers like `on_bar()`, `on_quote_tick()`, etc.
   - Used for live data processing.

### Callback handlers

Here's how different data operations map to their handlers:

| Operation                       | Category         | Handler                  | Purpose |
|:--------------------------------|:-----------------|:-------------------------|:--------|
| `subscribe_data()`              | Real-time&nbsp;  | `on_data()`              | Live data updates |
| `subscribe_instrument()`        | Real-time&nbsp;  | `on_instrument()`        | Live instrument definition updates |
| `subscribe_instruments()`       | Real-time&nbsp;  | `on_instrument()`        | Live instrument definition updates (for venue) |
| `subscribe_order_book_deltas()` | Real-time&nbsp;  | `on_order_book_deltas()` | Live order book updates |
| `subscribe_quote_ticks()`       | Real-time&nbsp;  | `on_quote_tick()`        | Live quote updates |
| `subscribe_trade_ticks()`       | Real-time&nbsp;  | `on_trade_tick()`        | Live trade updates |
| `subscribe_mark_prices()`       | Real-time&nbsp;  | `on_mark_price()`        | Live mark price updates |
| `subscribe_index_prices()`      | Real-time&nbsp;  | `on_index_price()`       | Live index price updates |
| `subscribe_bars()`              | Real-time&nbsp;  | `on_bar()`               | Live bar updates |
| `subscribe_instrument_status()` | Real-time&nbsp;  | `on_instrument_status()` | Live instrument status updates |
| `subscribe_instrument_close()`  | Real-time&nbsp;  | `on_instrument_close()`  | Live instrument close updates |
| `request_data()`                | Historical       | `on_historical_data()`   | Historical data processing |
| `request_instrument()`          | Historical       | `on_instrument()`        | Instrument definition updates |
| `request_instruments()`         | Historical       | `on_instrument()`        | Instrument definition updates |
| `request_quote_ticks()`         | Historical       | `on_historical_data()`   | Historical quotes processing |
| `request_trade_ticks()`         | Historical       | `on_historical_data()`   | Historical trades processing |
| `request_bars()`                | Historical       | `on_historical_data()`   | Historical bars processing |
| `request_aggregated_bars()`     | Historical       | `on_historical_data()`   | Historical aggregated bars (on-the-fly) |

### Example

Here's an example demonstrating both historical and real-time data handling:

```python
from nautilus_trader.common.actor import Actor
from nautilus_trader.config import ActorConfig
from nautilus_trader.core.data import Data
from nautilus_trader.model import Bar, BarType
from nautilus_trader.model import ClientId, InstrumentId


class MyActorConfig(ActorConfig):
    instrument_id: InstrumentId  # example value: "AAPL.XNAS"
    bar_type: BarType            # example value: "AAPL.XNAS-1-MINUTE-LAST-EXTERNAL"


class MyActor(Actor):
    def __init__(self, config: MyActorConfig) -> None:
        super().__init__(config)
        self.bar_type = config.bar_type

    def on_start(self) -> None:
        # Request historical data - will be processed by on_historical_data() handler
        self.request_bars(
            bar_type=self.bar_type,
            # Many optional parameters
            start=None,                # datetime, optional
            end=None,                  # datetime, optional
            callback=None,             # called with the request ID when completed
            update_catalog_mode=None,  # UpdateCatalogMode | None, default None
            params=None,               # dict[str, Any], optional
        )

        # Subscribe to real-time data - will be processed by on_bar() handler
        self.subscribe_bars(
            bar_type=self.bar_type,
            # Many optional parameters
            client_id=None,       # ClientId, optional
            await_partial=False,  # bool, default False
            params=None,          # dict[str, Any], optional
        )

    def on_historical_data(self, data: Data) -> None:
        # Handle historical data (from requests)
        if isinstance(data, Bar):
            self.log.info(f"Received historical bar: {data}")

    def on_bar(self, bar: Bar) -> None:
        # Handle real-time bar updates (from subscriptions)
        self.log.info(f"Received real-time bar: {bar}")
```

This separation between historical and real-time data handlers allows for different processing logic
based on the data context. For example, you might want to:

- Use historical data to initialize indicators or establish baseline metrics.
- Process real-time data differently for live trading decisions.
- Apply different validation or logging for historical vs real-time data.

:::tip
When debugging data flow issues, check that you're looking at the correct handler for your data source.
If you're not seeing data in `on_bar()` but see log messages about receiving bars, check `on_historical_data()`
as the data might be coming from a request rather than a subscription.
:::


---

file path: ./concepts/logging.md
# Logging

The platform provides logging for both backtesting and live trading using a high-performance logging subsystem implemented in Rust
with a standardized facade from the `log` crate.

The core logger operates in a separate thread and uses a multi-producer single-consumer (MPSC) channel to receive log messages.
This design ensures that the main thread remains performant, avoiding potential bottlenecks caused by log string formatting or file I/O operations.

Logging output is configurable and supports:

- **stdout/stderr writer** for console output
- **file writer** for persistent storage of logs

:::info
Infrastructure such as [Vector](https://github.com/vectordotdev/vector) can be integrated to collect and aggregate events within your system.
:::

## Configuration

Logging can be configured by importing the `LoggingConfig` object.
By default, log events with an 'INFO' `LogLevel` and higher are written to stdout/stderr.

Log level (`LogLevel`) values include (and generally match Rust's `tracing` level filters).

Python loggers expose the following levels:

- `OFF`
- `DEBUG`
- `INFO`
- `WARNING`
- `ERROR`

:::warning
The Python `Logger` does not provide a `trace()` method; `TRACE` level logs are only emitted by the underlying Rust components and cannot be generated directly from Python code.

See the `LoggingConfig` [API Reference](../api_reference/config.md#class-loggingconfig) for further details.
:::

Logging can be configured in the following ways:

- Minimum `LogLevel` for stdout/stderr
- Minimum `LogLevel` for log files
- Maximum size before rotating a log file
- Maximum number of backup log files to maintain when rotating
- Automatic log file naming with date or timestamp components, or custom log file name
- Directory for writing log files
- Plain text or JSON log file formatting
- Filtering of individual components by log level
- ANSI colors in log lines
- Bypass logging entirely
- Print Rust config to stdout at initialization
- Optionally initialize logging via the PyO3 bridge (`use_pyo3`) to capture log events emitted by Rust components
- Truncate existing log file on startup if it already exists (`clear_log_file`)

### Standard output logging

Log messages are written to the console via stdout/stderr writers. The minimum log level can be configured using the `log_level` parameter.

### File logging

Log files are written to the current working directory by default. The naming convention and rotation behavior are configurable and follow specific patterns based on your settings.

You can specify a custom log directory using `log_directory` and/or a custom file basename using `log_file_name`. Log files are always suffixed with `.log` (plain text) or `.json` (JSON).

For detailed information about log file naming conventions and rotation behavior, see the [Log file rotation](#log-file-rotation) and [Log file naming convention](#log-file-naming-convention) sections below.

#### Log file rotation

Rotation behavior depends on both the presence of a size limit and whether a custom file name is provided:

- **Size-based rotation**:
  - Enabled by specifying the `log_file_max_size` parameter (e.g., `100_000_000` for 100 MB).
  - When writing a log entry would make the current file exceed this size, the file is closed and a new one is created.
- **Date-based rotation (default naming only)**:
  - Applies when no `log_file_max_size` is specified and no custom `log_file_name` is provided.
  - At each UTC date change (midnight), the current log file is closed and a new one is started, creating one file per UTC day.
- **No rotation**:
  - When a custom `log_file_name` is provided without a `log_file_max_size`, logs continue to append to the same file.
- **Backup file management**:
  - Controlled by the `log_file_max_backup_count` parameter (default: 5), limiting the total number of rotated files kept.
  - When this limit is exceeded, the oldest backup files are automatically removed.

#### Log file naming convention

The default naming convention ensures log files are uniquely identifiable and timestamped.
The format depends on whether file rotation is enabled:

**With file rotation enabled**:

- **Format**: `{trader_id}_{%Y-%m-%d_%H%M%S:%3f}_{instance_id}.{log|json}`
- **Example**: `TESTER-001_2025-04-09_210721:521_d7dc12c8-7008-4042-8ac4-017c3db0fc38.log`
- **Components**:
  - `{trader_id}`: The trader identifier (e.g., `TESTER-001`).
  - `{%Y-%m-%d_%H%M%S:%3f}`: Full ISO 8601-compliant datetime with millisecond resolution.
  - `{instance_id}`: A unique instance identifier.
  - `{log|json}`: File suffix based on format setting.

**With file rotation disabled**:

- **Format**: `{trader_id}_{%Y-%m-%d}_{instance_id}.{log|json}`
- **Example**: `TESTER-001_2025-04-09_d7dc12c8-7008-4042-8ac4-017c3db0fc38.log`
- **Components**:
  - `{trader_id}`: The trader identifier.
  - `{%Y-%m-%d}`: Date only (YYYY-MM-DD).
  - `{instance_id}`: A unique instance identifier.
  - `{log|json}`: File suffix based on format setting.

**Custom naming**:

If `log_file_name` is set (e.g., `my_custom_log`):

- With rotation disabled: The file will be named exactly as provided (e.g., `my_custom_log.log`).
- With rotation enabled: The file will include the custom name and timestamp (e.g., `my_custom_log_2025-04-09_210721:521.log`).

### Component log filtering

The `log_component_levels` parameter can be used to set log levels for each component individually.
The input value should be a dictionary of component ID strings to log level strings: `dict[str, str]`.

Below is an example of a trading node logging configuration that includes some of the options mentioned above:

```python
from nautilus_trader.config import LoggingConfig
from nautilus_trader.config import TradingNodeConfig

config_node = TradingNodeConfig(
    trader_id="TESTER-001",
    logging=LoggingConfig(
        log_level="INFO",
        log_level_file="DEBUG",
        log_file_format="json",
        log_component_levels={ "Portfolio": "INFO" },
    ),
    ... # Omitted
)
```

For backtesting, the `BacktestEngineConfig` class can be used instead of `TradingNodeConfig`, as the same options are available.

### Log Colors

ANSI color codes are utilized to enhance the readability of logs when viewed in a terminal.
These color codes can make it easier to distinguish different parts of log messages.
In environments that do not support ANSI color rendering (such as some cloud environments or text editors),
these color codes may not be appropriate as they can appear as raw text.

To accommodate for such scenarios, the `LoggingConfig.log_colors` option can be set to `false`.
Disabling `log_colors` will prevent the addition of ANSI color codes to the log messages, ensuring
compatibility across different environments where color rendering is not supported.

## Using a Logger directly

It's possible to use `Logger` objects directly, and these can be initialized anywhere (very similar to the Python built-in `logging` API).

If you ***aren't*** using an object which already initializes a `NautilusKernel` (and logging) such as `BacktestEngine` or `TradingNode`,
then you can activate logging in the following way:

```python
from nautilus_trader.common.component import init_logging
from nautilus_trader.common.component import Logger

log_guard = init_logging()
logger = Logger("MyLogger")
```

:::info
See the `init_logging` [API Reference](../api_reference/common) for further details.
:::

:::warning
Only one logging subsystem can be initialized per process with an `init_logging` call, and the `LogGuard` which is returned must be kept alive for the lifetime of the program.
:::

## LogGuard: Managing log lifecycle

The `LogGuard` ensures that the logging subsystem remains active and operational throughout the lifecycle of a process.
It prevents premature shutdown of the logging subsystem when running multiple engines in the same process.

### Why use LogGuard?

Without a `LogGuard`, any attempt to run sequential engines in the same process may result in errors such as:

```
Error sending log event: [INFO] ...
```

This occurs because the logging subsystem's underlying channel and Rust `Logger` are closed when the first engine is disposed.
As a result, subsequent engines lose access to the logging subsystem, leading to these errors.

By leveraging a `LogGuard`, you can ensure robust logging behavior across multiple backtests or engine runs in the same process.
The `LogGuard` retains the resources of the logging subsystem and ensures that logs continue to function correctly,
even as engines are disposed and initialized.

:::note
Using `LogGuard` is critical to maintain consistent logging behavior throughout a process with multiple engines.
:::

## Running multiple engines

The following example demonstrates how to use a `LogGuard` when running multiple engines sequentially in the same process:

```python
log_guard = None  # Initialize LogGuard reference

for i in range(number_of_backtests):
    engine = setup_engine(...)

    # Assign reference to LogGuard
    if log_guard is None:
        log_guard = engine.get_log_guard()

    # Add actors and execute the engine
    actors = setup_actors(...)
    engine.add_actors(actors)
    engine.run()
    engine.dispose()  # Dispose safely
```

### Steps

- **Initialize LogGuard once**: The `LogGuard` is obtained from the first engine (`engine.get_log_guard()`) and is retained throughout the process. This ensures that the logging subsystem remains active.
- **Dispose engines safely**: Each engine is safely disposed of after its backtest completes, without affecting the logging subsystem.
- **Reuse LogGuard**: The same `LogGuard` instance is reused for subsequent engines, preventing the logging subsystem from shutting down prematurely.

### Considerations

- **Single LogGuard per process**: Only one `LogGuard` can be used per process.
- **Thread safety**: The logging subsystem, including `LogGuard`, is thread-safe, ensuring consistent behavior even in multi-threaded environments.
- **Flush logs on termination**: Always ensure that logs are properly flushed when the process terminates. The `LogGuard` automatically handles this as it goes out of scope.


---

file path: ./concepts/portfolio.md
# Portfolio

:::info
We are currently working on this concept guide.
:::

The Portfolio serves as the central hub for managing and tracking all positions across active strategies for the trading node or backtest.
It consolidates position data from multiple instruments, providing a unified view of your holdings, risk exposure, and overall performance.
Explore this section to understand how NautilusTrader aggregates and updates portfolio state to support effective trading and risk management.

## Portfolio Statistics

There are a variety of [built-in portfolio statistics](https://github.com/nautechsystems/nautilus_trader/tree/develop/nautilus_trader/analysis/statistics)
which are used to analyse a trading portfolios performance for both backtests and live trading.

The statistics are generally categorized as follows.

- PnLs based statistics (per currency)
- Returns based statistics
- Positions based statistics
- Orders based statistics

It's also possible to call a traders `PortfolioAnalyzer` and calculate statistics at any arbitrary
time, including *during* a backtest, or live trading session.

## Custom Statistics

Custom portfolio statistics can be defined by inheriting from the `PortfolioStatistic`
base class, and implementing any of the `calculate_` methods.

For example, the following is the implementation for the built-in `WinRate` statistic:

```python
import pandas as pd
from typing import Any
from nautilus_trader.analysis.statistic import PortfolioStatistic


class WinRate(PortfolioStatistic):
    """
    Calculates the win rate from a realized PnLs series.
    """

    def calculate_from_realized_pnls(self, realized_pnls: pd.Series) -> Any | None:
        # Preconditions
        if realized_pnls is None or realized_pnls.empty:
            return 0.0

        # Calculate statistic
        winners = [x for x in realized_pnls if x > 0.0]
        losers = [x for x in realized_pnls if x <= 0.0]

        return len(winners) / float(max(1, (len(winners) + len(losers))))
```

These statistics can then be registered with a traders `PortfolioAnalyzer`.

```python
stat = WinRate()

# Register with the portfolio analyzer
engine.portfolio.analyzer.register_statistic(stat)

:::info
See the `PortfolioAnalyzer` [API Reference](../api_reference/analysis.md#class-portfolioanalyzer) for details on available methods.
:::
```

:::tip
Ensure your statistic is robust to degenerate inputs such as ``None``, empty series, or insufficient data.

The expectation is that you would then return ``None``, NaN or a reasonable default.
:::

## Backtest Analysis

Following a backtest run, a performance analysis will be carried out by passing realized PnLs, returns, positions and orders data to each registered
statistic in turn, calculating their values (with a default configuration). Any output is then displayed in the tear sheet
under the `Portfolio Performance` heading, grouped as.

- Realized PnL statistics (per currency)
- Returns statistics (for the entire portfolio)
- General statistics derived from position and order data (for the entire portfolio)


---

file path: ./concepts/data.md
# Data

The NautilusTrader platform provides a set of built-in data types specifically designed to represent a trading domain.
These data types include:

- `OrderBookDelta` (L1/L2/L3): Represents the most granular order book updates.
- `OrderBookDeltas` (L1/L2/L3): Batches multiple order book deltas for more efficient processing.
- `OrderBookDepth10`: Aggregated order book snapshot (up to 10 levels per bid and ask side).
- `QuoteTick`: Represents the best bid and ask prices along with their sizes at the top-of-book.
- `TradeTick`: A single trade/match event between counterparties.
- `Bar`: OHLCV (Open, High, Low, Close, Volume) bar/candle, aggregated using a specified *aggregation method*.
- `InstrumentStatus`: An instrument-level status event.
- `InstrumentClose`: The closing price of an instrument.

NautilusTrader is designed primarily to operate on granular order book data, providing the highest realism
for execution simulations in backtesting.
However, backtests can also be conducted on any of the supported market data types, depending on the desired simulation fidelity.

## Order books

A high-performance order book implemented in Rust is available to maintain order book state based on provided data.

`OrderBook` instances are maintained per instrument for both backtesting and live trading, with the following book types available:

- `L3_MBO`: **Market by order (MBO)** or L3 data, uses every order book event at every price level, keyed by order ID.
- `L2_MBP`: **Market by price (MBP)** or L2 data, aggregates order book events by price level.
- `L1_MBP`: **Market by price (MBP)** or L1 data, also known as best bid and offer (BBO), captures only top-level updates.

:::note
Top-of-book data, such as `QuoteTick`, `TradeTick` and `Bar`, can also be used for backtesting, with markets operating on `L1_MBP` book types.
:::

## Instruments

The following instrument definitions are available:

- `Betting`: Represents an instrument in a betting market.
- `BinaryOption`: Represents a generic binary option instrument.
- `Cfd`: Represents a Contract for Difference (CFD) instrument.
- `Commodity`:  Represents a commodity instrument in a spot/cash market.
- `CryptoFuture`: Represents a deliverable futures contract instrument, with crypto assets as underlying and for settlement.
- `CryptoPerpetual`: Represents a crypto perpetual futures contract instrument (a.k.a. perpetual swap).
- `CurrencyPair`: Represents a generic currency pair instrument in a spot/cash market.
- `Equity`: Represents a generic equity instrument.
- `FuturesContract`: Represents a generic deliverable futures contract instrument.
- `FuturesSpread`: Represents a generic deliverable futures spread instrument.
- `Index`: Represents a generic index instrument.
- `OptionContract`: Represents a generic option contract instrument.
- `OptionSpread`: Represents a generic option spread instrument.
- `Synthetic`: Represents a synthetic instrument with prices derived from component instruments using a formula.

## Bars and aggregation

### Introduction to Bars

A *bar* (also known as a candle, candlestick or kline) is a data structure that represents
price and volume information over a specific period, including:

- Opening price
- Highest price
- Lowest price
- Closing price
- Traded volume (or ticks as a volume proxy)

These bars are generated using an *aggregation method*, which groups data based on specific criteria.

### Purpose of data aggregation

Data aggregation in NautilusTrader transforms granular market data into structured bars or candles for several reasons:

- To provide data for technical indicators and strategy development.
- Because time-aggregated data (like minute bars) are often sufficient for many strategies.
- To reduce costs compared to high-frequency L1/L2/L3 market data.

### Aggregation methods

The platform implements various aggregation methods:

| Name               | Description                                                                | Category     |
|:-------------------|:---------------------------------------------------------------------------|:-------------|
| `TICK`             | Aggregation of a number of ticks.                                          | Threshold    |
| `TICK_IMBALANCE`   | Aggregation of the buy/sell imbalance of ticks.                            | Threshold    |
| `TICK_RUNS`        | Aggregation of sequential buy/sell runs of ticks.                          | Information  |
| `VOLUME`           | Aggregation of traded volume.                                              | Threshold    |
| `VOLUME_IMBALANCE` | Aggregation of the buy/sell imbalance of traded volume.                    | Threshold    |
| `VOLUME_RUNS`      | Aggregation of sequential runs of buy/sell traded volume.                  | Information  |
| `VALUE`            | Aggregation of the notional value of trades (also known as "Dollar bars"). | Threshold    |
| `VALUE_IMBALANCE`  | Aggregation of the buy/sell imbalance of trading by notional value.        | Information  |
| `VALUE_RUNS`       | Aggregation of sequential buy/sell runs of trading by notional value.      | Threshold    |
| `MILLISECOND`      | Aggregation of time intervals with millisecond granularity.                | Time         |
| `SECOND`           | Aggregation of time intervals with second granularity.                     | Time         |
| `MINUTE`           | Aggregation of time intervals with minute granularity.                     | Time         |
| `HOUR`             | Aggregation of time intervals with hour granularity.                       | Time         |
| `DAY`              | Aggregation of time intervals with day granularity.                        | Time         |
| `WEEK`             | Aggregation of time intervals with week granularity.                       | Time         |
| `MONTH`            | Aggregation of time intervals with month granularity.                      | Time         |

### Types of aggregation

NautilusTrader implements three distinct data aggregation methods:

1. **Trade-to-bar aggregation**: Creates bars from `TradeTick` objects (executed trades)
   - Use case: For strategies analyzing execution prices or when working directly with trade data.
   - Always uses the `LAST` price type in the bar specification.

2. **Quote-to-bar aggregation**: Creates bars from `QuoteTick` objects (bid/ask prices)
   - Use case: For strategies focusing on bid/ask spreads or market depth analysis.
   - Uses `BID`, `ASK`, or `MID` price types in the bar specification.

3. **Bar-to-bar aggregation**: Creates larger-timeframe `Bar` objects from smaller-timeframe `Bar` objects
   - Use case: For resampling existing smaller timeframe bars (1-minute) into larger timeframes (5-minute, hourly).
   - Always requires the `@` symbol in the specification.

### Bar types and Components

NautilusTrader defines a unique *bar type* (`BarType` class) based on the following components:

- **Instrument ID** (`InstrumentId`): Specifies the particular instrument for the bar.
- **Bar Specification** (`BarSpecification`):
  - `step`: Defines the interval or frequency of each bar.
  - `aggregation`: Specifies the method used for data aggregation (see the above table).
  - `price_type`: Indicates the price basis of the bar (e.g., bid, ask, mid, last).
- **Aggregation Source** (`AggregationSource`): Indicates whether the bar was aggregated internally (within Nautilus)
- or externally (by a trading venue or data provider).

Bar types can also be classified as either *standard* or *composite*:

- **Standard**: Generated from granular market data, such as quote-ticks or trade-ticks.
- **Composite**: Derived from a higher-granularity bar type through subsampling (like 5-MINUTE bars aggregate from 1-MINUTE bars).

### Aggregation sources

Bar data aggregation can be either *internal* or *external*:

- `INTERNAL`: The bar is aggregated inside the local Nautilus system boundary.
- `EXTERNAL`: The bar is aggregated outside the local Nautilus system boundary (typically by a trading venue or data provider).

For bar-to-bar aggregation, the target bar type is always `INTERNAL` (since you're doing the aggregation within NautilusTrader),
but the source bars can be either `INTERNAL` or `EXTERNAL`, i.e., you can aggregate externally provided bars or already
aggregated internal bars.

### Defining Bar Types with String Syntax

#### Standard bars

You can define standard bar types from strings using the following convention:

`{instrument_id}-{step}-{aggregation}-{price_type}-{INTERNAL | EXTERNAL}`

For example, to define a `BarType` for AAPL trades (last price) on Nasdaq (XNAS) using a 5-minute interval
aggregated from trades locally by Nautilus:

```python
bar_type = BarType.from_str("AAPL.XNAS-5-MINUTE-LAST-INTERNAL")
```

#### Composite bars

Composite bars are derived by aggregating higher-granularity bars into the desired bar type. To define a composite bar,
use this convention:

`{instrument_id}-{step}-{aggregation}-{price_type}-INTERNAL@{step}-{aggregation}-{INTERNAL | EXTERNAL}`

**Notes**:

- The derived bar type must use an `INTERNAL` aggregation source (since this is how the bar is aggregated).
- The sampled bar type must have a higher granularity than the derived bar type.
- The sampled instrument ID is inferred to match that of the derived bar type.
- Composite bars can be aggregated *from* `INTERNAL` or `EXTERNAL` aggregation sources.

For example, to define a `BarType` for AAPL trades (last price) on Nasdaq (XNAS) using a 5-minute interval
aggregated locally by Nautilus, from 1-minute interval bars aggregated externally:

```python
bar_type = BarType.from_str("AAPL.XNAS-5-MINUTE-LAST-INTERNAL@1-MINUTE-EXTERNAL")
```

### Aggregation syntax examples

The `BarType` string format encodes both the target bar type and, optionally, the source data type:

```
{instrument_id}-{step}-{aggregation}-{price_type}-{source}@{step}-{aggregation}-{source}
```

The part after the `@` symbol is optional and only used for bar-to-bar aggregation:

- **Without `@`**: Aggregates from `TradeTick` objects (when price_type is `LAST`) or `QuoteTick` objects (when price_type is `BID`, `ASK`, or `MID`).
- **With `@`**: Aggregates from existing `Bar` objects (specifying the source bar type).

#### Trade-to-bar example

```python
def on_start(self) -> None:
    # Define a bar type for aggregating from TradeTick objects
    # Uses price_type=LAST which indicates TradeTick data as source
    bar_type = BarType.from_str("6EH4.XCME-50-VOLUME-LAST-INTERNAL")

    # Request historical data (will receive bars in on_historical_data handler)
    self.request_bars(bar_type)

    # Subscribe to live data (will receive bars in on_bar handler)
    self.subscribe_bars(bar_type)
```

#### Quote-to-bar example

```python
def on_start(self) -> None:
    # Create 1-minute bars from ASK prices (in QuoteTick objects)
    bar_type_ask = BarType.from_str("6EH4.XCME-1-MINUTE-ASK-INTERNAL")

    # Create 1-minute bars from BID prices (in QuoteTick objects)
    bar_type_bid = BarType.from_str("6EH4.XCME-1-MINUTE-BID-INTERNAL")

    # Create 1-minute bars from MID prices (middle between ASK and BID prices in QuoteTick objects)
    bar_type_mid = BarType.from_str("6EH4.XCME-1-MINUTE-MID-INTERNAL")

    # Request historical data and subscribe to live data
    self.request_bars(bar_type_ask)    # Historical bars processed in on_historical_data
    self.subscribe_bars(bar_type_ask)  # Live bars processed in on_bar
```

#### Bar-to-bar example

```python
def on_start(self) -> None:
    # Create 5-minute bars from 1-minute bars (Bar objects)
    # Format: target_bar_type@source_bar_type
    # Note: price type (LAST) is only needed on the left target side, not on the source side
    bar_type = BarType.from_str("6EH4.XCME-5-MINUTE-LAST-INTERNAL@1-MINUTE-EXTERNAL")

    # Request historical data (processed in on_historical_data(...) handler)
    self.request_bars(bar_type)

    # Subscribe to live updates (processed in on_bar(...) handler)
    self.subscribe_bars(bar_type)
```

#### Advanced bar-to-bar example

You can create complex aggregation chains where you aggregate from already aggregated bars:

```python
# First create 1-minute bars from TradeTick objects (LAST indicates TradeTick source)
primary_bar_type = BarType.from_str("6EH4.XCME-1-MINUTE-LAST-INTERNAL")

# Then create 5-minute bars from 1-minute bars
# Note the @1-MINUTE-INTERNAL part identifying the source bars
intermediate_bar_type = BarType.from_str("6EH4.XCME-5-MINUTE-LAST-INTERNAL@1-MINUTE-INTERNAL")

# Then create hourly bars from 5-minute bars
# Note the @5-MINUTE-INTERNAL part identifying the source bars
hourly_bar_type = BarType.from_str("6EH4.XCME-1-HOUR-LAST-INTERNAL@5-MINUTE-INTERNAL")
```

### Working with Bars: Request vs. Subscribe

NautilusTrader provides two distinct operations for working with bars:

- **`request_bars()`**: Fetches historical data processed by the `on_historical_data()` handler.
- **`subscribe_bars()`**: Establishes a real-time data feed processed by the `on_bar()` handler.

These methods work together in a typical workflow:

1. First, `request_bars()` loads historical data to initialize indicators or state of strategy with past market behavior.
2. Then, `subscribe_bars()` ensures the strategy continues receiving new bars as they form in real-time.

Example usage in `on_start()`:

```python
def on_start(self) -> None:
    # Define bar type
    bar_type = BarType.from_str("6EH4.XCME-5-MINUTE-LAST-INTERNAL")

    # Request historical data to initialize indicators
    # These bars will be delivered to the on_historical_data(...) handler in strategy
    self.request_bars(bar_type)

    # Subscribe to real-time updates
    # New bars will be delivered to the on_bar(...) handler in strategy
    self.subscribe_bars(bar_type)

    # Register indicators to receive bar updates (they will be automatically updated)
    self.register_indicator_for_bars(bar_type, self.my_indicator)
```

Required handlers in your strategy to receive the data:

```python
def on_historical_data(self, data):
    # Processes batches of historical bars from request_bars()
    # Note: indicators registered with register_indicator_for_bars
    # are updated automatically with historical data
    pass

def on_bar(self, bar):
    # Processes individual bars in real-time from subscribe_bars()
    # Indicators registered with this bar type will update automatically and they will be updated before this handler is called
    pass
```

### Historical data requests with aggregation

When requesting historical bars for backtesting or initializing indicators, you can use the `request_bars()` method, which supports both direct requests and aggregation:

```python
# Request raw 1-minute bars (aggregated from TradeTick objects as indicated by LAST price type)
self.request_bars(BarType.from_str("6EH4.XCME-1-MINUTE-LAST-EXTERNAL"))

# Request 5-minute bars aggregated from 1-minute bars
self.request_bars(BarType.from_str("6EH4.XCME-5-MINUTE-LAST-INTERNAL@1-MINUTE-EXTERNAL"))
```

If historical aggregated bars are needed, you can use specialized request `request_aggregated_bars()` method:

```python
# Request bars that are aggregated from historical trade ticks
self.request_aggregated_bars(BarType.from_str("6EH4.XCME-100-VOLUME-LAST-INTERNAL"))

# Request bars that are aggregated from other bars
self.request_aggregated_bars(BarType.from_str("6EH4.XCME-5-MINUTE-LAST-INTERNAL@1-MINUTE-EXTERNAL"))
```

### Common Pitfalls

**Register indicators before requesting data**: Ensure indicators are registered before requesting historical data so they get updated properly.

```python
# Correct order
self.register_indicator_for_bars(bar_type, self.ema)
self.request_bars(bar_type)

# Incorrect order
self.request_bars(bar_type)  # Indicator won't receive historical data
self.register_indicator_for_bars(bar_type, self.ema)
```

## Timestamps

The platform uses two fundamental timestamp fields that appear across many objects, including market data, orders, and events.
These timestamps serve distinct purposes and help maintain precise timing information throughout the system:

- `ts_event`: UNIX timestamp (nanoseconds) representing when an event actually occurred.
- `ts_init`: UNIX timestamp (nanoseconds) representing when Nautilus created the internal object representing that event.

### Examples

| **Event Type**   | **`ts_event`**                                        | **`ts_init`** |
| -----------------| ------------------------------------------------------| --------------|
| `TradeTick`      | Time when trade occurred at the exchange.             | Time when Nautilus received the trade data. |
| `QuoteTick`      | Time when quote occurred at the exchange.             | Time when Nautilus received the quote data. |
| `OrderBookDelta` | Time when order book update occurred at the exchange. | Time when Nautilus received the order book update. |
| `Bar`            | Time of the bar's closing (exact minute/hour).        | Time when Nautilus generated (for internal bars) or received the bar data (for external bars). |
| `OrderFilled`    | Time when order was filled at the exchange.           | Time when Nautilus received and processed the fill confirmation. |
| `OrderCanceled`  | Time when cancellation was processed at the exchange. | Time when Nautilus received and processed the cancellation confirmation. |
| `NewsEvent`      | Time when the news was published.                     | Time when the event object was created (if internal event) or received (if external event) in Nautilus. |
| Custom event     | Time when event conditions actually occurred.         | Time when the event object was created (if internal event) or received (if external event) in Nautilus. |

:::note
The `ts_init` field represents a more general concept than just the "time of reception" for events.
It denotes the timestamp when an object, such as a data point or command, was initialized within Nautilus.
This distinction is important because `ts_init` is not exclusive to "received events" — it applies to any internal
initialization process.

For example, the `ts_init` field is also used for commands, where the concept of reception does not apply.
This broader definition ensures consistent handling of initialization timestamps across various object types in the system.
:::

### Latency analysis

The dual timestamp system enables latency analysis within the platform:

- Latency can be calculated as `ts_init - ts_event`.
- This difference represents total system latency, including network transmission time, processing overhead, and any queueing delays.
- It's important to remember that the clocks producing these timestamps are likely not synchronized.

### Environment specific behavior

#### Backtesting environment

- Data is ordered by `ts_init` using a stable sort.
- This behavior ensures deterministic processing order and simulates realistic system behavior, including latencies.

#### Live trading environment

- Data is processed as it arrives, ensuring minimal latency and allowing for real-time decision-making.
  - `ts_init` field records the exact moment when data is received by Nautilus in real-time.
  - `ts_event` reflects the time the event occurred externally, enabling accurate comparisons between external event timing and system reception.
- We can use the difference between `ts_init` and `ts_event` to detect network or processing delays.

### Other notes and considerations

- For data from external sources, `ts_init` is always the same as or later than `ts_event`.
- For data created within Nautilus, `ts_init` and `ts_event` can be the same because the object is initialized at the same time the event happens.
- Not every type with a `ts_init` field necessarily has a `ts_event` field. This reflects cases where:
  - The initialization of an object happens at the same time as the event itself.
  - The concept of an external event time does not apply.

#### Persisted Data

The `ts_init` field indicates when the message was originally received.

## Data flow

The platform ensures consistency by flowing data through the same pathways across all system [environment contexts](/concepts/architecture.md#environment-contexts)
(e.g., `backtest`, `sandbox`, `live`). Data is primarily transported via the `MessageBus` to the `DataEngine`
and then distributed to subscribed or registered handlers.

For users who need more flexibility, the platform also supports the creation of custom data types.
For details on how to implement user-defined data types, see the [Custom Data](#custom-data) section below.

## Loading data

NautilusTrader facilitates data loading and conversion for three main use cases:

- Providing data for a `BacktestEngine` to run backtests.
- Persisting the Nautilus-specific Parquet format for the data catalog via `ParquetDataCatalog.write_data(...)` to be later used with a `BacktestNode`.
- For research purposes (to ensure data is consistent between research and backtesting).

Regardless of the destination, the process remains the same: converting diverse external data formats into Nautilus data structures.

To achieve this, two main components are necessary:

- A type of DataLoader (normally specific per raw source/format) which can read the data and return a `pd.DataFrame` with the correct schema for the desired Nautilus object
- A type of DataWrangler (specific per data type) which takes this `pd.DataFrame` and returns a `list[Data]` of Nautilus objects

### Data loaders

Data loader components are typically specific for the raw source/format and per integration. For instance, Binance order book data is stored in its raw CSV file form with
an entirely different format to [Databento Binary Encoding (DBN)](https://databento.com/docs/knowledge-base/new-users/dbn-encoding/getting-started-with-dbn) files.

### Data wranglers

Data wranglers are implemented per specific Nautilus data type, and can be found in the `nautilus_trader.persistence.wranglers` module.
Currently there exists:

- `OrderBookDeltaDataWrangler`
- `QuoteTickDataWrangler`
- `TradeTickDataWrangler`
- `BarDataWrangler`

:::warning
There are a number of **DataWrangler v2** components, which will take a `pd.DataFrame` typically
with a different fixed width Nautilus Arrow v2 schema, and output PyO3 Nautilus objects which are only compatible with the new version
of the Nautilus core, currently in development.

**These PyO3 provided data objects are not compatible where the legacy Cython objects are currently used (e.g., adding directly to a `BacktestEngine`).**
:::

### Transformation pipeline

**Process flow**:

1. Raw data (e.g., CSV) is input into the pipeline.
2. DataLoader processes the raw data and converts it into a `pd.DataFrame`.
3. DataWrangler further processes the `pd.DataFrame` to generate a list of Nautilus objects.
4. The Nautilus `list[Data]` is the output of the data loading process.

The following diagram illustrates how raw data is transformed into Nautilus data structures:

```
  ┌──────────┐    ┌──────────────────────┐                  ┌──────────────────────┐
  │          │    │                      │                  │                      │
  │          │    │                      │                  │                      │
  │ Raw data │    │                      │  `pd.DataFrame`  │                      │
  │ (CSV)    ├───►│      DataLoader      ├─────────────────►│     DataWrangler     ├───► Nautilus `list[Data]`
  │          │    │                      │                  │                      │
  │          │    │                      │                  │                      │
  │          │    │                      │                  │                      │
  └──────────┘    └──────────────────────┘                  └──────────────────────┘

```

Concretely, this would involve:

- `BinanceOrderBookDeltaDataLoader.load(...)` which reads CSV files provided by Binance from disk, and returns a `pd.DataFrame`.
- `OrderBookDeltaDataWrangler.process(...)` which takes the `pd.DataFrame` and returns `list[OrderBookDelta]`.

The following example shows how to accomplish the above in Python:

```python
from nautilus_trader import TEST_DATA_DIR
from nautilus_trader.adapters.binance.loaders import BinanceOrderBookDeltaDataLoader
from nautilus_trader.persistence.wranglers import OrderBookDeltaDataWrangler
from nautilus_trader.test_kit.providers import TestInstrumentProvider


# Load raw data
data_path = TEST_DATA_DIR / "binance" / "btcusdt-depth-snap.csv"
df = BinanceOrderBookDeltaDataLoader.load(data_path)

# Set up a wrangler
instrument = TestInstrumentProvider.btcusdt_binance()
wrangler = OrderBookDeltaDataWrangler(instrument)

# Process to a list `OrderBookDelta` Nautilus objects
deltas = wrangler.process(df)
```

## Data catalog

The data catalog is a central store for Nautilus data, persisted in the [Parquet](https://parquet.apache.org) file format.

We have chosen Parquet as the storage format for the following reasons:

- It performs much better than CSV/JSON/HDF5/etc in terms of compression ratio (storage size) and read performance.
- It does not require any separate running components (for example a database).
- It is quick and simple to get up and running with.

The Arrow schemas used for the Parquet format are either single sourced in the core `persistence` Rust crate, or available
from the `/serialization/arrow/schema.py` module.

:::note
2023-10-14: The current plan is to eventually phase out the Python schemas module, so that all schemas are single sourced in the Rust core.
:::

### Initializing

The data catalog can be initialized from a `NAUTILUS_PATH` environment variable, or by explicitly passing in a path like object.

The following example shows how to initialize a data catalog where there is pre-existing data already written to disk at the given path.

```python
from pathlib import Path
from nautilus_trader.persistence.catalog import ParquetDataCatalog


CATALOG_PATH = Path.cwd() / "catalog"

# Create a new catalog instance
catalog = ParquetDataCatalog(CATALOG_PATH)
```

### Writing data

New data can be stored in the catalog, which is effectively writing the given data to disk in the Nautilus-specific Parquet format.
All Nautilus built-in `Data` objects are supported, and any data which inherits from `Data` can be written.

The following example shows the above list of Binance `OrderBookDelta` objects being written:

```python
catalog.write_data(deltas)
```

### Basename template

Nautilus makes no assumptions about how data may be partitioned between files for a particular
data type and instrument ID.

The `basename_template` keyword argument is an additional optional naming component for the output files.
The template should include placeholders that will be filled in with actual values at runtime.
These values can be automatically derived from the data or provided as additional keyword arguments.

For example, using a basename template like `"{date}"` for AUD/USD.SIM quote tick data,
and assuming `"date"` is a provided or derivable field, could result in a filename like
`"2023-01-01.parquet"` under the `"quote_tick/audusd.sim/"` catalog directory.
If not provided, a default naming scheme will be applied. This parameter should be specified as a
keyword argument, like `write_data(data, basename_template="{date}")`.

:::warning
Any data which already exists under a filename will be overwritten.
If a `basename_template` is not provided, then its very likely existing data for the data type and instrument ID will
be overwritten. To prevent data loss, ensure that the `basename_template` (or the default naming scheme)
generates unique filenames for different data sets.
:::

Rust Arrow schema implementations are available for the follow data types (enhanced performance):

- `OrderBookDelta`
- `QuoteTick`
- `TradeTick`
- `Bar`

:::warning
By default any data which already exists under a filename will be overwritten.

You can use one of the following write mode with catalog.write_data:

- CatalogWriteMode.OVERWRITE
- CatalogWriteMode.APPEND
- CatalogWriteMode.PREPEND
- CatalogWriteMode.NEWFILE, which will create a file name of the form `part-{i}.parquet` where `i` is an integer starting at 0.

:::

### Reading data

Any stored data can then be read back into memory:

```python
from nautilus_trader.core.datetime import dt_to_unix_nanos
import pandas as pd
import pytz


start = dt_to_unix_nanos(pd.Timestamp("2020-01-03", tz=pytz.utc))
end =  dt_to_unix_nanos(pd.Timestamp("2020-01-04", tz=pytz.utc))

deltas = catalog.order_book_deltas(instrument_ids=[instrument.id.value], start=start, end=end)
```

### Streaming data

When running backtests in streaming mode with a `BacktestNode`, the data catalog can be used to stream the data in batches.

The following example shows how to achieve this by initializing a `BacktestDataConfig` configuration object:

```python
from nautilus_trader.config import BacktestDataConfig
from nautilus_trader.model import OrderBookDelta


data_config = BacktestDataConfig(
    catalog_path=str(catalog.path),
    data_cls=OrderBookDelta,
    instrument_id=instrument.id,
    start_time=start,
    end_time=end,
)
```

This configuration object can then be passed into a `BacktestRunConfig` and then in turn passed into a `BacktestNode` as part of a run.
See the [Backtest (high-level API)](../getting_started/backtest_high_level.md) tutorial for further details.

## Data migrations

NautilusTrader defines an internal data format specified in the `nautilus_model` crate.
These models are serialized into Arrow record batches and written to Parquet files.
Nautilus backtesting is most efficient when using these Nautilus-format Parquet files.

However, migrating the data model between [precision modes](../getting_started/installation.md#precision-mode) and schema changes can be challenging.
This guide explains how to handle data migrations using our utility tools.

### Migration tools

The `nautilus_persistence` crate provides two key utilities:

#### `to_json`

Converts Parquet files to JSON while preserving metadata:

- Creates two files:

  - `<input>.json`: Contains the deserialized data
  - `<input>.metadata.json`: Contains schema metadata and row group configuration

- Automatically detects data type from filename:

  - `OrderBookDelta` (contains "deltas" or "order_book_delta")
  - `QuoteTick` (contains "quotes" or "quote_tick")
  - `TradeTick` (contains "trades" or "trade_tick")
  - `Bar` (contains "bars")

#### `to_parquet`

Converts JSON back to Parquet format:

- Reads both the data JSON and metadata JSON files
- Preserves row group sizes from original metadata
- Uses ZSTD compression
- Creates `<input>.parquet`

### Migration Process

The following migration examples both use trades data (you can also migrate the other data types in the same way).
All commands should be run from the root of the `persistence` crate directory.

#### Migrating from standard-precision (64-bit) to high-precision (128-bit)

This example describes a scenario where you want to migrate from standard-precision schema to high-precision schema.

:::note
If you're migrating from a catalog that used the `Int64` and `UInt64` Arrow data types for prices and sizes,
be sure to check out commit [e284162](https://github.com/nautechsystems/nautilus_trader/commit/e284162cf27a3222115aeb5d10d599c8cf09cf50)
**before** compiling the code that writes the initial JSON.
:::

**1. Convert from standard-precision Parquet to JSON**:

```bash
cargo run --bin to_json trades.parquet
```

This will create `trades.json` and `trades.metadata.json` files.

**2. Convert from JSON to high-precision Parquet**:

Add the `--features high-precision` flag to write data as high-precision (128-bit) schema Parquet.

```bash
cargo run --features high-precision --bin to_parquet trades.json
```

This will create a `trades.parquet` file with high-precision schema data.

#### Migrating schema changes

This example describes a scenario where you want to migrate from one schema version to another.

**1. Convert from old schema Parquet to JSON**:

Add the `--features high-precision` flag if the source data uses a high-precision (128-bit) schema.

```bash
cargo run --bin to_json trades.parquet
```

This will create `trades.json` and `trades.metadata.json` files.

**2. Switch to new schema version**:

```bash
git checkout <new-version>
```

**3. Convert from JSON back to new schema Parquet**:

```bash
cargo run --features high-precision --bin to_parquet trades.json
```

This will create a `trades.parquet` file with the new schema.

### Best Practices

- Always test migrations with a small dataset first.
- Maintain backups of original files.
- Verify data integrity after migration.
- Perform migrations in a staging environment before applying them to production data.

## Custom Data

Due to the modular nature of the Nautilus design, it is possible to set up systems
with very flexible data streams, including custom user-defined data types. This
guide covers some possible use cases for this functionality.

It's possible to create custom data types within the Nautilus system. First you
will need to define your data by subclassing from `Data`.

:::info
As `Data` holds no state, it is not strictly necessary to call `super().__init__()`.
:::

```python
from nautilus_trader.core import Data


class MyDataPoint(Data):
    """
    This is an example of a user-defined data class, inheriting from the base class `Data`.

    The fields `label`, `x`, `y`, and `z` in this class are examples of arbitrary user data.
    """

    def __init__(
        self,
        label: str,
        x: int,
        y: int,
        z: int,
        ts_event: int,
        ts_init: int,
    ) -> None:
        self.label = label
        self.x = x
        self.y = y
        self.z = z
        self._ts_event = ts_event
        self._ts_init = ts_init

    @property
    def ts_event(self) -> int:
        """
        UNIX timestamp (nanoseconds) when the data event occurred.

        Returns
        -------
        int

        """
        return self._ts_event

    @property
    def ts_init(self) -> int:
        """
        UNIX timestamp (nanoseconds) when the object was initialized.

        Returns
        -------
        int

        """
        return self._ts_init

```

The `Data` abstract base class acts as a contract within the system and requires two properties
for all types of data: `ts_event` and `ts_init`. These represent the UNIX nanosecond timestamps
for when the event occurred and when the object was initialized, respectively.

The recommended approach to satisfy the contract is to assign `ts_event` and `ts_init`
to backing fields, and then implement the `@property` for each as shown above
(for completeness, the docstrings are copied from the `Data` base class).

:::info
These timestamps enable Nautilus to correctly order data streams for backtests
using monotonically increasing `ts_init` UNIX nanoseconds.
:::

We can now work with this data type for backtesting and live trading. For instance,
we could now create an adapter which is able to parse and create objects of this
type - and send them back to the `DataEngine` for consumption by subscribers.

You can publish a custom data type within your actor/strategy using the message bus
in the following way:

```python
self.publish_data(
    DataType(MyDataPoint, metadata={"some_optional_category": 1}),
    MyDataPoint(...),
)
```

The `metadata` dictionary optionally adds more granular information that is used in the
topic name to publish data with the message bus.

Extra metadata information can also be passed to a `BacktestDataConfig` configuration object in order to
enrich and describe custom data objects used in a backtesting context:

```python
from nautilus_trader.config import BacktestDataConfig

data_config = BacktestDataConfig(
    catalog_path=str(catalog.path),
    data_cls=MyDataPoint,
    metadata={"some_optional_category": 1},
)
```

You can subscribe to custom data types within your actor/strategy in the following way:

```python
self.subscribe_data(
    data_type=DataType(MyDataPoint,
    metadata={"some_optional_category": 1}),
    client_id=ClientId("MY_ADAPTER"),
)
```

The `client_id` provides an identifier to route the data subscription to a specific client.

This will result in your actor/strategy passing these received `MyDataPoint`
objects to your `on_data` method. You will need to check the type, as this
method acts as a flexible handler for all custom data.

```python
def on_data(self, data: Data) -> None:
    # First check the type of data
    if isinstance(data, MyDataPoint):
        # Do something with the data
```

### Publishing and receiving signal data

Here is an example of publishing and receiving signal data using the `MessageBus` from an actor or strategy.
A signal is an automatically generated custom data identified by a name containing only one value of a basic type
(str, float, int, bool or bytes).

```python
self.publish_signal("signal_name", value, ts_event)
self.subscribe_signal("signal_name")

def on_signal(self, signal):
    print("Signal", data)
```

### Option Greeks example

This example demonstrates how to create a custom data type for option Greeks, specifically the delta.
By following these steps, you can create custom data types, subscribe to them, publish them, and store
them in the `Cache` or `ParquetDataCatalog` for efficient retrieval.

```python
import msgspec
from nautilus_trader.core import Data
from nautilus_trader.core.datetime import unix_nanos_to_iso8601
from nautilus_trader.model import DataType
from nautilus_trader.serialization.base import register_serializable_type
from nautilus_trader.serialization.arrow.serializer import register_arrow
import pyarrow as pa

from nautilus_trader.model import InstrumentId
from nautilus_trader.core.datetime import dt_to_unix_nanos, unix_nanos_to_dt, format_iso8601


class GreeksData(Data):
    def __init__(
        self, instrument_id: InstrumentId = InstrumentId.from_str("ES.GLBX"),
        ts_event: int = 0,
        ts_init: int = 0,
        delta: float = 0.0,
    ) -> None:
        self.instrument_id = instrument_id
        self._ts_event = ts_event
        self._ts_init = ts_init
        self.delta = delta

    def __repr__(self):
        return (f"GreeksData(ts_init={unix_nanos_to_iso8601(self._ts_init)}, instrument_id={self.instrument_id}, delta={self.delta:.2f})")

    @property
    def ts_event(self):
        return self._ts_event

    @property
    def ts_init(self):
        return self._ts_init

    def to_dict(self):
        return {
            "instrument_id": self.instrument_id.value,
            "ts_event": self._ts_event,
            "ts_init": self._ts_init,
            "delta": self.delta,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return GreeksData(InstrumentId.from_str(data["instrument_id"]), data["ts_event"], data["ts_init"], data["delta"])

    def to_bytes(self):
        return msgspec.msgpack.encode(self.to_dict())

    @classmethod
    def from_bytes(cls, data: bytes):
        return cls.from_dict(msgspec.msgpack.decode(data))

    def to_catalog(self):
        return pa.RecordBatch.from_pylist([self.to_dict()], schema=GreeksData.schema())

    @classmethod
    def from_catalog(cls, table: pa.Table):
        return [GreeksData.from_dict(d) for d in table.to_pylist()]

    @classmethod
    def schema(cls):
        return pa.schema(
            {
                "instrument_id": pa.string(),
                "ts_event": pa.int64(),
                "ts_init": pa.int64(),
                "delta": pa.float64(),
            }
        )
```

#### Publishing and receiving data

Here is an example of publishing and receiving data using the `MessageBus` from an actor or strategy:

```python
register_serializable_type(GreeksData, GreeksData.to_dict, GreeksData.from_dict)

def publish_greeks(self, greeks_data: GreeksData):
    self.publish_data(DataType(GreeksData), greeks_data)

def subscribe_to_greeks(self):
    self.subscribe_data(DataType(GreeksData))

def on_data(self, data):
    if isinstance(GreeksData):
        print("Data", data)
```

#### Writing and reading data using the cache

Here is an example of writing and reading data using the `Cache` from an actor or strategy:

```python
def greeks_key(instrument_id: InstrumentId):
    return f"{instrument_id}_GREEKS"

def cache_greeks(self, greeks_data: GreeksData):
    self.cache.add(greeks_key(greeks_data.instrument_id), greeks_data.to_bytes())

def greeks_from_cache(self, instrument_id: InstrumentId):
    return GreeksData.from_bytes(self.cache.get(greeks_key(instrument_id)))
```

#### Writing and reading data using a catalog

For streaming custom data to feather files or writing it to parquet files in a catalog
(`register_arrow` needs to be used):

```python
register_arrow(GreeksData, GreeksData.schema(), GreeksData.to_catalog, GreeksData.from_catalog)

from nautilus_trader.persistence.catalog import ParquetDataCatalog
catalog = ParquetDataCatalog('.')

catalog.write_data([GreeksData()])
```

### Creating a custom data class automatically

The `@customdataclass` decorator enables the creation of a custom data class with default
implementations for all the features described above.

Each method can also be overridden if needed. Here is an example of its usage:

```python
from nautilus_trader.model.custom import customdataclass


@customdataclass
class GreeksTestData(Data):
    instrument_id: InstrumentId = InstrumentId.from_str("ES.GLBX")
    delta: float = 0.0


GreeksTestData(
    instrument_id=InstrumentId.from_str("CL.GLBX"),
    delta=1000.0,
    ts_event=1,
    ts_init=2,
)
```

#### Custom data type stub

To enhance development convenience and improve code suggestions in your IDE, you can create a `.pyi`
stub file with the proper constructor signature for your custom data types as well as type hints for attributes.
This is particularly useful when the constructor is dynamically generated at runtime, as it allows the IDE to recognize
and provide suggestions for the class's methods and attributes.

For instance, if you have a custom data class defined in `greeks.py`, you can create a corresponding `greeks.pyi` file
with the following constructor signature:

```python
from nautilus_trader.core import Data
from nautilus_trader.model import InstrumentId


class GreeksData(Data):
    instrument_id: InstrumentId
    delta: float

    def __init__(
        self,
        ts_event: int = 0,
        ts_init: int = 0,
        instrument_id: InstrumentId = InstrumentId.from_str("ES.GLBX"),
        delta: float = 0.0,
  ) -> GreeksData: ...
```


---

file path: ./concepts/execution.md
# Execution

NautilusTrader can handle trade execution and order management for multiple strategies and venues
simultaneously (per instance). Several interacting components are involved in execution, making it
crucial to understand the possible flows of execution messages (commands and events).

The main execution-related components include:

- `Strategy`
- `ExecAlgorithm` (execution algorithms)
- `OrderEmulator`
- `RiskEngine`
- `ExecutionEngine` or `LiveExecutionEngine`
- `ExecutionClient` or `LiveExecutionClient`

## Execution flow

The `Strategy` base class inherits from `Actor` and so contains all of the common data related
methods. It also provides methods for managing orders and trade execution:

- `submit_order(...)`
- `submit_order_list(...)`
- `modify_order(...)`
- `cancel_order(...)`
- `cancel_orders(...)`
- `cancel_all_orders(...)`
- `close_position(...)`
- `close_all_positions(...)`
- `query_order(...)`

These methods create the necessary execution commands under the hood and send them on the message
bus to the relevant components (point-to-point), as well as publishing any events (such as the
initialization of new orders i.e. `OrderInitialized` events).

The general execution flow looks like the following (each arrow indicates movement across the message bus):

`Strategy` -> `OrderEmulator` -> `ExecAlgorithm` -> `RiskEngine` -> `ExecutionEngine` -> `ExecutionClient`

The `OrderEmulator` and `ExecAlgorithm`(s) components are optional in the flow, depending on
individual order parameters (as explained below).

This diagram illustrates message flow (commands and events) across the Nautilus execution components.

```
                  ┌───────────────────┐
                  │                   │
                  │                   │
                  │                   │
          ┌───────►   OrderEmulator   ├────────────┐
          │       │                   │            │
          │       │                   │            │
          │       │                   │            │
┌─────────┴──┐    └─────▲──────┬──────┘            │
│            │          │      │           ┌───────▼────────┐   ┌─────────────────────┐   ┌─────────────────────┐
│            │          │      │           │                │   │                     │   │                     │
│            ├──────────┼──────┼───────────►                ├───►                     ├───►                     │
│  Strategy  │          │      │           │                │   │                     │   │                     │
│            │          │      │           │   RiskEngine   │   │   ExecutionEngine   │   │   ExecutionClient   │
│            ◄──────────┼──────┼───────────┤                ◄───┤                     ◄───┤                     │
│            │          │      │           │                │   │                     │   │                     │
│            │          │      │           │                │   │                     │   │                     │
└─────────┬──┘    ┌─────┴──────▼──────┐    └───────▲────────┘   └─────────────────────┘   └─────────────────────┘
          │       │                   │            │
          │       │                   │            │
          │       │                   │            │
          └───────►   ExecAlgorithm   ├────────────┘
                  │                   │
                  │                   │
                  │                   │
                  └───────────────────┘

```

## Order Management System (OMS)

An order management system (OMS) type refers to the method used for assigning orders to positions and tracking those positions for an instrument.
OMS types apply to both strategies and venues (simulated and real). Even if a venue doesn't explicitly
state the method in use, an OMS type is always in effect. The OMS type for a component can be specified
using the `OmsType` enum.

The `OmsType` enum has three variants:

- `UNSPECIFIED`: The OMS type defaults based on where it is applied (details below)
- `NETTING`: Positions are combined into a single position per instrument ID
- `HEDGING`: Multiple positions per instrument ID are supported (both long and short)

The table below describes different configuration combinations and their applicable scenarios.
When the strategy and venue OMS types differ, the `ExecutionEngine` handles this by overriding or assigning `position_id` values for received `OrderFilled` events.
A "virtual position" refers to a position ID that exists within the Nautilus system but not on the venue in
reality.

| Strategy OMS                 | Venue OMS              | Description                                                                                                                                                |
|:-----------------------------|:-----------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| `NETTING`                    | `NETTING`              | The strategy uses the venues native OMS type, with a single position ID per instrument ID.                                                                 |
| `HEDGING`                    | `HEDGING`              | The strategy uses the venues native OMS type, with multiple position IDs per instrument ID (both `LONG` and `SHORT`).                                      |
| `NETTING`                    | `HEDGING`              | The strategy **overrides** the venues native OMS type. The venue tracks multiple positions per instrument ID, but Nautilus maintains a single position ID. |
| `HEDGING`                    | `NETTING`              | The strategy **overrides** the venues native OMS type. The venue tracks a single position per instrument ID, but Nautilus maintains multiple position IDs. |

:::note
Configuring OMS types separately for strategies and venues increases platform complexity but allows
for a wide range of trading styles and preferences (see below).
:::

OMS config examples:

- Most cryptocurrency exchanges use a `NETTING` OMS type, representing a single position per market. It may be desirable for a trader to track multiple "virtual" positions for a strategy.
- Some FX ECNs or brokers use a `HEDGING` OMS type, tracking multiple positions both `LONG` and `SHORT`. The trader may only care about the NET position per currency pair.

:::info
Nautilus does not yet support venue-side hedging modes such as Binance `BOTH` vs. `LONG/SHORT` where the venue nets per direction.
It is advised to keep Binance account configurations as `BOTH` so that a single position is netted.
:::

### OMS configuration

If a strategy OMS type is not explicitly set using the `oms_type` configuration option,
it will default to `UNSPECIFIED`. This means the `ExecutionEngine` will not override any venue `position_id`s,
and the OMS type will follow the venue's OMS type.

:::tip
When configuring a backtest, you can specify the `oms_type` for the venue. To enhance backtest
accuracy, it is recommended to match this with the actual OMS type used by the venue in practice.
:::

## Risk engine

The `RiskEngine` is a core component of every Nautilus system, including backtest, sandbox, and live environments.
Every order command and event passes through the `RiskEngine` unless specifically bypassed in the `RiskEngineConfig`.

The `RiskEngine` includes several built-in pre-trade risk checks, including:

- Price precisions correct for the instrument
- Prices are positive (unless an option type instrument)
- Quantity precisions correct for the instrument
- Below maximum notional for the instrument
- Within maximum or minimum quantity for the instrument
- Only reducing position when a `reduce_only` execution instruction is specified for the order

If any risk check fails, an `OrderDenied` event is generated, effectively closing the order and
preventing it from progressing further. This event includes a human-readable reason for the denial.

### Trading state

Additionally, the current trading state of a Nautilus system affects order flow.

The `TradingState` enum has three variants:

- `ACTIVE`: The system operates normally
- `HALTED`: The system will not process further order commands until the state changes
- `REDUCING`: The system will only process cancels or commands that reduce open positions

:::info
See the `RiskEngineConfig` [API Reference](../api_reference/config#risk) for further details.
:::

## Execution algorithms

The platform supports customized execution algorithm components and provides some built-in
algorithms, such as the Time-Weighted Average Price (TWAP) algorithm.

### TWAP (Time-Weighted Average Price)

The TWAP execution algorithm aims to execute orders by evenly spreading them over a specified
time horizon. The algorithm receives a primary order representing the total size and direction
then splits this by spawning smaller child orders, which are then executed at regular intervals
throughout the time horizon.

This helps to reduce the impact of the full size of the primary order on the market, by
minimizing the concentration of trade size at any given time.

The algorithm will immediately submit the first order, with the final order submitted being the
primary order at the end of the horizon period.

Using the TWAP algorithm as an example (found in ``/examples/algorithms/twap.py``), this example
demonstrates how to initialize and register a TWAP execution algorithm directly with a
`BacktestEngine` (assuming an engine is already initialized):

```python
from nautilus_trader.examples.algorithms.twap import TWAPExecAlgorithm

# `engine` is an initialized BacktestEngine instance
exec_algorithm = TWAPExecAlgorithm()
engine.add_exec_algorithm(exec_algorithm)
```

For this particular algorithm, two parameters must be specified:

- `horizon_secs`
- `interval_secs`

The `horizon_secs` parameter determines the time period over which the algorithm will execute, while
the `interval_secs` parameter sets the time between individual order executions. These parameters
determine how a primary order is split into a series of spawned orders.

```python
from decimal import Decimal
from nautilus_trader.model.data import BarType
from nautilus_trader.test_kit.providers import TestInstrumentProvider
from nautilus_trader.examples.strategies.ema_cross_twap import EMACrossTWAP, EMACrossTWAPConfig

# Configure your strategy
config = EMACrossTWAPConfig(
    instrument_id=TestInstrumentProvider.ethusdt_binance().id,
    bar_type=BarType.from_str("ETHUSDT.BINANCE-250-TICK-LAST-INTERNAL"),
    trade_size=Decimal("0.05"),
    fast_ema_period=10,
    slow_ema_period=20,
    twap_horizon_secs=10.0,   # execution algorithm parameter (total horizon in seconds)
    twap_interval_secs=2.5,    # execution algorithm parameter (seconds between orders)
)

# Instantiate your strategy
strategy = EMACrossTWAP(config=config)
```

Alternatively, you can specify these parameters dynamically per order, determining them based on
actual market conditions. In this case, the strategy configuration parameters could be provided to
an execution model which determines the horizon and interval.

:::info
There is no limit to the number of execution algorithm parameters you can create. The parameters
just need to be a dictionary with string keys and primitive values (values that can be serialized
over the wire, such as ints, floats, and strings).
:::

### Writing execution algorithms

To implement a custom execution algorithm you must define a class which inherits from `ExecAlgorithm`.

An execution algorithm is a type of `Actor`, so it's capable of the following:

- Request and subscribe to data
- Access the `Cache`
- Set time alerts and/or timers using a `Clock`

Additionally it can:

- Access the central `Portfolio`
- Spawn secondary orders from a received primary (original) order

Once an execution algorithm is registered, and the system is running, it will receive orders off the
messages bus which are addressed to its `ExecAlgorithmId` via the `exec_algorithm_id` order parameter.
The order may also carry the `exec_algorithm_params` being a `dict[str, Any]`.

:::warning
Because of the flexibility of the `exec_algorithm_params` dictionary. It's important to thoroughly
validate all of the key value pairs for correct operation of the algorithm (for starters that the
dictionary is not ``None`` and all necessary parameters actually exist).
:::

Received orders will arrive via the following `on_order(...)` method. These received orders are
know as "primary" (original) orders when being handled by an execution algorithm.

```python
from nautilus_trader.model.orders.base import Order

def on_order(self, order: Order) -> None:
    # Handle the order here
```

When the algorithm is ready to spawn a secondary order, it can use one of the following methods:

- `spawn_market(...)` (spawns a `MARKET` order)
- `spawn_market_to_limit(...)` (spawns a `MARKET_TO_LIMIT` order)
- `spawn_limit(...)` (spawns a `LIMIT` order)

:::note
Additional order types will be implemented in future versions, as the need arises.
:::

Each of these methods takes the primary (original) `Order` as the first argument. The primary order
quantity will be reduced by the `quantity` passed in (becoming the spawned orders quantity).

:::warning
There must be enough primary order quantity remaining (this is validated).
:::

Once the desired number of secondary orders have been spawned, and the execution routine is over,
the intention is that the algorithm will then finally send the primary (original) order.

### Spawned orders

All secondary orders spawned from an execution algorithm will carry a `exec_spawn_id` which is
simply the `ClientOrderId` of the primary (original) order, and whose `client_order_id`
derives from this original identifier with the following convention:

- `exec_spawn_id` (primary order `client_order_id` value)
- `spawn_sequence` (the sequence number for the spawned order)

```
{exec_spawn_id}-E{spawn_sequence}
```

e.g. `O-20230404-001-000-E1` (for the first spawned order)

:::note
The "primary" and "secondary" / "spawn" terminology was specifically chosen to avoid conflict
or confusion with the "parent" and "child" contingent orders terminology (an execution algorithm may also deal with contingent orders).
:::

### Managing execution algorithm orders

The `Cache` provides several methods to aid in managing (keeping track of) the activity of
an execution algorithm. Calling the below method will return all execution algorithm orders
for the given query filters.

```python
def orders_for_exec_algorithm(
    self,
    exec_algorithm_id: ExecAlgorithmId,
    venue: Venue | None = None,
    instrument_id: InstrumentId | None = None,
    strategy_id: StrategyId | None = None,
    side: OrderSide = OrderSide.NO_ORDER_SIDE,
) -> list[Order]:
```

As well as more specifically querying the orders for a certain execution series/spawn.
Calling the below method will return all orders for the given `exec_spawn_id` (if found).

```python
def orders_for_exec_spawn(self, exec_spawn_id: ClientOrderId) -> list[Order]:
```

:::note
This also includes the primary (original) order.
:::


---

file path: ./concepts/adapters.md
# Adapters

The NautilusTrader design integrates data providers and/or trading venues
through adapter implementations. These can be found in the top-level `adapters` subpackage.

An integration adapter is *typically* comprised of the following main components:

- `HttpClient`
- `WebSocketClient`
- `InstrumentProvider`
- `DataClient`
- `ExecutionClient`

## Instrument providers

Instrument providers do as their name suggests - instantiating Nautilus
`Instrument` objects by parsing the raw API of the publisher or venue.

The use cases for the instruments available from an `InstrumentProvider` are either:

- Used standalone to discover the instruments available for an integration, using these for research or backtesting purposes
- Used in a `sandbox` or `live` [environment context](architecture.md#environment-contexts) for consumption by actors/strategies

### Research and backtesting

Here is an example of discovering the current instruments for the Binance Futures testnet:

```python
import asyncio
import os

from nautilus_trader.adapters.binance.common.enums import BinanceAccountType
from nautilus_trader.adapters.binance import get_cached_binance_http_client
from nautilus_trader.adapters.binance.futures.providers import BinanceFuturesInstrumentProvider
from nautilus_trader.common.component import LiveClock


clock = LiveClock()
account_type = BinanceAccountType.USDT_FUTURE

client = get_cached_binance_http_client(
    loop=asyncio.get_event_loop(),
    clock=clock,
    account_type=account_type,
    key=os.getenv("BINANCE_FUTURES_TESTNET_API_KEY"),
    secret=os.getenv("BINANCE_FUTURES_TESTNET_API_SECRET"),
    is_testnet=True,
)
await client.connect()

provider = BinanceFuturesInstrumentProvider(
    client=client,
    account_type=BinanceAccountType.USDT_FUTURE,
)

await provider.load_all_async()
```

### Live trading

Each integration is implementation specific, and there are generally two options for the behavior of an `InstrumentProvider` within a `TradingNode` for live trading,
as configured:

- All instruments are automatically loaded on start:

```python
from nautilus_trader.config import InstrumentProviderConfig

InstrumentProviderConfig(load_all=True)
```

- Only those instruments explicitly specified in the configuration are loaded on start:

```python
InstrumentProviderConfig(load_ids=["BTCUSDT-PERP.BINANCE", "ETHUSDT-PERP.BINANCE"])
```

## Data clients

### Requests

An `Actor` or `Strategy` can request custom data from a `DataClient` by sending a `DataRequest`. If the client that receives the
`DataRequest` implements a handler for the request, data will be returned to the `Actor` or `Strategy`.

#### Example

An example of this is a `DataRequest` for an `Instrument`, which the `Actor` class implements (copied below). Any `Actor` or
`Strategy` can call a `request_instrument` method with an `InstrumentId` to request the instrument from a `DataClient`.

In this particular case, the `Actor` implements a separate method `request_instrument`. A similar type of
`DataRequest` could be instantiated and called from anywhere and/or anytime in the actor/strategy code.

A simplified version of `request_instrument` for an actor/strategy is:

```python
# nautilus_trader/common/actor.pyx

cpdef void request_instrument(self, InstrumentId instrument_id, ClientId client_id=None):
    """
    Request `Instrument` data for the given instrument ID.

    Parameters
    ----------
    instrument_id : InstrumentId
        The instrument ID for the request.
    client_id : ClientId, optional
        The specific client ID for the command.
        If ``None`` then will be inferred from the venue in the instrument ID.
    """
    Condition.not_none(instrument_id, "instrument_id")

    cdef RequestInstrument request = RequestInstrument(
        instrument_id=instrument_id,
        start=None,
        end=None,
        client_id=client_id,
        venue=instrument_id.venue,
        callback=self._handle_instrument_response,
        request_id=UUID4(),
        ts_init=self._clock.timestamp_ns(),
        params=None,
    )

    self._send_data_req(request)
```

A simplified version of the request handler implemented in a `LiveMarketDataClient` that will retrieve the data
and send it back to actors/strategies is for example:

```python
# nautilus_trader/live/data_client.py

def request_instrument(self, request: RequestInstrument) -> None:
    self.create_task(self._request_instrument(request))

# nautilus_trader/adapters/binance/data.py

async def _request_instrument(self, request: RequestInstrument) -> None:
    instrument: Instrument | None = self._instrument_provider.find(request.instrument_id)

    if instrument is None:
        self._log.error(f"Cannot find instrument for {request.instrument_id}")
        return

    self._handle_instrument(instrument, request.id, request.params)
```

The `DataEngine` which is an important component in Nautilus links a request with a `DataClient`.
For example a simplified version of handling an instrument request is:

```python
# nautilus_trader/data/engine.pyx

self._msgbus.register(endpoint="DataEngine.request", handler=self.request)

cpdef void request(self, RequestData request):
    self._handle_request(request)

cpdef void _handle_request(self, RequestData request):
    cdef DataClient client = self._clients.get(request.client_id)

    if client is None:
        client = self._routing_map.get(request.venue, self._default_client)

    if isinstance(request, RequestInstrument):
        self._handle_request_instrument(client, request)

cpdef void _handle_request_instrument(self, DataClient client, RequestInstrument request):
    client.request_instrument(request)
```


---

file path: ./tutorials/index.md
# Tutorials

The tutorials provide a guided learning experience with a series of comprehensive step-by-step walkthroughs.
Each tutorial targets specific features or workflows, enabling hands-on learning.
From basic tasks to more advanced operations, these tutorials cater to a wide range of skill levels.

:::info
Each tutorial is generated from a Jupyter notebook located in the docs [tutorials directory](https://github.com/nautechsystems/nautilus_trader/tree/develop/docs/tutorials). These notebooks serve as valuable learning aids and let you execute the code interactively.
:::

:::tip

- Make sure you are using the tutorial docs that match your NautilusTrader version:
- **Latest**: These docs are built from the HEAD of the `master` branch and work with the latest stable release. See <https://nautilustrader.io/docs/latest/tutorials/>.
- **Nightly**: These docs are built from the HEAD of the `nightly` branch and work with bleeding-edge and experimental features. See <https://nautilustrader.io/docs/nightly/tutorials/>.

:::

## Running in docker

Alternatively, a self-contained dockerized Jupyter notebook server is available for download, which does not require any setup or
installation. This is the fastest way to get up and running to try out NautilusTrader. Bear in mind that any data will be
deleted when the container is deleted.

- To get started, install docker:
  - Go to [docker.com](https://docs.docker.com/get-docker/) and follow the instructions
- From a terminal, download the latest image
  - `docker pull ghcr.io/nautechsystems/jupyterlab:nightly --platform linux/amd64`
- Run the docker container, exposing the Jupyter port:
  - `docker run -p 8888:8888 ghcr.io/nautechsystems/jupyterlab:nightly`
- When the container starts, a URL with an access token will be printed in the terminal. Copy that URL and open it in your browser, for example:
  - <http://localhost:8888>

:::info
NautilusTrader currently exceeds the rate limit for Jupyter notebook logging (stdout output),
this is why `log_level` in the examples is set to `ERROR`. If you lower this level to see
more logging then the notebook will hang during cell execution. A fix is currently
being investigated which involves either raising the configured rate limits for
Jupyter, or throttling the log flushing from Nautilus.

- <https://github.com/jupyterlab/jupyterlab/issues/12845>
- <https://github.com/deshaw/jupyterlab-limit-output>

:::


---

file path: ./developer_guide/environment_setup.md
# Environment Setup

For development we recommend using the PyCharm *Professional* edition IDE, as it interprets Cython syntax. Alternatively, you could use Visual Studio Code with a Cython extension.

[uv](https://docs.astral.sh/uv) is the preferred tool for handling all Python virtual environments and dependencies.

[pre-commit](https://pre-commit.com/) is used to automatically run various checks, auto-formatters and linting tools at commit.

NautilusTrader uses increasingly more [Rust](https://www.rust-lang.org), so Rust should be installed on your system as well
([installation guide](https://www.rust-lang.org/tools/install)).

:::info
NautilusTrader *must* compile and run on **Linux, macOS, and Windows**. Please keep portability in
mind (use `std::path::Path`, avoid Bash-isms in shell scripts, etc.).
:::

## Setup

The following steps are for UNIX-like systems, and only need to be completed once.

1. Follow the [installation guide](../getting_started/installation.md) to set up the project with a modification to the final command to install development and test dependencies:

```bash
uv sync --active --all-groups --all-extras
```

or

```bash
make install
```

If you're developing and iterating frequently, then compiling in debug mode is often sufficient and *significantly* faster than a fully optimized build.
To install in debug mode, use:

```bash
make install-debug
```

2. Set up the pre-commit hook which will then run automatically at commit:

```bash
pre-commit install
```

Before opening a pull-request run the formatting and lint suite locally so that CI passes on the
first attempt:

```bash
make format
make pre-commit
```

Make sure the Rust compiler reports **zero errors** – broken builds slow everyone down.

3. **Optional**: For frequent Rust development, configure the `PYO3_PYTHON` variable in `.cargo/config.toml` with the path to the Python interpreter. This helps reduce recompilation times for IDE/rust-analyzer based `cargo check`:

```bash
PYTHON_PATH=$(which python)
echo -e "\n[env]\nPYO3_PYTHON = \"$PYTHON_PATH\"" >> .cargo/config.toml
```

Since `.cargo/config.toml` is tracked, configure git to skip any local modifications:

```bash
git update-index --skip-worktree .cargo/config.toml
```

To restore tracking: `git update-index --no-skip-worktree .cargo/config.toml`

## Builds

Following any changes to `.rs`, `.pyx` or `.pxd` files, you can re-compile by running:

```bash
uv run --no-sync python build.py
```

or

```bash
make build
```

If you're developing and iterating frequently, then compiling in debug mode is often sufficient and *significantly* faster than a fully optimized build.
To compile in debug mode, use:

```bash
make build-debug
```

## Faster builds 🏁

The cranelift backends reduces build time significantly for dev, testing and IDE checks. However, cranelift is available on the nightly toolchain and needs extra configuration. Install the nightly toolchain

```
rustup install nightly
rustup override set nightly
rustup component add rust-analyzer # install nightly lsp
rustup override set stable # reset to stable
```

Activate the nightly feature and use "cranelift" backend for dev and testing profiles in workspace `Cargo.toml`. You can apply the below patch using `git apply <patch>`. You can remove it using `git apply -R <patch>` before pushing changes.

```
diff --git a/Cargo.toml b/Cargo.toml
index 62b78cd8d0..beb0800211 100644
--- a/Cargo.toml
+++ b/Cargo.toml
@@ -1,3 +1,6 @@
+# This line needs to come before anything else in Cargo.toml
+cargo-features = ["codegen-backend"]
+
 [workspace]
 resolver = "2"
 members = [
@@ -140,6 +143,7 @@ lto = false
 panic = "unwind"
 incremental = true
 codegen-units = 256
+codegen-backend = "cranelift"

 [profile.test]
 opt-level = 0
@@ -150,11 +154,13 @@ strip = false
 lto = false
 incremental = true
 codegen-units = 256
+codegen-backend = "cranelift"

 [profile.nextest]
 inherits = "test"
 debug = false # Improves compile times
 strip = "debuginfo" # Improves compile times
+codegen-backend = "cranelift"

 [profile.release]
 opt-level = 3
```

Pass `RUSTUP_TOOLCHAIN=nightly` when running `make build-debug` like commands and include it in in all [rust analyzer settings](#rust-analyzer-settings) for faster builds and IDE checks.

## Services

You can use `docker-compose.yml` file located in `.docker` directory
to bootstrap the Nautilus working environment. This will start the following services:

```bash
docker-compose up -d
```

If you only want specific services running (like `postgres` for example), you can start them with command:

```bash
docker-compose up -d postgres
```

Used services are:

- `postgres`: Postgres database with root user `POSTRES_USER` which defaults to `postgres`, `POSTGRES_PASSWORD` which defaults to `pass` and `POSTGRES_DB` which defaults to `postgres`.
- `redis`: Redis server.
- `pgadmin`: PgAdmin4 for database management and administration.

:::info
Please use this as development environment only. For production, use a proper and more secure setup.
:::

After the services has been started, you must log in with `psql` cli to create `nautilus` Postgres database.
To do that you can run, and type `POSTGRES_PASSWORD` from docker service setup

```bash
psql -h localhost -p 5432 -U postgres
```

After you have logged in as `postgres` administrator, run `CREATE DATABASE` command with target db name (we use `nautilus`):

```
psql (16.2, server 15.2 (Debian 15.2-1.pgdg110+1))
Type "help" for help.

postgres=# CREATE DATABASE nautilus;
CREATE DATABASE

```

## Nautilus CLI Developer Guide

## Introduction

The Nautilus CLI is a command-line interface tool for interacting with the NautilusTrader ecosystem.
It offers commands for managing the PostgreSQL database and handling various trading operations.

:::note
The Nautilus CLI command is only supported on UNIX-like systems.
:::

## Install

You can install the Nautilus CLI using the below Makefile target, which leverages `cargo install` under the hood.
This will place the nautilus binary in your system's PATH, assuming Rust's `cargo` is properly configured.

```bash
make install-cli
```

## Commands

You can run `nautilus --help` to view the CLI structure and available command groups:

### Database

These commands handle bootstrapping the PostgreSQL database.
To use them, you need to provide the correct connection configuration,
either through command-line arguments or a `.env` file located in the root directory or the current working directory.

- `--host` or `POSTGRES_HOST` for the database host
- `--port` or `POSTGRES_PORT` for the database port
- `--user` or `POSTGRES_USER` for the root administrator (typically the postgres user)
- `--password` or `POSTGRES_PASSWORD` for the root administrator's password
- `--database` or `POSTGRES_DATABASE` for both the database **name and the new user** with privileges to that database
    (e.g., if you provide `nautilus` as the value, a new user named nautilus will be created with the password from `POSTGRES_PASSWORD`, and the `nautilus` database will be bootstrapped with this user as the owner).

Example of `.env` file

```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=pass
POSTGRES_DATABASE=nautilus
```

List of commands are:

1. `nautilus database init`: Will bootstrap schema, roles and all sql files located in `schema` root directory (like `tables.sql`).
2. `nautilus database drop`: Will drop all tables, roles and data in target Postgres database.

## Rust analyzer settings

Rust analyzer is a popular language server for Rust and has integrations for many IDEs. It is recommended to configure rust analyzer to have same environment variables as `make build-debug` for faster compile times. Below tested configurations for VSCode and Astro Nvim are provided. For more information see [PR](https://github.com/nautechsystems/nautilus_trader/pull/2524) or rust analyzer [config docs](https://rust-analyzer.github.io/book/configuration.html).

### VSCode

You can add the following settings to your VSCode `settings.json` file:

```
    "rust-analyzer.restartServerOnConfigChange": true,
    "rust-analyzer.linkedProjects": [
        "Cargo.toml"
    ],
    "rust-analyzer.cargo.features": "all",
    "rust-analyzer.check.workspace": false,
    "rust-analyzer.check.extraEnv": {
        "VIRTUAL_ENV": "<path-to-your-virtual-environment>/.venv",
        "CC": "clang",
        "CXX": "clang++"
    },
    "rust-analyzer.cargo.extraEnv": {
        "VIRTUAL_ENV": "<path-to-your-virtual-environment>/.venv",
        "CC": "clang",
        "CXX": "clang++"
    },
    "rust-analyzer.runnables.extraEnv": {
        "VIRTUAL_ENV": "<path-to-your-virtual-environment>/.venv",
        "CC": "clang",
        "CXX": "clang++"
    },
    "rust-analyzer.check.features": "all",
    "rust-analyzer.testExplorer": true
```

### Astro Nvim (Neovim + AstroLSP)

You can add the following to your astro lsp config file:

```
    config = {
      rust_analyzer = {
        settings = {
          ["rust-analyzer"] = {
            restartServerOnConfigChange = true,
            linkedProjects = { "Cargo.toml" },
            cargo = {
              features = "all",
              extraEnv = {
                VIRTUAL_ENV = "<path-to-your-virtual-environment>/.venv",
                CC = "clang",
                CXX = "clang++",
              },
            },
            check = {
              workspace = false,
              command = "check",
              features = "all",
              extraEnv = {
                VIRTUAL_ENV = "<path-to-your-virtual-environment>/.venv",
                CC = "clang",
                CXX = "clang++",
              },
            },
            runnables = {
              extraEnv = {
                VIRTUAL_ENV = "<path-to-your-virtual-environment>/.venv",
                CC = "clang",
                CXX = "clang++",
              },
            },
            testExplorer = true,
          },
        },
      },
```


---

file path: ./developer_guide/cython.md
# Cython

Here you will find guidance and tips for working on NautilusTrader using the Cython language.
More information on Cython syntax and conventions can be found by reading the [Cython docs](https://cython.readthedocs.io/en/latest/index.html).

## What is Cython?

Cython is a superset of Python that compiles to C extension modules, enabling optional static typing and optimized performance. NautilusTrader relies on Cython for its Python bindings and performance-critical components.

## Function and method signatures

Ensure that all functions and methods returning `void` or a primitive C type (such as `bint`, `int`, `double`) include the `except *` keyword in the signature.

This will ensure Python exceptions are not ignored, and instead are “bubbled up” to the caller as expected.

## Debugging

### PyCharm

Improved debugging support for Cython has remained a highly up-voted PyCharm
feature for many years. Unfortunately, it's safe to assume that PyCharm will not
be receiving first class support for Cython debugging
<https://youtrack.jetbrains.com/issue/PY-9476>.

### Cython Docs

The following recommendations are contained in the Cython docs:
<https://cython.readthedocs.io/en/latest/src/userguide/debugging.html>

The summary is it involves manually running a specialized version of `gdb` from the command line.
We don't recommend this workflow.

### Tips

When debugging and seeking to understand a complex system such as NautilusTrader, it can be
quite helpful to step through the code with a debugger. With this not being available
for the Cython part of the codebase, there are a few things which can help:

- Ensure `LogLevel.DEBUG` is configured for the backtesting or live system you are debugging.
  This is available on `BacktestEngineConfig(logging=LoggingConfig(log_level="DEBUG"))` or `TradingNodeConfig(logging=LoggingConfig=log_level="DEBUG"))`.
  With `DEBUG` mode active you will see more granular and verbose log traces which could be what you need to understand the flow.
- Beyond this, if you still require more granular visibility around a part of the system, we recommend some well-placed calls
  to a components logger (normally `self._log.debug(f"HERE {variable}"` is enough).


---

file path: ./developer_guide/docs.md
# Documentation Style Guide

This guide outlines the style conventions and best practices for writing documentation for NautilusTrader.

## General Principles

- We favor simplicity over complexity, less is more.
- We favor concise yet readable prose and documentation.
- We value standardization in conventions, style, patterns, etc.
- Documentation should be accessible to users of varying technical backgrounds.

## Markdown Tables

### Column Alignment and Spacing

- Use symmetrical column widths based on the space necessary dictated by the widest content in each column.
- Align column separators (`|`) vertically for better readability.
- Use consistent spacing around cell content.

### Notes and Descriptions

- All notes and descriptions should have terminating periods.
- Keep notes concise but informative.
- Use sentence case (capitalize only the first letter and proper nouns).

### Example

```markdown
| Order Type             | Spot | Margin | USDT Futures | Coin Futures | Notes                   |
|------------------------|------|--------|--------------|--------------|-------------------------|
| `MARKET`               | ✓    | ✓      | ✓            | ✓            |                         |
| `STOP_MARKET`          | -    | ✓      | ✓            | ✓            | Not supported for Spot. |
| `MARKET_IF_TOUCHED`    | -    | -      | ✓            | ✓            | Futures only.           |
```

### Support Indicators

- Use `✓` for supported features.
- Use `-` for unsupported features (not `✗` or other symbols).
- When adding notes for unsupported features, emphasize with italics: `*Not supported*`.
- Leave cells empty when no content is needed.

## Code References

- Use backticks for inline code, method names, class names, and configuration options.
- Use code blocks for multi-line examples.
- When referencing functions or code locations, include the pattern `file_path:line_number` to allow easy navigation.

## Headings

- Use title case for main headings (## Level 2).
- Use sentence case for subheadings (### Level 3 and below).
- Ensure proper heading hierarchy (don't skip levels).

## Lists

- Use hyphens (`-`) for unordered-list bullets; avoid `*` or `+` to keep the Markdown style
   consistent across the project.
- Use numbered lists only when order matters.
- Maintain consistent indentation for nested lists.
- End list items with periods when they are complete sentences.

## Links and References

- Use descriptive link text (avoid "click here" or "this link").
- Reference external documentation when appropriate.
- Ensure all internal links are relative and accurate.

## Technical Terminology

- Base capability matrices on the Nautilus domain model, not exchange-specific terminology.
- Mention exchange-specific terms in parentheses or notes when necessary for clarity.
- Use consistent terminology throughout the documentation.

## Examples and Code Samples

- Provide practical, working examples.
- Include necessary imports and context.
- Use realistic variable names and values.
- Add comments to explain non-obvious parts of examples.

## Warnings and Notes

- Use appropriate admonition blocks for important information:
  - `:::note` for general information.
  - `:::warning` for important caveats.
  - `:::tip` for helpful suggestions.

## API Documentation

- Document parameters and return types clearly.
- Include usage examples for complex APIs.
- Explain any side effects or important behavior.
- Keep parameter descriptions concise but complete.


---

file path: ./developer_guide/packaged_data.md
# Packaged Data

Various data is contained internally in the `tests/test_kit/data` folder.

## Libor Rates

The libor rates for 1 month USD can be updated by downloading the CSV data from <https://fred.stlouisfed.org/series/USD1MTD156N>.

Ensure you select `Max` for the time window.

## Short Term Interest Rates

The interbank short term interest rates can be updated by downloading the CSV data at <https://data.oecd.org/interest/short-term-interest-rates.htm>.

## Economic Events

The economic events can be updated from downloading the CSV data from fxstreet <https://www.fxstreet.com/economic-calendar>.

Ensure timezone is set to GMT.

A maximum 3 month range can be filtered and so yearly quarters must be downloaded manually and stitched together into a single CSV.
Use the calendar icon to filter the data in the following way;

- 01/01/xx - 31/03/xx
- 01/04/xx - 30/06/xx
- 01/07/xx - 30/09/xx
- 01/10/xx - 31/12/xx

Download each CSV.


---

file path: ./developer_guide/index.md
# Developer Guide

Welcome to the developer guide for NautilusTrader!

Here you'll find guidance on developing and extending NautilusTrader to meet your trading needs or to contribute improvements back to the project.

We believe in using the right tool for the job. The overall design philosophy is to fully utilize
the high level power of Python, with its rich eco-system of frameworks and libraries, whilst
overcoming some of its inherent shortcomings in performance and lack of built-in type safety
(with it being an interpreted dynamic language).

One of the advantages of Cython is that allocation and freeing of memory is handled by the C code
generator during the ‘cythonization’ step of the build (unless you’re specifically utilizing some of
its lower level features).

This approach combines Python’s simplicity with near-native C performance via compiled extensions.

The main development and runtime environment we are working in is of course Python. With the
introduction of Cython syntax throughout the production codebase in `.pyx` and `.pxd` files - it’s
important to be aware of how the CPython implementation of Python interacts with the underlying
CPython API, and the NautilusTrader C extension modules which Cython produces.

We recommend a thorough review of the [Cython docs](https://cython.readthedocs.io/en/latest/) to familiarize yourself with some of its core
concepts, and where C typing is being introduced.

It's not necessary to become a C language expert, however it's helpful to understand how Cython C
syntax is used in function and method definitions, in local code blocks, and the common primitive C
types and how these map to their corresponding `PyObject` types.

## Contents

- [Environment Setup](environment_setup.md)
- [Coding Standards](coding_standards.md)
- [Cython](cython.md)
- [Rust](rust.md)
- [Docs](docs.md)
- [Testing](testing.md)
- [Adapters](adapters.md)
- [Benchmarking](benchmarking.md)
- [Packaged Data](packaged_data.md)


---

file path: ./developer_guide/rust.md
# Rust Style Guide

The [Rust](https://www.rust-lang.org/learn) programming language is an ideal fit for implementing the mission-critical core of the platform and systems. Its strong type system, ownership model, and compile-time checks eliminate memory errors and data races by construction, while zero-cost abstractions and the absence of a garbage collector deliver C-like performance—critical for high-frequency trading workloads.

## Python Bindings

Python bindings are provided via Cython and [PyO3](https://pyo3.rs), allowing users to import NautilusTrader crates directly in Python without a Rust toolchain.

## Code Style and Conventions

### File Header Requirements

All Rust files must include the standardized copyright header:

```rust
// -------------------------------------------------------------------------------------------------
//  Copyright (C) 2015-2025 Nautech Systems Pty Ltd. All rights reserved.
//  https://nautechsystems.io
//
//  Licensed under the GNU Lesser General Public License Version 3.0 (the "License");
//  You may not use this file except in compliance with the License.
//  You may obtain a copy of the License at https://www.gnu.org/licenses/lgpl-3.0.en.html
//
//  Unless required by applicable law or agreed to in writing, software
//  distributed under the License is distributed on an "AS IS" BASIS,
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
//  limitations under the License.
// -------------------------------------------------------------------------------------------------
```

### Code Formatting

Import formatting is automatically handled by rustfmt when running `make format`.
The tool organizes imports into groups (standard library, external crates, local imports) and sorts them alphabetically within each group.

#### Function spacing

- Leave **one blank line between functions** (including tests) – this improves readability and
mirrors the default behavior of `rustfmt`.
- Leave **one blank line above every doc comment** (`///` or `//!`) so that the comment is clearly
  detached from the previous code block.

#### PyO3 naming convention

When exposing Rust functions to Python **via PyO3**:

1. The Rust symbol **must** be prefixed with `py_*` to make its purpose explicit inside the Rust
   codebase.
2. Use the `#[pyo3(name = "…")]` attribute to publish the *Python* name **without** the `py_`
   prefix so the Python API remains clean.

```rust
#[pyo3(name = "do_something")]
pub fn py_do_something() -> PyResult<()> {
    // …
}
```

### Error Handling

Use structured error handling patterns consistently:

1. **Primary Pattern**: Use `anyhow::Result<T>` for fallible functions:

   ```rust
   pub fn calculate_balance(&mut self) -> anyhow::Result<Money> {
       // Implementation
   }
   ```

2. **Custom Error Types**: Use `thiserror` for domain-specific errors:

   ```rust
   #[derive(Error, Debug)]
   pub enum NetworkError {
       #[error("Connection failed: {0}")]
       ConnectionFailed(String),
       #[error("Timeout occurred")]
       Timeout,
   }
   ```

3. **Error Propagation**: Use the `?` operator for clean error propagation.

4. **Error Creation**: Prefer `anyhow::bail!` for early returns with errors:

   ```rust
   // Preferred - using bail! for early returns
   pub fn process_value(value: i32) -> anyhow::Result<i32> {
       if value < 0 {
           anyhow::bail!("Value cannot be negative: {value}");
       }
       Ok(value * 2)
   }

   // Instead of - verbose return statement
   if value < 0 {
       return Err(anyhow::anyhow!("Value cannot be negative: {value}"));
   }
   ```

   **Note**: Use `anyhow::bail!` for early returns, but `anyhow::anyhow!` in closure contexts like `ok_or_else()` where early returns aren't possible.

5. **Error Message Formatting**: Prefer inline format strings over positional arguments:

   ```rust
   // Preferred - inline format with variable names
   anyhow::bail!("Failed to subtract {n} months from {datetime}");

   // Instead of - positional arguments
   anyhow::bail!("Failed to subtract {} months from {}", n, datetime);
   ```

   This makes error messages more readable and self-documenting, especially when there are multiple variables.

### Attribute Patterns

Consistent attribute usage and ordering:

```rust
#[repr(C)]
#[derive(Clone, Copy, Debug, Hash, PartialEq, Eq, PartialOrd, Ord)]
#[cfg_attr(
    feature = "python",
    pyo3::pyclass(module = "nautilus_trader.core.nautilus_pyo3.model")
)]
pub struct Symbol(Ustr);
```

For enums with extensive derive attributes:

```rust
#[repr(C)]
#[derive(
    Copy,
    Clone,
    Debug,
    Display,
    Hash,
    PartialEq,
    Eq,
    PartialOrd,
    Ord,
    AsRefStr,
    FromRepr,
    EnumIter,
    EnumString,
)]
#[strum(ascii_case_insensitive)]
#[strum(serialize_all = "SCREAMING_SNAKE_CASE")]
#[cfg_attr(
    feature = "python",
    pyo3::pyclass(eq, eq_int, module = "nautilus_trader.core.nautilus_pyo3.model.enums")
)]
pub enum AccountType {
    /// An account with unleveraged cash assets only.
    Cash = 1,
    /// An account which facilitates trading on margin, using account assets as collateral.
    Margin = 2,
}
```

### Constructor Patterns

Use the `new()` vs `new_checked()` convention consistently:

```rust
/// Creates a new [`Symbol`] instance with correctness checking.
///
/// # Errors
///
/// Returns an error if `value` is not a valid string.
///
/// # Notes
///
/// PyO3 requires a `Result` type for proper error handling and stacktrace printing in Python.
pub fn new_checked<T: AsRef<str>>(value: T) -> anyhow::Result<Self> {
    // Implementation
}

/// Creates a new [`Symbol`] instance.
///
/// # Panics
///
/// Panics if `value` is not a valid string.
pub fn new<T: AsRef<str>>(value: T) -> Self {
    Self::new_checked(value).expect(FAILED)
}
```

Always use the `FAILED` constant for `.expect()` messages related to correctness checks:

```rust
use nautilus_core::correctness::FAILED;
```

### Constants and Naming Conventions

Use SCREAMING_SNAKE_CASE for constants with descriptive names:

```rust
/// Number of nanoseconds in one second.
pub const NANOSECONDS_IN_SECOND: u64 = 1_000_000_000;

/// Bar specification for 1-minute last price bars.
pub const BAR_SPEC_1_MINUTE_LAST: BarSpecification = BarSpecification {
    step: NonZero::new(1).unwrap(),
    aggregation: BarAggregation::Minute,
    price_type: PriceType::Last,
};
```

### Re-export Patterns

Organize re-exports alphabetically and place at the end of lib.rs files:

```rust
// Re-exports
pub use crate::{
    nanos::UnixNanos,
    time::AtomicTime,
    uuid::UUID4,
};

// Module-level re-exports
pub use crate::identifiers::{
    account_id::AccountId,
    actor_id::ActorId,
    client_id::ClientId,
};
```

### Documentation Standards

#### Module-Level Documentation

All modules must have module-level documentation starting with a brief description:

```rust
//! Functions for correctness checks similar to the *design by contract* philosophy.
//!
//! This module provides validation checking of function or method conditions.
//!
//! A condition is a predicate which must be true just prior to the execution of
//! some section of code - for correct behavior as per the design specification.
```

For modules with feature flags, document them clearly:

```rust
//! # Feature flags
//!
//! This crate provides feature flags to control source code inclusion during compilation,
//! depending on the intended use case:
//!
//! - `ffi`: Enables the C foreign function interface (FFI) from [cbindgen](https://github.com/mozilla/cbindgen).
//! - `python`: Enables Python bindings from [PyO3](https://pyo3.rs).
//! - `stubs`: Enables type stubs for use in testing scenarios.
```

#### Field Documentation

All struct and enum fields must have documentation with terminating periods:

```rust
pub struct Currency {
    /// The currency code as an alpha-3 string (e.g., "USD", "EUR").
    pub code: Ustr,
    /// The currency decimal precision.
    pub precision: u8,
    /// The ISO 4217 currency code.
    pub iso4217: u16,
    /// The full name of the currency.
    pub name: Ustr,
    /// The currency type, indicating its category (e.g. Fiat, Crypto).
    pub currency_type: CurrencyType,
}
```

#### Function Documentation

Document all public functions with:

- Purpose and behavior
- Explanation of input argument usage
- Error conditions (if applicable)
- Panic conditions (if applicable)

```rust
/// Returns a reference to the `AccountBalance` for the specified currency, or `None` if absent.
///
/// # Panics
///
/// Panics if `currency` is `None` and `self.base_currency` is `None`.
pub fn base_balance(&self, currency: Option<Currency>) -> Option<&AccountBalance> {
    // Implementation
}
```

#### Errors and Panics Documentation Format

For single line errors and panics documentation, use sentence case with the following convention:

```rust
/// Returns a reference to the `AccountBalance` for the specified currency, or `None` if absent.
///
/// # Errors
///
/// Returns an error if the currency conversion fails.
///
/// # Panics
///
/// Panics if `currency` is `None` and `self.base_currency` is `None`.
pub fn base_balance(&self, currency: Option<Currency>) -> anyhow::Result<Option<&AccountBalance>> {
    // Implementation
}
```

For multi-line errors and panics documentation, use sentence case with bullets and terminating periods:

```rust
/// Calculates the unrealized profit and loss for the position.
///
/// # Errors
///
/// This function will return an error if:
/// - The market price for the instrument cannot be found.
/// - The conversion rate calculation fails.
/// - Invalid position state is encountered.
///
/// # Panics
///
/// This function will panic if:
/// - The instrument ID is invalid or uninitialized.
/// - Required market data is missing from the cache.
/// - Internal state consistency checks fail.
pub fn calculate_unrealized_pnl(&self, market_price: Price) -> anyhow::Result<Money> {
    // Implementation
}
```

#### Safety Documentation Format

For Safety documentation, use the `SAFETY:` prefix followed by a short description explaining why the unsafe operation is valid:

```rust
/// Creates a new instance from raw components without validation.
///
/// # Safety
///
/// The caller must ensure that all input parameters are valid and properly initialized.
pub unsafe fn from_raw_parts(ptr: *const u8, len: usize) -> Self {
    // SAFETY: Caller guarantees ptr is valid and len is correct
    Self {
        data: std::slice::from_raw_parts(ptr, len),
    }
}
```

For inline unsafe blocks, use the `SAFETY:` comment directly above the unsafe code:

```rust
impl Send for MessageBus {
    fn send(&self) {
        // SAFETY: Message bus is not meant to be passed between threads
        unsafe {
            // unsafe operation here
        }
    }
}
```

### Testing Conventions

#### Test Organization

Use consistent test module structure with section separators:

```rust
////////////////////////////////////////////////////////////////////////////////
// Tests
////////////////////////////////////////////////////////////////////////////////
#[cfg(test)]
mod tests {
    use rstest::rstest;
    use super::*;
    use crate::identifiers::{Symbol, stubs::*};

    #[rstest]
    fn test_string_reprs(symbol_eth_perp: Symbol) {
        assert_eq!(symbol_eth_perp.as_str(), "ETH-PERP");
        assert_eq!(format!("{symbol_eth_perp}"), "ETH-PERP");
    }
}
```

#### Parameterized Testing

Use the `rstest` attribute consistently, and for parameterized tests:

```rust
#[rstest]
#[case("AUDUSD", false)]
#[case("AUD/USD", false)]
#[case("CL.FUT", true)]
fn test_symbol_is_composite(#[case] input: &str, #[case] expected: bool) {
    let symbol = Symbol::new(input);
    assert_eq!(symbol.is_composite(), expected);
}
```

#### Test Naming

Use descriptive test names that explain the scenario:

```rust
fn test_sma_with_no_inputs()
fn test_sma_with_single_input()
fn test_symbol_is_composite()
```

## Unsafe Rust

It will be necessary to write `unsafe` Rust code to be able to achieve the value
of interoperating between Cython and Rust. The ability to step outside the boundaries of safe Rust is what makes it possible to
implement many of the most fundamental features of the Rust language itself, just as C and C++ are used to implement
their own standard libraries.

Great care will be taken with the use of Rusts `unsafe` facility - which just enables a small set of additional language features, thereby changing
the contract between the interface and caller, shifting some responsibility for guaranteeing correctness
from the Rust compiler, and onto us. The goal is to realize the advantages of the `unsafe` facility, whilst avoiding *any* undefined behavior.
The definition for what the Rust language designers consider undefined behavior can be found in the [language reference](https://doc.rust-lang.org/stable/reference/behavior-considered-undefined.html).

### Safety Policy

To maintain correctness, any use of `unsafe` Rust must follow our policy:

- If a function is `unsafe` to call, there *must* be a `Safety` section in the documentation explaining why the function is `unsafe`.
and covering the invariants which the function expects the callers to uphold, and how to meet their obligations in that contract.
- Document why each function is `unsafe` in its doc comment's Safety section, and cover all `unsafe` blocks with unit tests.
- Always include a `SAFETY:` comment explaining why the unsafe operation is valid:

```rust
// SAFETY: Message bus is not meant to be passed between threads
#[allow(unsafe_code)]
unsafe impl Send for MessageBus {}
```

## Tooling Configuration

The project uses several tools for code quality:

- **rustfmt**: Automatic code formatting (see `rustfmt.toml`).
- **clippy**: Linting and best practices (see `clippy.toml`).
- **cbindgen**: C header generation for FFI.

## Resources

- [The Rustonomicon](https://doc.rust-lang.org/nomicon/) – The Dark Arts of Unsafe Rust.
- [The Rust Reference – Unsafety](https://doc.rust-lang.org/stable/reference/unsafety.html).
- [Safe Bindings in Rust – Russell Johnston](https://www.abubalay.com/blog/2020/08/22/safe-bindings-in-rust).
- [Google – Rust and C interoperability](https://www.chromium.org/Home/chromium-security/memory-safety/rust-and-c-interoperability/).


---

file path: ./developer_guide/coding_standards.md
# Coding Standards

## Code Style

The current codebase can be used as a guide for formatting conventions.
Additional guidelines are provided below.

### Universal formatting rules

The following applies to **all** source files (Rust, Python, Cython, shell, etc.):

- Use **spaces only**, never hard tab characters.
- Lines should generally stay below **100 characters**; wrap thoughtfully when necessary.
- Prefer American English spelling (`color`, `serialize`, `behavior`).

### Comment conventions

1. Generally leave **one blank line above** every comment block or docstring so it is visually separated from code.
2. Use *sentence case* – capitalize the first letter, keep the rest lowercase unless proper nouns or acronyms.
3. Do not use double spaces after periods.
4. **Single-line comments** *must not* end with a period *unless* the line ends with a URL or inline Markdown link – in those cases leave the punctuation exactly as the link requires.
5. **Multi-line comments** should separate sentences with commas (not period-per-line). The final line *should* end with a period.
6. Keep comments concise; favor clarity and only explain the non-obvious – *less is more*.
7. Avoid emoji symbols in text.

### Doc comment / docstring mood

- **Python** docstrings should be written in the **imperative mood** – e.g. *“Return a cached client.”*
- **Rust** doc comments should be written in the **indicative mood** – e.g. *“Returns a cached client.”*

These conventions align with the prevailing styles of each language ecosystem and make generated
documentation feel natural to end-users.

### Formatting

1. For longer lines of code, and when passing more than a couple of arguments, you should take a new line which aligns at the next logical indent (rather than attempting a hanging 'vanity' alignment off an opening parenthesis). This practice conserves space to the right, ensures important code is more central in view, and is also robust to function/method name changes.

2. The closing parenthesis should be located on a new line, aligned at the logical indent.

3. Also ensure multiple hanging parameters or arguments end with a trailing comma:

```python
long_method_with_many_params(
    some_arg1,
    some_arg2,
    some_arg3,  # <-- trailing comma
)
```

### PEP-8

The codebase generally follows the PEP-8 style guide. Even though C typing is taken advantage of in the Cython parts of the codebase, we still aim to be idiomatic of Python where possible.
One notable departure is that Python truthiness is not always taken advantage of to check if an argument is `None` for everything other than collections.

There are two reasons for this;

1. Cython can generate more efficient C code from `is None` and `is not None`, rather than entering the Python runtime to check the `PyObject` truthiness.

2. As per the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) - it’s discouraged to use truthiness to check if an argument is/is not `None`, when there is a chance an unexpected object could be passed into the function or method which will yield an unexpected truthiness evaluation (which could result in a logical error type bug).

*“Always use if foo is None: (or is not None) to check for a None value. E.g., when testing whether a variable or argument that defaults to None was set to some other value. The other value might be a value that’s false in a boolean context!”*

There are still areas that aren’t performance-critical where truthiness checks for `None` (`if foo is None:` vs `if not foo:`) will be acceptable for clarity.

:::note
Use truthiness to check for empty collections (e.g., `if not my_list:`) rather than comparing explicitly to `None` or empty.
:::

We welcome all feedback on where the codebase departs from PEP-8 for no apparent reason.

## Python Style Guide

### Type Hints

All function and method signatures *must* include comprehensive type annotations:

```python
def __init__(self, config: EMACrossConfig) -> None:
def on_bar(self, bar: Bar) -> None:
def on_save(self) -> dict[str, bytes]:
def on_load(self, state: dict[str, bytes]) -> None:
```

**Generic Types**: Use `TypeVar` for reusable components

```python
T = TypeVar("T")
class ThrottledEnqueuer(Generic[T]):
```

### Docstrings

The [NumPy docstring spec](https://numpydoc.readthedocs.io/en/latest/format.html) is used throughout the codebase.
This needs to be adhered to consistently to ensure the docs build correctly.

**Test method naming**: Descriptive names explaining the scenario:

```python
def test_currency_with_negative_precision_raises_overflow_error(self):
def test_sma_with_no_inputs_returns_zero_count(self):
def test_sma_with_single_input_returns_expected_value(self):
```

### Ruff

[ruff](https://astral.sh/ruff) is utilized to lint the codebase. Ruff rules can be found in the top-level `pyproject.toml`, with ignore justifications typically commented.

### Commit messages

Here are some guidelines for the style of your commit messages:

1. Limit subject titles to 60 characters or fewer. Capitalize subject line and do not end with period.

2. Use 'imperative voice', i.e. the message should describe what the commit will do if applied.

3. Optional: Use the body to explain change. Separate from subject with a blank line. Keep under 100 character width. You can use bullet points with or without terminating periods.

4. Optional: Provide # references to relevant issues or tickets.

5. Optional: Provide any hyperlinks which are informative.


---

file path: ./developer_guide/testing.md
# Testing

The test suite is divided into broad categories of tests including:

- Unit tests
- Integration tests
- Acceptance tests
- Performance tests
- Memory leak tests

The performance tests exist to aid development of performance-critical components.

Tests can be run using [pytest](https://docs.pytest.org), which is our primary test runner. We recommend using parametrized tests and fixtures (e.g., `@pytest.mark.parametrize`) to avoid repetitive code and improve clarity.

## Running Tests

### Python Tests

From the repository root:

```bash
make pytest
# or
uv run --active --no-sync pytest --new-first --failed-first
# or simply
pytest
```

For performance tests:

```bash
make test-performance
# or
uv run --active --no-sync pytest tests/performance_tests --benchmark-disable-gc --codspeed
```

### Rust Tests

```bash
make cargo-test
# or
cargo nextest run --workspace --features "python,ffi,high-precision,defi" --cargo-profile nextest
```

### IDE Integration

- **PyCharm**: Right-click on tests folder or file → "Run pytest"
- **VS Code**: Use the Python Test Explorer extension

## Mocks

Unit tests will often include other components acting as mocks. The intent of this is to simplify
the test suite to avoid extensive use of a mocking framework, although `MagicMock` objects are
currently used in particular cases.

## Code Coverage

Code coverage output is generated using `coverage` and reported using [codecov](https://about.codecov.io/).

High test coverage is a goal for the project however not at the expense of appropriate error
handling, or causing “test induced damage” to the architecture.

There are currently areas of the codebase which are impossible to test unless there is a change to
the production code. For example the last condition check of an if-else block which would catch an
unrecognized value, these should be left in place in case there is a change to the production code - which these checks could then catch.

Other design-time exceptions may also be impossible to test for, and so 100% test coverage is not
the ultimate goal.

### Style guidance

- **Group assertions** where possible – perform all setup/act steps first, then assert expectations together at
  the end of the test to avoid the *act-assert-act* smell.
- Using `unwrap`, `expect`, or direct `panic!`/`assert` calls inside **tests** is acceptable. The
  clarity and conciseness of the test suite outweigh defensive error-handling that is required in
  production code.

## Excluded code coverage

The `pragma: no cover` comments found throughout the codebase [exclude code from test coverage](https://coverage.readthedocs.io/en/coverage-4.3.3/excluding.html).
The reason for their use is to reduce redundant/needless tests just to keep coverage high, such as:

- Asserting an abstract method raises `NotImplementedError` when called.
- Asserting the final condition check of an if-else block when impossible to test (as above).

These tests are expensive to maintain (as they must be kept in line with any refactorings), and
offer little to no benefit in return. The intention is for all abstract method
implementations to be fully covered by tests. Therefore `pragma: no cover` should be judiciously
removed when no longer appropriate, and its use *restricted* to the above cases.

## Debugging Rust Tests

Rust tests can be debugged using the default test configuration.

If you want to run all tests while compiling with debug symbols for later debugging some tests individually,
run `make cargo-test-debug` instead of `make cargo-test`.

In IntellijIdea, to debug parametrised tests starting with `#[rstest]` with arguments defined in the header of the test
you need to modify the run configuration of the test so it looks like
`test --package nautilus-model --lib data::bar::tests::test_get_time_bar_start::case_1`
(remove `-- --exact` at the end of the string and append `::case_n` where `n` is an integer corresponding to
the n-th parametrised test starting at 1).
The reason for this is [here](https://github.com/rust-lang/rust-analyzer/issues/8964#issuecomment-871592851)
(the test is expanded into a module with several functions named `case_n`).
In VSCode, it is possible to directly select which test case to debug.


---

file path: ./developer_guide/benchmarking.md
# Benchmarking

This guide explains how NautilusTrader measures Rust performance, when to
use each tool and the conventions you should follow when adding new benches.

---

## Tooling overview

Nautilus Trader relies on **two complementary benchmarking frameworks**:

| Framework | What is it? | What it measures | When to prefer it |
|-----------|-------------|------------------|-------------------|
| [**Criterion**](https://docs.rs/criterion/latest/criterion/) | Statistical benchmark harness that produces detailed HTML reports and performs outlier detection. | Wall-clock run time with confidence intervals. | End-to-end scenarios, anything slower than ≈100 ns, visual comparisons. |
| [**iai**](https://docs.rs/iai/latest/iai/) | Deterministic micro-benchmark harness that counts retired CPU instructions via hardware counters. | Exact instruction counts (noise-free). | Ultra-fast functions, CI gating via instruction diff. |

Most hot code paths benefit from **both** kinds of measurements.

---

## Directory layout

Each crate keeps its performance tests in a local `benches/` folder:

```text
crates/<crate_name>/
└── benches/
    ├── foo_criterion.rs   # Criterion group(s)
    └── foo_iai.rs         # iai micro benches
```

`Cargo.toml` must list every benchmark explicitly so `cargo bench` discovers
them:

```toml
[[bench]]
name = "foo_criterion"             # file stem in benches/
path = "benches/foo_criterion.rs"
harness = false                    # disable the default libtest harness
```

---

## Writing Criterion benchmarks

1. Perform **all expensive set-up outside** the timing loop (`b.iter`).
2. Wrap inputs/outputs in `black_box` to prevent the optimizer from removing
   work.
3. Group related cases with `benchmark_group!` and set `throughput` or
   `sample_size` when the defaults aren’t ideal.

```rust
use criterion::{black_box, Criterion, criterion_group, criterion_main};

fn bench_my_algo(c: &mut Criterion) {
    let data = prepare_data(); // heavy set-up done once

    c.bench_function("my_algo", |b| {
        b.iter(|| my_algo(black_box(&data)));
    });
}

criterion_group!(benches, bench_my_algo);
criterion_main!(benches);
```

---

## Writing iai benchmarks

`iai` requires functions that take **no parameters** and return a value (which
can be ignored). Keep them as small as possible so the measured instruction
count is meaningful.

```rust
use iai::black_box;

fn bench_add() -> i64 {
    let a = black_box(123);
    let b = black_box(456);
    a + b
}

iai::main!(bench_add);
```

---

## Running benches locally

- **All benches** for every crate: `make cargo-bench` (delegates to `cargo bench`).
- **Single crate**: `cargo bench -p nautilus-core`.
- **Single benchmark file**: `cargo bench -p nautilus-core --bench time`.

Criterion writes HTML reports to `target/criterion/`; open `target/criterion/report/index.html` in your browser.

### Generating a flamegraph

`cargo-flamegraph` (a thin wrapper around Linux `perf`) lets you see a sampled
call-stack profile of a single benchmark.

1. Install once per machine (the crate is called `flamegraph`; it installs a
   `cargo flamegraph` subcommand automatically). Linux requires `perf` to be
   available (`sudo apt install linux-tools-common linux-tools-$(uname -r)` on
   Debian/Ubuntu):

   ```bash
   cargo install flamegraph
   ```

2. Run a specific bench with the symbol-rich `bench` profile:

   ```bash
   # example: the matching benchmark in nautilus-common
   cargo flamegraph --bench matching -p nautilus-common --profile bench
   ```

3. Open the generated `flamegraph.svg` (or `.png`) in your browser and zoom
   into hot paths.

   If you see an error mentioning `perf_event_paranoid` you need to relax the
   kernel’s perf restrictions for the current session (root required):

   ```bash
   sudo sh -c 'echo 1 > /proc/sys/kernel/perf_event_paranoid'
   ```

   A value of `1` is typically enough; set it back to `2` (default) or make
   the change permanent via `/etc/sysctl.conf` if desired.

Because `[profile.bench]` keeps full debug symbols the SVG will show readable
function names without bloating production binaries (which still use
`panic = "abort"` and are built via `[profile.release]`).

> **Note** Benchmark binaries are compiled with the custom `[profile.bench]`
> defined in the workspace `Cargo.toml`.  That profile inherits from
> `release-debugging`, preserving full optimisation *and* debug symbols so that
> tools like `cargo flamegraph` or `perf` produce human-readable stack traces.

---

## Templates

Ready-to-copy starter files live in `docs/dev_templates/`.

- **Criterion**: `criterion_template.rs`
- **iai**: `iai_template.rs`

Copy the template into `benches/`, adjust imports and names, and start measuring!


---

file path: ./developer_guide/adapters.md
# Adapters

## Introduction

This developer guide provides instructions on how to develop an integration adapter for the NautilusTrader platform.
Adapters provide connectivity to trading venues and data providers—translating raw venue APIs into Nautilus’s unified interface and normalized domain model.

## Structure of an adapter

An adapter typically consists of several components:

1. **Instrument Provider**: Supplies instrument definitions
2. **Data Client**: Handles live market data feeds and historical data requests
3. **Execution Client**: Handles order execution and management
4. **Configuration**: Configures the client settings

## Adapter implementation steps

1. Create a new Python subpackage for your adapter
2. Implement the Instrument Provider by inheriting from `InstrumentProvider` and implementing the necessary methods to load instruments
3. Implement the Data Client by inheriting from either the `LiveDataClient` and `LiveMarketDataClient` class as applicable, providing implementations for the required methods
4. Implement the Execution Client by inheriting from `LiveExecutionClient` and providing implementations for the required methods
5. Create configuration classes to hold your adapter’s settings
6. Test your adapter thoroughly to ensure all methods are correctly implemented and the adapter works as expected (see the [Testing Guide](testing.md)).

## Template for building an adapter

Below is a step-by-step guide to building an adapter for a new data provider using the provided template.

### InstrumentProvider

The `InstrumentProvider` supplies instrument definitions available on the venue. This
includes loading all available instruments, specific instruments by ID, and applying filters to the
instrument list.

```python
from nautilus_trader.common.providers import InstrumentProvider
from nautilus_trader.model import InstrumentId

class TemplateInstrumentProvider(InstrumentProvider):
    """
    An example template of an ``InstrumentProvider`` showing the minimal methods which must be implemented for an integration to be complete.
    """

    async def load_all_async(self, filters: dict | None = None) -> None:
        raise NotImplementedError("implement `load_all_async` in your adapter subclass")

    async def load_ids_async(self, instrument_ids: list[InstrumentId], filters: dict | None = None) -> None:
        raise NotImplementedError("implement `load_ids_async` in your adapter subclass")

    async def load_async(self, instrument_id: InstrumentId, filters: dict | None = None) -> None:
        raise NotImplementedError("implement `load_async` in your adapter subclass")
```

**Key Methods**:

- `load_all_async`: Loads all instruments asynchronously, optionally applying filters
- `load_ids_async`: Loads specific instruments by their IDs
- `load_async`: Loads a single instrument by its ID

### DataClient

The `LiveDataClient` handles the subscription and management of data feeds that are not specifically
related to market data. This might include news feeds, custom data streams, or other data sources
that enhance trading strategies but do not directly represent market activity.

```python
from nautilus_trader.live.data_client import LiveDataClient
from nautilus_trader.model import DataType
from nautilus_trader.core import UUID4

class TemplateLiveDataClient(LiveDataClient):
    """
    An example of a ``LiveDataClient`` highlighting the overridable abstract methods.
    """

    async def _connect(self) -> None:
        raise NotImplementedError("implement `_connect` in your adapter subclass")

    async def _disconnect(self) -> None:
        raise NotImplementedError("implement `_disconnect` in your adapter subclass")

    def reset(self) -> None:
        raise NotImplementedError("implement `reset` in your adapter subclass")

    def dispose(self) -> None:
        raise NotImplementedError("implement `dispose` in your adapter subclass")

    async def _subscribe(self, data_type: DataType) -> None:
        raise NotImplementedError("implement `_subscribe` in your adapter subclass")

    async def _unsubscribe(self, data_type: DataType) -> None:
        raise NotImplementedError("implement `_unsubscribe` in your adapter subclass")

    async def _request(self, data_type: DataType, correlation_id: UUID4) -> None:
        raise NotImplementedError("implement `_request` in your adapter subclass")
```

**Key Methods**:

- `_connect`: Establishes a connection to the data provider
- `_disconnect`: Closes the connection to the data provider
- `reset`: Resets the state of the client
- `dispose`: Disposes of any resources held by the client
- `_subscribe`: Subscribes to a specific data type
- `_unsubscribe`: Unsubscribes from a specific data type
- `_request`: Requests data from the provider

### MarketDataClient

The `MarketDataClient` handles market-specific data such as order books, top-of-book quotes and trades,
and instrument status updates. It focuses on providing historical and real-time market data that is essential for
trading operations.

```python
from nautilus_trader.live.data_client import LiveMarketDataClient
from nautilus_trader.model import BarType, DataType
from nautilus_trader.model import InstrumentId
from nautilus_trader.model.enums import BookType

class TemplateLiveMarketDataClient(LiveMarketDataClient):
    """
    An example of a ``LiveMarketDataClient`` highlighting the overridable abstract methods.
    """

    async def _connect(self) -> None:
        raise NotImplementedError("implement `_connect` in your adapter subclass")

    async def _disconnect(self) -> None:
        raise NotImplementedError("implement `_disconnect` in your adapter subclass")

    def reset(self) -> None:
        raise NotImplementedError("implement `reset` in your adapter subclass")

    def dispose(self) -> None:
        raise NotImplementedError("implement `dispose` in your adapter subclass")

    async def _subscribe_instruments(self) -> None:
        raise NotImplementedError("implement `_subscribe_instruments` in your adapter subclass")

    async def _unsubscribe_instruments(self) -> None:
        raise NotImplementedError("implement `_unsubscribe_instruments` in your adapter subclass")

    async def _subscribe_order_book_deltas(self, instrument_id: InstrumentId, book_type: BookType, depth: int | None = None, kwargs: dict | None = None) -> None:
        raise NotImplementedError("implement `_subscribe_order_book_deltas` in your adapter subclass")

    async def _unsubscribe_order_book_deltas(self, instrument_id: InstrumentId) -> None:
        raise NotImplementedError("implement `_unsubscribe_order_book_deltas` in your adapter subclass")
```

**Key Methods**:

- `_connect`: Establishes a connection to the venues APIs
- `_disconnect`: Closes the connection to the venues APIs
- `reset`: Resets the state of the client
- `dispose`: Disposes of any resources held by the client
- `_subscribe_instruments`: Subscribes to market data for multiple instruments
- `_unsubscribe_instruments`: Unsubscribes from market data for multiple instruments
- `_subscribe_order_book_deltas`: Subscribes to order book delta updates
- `_unsubscribe_order_book_deltas`: Unsubscribes from order book delta updates

---

## REST‐API field-mapping guideline

When translating a venue’s REST payload into our domain model **avoid renaming** the upstream
fields unless there is a compelling reason (e.g. a clash with reserved keywords). The only
transformation we apply by default is **camelCase → snake_case**.

Keeping the external names intact makes it trivial to debug payloads, compare captures against the
Rust structs, and speeds up onboarding for new contributors who have the venue’s API reference
open side-by-side.

### ExecutionClient

The `ExecutionClient` is responsible for order management, including submission, modification, and
cancellation of orders. It is a crucial component of the adapter that interacts with the venues
trading system to manage and execute trades.

```python
from nautilus_trader.execution.messages import BatchCancelOrders, CancelAllOrders, CancelOrder, ModifyOrder, SubmitOrder
from nautilus_trader.execution.reports import FillReport, OrderStatusReport, PositionStatusReport
from nautilus_trader.live.execution_client import LiveExecutionClient
from nautilus_trader.model import ClientOrderId, InstrumentId, VenueOrderId

class TemplateLiveExecutionClient(LiveExecutionClient):
    """
    An example of a ``LiveExecutionClient`` highlighting the method requirements.
    """

    async def _connect(self) -> None:
        raise NotImplementedError("implement `_connect` in your adapter subclass")

    async def _disconnect(self) -> None:
        raise NotImplementedError("implement `_disconnect` in your adapter subclass")

    async def _submit_order(self, command: SubmitOrder) -> None:
        raise NotImplementedError("implement `_submit_order` in your adapter subclass")

    async def _modify_order(self, command: ModifyOrder) -> None:
        raise NotImplementedError("implement `_modify_order` in your adapter subclass")

    async def _cancel_order(self, command: CancelOrder) -> None:
        raise NotImplementedError("implement `_cancel_order` in your adapter subclass")

    async def _cancel_all_orders(self, command: CancelAllOrders) -> None:
        raise NotImplementedError("implement `_cancel_all_orders` in your adapter subclass")

    async def _batch_cancel_orders(self, command: BatchCancelOrders) -> None:
        raise NotImplementedError("implement `_batch_cancel_orders` in your adapter subclass")

    async def generate_order_status_report(
        self, instrument_id: InstrumentId, client_order_id: ClientOrderId | None = None, venue_order_id: VenueOrderId | None = None
    ) -> OrderStatusReport | None:
        raise NotImplementedError("method `generate_order_status_report` must be implemented in the subclass")

    async def generate_order_status_reports(
        self, instrument_id: InstrumentId | None = None, start: pd.Timestamp | None = None, end: pd.Timestamp | None = None, open_only: bool = False
    ) -> list[OrderStatusReport]:
        raise NotImplementedError("method `generate_order_status_reports` must be implemented in the subclass")

    async def generate_fill_reports(
        self, instrument_id: InstrumentId | None = None, venue_order_id: VenueOrderId | None = None, start: pd.Timestamp | None = None, end: pd.Timestamp | None = None
    ) -> list[FillReport]:
        raise NotImplementedError("method `generate_fill_reports` must be implemented in the subclass")

    async def generate_position_status_reports(
        self, instrument_id: InstrumentId | None = None, start: pd.Timestamp | None = None, end: pd.Timestamp | None = None
    ) -> list[PositionStatusReport]:
        raise NotImplementedError("method `generate_position_status_reports` must be implemented in the subclass")
```

**Key Methods**:

- `_connect`: Establishes a connection to the venues APIs
- `_disconnect`: Closes the connection to the venues APIs
- `_submit_order`: Submits a new order to the venue
- `_modify_order`: Modifies an existing order on the venue
- `_cancel_order`: Cancels a specific order on the venue
- `_cancel_all_orders`: Cancels all orders for an instrument on the venue
- `_batch_cancel_orders`: Cancels a batch of orders for an instrument on the venue
- `generate_order_status_report`: Generates a report for a specific order on the venue
- `generate_order_status_reports`: Generates reports for all orders on the venue
- `generate_fill_reports`: Generates reports for filled orders on the venue
- `generate_position_status_reports`: Generates reports for position status on the venue

### Configuration

The configuration file defines settings specific to the adapter, such as API keys and connection
details. These settings are essential for initializing and managing the adapter’s connection to the
data provider.

```python
from nautilus_trader.config import LiveDataClientConfig, LiveExecClientConfig

class TemplateDataClientConfig(LiveDataClientConfig):
    """
    Configuration for ``TemplateDataClient`` instances.
    """

    api_key: str
    api_secret: str
    base_url: str

class TemplateExecClientConfig(LiveExecClientConfig):
    """
    Configuration for ``TemplateExecClient`` instances.
    """

    api_key: str
    api_secret: str
    base_url: str
```

**Key Attributes**:

- `api_key`: The API key for authenticating with the data provider
- `api_secret`: The API secret for authenticating with the data provider
- `base_url`: The base URL for connecting to the data provider’s API


---

file path: ./getting_started/index.md
# Getting Started

To get started with NautilusTrader, you will need:

- A Python 3.11–3.13 environment with the `nautilus_trader` package installed.
- A way to run Python scripts or Jupyter notebooks for backtesting and/or live trading.

## [Installation](installation.md)

The **Installation** guide will help to ensure that NautilusTrader is properly installed on your machine.

## [Quickstart](quickstart.md)

The **Quickstart** provides a step-by-step walk through for setting up your first backtest.

## Examples in repository

The [online documentation](https://nautilustrader.io/docs/latest/) shows just a subset of examples. For the full set, see this repository on GitHub.

The following table lists example locations ordered by recommended learning progression:

| Directory                   | Contains                                                                                                                    |
|:----------------------------|:----------------------------------------------------------------------------------------------------------------------------|
| [examples/](https://github.com/nautechsystems/nautilus_trader/tree/develop/examples)                 | Fully runnable, self-contained Python examples.                                                                                     |
| [docs/tutorials/](tutorials/)           | Jupyter notebook tutorials demonstrating common workflows.                                                                              |
| [docs/concepts/](concepts/)            | Concept guides with concise code snippets illustrating key features. |
| [nautilus_trader/examples/](../nautilus_trader/examples/) | Pure-Python examples of basic strategies, indicators, and execution algorithms.                                     |
| [tests/unit_tests/](../../tests/unit_tests/)         | Unit tests covering core functionality and edge cases.                      |

## Backtesting API levels

NautilusTrader provides two different API levels for backtesting:

| API Level      | Description                           | Characteristics                                                                                                                                                                                                                                                                                                                                                        |
|:---------------|:--------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| High-Level API | Uses `BacktestNode` and `TradingNode` | Recommended for production: easier transition to live trading; requires a Parquet-based data catalog. |
| Low-Level API  | Uses `BacktestEngine`                 | Intended for library development: no live-trading path; direct component access; may encourage non–live-compatible patterns. |

Backtesting involves running simulated trading systems on historical data.

To get started backtesting with NautilusTrader you need to first understand the two different API
levels which are provided, and which one may be more suitable for your intended use case.

:::info
For more information on which API level to choose, refer to the [Backtesting](../concepts/backtesting.md) guide.
:::

### [Backtest (low-level API)](backtest_low_level.md)

This tutorial runs through how to load raw data (external to Nautilus) using data loaders and wranglers,
and then use this data with a `BacktestEngine` to run a single backtest.

### [Backtest (high-level API)](backtest_high_level.md)

This tutorial runs through how to load raw data (external to Nautilus) into the data catalog,
and then use this data with a `BacktestNode` to run a single backtest.

## Running in docker

Alternatively, a self-contained dockerized Jupyter notebook server is available for download, which does not require any setup or
installation. This is the fastest way to get up and running to try out NautilusTrader. Bear in mind that any data will be
deleted when the container is deleted.

- To get started, install docker:
  - Go to [docker.com](https://docs.docker.com/get-docker/) and follow the instructions
- From a terminal, download the latest image
  - `docker pull ghcr.io/nautechsystems/jupyterlab:nightly --platform linux/amd64`
- Run the docker container, exposing the jupyter port:
  - `docker run -p 8888:8888 ghcr.io/nautechsystems/jupyterlab:nightly`
- Open your web browser to `localhost:{port}`
  - <http://localhost:8888>

:::info
NautilusTrader currently exceeds the rate limit for Jupyter notebook logging (stdout output),
this is why `log_level` in the examples is set to `ERROR`. If you lower this level to see
more logging then the notebook will hang during cell execution. A fix is currently
being investigated which involves either raising the configured rate limits for
Jupyter, or throttling the log flushing from Nautilus.

- <https://github.com/jupyterlab/jupyterlab/issues/12845>
- <https://github.com/deshaw/jupyterlab-limit-output>

:::


---

file path: ./getting_started/quickstart.md
# Quickstart

This guide is generated from the Jupyter notebook [quickstart.ipynb](quickstart.ipynb).


---

file path: ./getting_started/installation.md
# Installation

NautilusTrader is officially supported for Python 3.11-3.13* on the following 64-bit platforms:

| Operating System       | Supported Versions    | CPU Architecture  |
|------------------------|-----------------------|-------------------|
| Linux (Ubuntu)         | 22.04 and later       | x86_64            |
| Linux (Ubuntu)         | 22.04 and later       | ARM64             |
| macOS                  | 14.7 and later        | ARM64             |
| Windows Server         | 2022 and later        | x86_64            |

\* Windows builds are currently pinned to CPython 3.13.2 because later
3.13.x Windows binaries were produced with the per-interpreter GIL enabled
but without exporting a handful of private C-API symbols. These missing
exports break linking of our Cython extensions. The pin can be removed
if/when an upstream CPython release restores the exports.

:::note
NautilusTrader may work on other platforms, but only those listed above are regularly used by developers and tested in CI.
:::

We recommend using the latest supported version of Python and installing [nautilus_trader](https://pypi.org/project/nautilus_trader/) inside a virtual environment to isolate dependencies.

**There are two supported ways to install**:

1. Pre-built binary wheel from PyPI *or* the Nautech Systems package index.
2. Build from source.

:::tip
We highly recommend installing using the [uv](https://docs.astral.sh/uv) package manager with a "vanilla" CPython.

Conda and other Python distributions *may* work but aren’t officially supported.
:::

## From PyPI

To install the latest [nautilus_trader](https://pypi.org/project/nautilus_trader/) binary wheel (or sdist package) from PyPI using Pythons pip package manager:

```bash
pip install -U nautilus_trader
```

## Extras

Install optional dependencies as 'extras' for specific integrations:

- `betfair`: Betfair adapter (integration) dependencies.
- `docker`: Needed for Docker when using the IB gateway (with the Interactive Brokers adapter).
- `dydx`: dYdX adapter (integration) dependencies.
- `ib`: Interactive Brokers adapter (integration) dependencies.
- `polymarket`: Polymarket adapter (integration) dependencies.

To install with specific extras using pip:

```bash
pip install -U "nautilus_trader[docker,ib]"
```

## From the Nautech Systems package index

The Nautech Systems package index (`packages.nautechsystems.io`) is [PEP-503](https://peps.python.org/pep-0503/) compliant and hosts both stable and development binary wheels for `nautilus_trader`.
This enables users to install either the latest stable release or pre-release versions for testing.

### Stable wheels

Stable wheels correspond to official releases of `nautilus_trader` on PyPI, and use standard versioning.

To install the latest stable release:

```bash
pip install -U nautilus_trader --index-url=https://packages.nautechsystems.io/simple
```

### Development wheels

Development wheels are published from both the `nightly` and `develop` branches,
allowing users to test features and fixes ahead of stable releases.

**Note**: Wheels from the `develop` branch are only built for the Linux x86_64 platform to save time
and compute resources, while `nightly` wheels support additional platforms as shown below.

| Platform           | Nightly | Develop |
| :----------------- | :------ | :------ |
| `Linux (x86_64)`   | ✓       | ✓       |
| `Linux (ARM64)`    | ✓       | -       |
| `macOS (ARM64)`    | ✓       | -       |
| `Windows (x86_64)` | ✓       | -       |

This process also helps preserve compute resources and ensures easy access to the exact binaries tested in CI pipelines,
while adhering to [PEP-440](https://peps.python.org/pep-0440/) versioning standards:

- `develop` wheels use the version format `dev{date}+{build_number}` (e.g., `1.208.0.dev20241212+7001`).
- `nightly` wheels use the version format `a{date}` (alpha) (e.g., `1.208.0a20241212`).

:::warning
We don't recommend using development wheels in production environments, such as live trading controlling real capital.
:::

### Installation commands

By default, pip installs the latest stable release. Adding the `--pre` flag ensures that pre-release versions, including development wheels, are considered.

To install the latest available pre-release (including development wheels):

```bash
pip install -U nautilus_trader --pre --index-url=https://packages.nautechsystems.io/simple
```

To install a specific development wheel (e.g., `1.208.0a20241212` for December 12, 2024):

```bash
pip install nautilus_trader==1.208.0a20241212 --index-url=https://packages.nautechsystems.io/simple
```

### Available versions

You can view all available versions of `nautilus_trader` on the [package index](https://packages.nautechsystems.io/simple/nautilus-trader/index.html).

To programmatically request and list available versions:

```bash
curl -s https://packages.nautechsystems.io/simple/nautilus-trader/index.html | grep -oP '(?<=<a href="))[^"]+(?=")' | awk -F'#' '{print $1}' | sort
```

### Branch updates

- `develop` branch wheels (`.dev`): Are built and published continuously with every merged commit.
- `nightly` branch wheels (`a`): Are built and published daily when `develop` branch is automatically merged at **14:00 UTC** (if there are changes).

### Retention policies

- `develop` branch wheels (`.dev`): Only the most recent wheel build is retained.
- `nightly` branch wheels (`a`): Only the 10 most recent wheel builds are retained.

## From Source

It's possible to install from source using pip if you first install the build dependencies as specified in the `pyproject.toml`.

1. Install [rustup](https://rustup.rs/) (the Rust toolchain installer):
   - Linux and macOS:

```bash
curl https://sh.rustup.rs -sSf | sh
```

- Windows:
  - Download and install [`rustup-init.exe`](https://win.rustup.rs/x86_64)
  - Install "Desktop development with C++" with [Build Tools for Visual Studio 2019](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=BuildTools&rel=16)
- Verify (any system):
    from a terminal session run: `rustc --version`

2. Enable `cargo` in the current shell:
   - Linux and macOS:

```bash
source $HOME/.cargo/env
```

- Windows:
  - Start a new PowerShell

     1. Install [clang](https://clang.llvm.org/) (a C language frontend for LLVM):
- Linux:

```bash
sudo apt-get install clang
```

- Windows:

1. Add Clang to your [Build Tools for Visual Studio 2019](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=BuildTools&rel=16):

- Start | Visual Studio Installer | Modify | C++ Clang tools for Windows (12.0.0 - x64…) = checked | Modify

2. Enable `clang` in the current shell:

```powershell
[System.Environment]::SetEnvironmentVariable('path', "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\Llvm\x64\bin\;" + $env:Path,"User")
```

- Verify (any system):
  from a terminal session run:

```bash
clang --version
```

3. Install uv (see the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation) for more details):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

4. Clone the source with `git`, and install from the project's root directory:

```bash
git clone --branch develop --depth 1 https://github.com/nautechsystems/nautilus_trader
cd nautilus_trader
uv sync --all-extras
```

:::note
The `--depth 1` flag fetches just the latest commit for a faster, lightweight clone.
:::

5. Set environment variables for PyO3 compilation (Linux and macOS only):

```bash
# Set the library path for the Python interpreter (in this case Python 3.13.4)
export LD_LIBRARY_PATH="$HOME/.local/share/uv/python/cpython-3.13.4-linux-x86_64-gnu/lib:$LD_LIBRARY_PATH"

# Set the Python executable path for PyO3
export PYO3_PYTHON=$(pwd)/.venv/bin/python
```

:::note
Adjust the Python version and architecture in the `LD_LIBRARY_PATH` to match your system.
Use `uv python list` to find the exact path for your Python installation.
:::

## From GitHub Release

To install a binary wheel from GitHub, first navigate to the [latest release](https://github.com/nautechsystems/nautilus_trader/releases/latest).
Download the appropriate `.whl` for your operating system and Python version, then run:

```bash
pip install <file-name>.whl
```

## Versioning and releases

NautilusTrader is still under active development. Some features may be incomplete, and while
the API is becoming more stable, breaking changes can occur between releases.
We strive to document these changes in the release notes on a **best-effort basis**.

We aim to follow a **weekly release schedule**, though experimental or larger features may cause delays.

Use NautilusTrader only if you are prepared to adapt to these changes.

## Redis

Using [Redis](https://redis.io) with NautilusTrader is **optional** and only required if configured as the backend for a cache database or [message bus](../concepts/message_bus.md).

:::info
The minimum supported Redis version is 6.2 (required for [streams](https://redis.io/docs/latest/develop/data-types/streams/) functionality).
:::

For a quick setup, we recommend using a [Redis Docker container](https://hub.docker.com/_/redis/). You can find an example setup in the `.docker` directory,
or run the following command to start a container:

```bash
docker run -d --name redis -p 6379:6379 redis:latest
```

This command will:

- Pull the latest version of Redis from Docker Hub if it's not already downloaded.
- Run the container in detached mode (`-d`).
- Name the container `redis` for easy reference.
- Expose Redis on the default port 6379, making it accessible to NautilusTrader on your machine.

To manage the Redis container:

- Start it with `docker start redis`
- Stop it with `docker stop redis`

:::tip
We recommend using [Redis Insight](https://redis.io/insight/) as a GUI to visualize and debug Redis data efficiently.
:::

## Precision mode

NautilusTrader supports two precision modes for its core value types (`Price`, `Quantity`, `Money`),
which differ in their internal bit-width and maximum decimal precision.

- **High-precision**: 128-bit integers with up to 16 decimals of precision, and a larger value range.
- **Standard-precision**: 64-bit integers with up to 9 decimals of precision, and a smaller value range.

:::note
By default, the official Python wheels **ship** in high-precision (128-bit) mode on Linux and macOS.
On Windows, only standard-precision (64-bit) is available due to the lack of native 128-bit integer support.

For the Rust crates, the default is standard-precision unless you explicitly enable the `high-precision` feature flag.
:::

The performance tradeoff is that standard-precision is ~3–5% faster in typical backtests,
but has lower decimal precision and a smaller representable value range.

:::note
Performance benchmarks comparing the modes are pending.
:::

### Build configuration

The precision mode is determined by:

- Setting the `HIGH_PRECISION` environment variable during compilation, **and/or**
- Enabling the `high-precision` Rust feature flag explicitly.

#### High-precision mode (128-bit)

```bash
export HIGH_PRECISION=true
make install-debug
```

#### Standard-precision mode (64-bit)

```bash
export HIGH_PRECISION=false
make install-debug
```

### Rust feature flag

To enable high-precision (128-bit) mode in Rust, add the `high-precision` feature to your `Cargo.toml`:

```toml
[dependencies]
nautilus_core = { version = "*", features = ["high-precision"] }
```

:::info
See the [Value Types](../concepts/overview.md#value-types) specifications for more details.
:::


---

file path: ./getting_started/backtest_low_level.md
# Backtest (low-level API)

This guide is generated from the Jupyter notebook [backtest_low_level.ipynb](backtest_low_level.ipynb).


---

file path: ./getting_started/backtest_high_level.md
# Backtest (high-level API)

This guide is generated from the Jupyter notebook [backtest_high_level.ipynb](backtest_high_level.ipynb).


---

file path: ./dev_guide/environment_setup.md
# Environment Setup

For development we recommend using the PyCharm *Professional* edition IDE, as it interprets Cython syntax. Alternatively, you could use Visual Studio Code with a Cython extension.

[uv](https://docs.astral.sh/uv) is the preferred tool for handling all Python virtual environments and dependencies.

[pre-commit](https://pre-commit.com/) is used to automatically run various checks, auto-formatters and linting tools at commit.

NautilusTrader uses increasingly more [Rust](https://www.rust-lang.org), so Rust should be installed on your system as well
([installation guide](https://www.rust-lang.org/tools/install)).

:::info
NautilusTrader *must* compile and run on **Linux, macOS, and Windows**. Please keep portability in
mind (use `std::path::Path`, avoid Bash-isms in shell scripts, etc.).
:::

## Setup

The following steps are for UNIX-like systems, and only need to be completed once.

1. Follow the [installation guide](../getting_started/installation.md) to set up the project with a modification to the final command to install development and test dependencies:

```bash
uv sync --active --all-groups --all-extras
```

or

```bash
make install
```

If you're developing and iterating frequently, then compiling in debug mode is often sufficient and *significantly* faster than a fully optimized build.
To install in debug mode, use:

```bash
make install-debug
```

2. Set up the pre-commit hook which will then run automatically at commit:

```bash
pre-commit install
```

Before opening a pull-request run the formatting and lint suite locally so that CI passes on the
first attempt:

```bash
make format
make pre-commit
```

Make sure the Rust compiler reports **zero errors** – broken builds slow everyone down.

3. **Optional**: For frequent Rust development, configure the `PYO3_PYTHON` variable in `.cargo/config.toml` with the path to the Python interpreter. This helps reduce recompilation times for IDE/rust-analyzer based `cargo check`:

```bash
PYTHON_PATH=$(which python)
echo -e "\n[env]\nPYO3_PYTHON = \"$PYTHON_PATH\"" >> .cargo/config.toml
```

Since `.cargo/config.toml` is tracked, configure git to skip any local modifications:

```bash
git update-index --skip-worktree .cargo/config.toml
```

To restore tracking: `git update-index --no-skip-worktree .cargo/config.toml`

## Builds

Following any changes to `.rs`, `.pyx` or `.pxd` files, you can re-compile by running:

```bash
uv run --no-sync python build.py
```

or

```bash
make build
```

If you're developing and iterating frequently, then compiling in debug mode is often sufficient and *significantly* faster than a fully optimized build.
To compile in debug mode, use:

```bash
make build-debug
```

## Faster builds 🏁

The cranelift backends reduces build time significantly for dev, testing and IDE checks. However, cranelift is available on the nightly toolchain and needs extra configuration. Install the nightly toolchain

```
rustup install nightly
rustup override set nightly
rustup component add rust-analyzer # install nightly lsp
rustup override set stable # reset to stable
```

Activate the nightly feature and use "cranelift" backend for dev and testing profiles in workspace `Cargo.toml`. You can apply the below patch using `git apply <patch>`. You can remove it using `git apply -R <patch>` before pushing changes.

```
diff --git a/Cargo.toml b/Cargo.toml
index 62b78cd8d0..beb0800211 100644
--- a/Cargo.toml
+++ b/Cargo.toml
@@ -1,3 +1,6 @@
+# This line needs to come before anything else in Cargo.toml
+cargo-features = ["codegen-backend"]
+
 [workspace]
 resolver = "2"
 members = [
@@ -140,6 +143,7 @@ lto = false
 panic = "unwind"
 incremental = true
 codegen-units = 256
+codegen-backend = "cranelift"

 [profile.test]
 opt-level = 0
@@ -150,11 +154,13 @@ strip = false
 lto = false
 incremental = true
 codegen-units = 256
+codegen-backend = "cranelift"

 [profile.nextest]
 inherits = "test"
 debug = false # Improves compile times
 strip = "debuginfo" # Improves compile times
+codegen-backend = "cranelift"

 [profile.release]
 opt-level = 3
```

Pass `RUSTUP_TOOLCHAIN=nightly` when running `make build-debug` like commands and include it in in all [rust analyzer settings](#rust-analyzer-settings) for faster builds and IDE checks.

## Services

You can use `docker-compose.yml` file located in `.docker` directory
to bootstrap the Nautilus working environment. This will start the following services:

```bash
docker-compose up -d
```

If you only want specific services running (like `postgres` for example), you can start them with command:

```bash
docker-compose up -d postgres
```

Used services are:

- `postgres`: Postgres database with root user `POSTRES_USER` which defaults to `postgres`, `POSTGRES_PASSWORD` which defaults to `pass` and `POSTGRES_DB` which defaults to `postgres`.
- `redis`: Redis server.
- `pgadmin`: PgAdmin4 for database management and administration.

:::info
Please use this as development environment only. For production, use a proper and more secure setup.
:::

After the services has been started, you must log in with `psql` cli to create `nautilus` Postgres database.
To do that you can run, and type `POSTGRES_PASSWORD` from docker service setup

```bash
psql -h localhost -p 5432 -U postgres
```

After you have logged in as `postgres` administrator, run `CREATE DATABASE` command with target db name (we use `nautilus`):

```
psql (16.2, server 15.2 (Debian 15.2-1.pgdg110+1))
Type "help" for help.

postgres=# CREATE DATABASE nautilus;
CREATE DATABASE

```

## Nautilus CLI Developer Guide

## Introduction

The Nautilus CLI is a command-line interface tool for interacting with the NautilusTrader ecosystem.
It offers commands for managing the PostgreSQL database and handling various trading operations.

:::note
The Nautilus CLI command is only supported on UNIX-like systems.
:::

## Install

You can install the Nautilus CLI using the below Makefile target, which leverages `cargo install` under the hood.
This will place the nautilus binary in your system's PATH, assuming Rust's `cargo` is properly configured.

```bash
make install-cli
```

## Commands

You can run `nautilus --help` to view the CLI structure and available command groups:

### Database

These commands handle bootstrapping the PostgreSQL database.
To use them, you need to provide the correct connection configuration,
either through command-line arguments or a `.env` file located in the root directory or the current working directory.

- `--host` or `POSTGRES_HOST` for the database host
- `--port` or `POSTGRES_PORT` for the database port
- `--user` or `POSTGRES_USER` for the root administrator (typically the postgres user)
- `--password` or `POSTGRES_PASSWORD` for the root administrator's password
- `--database` or `POSTGRES_DATABASE` for both the database **name and the new user** with privileges to that database
    (e.g., if you provide `nautilus` as the value, a new user named nautilus will be created with the password from `POSTGRES_PASSWORD`, and the `nautilus` database will be bootstrapped with this user as the owner).

Example of `.env` file

```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=pass
POSTGRES_DATABASE=nautilus
```

List of commands are:

1. `nautilus database init`: Will bootstrap schema, roles and all sql files located in `schema` root directory (like `tables.sql`).
2. `nautilus database drop`: Will drop all tables, roles and data in target Postgres database.

## Rust analyzer settings

Rust analyzer is a popular language server for Rust and has integrations for many IDEs. It is recommended to configure rust analyzer to have same environment variables as `make build-debug` for faster compile times. Below tested configurations for VSCode and Astro Nvim are provided. For more information see [PR](https://github.com/nautechsystems/nautilus_trader/pull/2524) or rust analyzer [config docs](https://rust-analyzer.github.io/book/configuration.html).

### VSCode

You can add the following settings to your VSCode `settings.json` file:

```
    "rust-analyzer.restartServerOnConfigChange": true,
    "rust-analyzer.linkedProjects": [
        "Cargo.toml"
    ],
    "rust-analyzer.cargo.features": "all",
    "rust-analyzer.check.workspace": false,
    "rust-analyzer.check.extraEnv": {
        "VIRTUAL_ENV": "<path-to-your-virtual-environment>/.venv",
        "CC": "clang",
        "CXX": "clang++"
    },
    "rust-analyzer.cargo.extraEnv": {
        "VIRTUAL_ENV": "<path-to-your-virtual-environment>/.venv",
        "CC": "clang",
        "CXX": "clang++"
    },
    "rust-analyzer.runnables.extraEnv": {
        "VIRTUAL_ENV": "<path-to-your-virtual-environment>/.venv",
        "CC": "clang",
        "CXX": "clang++"
    },
    "rust-analyzer.check.features": "all",
    "rust-analyzer.testExplorer": true
```

### Astro Nvim (Neovim + AstroLSP)

You can add the following to your astro lsp config file:

```
    config = {
      rust_analyzer = {
        settings = {
          ["rust-analyzer"] = {
            restartServerOnConfigChange = true,
            linkedProjects = { "Cargo.toml" },
            cargo = {
              features = "all",
              extraEnv = {
                VIRTUAL_ENV = "<path-to-your-virtual-environment>/.venv",
                CC = "clang",
                CXX = "clang++",
              },
            },
            check = {
              workspace = false,
              command = "check",
              features = "all",
              extraEnv = {
                VIRTUAL_ENV = "<path-to-your-virtual-environment>/.venv",
                CC = "clang",
                CXX = "clang++",
              },
            },
            runnables = {
              extraEnv = {
                VIRTUAL_ENV = "<path-to-your-virtual-environment>/.venv",
                CC = "clang",
                CXX = "clang++",
              },
            },
            testExplorer = true,
          },
        },
      },
```


---

file path: ./dev_guide/cython.md
# Cython

Here you will find guidance and tips for working on NautilusTrader using the Cython language.
More information on Cython syntax and conventions can be found by reading the [Cython docs](https://cython.readthedocs.io/en/latest/index.html).

## What is Cython?

Cython is a superset of Python that compiles to C extension modules, enabling optional static typing and optimized performance. NautilusTrader relies on Cython for its Python bindings and performance-critical components.

## Function and method signatures

Ensure that all functions and methods returning `void` or a primitive C type (such as `bint`, `int`, `double`) include the `except *` keyword in the signature.

This will ensure Python exceptions are not ignored, and instead are “bubbled up” to the caller as expected.

## Debugging

### PyCharm

Improved debugging support for Cython has remained a highly up-voted PyCharm
feature for many years. Unfortunately, it's safe to assume that PyCharm will not
be receiving first class support for Cython debugging
<https://youtrack.jetbrains.com/issue/PY-9476>.

### Cython Docs

The following recommendations are contained in the Cython docs:
<https://cython.readthedocs.io/en/latest/src/userguide/debugging.html>

The summary is it involves manually running a specialized version of `gdb` from the command line.
We don't recommend this workflow.

### Tips

When debugging and seeking to understand a complex system such as NautilusTrader, it can be
quite helpful to step through the code with a debugger. With this not being available
for the Cython part of the codebase, there are a few things which can help:

- Ensure `LogLevel.DEBUG` is configured for the backtesting or live system you are debugging.
  This is available on `BacktestEngineConfig(logging=LoggingConfig(log_level="DEBUG"))` or `TradingNodeConfig(logging=LoggingConfig=log_level="DEBUG"))`.
  With `DEBUG` mode active you will see more granular and verbose log traces which could be what you need to understand the flow.
- Beyond this, if you still require more granular visibility around a part of the system, we recommend some well-placed calls
  to a components logger (normally `self._log.debug(f"HERE {variable}"` is enough).


---

file path: ./dev_guide/docs.md
# Documentation Style Guide

This guide outlines the style conventions and best practices for writing documentation for NautilusTrader.

## General Principles

- We favor simplicity over complexity, less is more.
- We favor concise yet readable prose and documentation.
- We value standardization in conventions, style, patterns, etc.
- Documentation should be accessible to users of varying technical backgrounds.

## Markdown Tables

### Column Alignment and Spacing

- Use symmetrical column widths based on the space necessary dictated by the widest content in each column.
- Align column separators (`|`) vertically for better readability.
- Use consistent spacing around cell content.

### Notes and Descriptions

- All notes and descriptions should have terminating periods.
- Keep notes concise but informative.
- Use sentence case (capitalize only the first letter and proper nouns).

### Example

```markdown
| Order Type             | Spot | Margin | USDT Futures | Coin Futures | Notes                   |
|------------------------|------|--------|--------------|--------------|-------------------------|
| `MARKET`               | ✓    | ✓      | ✓            | ✓            |                         |
| `STOP_MARKET`          | -    | ✓      | ✓            | ✓            | Not supported for Spot. |
| `MARKET_IF_TOUCHED`    | -    | -      | ✓            | ✓            | Futures only.           |
```

### Support Indicators

- Use `✓` for supported features.
- Use `-` for unsupported features (not `✗` or other symbols).
- When adding notes for unsupported features, emphasize with italics: `*Not supported*`.
- Leave cells empty when no content is needed.

## Code References

- Use backticks for inline code, method names, class names, and configuration options.
- Use code blocks for multi-line examples.
- When referencing functions or code locations, include the pattern `file_path:line_number` to allow easy navigation.

## Headings

- Use title case for main headings (## Level 2).
- Use sentence case for subheadings (### Level 3 and below).
- Ensure proper heading hierarchy (don't skip levels).

## Lists

- Use hyphens (`-`) for unordered-list bullets; avoid `*` or `+` to keep the Markdown style
   consistent across the project.
- Use numbered lists only when order matters.
- Maintain consistent indentation for nested lists.
- End list items with periods when they are complete sentences.

## Links and References

- Use descriptive link text (avoid "click here" or "this link").
- Reference external documentation when appropriate.
- Ensure all internal links are relative and accurate.

## Technical Terminology

- Base capability matrices on the Nautilus domain model, not exchange-specific terminology.
- Mention exchange-specific terms in parentheses or notes when necessary for clarity.
- Use consistent terminology throughout the documentation.

## Examples and Code Samples

- Provide practical, working examples.
- Include necessary imports and context.
- Use realistic variable names and values.
- Add comments to explain non-obvious parts of examples.

## Warnings and Notes

- Use appropriate admonition blocks for important information:
  - `:::note` for general information.
  - `:::warning` for important caveats.
  - `:::tip` for helpful suggestions.

## API Documentation

- Document parameters and return types clearly.
- Include usage examples for complex APIs.
- Explain any side effects or important behavior.
- Keep parameter descriptions concise but complete.


---

file path: ./dev_guide/packaged_data.md
# Packaged Data

Various data is contained internally in the `tests/test_kit/data` folder.

## Libor Rates

The libor rates for 1 month USD can be updated by downloading the CSV data from <https://fred.stlouisfed.org/series/USD1MTD156N>.

Ensure you select `Max` for the time window.

## Short Term Interest Rates

The interbank short term interest rates can be updated by downloading the CSV data at <https://data.oecd.org/interest/short-term-interest-rates.htm>.

## Economic Events

The economic events can be updated from downloading the CSV data from fxstreet <https://www.fxstreet.com/economic-calendar>.

Ensure timezone is set to GMT.

A maximum 3 month range can be filtered and so yearly quarters must be downloaded manually and stitched together into a single CSV.
Use the calendar icon to filter the data in the following way;

- 01/01/xx - 31/03/xx
- 01/04/xx - 30/06/xx
- 01/07/xx - 30/09/xx
- 01/10/xx - 31/12/xx

Download each CSV.


---

file path: ./dev_guide/index.md
# Developer Guide

Welcome to the developer guide for NautilusTrader!

Here you'll find guidance on developing and extending NautilusTrader to meet your trading needs or to contribute improvements back to the project.

We believe in using the right tool for the job. The overall design philosophy is to fully utilize
the high level power of Python, with its rich eco-system of frameworks and libraries, whilst
overcoming some of its inherent shortcomings in performance and lack of built-in type safety
(with it being an interpreted dynamic language).

One of the advantages of Cython is that allocation and freeing of memory is handled by the C code
generator during the ‘cythonization’ step of the build (unless you’re specifically utilizing some of
its lower level features).

This approach combines Python’s simplicity with near-native C performance via compiled extensions.

The main development and runtime environment we are working in is of course Python. With the
introduction of Cython syntax throughout the production codebase in `.pyx` and `.pxd` files - it’s
important to be aware of how the CPython implementation of Python interacts with the underlying
CPython API, and the NautilusTrader C extension modules which Cython produces.

We recommend a thorough review of the [Cython docs](https://cython.readthedocs.io/en/latest/) to familiarize yourself with some of its core
concepts, and where C typing is being introduced.

It's not necessary to become a C language expert, however it's helpful to understand how Cython C
syntax is used in function and method definitions, in local code blocks, and the common primitive C
types and how these map to their corresponding `PyObject` types.

## Contents

- [Environment Setup](environment_setup.md)
- [Coding Standards](coding_standards.md)
- [Cython](cython.md)
- [Rust](rust.md)
- [Docs](docs.md)
- [Testing](testing.md)
- [Adapters](adapters.md)
- [Benchmarking](benchmarking.md)
- [Packaged Data](packaged_data.md)


---

file path: ./dev_guide/rust.md
# Rust Style Guide

The [Rust](https://www.rust-lang.org/learn) programming language is an ideal fit for implementing the mission-critical core of the platform and systems. Its strong type system, ownership model, and compile-time checks eliminate memory errors and data races by construction, while zero-cost abstractions and the absence of a garbage collector deliver C-like performance—critical for high-frequency trading workloads.

## Python Bindings

Python bindings are provided via Cython and [PyO3](https://pyo3.rs), allowing users to import NautilusTrader crates directly in Python without a Rust toolchain.

## Code Style and Conventions

### File Header Requirements

All Rust files must include the standardized copyright header:

```rust
// -------------------------------------------------------------------------------------------------
//  Copyright (C) 2015-2025 Nautech Systems Pty Ltd. All rights reserved.
//  https://nautechsystems.io
//
//  Licensed under the GNU Lesser General Public License Version 3.0 (the "License");
//  You may not use this file except in compliance with the License.
//  You may obtain a copy of the License at https://www.gnu.org/licenses/lgpl-3.0.en.html
//
//  Unless required by applicable law or agreed to in writing, software
//  distributed under the License is distributed on an "AS IS" BASIS,
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
//  limitations under the License.
// -------------------------------------------------------------------------------------------------
```

### Code Formatting

Import formatting is automatically handled by rustfmt when running `make format`.
The tool organizes imports into groups (standard library, external crates, local imports) and sorts them alphabetically within each group.

#### Function spacing

- Leave **one blank line between functions** (including tests) – this improves readability and
mirrors the default behavior of `rustfmt`.
- Leave **one blank line above every doc comment** (`///` or `//!`) so that the comment is clearly
  detached from the previous code block.

#### PyO3 naming convention

When exposing Rust functions to Python **via PyO3**:

1. The Rust symbol **must** be prefixed with `py_*` to make its purpose explicit inside the Rust
   codebase.
2. Use the `#[pyo3(name = "…")]` attribute to publish the *Python* name **without** the `py_`
   prefix so the Python API remains clean.

```rust
#[pyo3(name = "do_something")]
pub fn py_do_something() -> PyResult<()> {
    // …
}
```

### Error Handling

Use structured error handling patterns consistently:

1. **Primary Pattern**: Use `anyhow::Result<T>` for fallible functions:

   ```rust
   pub fn calculate_balance(&mut self) -> anyhow::Result<Money> {
       // Implementation
   }
   ```

2. **Custom Error Types**: Use `thiserror` for domain-specific errors:

   ```rust
   #[derive(Error, Debug)]
   pub enum NetworkError {
       #[error("Connection failed: {0}")]
       ConnectionFailed(String),
       #[error("Timeout occurred")]
       Timeout,
   }
   ```

3. **Error Propagation**: Use the `?` operator for clean error propagation.

4. **Error Creation**: Prefer `anyhow::bail!` for early returns with errors:

   ```rust
   // Preferred - using bail! for early returns
   pub fn process_value(value: i32) -> anyhow::Result<i32> {
       if value < 0 {
           anyhow::bail!("Value cannot be negative: {value}");
       }
       Ok(value * 2)
   }

   // Instead of - verbose return statement
   if value < 0 {
       return Err(anyhow::anyhow!("Value cannot be negative: {value}"));
   }
   ```

   **Note**: Use `anyhow::bail!` for early returns, but `anyhow::anyhow!` in closure contexts like `ok_or_else()` where early returns aren't possible.

5. **Error Message Formatting**: Prefer inline format strings over positional arguments:

   ```rust
   // Preferred - inline format with variable names
   anyhow::bail!("Failed to subtract {n} months from {datetime}");

   // Instead of - positional arguments
   anyhow::bail!("Failed to subtract {} months from {}", n, datetime);
   ```

   This makes error messages more readable and self-documenting, especially when there are multiple variables.

### Attribute Patterns

Consistent attribute usage and ordering:

```rust
#[repr(C)]
#[derive(Clone, Copy, Debug, Hash, PartialEq, Eq, PartialOrd, Ord)]
#[cfg_attr(
    feature = "python",
    pyo3::pyclass(module = "nautilus_trader.core.nautilus_pyo3.model")
)]
pub struct Symbol(Ustr);
```

For enums with extensive derive attributes:

```rust
#[repr(C)]
#[derive(
    Copy,
    Clone,
    Debug,
    Display,
    Hash,
    PartialEq,
    Eq,
    PartialOrd,
    Ord,
    AsRefStr,
    FromRepr,
    EnumIter,
    EnumString,
)]
#[strum(ascii_case_insensitive)]
#[strum(serialize_all = "SCREAMING_SNAKE_CASE")]
#[cfg_attr(
    feature = "python",
    pyo3::pyclass(eq, eq_int, module = "nautilus_trader.core.nautilus_pyo3.model.enums")
)]
pub enum AccountType {
    /// An account with unleveraged cash assets only.
    Cash = 1,
    /// An account which facilitates trading on margin, using account assets as collateral.
    Margin = 2,
}
```

### Constructor Patterns

Use the `new()` vs `new_checked()` convention consistently:

```rust
/// Creates a new [`Symbol`] instance with correctness checking.
///
/// # Errors
///
/// Returns an error if `value` is not a valid string.
///
/// # Notes
///
/// PyO3 requires a `Result` type for proper error handling and stacktrace printing in Python.
pub fn new_checked<T: AsRef<str>>(value: T) -> anyhow::Result<Self> {
    // Implementation
}

/// Creates a new [`Symbol`] instance.
///
/// # Panics
///
/// Panics if `value` is not a valid string.
pub fn new<T: AsRef<str>>(value: T) -> Self {
    Self::new_checked(value).expect(FAILED)
}
```

Always use the `FAILED` constant for `.expect()` messages related to correctness checks:

```rust
use nautilus_core::correctness::FAILED;
```

### Constants and Naming Conventions

Use SCREAMING_SNAKE_CASE for constants with descriptive names:

```rust
/// Number of nanoseconds in one second.
pub const NANOSECONDS_IN_SECOND: u64 = 1_000_000_000;

/// Bar specification for 1-minute last price bars.
pub const BAR_SPEC_1_MINUTE_LAST: BarSpecification = BarSpecification {
    step: NonZero::new(1).unwrap(),
    aggregation: BarAggregation::Minute,
    price_type: PriceType::Last,
};
```

### Re-export Patterns

Organize re-exports alphabetically and place at the end of lib.rs files:

```rust
// Re-exports
pub use crate::{
    nanos::UnixNanos,
    time::AtomicTime,
    uuid::UUID4,
};

// Module-level re-exports
pub use crate::identifiers::{
    account_id::AccountId,
    actor_id::ActorId,
    client_id::ClientId,
};
```

### Documentation Standards

#### Module-Level Documentation

All modules must have module-level documentation starting with a brief description:

```rust
//! Functions for correctness checks similar to the *design by contract* philosophy.
//!
//! This module provides validation checking of function or method conditions.
//!
//! A condition is a predicate which must be true just prior to the execution of
//! some section of code - for correct behavior as per the design specification.
```

For modules with feature flags, document them clearly:

```rust
//! # Feature flags
//!
//! This crate provides feature flags to control source code inclusion during compilation,
//! depending on the intended use case:
//!
//! - `ffi`: Enables the C foreign function interface (FFI) from [cbindgen](https://github.com/mozilla/cbindgen).
//! - `python`: Enables Python bindings from [PyO3](https://pyo3.rs).
//! - `stubs`: Enables type stubs for use in testing scenarios.
```

#### Field Documentation

All struct and enum fields must have documentation with terminating periods:

```rust
pub struct Currency {
    /// The currency code as an alpha-3 string (e.g., "USD", "EUR").
    pub code: Ustr,
    /// The currency decimal precision.
    pub precision: u8,
    /// The ISO 4217 currency code.
    pub iso4217: u16,
    /// The full name of the currency.
    pub name: Ustr,
    /// The currency type, indicating its category (e.g. Fiat, Crypto).
    pub currency_type: CurrencyType,
}
```

#### Function Documentation

Document all public functions with:

- Purpose and behavior
- Explanation of input argument usage
- Error conditions (if applicable)
- Panic conditions (if applicable)

```rust
/// Returns a reference to the `AccountBalance` for the specified currency, or `None` if absent.
///
/// # Panics
///
/// Panics if `currency` is `None` and `self.base_currency` is `None`.
pub fn base_balance(&self, currency: Option<Currency>) -> Option<&AccountBalance> {
    // Implementation
}
```

#### Errors and Panics Documentation Format

For single line errors and panics documentation, use sentence case with the following convention:

```rust
/// Returns a reference to the `AccountBalance` for the specified currency, or `None` if absent.
///
/// # Errors
///
/// Returns an error if the currency conversion fails.
///
/// # Panics
///
/// Panics if `currency` is `None` and `self.base_currency` is `None`.
pub fn base_balance(&self, currency: Option<Currency>) -> anyhow::Result<Option<&AccountBalance>> {
    // Implementation
}
```

For multi-line errors and panics documentation, use sentence case with bullets and terminating periods:

```rust
/// Calculates the unrealized profit and loss for the position.
///
/// # Errors
///
/// This function will return an error if:
/// - The market price for the instrument cannot be found.
/// - The conversion rate calculation fails.
/// - Invalid position state is encountered.
///
/// # Panics
///
/// This function will panic if:
/// - The instrument ID is invalid or uninitialized.
/// - Required market data is missing from the cache.
/// - Internal state consistency checks fail.
pub fn calculate_unrealized_pnl(&self, market_price: Price) -> anyhow::Result<Money> {
    // Implementation
}
```

#### Safety Documentation Format

For Safety documentation, use the `SAFETY:` prefix followed by a short description explaining why the unsafe operation is valid:

```rust
/// Creates a new instance from raw components without validation.
///
/// # Safety
///
/// The caller must ensure that all input parameters are valid and properly initialized.
pub unsafe fn from_raw_parts(ptr: *const u8, len: usize) -> Self {
    // SAFETY: Caller guarantees ptr is valid and len is correct
    Self {
        data: std::slice::from_raw_parts(ptr, len),
    }
}
```

For inline unsafe blocks, use the `SAFETY:` comment directly above the unsafe code:

```rust
impl Send for MessageBus {
    fn send(&self) {
        // SAFETY: Message bus is not meant to be passed between threads
        unsafe {
            // unsafe operation here
        }
    }
}
```

### Testing Conventions

#### Test Organization

Use consistent test module structure with section separators:

```rust
////////////////////////////////////////////////////////////////////////////////
// Tests
////////////////////////////////////////////////////////////////////////////////
#[cfg(test)]
mod tests {
    use rstest::rstest;
    use super::*;
    use crate::identifiers::{Symbol, stubs::*};

    #[rstest]
    fn test_string_reprs(symbol_eth_perp: Symbol) {
        assert_eq!(symbol_eth_perp.as_str(), "ETH-PERP");
        assert_eq!(format!("{symbol_eth_perp}"), "ETH-PERP");
    }
}
```

#### Parameterized Testing

Use the `rstest` attribute consistently, and for parameterized tests:

```rust
#[rstest]
#[case("AUDUSD", false)]
#[case("AUD/USD", false)]
#[case("CL.FUT", true)]
fn test_symbol_is_composite(#[case] input: &str, #[case] expected: bool) {
    let symbol = Symbol::new(input);
    assert_eq!(symbol.is_composite(), expected);
}
```

#### Test Naming

Use descriptive test names that explain the scenario:

```rust
fn test_sma_with_no_inputs()
fn test_sma_with_single_input()
fn test_symbol_is_composite()
```

## Unsafe Rust

It will be necessary to write `unsafe` Rust code to be able to achieve the value
of interoperating between Cython and Rust. The ability to step outside the boundaries of safe Rust is what makes it possible to
implement many of the most fundamental features of the Rust language itself, just as C and C++ are used to implement
their own standard libraries.

Great care will be taken with the use of Rusts `unsafe` facility - which just enables a small set of additional language features, thereby changing
the contract between the interface and caller, shifting some responsibility for guaranteeing correctness
from the Rust compiler, and onto us. The goal is to realize the advantages of the `unsafe` facility, whilst avoiding *any* undefined behavior.
The definition for what the Rust language designers consider undefined behavior can be found in the [language reference](https://doc.rust-lang.org/stable/reference/behavior-considered-undefined.html).

### Safety Policy

To maintain correctness, any use of `unsafe` Rust must follow our policy:

- If a function is `unsafe` to call, there *must* be a `Safety` section in the documentation explaining why the function is `unsafe`.
and covering the invariants which the function expects the callers to uphold, and how to meet their obligations in that contract.
- Document why each function is `unsafe` in its doc comment's Safety section, and cover all `unsafe` blocks with unit tests.
- Always include a `SAFETY:` comment explaining why the unsafe operation is valid:

```rust
// SAFETY: Message bus is not meant to be passed between threads
#[allow(unsafe_code)]
unsafe impl Send for MessageBus {}
```

## Tooling Configuration

The project uses several tools for code quality:

- **rustfmt**: Automatic code formatting (see `rustfmt.toml`).
- **clippy**: Linting and best practices (see `clippy.toml`).
- **cbindgen**: C header generation for FFI.

## Resources

- [The Rustonomicon](https://doc.rust-lang.org/nomicon/) – The Dark Arts of Unsafe Rust.
- [The Rust Reference – Unsafety](https://doc.rust-lang.org/stable/reference/unsafety.html).
- [Safe Bindings in Rust – Russell Johnston](https://www.abubalay.com/blog/2020/08/22/safe-bindings-in-rust).
- [Google – Rust and C interoperability](https://www.chromium.org/Home/chromium-security/memory-safety/rust-and-c-interoperability/).


---

file path: ./dev_guide/coding_standards.md
# Coding Standards

## Code Style

The current codebase can be used as a guide for formatting conventions.
Additional guidelines are provided below.

### Universal formatting rules

The following applies to **all** source files (Rust, Python, Cython, shell, etc.):

- Use **spaces only**, never hard tab characters.
- Lines should generally stay below **100 characters**; wrap thoughtfully when necessary.
- Prefer American English spelling (`color`, `serialize`, `behavior`).

### Comment conventions

1. Generally leave **one blank line above** every comment block or docstring so it is visually separated from code.
2. Use *sentence case* – capitalize the first letter, keep the rest lowercase unless proper nouns or acronyms.
3. Do not use double spaces after periods.
4. **Single-line comments** *must not* end with a period *unless* the line ends with a URL or inline Markdown link – in those cases leave the punctuation exactly as the link requires.
5. **Multi-line comments** should separate sentences with commas (not period-per-line). The final line *should* end with a period.
6. Keep comments concise; favor clarity and only explain the non-obvious – *less is more*.
7. Avoid emoji symbols in text.

### Doc comment / docstring mood

- **Python** docstrings should be written in the **imperative mood** – e.g. *“Return a cached client.”*
- **Rust** doc comments should be written in the **indicative mood** – e.g. *“Returns a cached client.”*

These conventions align with the prevailing styles of each language ecosystem and make generated
documentation feel natural to end-users.

### Formatting

1. For longer lines of code, and when passing more than a couple of arguments, you should take a new line which aligns at the next logical indent (rather than attempting a hanging 'vanity' alignment off an opening parenthesis). This practice conserves space to the right, ensures important code is more central in view, and is also robust to function/method name changes.

2. The closing parenthesis should be located on a new line, aligned at the logical indent.

3. Also ensure multiple hanging parameters or arguments end with a trailing comma:

```python
long_method_with_many_params(
    some_arg1,
    some_arg2,
    some_arg3,  # <-- trailing comma
)
```

### PEP-8

The codebase generally follows the PEP-8 style guide. Even though C typing is taken advantage of in the Cython parts of the codebase, we still aim to be idiomatic of Python where possible.
One notable departure is that Python truthiness is not always taken advantage of to check if an argument is `None` for everything other than collections.

There are two reasons for this;

1. Cython can generate more efficient C code from `is None` and `is not None`, rather than entering the Python runtime to check the `PyObject` truthiness.

2. As per the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) - it’s discouraged to use truthiness to check if an argument is/is not `None`, when there is a chance an unexpected object could be passed into the function or method which will yield an unexpected truthiness evaluation (which could result in a logical error type bug).

*“Always use if foo is None: (or is not None) to check for a None value. E.g., when testing whether a variable or argument that defaults to None was set to some other value. The other value might be a value that’s false in a boolean context!”*

There are still areas that aren’t performance-critical where truthiness checks for `None` (`if foo is None:` vs `if not foo:`) will be acceptable for clarity.

:::note
Use truthiness to check for empty collections (e.g., `if not my_list:`) rather than comparing explicitly to `None` or empty.
:::

We welcome all feedback on where the codebase departs from PEP-8 for no apparent reason.

## Python Style Guide

### Type Hints

All function and method signatures *must* include comprehensive type annotations:

```python
def __init__(self, config: EMACrossConfig) -> None:
def on_bar(self, bar: Bar) -> None:
def on_save(self) -> dict[str, bytes]:
def on_load(self, state: dict[str, bytes]) -> None:
```

**Generic Types**: Use `TypeVar` for reusable components

```python
T = TypeVar("T")
class ThrottledEnqueuer(Generic[T]):
```

### Docstrings

The [NumPy docstring spec](https://numpydoc.readthedocs.io/en/latest/format.html) is used throughout the codebase.
This needs to be adhered to consistently to ensure the docs build correctly.

**Test method naming**: Descriptive names explaining the scenario:

```python
def test_currency_with_negative_precision_raises_overflow_error(self):
def test_sma_with_no_inputs_returns_zero_count(self):
def test_sma_with_single_input_returns_expected_value(self):
```

### Ruff

[ruff](https://astral.sh/ruff) is utilized to lint the codebase. Ruff rules can be found in the top-level `pyproject.toml`, with ignore justifications typically commented.

### Commit messages

Here are some guidelines for the style of your commit messages:

1. Limit subject titles to 60 characters or fewer. Capitalize subject line and do not end with period.

2. Use 'imperative voice', i.e. the message should describe what the commit will do if applied.

3. Optional: Use the body to explain change. Separate from subject with a blank line. Keep under 100 character width. You can use bullet points with or without terminating periods.

4. Optional: Provide # references to relevant issues or tickets.

5. Optional: Provide any hyperlinks which are informative.


---

file path: ./dev_guide/testing.md
# Testing

The test suite is divided into broad categories of tests including:

- Unit tests
- Integration tests
- Acceptance tests
- Performance tests
- Memory leak tests

The performance tests exist to aid development of performance-critical components.

Tests can be run using [pytest](https://docs.pytest.org), which is our primary test runner. We recommend using parametrized tests and fixtures (e.g., `@pytest.mark.parametrize`) to avoid repetitive code and improve clarity.

## Running Tests

### Python Tests

From the repository root:

```bash
make pytest
# or
uv run --active --no-sync pytest --new-first --failed-first
# or simply
pytest
```

For performance tests:

```bash
make test-performance
# or
uv run --active --no-sync pytest tests/performance_tests --benchmark-disable-gc --codspeed
```

### Rust Tests

```bash
make cargo-test
# or
cargo nextest run --workspace --features "python,ffi,high-precision,defi" --cargo-profile nextest
```

### IDE Integration

- **PyCharm**: Right-click on tests folder or file → "Run pytest"
- **VS Code**: Use the Python Test Explorer extension

## Mocks

Unit tests will often include other components acting as mocks. The intent of this is to simplify
the test suite to avoid extensive use of a mocking framework, although `MagicMock` objects are
currently used in particular cases.

## Code Coverage

Code coverage output is generated using `coverage` and reported using [codecov](https://about.codecov.io/).

High test coverage is a goal for the project however not at the expense of appropriate error
handling, or causing “test induced damage” to the architecture.

There are currently areas of the codebase which are impossible to test unless there is a change to
the production code. For example the last condition check of an if-else block which would catch an
unrecognized value, these should be left in place in case there is a change to the production code - which these checks could then catch.

Other design-time exceptions may also be impossible to test for, and so 100% test coverage is not
the ultimate goal.

### Style guidance

- **Group assertions** where possible – perform all setup/act steps first, then assert expectations together at
  the end of the test to avoid the *act-assert-act* smell.
- Using `unwrap`, `expect`, or direct `panic!`/`assert` calls inside **tests** is acceptable. The
  clarity and conciseness of the test suite outweigh defensive error-handling that is required in
  production code.

## Excluded code coverage

The `pragma: no cover` comments found throughout the codebase [exclude code from test coverage](https://coverage.readthedocs.io/en/coverage-4.3.3/excluding.html).
The reason for their use is to reduce redundant/needless tests just to keep coverage high, such as:

- Asserting an abstract method raises `NotImplementedError` when called.
- Asserting the final condition check of an if-else block when impossible to test (as above).

These tests are expensive to maintain (as they must be kept in line with any refactorings), and
offer little to no benefit in return. The intention is for all abstract method
implementations to be fully covered by tests. Therefore `pragma: no cover` should be judiciously
removed when no longer appropriate, and its use *restricted* to the above cases.

## Debugging Rust Tests

Rust tests can be debugged using the default test configuration.

If you want to run all tests while compiling with debug symbols for later debugging some tests individually,
run `make cargo-test-debug` instead of `make cargo-test`.

In IntellijIdea, to debug parametrised tests starting with `#[rstest]` with arguments defined in the header of the test
you need to modify the run configuration of the test so it looks like
`test --package nautilus-model --lib data::bar::tests::test_get_time_bar_start::case_1`
(remove `-- --exact` at the end of the string and append `::case_n` where `n` is an integer corresponding to
the n-th parametrised test starting at 1).
The reason for this is [here](https://github.com/rust-lang/rust-analyzer/issues/8964#issuecomment-871592851)
(the test is expanded into a module with several functions named `case_n`).
In VSCode, it is possible to directly select which test case to debug.


---

file path: ./dev_guide/benchmarking.md
# Benchmarking

This guide explains how NautilusTrader measures Rust performance, when to
use each tool and the conventions you should follow when adding new benches.

---

## Tooling overview

Nautilus Trader relies on **two complementary benchmarking frameworks**:

| Framework | What is it? | What it measures | When to prefer it |
|-----------|-------------|------------------|-------------------|
| [**Criterion**](https://docs.rs/criterion/latest/criterion/) | Statistical benchmark harness that produces detailed HTML reports and performs outlier detection. | Wall-clock run time with confidence intervals. | End-to-end scenarios, anything slower than ≈100 ns, visual comparisons. |
| [**iai**](https://docs.rs/iai/latest/iai/) | Deterministic micro-benchmark harness that counts retired CPU instructions via hardware counters. | Exact instruction counts (noise-free). | Ultra-fast functions, CI gating via instruction diff. |

Most hot code paths benefit from **both** kinds of measurements.

---

## Directory layout

Each crate keeps its performance tests in a local `benches/` folder:

```text
crates/<crate_name>/
└── benches/
    ├── foo_criterion.rs   # Criterion group(s)
    └── foo_iai.rs         # iai micro benches
```

`Cargo.toml` must list every benchmark explicitly so `cargo bench` discovers
them:

```toml
[[bench]]
name = "foo_criterion"             # file stem in benches/
path = "benches/foo_criterion.rs"
harness = false                    # disable the default libtest harness
```

---

## Writing Criterion benchmarks

1. Perform **all expensive set-up outside** the timing loop (`b.iter`).
2. Wrap inputs/outputs in `black_box` to prevent the optimizer from removing
   work.
3. Group related cases with `benchmark_group!` and set `throughput` or
   `sample_size` when the defaults aren’t ideal.

```rust
use criterion::{black_box, Criterion, criterion_group, criterion_main};

fn bench_my_algo(c: &mut Criterion) {
    let data = prepare_data(); // heavy set-up done once

    c.bench_function("my_algo", |b| {
        b.iter(|| my_algo(black_box(&data)));
    });
}

criterion_group!(benches, bench_my_algo);
criterion_main!(benches);
```

---

## Writing iai benchmarks

`iai` requires functions that take **no parameters** and return a value (which
can be ignored). Keep them as small as possible so the measured instruction
count is meaningful.

```rust
use iai::black_box;

fn bench_add() -> i64 {
    let a = black_box(123);
    let b = black_box(456);
    a + b
}

iai::main!(bench_add);
```

---

## Running benches locally

- **All benches** for every crate: `make cargo-bench` (delegates to `cargo bench`).
- **Single crate**: `cargo bench -p nautilus-core`.
- **Single benchmark file**: `cargo bench -p nautilus-core --bench time`.

Criterion writes HTML reports to `target/criterion/`; open `target/criterion/report/index.html` in your browser.

### Generating a flamegraph

`cargo-flamegraph` (a thin wrapper around Linux `perf`) lets you see a sampled
call-stack profile of a single benchmark.

1. Install once per machine (the crate is called `flamegraph`; it installs a
   `cargo flamegraph` subcommand automatically). Linux requires `perf` to be
   available (`sudo apt install linux-tools-common linux-tools-$(uname -r)` on
   Debian/Ubuntu):

   ```bash
   cargo install flamegraph
   ```

2. Run a specific bench with the symbol-rich `bench` profile:

   ```bash
   # example: the matching benchmark in nautilus-common
   cargo flamegraph --bench matching -p nautilus-common --profile bench
   ```

3. Open the generated `flamegraph.svg` (or `.png`) in your browser and zoom
   into hot paths.

   If you see an error mentioning `perf_event_paranoid` you need to relax the
   kernel’s perf restrictions for the current session (root required):

   ```bash
   sudo sh -c 'echo 1 > /proc/sys/kernel/perf_event_paranoid'
   ```

   A value of `1` is typically enough; set it back to `2` (default) or make
   the change permanent via `/etc/sysctl.conf` if desired.

Because `[profile.bench]` keeps full debug symbols the SVG will show readable
function names without bloating production binaries (which still use
`panic = "abort"` and are built via `[profile.release]`).

> **Note** Benchmark binaries are compiled with the custom `[profile.bench]`
> defined in the workspace `Cargo.toml`.  That profile inherits from
> `release-debugging`, preserving full optimisation *and* debug symbols so that
> tools like `cargo flamegraph` or `perf` produce human-readable stack traces.

---

## Templates

Ready-to-copy starter files live in `docs/dev_templates/`.

- **Criterion**: `criterion_template.rs`
- **iai**: `iai_template.rs`

Copy the template into `benches/`, adjust imports and names, and start measuring!


---

file path: ./dev_guide/adapters.md
# Adapters

## Introduction

This developer guide provides instructions on how to develop an integration adapter for the NautilusTrader platform.
Adapters provide connectivity to trading venues and data providers—translating raw venue APIs into Nautilus’s unified interface and normalized domain model.

## Structure of an adapter

An adapter typically consists of several components:

1. **Instrument Provider**: Supplies instrument definitions
2. **Data Client**: Handles live market data feeds and historical data requests
3. **Execution Client**: Handles order execution and management
4. **Configuration**: Configures the client settings

## Adapter implementation steps

1. Create a new Python subpackage for your adapter
2. Implement the Instrument Provider by inheriting from `InstrumentProvider` and implementing the necessary methods to load instruments
3. Implement the Data Client by inheriting from either the `LiveDataClient` and `LiveMarketDataClient` class as applicable, providing implementations for the required methods
4. Implement the Execution Client by inheriting from `LiveExecutionClient` and providing implementations for the required methods
5. Create configuration classes to hold your adapter’s settings
6. Test your adapter thoroughly to ensure all methods are correctly implemented and the adapter works as expected (see the [Testing Guide](testing.md)).

## Template for building an adapter

Below is a step-by-step guide to building an adapter for a new data provider using the provided template.

### InstrumentProvider

The `InstrumentProvider` supplies instrument definitions available on the venue. This
includes loading all available instruments, specific instruments by ID, and applying filters to the
instrument list.

```python
from nautilus_trader.common.providers import InstrumentProvider
from nautilus_trader.model import InstrumentId

class TemplateInstrumentProvider(InstrumentProvider):
    """
    An example template of an ``InstrumentProvider`` showing the minimal methods which must be implemented for an integration to be complete.
    """

    async def load_all_async(self, filters: dict | None = None) -> None:
        raise NotImplementedError("implement `load_all_async` in your adapter subclass")

    async def load_ids_async(self, instrument_ids: list[InstrumentId], filters: dict | None = None) -> None:
        raise NotImplementedError("implement `load_ids_async` in your adapter subclass")

    async def load_async(self, instrument_id: InstrumentId, filters: dict | None = None) -> None:
        raise NotImplementedError("implement `load_async` in your adapter subclass")
```

**Key Methods**:

- `load_all_async`: Loads all instruments asynchronously, optionally applying filters
- `load_ids_async`: Loads specific instruments by their IDs
- `load_async`: Loads a single instrument by its ID

### DataClient

The `LiveDataClient` handles the subscription and management of data feeds that are not specifically
related to market data. This might include news feeds, custom data streams, or other data sources
that enhance trading strategies but do not directly represent market activity.

```python
from nautilus_trader.live.data_client import LiveDataClient
from nautilus_trader.model import DataType
from nautilus_trader.core import UUID4

class TemplateLiveDataClient(LiveDataClient):
    """
    An example of a ``LiveDataClient`` highlighting the overridable abstract methods.
    """

    async def _connect(self) -> None:
        raise NotImplementedError("implement `_connect` in your adapter subclass")

    async def _disconnect(self) -> None:
        raise NotImplementedError("implement `_disconnect` in your adapter subclass")

    def reset(self) -> None:
        raise NotImplementedError("implement `reset` in your adapter subclass")

    def dispose(self) -> None:
        raise NotImplementedError("implement `dispose` in your adapter subclass")

    async def _subscribe(self, data_type: DataType) -> None:
        raise NotImplementedError("implement `_subscribe` in your adapter subclass")

    async def _unsubscribe(self, data_type: DataType) -> None:
        raise NotImplementedError("implement `_unsubscribe` in your adapter subclass")

    async def _request(self, data_type: DataType, correlation_id: UUID4) -> None:
        raise NotImplementedError("implement `_request` in your adapter subclass")
```

**Key Methods**:

- `_connect`: Establishes a connection to the data provider
- `_disconnect`: Closes the connection to the data provider
- `reset`: Resets the state of the client
- `dispose`: Disposes of any resources held by the client
- `_subscribe`: Subscribes to a specific data type
- `_unsubscribe`: Unsubscribes from a specific data type
- `_request`: Requests data from the provider

### MarketDataClient

The `MarketDataClient` handles market-specific data such as order books, top-of-book quotes and trades,
and instrument status updates. It focuses on providing historical and real-time market data that is essential for
trading operations.

```python
from nautilus_trader.live.data_client import LiveMarketDataClient
from nautilus_trader.model import BarType, DataType
from nautilus_trader.model import InstrumentId
from nautilus_trader.model.enums import BookType

class TemplateLiveMarketDataClient(LiveMarketDataClient):
    """
    An example of a ``LiveMarketDataClient`` highlighting the overridable abstract methods.
    """

    async def _connect(self) -> None:
        raise NotImplementedError("implement `_connect` in your adapter subclass")

    async def _disconnect(self) -> None:
        raise NotImplementedError("implement `_disconnect` in your adapter subclass")

    def reset(self) -> None:
        raise NotImplementedError("implement `reset` in your adapter subclass")

    def dispose(self) -> None:
        raise NotImplementedError("implement `dispose` in your adapter subclass")

    async def _subscribe_instruments(self) -> None:
        raise NotImplementedError("implement `_subscribe_instruments` in your adapter subclass")

    async def _unsubscribe_instruments(self) -> None:
        raise NotImplementedError("implement `_unsubscribe_instruments` in your adapter subclass")

    async def _subscribe_order_book_deltas(self, instrument_id: InstrumentId, book_type: BookType, depth: int | None = None, kwargs: dict | None = None) -> None:
        raise NotImplementedError("implement `_subscribe_order_book_deltas` in your adapter subclass")

    async def _unsubscribe_order_book_deltas(self, instrument_id: InstrumentId) -> None:
        raise NotImplementedError("implement `_unsubscribe_order_book_deltas` in your adapter subclass")
```

**Key Methods**:

- `_connect`: Establishes a connection to the venues APIs
- `_disconnect`: Closes the connection to the venues APIs
- `reset`: Resets the state of the client
- `dispose`: Disposes of any resources held by the client
- `_subscribe_instruments`: Subscribes to market data for multiple instruments
- `_unsubscribe_instruments`: Unsubscribes from market data for multiple instruments
- `_subscribe_order_book_deltas`: Subscribes to order book delta updates
- `_unsubscribe_order_book_deltas`: Unsubscribes from order book delta updates

---

## REST‐API field-mapping guideline

When translating a venue’s REST payload into our domain model **avoid renaming** the upstream
fields unless there is a compelling reason (e.g. a clash with reserved keywords). The only
transformation we apply by default is **camelCase → snake_case**.

Keeping the external names intact makes it trivial to debug payloads, compare captures against the
Rust structs, and speeds up onboarding for new contributors who have the venue’s API reference
open side-by-side.

### ExecutionClient

The `ExecutionClient` is responsible for order management, including submission, modification, and
cancellation of orders. It is a crucial component of the adapter that interacts with the venues
trading system to manage and execute trades.

```python
from nautilus_trader.execution.messages import BatchCancelOrders, CancelAllOrders, CancelOrder, ModifyOrder, SubmitOrder
from nautilus_trader.execution.reports import FillReport, OrderStatusReport, PositionStatusReport
from nautilus_trader.live.execution_client import LiveExecutionClient
from nautilus_trader.model import ClientOrderId, InstrumentId, VenueOrderId

class TemplateLiveExecutionClient(LiveExecutionClient):
    """
    An example of a ``LiveExecutionClient`` highlighting the method requirements.
    """

    async def _connect(self) -> None:
        raise NotImplementedError("implement `_connect` in your adapter subclass")

    async def _disconnect(self) -> None:
        raise NotImplementedError("implement `_disconnect` in your adapter subclass")

    async def _submit_order(self, command: SubmitOrder) -> None:
        raise NotImplementedError("implement `_submit_order` in your adapter subclass")

    async def _modify_order(self, command: ModifyOrder) -> None:
        raise NotImplementedError("implement `_modify_order` in your adapter subclass")

    async def _cancel_order(self, command: CancelOrder) -> None:
        raise NotImplementedError("implement `_cancel_order` in your adapter subclass")

    async def _cancel_all_orders(self, command: CancelAllOrders) -> None:
        raise NotImplementedError("implement `_cancel_all_orders` in your adapter subclass")

    async def _batch_cancel_orders(self, command: BatchCancelOrders) -> None:
        raise NotImplementedError("implement `_batch_cancel_orders` in your adapter subclass")

    async def generate_order_status_report(
        self, instrument_id: InstrumentId, client_order_id: ClientOrderId | None = None, venue_order_id: VenueOrderId | None = None
    ) -> OrderStatusReport | None:
        raise NotImplementedError("method `generate_order_status_report` must be implemented in the subclass")

    async def generate_order_status_reports(
        self, instrument_id: InstrumentId | None = None, start: pd.Timestamp | None = None, end: pd.Timestamp | None = None, open_only: bool = False
    ) -> list[OrderStatusReport]:
        raise NotImplementedError("method `generate_order_status_reports` must be implemented in the subclass")

    async def generate_fill_reports(
        self, instrument_id: InstrumentId | None = None, venue_order_id: VenueOrderId | None = None, start: pd.Timestamp | None = None, end: pd.Timestamp | None = None
    ) -> list[FillReport]:
        raise NotImplementedError("method `generate_fill_reports` must be implemented in the subclass")

    async def generate_position_status_reports(
        self, instrument_id: InstrumentId | None = None, start: pd.Timestamp | None = None, end: pd.Timestamp | None = None
    ) -> list[PositionStatusReport]:
        raise NotImplementedError("method `generate_position_status_reports` must be implemented in the subclass")
```

**Key Methods**:

- `_connect`: Establishes a connection to the venues APIs
- `_disconnect`: Closes the connection to the venues APIs
- `_submit_order`: Submits a new order to the venue
- `_modify_order`: Modifies an existing order on the venue
- `_cancel_order`: Cancels a specific order on the venue
- `_cancel_all_orders`: Cancels all orders for an instrument on the venue
- `_batch_cancel_orders`: Cancels a batch of orders for an instrument on the venue
- `generate_order_status_report`: Generates a report for a specific order on the venue
- `generate_order_status_reports`: Generates reports for all orders on the venue
- `generate_fill_reports`: Generates reports for filled orders on the venue
- `generate_position_status_reports`: Generates reports for position status on the venue

### Configuration

The configuration file defines settings specific to the adapter, such as API keys and connection
details. These settings are essential for initializing and managing the adapter’s connection to the
data provider.

```python
from nautilus_trader.config import LiveDataClientConfig, LiveExecClientConfig

class TemplateDataClientConfig(LiveDataClientConfig):
    """
    Configuration for ``TemplateDataClient`` instances.
    """

    api_key: str
    api_secret: str
    base_url: str

class TemplateExecClientConfig(LiveExecClientConfig):
    """
    Configuration for ``TemplateExecClient`` instances.
    """

    api_key: str
    api_secret: str
    base_url: str
```

**Key Attributes**:

- `api_key`: The API key for authenticating with the data provider
- `api_secret`: The API secret for authenticating with the data provider
- `base_url`: The base URL for connecting to the data provider’s API


---

file path: ./api_reference/backtest.md
# Backtest

```{eval-rst}
.. automodule:: nautilus_trader.backtest
```

```{eval-rst}
.. automodule:: nautilus_trader.backtest.auction
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.backtest.data_client
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.backtest.engine
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.backtest.exchange
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.backtest.execution_client
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.backtest.models
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.backtest.modules
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.backtest.node
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.backtest.results
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/analysis.md
# Analysis

```{eval-rst}
.. automodule:: nautilus_trader.analysis
```

```{eval-rst}
.. automodule:: nautilus_trader.analysis.analyzer
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.analysis.reporter
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.analysis.statistic
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.analysis.statistics.expectancy
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.analysis.statistics.long_ratio
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.analysis.statistics.loser_avg
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.analysis.statistics.loser_max
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.analysis.statistics.loser_min
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.analysis.statistics.profit_factor
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.analysis.statistics.returns_avg
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.analysis.statistics.returns_avg_loss
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.analysis.statistics.returns_avg_win
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.analysis.statistics.returns_volatility
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.analysis.statistics.risk_return_ratio
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.analysis.statistics.sharpe_ratio
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.analysis.statistics.sortino_ratio
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.analysis.statistics.win_rate
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.analysis.statistics.winner_avg
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.analysis.statistics.winner_max
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.analysis.statistics.winner_min
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/cache.md
# Cache

```{eval-rst}
.. automodule:: nautilus_trader.cache
```

```{eval-rst}
.. automodule:: nautilus_trader.cache.cache
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.cache.database
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.cache.base
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/common.md
# Common

```{eval-rst}
.. automodule:: nautilus_trader.common
```

```{eval-rst}
.. automodule:: nautilus_trader.common.actor
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.common.factories
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Component

```{eval-rst}
.. automodule:: nautilus_trader.common.component
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Executor

```{eval-rst}
.. automodule:: nautilus_trader.common.executor
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Generators

```{eval-rst}
.. automodule:: nautilus_trader.common.generators
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.common.providers
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/accounting.md
# Accounting

```{eval-rst}
.. automodule:: nautilus_trader.accounting
```

```{eval-rst}
.. automodule:: nautilus_trader.accounting.accounts.cash
    :show-inheritance:
    :inherited-members:
    :members:
    :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.accounting.accounts.margin
    :show-inheritance:
    :inherited-members:
    :members:
    :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.accounting.calculators
    :show-inheritance:
    :inherited-members:
    :members:
    :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.accounting.factory
    :show-inheritance:
    :inherited-members:
    :members:
    :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.accounting.manager
    :show-inheritance:
    :inherited-members:
    :members:
    :member-order: bysource
```


---

file path: ./api_reference/index.md
# Python API

Welcome to the Python API reference for NautilusTrader!

The API reference provides detailed technical documentation for the NautilusTrader framework,
including its modules, classes, methods, and functions. The reference is automatically generated
from the latest NautilusTrader source code using [Sphinx](https://www.sphinx-doc.org/en/master/).

Please note that there are separate references for different versions of NautilusTrader:

- **Latest**: This API reference is built from the head of the `develop` branch and represents the latest stable release.
- **Nightly**: This API reference is built from the head of the `nightly` branch and represents bleeding edge and experimental changes/features currently in development.

You can select the desired API reference from the **Versions** top left drop down menu.

Use the right navigation sidebar to explore the available modules and their contents.
You can click on any item to view its detailed documentation, including parameter descriptions, and return value explanations.

## Why Python?

Python was originally created decades ago as a simple scripting language with a clean straight
forward syntax. It has since evolved into a fully fledged general purpose object-oriented
programming language. Based on the TIOBE index, Python is currently the most popular programming language in the world.
Not only that, Python has become the *de facto lingua franca* of data science, machine learning, and artificial intelligence.

The language out of the box is not without its drawbacks however, especially in the context of
implementing large performance-critical systems. Cython has addressed a lot of these issues, offering all the advantages
of a statically typed language, embedded into Python's rich ecosystem of software libraries and
developer/user communities.


---

file path: ./api_reference/live.md
# Live

```{eval-rst}
.. automodule:: nautilus_trader.live
```

```{eval-rst}
.. automodule:: nautilus_trader.live.data_client
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.live.data_engine
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.live.execution_client
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.live.execution_engine
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.live.risk_engine
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.live.node
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.live.node_builder
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/trading.md
# Trading

```{eval-rst}
.. automodule:: nautilus_trader.trading
```

```{eval-rst}
.. automodule:: nautilus_trader.trading.controller
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.trading.filters
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.trading.strategy
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.trading.trader
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/system.md
# System

```{eval-rst}
.. automodule:: nautilus_trader.system
```

```{eval-rst}
.. automodule:: nautilus_trader.system.kernel
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/core.md
# Core

```{eval-rst}
.. automodule:: nautilus_trader.core
```

## Datetime

```{eval-rst}
.. automodule:: nautilus_trader.core.datetime
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Finite-State Machine (FSM)

```{eval-rst}
.. automodule:: nautilus_trader.core.fsm
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Message

```{eval-rst}
.. automodule:: nautilus_trader.core.message
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Stats

```{eval-rst}
.. automodule:: nautilus_trader.core.stats
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## UUID

```{eval-rst}
.. automodule:: nautilus_trader.core.uuid
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/serialization.md
# Serialization

```{eval-rst}
.. automodule:: nautilus_trader.serialization
```

```{eval-rst}
.. automodule:: nautilus_trader.serialization.serializer
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.serialization.base
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/indicators.md
# Indicators

```{eval-rst}
.. automodule:: nautilus_trader.indicators
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.average.ama
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.average.ema
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.donchian_channel
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.average.hma
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.average.ma_factory
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.average.sma
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.average.wma
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.atr
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.bollinger_bands
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.efficiency_ratio
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.fuzzy_candlesticks
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.keltner_channel
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.keltner_position
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.macd
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.obv
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.pressure
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.roc
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.rsi
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.spread_analyzer
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.stochastics
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.swings
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.volatility_ratio
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.vwap
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.average.moving_average
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.indicators.base.indicator
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/persistence.md
# Persistence

```{eval-rst}
.. automodule:: nautilus_trader.persistence
```

```{eval-rst}
.. automodule:: nautilus_trader.persistence.catalog.base
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.persistence.catalog.parquet
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.persistence.wranglers
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.persistence.writer
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/risk.md
# Risk

```{eval-rst}
.. automodule:: nautilus_trader.risk
```

```{eval-rst}
.. automodule:: nautilus_trader.risk.engine
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.risk.sizing
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/portfolio.md
# Portfolio

```{eval-rst}
.. automodule:: nautilus_trader.portfolio
```

```{eval-rst}
.. automodule:: nautilus_trader.portfolio.portfolio
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.portfolio.base
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/data.md
# Data

```{eval-rst}
.. automodule:: nautilus_trader.data
```

## Aggregation

```{eval-rst}
.. automodule:: nautilus_trader.data.aggregation
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Client

```{eval-rst}
.. automodule:: nautilus_trader.data.client
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Engine

```{eval-rst}
.. automodule:: nautilus_trader.data.engine
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Messages

```{eval-rst}
.. automodule:: nautilus_trader.data.messages
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/execution.md
# Execution

```{eval-rst}
.. automodule:: nautilus_trader.execution
```

## Components

```{eval-rst}
.. automodule:: nautilus_trader.execution.algorithm
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.execution.client
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.execution.emulator
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.execution.engine
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.execution.manager
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.execution.matching_core
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Messages

```{eval-rst}
.. automodule:: nautilus_trader.execution.messages
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Reports

```{eval-rst}
.. automodule:: nautilus_trader.execution.reports
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/config.md
# Config

## Backtest

```{eval-rst}
.. automodule:: nautilus_trader.backtest.config
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Cache

```{eval-rst}
.. automodule:: nautilus_trader.cache.config
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Common

```{eval-rst}
.. automodule:: nautilus_trader.common.config
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Data

```{eval-rst}
.. automodule:: nautilus_trader.data.config
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Execution

```{eval-rst}
.. automodule:: nautilus_trader.execution.config
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Live

```{eval-rst}
.. automodule:: nautilus_trader.live.config
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Persistence

```{eval-rst}
.. automodule:: nautilus_trader.persistence.config
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Risk

```{eval-rst}
.. automodule:: nautilus_trader.risk.config
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## System

```{eval-rst}
.. automodule:: nautilus_trader.system.config
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Trading

```{eval-rst}
.. automodule:: nautilus_trader.trading.config
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/model/objects.md
# Objects

```{eval-rst}
.. automodule:: nautilus_trader.model.objects
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/model/events.md
# Events

```{eval-rst}
.. automodule:: nautilus_trader.model.events
```

```{eval-rst}
.. automodule:: nautilus_trader.model.events.account
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.model.events.order
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.model.events.position
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/model/position.md
# Position

```{eval-rst}
.. automodule:: nautilus_trader.model.position
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/model/tick_scheme.md
# Tick Scheme

```{eval-rst}
.. automodule:: nautilus_trader.model.tick_scheme
```

```{eval-rst}
.. automodule:: nautilus_trader.model.tick_scheme.implementations.fixed
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.model.tick_scheme.implementations.tiered
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.model.tick_scheme.base
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/model/index.md
# Model

```{eval-rst}
.. automodule:: nautilus_trader.model
```

```{eval-rst}
.. toctree::
   :maxdepth: 2
   :glob:
   :titlesonly:
   :hidden:

   book.md
   data.md
   events.md
   identifiers.md
   instruments.md
   objects.md
   orders.md
   position.md
   tick_scheme.md
```


---

file path: ./api_reference/model/instruments.md
# Instruments

```{eval-rst}
.. automodule:: nautilus_trader.model.instruments
```

```{eval-rst}
.. automodule:: nautilus_trader.model.instruments.betting
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.model.instruments.crypto_perpetual
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.model.instruments.crypto_future
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.model.instruments.currency_pair
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.model.instruments.equity
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.model.instruments.futures_contract
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.model.instruments.option_contract
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.model.instruments.synthetic
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.model.instruments.base
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/model/book.md
# Order Book

```{eval-rst}
.. automodule:: nautilus_trader.model.book
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/model/orders.md
# Orders

```{eval-rst}
.. automodule:: nautilus_trader.model.orders
```

```{eval-rst}
.. automodule:: nautilus_trader.model.orders.market
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.model.orders.limit
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.model.orders.stop_market
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.model.orders.stop_limit
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.model.orders.market_to_limit
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.model.orders.market_if_touched
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.model.orders.limit_if_touched
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.model.orders.trailing_stop_market
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.model.orders.trailing_stop_limit
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.model.orders.list
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.model.orders.base
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/model/data.md
# Data

```{eval-rst}
.. automodule:: nautilus_trader.model.data
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/model/identifiers.md
# Identifiers

```{eval-rst}
.. automodule:: nautilus_trader.model.identifiers
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/adapters/tardis.md
# Tardis

```{eval-rst}
.. automodule:: nautilus_trader.adapters.tardis
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Loaders

```{eval-rst}
.. automodule:: nautilus_trader.adapters.tardis.loaders
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Config

```{eval-rst}
.. automodule:: nautilus_trader.adapters.tardis.config
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Providers

```{eval-rst}
.. automodule:: nautilus_trader.adapters.tardis.providers
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Factories

```{eval-rst}
.. automodule:: nautilus_trader.adapters.tardis.factories
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Data

```{eval-rst}
.. automodule:: nautilus_trader.adapters.tardis.data
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/adapters/bybit.md
# Bybit

```{eval-rst}
.. automodule:: nautilus_trader.adapters.bybit
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Config

```{eval-rst}
.. automodule:: nautilus_trader.adapters.bybit.config
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Factories

```{eval-rst}
.. automodule:: nautilus_trader.adapters.bybit.factories
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Enums

```{eval-rst}
.. automodule:: nautilus_trader.adapters.bybit.common.enums
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Providers

```{eval-rst}
.. automodule:: nautilus_trader.adapters.bybit.providers
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Data

```{eval-rst}
.. automodule:: nautilus_trader.adapters.bybit.data
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Execution

```{eval-rst}
.. automodule:: nautilus_trader.adapters.bybit.execution
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/adapters/index.md
# Adapters

```{eval-rst}
.. automodule:: nautilus_trader.adapters
```

```{eval-rst}
.. toctree::
   :maxdepth: 2
   :glob:
   :titlesonly:
   :hidden:

   betfair.md
   binance.md
   bybit.md
   coinbase_intx.md
   databento.md
   dydx.md
   interactive_brokers.md
   okx.md
   polymarket.md
   tardis.md
```


---

file path: ./api_reference/adapters/interactive_brokers.md
# Interactive Brokers

```{eval-rst}
.. automodule:: nautilus_trader.adapters.interactive_brokers
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Client

```{eval-rst}
.. automodule:: nautilus_trader.adapters.interactive_brokers.client.client
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Common

```{eval-rst}
.. automodule:: nautilus_trader.adapters.interactive_brokers.common
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Config

```{eval-rst}
.. automodule:: nautilus_trader.adapters.interactive_brokers.config
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Data

```{eval-rst}
.. automodule:: nautilus_trader.adapters.interactive_brokers.data
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Execution

```{eval-rst}
.. automodule:: nautilus_trader.adapters.interactive_brokers.execution
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Factories

```{eval-rst}
.. automodule:: nautilus_trader.adapters.interactive_brokers.factories
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Gateway

```{eval-rst}
.. automodule:: nautilus_trader.adapters.interactive_brokers.gateway
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Historical

```{eval-rst}
.. automodule:: nautilus_trader.adapters.interactive_brokers.historical.client
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Parsing

```{eval-rst}
.. automodule:: nautilus_trader.adapters.interactive_brokers.parsing.execution
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

```{eval-rst}
.. automodule:: nautilus_trader.adapters.interactive_brokers.parsing.instruments
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Providers

```{eval-rst}
.. automodule:: nautilus_trader.adapters.interactive_brokers.providers
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/adapters/coinbase_intx.md
# Coinbase International

```{eval-rst}
.. automodule:: nautilus_trader.adapters.coinbase_intx
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Config

```{eval-rst}
.. automodule:: nautilus_trader.adapters.coinbase_intx.config
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Constants

```{eval-rst}
.. automodule:: nautilus_trader.adapters.coinbase_intx.constants
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Factories

```{eval-rst}
.. automodule:: nautilus_trader.adapters.coinbase_intx.factories
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Providers

```{eval-rst}
.. automodule:: nautilus_trader.adapters.coinbase_intx.providers
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Data

```{eval-rst}
.. automodule:: nautilus_trader.adapters.coinbase_intx.data
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Execution

```{eval-rst}
.. automodule:: nautilus_trader.adapters.coinbase_intx.execution
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/adapters/betfair.md
# Betfair

```{eval-rst}
.. automodule:: nautilus_trader.adapters.betfair
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Client

```{eval-rst}
.. automodule:: nautilus_trader.adapters.betfair.client
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Common

```{eval-rst}
.. automodule:: nautilus_trader.adapters.betfair.common
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Config

```{eval-rst}
.. automodule:: nautilus_trader.adapters.betfair.config
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Data

```{eval-rst}
.. automodule:: nautilus_trader.adapters.betfair.data
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Data Types

```{eval-rst}
.. automodule:: nautilus_trader.adapters.betfair.data_types
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Execution

```{eval-rst}
.. automodule:: nautilus_trader.adapters.betfair.execution
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Factories

```{eval-rst}
.. automodule:: nautilus_trader.adapters.betfair.factories
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## OrderBook

```{eval-rst}
.. automodule:: nautilus_trader.adapters.betfair.orderbook
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Providers

```{eval-rst}
.. automodule:: nautilus_trader.adapters.betfair.providers
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Sockets

```{eval-rst}
.. automodule:: nautilus_trader.adapters.betfair.sockets
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/adapters/okx.md
# OKX

```{eval-rst}
.. automodule:: nautilus_trader.adapters.okx
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Config

```{eval-rst}
.. automodule:: nautilus_trader.adapters.okx.config
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Factories

```{eval-rst}
.. automodule:: nautilus_trader.adapters.okx.factories
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Enums

```{eval-rst}
.. automodule:: nautilus_trader.adapters.okx.common.enums
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Providers

```{eval-rst}
.. automodule:: nautilus_trader.adapters.okx.providers
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Data

```{eval-rst}
.. automodule:: nautilus_trader.adapters.okx.data
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Execution

```{eval-rst}
.. automodule:: nautilus_trader.adapters.okx.execution
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/adapters/dydx.md
# dYdX

```{eval-rst}
.. automodule:: nautilus_trader.adapters.dydx
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Config

```{eval-rst}
.. automodule:: nautilus_trader.adapters.dydx.config
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Factories

```{eval-rst}
.. automodule:: nautilus_trader.adapters.dydx.factories
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Enums

```{eval-rst}
.. automodule:: nautilus_trader.adapters.dydx.common.enums
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Providers

```{eval-rst}
.. automodule:: nautilus_trader.adapters.dydx.providers
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Data

```{eval-rst}
.. automodule:: nautilus_trader.adapters.dydx.data
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Execution

```{eval-rst}
.. automodule:: nautilus_trader.adapters.dydx.execution
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/adapters/polymarket.md
# Polymarket

```{eval-rst}
.. automodule:: nautilus_trader.adapters.polymarket
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Config

```{eval-rst}
.. automodule:: nautilus_trader.adapters.polymarket.config
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Factories

```{eval-rst}
.. automodule:: nautilus_trader.adapters.polymarket.factories
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Enums

```{eval-rst}
.. automodule:: nautilus_trader.adapters.polymarket.common.enums
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Providers

```{eval-rst}
.. automodule:: nautilus_trader.adapters.polymarket.providers
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Data

```{eval-rst}
.. automodule:: nautilus_trader.adapters.polymarket.data
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Execution

```{eval-rst}
.. automodule:: nautilus_trader.adapters.polymarket.execution
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/adapters/binance.md
# Binance

```{eval-rst}
.. automodule:: nautilus_trader.adapters.binance
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Config

```{eval-rst}
.. automodule:: nautilus_trader.adapters.binance.config
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Factories

```{eval-rst}
.. automodule:: nautilus_trader.adapters.binance.factories
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Enums

```{eval-rst}
.. automodule:: nautilus_trader.adapters.binance.common.enums
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Types

```{eval-rst}
.. automodule:: nautilus_trader.adapters.binance.common.types
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Futures

### Data

```{eval-rst}
.. automodule:: nautilus_trader.adapters.binance.futures.data
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

### Enums

```{eval-rst}
.. automodule:: nautilus_trader.adapters.binance.futures.enums
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

### Execution

```{eval-rst}
.. automodule:: nautilus_trader.adapters.binance.futures.execution
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

### Providers

```{eval-rst}
.. automodule:: nautilus_trader.adapters.binance.futures.providers
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

### Types

```{eval-rst}
.. automodule:: nautilus_trader.adapters.binance.futures.types
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Spot

### Data

```{eval-rst}
.. automodule:: nautilus_trader.adapters.binance.spot.data
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

### Enums

```{eval-rst}
.. automodule:: nautilus_trader.adapters.binance.spot.enums
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

### Execution

```{eval-rst}
.. automodule:: nautilus_trader.adapters.binance.spot.execution
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

### Providers

```{eval-rst}
.. automodule:: nautilus_trader.adapters.binance.spot.providers
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```


---

file path: ./api_reference/adapters/databento.md
# Databento

```{eval-rst}
.. automodule:: nautilus_trader.adapters.databento
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Config

```{eval-rst}
.. automodule:: nautilus_trader.adapters.databento.config
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Factories

```{eval-rst}
.. automodule:: nautilus_trader.adapters.databento.factories
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Enums

```{eval-rst}
.. automodule:: nautilus_trader.adapters.databento.enums
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Types

```{eval-rst}
.. automodule:: nautilus_trader.adapters.databento.types
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Loaders

```{eval-rst}
.. automodule:: nautilus_trader.adapters.databento.loaders
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Providers

```{eval-rst}
.. automodule:: nautilus_trader.adapters.databento.providers
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```

## Data

```{eval-rst}
.. automodule:: nautilus_trader.adapters.databento.data
   :show-inheritance:
   :inherited-members:
   :members:
   :member-order: bysource
```
