import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional


class ChartVisualizer:
    def __init__(self):
        self.default_layout = {
            'template': 'plotly_dark',
            'height': 800,
            'showlegend': True,
            'xaxis_rangeslider_visible': False
        }
    
    def create_candlestick_chart(self, df: pd.DataFrame, ticker: str) -> go.Figure:
        fig = go.Figure()
        
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price'
        ))
        
        if 'SMA_20' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['SMA_20'],
                name='SMA 20',
                line=dict(color='yellow', width=1)
            ))
        
        if 'SMA_50' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['SMA_50'],
                name='SMA 50',
                line=dict(color='orange', width=1)
            ))
        
        if 'BB_upper' in df.columns and 'BB_lower' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['BB_upper'],
                name='BB Upper',
                line=dict(color='gray', width=1, dash='dash')
            ))
            
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['BB_lower'],
                name='BB Lower',
                line=dict(color='gray', width=1, dash='dash'),
                fill='tonexty',
                fillcolor='rgba(128, 128, 128, 0.1)'
            ))
        
        fig.update_layout(
            title=f'{ticker} - Price Chart',
            yaxis_title='Price',
            **self.default_layout
        )
        
        return fig
    
    def create_technical_indicators_chart(self, df: pd.DataFrame, ticker: str) -> go.Figure:
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.5, 0.2, 0.15, 0.15],
            subplot_titles=(f'{ticker} Price', 'Volume', 'MACD', 'RSI')
        )
        
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price'
        ), row=1, col=1)
        
        colors = ['red' if row['close'] < row['open'] else 'green' 
                 for idx, row in df.iterrows()]
        
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['volume'],
            name='Volume',
            marker_color=colors
        ), row=2, col=1)
        
        if 'MACD' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['MACD'],
                name='MACD',
                line=dict(color='blue', width=1)
            ), row=3, col=1)
            
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['MACD_signal'],
                name='Signal',
                line=dict(color='red', width=1)
            ), row=3, col=1)
            
            fig.add_trace(go.Bar(
                x=df.index,
                y=df['MACD_histogram'],
                name='Histogram',
                marker_color='gray'
            ), row=3, col=1)
        
        if 'RSI' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['RSI'],
                name='RSI',
                line=dict(color='purple', width=1)
            ), row=4, col=1)
            
            fig.add_hline(y=70, line_dash="dash", line_color="red", 
                         annotation_text="Overbought", row=4, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", 
                         annotation_text="Oversold", row=4, col=1)
        
        fig.update_xaxes(title_text="Date", row=4, col=1)
        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="MACD", row=3, col=1)
        fig.update_yaxes(title_text="RSI", row=4, col=1)
        
        fig.update_layout(
            height=1000,
            template='plotly_dark',
            showlegend=True,
            xaxis_rangeslider_visible=False
        )
        
        return fig
    
    def create_comparison_chart(self, data_dict: Dict[str, pd.DataFrame]) -> go.Figure:
        fig = go.Figure()
        
        for ticker, df in data_dict.items():
            normalized_close = (df['close'] / df['close'].iloc[0]) * 100
            
            fig.add_trace(go.Scatter(
                x=df.index,
                y=normalized_close,
                name=ticker,
                mode='lines'
            ))
        
        fig.update_layout(
            title='Normalized Price Comparison (Base = 100)',
            yaxis_title='Relative Performance (%)',
            xaxis_title='Date',
            **self.default_layout
        )
        
        return fig
    
    def create_volume_profile_chart(self, df: pd.DataFrame, ticker: str, bins: int = 30) -> go.Figure:
        fig = make_subplots(
            rows=1, cols=2,
            column_widths=[0.7, 0.3],
            shared_yaxes=True,
            horizontal_spacing=0.01
        )
        
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price'
        ), row=1, col=1)
        
        price_range = pd.cut(df['close'], bins=bins)
        volume_profile = df.groupby(price_range)['volume'].sum()
        
        fig.add_trace(go.Bar(
            x=volume_profile.values,
            y=[interval.mid for interval in volume_profile.index],
            orientation='h',
            name='Volume Profile',
            marker_color='cyan'
        ), row=1, col=2)
        
        fig.update_xaxes(title_text="Date", row=1, col=1)
        fig.update_xaxes(title_text="Volume", row=1, col=2)
        fig.update_yaxes(title_text="Price", row=1, col=1)
        
        fig.update_layout(
            title=f'{ticker} - Price with Volume Profile',
            height=600,
            template='plotly_dark',
            showlegend=False,
            xaxis1_rangeslider_visible=False
        )
        
        return fig
    
    def create_correlation_heatmap(self, data_dict: Dict[str, pd.DataFrame]) -> go.Figure:
        close_prices = pd.DataFrame({
            ticker: df['close'] for ticker, df in data_dict.items()
        })
        
        correlation_matrix = close_prices.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=correlation_matrix.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 12}
        ))
        
        fig.update_layout(
            title='Price Correlation Matrix',
            height=600,
            template='plotly_dark'
        )
        
        return fig