from polygon_client import PolygonClient
from datetime import datetime, timedelta
import pandas as pd
from typing import Optional, List, Dict


class DataFetcher:
    def __init__(self, api_keys):
        # Support both single key and multiple keys
        self.client = PolygonClient(api_keys)
    
    def fetch_stock_data(self, ticker: str, days_back: int = 30, 
                        timespan: str = "day") -> Optional[pd.DataFrame]:
        # Use yesterday as the end date to ensure data availability
        to_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=days_back + 1)).strftime("%Y-%m-%d")
        
        print(f"Fetching {ticker} data from {from_date} to {to_date}")
        
        data = self.client.get_aggregates(
            ticker=ticker,
            multiplier=1,
            timespan=timespan,
            from_date=from_date,
            to_date=to_date
        )
        
        if data:
            return self.client.aggregates_to_dataframe(data)
        return None
    
    def fetch_forex_data(self, ticker: str, days_back: int = 30,
                        timespan: str = "day") -> Optional[pd.DataFrame]:
        # Use yesterday as the end date to ensure data availability
        to_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=days_back + 1)).strftime("%Y-%m-%d")
        
        print(f"Fetching forex {ticker} data from {from_date} to {to_date}")
        
        ticker_formatted = f"C:{ticker}"
        
        data = self.client.get_forex_aggregates(
            ticker=ticker_formatted,
            multiplier=1,
            timespan=timespan,
            from_date=from_date,
            to_date=to_date
        )
        
        if data:
            return self.client.aggregates_to_dataframe(data)
        return None
    
    def fetch_crypto_data(self, ticker: str, days_back: int = 30,
                         timespan: str = "day") -> Optional[pd.DataFrame]:
        # Use yesterday as the end date to ensure data availability
        to_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=days_back + 1)).strftime("%Y-%m-%d")
        
        print(f"Fetching crypto {ticker} data from {from_date} to {to_date}")
        
        ticker_formatted = f"X:{ticker}"
        
        data = self.client.get_crypto_aggregates(
            ticker=ticker_formatted,
            multiplier=1,
            timespan=timespan,
            from_date=from_date,
            to_date=to_date
        )
        
        if data:
            return self.client.aggregates_to_dataframe(data)
        return None
    
    def fetch_multiple_stocks(self, tickers: List[str], days_back: int = 30,
                            timespan: str = "day") -> Dict[str, pd.DataFrame]:
        results = {}
        
        for ticker in tickers:
            df = self.fetch_stock_data(ticker, days_back, timespan)
            if df is not None:
                results[ticker] = df
            else:
                print(f"Failed to fetch data for {ticker}")
        
        return results
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        df['SMA_20'] = df['close'].rolling(window=20, min_periods=1).mean()
        df['SMA_50'] = df['close'].rolling(window=50, min_periods=1).mean()
        
        df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()
        
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['ATR'] = true_range.rolling(window=14).mean()
        
        df['BB_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
        df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
        
        return df