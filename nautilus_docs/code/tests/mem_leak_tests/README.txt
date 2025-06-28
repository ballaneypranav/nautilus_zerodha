TITLE: Connecting to Memray Live Profiler Dashboard
DESCRIPTION: This command connects to the `memray` live profiling server, typically started by a `memray run` command, to view the real-time memory usage dashboard in another shell.
SOURCE: tests/mem_leak_tests/README.md
LANGUAGE: bash
KEYWORDS: dev:profiling,development,live dashboard,memory,memray,testing
CODE:
```
memray live 8100
```
----------------------------------------
TITLE: Running Memray Profiler for Backtest
DESCRIPTION: This command invokes `memray` to run a Python script (`memray_backtest.py`) and profile its memory usage. It starts a live profiling server on port 8100, allowing real-time monitoring from another shell.
SOURCE: tests/mem_leak_tests/README.md
LANGUAGE: bash
KEYWORDS: backtest,dev:profiling,development,memory,memray,run,testing
CODE:
```
memray run --live-port 8100 --live-remote tests/mem_leak_tests/memray_backtest.py
```
----------------------------------------
TITLE: Installing Memray Python Package
DESCRIPTION: This command installs the `memray` package, a memory profiler, using pip. It's a prerequisite for conducting memory profiling tests, though it doesn't support Windows.
SOURCE: tests/mem_leak_tests/README.md
LANGUAGE: bash
KEYWORDS: dev:installation,dev:profiling,dev:tooling,development,memory,memray,testing
CODE:
```
pip install memray
```