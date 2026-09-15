-- ============================================================================
-- QUANT AI: Multi-Modal Quantitative Intelligence Supabase Schema
-- Organization: szlgsmaolpgwjrvdgvut
-- Created: 2026-09-16
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ----------------------------------------------------------------------------
-- 1. MARKET DATA TABLE (OHLCV + Technical Indicators)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.market_ohlcv (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open NUMERIC(14, 4) NOT NULL,
    high NUMERIC(14, 4) NOT NULL,
    low NUMERIC(14, 4) NOT NULL,
    close NUMERIC(14, 4) NOT NULL,
    volume BIGINT NOT NULL,
    returns_1d NUMERIC(8, 6),
    returns_5d NUMERIC(8, 6),
    sma_20 NUMERIC(14, 4),
    sma_50 NUMERIC(14, 4),
    rsi_14 NUMERIC(6, 2),
    volatility_20d NUMERIC(8, 6),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_market_ticker_date UNIQUE (ticker, date)
);

CREATE INDEX IF NOT EXISTS idx_market_ticker_date ON public.market_ohlcv (ticker, date DESC);

-- ----------------------------------------------------------------------------
-- 2. NEWS & SENTIMENT TABLE (NLP Alignment Policy Enforcement)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.news_sentiment (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(10) NOT NULL,
    published_at TIMESTAMPTZ NOT NULL,
    effective_date DATE NOT NULL, -- T+1 if published >= 21:00 UTC
    headline TEXT NOT NULL,
    source VARCHAR(100),
    sentiment_score NUMERIC(5, 4) CHECK (sentiment_score BETWEEN -1 AND 1),
    sentiment_label VARCHAR(20),
    impact_score NUMERIC(4, 2),
    confidence NUMERIC(5, 4),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_news_ticker_effective ON public.news_sentiment (ticker, effective_date DESC);

-- ----------------------------------------------------------------------------
-- 3. FUNDAMENTAL RATIOS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.fundamental_ratios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(10) NOT NULL,
    quarter_end_date DATE NOT NULL,
    pe_ratio NUMERIC(10, 2),
    pb_ratio NUMERIC(10, 2),
    roe NUMERIC(8, 4),
    debt_to_equity NUMERIC(10, 4),
    fcf_margin NUMERIC(8, 4),
    revenue_growth NUMERIC(8, 4),
    eps_growth NUMERIC(8, 4),
    fundamental_score NUMERIC(4, 2) CHECK (fundamental_score BETWEEN 0 AND 10),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_fundamental_ticker_quarter UNIQUE (ticker, quarter_end_date)
);

CREATE INDEX IF NOT EXISTS idx_fundamental_ticker ON public.fundamental_ratios (ticker, quarter_end_date DESC);

-- ----------------------------------------------------------------------------
-- 4. MULTI-MODAL AI SIGNALS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.ai_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(10) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    horizon VARCHAR(10) DEFAULT '5D',
    signal VARCHAR(20) NOT NULL CHECK (signal IN ('STRONG BUY', 'BUY', 'NEUTRAL', 'SELL', 'STRONG SELL')),
    forecast_return_5d NUMERIC(8, 6) NOT NULL,
    confidence_score NUMERIC(5, 4) NOT NULL CHECK (confidence_score BETWEEN 0 AND 1),
    composite_alpha_score NUMERIC(6, 4) NOT NULL,
    market_factor_score NUMERIC(6, 4),
    news_factor_score NUMERIC(6, 4),
    fundamental_factor_score NUMERIC(6, 4),
    technical_factor_score NUMERIC(6, 4),
    macro_factor_score NUMERIC(6, 4),
    model_agreement_count INT DEFAULT 5,
    total_models INT DEFAULT 5,
    factor_breakdown JSONB,
    model_consensus JSONB,
    regime VARCHAR(30) DEFAULT 'BULLISH',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_signals_ticker_ts ON public.ai_signals (ticker, timestamp DESC);

-- ----------------------------------------------------------------------------
-- 5. MODEL REGISTRY TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.model_registry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- XGBoost, LSTM, GRU, Transformer, MultiModal
    status VARCHAR(20) DEFAULT 'ONLINE',
    val_loss NUMERIC(10, 6),
    rmse NUMERIC(10, 6),
    ic_score NUMERIC(8, 4),
    directional_accuracy NUMERIC(6, 4),
    hyperparameters JSONB,
    feature_importance JSONB,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_model_name_version UNIQUE (model_name, version)
);

-- ----------------------------------------------------------------------------
-- 6. PORTFOLIO ALLOCATIONS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.portfolio_allocations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(10) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    current_weight NUMERIC(6, 4) NOT NULL,
    target_weight NUMERIC(6, 4) NOT NULL,
    recommended_change NUMERIC(6, 4) NOT NULL,
    portfolio_action VARCHAR(20) NOT NULL CHECK (portfolio_action IN ('INCREASE', 'DECREASE', 'HOLD', 'REBALANCE')),
    portfolio_contribution NUMERIC(6, 4),
    risk_contribution NUMERIC(6, 4),
    sector VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_portfolio_allocations_ts ON public.portfolio_allocations (timestamp DESC);

-- ----------------------------------------------------------------------------
-- 7. RISK MONITOR METRICS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.risk_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    portfolio_value NUMERIC(14, 2) NOT NULL DEFAULT 1024820.00,
    volatility_ann NUMERIC(6, 4) NOT NULL,
    sharpe_ratio NUMERIC(6, 4) NOT NULL,
    var_95 NUMERIC(6, 4) NOT NULL,
    max_drawdown NUMERIC(6, 4) NOT NULL,
    beta NUMERIC(6, 4) NOT NULL,
    gross_exposure NUMERIC(6, 4) NOT NULL,
    cash_weight NUMERIC(6, 4) NOT NULL,
    risk_status VARCHAR(20) DEFAULT 'NORMAL',
    sector_exposures JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 8. BACKTEST RESULTS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.backtest_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id VARCHAR(50) NOT NULL UNIQUE,
    strategy_name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    cagr NUMERIC(6, 4) NOT NULL,
    sharpe_ratio NUMERIC(6, 4) NOT NULL,
    sortino_ratio NUMERIC(6, 4) NOT NULL,
    max_drawdown NUMERIC(6, 4) NOT NULL,
    win_rate NUMERIC(6, 4) NOT NULL,
    turnover_annualized NUMERIC(6, 4) NOT NULL,
    equity_curve JSONB NOT NULL,
    ablation_metrics JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 9. USEFUL VIEWS
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW public.v_latest_signals AS
SELECT DISTINCT ON (ticker)
    ticker,
    timestamp,
    signal,
    forecast_return_5d,
    confidence_score,
    composite_alpha_score,
    market_factor_score,
    news_factor_score,
    fundamental_factor_score,
    technical_factor_score,
    macro_factor_score,
    model_agreement_count,
    total_models,
    regime
FROM public.ai_signals
ORDER BY ticker, timestamp DESC;

CREATE OR REPLACE VIEW public.v_portfolio_summary AS
SELECT DISTINCT ON (ticker)
    ticker,
    sector,
    current_weight,
    target_weight,
    recommended_change,
    portfolio_action,
    risk_contribution,
    timestamp
FROM public.portfolio_allocations
ORDER BY ticker, timestamp DESC;

-- ----------------------------------------------------------------------------
-- 10. ROW LEVEL SECURITY (RLS)
-- ----------------------------------------------------------------------------
ALTER TABLE public.market_ohlcv ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.news_sentiment ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fundamental_ratios ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.model_registry ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.portfolio_allocations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.risk_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.backtest_results ENABLE ROW LEVEL SECURITY;

-- Public Read-Only Access Policies
CREATE POLICY "Allow public read access for market_ohlcv" ON public.market_ohlcv FOR SELECT USING (true);
CREATE POLICY "Allow public read access for news_sentiment" ON public.news_sentiment FOR SELECT USING (true);
CREATE POLICY "Allow public read access for fundamental_ratios" ON public.fundamental_ratios FOR SELECT USING (true);
CREATE POLICY "Allow public read access for ai_signals" ON public.ai_signals FOR SELECT USING (true);
CREATE POLICY "Allow public read access for model_registry" ON public.model_registry FOR SELECT USING (true);
CREATE POLICY "Allow public read access for portfolio_allocations" ON public.portfolio_allocations FOR SELECT USING (true);
CREATE POLICY "Allow public read access for risk_metrics" ON public.risk_metrics FOR SELECT USING (true);
CREATE POLICY "Allow public read access for backtest_results" ON public.backtest_results FOR SELECT USING (true);

-- Service Role Full Access Policies
CREATE POLICY "Service role full access on market_ohlcv" ON public.market_ohlcv FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access on news_sentiment" ON public.news_sentiment FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access on fundamental_ratios" ON public.fundamental_ratios FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access on ai_signals" ON public.ai_signals FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access on model_registry" ON public.model_registry FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access on portfolio_allocations" ON public.portfolio_allocations FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access on risk_metrics" ON public.risk_metrics FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access on backtest_results" ON public.backtest_results FOR ALL USING (auth.role() = 'service_role');
