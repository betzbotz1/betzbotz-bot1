"""
BetzBotz API Server
REST API for the frontend UI
"""

import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import Config
from polymarket.client import client
from polymarket.trading import engine

logger = logging.getLogger(__name__)

app = FastAPI(
    title="BetzBotz API",
    description="Trading bot API",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Auth dependency
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if Config.API_SECRET_KEY and Config.API_SECRET_KEY != "change-me-in-production":
        if x_api_key != Config.API_SECRET_KEY:
            raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


# Request models
class SettingsUpdate(BaseModel):
    max_bet_per_side: Optional[float] = None
    ai_mode_enabled: Optional[bool] = None
    min_market_volume: Optional[float] = None
    max_entry_price: Optional[float] = None


class SellRequest(BaseModel):
    token_id: str
    percent: int = 100


# Routes
@app.get("/")
async def root():
    return {"service": "BetzBotz API", "version": "1.0.0", "status": "ok"}


@app.get("/status")
async def get_status(api_key: str = Depends(verify_api_key)):
    """Get bot status."""
    # Import here to avoid circular import
    from main import bot
    return bot.get_status()


@app.get("/balance")
async def get_balance(api_key: str = Depends(verify_api_key)):
    """Get wallet balance."""
    return {
        "balance": client.get_balance(),
        "address": client.get_address(),
    }


@app.get("/positions")
async def get_positions(api_key: str = Depends(verify_api_key)):
    """Get open positions."""
    positions = engine.get_positions()
    return {
        "positions": positions,
        "total_value": engine.get_total_value(),
        "total_pnl": engine.get_total_pnl(),
    }


@app.get("/stats")
async def get_stats(api_key: str = Depends(verify_api_key)):
    """Get bot statistics."""
    from main import bot
    return bot.get_stats()


@app.get("/settings")
async def get_settings(api_key: str = Depends(verify_api_key)):
    """Get current settings."""
    return Config.to_dict()


@app.post("/settings")
async def update_settings(settings: SettingsUpdate, api_key: str = Depends(verify_api_key)):
    """Update bot settings."""
    if settings.max_bet_per_side is not None:
        Config.MAX_BET_PER_SIDE = settings.max_bet_per_side
    if settings.ai_mode_enabled is not None:
        Config.AI_MODE_ENABLED = settings.ai_mode_enabled
    if settings.min_market_volume is not None:
        Config.MIN_MARKET_VOLUME = settings.min_market_volume
    if settings.max_entry_price is not None:
        Config.MAX_ENTRY_PRICE = settings.max_entry_price
    
    logger.info(f"Settings updated: {settings}")
    return Config.to_dict()


@app.post("/bot/start")
async def start_bot(api_key: str = Depends(verify_api_key)):
    """Start the bot."""
    from main import bot
    import asyncio
    
    if not bot.running:
        asyncio.create_task(bot.start())
    
    return {"status": "started"}


@app.post("/bot/stop")
async def stop_bot(api_key: str = Depends(verify_api_key)):
    """Stop the bot."""
    from main import bot
    bot.stop()
    return {"status": "stopped"}


@app.post("/sell")
async def sell_position(req: SellRequest, api_key: str = Depends(verify_api_key)):
    """Sell a position."""
    result = engine.execute_sell(req.token_id, req.percent)
    if result:
        return result
    raise HTTPException(status_code=400, detail="Failed to sell position")


@app.post("/cancel-orders")
async def cancel_orders(api_key: str = Depends(verify_api_key)):
    """Cancel all open orders."""
    # TODO: Implement order cancellation
    return {"status": "ok", "cancelled": 0}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
