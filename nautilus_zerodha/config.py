from nautilus_trader.live.config import LiveDataClientConfig


class ZerodhaAdapterConfig(LiveDataClientConfig):
    """Configuration for Zerodha adapter.
    
    TODO: Verify correct field names from Zerodha KiteConnect documentation.
    """
    
    # TODO: Confirm these are the correct credential field names
    api_key: str
    access_token: str
    
    # Optional base URL for flexibility (testing, etc.)
    base_url: str = "https://api.kite.trade"
    
    # TODO: Add any other required fields like user_id, secret, etc.