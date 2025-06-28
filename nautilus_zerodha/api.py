import aiohttp
from typing import List, Dict, Any

from kiteconnect import KiteConnect
from .config import ZerodhaAdapterConfig


class ZerodhaAPIClient:
    """Async HTTP client for Zerodha KiteConnect API.
    
    TODO: Implement actual Zerodha API integration once documentation is reviewed.
    """
    
    def __init__(self, config: ZerodhaAdapterConfig) -> None:
        """Initialize the API client with configuration."""
        self.config = config
        self.authenticated = False
        self.kite = KiteConnect(api_key=config.api_key)
        self.kite.set_access_token(config.access_token)
        if self.validate_access_token():
            self.authenticated = True
        else:
            raise RuntimeError("Failed to authenticate with Zerodha API. Check your credentials.")

    def validate_access_token(self) -> Dict:
        """
        Validate access token by fetching user profile
        Based on pattern from provided examples
        
        Returns:
            User profile data
        """
        if not self.config.access_token:
            raise RuntimeError("No access token available. Complete authentication first.")
        
        # Fetch user profile to validate token
        profile = self.kite.profile()
        return profile
        
    async def get_all_instruments_async(self) -> List[Dict[str, Any]]:
        """Fetch all instruments from Zerodha API.
        
        TODO: Implement actual API call to Zerodha instruments endpoint.
        TODO: Research correct endpoint URL and response format.
        TODO: Verify authentication header format.
        
        Returns:
            List of raw instrument dictionaries from Zerodha API.
        """
        instruments = self.kite.instruments()
        return instruments[:5]
        