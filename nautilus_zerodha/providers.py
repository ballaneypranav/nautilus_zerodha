from typing import Dict, List, Optional
from icecream import ic # noqa: F401 # For debugging, don't remove
import pandas as pd

from nautilus_trader.common.providers import InstrumentProvider
from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
from nautilus_trader.model.instruments import (
    Instrument,
    Equity,
    FuturesContract,
    OptionsContract,
)
from nautilus_trader.model.objects import Price, Quantity
from nautilus_trader.model.enums import OptionKind, AssetClass
from nautilus_trader.model.currencies import INR

from nautilus_zerodha.config import ZerodhaInstrumentProviderConfig
from .api import ZerodhaAPIClient


class ZerodhaInstrumentProvider(InstrumentProvider):
    """Instrument provider for Zerodha.
    
    Maps Zerodha instrument data to appropriate Nautilus instrument types:
    - EQ -> Equity instruments
    - FUT -> Futures contracts  
    - CE/PE -> Options contracts (Call/Put)
    """
    
    def __init__(self, client: ZerodhaAPIClient, config: ZerodhaInstrumentProviderConfig | None = None) -> None:
        """Initialize the instrument provider."""
        super().__init__(config=config)
        self._client = client
        if config is None:
            config = ZerodhaInstrumentProviderConfig()
        self.config = config
        self._instruments: Dict[InstrumentId, Instrument] = {}
        
    def _get_precision_from_tick_size(self, tick_size: float) -> int:
        """Calculate precision from tick size."""
        if tick_size == 0:
            return 2
        return max(0, len(str(tick_size).split('.')[-1]) if '.' in str(tick_size) else 0)
    
    def _create_instrument_id(self, tradingsymbol: str, exchange: str) -> InstrumentId:
        """Create Nautilus InstrumentId from Zerodha data."""
        symbol = Symbol(tradingsymbol)
        venue = Venue(exchange)
        return InstrumentId(symbol, venue)
    
    def _create_nautilus_instrument(self, raw_instrument: dict) -> Optional[Instrument]:
        """Create appropriate Nautilus instrument from Zerodha data."""
        try:
            instrument_type = raw_instrument.get('instrument_type')
            tradingsymbol = raw_instrument.get('tradingsymbol')
            exchange = raw_instrument.get('exchange')

            # Zerodha occasionally returns zero tick/lot sizes for index-like symbols.
            raw_tick_size = raw_instrument.get('tick_size', 0.01)
            tick_size = float(raw_tick_size if raw_tick_size not in (None, "") else 0.01)
            if tick_size <= 0:
                self._log.warning(
                    "Invalid tick_size=%s for %s, defaulting to 0.01",
                    raw_tick_size,
                    tradingsymbol,
                )
                tick_size = 0.01

            raw_lot_size = raw_instrument.get('lot_size', 1)
            lot_size = int(raw_lot_size if raw_lot_size not in (None, "") else 1)
            if lot_size <= 0:
                self._log.warning(
                    "Invalid lot_size=%s for %s, defaulting to 1",
                    raw_lot_size,
                    tradingsymbol,
                )
                lot_size = 1
            
            if not all([instrument_type, tradingsymbol, exchange]):
                self._log.warning(f"Missing required fields in instrument data: instrument_type={instrument_type}, tradingsymbol={tradingsymbol}, exchange={exchange}")
                return None
                
            # Type safety checks
            if not isinstance(tradingsymbol, str) or not isinstance(exchange, str):
                self._log.warning(f"Invalid field types: tradingsymbol={type(tradingsymbol)}, exchange={type(exchange)}")
                return None
                
            instrument_id = self._create_instrument_id(tradingsymbol, exchange)
            price_precision = self._get_precision_from_tick_size(tick_size)
            price_increment = Price.from_str(str(tick_size))
            size_precision = 0  # Integer quantities for Indian markets
            size_increment = Quantity.from_int(lot_size)
            
            # Common timestamps (use current time in nanoseconds)
            import time
            current_time_ns = int(time.time() * 1_000_000_000)
            ts_event = current_time_ns
            ts_init = current_time_ns
            
            if instrument_type == 'EQ':
                # Equity constructor signature (PyO3 positional args):
                # Equity(instrument_id, raw_symbol, currency, price_precision,
                #        price_increment, lot_size, ts_event, ts_init, **kwargs)
                return Equity(
                    instrument_id,           # InstrumentId
                    Symbol(tradingsymbol),   # raw_symbol: Symbol
                    INR,                     # currency: Currency
                    price_precision,         # price_precision: int
                    price_increment,         # price_increment: Price
                    size_increment,          # lot_size: Quantity
                    ts_event,                # ts_event: uint64_t
                    ts_init,                 # ts_init: uint64_t
                )
                
            elif instrument_type == 'FUT':
                expiry_str = raw_instrument.get('expiry')
                if expiry_str:
                    # Convert datetime.date to pd.Timestamp for expiry
                    if hasattr(expiry_str, 'strftime'):
                        expiry = pd.Timestamp(expiry_str)
                    else:
                        expiry = pd.Timestamp(str(expiry_str))
                else:
                    self._log.warning(f"Missing expiry date for futures contract: {tradingsymbol}")
                    return None
                    
                
                # Create FuturesContract with correct signature
                asset_class = AssetClass.INDEX if ('NIFTY' in str(tradingsymbol) or 'SENSEX' in str(tradingsymbol)) else AssetClass.EQUITY
                
                # Convert expiry date to expiration timestamp in nanoseconds
                expiration_ns = int(expiry.timestamp() * 1_000_000_000)
                
                
                futures_contract = FuturesContract(
                    instrument_id=instrument_id,
                    raw_symbol=Symbol(tradingsymbol),
                    asset_class=asset_class,
                    exchange=Venue(exchange),
                    currency=INR,  # Indian Rupee for Zerodha instruments
                    price_precision=price_precision,
                    price_increment=Price.from_str(str(tick_size)),  # Use Price object
                    multiplier=Quantity.from_int(lot_size),
                    lot_size=Quantity.from_int(lot_size),
                    underlying=None,  # Not provided by Zerodha
                    activation_ns=current_time_ns,  # Use current time for activation
                    expiration_ns=expiration_ns,
                    ts_event=ts_event,
                    ts_init=ts_init
                )
                return futures_contract
                
            elif instrument_type in ['CE', 'PE']:
                expiry_str = raw_instrument.get('expiry')
                strike_price = float(raw_instrument.get('strike', 0.0))
                
                if not expiry_str or strike_price == 0:
                    self._log.warning(f"Missing expiry ({expiry_str}) or strike price ({strike_price}) for options contract: {tradingsymbol}")
                    return None
                    
                if hasattr(expiry_str, 'strftime'):
                    expiry = pd.Timestamp(expiry_str)
                else:
                    expiry = pd.Timestamp(str(expiry_str))
                    
                option_kind = OptionKind.CALL if instrument_type == 'CE' else OptionKind.PUT
                
                return OptionsContract(
                    instrument_id=instrument_id,
                    raw_symbol=Symbol(tradingsymbol),
                    asset_class=AssetClass.INDEX if ('NIFTY' in str(tradingsymbol) or 'SENSEX' in str(tradingsymbol)) else AssetClass.EQUITY,
                    option_kind=option_kind,
                    expiry_date=expiry,
                    strike_price=Price.from_str(str(strike_price)),
                    price_precision=price_precision,
                    price_increment=price_increment,
                    size_precision=size_precision,
                    size_increment=size_increment,
                    ts_event=ts_event,
                    ts_init=ts_init,
                    multiplier=Quantity.from_int(lot_size),
                    underlying=None,  # Could be derived from tradingsymbol if needed
                )
                
            else:
                # Log unsupported instrument type
                self._log.warning(f"Unsupported instrument type: {instrument_type} for {tradingsymbol}")
                return None
                
        except Exception as e:
            self._log.error(f"Error creating instrument from {raw_instrument}: {e}")
            return None
        
    async def load_all_async(self, filters: dict | None = None) -> None:
        """Load all instruments from Zerodha API and cache them.

        Here is a structure of instruments
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

        Zerodha instrument fields and their mapping to Nautilus:
        - tradingsymbol -> Symbol
        - exchange -> Venue
        - instrument_type -> Instrument type (EQ=Equity, FUT=FuturesContract, CE/PE=OptionsContract)
        - tick_size -> price_increment & price_precision
        - lot_size -> size_increment
        - expiry -> expiry_date (for derivatives)
        - strike -> strike_price (for options)
        """
        # Extract exchange filter if provided (for API-level filtering)
        exchange_filter = None
        if filters and 'exchange' in filters:
            exchange_filter = filters['exchange']
            # If exchange is a list, use the first one for API call
            if isinstance(exchange_filter, list):
                exchange_filter = exchange_filter[0] if exchange_filter else None

        # Fetch raw instrument data from API (with exchange filter for efficiency)
        raw_instruments = await self._client.get_all_instruments_async(exchange=exchange_filter)

        instrument_count = 0
        failed_count = 0
        filtered_count = 0

        for raw_instrument in raw_instruments:
            # Apply filters if provided
            if filters:
                # Skip if instrument doesn't match filters
                if not self._matches_filters(raw_instrument, filters):
                    filtered_count += 1
                    continue

            # Create Nautilus instrument from Zerodha data
            nautilus_instrument = self._create_nautilus_instrument(raw_instrument)
            
            if nautilus_instrument:
                # Cache the instrument
                self._instruments[nautilus_instrument.id] = nautilus_instrument
                instrument_count += 1
            else:
                failed_count += 1
                
        self._log.info(f"Loaded {instrument_count} instruments from Zerodha (failed: {failed_count}, filtered: {filtered_count})")
        
    def _matches_filters(self, raw_instrument: dict, filters: dict) -> bool:
        """Check if instrument matches the provided filters."""
        for key, value in filters.items():
            if key in raw_instrument:
                if isinstance(value, list):
                    if raw_instrument[key] not in value:
                        return False
                else:
                    if raw_instrument[key] != value:
                        return False
        return True
            
    def find(self, instrument_id: InstrumentId) -> Optional[Instrument]:
        """Find an instrument by ID."""
        return self._instruments.get(instrument_id)
        
    def list_all(self) -> List[Instrument]:
        """List all cached instruments."""
        return list(self._instruments.values())
        
    async def load_ids_async(self, instrument_ids: list[InstrumentId], filters: dict | None = None) -> None:
        """Load specific instruments by ID."""
        # For simplicity, load all instruments and filter
        # In a production implementation, you might want to optimize this
        # by only fetching the requested instrument_ids
        _ = instrument_ids  # TODO: Implement optimized loading by specific IDs
        await self.load_all_async(filters)
        
    async def load_async(self, instrument_id: InstrumentId, filters: dict | None = None) -> None:
        """Load a single instrument by ID.""" 
        # For simplicity, load all instruments and filter
        # In a production implementation, you might want to optimize this
        # by only fetching the requested instrument_id
        _ = instrument_id  # TODO: Implement optimized loading by specific ID
        await self.load_all_async(filters)
