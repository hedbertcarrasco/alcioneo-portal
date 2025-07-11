import requests
from datetime import datetime, timedelta
import pandas as pd
from typing import Optional, Dict, List
import time
import json
import os
from functools import wraps
import hashlib


def rate_limit(calls_per_minute=5):
    """Decorator to rate limit API calls"""
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator


class CacheManager:
    def __init__(self, cache_dir="cache", ttl_minutes=5):
        self.cache_dir = cache_dir
        self.ttl_minutes = ttl_minutes
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, url, params):
        """Generate a unique cache key from URL and params"""
        key_str = f"{url}_{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, url, params):
        """Get cached data if available and not expired"""
        cache_key = self._get_cache_key(url, params)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            # Check if cache is still valid
            file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
            if datetime.now() - file_time < timedelta(minutes=self.ttl_minutes):
                with open(cache_file, 'r') as f:
                    return json.load(f)
        return None
    
    def set(self, url, params, data):
        """Save data to cache"""
        cache_key = self._get_cache_key(url, params)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        with open(cache_file, 'w') as f:
            json.dump(data, f)


class PolygonClient:
    def __init__(self, api_keys, rate_limit_per_minute=5):
        # Support both single key (string) and multiple keys (list)
        if isinstance(api_keys, str):
            self.api_keys = [api_keys]
        else:
            self.api_keys = api_keys
            
        self.current_key_index = 0
        self.base_url = "https://api.polygon.io"
        self.sessions = []
        
        # Create a session for each API key
        for api_key in self.api_keys:
            session = requests.Session()
            session.headers.update({
                "Authorization": f"Bearer {api_key}"
            })
            self.sessions.append(session)
            
        self.cache = CacheManager()
        # Rate limit is per key, so total rate limit is multiplied
        self.rate_limit_per_minute = rate_limit_per_minute * len(self.api_keys)
        self.last_request_times = [0] * len(self.api_keys)
        self.min_interval = 60.0 / rate_limit_per_minute
        self.request_counts = [0] * len(self.api_keys)  # Track requests per key
        
    def _get_next_key_index(self):
        """Get the next API key to use (round-robin with rate limiting check)"""
        # Try to find a key that hasn't hit rate limit
        for _ in range(len(self.api_keys)):
            elapsed = time.time() - self.last_request_times[self.current_key_index]
            if elapsed >= self.min_interval:
                return self.current_key_index
            # Move to next key
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        
        # All keys are rate limited, use the one with longest elapsed time
        oldest_time_index = 0
        oldest_time = self.last_request_times[0]
        for i in range(1, len(self.api_keys)):
            if self.last_request_times[i] < oldest_time:
                oldest_time = self.last_request_times[i]
                oldest_time_index = i
        
        self.current_key_index = oldest_time_index
        return self.current_key_index
    
    def _wait_if_needed(self, key_index):
        """Enforce rate limiting for specific key"""
        elapsed = time.time() - self.last_request_times[key_index]
        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            print(f"Rate limiting on key {key_index + 1}/{len(self.api_keys)}: waiting {wait_time:.2f} seconds...")
            time.sleep(wait_time)
    
    def _make_request(self, url: str, params: Dict, max_retries: int = 3) -> Optional[Dict]:
        """Make HTTP request with caching, rate limiting, and retry logic"""
        # Check cache first
        cached_data = self.cache.get(url, params)
        if cached_data:
            print(f"Using cached data for {url}")
            return cached_data
        
        # Try each API key if needed
        for key_attempt in range(len(self.api_keys)):
            # Get next available key
            key_index = self._get_next_key_index()
            session = self.sessions[key_index]
            
            # Rate limiting for this specific key
            self._wait_if_needed(key_index)
            
            for attempt in range(max_retries):
                try:
                    print(f"Using API key {key_index + 1}/{len(self.api_keys)} for request...")
                    response = session.get(url, params=params)
                    self.last_request_times[key_index] = time.time()
                    self.request_counts[key_index] += 1
                    
                    if response.status_code == 429:
                        # Rate limit exceeded on this key
                        retry_after = int(response.headers.get('Retry-After', 60))
                        print(f"Rate limit exceeded on key {key_index + 1}. Waiting {retry_after} seconds...")
                        # Mark this key as rate limited
                        self.last_request_times[key_index] = time.time() + retry_after
                        # Try next key
                        break
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    # Cache successful response
                    self.cache.set(url, params, data)
                    
                    # Log statistics
                    total_requests = sum(self.request_counts)
                    print(f"Request successful. Total requests: {total_requests} " +
                          f"(Key distribution: {self.request_counts})")
                    
                    return data
                    
                except requests.exceptions.RequestException as e:
                    print(f"Error on attempt {attempt + 1} with key {key_index + 1}: {e}")
                    if attempt < max_retries - 1:
                        # Exponential backoff
                        wait_time = (2 ** attempt) * 5
                        print(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        print(f"Max retries reached for key {key_index + 1}")
                        # Try next key
                        break
            
            # Move to next key for next attempt
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        
        print(f"All API keys exhausted. Request failed.")
        return None
    
    def get_aggregates(self, ticker: str, multiplier: int, timespan: str, 
                      from_date: str, to_date: str, adjusted: bool = True) -> Dict:
        endpoint = f"/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
        
        params = {
            "adjusted": str(adjusted).lower(),
            "sort": "asc",
            "limit": 50000
        }
        
        url = f"{self.base_url}{endpoint}"
        return self._make_request(url, params)
    
    def get_ticker_details(self, ticker: str) -> Dict:
        endpoint = f"/v3/reference/tickers/{ticker}"
        url = f"{self.base_url}{endpoint}"
        return self._make_request(url, {})
    
    def get_daily_open_close(self, ticker: str, date: str) -> Dict:
        endpoint = f"/v1/open-close/{ticker}/{date}"
        url = f"{self.base_url}{endpoint}"
        return self._make_request(url, {})
    
    def aggregates_to_dataframe(self, aggregates_data: Dict) -> Optional[pd.DataFrame]:
        if not aggregates_data or "results" not in aggregates_data:
            return None
        
        results = aggregates_data["results"]
        if not results:
            return None
        
        df = pd.DataFrame(results)
        
        df["datetime"] = pd.to_datetime(df["t"], unit="ms")
        
        df = df.rename(columns={
            "o": "open",
            "h": "high",
            "l": "low",
            "c": "close",
            "v": "volume",
            "vw": "vwap",
            "n": "transactions"
        })
        
        df = df.set_index("datetime")
        
        return df[["open", "high", "low", "close", "volume", "vwap", "transactions"]]
    
    def get_forex_aggregates(self, ticker: str, multiplier: int, timespan: str,
                            from_date: str, to_date: str) -> Dict:
        endpoint = f"/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
        
        params = {
            "adjusted": "true",
            "sort": "asc",
            "limit": 50000
        }
        
        url = f"{self.base_url}{endpoint}"
        return self._make_request(url, params)
    
    def get_crypto_aggregates(self, ticker: str, multiplier: int, timespan: str,
                             from_date: str, to_date: str) -> Dict:
        endpoint = f"/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
        
        params = {
            "adjusted": "true",
            "sort": "asc",
            "limit": 50000
        }
        
        url = f"{self.base_url}{endpoint}"
        return self._make_request(url, params)
    
    def clear_cache(self):
        """Clear all cached data"""
        cache_files = os.listdir(self.cache.cache_dir)
        for file in cache_files:
            if file.endswith('.json'):
                os.remove(os.path.join(self.cache.cache_dir, file))
        print(f"Cleared {len(cache_files)} cache files")