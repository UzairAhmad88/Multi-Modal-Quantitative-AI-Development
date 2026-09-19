/**
 * QUANT AI: Typed REST API Client Interface
 * Communicates directly with FastAPI Backend
 */

const API_BASE = (typeof window !== "undefined" && (window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost"))
    ? "http://127.0.0.1:8000"
    : "";

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

    async fetchSignalLineage(signalId = "SIG-001") {
        try {
            const res = await fetch(`${API_BASE}/research/signals/${signalId}/lineage`);
            return await res.json();
        } catch (e) {
            return { signal_id: signalId, lineage_chain: [] };
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

    async fetchFeatures() {
        try {
            const res = await fetch(`${API_BASE}/research/features`);
            return await res.json();
        } catch (e) {
            return { status: "error", feature_groups: [], top_permutation_features: [] };
        }
    }

    async fetchPaperSession() {
        try {
            const res = await fetch(`${API_BASE}/research/paper-trading/session`);
            return await res.json();
        } catch (e) {
            return { session_id: "PAPER-SESS", status: "OFFLINE", open_orders: [], recent_fills: [] };
        }
    }

    async fetchDataHealth() {
        try {
            const res = await fetch(`${API_BASE}/research/data/health`);
            return await res.json();
        } catch (e) {
            return { status: "OFFLINE", providers: [] };
        }
    }

    async fetchReports() {
        try {
            const res = await fetch(`${API_BASE}/research/reports`);
            return await res.json();
        } catch (e) {
            return [];
        }
    }

    async fetchReportContent(filename) {
        try {
            const res = await fetch(`${API_BASE}/research/reports/${filename}`);
            return await res.json();
        } catch (e) {
            return { filename, content: "Error loading report content." };
        }
    }

    async fetchResearchOverview() {
        try {
            const res = await fetch(`${API_BASE}/research/overview`);
            return await res.json();
        } catch (e) {
            return { status: "error" };
        }
    }

    async fetchHypotheses() {
        try {
            const res = await fetch(`${API_BASE}/research/hypotheses`);
            return await res.json();
        } catch (e) {
            return [];
        }
    }

    async fetchExperiments() {
        try {
            const res = await fetch(`${API_BASE}/research/experiments`);
            return await res.json();
        } catch (e) {
            return [];
        }
    }

    async fetchFindings() {
        try {
            const res = await fetch(`${API_BASE}/research/findings`);
            return await res.json();
        } catch (e) {
            return [];
        }
    }

    async fetchResearchGraph() {
        try {
            const res = await fetch(`${API_BASE}/research/graph`);
            return await res.json();
        } catch (e) {
            return { nodes: [], edges: [] };
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
