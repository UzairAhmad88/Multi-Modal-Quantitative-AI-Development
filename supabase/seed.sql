-- ============================================================================
-- QUANT AI: Supabase Seed Data
-- ============================================================================

-- 1. MODEL REGISTRY SEED
INSERT INTO public.model_registry (model_name, version, model_type, status, val_loss, rmse, ic_score, directional_accuracy, hyperparameters)
VALUES 
('XGBoost Alpha Regressor', 'v2.4.1', 'XGBoost', 'ONLINE', 0.00142, 0.0182, 0.084, 0.6120, '{"n_estimators": 300, "max_depth": 6, "learning_rate": 0.03}'),
('LSTM Sequence Predictor', 'v2.4.1', 'LSTM', 'ONLINE', 0.00156, 0.0191, 0.078, 0.5980, '{"hidden_dim": 64, "num_layers": 2, "dropout": 0.2}'),
('GRU Temporal Forecaster', 'v2.4.1', 'GRU', 'ONLINE', 0.00151, 0.0188, 0.081, 0.6040, '{"hidden_dim": 64, "num_layers": 2, "dropout": 0.2}'),
('Transformer Encoder', 'v2.4.1', 'Transformer', 'ONLINE', 0.00138, 0.0179, 0.091, 0.6250, '{"d_model": 64, "nhead": 4, "num_layers": 2}'),
('MultiModalQuantNet Fusion', 'v2.4.1', 'MultiModal', 'ONLINE', 0.00121, 0.0165, 0.112, 0.6480, '{"fusion_dim": 128, "learned_fusion": true}')
ON CONFLICT (model_name, version) DO NOTHING;

-- 2. AI SIGNALS SEED
INSERT INTO public.ai_signals (ticker, timestamp, horizon, signal, forecast_return_5d, confidence_score, composite_alpha_score, market_factor_score, news_factor_score, fundamental_factor_score, technical_factor_score, macro_factor_score, model_agreement_count, total_models, regime, factor_breakdown, model_consensus)
VALUES
('AAPL', NOW(), '5D', 'BUY', 0.0284, 0.8700, 0.7600, 0.7400, 0.6800, 0.8200, 0.7100, 0.4100, 5, 5, 'BULLISH', 
 '{"momentum_5d": 0.85, "news_sentiment": 0.68, "earnings_growth": 0.82, "drawdown_risk": 0.90}',
 '{"XGBoost": {"signal": "BUY", "confidence": 0.82}, "LSTM": {"signal": "BUY", "confidence": 0.76}, "GRU": {"signal": "BUY", "confidence": 0.79}, "Transformer": {"signal": "BUY", "confidence": 0.84}, "MultiModal": {"signal": "STRONG BUY", "confidence": 0.91}}'),

('NVDA', NOW(), '5D', 'STRONG BUY', 0.0412, 0.9100, 0.8900, 0.9200, 0.7300, 0.9100, 0.8800, 0.5200, 5, 5, 'BULLISH',
 '{"momentum_5d": 0.95, "news_sentiment": 0.73, "earnings_growth": 0.91, "drawdown_risk": 0.82}',
 '{"XGBoost": {"signal": "STRONG BUY", "confidence": 0.89}, "LSTM": {"signal": "STRONG BUY", "confidence": 0.88}, "GRU": {"signal": "STRONG BUY", "confidence": 0.90}, "Transformer": {"signal": "STRONG BUY", "confidence": 0.93}, "MultiModal": {"signal": "STRONG BUY", "confidence": 0.94}}'),

('MSFT', NOW(), '5D', 'BUY', 0.0215, 0.8400, 0.7100, 0.7000, 0.6500, 0.8500, 0.6900, 0.4500, 4, 5, 'BULLISH',
 '{"momentum_5d": 0.72, "news_sentiment": 0.65, "earnings_growth": 0.85, "drawdown_risk": 0.88}',
 '{"XGBoost": {"signal": "BUY", "confidence": 0.80}, "LSTM": {"signal": "BUY", "confidence": 0.75}, "GRU": {"signal": "BUY", "confidence": 0.78}, "Transformer": {"signal": "BUY", "confidence": 0.83}, "MultiModal": {"signal": "BUY", "confidence": 0.86}}'),

('AMZN', NOW(), '5D', 'BUY', 0.0265, 0.8200, 0.6800, 0.6900, 0.6200, 0.7800, 0.6700, 0.4200, 4, 5, 'BULLISH',
 '{"momentum_5d": 0.70, "news_sentiment": 0.62, "earnings_growth": 0.78, "drawdown_risk": 0.81}',
 '{"XGBoost": {"signal": "BUY", "confidence": 0.78}, "LSTM": {"signal": "BUY", "confidence": 0.74}, "GRU": {"signal": "BUY", "confidence": 0.76}, "Transformer": {"signal": "BUY", "confidence": 0.81}, "MultiModal": {"signal": "BUY", "confidence": 0.83}}'),

('GOOGL', NOW(), '5D', 'NEUTRAL', 0.0042, 0.6500, 0.4500, 0.4800, 0.4100, 0.6800, 0.4600, 0.3800, 3, 5, 'SIDEWAYS',
 '{"momentum_5d": 0.45, "news_sentiment": 0.41, "earnings_growth": 0.68, "drawdown_risk": 0.75}',
 '{"XGBoost": {"signal": "NEUTRAL", "confidence": 0.62}, "LSTM": {"signal": "NEUTRAL", "confidence": 0.64}, "GRU": {"signal": "NEUTRAL", "confidence": 0.63}, "Transformer": {"signal": "BUY", "confidence": 0.68}, "MultiModal": {"signal": "NEUTRAL", "confidence": 0.66}}');

-- 3. PORTFOLIO ALLOCATIONS SEED
INSERT INTO public.portfolio_allocations (ticker, current_weight, target_weight, recommended_change, portfolio_action, portfolio_contribution, risk_contribution, sector)
VALUES
('AAPL', 0.1820, 0.2200, 0.0380, 'INCREASE', 0.0034, 0.0720, 'Technology'),
('NVDA', 0.1500, 0.2000, 0.0500, 'INCREASE', 0.0052, 0.0950, 'Technology'),
('MSFT', 0.1600, 0.1800, 0.0200, 'INCREASE', 0.0028, 0.0610, 'Technology'),
('AMZN', 0.1200, 0.1400, 0.0200, 'INCREASE', 0.0024, 0.0480, 'Consumer Cyclical'),
('GOOGL', 0.1000, 0.0900, -0.0100, 'DECREASE', -0.0005, 0.0350, 'Communication Services');

-- 4. RISK METRICS SEED
INSERT INTO public.risk_metrics (portfolio_value, volatility_ann, sharpe_ratio, var_95, max_drawdown, beta, gross_exposure, cash_weight, risk_status, sector_exposures)
VALUES
(1024820.00, 0.1480, 1.7200, -0.0182, -0.0841, 0.9400, 0.8300, 0.1700, 'NORMAL',
 '{"Technology": 0.42, "Financials": 0.18, "Healthcare": 0.12, "Energy": 0.10, "Consumer": 0.09, "Cash": 0.09}');

-- 5. BACKTEST RESULTS SEED
INSERT INTO public.backtest_results (run_id, strategy_name, start_date, end_date, cagr, sharpe_ratio, sortino_ratio, max_drawdown, win_rate, turnover_annualized, equity_curve, ablation_metrics)
VALUES
('BT-RUN-2026-0916', 'MULTI-MODAL AI ENSEMBLE', '2021-01-01', '2026-09-15', 0.1870, 1.6400, 2.2100, -0.1120, 0.5840, 3.2000,
 '[{"date": "2021-01-01", "strategy": 100.0, "benchmark": 100.0}, {"date": "2023-01-01", "strategy": 142.5, "benchmark": 118.2}, {"date": "2026-09-15", "strategy": 235.8, "benchmark": 164.3}]',
 '{"Full_MultiModal": {"sharpe": 1.64, "cagr": 0.187}, "No_News_NLP": {"sharpe": 1.38, "cagr": 0.152}, "No_Fundamentals": {"sharpe": 1.45, "cagr": 0.161}, "Market_Only": {"sharpe": 1.12, "cagr": 0.118}}');
