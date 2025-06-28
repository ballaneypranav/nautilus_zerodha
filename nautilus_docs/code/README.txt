TITLE: Install Nautilus Trader from PyPI
DESCRIPTION: Install the latest stable binary wheel or sdist package of `nautilus_trader` from PyPI using Python's pip package manager. It is highly recommended to perform this installation inside a virtual environment to isolate dependencies.
SOURCE: README.md
LANGUAGE: bash
KEYWORDS: dev:environment:virtual,dev:installation,dev:package-index:pypi,dev:package-management,dev:release-type:stable,development
CODE:
```
pip install -U nautilus_trader
```
----------------------------------------
TITLE: Clone NautilusTrader Source and Install Dependencies
DESCRIPTION: These commands clone the `nautilus_trader` source code from GitHub, navigate into the project directory, and then synchronize all project dependencies using `uv`.
SOURCE: README.md
LANGUAGE: bash
KEYWORDS: dev:build,dev:dependencies,dev:installation,dev:source-build,development
CODE:
```
git clone --branch develop --depth 1 https://github.com/nautechsystems/nautilus_trader
cd nautilus_trader
uv sync --all-extras
```
----------------------------------------
TITLE: Launching NautilusTrader JupyterLab Backtest Example
DESCRIPTION: These commands show how to pull and run the `jupyterlab:nightly` Docker container for NautilusTrader, mapping port 8888 to access the JupyterLab interface with an example backtest notebook.
SOURCE: README.md
LANGUAGE: bash
KEYWORDS: backtesting,example,run,tech:docker,tech:jupyter,technology
CODE:
```
docker pull ghcr.io/nautechsystems/jupyterlab:nightly --platform linux/amd64
docker run -p 8888:8888 ghcr.io/nautechsystems/jupyterlab:nightly
```
----------------------------------------
TITLE: NautilusTrader Integration Status Definitions
DESCRIPTION: Defines the different development and stability statuses used for NautilusTrader integrations, indicating their readiness and testing levels.
SOURCE: README.md
LANGUAGE: APIDOC
KEYWORDS: beta,building,documentation:API-reference,integration,stable,status
CODE:
```
Status Definitions:
- building: Under construction and likely not in a usable state.
- beta: Completed to a minimally working state and in a beta testing phase.
- stable: Stabilized feature set and API, the integration has been tested by both developers and users to a reasonable level (some bugs may still remain).
```
----------------------------------------
TITLE: Enable Cargo in Current Shell (Linux/macOS)
DESCRIPTION: After installing Rustup, this command sources the environment file to enable the `cargo` command-line tool in the current shell session on Linux and macOS.
SOURCE: README.md
LANGUAGE: bash
KEYWORDS: cargo,configuration:environment-variables,dev:source-build,development,language:rust
CODE:
```
source $HOME/.cargo/env
```
----------------------------------------
TITLE: Enable Cargo in Current Shell (Linux/macOS)
DESCRIPTION: After installing Rustup, this command sources the environment file to enable the `cargo` command-line tool in the current shell session on Linux and macOS.
SOURCE: README.md
LANGUAGE: bash
KEYWORDS: cargo,configuration:environment-variables,dev:source-build,development,language:rust
CODE:
```
source $HOME/.cargo/env
```
----------------------------------------
TITLE: Supported NautilusTrader Integrations
DESCRIPTION: Lists the trading venues and data providers integrated with NautilusTrader, including their unique IDs, types, and current development status.
SOURCE: README.md
LANGUAGE: APIDOC
KEYWORDS: Binance,Bybit,Databento,Interactive Brokers,dYdX,documentation:API-reference,integration,supported venues
CODE:
```
Integrations List:
- Name: Betfair
  ID: BETFAIR
  Type: Sports Betting Exchange
  Status: stable
- Name: Binance
  ID: BINANCE
  Type: Crypto Exchange (CEX)
  Status: stable
- Name: Binance US
  ID: BINANCE
  Type: Crypto Exchange (CEX)
  Status: stable
- Name: Binance Futures
  ID: BINANCE
  Type: Crypto Exchange (CEX)
  Status: stable
- Name: Bybit
  ID: BYBIT
  Type: Crypto Exchange (CEX)
  Status: stable
- Name: Coinbase International
  ID: COINBASE_INTX
  Type: Crypto Exchange (CEX)
  Status: stable
- Name: Databento
  ID: DATABENTO
  Type: Data Provider
  Status: stable
- Name: dYdX
  ID: DYDX
  Type: Crypto Exchange (DEX)
  Status: stable
- Name: Interactive Brokers
  ID: INTERACTIVE_BROKERS
  Type: Brokerage (multi-venue)
  Status: stable
- Name: OKX
  ID: OKX
  Type: Crypto Exchange (CEX)
  Status: building
- Name: Polymarket
  ID: POLYMARKET
  Type: Prediction Market (DEX)
  Status: stable
- Name: Tardis
  ID: TARDIS
  Type: Crypto Data Provider
  Status: stable

Additional Details:
- ID: The default client ID for the integrations adapter clients.
- Type: The type of integration (often the venue type).
```
----------------------------------------
TITLE: Install uv (Universal Installer)
DESCRIPTION: This command installs `uv`, a fast Python package installer and resolver, which is used for managing project dependencies for `nautilus_trader`.
SOURCE: README.md
LANGUAGE: bash
KEYWORDS: dev:cli,dev:installation,dev:package-management,development
CODE:
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```
----------------------------------------
TITLE: Installing cargo-nextest for Rust Testing
DESCRIPTION: This command installs `cargo-nextest`, the standard Rust test runner for NautilusTrader, which isolates each test in its own process for reliability.
SOURCE: README.md
LANGUAGE: bash
KEYWORDS: cargo-nextest,dev:installation,dev:testing,development,language:rust
CODE:
```
cargo install cargo-nextest
```
----------------------------------------
TITLE: Makefile Automation Targets for NautilusTrader
DESCRIPTION: This section details the various `make` targets available in the NautilusTrader project's Makefile, automating common development, build, installation, and testing tasks.
SOURCE: README.md
LANGUAGE: APIDOC
KEYWORDS: build,clean,dev:tooling,development,documentation:API-reference,install,make,test
CODE:
```
Makefile Targets:
  install: Installs in release build mode with all dependency groups and extras.
  install-debug: Same as install but with debug build mode.
  install-just-deps: Installs just the main, dev and test dependencies (does not install package).
  build: Runs the build script in release build mode (default).
  build-debug: Runs the build script in debug build mode.
  build-wheel: Runs uv build with a wheel format in release mode.
  build-wheel-debug: Runs uv build with a wheel format in debug mode.
  clean: Deletes all build results, such as .so or .dll files.
  distclean: CAUTION Removes all artifacts not in the git index from the repository. This includes source files which have not been git added.
  docs: Builds the documentation HTML using Sphinx.
  pre-commit: Runs the pre-commit checks over all files.
  ruff: Runs ruff over all files using the pyproject.toml config (with autofix).
  pytest: Runs all tests with pytest.
  test-performance: Runs performance tests with codspeed.
```
----------------------------------------
TITLE: Fetch and List Available NautilusTrader Versions
DESCRIPTION: This snippet demonstrates how to programmatically fetch and list all available versions of the `nautilus_trader` package from its package index using standard command-line tools.
SOURCE: README.md
LANGUAGE: bash
KEYWORDS: dev:cli,dev:installation,dev:package-index,development,list,versions
CODE:
```
curl -s https://packages.nautechsystems.io/simple/nautilus-trader/index.html | grep -oP '(?<=<a href=")[^"]+(?=")' | awk -F'#' '{print $1}' | sort
```
----------------------------------------
TITLE: Install Clang on Linux
DESCRIPTION: This command installs `clang` on Linux systems using `apt-get`, which is a necessary C language frontend for LLVM required for building `nautilus_trader` from source.
SOURCE: README.md
LANGUAGE: bash
KEYWORDS: Linux,apt-get,clang,dev:installation,dev:source-build,development
CODE:
```
sudo apt-get install clang
```
----------------------------------------
TITLE: Install Clang on Linux
DESCRIPTION: This command installs `clang` on Linux systems using `apt-get`, which is a necessary C language frontend for LLVM required for building `nautilus_trader` from source.
SOURCE: README.md
LANGUAGE: bash
KEYWORDS: Linux,apt-get,clang,dev:installation,dev:source-build,development
CODE:
```
sudo apt-get install clang
```
----------------------------------------
TITLE: Install Stable Nautilus Trader Wheels from Nautech Systems Index
DESCRIPTION: Install the latest stable release of `nautilus_trader` from the Nautech Systems package index. This index is PEP-503 compliant and hosts official releases, providing an alternative source to PyPI.
SOURCE: README.md
LANGUAGE: bash
KEYWORDS: dev:installation,dev:package-index,dev:package-management,dev:release-type:stable,development
CODE:
```
pip install -U nautilus_trader --index-url=https://packages.nautechsystems.io/simple
```
----------------------------------------
TITLE: Pulling NautilusTrader Docker Container Images
DESCRIPTION: This command demonstrates how to pull various NautilusTrader Docker container images from `ghcr.io/nautechsystems`, specifying the image variant tag and platform.
SOURCE: README.md
LANGUAGE: bash
KEYWORDS: dev:installation,development,image,pull,tech:docker,technology,variants
CODE:
```
docker pull ghcr.io/nautechsystems/<image_variant_tag> --platform linux/amd64
```
----------------------------------------
TITLE: Install Rustup on Linux and macOS
DESCRIPTION: This command installs `rustup`, the Rust toolchain installer, which is a prerequisite for building `nautilus_trader` from source on Linux and macOS systems.
SOURCE: README.md
LANGUAGE: bash
KEYWORDS: dev:cli,dev:installation,dev:source-build,development,language:rust
CODE:
```
curl https://sh.rustup.rs -sSf | sh
```
----------------------------------------
TITLE: Install Rustup on Linux and macOS
DESCRIPTION: This command installs `rustup`, the Rust toolchain installer, which is a prerequisite for building `nautilus_trader` from source on Linux and macOS systems.
SOURCE: README.md
LANGUAGE: bash
KEYWORDS: dev:cli,dev:installation,dev:source-build,development,language:rust
CODE:
```
curl https://sh.rustup.rs -sSf | sh
```
----------------------------------------
TITLE: Enable High-Precision Mode in Rust
DESCRIPTION: To enable high-precision mode for Nautilus Trader's core value types in Rust, add the `high-precision` feature flag to your `Cargo.toml` dependencies. This configures the `nautilus_model` crate to use 128-bit integers for increased precision, which is not the default for Rust crates.
SOURCE: README.md
LANGUAGE: toml
KEYWORDS: dev:build,dev:source-build,development,feature flag,feature:128-bit,feature:high-precision,language:rust,nautilus_model
CODE:
```
[dependencies]
nautilus_model = { version = "*", features = ["high-precision"] }
```
----------------------------------------
TITLE: Install Specific Development Wheel of Nautilus Trader
DESCRIPTION: Install a specific development wheel of `nautilus_trader` by providing its exact version number from the Nautech Systems package index. This command allows users to target and test particular pre-release builds, such as those from `nightly` or `develop` branches.
SOURCE: README.md
LANGUAGE: bash
KEYWORDS: dev:installation,dev:package-index,dev:package-management,dev:release-type:development,development,version
CODE:
```
pip install nautilus_trader==1.208.0a20241212 --index-url=https://packages.nautechsystems.io/simple
```
----------------------------------------
TITLE: Install Latest Pre-release Nautilus Trader Wheels
DESCRIPTION: Install the latest available pre-release version of `nautilus_trader`, including development wheels from the Nautech Systems package index. The `--pre` flag is essential to consider pre-release versions, which are not installed by default.
SOURCE: README.md
LANGUAGE: bash
KEYWORDS: dev:installation,dev:package-index,dev:package-management,dev:release-type:pre-release,development
CODE:
```
pip install -U nautilus_trader --pre --index-url=https://packages.nautechsystems.io/simple
```
----------------------------------------
TITLE: Set PyO3 Compilation Environment Variables (Linux/macOS)
DESCRIPTION: These environment variables are crucial for PyO3 to correctly link with the Python interpreter during compilation on Linux and macOS, ensuring the build process succeeds.
SOURCE: README.md
LANGUAGE: bash
KEYWORDS: LD_LIBRARY_PATH,PyO3,configuration:environment-variables,dev:source-build,development
CODE:
```
# Set the library path for the Python interpreter (in this case Python 3.13.4)
export LD_LIBRARY_PATH="$HOME/.local/share/uv/python/cpython-3.13.4-linux-x86_64-gnu/lib:$LD_LIBRARY_PATH"

# Set the Python executable path for PyO3
export PYO3_PYTHON=$(pwd)/.venv/bin/python
```
----------------------------------------
TITLE: Enable Clang in Current Shell (Windows PowerShell)
DESCRIPTION: This PowerShell command adds the Clang executable path to the system's environment variables on Windows, making it accessible from any new PowerShell session.
SOURCE: README.md
LANGUAGE: powershell
KEYWORDS: PowerShell,Windows,clang,configuration:environment-variables,dev:source-build,development
CODE:
```
[System.Environment]::SetEnvironmentVariable('path', "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\Llvm\x64\bin\;" + $env:Path,"User")
```
----------------------------------------
TITLE: Enable Clang in Current Shell (Windows PowerShell)
DESCRIPTION: This PowerShell command adds the Clang executable path to the system's environment variables on Windows, making it accessible from any new PowerShell session.
SOURCE: README.md
LANGUAGE: powershell
KEYWORDS: PowerShell,Windows,clang,configuration:environment-variables,dev:source-build,development
CODE:
```
[System.Environment]::SetEnvironmentVariable('path', "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\Llvm\x64\bin\;" + $env:Path,"User")
```