# core/broker_manager.py
"""
Broker Manager - Fixed for Oracle Cloud timeout issues
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime, timedelta
from utils.helpers import load_secrets
from utils.logger import setup_logger
import time

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
    """AngelOne SmartAPI - Fixed for Oracle Cloud timeout"""
    
    def __init__(self):
        super().__init__("angelone")
        self.smart_api = None
        self._token_cache = {}
        self._last_auth_time = None
        self._auth_valid_hours = 6
        self._max_retries = 3
        self._retry_delay = 2
    
    def authenticate(self) -> bool:
        """Authenticate with retry logic for Oracle Cloud"""
        # Check if recent authentication is still valid
        if self._last_auth_time:
            hours_since_auth = (datetime.now() - self._last_auth_time).total_seconds() / 3600
            if hours_since_auth < self._auth_valid_hours and self.is_authenticated:
                self.logger.info("✅ Using existing authentication")
                return True
        
        # Try authentication with retries
        for attempt in range(self._max_retries):
            try:
                from SmartApi import SmartConnect
                import pyotp
                
                self.logger.info(f"🔄 Authentication attempt {attempt + 1}/{self._max_retries}")
                
                # Initialize with longer timeout
                self.smart_api = SmartConnect(
                    api_key=self.credentials['api_key'],
                    timeout=30  # Increased timeout for Oracle Cloud
                )
                
                # Generate TOTP
                totp = pyotp.TOTP(self.credentials['totp_secret']).now()
                self.logger.info(f"🔑 Generated TOTP: {totp}")
                
                # Login with retry
                data = self.smart_api.generateSession(
                    clientCode=self.credentials['client_id'],
                    password=self.credentials['password'],
                    totp=totp
                )
                
                if data and data.get('status'):
                    self.logger.info("✅ AngelOne authentication successful")
                    self.is_authenticated = True
                    self._last_auth_time = datetime.now()
                    return True
                else:
                    error_msg = data.get('message', 'Unknown error') if data else 'No response'
                    self.logger.error(f"❌ AngelOne authentication failed: {error_msg}")
                    
                    # If invalid credentials, don't retry
                    if 'Invalid' in error_msg or 'incorrect' in error_msg.lower():
                        return False
                    
                    # Wait before retry
                    if attempt < self._max_retries - 1:
                        self.logger.info(f"⏳ Waiting {self._retry_delay}s before retry...")
                        time.sleep(self._retry_delay)
                        
            except Exception as e:
                error_str = str(e)
                self.logger.error(f"❌ Authentication attempt {attempt + 1} failed: {error_str}")
                
                # Check if it's a timeout error
                if 'timeout' in error_str.lower() or 'timed out' in error_str.lower():
                    self.logger.warning("⚠️ Connection timeout - Oracle Cloud may be blocking outbound HTTPS")
                    self.logger.info("💡 Trying with different network settings...")
                    
                    # Wait longer before retry on timeout
                    if attempt < self._max_retries - 1:
                        wait_time = self._retry_delay * (attempt + 1)
                        self.logger.info(f"⏳ Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                else:
                    # Non-timeout error, fail immediately
                    self.logger.error(f"❌ Critical error: {e}", exc_info=True)
                    return False
        
        # All retries failed
        self.logger.error("❌ All authentication attempts failed")
        self._print_troubleshooting()
        return False
    
    def _print_troubleshooting(self):
        """Print troubleshooting steps for Oracle Cloud"""
        self.logger.error("\n" + "="*60)
        self.logger.error("🔧 TROUBLESHOOTING STEPS FOR ORACLE CLOUD:")
        self.logger.error("="*60)
        self.logger.error("\n1. Check Oracle Cloud Firewall:")
        self.logger.error("   sudo iptables -L -n | grep 443")
        self.logger.error("   sudo iptables -A OUTPUT -p tcp --dport 443 -j ACCEPT")
        self.logger.error("\n2. Test connection to AngelOne:")
        self.logger.error("   curl -v https://apiconnect.angelone.in")
        self.logger.error("\n3. Check DNS resolution:")
        self.logger.error("   nslookup apiconnect.angelone.in")
        self.logger.error("\n4. Check if proxy is needed:")
        self.logger.error("   echo $http_proxy")
        self.logger.error("   echo $https_proxy")
        self.logger.error("\n5. Verify credentials in config/secrets.yaml")
        self.logger.error("\n6. Try from local machine first to verify credentials")
        self.logger.error("="*60 + "\n")
    
    def get_ltp(self, symbol: str, exchange: str) -> Optional[float]:
        """Get LTP with retry logic"""
        if not self.is_authenticated:
            self.logger.error("❌ Not authenticated with AngelOne")
            return None
        
        for attempt in range(self._max_retries):
            try:
                token = self._get_token(symbol, exchange)
                if not token:
                    return None
                
                ltp_data = self.smart_api.ltpData(exchange, symbol, token)
                
                if ltp_data and ltp_data.get('status'):
                    return float(ltp_data['data']['ltp'])
                
                return None
                
            except Exception as e:
                if 'timeout' in str(e).lower() and attempt < self._max_retries - 1:
                    self.logger.warning(f"⚠️ LTP timeout, retry {attempt + 1}")
                    time.sleep(1)
                    continue
                
                self.logger.error(f"❌ Error fetching LTP for {symbol}: {e}")
                return None
        
        return None
    
    def get_historical_data(self, symbol: str, exchange: str,
                          from_date: str, to_date: str,
                          interval: str = "ONE_MINUTE") -> Optional[pd.DataFrame]:
        """Get historical data with retry logic"""
        if not self.is_authenticated:
            self.logger.error("❌ Not authenticated with AngelOne")
            return None
        
        for attempt in range(self._max_retries):
            try:
                token = self._get_token(symbol, exchange)
                if not token:
                    self.logger.error(f"❌ Token not found for {symbol}")
                    return None
                
                # Validate dates
                try:
                    dt_from = datetime.strptime(from_date, '%Y-%m-%d %H:%M')
                    dt_to = datetime.strptime(to_date, '%Y-%m-%d %H:%M')
                except ValueError:
                    try:
                        dt_from = datetime.strptime(from_date, '%Y-%m-%d')
                        dt_to = datetime.strptime(to_date, '%Y-%m-%d')
                        from_date = dt_from.strftime('%Y-%m-%d 09:15')
                        to_date = dt_to.strftime('%Y-%m-%d 15:30')
                    except ValueError as e:
                        self.logger.error(f"❌ Invalid date format: {e}")
                        return None
                
                # Map interval
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
                
                self.logger.info(f"📊 Fetching {symbol} from {from_date} to {to_date}")
                
                hist_data = self.smart_api.getCandleData(params)
                
                if not hist_data:
                    if attempt < self._max_retries - 1:
                        self.logger.warning(f"⚠️ Empty response, retry {attempt + 1}")
                        time.sleep(2)
                        continue
                    self.logger.error("❌ Empty response from AngelOne API")
                    return None
                
                if hist_data.get('status') is False:
                    error_msg = hist_data.get('message', 'Unknown error')
                    self.logger.error(f"❌ AngelOne API error: {error_msg}")
                    return None
                
                data = hist_data.get('data', [])
                
                if not data:
                    self.logger.warning(f"⚠️ No candle data for {symbol}")
                    return None
                
                df = pd.DataFrame(
                    data,
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp').reset_index(drop=True)
                
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                df = df.dropna()
                
                self.logger.info(f"✅ Retrieved {len(df)} candles for {symbol}")
                return df
                
            except Exception as e:
                if 'timeout' in str(e).lower() and attempt < self._max_retries - 1:
                    self.logger.warning(f"⚠️ Timeout, retry {attempt + 1}")
                    time.sleep(2)
                    continue
                
                self.logger.error(f"❌ Error fetching historical data: {e}", exc_info=True)
                return None
        
        return None
    
    def place_order(self, symbol: str, exchange: str,
                   transaction_type: str, quantity: int,
                   order_type: str = "MARKET",
                   price: float = 0.0) -> Optional[str]:
        """Place order with retry logic"""
        if not self.is_authenticated:
            self.logger.error("❌ Not authenticated with AngelOne")
            return None
        
        for attempt in range(self._max_retries):
            try:
                token = self._get_token(symbol, exchange)
                if not token:
                    return None
                
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
                
                order_response = self.smart_api.placeOrder(order_params)
                
                if order_response and order_response.get('status'):
                    order_id = order_response['data']['orderid']
                    self.logger.info(f"✅ Order placed: {order_id}")
                    return order_id
                else:
                    error_msg = order_response.get('message', 'Unknown') if order_response else 'No response'
                    
                    if attempt < self._max_retries - 1 and 'timeout' in error_msg.lower():
                        self.logger.warning(f"⚠️ Order timeout, retry {attempt + 1}")
                        time.sleep(1)
                        continue
                    
                    self.logger.error(f"❌ Order failed: {error_msg}")
                    return None
                
            except Exception as e:
                if 'timeout' in str(e).lower() and attempt < self._max_retries - 1:
                    self.logger.warning(f"⚠️ Timeout, retry {attempt + 1}")
                    time.sleep(1)
                    continue
                
                self.logger.error(f"❌ Error placing order: {e}", exc_info=True)
                return None
        
        return None
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get positions"""
        if not self.is_authenticated:
            return []
        
        try:
            position_response = self.smart_api.position()
            if position_response and position_response.get('status'):
                return position_response.get('data', [])
            return []
        except Exception as e:
            self.logger.error(f"❌ Error fetching positions: {e}")
            return []
    
    def get_orders(self) -> List[Dict[str, Any]]:
        """Get orders"""
        if not self.is_authenticated:
            return []
        
        try:
            order_response = self.smart_api.orderBook()
            if order_response and order_response.get('status'):
                return order_response.get('data', [])
            return []
        except Exception as e:
            self.logger.error(f"❌ Error fetching orders: {e}")
            return []
    
    def _get_token(self, symbol: str, exchange: str) -> Optional[str]:
        """Get instrument token with caching"""
        cache_key = f"{exchange}:{symbol}"
        if cache_key in self._token_cache:
            return self._token_cache[cache_key]
        
        try:
            from core.symbol_manager import SymbolManager
            
            segment_map = {
                'NSE': 'NSE_EQ',
                'NFO': 'NSE_FO',
                'BSE': 'BSE_EQ',
                'MCX': 'MCX_FO',
                'CDS': 'CDS_FO'
            }
            
            segment = segment_map.get(exchange, 'NSE_FO')
            sym_mgr = SymbolManager('angelone')
            details = sym_mgr.get_symbol_details(segment, symbol, broker='angelone')
            
            if details and details.get('token'):
                token = str(details['token'])
                self._token_cache[cache_key] = token
                return token
            
            self.logger.warning(f"⚠️ Token not found for {symbol}")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error getting token: {e}")
            return None


class BrokerManager:
    """Manage multiple broker instances"""
    
    def __init__(self):
        self.brokers: Dict[str, BaseBroker] = {}
        self.active_broker: Optional[BaseBroker] = None
        self.logger = setup_logger("broker_manager")
        self._initialize_brokers()
    
    def _initialize_brokers(self):
        """Initialize all enabled brokers"""
        secrets = load_secrets()
        
        if secrets['brokers']['angelone'].get('enabled', False):
            try:
                self.brokers['angelone'] = AngelOneSmartAPIBroker()
                self.logger.info("✅ Initialized AngelOne broker")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize AngelOne: {e}")
    
    def set_active_broker(self, broker_name: str) -> bool:
        """Set active broker"""
        if broker_name not in self.brokers:
            self.logger.error(f"❌ Broker {broker_name} not initialized")
            return False
        
        broker = self.brokers[broker_name]
        
        if not broker.is_authenticated:
            if not broker.authenticate():
                self.logger.error(f"❌ Failed to authenticate with {broker_name}")
                return False
        
        self.active_broker = broker
        self.logger.info(f"✅ Active broker: {broker_name}")
        return True
    
    def get_active_broker(self) -> Optional[BaseBroker]:
        """Get active broker"""
        return self.active_broker
    
    def get_available_brokers(self) -> List[str]:
        """Get available brokers"""
        return list(self.brokers.keys())