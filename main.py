"""
BetzBotz - Polymarket Trading Bot
Main entry point
"""

import argparse
import asyncio
import logging
import sys
from datetime import datetime

from config import Config

# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


class BetzBotz:
    """Main bot class."""
    
    def __init__(self):
        self.running = False
        self.start_time = None
        self.markets_detected = 0
        self.orders_placed = 0
        self.orders_filled = 0
        
    async def start(self):
        """Start the bot."""
        logger.info("🤖 Starting BetzBotz...")
        
        # Validate config
        errors = Config.validate()
        if errors:
            for err in errors:
                logger.error(f"Config error: {err}")
            return
        
        self.running = True
        self.start_time = datetime.utcnow()
        
        logger.info("✅ Bot started successfully")
        logger.info(f"   Max bet: ${Config.MAX_BET_PER_SIDE}")
        logger.info(f"   AI mode: {Config.AI_MODE_ENABLED}")
        
        # Main loop
        while self.running:
            try:
                await self.scan_markets()
                await asyncio.sleep(30)  # Scan every 30 seconds
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(60)
    
    async def scan_markets(self):
        """Scan for new market opportunities."""
        # TODO: Implement market scanning
        pass
    
    def stop(self):
        """Stop the bot."""
        logger.info("🛑 Stopping BetzBotz...")
        self.running = False
    
    def get_status(self):
        """Get current bot status."""
        uptime = 0
        if self.start_time:
            uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            "running": self.running,
            "ai_mode": Config.AI_MODE_ENABLED,
            "connected": True,
            "uptime_seconds": int(uptime),
        }
    
    def get_stats(self):
        """Get bot statistics."""
        return {
            "markets_detected": self.markets_detected,
            "orders_placed": self.orders_placed,
            "orders_filled": self.orders_filled,
            "fill_rate": (self.orders_filled / self.orders_placed * 100) if self.orders_placed > 0 else 0,
            "total_trades": self.orders_filled,
            "win_rate": 0,
            "total_pnl": 0,
        }


# Global bot instance
bot = BetzBotz()


def run_api():
    """Run the API server."""
    import uvicorn
    from api.server import app
    
    logger.info(f"🌐 Starting API server on port {Config.API_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=Config.API_PORT)


def main():
    parser = argparse.ArgumentParser(description="BetzBotz Trading Bot")
    parser.add_argument("--api", action="store_true", help="Run API server")
    args = parser.parse_args()
    
    if args.api:
        run_api()
    else:
        asyncio.run(bot.start())


if __name__ == "__main__":
    main()
