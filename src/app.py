import dash
from dash import dcc, html, Input, Output, State, no_update
import dash_bootstrap_components as dbc
from data_fetcher import DataFetcher
from visualization import ChartVisualizer
import os
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to get API keys from environment variable first (for Vercel)
if os.environ.get('POLYGON_API_KEYS'):
    # In Vercel, store multiple keys separated by commas
    API_KEYS = [key.strip() for key in os.environ.get('POLYGON_API_KEYS').split(',')]
else:
    # Local development: read from file
    api_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'polygon-api.txt')
    if os.path.exists(api_file_path):
        with open(api_file_path, 'r') as f:
            content = f.read().strip()
            # Extract all API keys (looking for lines that are API keys)
            lines = content.split('\n')
            API_KEYS = []
            for line in lines:
                line = line.strip()
                # API keys are typically 32 characters and contain letters/numbers/underscores
                if len(line) >= 32 and line.replace('_', '').isalnum():
                    API_KEYS.append(line)
    else:
        API_KEYS = []
    
# Use the first key as default for backward compatibility
API_KEY = API_KEYS[0] if API_KEYS else ""

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

fetcher = DataFetcher(API_KEYS)  # Pass all API keys for rotation
visualizer = ChartVisualizer()

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("AlcioNEO MVP - Trading Dashboard", className="text-center mb-4"),
            html.Hr()
        ])
    ]),
    
    dbc.Alert(
        [
            html.H6("📊 API Usage Information", className="alert-heading"),
            html.P(f"Using {len(API_KEYS)} API keys | {5 * len(API_KEYS)} total calls/minute | Data cached for 5 minutes | Live mode refreshes every 10 seconds", className="mb-0")
        ],
        color="info",
        dismissable=True,
        is_open=True,
        className="mb-3"
    ),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Market Selection", className="card-title"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Asset Type"),
                            dbc.Select(
                                id="asset-type",
                                options=[
                                    {"label": "Stocks", "value": "stock"},
                                    {"label": "Forex", "value": "forex"},
                                    {"label": "Crypto", "value": "crypto"}
                                ],
                                value="stock"
                            )
                        ], md=4),
                        dbc.Col([
                            dbc.Label("Ticker Symbol"),
                            dbc.Select(
                                id="ticker-input",
                                options=[
                                    {"label": "--- Stocks ---", "value": "", "disabled": True},
                                    {"label": "AAPL (Apple Inc.)", "value": "AAPL"},
                                    {"label": "MSFT (Microsoft Corporation)", "value": "MSFT"},
                                    {"label": "GOOGL (Alphabet Inc.)", "value": "GOOGL"},
                                    {"label": "AMZN (Amazon.com Inc.)", "value": "AMZN"},
                                    {"label": "TSLA (Tesla Inc.)", "value": "TSLA"},
                                    {"label": "META (Meta Platforms Inc.)", "value": "META"},
                                    {"label": "NVDA (NVIDIA Corporation)", "value": "NVDA"},
                                    {"label": "JPM (JPMorgan Chase & Co.)", "value": "JPM"},
                                    {"label": "V (Visa Inc.)", "value": "V"},
                                    {"label": "WMT (Walmart Inc.)", "value": "WMT"},
                                    {"label": "--- Forex ---", "value": "", "disabled": True},
                                    {"label": "EURUSD (Euro/US Dollar)", "value": "EURUSD"},
                                    {"label": "GBPUSD (British Pound/US Dollar)", "value": "GBPUSD"},
                                    {"label": "USDJPY (US Dollar/Japanese Yen)", "value": "USDJPY"},
                                    {"label": "AUDUSD (Australian Dollar/US Dollar)", "value": "AUDUSD"},
                                    {"label": "USDCAD (US Dollar/Canadian Dollar)", "value": "USDCAD"},
                                    {"label": "USDCHF (US Dollar/Swiss Franc)", "value": "USDCHF"},
                                    {"label": "--- Crypto ---", "value": "", "disabled": True},
                                    {"label": "BTCUSD (Bitcoin/US Dollar)", "value": "BTCUSD"},
                                    {"label": "ETHUSD (Ethereum/US Dollar)", "value": "ETHUSD"},
                                    {"label": "BNBUSD (Binance Coin/US Dollar)", "value": "BNBUSD"},
                                    {"label": "XRPUSD (Ripple/US Dollar)", "value": "XRPUSD"},
                                    {"label": "ADAUSD (Cardano/US Dollar)", "value": "ADAUSD"},
                                    {"label": "DOGEUSD (Dogecoin/US Dollar)", "value": "DOGEUSD"},
                                    {"label": "SOLUSD (Solana/US Dollar)", "value": "SOLUSD"}
                                ],
                                value="AAPL"
                            )
                        ], md=4),
                        dbc.Col([
                            dbc.Label("Time Period (days)"),
                            dbc.Input(
                                id="days-input",
                                type="number",
                                min=1,
                                max=365,
                                value=30
                            )
                        ], md=4)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Timeframe"),
                            dbc.Select(
                                id="timeframe-select",
                                options=[
                                    {"label": "🔴 Live (10s refresh)", "value": "live"},
                                    {"label": "1 Minute", "value": "minute"},
                                    {"label": "5 Minutes", "value": "5minute"},
                                    {"label": "15 Minutes", "value": "15minute"},
                                    {"label": "1 Hour", "value": "hour"},
                                    {"label": "Daily", "value": "day"},
                                    {"label": "Weekly", "value": "week"}
                                ],
                                value="day"
                            )
                        ], md=4),
                        dbc.Col([
                            dbc.Label("Chart Type"),
                            dbc.Select(
                                id="chart-type",
                                options=[
                                    {"label": "Candlestick", "value": "candlestick"},
                                    {"label": "Technical Indicators", "value": "technical"},
                                    {"label": "Volume Profile", "value": "volume_profile"}
                                ],
                                value="candlestick"
                            )
                        ], md=4),
                        dbc.Col([
                            dbc.ButtonGroup([
                                dbc.Button(
                                    "Fetch Data",
                                    id="fetch-button",
                                    color="primary",
                                    className="me-1"
                                ),
                                dbc.Button(
                                    "Clear Cache",
                                    id="clear-cache-button",
                                    color="secondary",
                                    outline=True
                                )
                            ], className="w-100 mt-4")
                        ], md=4)
                    ], className="mt-3")
                ])
            ])
        ], md=12)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Loading(
                        id="loading",
                        type="default",
                        children=[
                            html.Div(id="chart-container")
                        ]
                    )
                ])
            ])
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Market Statistics", className="card-title"),
                    html.Div(id="stats-container")
                ])
            ])
        ], md=12, className="mt-4")
    ]),
    
    dcc.Store(id="data-store"),
    dcc.Store(id="live-data-store"),  # Store for live mode data
    dcc.Interval(
        id='interval-component',
        interval=10000,  # 10 seconds in milliseconds (reduced from 1 second)
        n_intervals=0,
        disabled=True  # Start disabled
    ),
    html.Div(id="live-indicator", style={"position": "fixed", "top": "10px", "right": "10px", "zIndex": 1000})
    
], fluid=True)


@app.callback(
    Output("ticker-input", "options"),
    Input("asset-type", "value")
)
def update_ticker_options(asset_type):
    if asset_type == "stock":
        return [
            {"label": "AAPL (Apple Inc.)", "value": "AAPL"},
            {"label": "MSFT (Microsoft Corporation)", "value": "MSFT"},
            {"label": "GOOGL (Alphabet Inc.)", "value": "GOOGL"},
            {"label": "AMZN (Amazon.com Inc.)", "value": "AMZN"},
            {"label": "TSLA (Tesla Inc.)", "value": "TSLA"},
            {"label": "META (Meta Platforms Inc.)", "value": "META"},
            {"label": "NVDA (NVIDIA Corporation)", "value": "NVDA"},
            {"label": "JPM (JPMorgan Chase & Co.)", "value": "JPM"},
            {"label": "V (Visa Inc.)", "value": "V"},
            {"label": "WMT (Walmart Inc.)", "value": "WMT"},
            {"label": "BA (Boeing Company)", "value": "BA"},
            {"label": "DIS (Walt Disney Company)", "value": "DIS"}
        ]
    elif asset_type == "forex":
        return [
            {"label": "EURUSD (Euro/US Dollar)", "value": "EURUSD"},
            {"label": "GBPUSD (British Pound/US Dollar)", "value": "GBPUSD"},
            {"label": "USDJPY (US Dollar/Japanese Yen)", "value": "USDJPY"},
            {"label": "AUDUSD (Australian Dollar/US Dollar)", "value": "AUDUSD"},
            {"label": "USDCAD (US Dollar/Canadian Dollar)", "value": "USDCAD"},
            {"label": "USDCHF (US Dollar/Swiss Franc)", "value": "USDCHF"},
            {"label": "NZDUSD (New Zealand Dollar/US Dollar)", "value": "NZDUSD"},
            {"label": "EURGBP (Euro/British Pound)", "value": "EURGBP"}
        ]
    elif asset_type == "crypto":
        return [
            {"label": "BTCUSD (Bitcoin/US Dollar)", "value": "BTCUSD"},
            {"label": "ETHUSD (Ethereum/US Dollar)", "value": "ETHUSD"},
            {"label": "BNBUSD (Binance Coin/US Dollar)", "value": "BNBUSD"},
            {"label": "XRPUSD (Ripple/US Dollar)", "value": "XRPUSD"},
            {"label": "ADAUSD (Cardano/US Dollar)", "value": "ADAUSD"},
            {"label": "DOGEUSD (Dogecoin/US Dollar)", "value": "DOGEUSD"},
            {"label": "SOLUSD (Solana/US Dollar)", "value": "SOLUSD"},
            {"label": "MATICUSD (Polygon/US Dollar)", "value": "MATICUSD"}
        ]
    else:
        return []


@app.callback(
    [Output("data-store", "data"),
     Output("chart-container", "children"),
     Output("stats-container", "children")],
    [Input("fetch-button", "n_clicks")],
    [State("asset-type", "value"),
     State("ticker-input", "value"),
     State("days-input", "value"),
     State("timeframe-select", "value"),
     State("chart-type", "value")]
)
def update_dashboard(n_clicks, asset_type, ticker, days, timeframe, chart_type):
    if n_clicks is None:
        return None, html.Div("Click 'Fetch Data' to load market data"), html.Div()
    
    if not ticker:
        return None, html.Div("Please enter a ticker symbol"), html.Div()
    
    try:
        # Handle live mode differently
        if timeframe == "live":
            timeframe_actual = "minute"  # Use minute data for live view
            days_actual = 1  # Get last day of minute data
        else:
            timeframe_actual = timeframe
            days_actual = days
            
        if asset_type == "stock":
            df = fetcher.fetch_stock_data(ticker.upper(), days_actual, timeframe_actual)
        elif asset_type == "forex":
            df = fetcher.fetch_forex_data(ticker.upper(), days_actual, timeframe_actual)
        elif asset_type == "crypto":
            df = fetcher.fetch_crypto_data(ticker.upper(), days_actual, timeframe_actual)
        else:
            return None, html.Div("Invalid asset type"), html.Div()
        
        if df is None or df.empty:
            return None, html.Div(f"No data found for {ticker}"), html.Div()
        
        df_with_indicators = fetcher.calculate_technical_indicators(df)
        
        if chart_type == "candlestick":
            fig = visualizer.create_candlestick_chart(df_with_indicators, ticker.upper())
        elif chart_type == "technical":
            fig = visualizer.create_technical_indicators_chart(df_with_indicators, ticker.upper())
        elif chart_type == "volume_profile":
            fig = visualizer.create_volume_profile_chart(df_with_indicators, ticker.upper())
        else:
            fig = visualizer.create_candlestick_chart(df_with_indicators, ticker.upper())
        
        chart = dcc.Graph(figure=fig, style={'height': '800px'})
        
        latest_price = df_with_indicators['close'].iloc[-1]
        price_change = df_with_indicators['close'].iloc[-1] - df_with_indicators['close'].iloc[0]
        price_change_pct = (price_change / df_with_indicators['close'].iloc[0]) * 100
        
        total_volume = df_with_indicators['volume'].sum()
        avg_volume = df_with_indicators['volume'].mean()
        
        high = df_with_indicators['high'].max()
        low = df_with_indicators['low'].min()
        
        latest_rsi = df_with_indicators['RSI'].iloc[-1] if 'RSI' in df_with_indicators.columns else None
        
        stats = dbc.Row([
            dbc.Col([
                html.H6("Latest Price"),
                html.H4(f"${latest_price:.2f}", className="text-primary")
            ], md=2),
            dbc.Col([
                html.H6("Change"),
                html.H4(
                    f"{price_change:+.2f} ({price_change_pct:+.2f}%)",
                    className="text-success" if price_change >= 0 else "text-danger"
                )
            ], md=2),
            dbc.Col([
                html.H6("Period High"),
                html.H4(f"${high:.2f}", className="text-info")
            ], md=2),
            dbc.Col([
                html.H6("Period Low"),
                html.H4(f"${low:.2f}", className="text-info")
            ], md=2),
            dbc.Col([
                html.H6("Average Volume"),
                html.H4(f"{avg_volume:,.0f}")
            ], md=2),
            dbc.Col([
                html.H6("RSI (14)"),
                html.H4(
                    f"{latest_rsi:.2f}" if latest_rsi else "N/A",
                    className="text-warning" if latest_rsi and (latest_rsi > 70 or latest_rsi < 30) else ""
                )
            ], md=2)
        ])
        
        # Convert DataFrame to JSON-serializable format
        data_dict = {
            'dates': df_with_indicators.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            'open': df_with_indicators['open'].tolist(),
            'high': df_with_indicators['high'].tolist(),
            'low': df_with_indicators['low'].tolist(),
            'close': df_with_indicators['close'].tolist(),
            'volume': df_with_indicators['volume'].tolist()
        }
        
        return data_dict, chart, stats
        
    except Exception as e:
        error_msg = f"Error fetching data: {str(e)}"
        return None, html.Div(error_msg, className="text-danger"), html.Div()


# Callback to control interval component
@app.callback(
    [Output("interval-component", "disabled"),
     Output("live-indicator", "children")],
    [Input("timeframe-select", "value")]
)
def toggle_interval(timeframe):
    if timeframe == "live":
        indicator = dbc.Badge(
            "🔴 LIVE", 
            color="danger", 
            className="me-1 pulse-animation",
            style={"animation": "pulse 1s infinite"}
        )
        return False, indicator  # Enable interval
    else:
        return True, ""  # Disable interval


# Callback for live updates
@app.callback(
    [Output("chart-container", "children", allow_duplicate=True),
     Output("stats-container", "children", allow_duplicate=True)],
    [Input("interval-component", "n_intervals")],
    [State("asset-type", "value"),
     State("ticker-input", "value"),
     State("timeframe-select", "value"),
     State("chart-type", "value")],
    prevent_initial_call=True
)
def update_live_data(n_intervals, asset_type, ticker, timeframe, chart_type):
    if timeframe != "live" or not ticker:
        return no_update, no_update
    
    try:
        # Fetch latest minute data for live view
        if asset_type == "stock":
            df = fetcher.fetch_stock_data(ticker.upper(), 1, "minute")
        elif asset_type == "forex":
            df = fetcher.fetch_forex_data(ticker.upper(), 1, "minute")
        elif asset_type == "crypto":
            df = fetcher.fetch_crypto_data(ticker.upper(), 1, "minute")
        else:
            return no_update, no_update
        
        if df is None or df.empty:
            return no_update, no_update
        
        # Get last 100 data points for better visualization
        if asset_type == "stock":
            df_full = fetcher.fetch_stock_data(ticker.upper(), 1, "minute")
        elif asset_type == "forex":
            df_full = fetcher.fetch_forex_data(ticker.upper(), 1, "minute") 
        elif asset_type == "crypto":
            df_full = fetcher.fetch_crypto_data(ticker.upper(), 1, "minute")
            
        if df_full is not None and not df_full.empty:
            df_with_indicators = fetcher.calculate_technical_indicators(df_full)
            
            # Create chart with live annotation
            if chart_type == "candlestick":
                fig = visualizer.create_candlestick_chart(df_with_indicators, ticker.upper())
            elif chart_type == "technical":
                fig = visualizer.create_technical_indicators_chart(df_with_indicators, ticker.upper())
            elif chart_type == "volume_profile":
                fig = visualizer.create_volume_profile_chart(df_with_indicators, ticker.upper())
            else:
                fig = visualizer.create_candlestick_chart(df_with_indicators, ticker.upper())
            
            # Add live annotation
            fig.add_annotation(
                text=f"Live Update #{n_intervals}",
                xref="paper", yref="paper",
                x=0.02, y=0.98,
                showarrow=False,
                font=dict(size=12, color="red"),
                bgcolor="rgba(0,0,0,0.5)"
            )
            
            chart = dcc.Graph(figure=fig, style={'height': '800px'})
            
            # Update stats
            latest_price = df_with_indicators['close'].iloc[-1]
            price_change = df_with_indicators['close'].iloc[-1] - df_with_indicators['close'].iloc[0]
            price_change_pct = (price_change / df_with_indicators['close'].iloc[0]) * 100
            
            avg_volume = df_with_indicators['volume'].mean()
            high = df_with_indicators['high'].max()
            low = df_with_indicators['low'].min()
            latest_rsi = df_with_indicators['RSI'].iloc[-1] if 'RSI' in df_with_indicators.columns else None
            
            stats = dbc.Row([
                dbc.Col([
                    html.H6("Latest Price"),
                    html.H4(f"${latest_price:.2f}", className="text-primary")
                ], md=2),
                dbc.Col([
                    html.H6("Change"),
                    html.H4(
                        f"{price_change:+.2f} ({price_change_pct:+.2f}%)",
                        className="text-success" if price_change >= 0 else "text-danger"
                    )
                ], md=2),
                dbc.Col([
                    html.H6("Period High"),
                    html.H4(f"${high:.2f}", className="text-info")
                ], md=2),
                dbc.Col([
                    html.H6("Period Low"),
                    html.H4(f"${low:.2f}", className="text-info")
                ], md=2),
                dbc.Col([
                    html.H6("Average Volume"),
                    html.H4(f"{avg_volume:,.0f}")
                ], md=2),
                dbc.Col([
                    html.H6("RSI (14)"),
                    html.H4(
                        f"{latest_rsi:.2f}" if latest_rsi else "N/A",
                        className="text-warning" if latest_rsi and (latest_rsi > 70 or latest_rsi < 30) else ""
                    )
                ], md=2)
            ])
            
            return chart, stats
            
    except Exception as e:
        print(f"Error in live update: {e}")
        return no_update, no_update
    
    return dash.no_update, dash.no_update


# Add CSS for pulse animation
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            @keyframes pulse {
                0% {
                    opacity: 1;
                }
                50% {
                    opacity: 0.5;
                }
                100% {
                    opacity: 1;
                }
            }
            .pulse-animation {
                animation: pulse 1s infinite;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


# Callback for clear cache button
@app.callback(
    Output("clear-cache-button", "children"),
    Input("clear-cache-button", "n_clicks"),
    prevent_initial_call=True
)
def clear_cache(n_clicks):
    if n_clicks:
        # Clear the cache
        fetcher.client.clear_cache()
        return "Cache Cleared!"
    return "Clear Cache"


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8050)