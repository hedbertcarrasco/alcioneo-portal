# API Configuration for AlcioNEO MVP

# Polygon API Rate Limits
# Free tier: 5 API calls per minute
# Basic tier: 100 API calls per minute
# Pro tier: 1000 API calls per minute

POLYGON_CONFIG = {
    "rate_limit_per_minute": 5,  # Adjust based on your tier
    "cache_ttl_minutes": 5,      # Cache data for 5 minutes
    "live_refresh_seconds": 10,   # Live mode refresh interval
    "max_retries": 3,            # Max retries for failed requests
    "retry_delay_base": 5,       # Base delay for exponential backoff
}

# Timeframe configurations
TIMEFRAME_CONFIG = {
    "live": {
        "actual_timeframe": "minute",
        "days_back": 1,
        "max_points": 100  # Limit data points for live view
    },
    "minute": {
        "max_days": 7      # Limit minute data to 7 days
    },
    "5minute": {
        "max_days": 30     # Limit 5-minute data to 30 days
    },
    "15minute": {
        "max_days": 60     # Limit 15-minute data to 60 days
    },
    "hour": {
        "max_days": 365    # Limit hourly data to 1 year
    },
    "day": {
        "max_days": 1825   # Limit daily data to 5 years
    },
    "week": {
        "max_days": 3650   # Limit weekly data to 10 years
    }
}

# API Usage Tips
API_USAGE_TIPS = """
To avoid hitting rate limits:
1. Use larger timeframes when possible (daily instead of minute)
2. Enable caching (data is cached for 5 minutes)
3. In live mode, data refreshes every 10 seconds
4. Consider upgrading your Polygon plan for more API calls
5. Use the 'Clear Cache' button if you need fresh data

Current tier: Free (5 calls/minute)
"""