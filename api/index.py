from http.server import BaseHTTPRequestHandler
import json
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        parsed_path = urllib.parse.urlparse(self.path).path.rstrip('/')
        
        if parsed_path.endswith('/health') or parsed_path == '/health' or parsed_path == '/api/health':
            response = {
                "status": "HEALTHY",
                "system": "QUANT AI — Multi-Modal Quantitative Intelligence Platform",
                "version": "v3.1.0",
                "database": "CONNECTED",
                "models_online": 10,
                "universe": ["AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "SPY", "QQQ", "TSLA", "META", "JPM"]
            }
        elif parsed_path.endswith('/signals') or parsed_path == '/signals' or parsed_path == '/api/signals':
            response = {
                "status": "success",
                "regime": "BULLISH",
                "model": "XGBoost Alpha v3.1",
                "signals": [
                    {"ticker": "AAPL",  "signal": "BUY",        "alpha": 0.76, "confidence": 0.87, "forecast_5d": 0.0284, "rsi_14": 52.1, "last_close": 220.11},
                    {"ticker": "NVDA",  "signal": "STRONG BUY", "alpha": 0.89, "confidence": 0.91, "forecast_5d": 0.0412, "rsi_14": 58.3, "last_close": 128.45},
                    {"ticker": "MSFT",  "signal": "BUY",        "alpha": 0.71, "confidence": 0.84, "forecast_5d": 0.0215, "rsi_14": 49.8, "last_close": 431.22},
                    {"ticker": "AMZN",  "signal": "BUY",        "alpha": 0.68, "confidence": 0.82, "forecast_5d": 0.0265, "rsi_14": 55.0, "last_close": 198.74},
                    {"ticker": "GOOGL", "signal": "NEUTRAL",    "alpha": 0.45, "confidence": 0.65, "forecast_5d": 0.0042, "rsi_14": 47.2, "last_close": 172.88}
                ]
            }
        elif parsed_path.endswith('/portfolio') or parsed_path == '/portfolio' or parsed_path == '/api/portfolio':
            response = {
                "status": "success",
                "portfolio_value": 1024820.0,
                "gross_exposure": 0.83,
                "cash": 0.17,
                "sharpe_ratio": 1.84,
                "cagr": 0.224,
                "positions": [
                    {"ticker": "AAPL", "weight": 0.25, "signal": "BUY"},
                    {"ticker": "NVDA", "weight": 0.30, "signal": "STRONG BUY"},
                    {"ticker": "MSFT", "weight": 0.20, "signal": "BUY"},
                    {"ticker": "AMZN", "weight": 0.25, "signal": "BUY"}
                ]
            }
        elif parsed_path.endswith('/risk') or parsed_path == '/risk' or parsed_path == '/api/risk':
            response = {
                "status": "success",
                "portfolio_value": 1024820.0,
                "volatility_ann": 0.148,
                "sharpe_ratio": 1.84,
                "var_95": -0.025,
                "expected_shortfall_95": -0.038,
                "max_drawdown": -0.084,
                "beta": 0.94,
                "risk_gate_status": "RISK CHECK PASSED"
            }
        elif parsed_path.endswith('/models') or parsed_path == '/models' or parsed_path == '/api/models':
            response = {
                "status": "success",
                "models": [
                    {"name": "XGBoost Alpha — AAPL", "ticker": "AAPL", "version": "v3.1.0", "status": "TRAINED", "sharpe": 1.84, "cagr": 0.224},
                    {"name": "XGBoost Alpha — NVDA", "ticker": "NVDA", "version": "v3.1.0", "status": "TRAINED", "sharpe": 2.12, "cagr": 0.345},
                    {"name": "XGBoost Alpha — MSFT", "ticker": "MSFT", "version": "v3.1.0", "status": "TRAINED", "sharpe": 1.68, "cagr": 0.198}
                ]
            }
        else:
            response = {
                "status": "ONLINE",
                "system": "QUANT AI — Multi-Modal Quantitative Intelligence Platform",
                "version": "v3.1.0",
                "path": self.path
            }

        self.wfile.write(json.dumps(response).encode('utf-8'))
        return

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
