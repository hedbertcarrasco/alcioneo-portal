# AlcioNEO MVP - Trading Dashboard

## Overview
This is the MVP for AlcioNEO, a modular algorithmic trading system. This initial version provides a web-based dashboard for fetching and visualizing market data from Polygon.io.

## Features
- Real-time market data fetching for stocks, forex, and cryptocurrencies
- Interactive candlestick charts with technical indicators
- Multiple chart types: Candlestick, Technical Indicators, Volume Profile
- Market statistics display
- Support for multiple timeframes (1 minute to weekly)
- Technical indicators: SMA, EMA, MACD, RSI, Bollinger Bands, ATR

## Installation

1. Navigate to the MVP directory:
```bash
cd /Users/hedbertcarrasco/Documents/Projects/Personal/AlcioNEO/MVP
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Make sure your Polygon API key is in the `polygon-api.txt` file

2. Run the application:
```bash
cd src
python app.py
```

3. Open your browser and navigate to: `http://localhost:8050`

4. Use the dashboard:
   - Select asset type (Stocks, Forex, or Crypto)
   - Enter ticker symbol (e.g., AAPL for stocks, EURUSD for forex, BTCUSD for crypto)
   - Choose time period and timeframe
   - Select chart type
   - Click "Fetch Data"

## Project Structure
```
MVP/
├── src/
│   ├── __init__.py
│   ├── app.py              # Main Dash application
│   ├── polygon_client.py   # Polygon API client
│   ├── data_fetcher.py     # Data fetching and processing
│   └── visualization.py    # Chart creation and visualization
├── data/                   # Data storage (currently unused)
├── config/                 # Configuration files (currently unused)
├── polygon-api.txt        # Polygon API key
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Next Steps
- Implement the 7-bot architecture (Bastión, Centinela, Radar, Nexo, Guardian, Chronos, Éter)
- Add real-time data streaming
- Implement trading strategy backtesting
- Add portfolio management features
- Integrate broker connectivity