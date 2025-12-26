"""
BetzBotz Configuration
Loads settings from environment variables
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Polymarket Credentials
    POLYMARKET_PRIVATE_KEY = os.getenv("POLYMARKET_PRIVATE_KEY", "")
    POLYMARKET_API_KEY = os.getenv("POLYMARKET_API_KEY", "")
    
    # Trading Settings
    MAX_BET_PER_SIDE = float(os.getenv("MAX_BET_PER_SIDE", "0.50"))
    MIN_MARKET_VOLUME = float(os.getenv("MIN_MARKET_VOLUME", "500"))
    MAX_ENTRY_PRICE = float(os.getenv("MAX_ENTRY_PRICE", "0.05"))
    MIN_HOURS_TO_EXPIRY = int(os.getenv("MIN_HOURS_TO_EXPIRY", "48"))
    MAX_DAYS_TO_EXPIRY = int(os.getenv("MAX_DAYS_TO_EXPIRY", "90"))
    
    # Take Profit Tiers (price multiplier, percent to sell)
    TAKE_PROFIT_TIERS = [
        (float(os.getenv("TAKE_PROFIT_TIER_1_MULTIPLIER", "2")), float(os.getenv("TAKE_PROFIT_TIER_1_PERCENT", "25"))),
        (float(os.getenv("TAKE_PROFIT_TIER_2_MULTIPLIER", "3")), float(os.getenv("TAKE_PROFIT_TIER_2_PERCENT", "25"))),
        (float(os.getenv("TAKE_PROFIT_TIER_3_MULTIPLIER", "5")), float(os.getenv("TAKE_PROFIT_TIER_3_PERCENT", "25"))),
        (float(os.getenv("TAKE_PROFIT_TIER_4_MULTIPLIER", "10")), float(os.getenv("TAKE_PROFIT_TIER_4_PERCENT", "25"))),
    ]
    
    # AI Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    AI_MODE_ENABLED = os.getenv("AI_MODE_ENABLED", "false").lower() == "true"
    
    # API Settings
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_SECRET_KEY = os.getenv("API_SECRET_KEY", "change-me-in-production")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://betzbotz.app,http://localhost:3000").split(",")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """Check required settings are present."""
        errors = []
        if not cls.POLYMARKET_PRIVATE_KEY:
            errors.append("POLYMARKET_PRIVATE_KEY is required")
        return errors
    
    @classmethod
    def to_dict(cls):
        """Return safe settings (no secrets)."""
        return {
            "max_bet_per_side": cls.MAX_BET_PER_SIDE,
            "min_market_volume": cls.MIN_MARKET_VOLUME,
            "max_entry_price": cls.MAX_ENTRY_PRICE,
            "min_hours_to_expiry": cls.MIN_HOURS_TO_EXPIRY,
            "max_days_to_expiry": cls.MAX_DAYS_TO_EXPIRY,
            "ai_mode_enabled": cls.AI_MODE_ENABLED,
        }
