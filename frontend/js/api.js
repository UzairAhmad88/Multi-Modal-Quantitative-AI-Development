/**
 * QUANT AI: Typed REST API Client Interface
 * Communicates directly with FastAPI Backend (http://127.0.0.1:8000)
 */

const API_BASE = "http://127.0.0.1:8000";

class QuantAPIClient {
    async fetchHealth() {
        try {
            const res = await fetch(`${API_BASE}/health`);
            return await res.json();
        } catch (e) {
            return { status: "OFFLINE", error: e.message };
        }
    }

    async fetchMarket(ticker = "AAPL") {
        try {
            const res = await fetch(`${API_BASE}/market/${ticker}`);
            return await res.json();
        } catch (e) {
            return { status: "error", message: e.message, data: [] };
        }
    }

    async fetchNews(ticker = "AAPL") {
        try {
            const res = await fetch(`${API_BASE}/news/${ticker}`);
            return await res.json();
        } catch (e) {
            return { status: "error", articles: [] };
        }
    }

    async fetchFundamentals(ticker = "AAPL") {
        try {
            const res = await fetch(`${API_BASE}/fundamentals/${ticker}`);
            return await res.json();
        } catch (e) {
            return { status: "error", statements: [] };
        }
    }

    async fetchSignals() {
        try {
            const res = await fetch(`${API_BASE}/signals`);
            return await res.json();
        } catch (e) {
            return { status: "error", signals: [] };
        }
    }

    async fetchPortfolio() {
        try {
            const res = await fetch(`${API_BASE}/portfolio`);
            return await res.json();
        } catch (e) {
            return { status: "error", positions: [] };
        }
    }

    async fetchRisk() {
        try {
            const res = await fetch(`${API_BASE}/risk`);
            return await res.json();
        } catch (e) {
            return { status: "error" };
        }
    }

    async fetchModels() {
        try {
            const res = await fetch(`${API_BASE}/models`);
            return await res.json();
        } catch (e) {
            return { status: "error", models: [] };
        }
    }

    async runBacktest(ticker = "AAPL", capital = 100000.0) {
        try {
            const res = await fetch(`${API_BASE}/backtest`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ticker, initial_capital: capital })
            });
            return await res.json();
        } catch (e) {
            return { status: "error", message: e.message };
        }
    }
}

window.apiClient = new QuantAPIClient();
