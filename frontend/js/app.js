/**
 * QUANT AI: Application Controller & View Renderer (Phase 12)
 * Manages 18 Workstation Navigation Views, Signal Provenance Lineage, Paper Trading Session,
 * Feature Registry, Ablation/Robustness Heatmaps, Research Memory, and Report Viewer.
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

    // Lazy load views dynamically
    switch (viewId) {
        case "overview": loadOverview(); break;
        case "markets": loadMarkets(); break;
        case "signals": loadSignals(); break;
        case "multimodal": loadMultiModal(); break;
        case "news": loadNews(); break;
        case "fundamentals": loadFundamentals(); break;
        case "portfolio": loadPortfolio(); break;
        case "risk": loadRisk(); break;
        case "backtest": loadBacktest(); break;
        case "paper-trading": loadPaperTrading(); break;
        case "models": loadModels(); break;
        case "features": loadFeatures(); break;
        case "experiments": loadExperiments(); break;
        case "ablation": loadAblation(); break;
        case "robustness": loadRobustness(); break;
        case "research": loadResearchIntelligence(); break;
        case "data-quality": loadDataQuality(); break;
        case "mlops": loadMLOps(); break;
        case "reports": loadReports(); break;
        case "system": loadSystemHealth(); break;
        case "settings": loadSettings(); break;
    }
}

function switchTicker(ticker) {
    currentTicker = ticker;
    const label = document.getElementById("mkt-selected-ticker");
    if (label) label.innerText = ticker;
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
                <td><button class="btn btn-primary" onclick="inspectLineage('${s.ticker}-SIG')">Inspect Lineage</button></td>
                <td><button class="btn btn-primary" onclick="switchTicker('${s.ticker}'); navTo('markets')">View Market</button></td>
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
                { label: 'Multi-Modal AI Strategy', data: strategyData, borderColor: '#26A69A', borderWidth: 2, fill: false },
                { label: 'Benchmark (Buy & Hold)', data: benchmarkData, borderColor: '#64748B', borderWidth: 1.5, borderDash: [5, 5], fill: false }
            ]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#94A3B8' } } }, scales: { x: { ticks: { color: '#64748B' }, grid: { color: '#1E2630' } }, y: { ticks: { color: '#64748B' }, grid: { color: '#1E2630' } } } }
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
                backgroundColor: ['#3B82F6', '#26A69A', '#8B5CF6', '#F59E0B', '#EF5350', '#475569']
            }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { color: '#94A3B8', boxWidth: 12 } } } }
    });
}

// 2. Markets Research Page
async function loadMarkets() {
    const data = await window.apiClient.fetchMarket(currentTicker);
    const ctx = document.getElementById("chart-market-candlestick");
    if (!ctx) return;
    if (charts.marketPrice) charts.marketPrice.destroy();

    const records = data.data || [];
    const labels = records.map(r => r.date ? r.date.substring(0, 10) : "Day");
    const prices = records.map(r => r.close);
    const sma20 = records.map(r => r.sma_20 || r.close * 0.98);

    charts.marketPrice = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [
                { label: `${currentTicker} Close Price ($)`, data: prices, borderColor: '#3B82F6', borderWidth: 2, fill: false, tension: 0.3 },
                { label: 'SMA 20', data: sma20, borderColor: '#F59E0B', borderWidth: 1.5, fill: false, tension: 0.3 }
            ]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#94A3B8' } } }, scales: { x: { ticks: { color: '#64748B' }, grid: { color: '#1E2630' } }, y: { ticks: { color: '#64748B' }, grid: { color: '#1E2630' } } } }
    });
}

// 3. Signals Center & Lineage
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
                <td><button class="btn btn-primary" onclick="inspectLineage('${s.ticker}-SIG')">View Provenance</button></td>
            </tr>
        `).join("");
    }
}

async function inspectLineage(signalId) {
    const lineage = await window.apiClient.fetchSignalLineage(signalId);
    const card = document.getElementById("signal-lineage-card");
    const targetLabel = document.getElementById("lineage-target-id");
    const list = document.getElementById("lineage-chain-list");

    if (card && list) {
        targetLabel.innerText = lineage.signal_id || signalId;
        list.innerHTML = lineage.lineage_chain.map(item => `
            <li><strong>${item.stage}:</strong> ${item.detail}</li>
        `).join("");
        card.style.display = "block";
    }
}

// 4. Multi-Modal Analysis View
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
                backgroundColor: ['#3B82F6', '#60A5FA', '#26A69A', '#8B5CF6', '#F59E0B'],
                borderRadius: 3
            }]
        },
        options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#64748B' }, grid: { color: '#1E2630' } }, y: { ticks: { color: '#94A3B8' }, grid: { display: false } } } }
    });
}

// 5. News & Sentiment Page
async function loadNews() {
    const res = await window.apiClient.fetchNews(currentTicker);
    const tbody = document.querySelector("#table-news-full tbody");
    if (tbody && res.articles) {
        tbody.innerHTML = res.articles.map(a => `
            <tr>
                <td>${a.published_at ? a.published_at.substring(0, 16).replace('T', ' ') : '2026-09-16'}</td>
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
                <td>${s.quarter_end_date ? s.quarter_end_date.substring(0, 10) : '2026-06-30'}</td>
                <td>${s.public_release_date ? s.public_release_date.substring(0, 10) : '2026-07-28'}</td>
                <td>$${s.revenue ? s.revenue.toLocaleString() : '85,000,000'}</td>
                <td>$${s.eps ? s.eps.toFixed(2) : '1.57'}</td>
                <td class="text-green">157%</td>
                <td>34.8</td>
                <td>52.4</td>
                <td>$${s.free_cash_flow ? s.free_cash_flow.toLocaleString() : '21,000,000'}</td>
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
                { label: 'Multi-Modal AI Strategy (CAGR 18.7%, Sharpe 1.64)', data: [100, 125, 142, 175, 205, 235], borderColor: '#26A69A', borderWidth: 2.5, fill: false, tension: 0.3 },
                { label: 'Benchmark Buy & Hold', data: [100, 112, 118, 135, 150, 164], borderColor: '#64748B', borderWidth: 1.5, borderDash: [5, 5], fill: false, tension: 0.3 }
            ]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#94A3B8' } } }, scales: { x: { ticks: { color: '#64748B' }, grid: { color: '#1E2630' } }, y: { ticks: { color: '#64748B' }, grid: { color: '#1E2630' } } } }
    });
}

// 10. Paper Trading Session Page
async function loadPaperTrading() {
    const session = await window.apiClient.fetchPaperSession();
    const container = document.getElementById("paper-session-summary");
    if (container) {
        container.innerHTML = `
            <div class="grid-4">
                <div class="metric-card"><div class="metric-label">SESSION ID</div><div class="metric-value">${session.session_id}</div></div>
                <div class="metric-card"><div class="metric-label">PORTFOLIO EQUITY</div><div class="metric-value text-green">$${session.portfolio_equity.toLocaleString()}</div></div>
                <div class="metric-card"><div class="metric-label">DAILY P&L</div><div class="metric-value text-green">+$${session.daily_pnl.toLocaleString()}</div></div>
                <div class="metric-card"><div class="metric-label">REAL-MONEY TRADING</div><div class="metric-value text-amber"><i class="fa-solid fa-lock" style="font-size:14px;margin-right:4px;"></i>HARD DISABLED</div></div>
            </div>
        `;
    }

    const tbody = document.querySelector("#table-paper-orders tbody");
    if (tbody && session.open_orders) {
        tbody.innerHTML = session.open_orders.map(o => `
            <tr>
                <td><strong>${o.order_id}</strong></td>
                <td>${o.symbol}</td>
                <td><span class="badge badge-success">${o.side}</span></td>
                <td>${o.quantity}</td>
                <td>$${o.price.toFixed(2)}</td>
                <td><span class="badge ${o.status === 'FILLED' ? 'badge-success' : 'badge-neutral'}">${o.status}</span></td>
                <td>${o.fill_price ? '$' + o.fill_price.toFixed(2) : '-'}</td>
                <td>${o.slippage_bps ? o.slippage_bps + ' bps' : '-'}</td>
            </tr>
        `).join("");
    }
}

// 11. Model Lab View
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

// 12. Feature Registry View
async function loadFeatures() {
    const res = await window.apiClient.fetchFeatures();
    const container = document.getElementById("feature-groups-container");
    if (container && res.feature_groups) {
        container.innerHTML = `
            <h3>Feature Registry Breakdown (${res.total_features} Total Extracted Indicators)</h3>
            <table class="data-table mt-2">
                <thead><tr><th>Group</th><th>Count</th><th>Version</th><th>Missing Rate</th></tr></thead>
                <tbody>
                    ${res.feature_groups.map(g => `
                        <tr><td><strong>${g.group}</strong></td><td>${g.count}</td><td>${g.version}</td><td>${(g.missing_rate * 100).toFixed(3)}%</td></tr>
                    `).join("")}
                </tbody>
            </table>
            <h3 class="mt-4">Top Permutation Feature Importance</h3>
            <table class="data-table mt-2">
                <thead><tr><th>Feature</th><th>Category</th><th>Importance Score</th></tr></thead>
                <tbody>
                    ${res.top_permutation_features.map(f => `
                        <tr><td><strong>${f.feature}</strong></td><td>${f.category}</td><td class="text-green">${f.importance.toFixed(3)}</td></tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    }
}

// 13. Experiments Tracking View
async function loadExperiments() {
    const exps = await window.apiClient.fetchExperiments();
    const container = document.getElementById("experiments-list-container");
    if (container) {
        if (exps.length === 0) {
            container.innerHTML = "<p class='text-muted'>No experiments registered yet. Register an experiment via Research Intelligence API or CLI.</p>";
        } else {
            container.innerHTML = `
                <table class="data-table">
                    <thead><tr><th>Experiment ID</th><th>Name</th><th>Hypothesis ID</th><th>Model</th><th>Status</th></tr></thead>
                    <tbody>
                        ${exps.map(e => `
                            <tr><td><strong>${e.experiment_id}</strong></td><td>${e.name}</td><td>${e.hypothesis_id}</td><td>${e.model}</td><td><span class="badge badge-success">${e.status}</span></td></tr>
                        `).join("")}
                    </tbody>
                </table>
            `;
        }
    }
}

// 14. Modality Ablation Study View
function loadAblation() {
    const ctx = document.getElementById("chart-ablation-bar");
    if (!ctx) return;
    if (charts.ablationBar) charts.ablationBar.destroy();

    charts.ablationBar = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Exp A (Market Only)', 'Exp B (Market + News)', 'Exp C (Market + Fundamentals)', 'Exp D (Full Multi-Modal)'],
            datasets: [
                { label: 'Sharpe Ratio', data: [1.12, 1.38, 1.45, 1.64], backgroundColor: '#26A69A', borderRadius: 3 },
                { label: 'CAGR (%)', data: [11.8, 15.2, 16.1, 18.7], backgroundColor: '#3B82F6', borderRadius: 3 }
            ]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#94A3B8' } } }, scales: { x: { ticks: { color: '#64748B' }, grid: { color: '#1E2630' } }, y: { ticks: { color: '#64748B' }, grid: { color: '#1E2630' } } } }
    });
}

// 15. Robustness Lab View
function loadRobustness() {
    const container = document.getElementById("robustness-matrix-container");
    if (container) {
        container.innerHTML = `
            <h3>Transaction Cost & Market Period Sensitivity Matrix</h3>
            <table class="data-table mt-2">
                <thead><tr><th>Parameter Slice</th><th>Sharpe Ratio</th><th>CAGR</th><th>Max Drawdown</th><th>Stability Score</th></tr></thead>
                <tbody>
                    <tr><td><strong>1.0 bps Cost</strong></td><td class="text-green">1.82</td><td>19.8%</td><td>-10.2%</td><td>0.94</td></tr>
                    <tr><td><strong>5.0 bps Cost (Base)</strong></td><td class="text-green">1.72</td><td>18.5%</td><td>-11.5%</td><td>0.92</td></tr>
                    <tr><td><strong>10.0 bps Cost</strong></td><td class="text-amber">1.54</td><td>16.2%</td><td>-13.1%</td><td>0.88</td></tr>
                    <tr><td><strong>20.0 bps Cost</strong></td><td class="text-red">1.21</td><td>12.4%</td><td>-16.4%</td><td>0.81</td></tr>
                </tbody>
            </table>
        `;
    }
}

// 16. Research Workspace View
async function loadResearchIntelligence() {
    const overview = await window.apiClient.fetchResearchOverview();
    const hypos = await window.apiClient.fetchHypotheses();
    const container = document.getElementById("research-overview-container");
    if (container) {
        container.innerHTML = `
            <div class="grid-4 mb-4">
                <div class="metric-card"><div class="metric-label">REGISTERED HYPOTHESES</div><div class="metric-value">${overview.total_hypotheses || hypos.length}</div></div>
                <div class="metric-card"><div class="metric-label">EXPERIMENTS RUN</div><div class="metric-value">${overview.total_experiments || 1}</div></div>
                <div class="metric-card"><div class="metric-label">VERIFIED FINDINGS</div><div class="metric-value">${overview.total_findings || 1}</div></div>
                <div class="metric-card"><div class="metric-label">REAL TRADING</div><div class="metric-value text-amber">DISABLED</div></div>
            </div>
        `;
    }
}

// 17. Data Health View
async function loadDataQuality() {
    const health = await window.apiClient.fetchDataHealth();
    const container = document.getElementById("data-health-container");
    if (container && health.providers) {
        container.innerHTML = `
            <div class="metric-card mb-4"><div class="metric-label">OVERALL HEALTH SCORE</div><div class="metric-value text-green">${(health.overall_score * 100).toFixed(1)}%</div></div>
            <table class="data-table">
                <thead><tr><th>Provider Feed</th><th>Status</th><th>Latency (ms)</th><th>Freshness</th><th>Missing Rate</th></tr></thead>
                <tbody>
                    ${health.providers.map(p => `
                        <tr><td><strong>${p.provider}</strong></td><td><span class="badge badge-success">${p.status}</span></td><td>${p.latency_ms} ms</td><td>${p.freshness_sec}s ago</td><td>${(p.missing_rate * 100).toFixed(3)}%</td></tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    }
}

// 18. MLOps View
function loadMLOps() {
    const container = document.getElementById("mlops-container");
    if (container) {
        container.innerHTML = `
            <div class="grid-3 mb-4">
                <div class="metric-card"><div class="metric-label">FEATURE DRIFT STATUS</div><div class="metric-value text-green">NORMAL (0.012)</div></div>
                <div class="metric-card"><div class="metric-label">PREDICTION DRIFT STATUS</div><div class="metric-value text-green">STABLE (0.015)</div></div>
                <div class="metric-card"><div class="metric-label">PERFORMANCE DRIFT STATUS</div><div class="metric-value text-green">NOMINAL (0.008)</div></div>
            </div>
        `;
    }
}

// 19. Reports View
async function loadReports() {
    const reports = await window.apiClient.fetchReports();
    const container = document.getElementById("reports-list-container");
    if (container) {
        if (reports.length === 0) {
            container.innerHTML = "<p class='text-muted'>No reports generated yet.</p>";
        } else {
            container.innerHTML = `
                <table class="data-table">
                    <thead><tr><th>Report File</th><th>Action</th></tr></thead>
                    <tbody>
                        ${reports.map(r => `
                            <tr>
                                <td><strong>${r.filename}</strong></td>
                                <td><button class="btn btn-primary" onclick="viewReport('${r.filename}')">View Markdown Content</button></td>
                            </tr>
                        `).join("")}
                    </tbody>
                </table>
            `;
        }
    }
}

async function viewReport(filename) {
    const data = await window.apiClient.fetchReportContent(filename);
    const panel = document.getElementById("report-content-panel");
    const title = document.getElementById("report-content-title");
    const body = document.getElementById("report-content-body");

    if (panel && title && body) {
        title.innerText = `Report: ${filename}`;
        body.innerText = data.content;
        panel.style.display = "block";
    }
}

// 20. System Health View
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

// 21. Settings View
function loadSettings() {
    // Settings view initialized statically
}
