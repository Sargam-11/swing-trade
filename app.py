import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import config
from database import StockDatabase
from scoring_engine import ScoringEngine, run_daily_analysis
from data_fetcher import DataFetcher

# Page configuration
st.set_page_config(
    page_title="Swing Trade Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)


# Initialize components
@st.cache_resource
def get_database():
    return StockDatabase()


@st.cache_resource
def get_scoring_engine():
    return ScoringEngine()


# Force refresh database if holdings were just added
if 'refresh_db' not in st.session_state:
    st.session_state.refresh_db = False

if st.session_state.refresh_db:
    get_database.clear()
    get_scoring_engine.clear()
    st.session_state.refresh_db = False


def create_price_chart(chart_data, symbol):
    """Create interactive price chart with technical indicators"""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(f'{symbol} Price & Moving Averages', 'MACD', 'RSI'),
        row_heights=[0.5, 0.25, 0.25]
    )

    # Candlestick chart would go here if OHLC data available
    # For now, using line chart
    fig.add_trace(
        go.Scatter(x=chart_data.index, y=chart_data['Close'],
                  name='Price', line=dict(color='blue', width=2)),
        row=1, col=1
    )

    # Moving averages
    if 'sma_20' in chart_data.columns:
        fig.add_trace(
            go.Scatter(x=chart_data.index, y=chart_data['sma_20'],
                      name='SMA 20', line=dict(color='orange', width=1)),
            row=1, col=1
        )

    if 'sma_50' in chart_data.columns:
        fig.add_trace(
            go.Scatter(x=chart_data.index, y=chart_data['sma_50'],
                      name='SMA 50', line=dict(color='green', width=1)),
            row=1, col=1
        )

    if 'sma_200' in chart_data.columns:
        fig.add_trace(
            go.Scatter(x=chart_data.index, y=chart_data['sma_200'],
                      name='SMA 200', line=dict(color='red', width=1)),
            row=1, col=1
        )

    # Bollinger Bands
    if all(col in chart_data.columns for col in ['bb_upper', 'bb_lower', 'bb_middle']):
        fig.add_trace(
            go.Scatter(x=chart_data.index, y=chart_data['bb_upper'],
                      name='BB Upper', line=dict(color='gray', width=1, dash='dash')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=chart_data.index, y=chart_data['bb_lower'],
                      name='BB Lower', line=dict(color='gray', width=1, dash='dash')),
            row=1, col=1
        )

    # MACD
    if all(col in chart_data.columns for col in ['macd', 'macd_signal']):
        fig.add_trace(
            go.Scatter(x=chart_data.index, y=chart_data['macd'],
                      name='MACD', line=dict(color='blue', width=1)),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(x=chart_data.index, y=chart_data['macd_signal'],
                      name='Signal', line=dict(color='red', width=1)),
            row=2, col=1
        )

    # RSI
    if 'rsi' in chart_data.columns:
        fig.add_trace(
            go.Scatter(x=chart_data.index, y=chart_data['rsi'],
                      name='RSI', line=dict(color='purple', width=1)),
            row=3, col=1
        )
        # Add overbought/oversold lines
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

    fig.update_layout(height=800, showlegend=True, hovermode='x unified')
    fig.update_xaxes(rangeslider_visible=False)

    return fig


def display_recommendation_card(rec, show_add_button=False):
    """Display a recommendation as a card"""
    color = {
        'STRONG BUY': '#00FF00',
        'BUY': '#90EE90',
        'HOLD': '#FFD700',
        'SELL': '#FFA500',
        'STRONG SELL': '#FF0000'
    }.get(rec['recommendation'], '#CCCCCC')

    with st.container():
        # First row: Symbol and main info
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])

        with col1:
            st.markdown(f"### {rec['symbol']}")

        with col2:
            st.metric("Overall Score", f"{rec['score']:.1f}/100")

        with col3:
            tech_score = rec.get('technical_score', 0)
            st.metric("Technical", f"{tech_score:.1f}/100")

        with col4:
            fund_score = rec.get('fundamental_score', 0)
            st.metric("Fundamental", f"{fund_score:.1f}/100")

        with col5:
            price = rec.get('price_at_recommendation', rec.get('current_price', 0))
            st.metric("Price", f"${price:.2f}")

        # Second row: Reasoning and action
        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(f"**Analysis:** {rec['reasoning']}")

        with col2:
            st.markdown(f"**{rec['recommendation']}**")
            st.markdown(f"<div style='background-color:{color};padding:5px;border-radius:5px;text-align:center;'></div>",
                       unsafe_allow_html=True)

            if show_add_button:
                if st.button(f"Add to Holdings", key=f"add_{rec['symbol']}_{rec.get('id', 0)}"):
                    return rec['symbol'], price

        st.divider()
        return None, None


def main():
    st.title("📈 Swing Trade Analyzer")
    st.markdown("*AI-powered stock analysis for swing trading*")

    # Sidebar
    with st.sidebar:
        st.header("Settings")

        # Analysis controls
        if st.button("🔄 Run Daily Analysis", type="primary"):
            with st.spinner("Running analysis... This may take several minutes..."):
                try:
                    results = run_daily_analysis(config.STOCK_UNIVERSE, save_to_db=True)
                    st.success(f"Analysis complete! Found {len(results['buy_recommendations'])} buy opportunities")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error running analysis: {e}")

        st.divider()

        # Stock universe info
        st.subheader("Stock Universe")
        st.write(f"Total stocks: {len(config.STOCK_UNIVERSE)}")
        with st.expander("View all stocks"):
            st.write(", ".join(config.STOCK_UNIVERSE))

        st.divider()

        # Configuration
        st.subheader("Analysis Weights")
        st.write(f"Technical: {config.TECHNICAL_WEIGHT*100:.0f}%")
        st.write(f"Fundamental: {config.FUNDAMENTAL_WEIGHT*100:.0f}%")

    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Buy Recommendations",
        "💰 Sell Signals",
        "🔍 Stock Analysis",
        "📈 Portfolio Overview"
    ])

    db = get_database()
    engine = get_scoring_engine()

    # Tab 1: Buy Recommendations
    with tab1:
        st.header("Top Buy Recommendations")

        # Get latest recommendations
        buy_recs = db.get_latest_recommendations('STRONG BUY', limit=5)
        if buy_recs.empty:
            buy_recs = db.get_latest_recommendations('BUY', limit=5)

        if not buy_recs.empty:
            st.success(f"Found {len(buy_recs)} buy opportunities")

            for idx, rec in buy_recs.iterrows():
                symbol, price = display_recommendation_card(rec.to_dict(), show_add_button=True)
                if symbol:
                    # Show input for quantity
                    with st.form(key=f"form_{symbol}_{idx}"):
                        st.write(f"Add {symbol} to Holdings")
                        quantity = st.number_input("Quantity", min_value=1, value=10, key=f"qty_{symbol}_{idx}")
                        if st.form_submit_button("Confirm"):
                            try:
                                db.add_holding(
                                    symbol,
                                    datetime.now().strftime('%Y-%m-%d'),
                                    price,
                                    quantity
                                )
                                st.success(f"✅ Added {quantity} shares of {symbol} at ${price:.2f}")
                                st.balloons()
                                # Set flag to refresh database on next run
                                st.session_state.refresh_db = True
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error adding holding: {e}")
        else:
            st.info("No buy recommendations available. Run daily analysis to generate recommendations.")

    # Tab 2: Sell Signals
    with tab2:
        st.header("Sell Signals for Holdings")

        # Get active holdings
        holdings = db.get_active_holdings()

        if not holdings.empty:
            st.subheader("Current Holdings")

            # Display holdings table
            holdings_display = holdings[['symbol', 'purchase_date', 'purchase_price',
                                        'quantity']].copy()
            st.dataframe(holdings_display, use_container_width=True)

            # Check each holding for sell signals
            st.subheader("Sell Analysis")

            for idx, holding in holdings.iterrows():
                symbol = holding['symbol']
                current_price = engine.data_fetcher.get_current_price(symbol)

                if current_price:
                    profit_loss = (current_price - holding['purchase_price']) * holding['quantity']
                    profit_pct = ((current_price - holding['purchase_price']) /
                                 holding['purchase_price']) * 100

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric(f"{symbol}", f"${current_price:.2f}")

                    with col2:
                        st.metric("P/L", f"${profit_loss:.2f}",
                                 delta=f"{profit_pct:.1f}%")

                    with col3:
                        # Get latest recommendation
                        latest_rec = db.get_latest_recommendations(limit=100)
                        stock_rec = latest_rec[latest_rec['symbol'] == symbol]

                        if not stock_rec.empty:
                            rec = stock_rec.iloc[0]
                            st.write(f"Score: {rec['score']:.1f}")
                            st.write(f"**{rec['recommendation']}**")
                        else:
                            st.write("No analysis")

                    with col4:
                        if st.button(f"Sell {symbol}", key=f"sell_{symbol}"):
                            db.close_holding(
                                holding['id'],
                                datetime.now().strftime('%Y-%m-%d'),
                                current_price
                            )
                            st.success(f"Sold {symbol}")
                            st.rerun()

                st.divider()
        else:
            st.info("No active holdings. Add holdings from the Stock Analysis tab.")

    # Tab 3: Stock Analysis
    with tab3:
        st.header("Individual Stock Analysis")

        # Stock selector
        selected_symbol = st.selectbox(
            "Select a stock to analyze",
            options=config.STOCK_UNIVERSE
        )

        if st.button("Analyze Stock", type="primary"):
            with st.spinner(f"Analyzing {selected_symbol}..."):
                try:
                    analysis = engine.analyze_stock_details(selected_symbol)

                    if 'error' not in analysis:
                        # Display metrics
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric("Overall Score", f"{analysis['overall_score']:.1f}/100")

                        with col2:
                            st.metric("Technical Score", f"{analysis['technical_score']:.1f}/100")

                        with col3:
                            st.metric("Fundamental Score", f"{analysis['fundamental_score']:.1f}/100")

                        with col4:
                            st.metric("Recommendation", analysis['recommendation'])

                        st.divider()

                        # Reasoning
                        st.subheader("Analysis Reasoning")
                        st.info(analysis['reasoning'])

                        st.divider()

                        # Charts
                        st.subheader("Technical Charts")
                        if 'chart_data' in analysis:
                            fig = create_price_chart(analysis['chart_data'], selected_symbol)
                            st.plotly_chart(fig, use_container_width=True)

                        # Fundamental metrics
                        if analysis.get('fundamental_metrics'):
                            st.subheader("Fundamental Metrics")

                            metrics = analysis['fundamental_metrics']
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                if 'pe_ratio' in metrics and metrics['pe_ratio']:
                                    st.metric("P/E Ratio", f"{metrics['pe_ratio']:.2f}")
                                if 'profit_margin' in metrics and metrics['profit_margin']:
                                    st.metric("Profit Margin",
                                             f"{metrics['profit_margin']*100:.1f}%")

                            with col2:
                                if 'revenue_growth' in metrics and metrics['revenue_growth']:
                                    st.metric("Revenue Growth",
                                             f"{metrics['revenue_growth']*100:.1f}%")
                                if 'return_on_equity' in metrics and metrics['return_on_equity']:
                                    st.metric("ROE",
                                             f"{metrics['return_on_equity']*100:.1f}%")

                            with col3:
                                if 'debt_to_equity' in metrics and metrics['debt_to_equity']:
                                    st.metric("Debt/Equity", f"{metrics['debt_to_equity']:.2f}")
                                if 'beta' in metrics and metrics['beta']:
                                    st.metric("Beta", f"{metrics['beta']:.2f}")

                        # Add to holdings button
                        st.divider()
                        st.subheader("Add to Holdings")

                        with st.form(key=f"add_holding_{selected_symbol}"):
                            col1, col2 = st.columns(2)

                            with col1:
                                quantity = st.number_input("Quantity", min_value=1, value=10, key=f"holding_qty_{selected_symbol}")

                            with col2:
                                st.write("")  # Spacer
                                st.write("")  # Spacer
                                submit_button = st.form_submit_button("Add to Portfolio", type="primary")

                            if submit_button:
                                try:
                                    db.add_holding(
                                        selected_symbol,
                                        datetime.now().strftime('%Y-%m-%d'),
                                        analysis['current_price'],
                                        quantity
                                    )
                                    st.success(f"✅ Added {quantity} shares of {selected_symbol} at ${analysis['current_price']:.2f}")
                                    st.balloons()
                                    # Set flag to refresh database on next run
                                    st.session_state.refresh_db = True
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error adding holding: {e}")

                    else:
                        st.error(analysis['error'])

                except Exception as e:
                    st.error(f"Error analyzing stock: {e}")

    # Tab 4: Portfolio Overview
    with tab4:
        st.header("Portfolio Performance Overview")

        holdings = db.get_active_holdings()

        if not holdings.empty:
            total_value = 0
            total_cost = 0

            portfolio_data = []

            for idx, holding in holdings.iterrows():
                current_price = engine.data_fetcher.get_current_price(holding['symbol'])

                if current_price:
                    cost = holding['purchase_price'] * holding['quantity']
                    value = current_price * holding['quantity']
                    pl = value - cost
                    pl_pct = (pl / cost) * 100

                    total_value += value
                    total_cost += cost

                    portfolio_data.append({
                        'Symbol': holding['symbol'],
                        'Quantity': holding['quantity'],
                        'Purchase Price': f"${holding['purchase_price']:.2f}",
                        'Current Price': f"${current_price:.2f}",
                        'Cost': f"${cost:.2f}",
                        'Value': f"${value:.2f}",
                        'P/L': f"${pl:.2f}",
                        'P/L %': f"{pl_pct:.1f}%"
                    })

            # Summary metrics
            total_pl = total_value - total_cost
            total_pl_pct = (total_pl / total_cost * 100) if total_cost > 0 else 0

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Value", f"${total_value:.2f}")

            with col2:
                st.metric("Total Cost", f"${total_cost:.2f}")

            with col3:
                st.metric("Total P/L", f"${total_pl:.2f}",
                         delta=f"{total_pl_pct:.1f}%")

            with col4:
                st.metric("# Holdings", len(holdings))

            st.divider()

            # Portfolio table
            st.subheader("Holdings Detail")
            portfolio_df = pd.DataFrame(portfolio_data)
            st.dataframe(portfolio_df, use_container_width=True)

        else:
            st.info("No active holdings to display")

        # Closed positions
        st.divider()
        st.subheader("Trade History")

        all_holdings = pd.read_sql(
            "SELECT * FROM holdings WHERE status = 'CLOSED' ORDER BY sell_date DESC LIMIT 10",
            db.engine
        )

        if not all_holdings.empty:
            history_data = []

            for idx, trade in all_holdings.iterrows():
                history_data.append({
                    'Symbol': trade['symbol'],
                    'Buy Date': trade['purchase_date'],
                    'Sell Date': trade['sell_date'],
                    'Buy Price': f"${trade['purchase_price']:.2f}",
                    'Sell Price': f"${trade['sell_price']:.2f}",
                    'Quantity': trade['quantity'],
                    'P/L': f"${trade['profit_loss']:.2f}"
                })

            history_df = pd.DataFrame(history_data)
            st.dataframe(history_df, use_container_width=True)
        else:
            st.info("No trade history available")


if __name__ == "__main__":
    main()
