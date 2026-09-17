-- ============================================================================
-- QUANT AI: Live Trading, Broker Abstraction & Order Lineage Extension
-- Schema Version: 2.0.0
-- Created: 2026-09-18
-- ============================================================================

-- 1. BROKER ACCOUNTS TABLE
CREATE TABLE IF NOT EXISTS public.broker_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id VARCHAR(50) NOT NULL UNIQUE,
    environment VARCHAR(20) NOT NULL CHECK (environment IN ('BACKTEST', 'PAPER', 'SHADOW', 'SANDBOX', 'LIVE')),
    broker_name VARCHAR(50) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    cash NUMERIC(14, 2) NOT NULL DEFAULT 100000.00,
    equity NUMERIC(14, 2) NOT NULL DEFAULT 100000.00,
    buying_power NUMERIC(14, 2) NOT NULL DEFAULT 100000.00,
    is_active BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. ORDERS TABLE (With Idempotency & Order Lineage)
CREATE TABLE IF NOT EXISTS public.orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    internal_order_id VARCHAR(50) NOT NULL UNIQUE,
    broker_order_id VARCHAR(100),
    signal_id VARCHAR(100),
    model_id VARCHAR(50),
    model_version VARCHAR(20),
    environment VARCHAR(20) NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    side VARCHAR(10) NOT NULL CHECK (side IN ('BUY', 'SELL')),
    quantity NUMERIC(12, 4) NOT NULL,
    filled_quantity NUMERIC(12, 4) DEFAULT 0.0,
    order_type VARCHAR(20) DEFAULT 'MARKET',
    price NUMERIC(14, 4),
    avg_fill_price NUMERIC(14, 4),
    status VARCHAR(30) NOT NULL CHECK (status IN ('CREATED', 'VALIDATING', 'APPROVED', 'SUBMITTED', 'ACKNOWLEDGED', 'PARTIALLY_FILLED', 'FILLED', 'REJECTED', 'CANCELLED', 'EXPIRED', 'FAILED', 'HYPOTHETICAL_FILL')),
    idempotency_key VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_orders_ticker_status ON public.orders (ticker, status);
CREATE INDEX IF NOT EXISTS idx_orders_signal_id ON public.orders (signal_id);

-- 3. ORDER EVENTS AUDIT LOG TABLE
CREATE TABLE IF NOT EXISTS public.order_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    internal_order_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    from_state VARCHAR(30),
    to_state VARCHAR(30),
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. BROKER FILLS TABLE
CREATE TABLE IF NOT EXISTS public.fills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    fill_id VARCHAR(100) NOT NULL UNIQUE,
    internal_order_id VARCHAR(50) NOT NULL,
    broker_order_id VARCHAR(100),
    ticker VARCHAR(10) NOT NULL,
    side VARCHAR(10) NOT NULL,
    quantity NUMERIC(12, 4) NOT NULL,
    fill_price NUMERIC(14, 4) NOT NULL,
    commission NUMERIC(10, 4) DEFAULT 0.0,
    slippage_bps NUMERIC(8, 2) DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. POSITIONS TABLE
CREATE TABLE IF NOT EXISTS public.positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id VARCHAR(50) NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    quantity NUMERIC(12, 4) NOT NULL,
    avg_price NUMERIC(14, 4) NOT NULL,
    market_price NUMERIC(14, 4) NOT NULL,
    market_value NUMERIC(14, 2) NOT NULL,
    unrealized_pnl NUMERIC(14, 2) DEFAULT 0.0,
    realized_pnl NUMERIC(14, 2) DEFAULT 0.0,
    weight NUMERIC(6, 4) DEFAULT 0.0,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_account_ticker UNIQUE (account_id, ticker)
);

-- 6. TRADING SESSIONS TABLE
CREATE TABLE IF NOT EXISTS public.trading_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(100) NOT NULL UNIQUE,
    environment VARCHAR(20) NOT NULL,
    broker_name VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'RUNNING',
    initial_cash NUMERIC(14, 2) NOT NULL,
    final_cash NUMERIC(14, 2),
    final_equity NUMERIC(14, 2),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ
);

-- 7. RECONCILIATION RECORDS TABLE
CREATE TABLE IF NOT EXISTS public.reconciliation_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(100),
    is_reconciled BOOLEAN NOT NULL,
    broker_cash NUMERIC(14, 2) NOT NULL,
    local_cash NUMERIC(14, 2) NOT NULL,
    cash_diff NUMERIC(14, 2) NOT NULL,
    mismatches JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.broker_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.order_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fills ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trading_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reconciliation_records ENABLE ROW LEVEL SECURITY;

-- Read Access Policies
CREATE POLICY "Allow read access on broker_accounts" ON public.broker_accounts FOR SELECT USING (true);
CREATE POLICY "Allow read access on orders" ON public.orders FOR SELECT USING (true);
CREATE POLICY "Allow read access on order_events" ON public.order_events FOR SELECT USING (true);
CREATE POLICY "Allow read access on fills" ON public.fills FOR SELECT USING (true);
CREATE POLICY "Allow read access on positions" ON public.positions FOR SELECT USING (true);
CREATE POLICY "Allow read access on trading_sessions" ON public.trading_sessions FOR SELECT USING (true);
CREATE POLICY "Allow read access on reconciliation_records" ON public.reconciliation_records FOR SELECT USING (true);

-- Service Role Full Access Policies
CREATE POLICY "Service role access on broker_accounts" ON public.broker_accounts FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role access on orders" ON public.orders FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role access on order_events" ON public.order_events FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role access on fills" ON public.fills FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role access on positions" ON public.positions FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role access on trading_sessions" ON public.trading_sessions FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role access on reconciliation_records" ON public.reconciliation_records FOR ALL USING (auth.role() = 'service_role');
