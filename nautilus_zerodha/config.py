from nautilus_trader.live.config import NautilusConfig, InstrumentProviderConfig


class ZerodhaAdapterConfig(NautilusConfig, frozen=True):
    """Configuration for Zerodha adapter.
    """
    api_key: str | None = None
    access_token: str | None = None

class ZerodhaInstrumentProviderConfig(InstrumentProviderConfig, frozen=True):
    """Configuration for Zerodha instrument provider.
    
    This can be extended with additional fields if needed.
    """
    pass

