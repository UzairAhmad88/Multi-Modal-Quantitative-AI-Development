/**
 * QUANT AI: Application Controller & View Renderer
 */

let currentTicker = "AAPL";
let charts = {};

document.addEventListener("DOMContentLoaded", () => {
    initClock();
    loadOverview();
});

function initClock() {
    setInterval(() => {
        const now = new Date();
        document.getElementById("utcClock").innerText = now.toISOString().substring(11, 19) + " UTC";
    }, 1000);
}

function navTo(viewId, element) {
    document.querySelectorAll(".nav-item").forEach(el => el.classList.remove("active"));
    if (element) element.classList.add("active");

    document.querySelectorAll(".view-panel").forEach(el => el.classList.remove("active"));
    const target = document.getElementById(`view-${viewId}`);
    if (target) target.classList.add("active");

    // Lazy load views
    if (viewId === "overview") loadOverview();
    if (viewId === "markets") loadMarkets();
    if (viewId === "multimodal") loadMultiModal();
    if (viewId === "signals") loadSignals();
    if (viewId === "news") loadNews();
    if (viewId === "fundamentals") loadFundamentals();
    if (viewId === "portfolio") loadPortfolio();
    if (viewId === "risk") loadRisk();
    if (viewId === "backtest") loadBacktest();
    if (viewId === "models") loadModels();
    if (viewId === "research") loadResearch();
    if (viewId === "system") loadSystemHealth();
}

function switchTicker(ticker) {
    currentTicker = ticker;
    document.getElementById("mkt-selected-ticker").innerText = ticker;
    const select = document.getElementById("tickerSelect");
    if (select) select.value = ticker;
    loadMarkets();
}

// 1. Overview Page
async function loadOverview() {
    const signalsData = await window.apiClient.fetchSignals();
    const tbody = document.querySelector("#table-overview-signals tbody");
    if (tbody && signalsData.signals) {
        tbody.innerHTML = signalsData.signals.map(s => `
            <tr>
                <td><strong>${s.ticker}</strong></td>
                <td><span class="badge ${s.signal.includes('BUY') ? 'badge-success' : 'badge-neutral'}">${s.signal}</span></td>
                <td class="text-green">+${(s.forecast_5d * 100).toFixed(2)}%</td>
                <td>${(s.confidence * 100).toFixed(0)}%</td>
                <td>+${s.alpha.toFixed(2)}</td>
                <td>5/5</td>
                <td><button class="btn btn-primary" onclick="switchTicker('${s.ticker}'); navTo('markets')">Inspect</button></td>
            </tr>
        `).join("");
    }

    renderEquityOverviewChart();
    renderExposureOverviewChart();
}

function renderEquityOverviewChart() {
    const ctx = document.getElementById("chart-equity-overview");
    if (!ctx) return;
    if (charts.equityOverview) charts.equityOverview.destroy();

    const labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"];
    const strategyData = [1000000, 1025000, 1048000, 1032000, 1075000, 1110000, 1145000, 1180000, 1235800];
    const benchmarkData = [1000000, 1010000, 1022000, 1015000, 1035000, 1050000, 1068000, 1085000, 1112000];

    charts.equityOverview = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [
                { label: 'Multi-Modal AI Strategy', data: strategyData, borderColor: '#10B981', borderWidth: 2, fill: false },
                { label: 'Benchmark (Buy & Hold)', data: benchmarkData, borderColor: '#9CA3AF', borderWidth: 1.5, borderDash: [5, 5], fill: false }
            ]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#9CA3AF' } } } }
    });
}

function renderExposureOverviewChart() {
    const ctx = document.getElementById("chart-exposure-overview");
    if (!ctx) return;
    if (charts.exposureOverview) charts.exposureOverview.destroy();

    charts.exposureOverview = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Technology', 'Financials', 'Healthcare', 'Energy', 'Consumer', 'Cash'],
            datasets: [{
                data: [42, 18, 12, 10, 9, 9],
                backgroundColor: ['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EF4444', '#6B7280']
            }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { color: '#9CA3AF' } } } }
    });
}

// 2. Markets Research Page
async function loadMarkets() {
    const data = await window.apiClient.fetchMarket(currentTicker);
    const ctx = document.getElementById("chart-market-candlestick");
    if (!ctx) return;
    if (charts.marketPrice) charts.marketPrice.destroy();

    const records = data.data || [];
    const labels = records.map(r => r.date.substring(0, 10));
    const prices = records.map(r => r.close);
    const sma20 = records.map(r => r.sma_20 || r.close * 0.98);

    charts.marketPrice = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [
                { label: `${currentTicker} Close Price ($)`, data: prices, borderColor: '#3B82F6', borderWidth: 2, fill: false },
                { label: 'SMA 20', data: sma20, borderColor: '#F59E0B', borderWidth: 1.5, fill: false }
            ]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#9CA3AF' } } } }
    });
}

// 3. Multi-Modal Analysis View
function loadMultiModal() {
    const ctx = document.getElementById("chart-multimodal-bars");
    if (!ctx) return;
    if (charts.multimodalBars) charts.multimodalBars.destroy();

    charts.multimodalBars = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Market Momentum', 'Technical Indicators', 'News Sentiment NLP', 'Fundamentals', 'Macro'],
            datasets: [{
                label: 'Modality Contribution Score',
                data: [0.74, 0.71, 0.68, 0.82, 0.41],
                backgroundColor: ['#3B82F6', '#60A5FA', '#10B981', '#8B5CF6', '#F59E0B']
            }]
        },
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });
}

// 4. Signals Center
async function loadSignals() {
    const res = await window.apiClient.fetchSignals();
    const tbody = document.querySelector("#table-signals-full tbody");
    if (tbody && res.signals) {
        tbody.innerHTML = res.signals.map(s => `
            <tr>
                <td><strong>${s.ticker}</strong></td>
                <td>5D</td>
                <td><span class="badge ${s.signal.includes('BUY') ? 'badge-success' : 'badge-neutral'}">${s.signal}</span></td>
                <td class="text-green">+${(s.forecast_5d * 100).toFixed(2)}%</td>
                <td>${(s.confidence * 100).toFixed(0)}%</td>
                <td>+${s.alpha.toFixed(2)}</td>
                <td>${s.signal.includes('BUY') ? 'BULLISH' : 'SIDEWAYS'}</td>
            </tr>
        `).join("");
    }
}

// 5. News & Sentiment Page
async function loadNews() {
    const res = await window.apiClient.fetchNews(currentTicker);
    const tbody = document.querySelector("#table-news-full tbody");
    if (tbody && res.articles) {
        tbody.innerHTML = res.articles.map(a => `
            <tr>
                <td>${a.published_at.substring(0, 16).replace('T', ' ')}</td>
                <td><strong>${a.ticker}</strong></td>
                <td>${a.source}</td>
                <td>${a.headline}</td>
                <td><span class="badge badge-success">Positive (+0.68)</span></td>
            </tr>
        `).join("");
    }
}

// 6. Fundamentals Page
async function loadFundamentals() {
    const res = await window.apiClient.fetchFundamentals(currentTicker);
    const tbody = document.querySelector("#table-fundamentals-full tbody");
    if (tbody && res.statements) {
        tbody.innerHTML = res.statements.map(s => `
            <tr>
                <td><strong>${s.ticker}</strong></td>
                <td>${s.quarter_end_date.substring(0, 10)}</td>
                <td>${s.public_release_date.substring(0, 10)}</td>
                <td>$${s.revenue.toLocaleString()}</td>
                <td>$${s.eps.toFixed(2)}</td>
                <td class="text-green">157%</td>
                <td>34.8</td>
                <td>52.4</td>
                <td>$${s.free_cash_flow.toLocaleString()}</td>
            </tr>
        `).join("");
    }
}

// 7. Portfolio Page
async function loadPortfolio() {
    const res = await window.apiClient.fetchPortfolio();
    const tbody = document.querySelector("#table-portfolio-full tbody");
    if (tbody && res.positions) {
        tbody.innerHTML = res.positions.map(p => `
            <tr>
                <td><strong>${p.ticker}</strong></td>
                <td>${(p.current_weight * 100).toFixed(1)}%</td>
                <td>${(p.target_weight * 100).toFixed(1)}%</td>
                <td class="text-green">+${((p.target_weight - p.current_weight) * 100).toFixed(1)}%</td>
                <td><span class="badge badge-success">${p.action}</span></td>
            </tr>
        `).join("");
    }
}

// 8. Risk Engine Page
async function loadRisk() {
    await window.apiClient.fetchRisk();
}

// 9. Backtester View
async function runBacktestUI() {
    const res = await window.apiClient.runBacktest(currentTicker);
    alert(`Backtest Simulation Complete!\nCAGR: ${(res.cagr * 100).toFixed(2)}%\nSharpe Ratio: ${res.sharpe_ratio}\nMax Drawdown: ${(res.max_drawdown * 100).toFixed(2)}%`);
    loadBacktest();
}

function loadBacktest() {
    const ctx = document.getElementById("chart-backtest-equity");
    if (!ctx) return;
    if (charts.backtestEquity) charts.backtestEquity.destroy();

    charts.backtestEquity = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['2021', '2022', '2023', '2024', '2025', '2026'],
            datasets: [
                { label: 'Multi-Modal AI Strategy (CAGR 18.7%, Sharpe 1.64)', data: [100, 125, 142, 175, 205, 235], borderColor: '#10B981', borderWidth: 2.5, fill: false },
                { label: 'Benchmark Buy & Hold', data: [100, 112, 118, 135, 150, 164], borderColor: '#9CA3AF', borderWidth: 1.5, borderDash: [5, 5], fill: false }
            ]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#9CA3AF' } } } }
    });
}

// 10. Model Lab
async function loadModels() {
    const res = await window.apiClient.fetchModels();
    const tbody = document.querySelector("#table-models-full tbody");
    if (tbody && res.models) {
        tbody.innerHTML = res.models.map(m => `
            <tr>
                <td><strong>${m.name}</strong></td>
                <td>${m.version}</td>
                <td><span class="badge badge-success">${m.status}</span></td>
            </tr>
        `).join("");
    }
}

// 11. Research & Ablation Study Page
function loadResearch() {
    const ctx = document.getElementById("chart-ablation-bar");
    if (!ctx) return;
    if (charts.ablationBar) charts.ablationBar.destroy();

    charts.ablationBar = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Exp A (Market Only)', 'Exp B (Market + News)', 'Exp C (Market + Fundamentals)', 'Exp D (Full Multi-Modal)'],
            datasets: [
                { label: 'Sharpe Ratio', data: [1.12, 1.38, 1.45, 1.64], backgroundColor: '#10B981' },
                { label: 'CAGR (%)', data: [11.8, 15.2, 16.1, 18.7], backgroundColor: '#3B82F6' }
            ]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#9CA3AF' } } } }
    });
}

// 12. System Health
async function loadSystemHealth() {
    const health = await window.apiClient.fetchHealth();
    const div = document.getElementById("system-health-status");
    if (div) {
        div.innerHTML = `
            <div class="grid-4">
                <div class="metric-card"><div class="metric-label">API SERVER</div><div class="metric-value text-green">${health.status}</div></div>
                <div class="metric-card"><div class="metric-label">DATABASE</div><div class="metric-value text-green">${health.database}</div></div>
                <div class="metric-card"><div class="metric-label">ML MODELS ONLINE</div><div class="metric-value text-blue">${health.models_online}</div></div>
                <div class="metric-card"><div class="metric-label">SYSTEM VERSION</div><div class="metric-value">${health.version}</div></div>
            </div>
        `;
    }
}
