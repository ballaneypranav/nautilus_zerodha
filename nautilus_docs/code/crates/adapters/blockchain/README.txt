TITLE: Configure Environment Variables via Command Line
DESCRIPTION: Shows how to provide environment variables directly in the command line when running a Rust application. This method allows for quick, one-off configuration without modifying a `.env` file.
SOURCE: crates/adapters/blockchain/README.md
LANGUAGE: Shell
KEYWORDS: configuration,configuration:environment-variables,dev:cli,development,language:rust
CODE:
```
CHAIN=Ethereum RPC_WSS_URL=wss://your-node-endpoint cargo run --bin live_blocks_rpc
```
----------------------------------------
TITLE: Configure Environment Variables via .env File
DESCRIPTION: Demonstrates how to set up required environment variables for blockchain connection by creating a `.env` file in the project root. These variables specify the target blockchain and RPC endpoints.
SOURCE: crates/adapters/blockchain/README.md
LANGUAGE: Shell
KEYWORDS: blockchain,configuration,configuration:environment-variables,rpc
CODE:
```
CHAIN=Ethereum
RPC_WSS_URL=wss://mainnet.infura.io/ws/v3/YOUR_INFURA_API_KEY
RPC_HTTP_URL=https://mainnet.infura.io/v3/YOUR_INFURA_API_KEY
```
----------------------------------------
TITLE: Sync Uniswap V3 DEX, Tokens, and Pools on Ethereum
DESCRIPTION: Runs a script to discover and cache Uniswap V3 pools and their associated tokens on the Ethereum blockchain. It queries pool creation events, retrieves token metadata via smart contract calls, and stores the data in a local Postgres database.
SOURCE: crates/adapters/blockchain/README.md
LANGUAGE: Shell
KEYWORDS: DEX,Ethereum,Uniswap V3,blockchain,discovery,hypersync,sync
CODE:
```
cargo run --bin sync_tokens_pools --features hypersync
```
----------------------------------------
TITLE: Watch Live Blockchain Blocks (RPC and Hypersync)
DESCRIPTION: Commands to connect to the specified blockchain and log information about each new block received. One command uses the RPC version, and the other uses only Hypersync for block ingestion.
SOURCE: crates/adapters/blockchain/README.md
LANGUAGE: Shell
KEYWORDS: Ethereum,RPC,blockchain,blocks,data type:live,hypersync
CODE:
```
cargo run --bin live_blocks_rpc --features hypersync
```

LANGUAGE: Shell
CODE:
```
cargo run --bin live_blocks_hypersync --features hypersync
```