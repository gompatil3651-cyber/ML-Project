import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Dict, Any

def render_candlestick_chart(history_data: List[Dict[str, Any]], ticker: str) -> go.Figure:
    """
    Renders an interactive, light-themed candlestick chart with SMA/EMA overlays and volume subplot.
    """
    if not history_data:
        fig = go.Figure()
        fig.add_annotation(text="No historical price data available", showarrow=False)
        return fig

    df = pd.DataFrame(history_data)
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.75, 0.25],
        subplot_titles=(f"{ticker} Price & Moving Averages", "Volume")
    )

    # 1. Candlestick
    fig.add_trace(
        go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="OHLC",
            increasing_line_color="#10B981",
            decreasing_line_color="#EF4444",
            increasing_fillcolor="#10B981",
            decreasing_fillcolor="#EF4444"
        ),
        row=1, col=1
    )

    # 2. SMA 20 Overlay
    if 'SMA_20' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df['Date'],
                y=df['SMA_20'],
                line=dict(color="#2563EB", width=1.5),
                name="SMA 20"
            ),
            row=1, col=1
        )

    # 3. EMA 20 Overlay
    if 'EMA_20' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df['Date'],
                y=df['EMA_20'],
                line=dict(color="#8B5CF6", width=1.5, dash="dot"),
                name="EMA 20"
            ),
            row=1, col=1
        )

    # 4. Volume Bar Chart
    colors = ['#10B981' if c >= o else '#EF4444' for c, o in zip(df['Close'], df['Open'])]
    fig.add_trace(
        go.Bar(
            x=df['Date'],
            y=df['Volume'],
            marker_color=colors,
            name="Volume",
            opacity=0.6
        ),
        row=2, col=1
    )

    # Styling for sleek light theme
    fig.update_layout(
        template="plotly_white",
        height=520,
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_rangeslider_visible=False,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        hovermode="x unified"
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#F1F5F9")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#F1F5F9")

    return fig

def render_rsi_chart(history_data: List[Dict[str, Any]]) -> go.Figure:
    """
    Renders the 14-period Relative Strength Index (RSI) chart with overbought/oversold bands.
    """
    df = pd.DataFrame(history_data)
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])

    fig = go.Figure()

    if 'RSI_14' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df['Date'],
                y=df['RSI_14'],
                line=dict(color="#F59E0B", width=2),
                name="RSI 14"
            )
        )

        # Overbought (70) and Oversold (30) reference lines
        fig.add_hline(y=70, line_dash="dash", line_color="#EF4444", annotation_text="Overbought (70)", annotation_position="top left")
        fig.add_hline(y=30, line_dash="dash", line_color="#10B981", annotation_text="Oversold (30)", annotation_position="bottom left")
        fig.add_hrect(y0=30, y1=70, fillcolor="#F8FAFC", opacity=0.5, line_width=0)

    fig.update_layout(
        title="Relative Strength Index (RSI 14)",
        template="plotly_white",
        height=220,
        margin=dict(l=20, r=20, t=35, b=20),
        yaxis=dict(range=[10, 90]),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF"
    )
    fig.update_xaxes(showgrid=True, gridcolor="#F1F5F9")
    fig.update_yaxes(showgrid=True, gridcolor="#F1F5F9")

    return fig
