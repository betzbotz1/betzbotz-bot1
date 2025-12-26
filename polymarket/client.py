"""
Polymarket API Client
Handles authentication and API calls
"""

import logging
import requests
from typing import Optional, Dict, Any, List
from eth_account import Account
from config import Config

logger = logging.getLogger(__name__)

POLYMARKET_API_URL = "https://clob.polymarket.com"
GAMMA_API_URL = "https://gamma-api.polymarket.com"


class PolymarketClient:
    """Client for interacting with Polymarket."""
    
    def __init__(self):
        self.private_key = Config.POLYMARKET_PRIVATE_KEY
        self.api_key = Config.POLYMARKET_API_KEY
        self.account = None
        self.address = None
        
        if self.private_key:
            try:
                self.account = Account.from_key(self.private_key)
                self.address = self.account.address
                logger.info(f"Wallet initialized: {self.address[:10]}...")
            except Exception as e:
                logger.error(f"Failed to initialize wallet: {e}")
    
    def get_address(self) -> str:
        """Get wallet address."""
        return self.address or ""
    
    def get_balance(self) -> float:
        """Get USDC balance."""
        if not self.address:
            return 0.0
        
        try:
            # Query balance from Polymarket
            response = requests.get(
                f"{GAMMA_API_URL}/balance",
                params={"address": self.address},
                timeout=10
            )
            if response.ok:
                data = response.json()
                return float(data.get("balance", 0))
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
        
        return 0.0
    
    def get_markets(self, limit: int = 100, active: bool = True) -> List[Dict]:
        """Get list of markets."""
        try:
            response = requests.get(
                f"{GAMMA_API_URL}/markets",
                params={"limit": limit, "active": active},
                timeout=15
            )
            if response.ok:
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get markets: {e}")
        
        return []
    
    def get_market(self, market_id: str) -> Optional[Dict]:
        """Get single market details."""
        try:
            response = requests.get(
                f"{GAMMA_API_URL}/markets/{market_id}",
                timeout=10
            )
            if response.ok:
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get market {market_id}: {e}")
        
        return None
    
    def get_orderbook(self, token_id: str) -> Optional[Dict]:
        """Get orderbook for a token."""
        try:
            response = requests.get(
                f"{POLYMARKET_API_URL}/book",
                params={"token_id": token_id},
                timeout=10
            )
            if response.ok:
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get orderbook: {e}")
        
        return None
    
    def get_positions(self) -> List[Dict]:
        """Get current positions."""
        if not self.address:
            return []
        
        try:
            response = requests.get(
                f"{GAMMA_API_URL}/positions",
                params={"address": self.address},
                timeout=10
            )
            if response.ok:
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
        
        return []
    
    def place_order(
        self,
        token_id: str,
        side: str,
        price: float,
        size: float
    ) -> Optional[Dict]:
        """Place a limit order."""
        if not self.account:
            logger.error("Wallet not initialized")
            return None
        
        try:
            # Build order
            order = {
                "tokenId": token_id,
                "side": side.upper(),
                "price": str(price),
                "size": str(size),
            }
            
            # Sign order
            # TODO: Implement proper CLOB signing
            
            logger.info(f"Placing order: {side} {size} @ {price}")
            
            # For now, return mock success
            return {"orderId": "mock-order-id", "status": "placed"}
            
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
        
        return None
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        try:
            # TODO: Implement cancel
            logger.info(f"Cancelling order: {order_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel order: {e}")
        
        return False
    
    def sell_position(self, token_id: str, percent: int = 100) -> Optional[Dict]:
        """Sell a position."""
        try:
            # Get current position
            positions = self.get_positions()
            position = next((p for p in positions if p.get("tokenId") == token_id), None)
            
            if not position:
                logger.warning(f"Position not found: {token_id}")
                return None
            
            # Calculate amount to sell
            size = float(position.get("size", 0)) * (percent / 100)
            
            if size <= 0:
                logger.warning("Nothing to sell")
                return None
            
            # Place sell order at market
            # TODO: Implement market sell
            logger.info(f"Selling {percent}% of position {token_id}")
            
            return {"status": "sold", "size": size}
            
        except Exception as e:
            logger.error(f"Failed to sell position: {e}")
        
        return None


# Global client instance
client = PolymarketClient()
