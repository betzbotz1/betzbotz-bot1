"""
Market Monitoring
Scans for new market opportunities
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from config import Config
from polymarket.client import client

logger = logging.getLogger(__name__)


class MarketMonitor:
    """Monitors markets for sniping opportunities."""
    
    def __init__(self):
        self.seen_markets = set()
        self.opportunities = []
    
    def scan_new_markets(self) -> List[Dict]:
        """Scan for newly created markets."""
        new_opportunities = []
        
        try:
            markets = client.get_markets(limit=50, active=True)
            
            for market in markets:
                market_id = market.get("id")
                
                # Skip if already seen
                if market_id in self.seen_markets:
                    continue
                
                self.seen_markets.add(market_id)
                
                # Check if market passes filters
                if self.passes_filters(market):
                    opportunity = self.analyze_market(market)
                    if opportunity:
                        new_opportunities.append(opportunity)
                        logger.info(f"New opportunity: {market.get('question', '')[:50]}...")
            
        except Exception as e:
            logger.error(f"Error scanning markets: {e}")
        
        return new_opportunities
    
    def passes_filters(self, market: Dict) -> bool:
        """Check if market passes configured filters."""
        try:
            # Check volume
            volume = float(market.get("volume", 0))
            if volume < Config.MIN_MARKET_VOLUME:
                return False
            
            # Check expiry
            end_date = market.get("endDate")
            if end_date:
                expiry = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                now = datetime.now(expiry.tzinfo)
                hours_to_expiry = (expiry - now).total_seconds() / 3600
                
                if hours_to_expiry < Config.MIN_HOURS_TO_EXPIRY:
                    return False
                
                if hours_to_expiry > Config.MAX_DAYS_TO_EXPIRY * 24:
                    return False
            
            # Check if tokens available
            tokens = market.get("tokens", [])
            if not tokens:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking filters: {e}")
            return False
    
    def analyze_market(self, market: Dict) -> Optional[Dict]:
        """Analyze market for trading opportunity."""
        try:
            tokens = market.get("tokens", [])
            
            for token in tokens:
                token_id = token.get("token_id")
                outcome = token.get("outcome")  # YES or NO
                
                # Get orderbook
                orderbook = client.get_orderbook(token_id)
                if not orderbook:
                    continue
                
                # Check best ask price
                asks = orderbook.get("asks", [])
                if not asks:
                    continue
                
                best_ask = float(asks[0].get("price", 1))
                
                # Check if price is low enough
                if best_ask <= Config.MAX_ENTRY_PRICE:
                    return {
                        "market_id": market.get("id"),
                        "market_question": market.get("question", ""),
                        "token_id": token_id,
                        "side": outcome,
                        "entry_price": best_ask,
                        "volume": market.get("volume", 0),
                        "end_date": market.get("endDate"),
                    }
            
        except Exception as e:
            logger.error(f"Error analyzing market: {e}")
        
        return None
    
    def get_opportunities(self) -> List[Dict]:
        """Get current list of opportunities."""
        return self.opportunities


# Global monitor instance
monitor = MarketMonitor()
