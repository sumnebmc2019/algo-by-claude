# core/broker_manager.py
"""
Broker Manager - Unified interface for multiple brokers (OPTIMIZED)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime, timedelta
from utils.helpers import load_secrets
from utils.logger import setup_logger

logger = setup_logger(__name__)

class BaseBroker(ABC):
    """Base class for broker implementations"""
    
    def __init__(self, broker_name: str):
        self.broker_name = broker_name
        self.credentials = self._load_credentials()
        self.is_authenticated = False
        self.logger = setup_logger(f"broker.{broker_name}")
    
    def _load_credentials(self) -> Dict[str, Any]:
        """Load broker credentials from secrets"""
        secrets = load_secrets()
        return secrets['brokers'].get(self.broker_name, {})
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with broker API"""
        pass
    
    @abstractmethod
    def get_ltp(self, symbol: str, exchange: str) -> Optional[float]:
        """Get Last Traded Price"""
        pass
    
    @abstractmethod
    def get_historical_data(self, symbol: str, exchange: str,
                          from_date: str, to_date: str,
                          interval: str = "ONE_MINUTE") -> Optional[pd.DataFrame]:
        """Get historical OHLCV data"""
        pass
    
    @abstractmethod
    def place_order(self, symbol: str, exchange: str,
                   transaction_type: str, quantity: int,
                   order_type: str = "MARKET",
                   price: float = 0.0) -> Optional[str]:
        """Place an order"""
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions"""
        pass
    
    @abstractmethod
    def get_orders(self) -> List[Dict[str, Any]]:
        """Get order history"""
        pass


class AngelOneSmartAPIBroker(BaseBroker):
    """AngelOne SmartAPI implementation - OPTIMIZED"""
    
    def __init__(self):
        super().__init__("angelone")
        self.smart_api = None
        self._token_cache = {}  # Cache tokens to avoid repeated lookups
        self._last_auth_time = None
        self._auth_valid_hours = 6  # Re-authenticate after 6 hours
    
    def authenticate(self) -> bool:
        """Authenticate with AngelOne SmartAPI"""
        try:
            # Check if recent authentication is still valid
            if self._last_auth_time:
                hours_since_auth = (datetime.now() - self._last_auth_time).total_seconds() / 3600
                if hours_since_auth < self._auth_valid_hours and self.is_authenticated:
                    self.logger.info("Using existing authentication")
                    return True
            
            from SmartApi import SmartConnect
            import pyotp
            
            # Initialize SmartAPI
            self.smart_api = SmartConnect(api_key=self.credentials['api_key'])
            
            # Generate TOTP
            totp = pyotp.TOTP(self.credentials['totp_secret']).now()
            
            # Login
            data = self.smart_api.generateSession(
                clientCode=self.credentials['client_id'],
                password=self.credentials['password'],
                totp=totp
            )
            
            if data and data.get('status'):
                self.logger.info("AngelOne authentication successful")
                self.is_authenticated = True
                self._last_auth_time = datetime.now()
                return True
            else:
                error_msg = data.get('message', 'Unknown error') if data else 'No response'
                self.logger.error(f"AngelOne authentication failed: {error_msg}")
                return False
                
        except Exception as e:
            self.logger.error(f"AngelOne authentication failed: {e}", exc_info=True)
            return False
    
    def get_ltp(self, symbol: str, exchange: str) -> Optional[float]:
        """Get LTP from AngelOne - OPTIMIZED"""
        if not self.is_authenticated:
            self.logger.error("Not authenticated with AngelOne")
            return None
        
        try:
            # Get token from cache or lookup
            token = self._get_token(symbol, exchange)
            if not token:
                return None
            
            # Fetch LTP
            ltp_data = self.smart_api.ltpData(exchange, symbol, token)
            
            if ltp_data and ltp_data.get('status'):
                return float(ltp_data['data']['ltp'])
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching LTP for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol: str, exchange: str,
                          from_date: str, to_date: str,
                          interval: str = "ONE_MINUTE") -> Optional[pd.DataFrame]:
        """Get historical data from AngelOne - OPTIMIZED with better error handling"""
        if not self.is_authenticated:
            self.logger.error("Not authenticated with AngelOne")
            return None
        
        try:
            # Get token
            token = self._get_token(symbol, exchange)
            if not token:
                self.logger.error(f"Token not found for {symbol}")
                return None
            
            # Validate and parse dates
            try:
                dt_from = datetime.strptime(from_date, '%Y-%m-%d %H:%M')
                dt_to = datetime.strptime(to_date, '%Y-%m-%d %H:%M')
            except ValueError:
                # Try alternative format
                try:
                    dt_from = datetime.strptime(from_date, '%Y-%m-%d')
                    dt_to = datetime.strptime(to_date, '%Y-%m-%d')
                    # Add time component
                    from_date = dt_from.strftime('%Y-%m-%d 09:15')
                    to_date = dt_to.strftime('%Y-%m-%d 15:30')
                except ValueError as e:
                    self.logger.error(f"Invalid date format: {e}. Use 'YYYY-MM-DD HH:MM' or 'YYYY-MM-DD'")
                    return None
            
            # Check date range validity
            if dt_from >= dt_to:
                self.logger.error("from_date must be before to_date")
                return None
            
            # Check if dates are too old (AngelOne limit: ~1 year for intraday data)
            days_ago = (datetime.now() - dt_from).days
            if days_ago > 365:
                self.logger.warning(f"Data {days_ago} days old - AngelOne may not have it")
            
            # Map interval to AngelOne format
            interval_map = {
                '1minute': 'ONE_MINUTE',
                '1min': 'ONE_MINUTE',
                '5minute': 'FIVE_MINUTE',
                '5min': 'FIVE_MINUTE',
                '15minute': 'FIFTEEN_MINUTE',
                '15min': 'FIFTEEN_MINUTE',
                '1hour': 'ONE_HOUR',
                '1day': 'ONE_DAY'
            }
            
            angelone_interval = interval_map.get(interval.lower(), interval)
            
            params = {
                "exchange": exchange,
                "symboltoken": token,
                "interval": angelone_interval,
                "fromdate": from_date,
                "todate": to_date
            }
            
            self.logger.info(f"Fetching {symbol} data from {from_date} to {to_date}")
            
            # Fetch data
            hist_data = self.smart_api.getCandleData(params)
            
            # Check response
            if not hist_data:
                self.logger.error("Empty response from AngelOne API")
                return None
            
            if hist_data.get('status') is False:
                error_msg = hist_data.get('message', 'Unknown error')
                self.logger.error(f"AngelOne API error: {error_msg}")
                
                # Common error handling
                if 'No data' in error_msg or 'no candle' in error_msg.lower():
                    self.logger.warning(f"No data available for {symbol} in specified range")
                elif 'Invalid' in error_msg:
                    self.logger.error("Invalid parameters or symbol")
                
                return None
            
            data = hist_data.get('data', [])
            
            if not data or len(data) == 0:
                self.logger.warning(f"No candle data returned for {symbol}")
                return None
            
            # Create DataFrame
            df = pd.DataFrame(
                data,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            # Process data
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            # Convert to numeric types
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Remove any NaN rows
            df = df.dropna()
            
            self.logger.info(f"Retrieved {len(df)} candles for {symbol}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching historical data: {e}", exc_info=True)
            return None
    
    def place_order(self, symbol: str, exchange: str,
                   transaction_type: str, quantity: int,
                   order_type: str = "MARKET",
                   price: float = 0.0) -> Optional[str]:
        """Place order with AngelOne - OPTIMIZED"""
        if not self.is_authenticated:
            self.logger.error("Not authenticated with AngelOne")
            return None
        
        try:
            # Get token
            token = self._get_token(symbol, exchange)
            if not token:
                return None
            
            # Prepare order params
            order_params = {
                "variety": "NORMAL",
                "tradingsymbol": symbol,
                "symboltoken": token,
                "transactiontype": transaction_type.upper(),
                "exchange": exchange,
                "ordertype": order_type.upper(),
                "producttype": "INTRADAY",
                "duration": "DAY",
                "price": str(price) if order_type.upper() == "LIMIT" else "0",
                "squareoff": "0",
                "stoploss": "0",
                "quantity": str(quantity)
            }
            
            # Place order
            order_response = self.smart_api.placeOrder(order_params)
            
            if order_response and order_response.get('status'):
                order_id = order_response['data']['orderid']
                self.logger.info(f"Order placed: {order_id} - {transaction_type} {quantity} {symbol}")
                return order_id
            else:
                error_msg = order_response.get('message', 'Unknown error') if order_response else 'No response'
                self.logger.error(f"Order placement failed: {error_msg}")
                return None
            
        except Exception as e:
            self.logger.error(f"Error placing order: {e}", exc_info=True)
            return None
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get positions from AngelOne"""
        if not self.is_authenticated:
            return []
        
        try:
            position_response = self.smart_api.position()
            
            if position_response and position_response.get('status'):
                return position_response.get('data', [])
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error fetching positions: {e}")
            return []
    
    def get_orders(self) -> List[Dict[str, Any]]:
        """Get orders from AngelOne"""
        if not self.is_authenticated:
            return []
        
        try:
            order_response = self.smart_api.orderBook()
            
            if order_response and order_response.get('status'):
                return order_response.get('data', [])
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error fetching orders: {e}")
            return []
    
    def _get_token(self, symbol: str, exchange: str) -> Optional[str]:
        """Get instrument token - OPTIMIZED with caching"""
        # Check cache first
        cache_key = f"{exchange}:{symbol}"
        if cache_key in self._token_cache:
            return self._token_cache[cache_key]
        
        try:
            from core.symbol_manager import SymbolManager
            
            # Map exchange to segment
            segment_map = {
                'NSE': 'NSE_EQ',
                'NFO': 'NSE_FO',
                'BSE': 'BSE_EQ',
                'MCX': 'MCX_FO',
                'CDS': 'CDS_FO'
            }
            
            segment = segment_map.get(exchange, 'NSE_FO')
            
            # Create symbol manager instance
            sym_mgr = SymbolManager('angelone')
            
            # Get symbol details
            details = sym_mgr.get_symbol_details(segment, symbol, broker='angelone')
            
            if details and details.get('token'):
                token = str(details['token'])
                # Cache the token
                self._token_cache[cache_key] = token
                return token
            
            self.logger.warning(f"Token not found for {symbol} in {segment}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting token for {symbol}: {e}")
            return None


class ZerodhaKiteBroker(BaseBroker):
    """Zerodha Kite Connect API implementation"""
    
    def __init__(self):
        super().__init__("zerodha")
        self.kite = None
    
    def authenticate(self) -> bool:
        """Authenticate with Zerodha Kite"""
        try:
            # TODO: Implement Kite Connect authentication
            self.logger.warning("Zerodha authentication not implemented yet")
            return False
            
        except Exception as e:
            self.logger.error(f"Zerodha authentication failed: {e}")
            return False
    
    def get_ltp(self, symbol: str, exchange: str) -> Optional[float]:
        """Get LTP from Zerodha"""
        self.logger.warning("Zerodha LTP not implemented yet")
        return None
    
    def get_historical_data(self, symbol: str, exchange: str,
                          from_date: str, to_date: str,
                          interval: str = "minute") -> Optional[pd.DataFrame]:
        """Get historical data from Zerodha"""
        self.logger.warning("Zerodha historical data not implemented yet")
        return None
    
    def place_order(self, symbol: str, exchange: str,
                   transaction_type: str, quantity: int,
                   order_type: str = "MARKET",
                   price: float = 0.0) -> Optional[str]:
        """Place order with Zerodha"""
        self.logger.warning("Zerodha order placement not implemented yet")
        return None
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get positions from Zerodha"""
        return []
    
    def get_orders(self) -> List[Dict[str, Any]]:
        """Get orders from Zerodha"""
        return []


class BrokerManager:
    """Manage multiple broker instances - OPTIMIZED"""
    
    def __init__(self):
        self.brokers: Dict[str, BaseBroker] = {}
        self.active_broker: Optional[BaseBroker] = None
        self.logger = setup_logger("broker_manager")
        self._initialize_brokers()
    
    def _initialize_brokers(self):
        """Initialize all enabled brokers"""
        secrets = load_secrets()
        
        # Initialize AngelOne
        if secrets['brokers']['angelone'].get('enabled', False):
            try:
                self.brokers['angelone'] = AngelOneSmartAPIBroker()
                self.logger.info("Initialized AngelOne broker")
            except Exception as e:
                self.logger.error(f"Failed to initialize AngelOne: {e}")
        
        # Initialize Zerodha
        if secrets['brokers']['zerodha'].get('enabled', False):
            try:
                self.brokers['zerodha'] = ZerodhaKiteBroker()
                self.logger.info("Initialized Zerodha broker")
            except Exception as e:
                self.logger.error(f"Failed to initialize Zerodha: {e}")
    
    def set_active_broker(self, broker_name: str) -> bool:
        """Set active broker with authentication"""
        if broker_name not in self.brokers:
            self.logger.error(f"Broker {broker_name} not initialized")
            return False
        
        broker = self.brokers[broker_name]
        
        if not broker.is_authenticated:
            if not broker.authenticate():
                self.logger.error(f"Failed to authenticate with {broker_name}")
                return False
        
        self.active_broker = broker
        self.logger.info(f"Active broker set to: {broker_name}")
        return True
    
    def get_active_broker(self) -> Optional[BaseBroker]:
        """Get currently active broker"""
        return self.active_broker
    
    def get_available_brokers(self) -> List[str]:
        """Get list of available broker names"""
        return list(self.brokers.keys())