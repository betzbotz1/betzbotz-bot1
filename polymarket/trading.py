"""
Trading Engine
Executes trades and manages positions
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

from config import Config
from polymarket.client import client

logger = logging.getLogger(__name__)


class Position:
    """Represents an open position."""
    
    def __init__(self, data: Dict):
        self.id = data.get("token_id", "")
        self.market_id = data.get("market_id", "")
        self.market_question = data.get("market_question", "")
        self.token_id = data.get("token_id", "")
        self.side = data.get("side", "YES")
        self.entry_price = float(data.get("entry_price", 0))
        self.shares = float(data.get("shares", 0))
        self.current_price = float(data.get("current_price", 0))
        self.created_at = data.get("created_at", datetime.utcnow().isoformat())
        self.status = data.get("status", "open")
    
    @property
    def cost_basis(self) -> float:
        return self.entry_price * self.shares
    
    @property
    def current_value(self) -> float:
        return self.current_price * self.shares
    
    @property
    def unrealized_pnl(self) -> float:
        return self.current_value - self.cost_basis
    
    @property
    def unrealized_pnl_pct(self) -> float:
        if self.cost_basis == 0:
            return 0
        return (self.unrealized_pnl / self.cost_basis) * 100
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "market_id": self.market_id,
            "market_question": self.market_question,
            "token_id": self.token_id,
            "side": self.side,
            "entry_price": self.entry_price,
            "shares": self.shares,
            "current_price": self.current_price,
            "unrealized_pnl": round(self.unrealized_pnl, 2),
            "unrealized_pnl_pct": round(self.unrealized_pnl_pct, 1),
            "created_at": self.created_at,
            "status": self.status,
        }


class TradingEngine:
    """Manages trading operations."""
    
    def __init__(self):
        self.positions: List[Position] = []
        self.trade_history: List[Dict] = []
        self.total_pnl = 0.0
    
    def execute_buy(self, opportunity: Dict) -> Optional[Position]:
        """Execute a buy order."""
        try:
            token_id = opportunity.get("token_id")
            entry_price = opportunity.get("entry_price", 0)
            
            # Calculate size based on max bet
            size = Config.MAX_BET_PER_SIDE / entry_price if entry_price > 0 else 0
            
            if size <= 0:
                logger.warning("Invalid size calculation")
                return None
            
            # Place order
            result = client.place_order(
                token_id=token_id,
                side="BUY",
                price=entry_price,
                size=size
            )
            
            if result:
                # Create position
                position = Position({
                    "token_id": token_id,
                    "market_id": opportunity.get("market_id"),
                    "market_question": opportunity.get("market_question"),
                    "side": opportunity.get("side", "YES"),
                    "entry_price": entry_price,
                    "shares": size,
                    "current_price": entry_price,
                    "created_at": datetime.utcnow().isoformat(),
                    "status": "open",
                })
                
                self.positions.append(position)
                logger.info(f"Opened position: {position.market_question[:40]}...")
                
                return position
                
        except Exception as e:
            logger.error(f"Failed to execute buy: {e}")
        
        return None
    
    def execute_sell(self, token_id: str, percent: int = 100) -> Optional[Dict]:
        """Execute a sell order."""
        try:
            # Find position
            position = next((p for p in self.positions if p.token_id == token_id), None)
            
            if not position:
                logger.warning(f"Position not found: {token_id}")
                return None
            
            # Execute sell
            result = client.sell_position(token_id, percent)
            
            if result:
                if percent >= 100:
                    # Close position fully
                    self.total_pnl += position.unrealized_pnl
                    position.status = "closed"
                    self.trade_history.append(position.to_dict())
                    self.positions = [p for p in self.positions if p.token_id != token_id]
                else:
                    # Partial close
                    sold_shares = position.shares * (percent / 100)
                    position.shares -= sold_shares
                
                logger.info(f"Sold {percent}% of position {token_id}")
                return {"status": "sold", "percent": percent}
                
        except Exception as e:
            logger.error(f"Failed to execute sell: {e}")
        
        return None
    
    def check_take_profits(self):
        """Check positions for take profit conditions."""
        for position in self.positions:
            if position.status != "open":
                continue
            
            # Update current price
            orderbook = client.get_orderbook(position.token_id)
            if orderbook:
                bids = orderbook.get("bids", [])
                if bids:
                    position.current_price = float(bids[0].get("price", position.current_price))
            
            # Check take profit tiers
            price_multiplier = position.current_price / position.entry_price if position.entry_price > 0 else 0
            
            for tier_mult, tier_pct in Config.TAKE_PROFIT_TIERS:
                if price_multiplier >= tier_mult:
                    logger.info(f"Take profit triggered at {tier_mult}x for {position.token_id}")
                    self.execute_sell(position.token_id, int(tier_pct))
                    break
    
    def get_positions(self) -> List[Dict]:
        """Get all open positions."""
        return [p.to_dict() for p in self.positions if p.status == "open"]
    
    def get_total_value(self) -> float:
        """Get total value of open positions."""
        return sum(p.current_value for p in self.positions if p.status == "open")
    
    def get_total_pnl(self) -> float:
        """Get total realized + unrealized PnL."""
        unrealized = sum(p.unrealized_pnl for p in self.positions if p.status == "open")
        return self.total_pnl + unrealized


# Global trading engine instance
engine = TradingEngine()
