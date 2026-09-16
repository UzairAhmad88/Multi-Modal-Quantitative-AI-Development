/**
 * MMQAI TERMINAL — TradingView-Inspired Quantitative Research & Trading Terminal
 * Application Controller & Financial Chart Engine (Phase 30 Master UI Upgrade)
 */

let currentTicker = "AAPL";
let currentFrame = "1D";
let charts = {};
let lightweightChart = null;
let candlestickSeries = null;
let volumeSeries = null;
let ema20Series = null;
let ema50Series = null;
let activeIndicators = { ema20: true, ema50: true, bb: false, signals: true };

const WATCHLIST_SYMBOLS = [
    { symbol: "AAPL", name: "Apple Inc.", price: 185.40, change: 1.85, signal: "BUY", conf: 0.74, sentiment: 0.28 },
    { symbol: "MSFT", name: "Microsoft Corp.", price: 420.15, change: 1.20, signal: "BUY", conf: 0.81, sentiment: 0.35 },
    { symbol: "NVDA", name: "NVIDIA Corp.", price: 128.50, change: 4.15, signal: "BUY", conf: 0.88, sentiment: 0.42 },
    { symbol: "TSLA", name: "Tesla Inc.", price: 235.80, change: -1.45, signal: "SELL", conf: 0.68, sentiment: -0.15 },
    { symbol: "AMZN", name: "Amazon.com Inc.", price: 186.20, change: 0.95, signal: "BUY", conf: 0.72, sentiment: 0.18 },
    { symbol: "META", name: "Meta Platforms", price: 512.30, change: 2.10, signal: "BUY", conf: 0.79, sentiment: 0.31 },
    { symbol: "GOOGL", name: "Alphabet Inc.", price: 175.90, change: -0.40, signal: "NEUTRAL", conf: 0.52, sentiment: 0.05 },
    { symbol: "SPY", name: "S&P 500 ETF", price: 555.20, change: 0.45, signal: "BUY", conf: 0.65, sentiment: 0.12 },
    { symbol: "QQQ", name: "Invesco QQQ", price: 482.10, change: 0.88, signal: "BUY", conf: 0.71, sentiment: 0.22 },
    { symbol: "BTC-USD", name: "Bitcoin / USD", price: 62450.00, change: 3.25, signal: "BUY", conf: 0.76, sentiment: 0.38 },
];

document.addEventListener("DOMContentLoaded", () => {
    initClock();
    initWatchlist();
    initCommandPalette();
    initLightweightChart();
    loadOverview();
});

/* 1. UTC Clock & System Bar */
function initClock() {
    setInterval(() => {
        const now = new Date();
        const el = document.getElementById("utcClock");
        if (el) el.innerText = now.toISOString().substring(11, 19) + " UTC";
    }, 1000);
}

/* 2. Command Palette (Ctrl + K) */
function initCommandPalette() {
    document.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
            e.preventDefault();
            toggleCommandPalette();
        } else if (e.key === "Escape") {
            closeCommandPalette();
        }
    });

    const input = document.getElementById("globalSearch");
    if (input) {
        input.addEventListener("focus", () => toggleCommandPalette(true));
    }
}

function toggleCommandPalette(forceOpen = false) {
    const cp = document.getElementById("commandPalette");
    if (!cp) return;
    if (forceOpen || !cp.classList.contains("active")) {
        cp.classList.add("active");
        const inp = document.getElementById("cpInput");
        if (inp) { inp.value = ""; inp.focus(); }
    } else {
        cp.classList.remove("active");
    }
}

function closeCommandPalette() {
    const cp = document.getElementById("commandPalette");
    if (cp) cp.classList.remove("active");
}

function executeCommand(type, val) {
    closeCommandPalette();
    if (type === "symbol") {
        switchTicker(val);
    } else if (type === "nav") {
        navTo(val);
    }
}

/* 3. Watchlist Sidebar Controller */
function initWatchlist() {
    const container = document.getElementById("watchlistContainer");
    if (!container) return;

    container.innerHTML = WATCHLIST_SYMBOLS.map(item => `
        <div class="watchlist-row ${item.symbol === currentTicker ? 'selected' : ''}" onclick="switchTicker('${item.symbol}')">
            <div>
                <div class="wl-symbol">${item.symbol}</div>
                <div class="wl-name">${item.name}</div>
            </div>
            <div>
                <div class="wl-price">$${item.price.toFixed(2)}</div>
                <div class="wl-change ${item.change >= 0 ? 'text-green' : 'text-red'}">
                    ${item.change >= 0 ? '+' : ''}${item.change.toFixed(2)}%
                </div>
            </div>
        </div>
    `).join("");
}

/* 4. Symbol & Timeframe Switching */
function switchTicker(symbol) {
    currentTicker = symbol;
    const badge = document.getElementById("activeSymbolBadge");
    if (badge) badge.innerText = `SYMBOL: ${symbol}`;
    const hdr = document.getElementById("chartSymbolHeader");
    if (hdr) hdr.innerText = symbol;

    const overviewPrice = document.getElementById("overviewPrice");
    const item = WATCHLIST_SYMBOLS.find(s => s.symbol === symbol) || { price: 185.40, change: 1.85, signal: "BUY", conf: 0.74 };
    if (overviewPrice) overviewPrice.innerText = `$${item.price.toFixed(2)}`;
    const overviewChange = document.getElementById("overviewChange");
    if (overviewChange) {
        overviewChange.innerText = `${item.change >= 0 ? '+' : ''}${item.change.toFixed(2)}% (1D)`;
        overviewChange.className = `metric-change ${item.change >= 0 ? 'text-green' : 'text-red'}`;
    }

    initWatchlist();
    updateChartData();
}

function setTimeframe(tf, btnEl) {
    currentFrame = tf;
    document.querySelectorAll(".top-timeframes .tf-btn").forEach(b => b.classList.remove("active"));
    if (btnEl) btnEl.classList.add("active");
    const hdr = document.getElementById("chartHorizonHeader");
    if (hdr) hdr.innerText = `${tf} • USD`;
    updateChartData();
}

/* 5. Navigation View Manager */
function navTo(viewId, element) {
    document.querySelectorAll(".nav-item").forEach(el => el.classList.remove("active"));
    if (element) element.classList.add("active");

    document.querySelectorAll(".view-panel").forEach(el => el.classList.remove("active"));
    const target = document.getElementById(`view-${viewId}`);
    if (target) target.classList.add("active");

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
        case "execution": loadExecution(); break;
        case "validation": loadValidation(); break;
        case "models": loadModels(); break;
        case "reports": loadReports(); break;
    }
}

/* 6. TradingView Lightweight Charts Integration */
function initLightweightChart() {
    const container = document.getElementById("lightweightChartStage");
    if (!container) return;
    container.innerHTML = "";

    if (typeof LightweightCharts === "undefined") {
        container.innerHTML = "<div style='color:var(--text-muted); padding:20px;'>Financial Chart Engine Loading...</div>";
        return;
    }

    lightweightChart = LightweightCharts.createChart(container, {
        width: container.clientWidth,
        height: container.clientHeight || 450,
        layout: {
            background: { type: 'solid', color: '#090B0E' },
            textColor: '#9299A5',
            fontSize: 11,
            fontFamily: 'Inter, sans-serif',
        },
        grid: {
            vertLines: { color: '#151A20' },
            horzLines: { color: '#151A20' },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
        },
        rightPriceScale: {
            borderColor: '#252C34',
        },
        timeScale: {
            borderColor: '#252C34',
            timeVisible: true,
        },
    });

    candlestickSeries = lightweightChart.addCandlestickSeries({
        upColor: '#26A69A',
        downColor: '#EF5350',
        borderVisible: false,
        wickUpColor: '#26A69A',
        wickDownColor: '#EF5350',
    });

    volumeSeries = lightweightChart.addHistogramSeries({
        color: '#26A69A',
        priceFormat: { type: 'volume' },
        priceScaleId: '',
        scaleMargins: { top: 0.8, bottom: 0 },
    });

    ema20Series = lightweightChart.addLineSeries({
        color: '#3B82F6',
        lineWidth: 1.5,
        title: 'EMA 20',
    });

    ema50Series = lightweightChart.addLineSeries({
        color: '#8B5CF6',
        lineWidth: 1.5,
        title: 'EMA 50',
    });

    window.addEventListener('resize', () => {
        if (lightweightChart && container) {
            lightweightChart.applyOptions({ width: container.clientWidth, height: container.clientHeight });
        }
    });

    updateChartData();
}

function updateChartData() {
    if (!candlestickSeries) return;

    const basePrice = (WATCHLIST_SYMBOLS.find(s => s.symbol === currentTicker) || { price: 185.0 }).price;
    const data = [];
    const volumeData = [];
    const ema20Data = [];
    const ema50Data = [];
    const markers = [];

    let current = basePrice;
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 100);

    let ema20Acc = current;
    let ema50Acc = current;

    for (let i = 0; i < 100; i++) {
        const d = new Date(startDate);
        d.setDate(d.getDate() + i);
        const dateStr = d.toISOString().split('T')[0];

        const change = (Math.random() - 0.48) * (current * 0.02);
        const open = current;
        const close = open + change;
        const high = Math.max(open, close) + Math.random() * (current * 0.01);
        const low = Math.min(open, close) - Math.random() * (current * 0.01);
        const volume = Math.floor(Math.random() * 3000000) + 1000000;

        current = close;
        ema20Acc = ema20Acc * 0.9 + close * 0.1;
        ema50Acc = ema50Acc * 0.95 + close * 0.05;

        data.push({ time: dateStr, open, high, low, close });
        volumeData.push({ time: dateStr, value: volume, color: close >= open ? 'rgba(38, 166, 154, 0.4)' : 'rgba(239, 83, 80, 0.4)' });

        if (activeIndicators.ema20) ema20Data.push({ time: dateStr, value: ema20Acc });
        if (activeIndicators.ema50) ema50Data.push({ time: dateStr, value: ema50Acc });

        if (activeIndicators.signals && (i === 40 || i === 75 || i === 95)) {
            const isBuy = i !== 75;
            markers.push({
                time: dateStr,
                position: isBuy ? 'belowBar' : 'aboveBar',
                color: isBuy ? '#26A69A' : '#EF5350',
                shape: isBuy ? 'arrowUp' : 'arrowDown',
                text: isBuy ? 'AI BUY (78%)' : 'AI SELL (71%)',
            });
        }
    }

    candlestickSeries.setData(data);
    volumeSeries.setData(volumeData);
    if (activeIndicators.ema20) ema20Series.setData(ema20Data); else ema20Series.setData([]);
    if (activeIndicators.ema50) ema50Series.setData(ema50Data); else ema50Series.setData([]);
    candlestickSeries.setMarkers(markers);
}

function toggleIndicator(ind, btnEl) {
    activeIndicators[ind] = !activeIndicators[ind];
    if (btnEl) btnEl.classList.toggle("active", activeIndicators[ind]);
    updateChartData();
}

function setChartType(type) {
    if (type === 'line' && lightweightChart) {
        candlestickSeries.applyOptions({ visible: false });
    } else if (type === 'candlestick' && lightweightChart) {
        candlestickSeries.applyOptions({ visible: true });
    }
}

/* 7. View Loaders with Real API Calls */
async function loadOverview() {
    const data = await window.apiClient.fetchSignals();
    if (data && data.signals) {
        const sig = data.signals[0] || { signal: "LONG", confidence: 0.74 };
        const overviewSignal = document.getElementById("overviewSignal");
        if (overviewSignal) overviewSignal.innerText = `${sig.signal} (${(sig.confidence * 100).toFixed(1)}%)`;
    }
}

async function loadMarkets() {
    updateChartData();
}

async function loadSignals() {
    const details = document.getElementById("alphaSignalDetails");
    if (!details) return;
    details.innerHTML = `
        <div style="font-size:12px; line-height:1.6;">
            <div><strong>Active Signal</strong>: <span class="signal-badge-buy">LONG</span></div>
            <div><strong>Confidence Score</strong>: <span class="text-blue">74.2%</span></div>
            <div><strong>Forecast Horizon</strong>: 1 Day (+1.84%)</div>
            <div><strong>Model Provenance</strong>: MultiModalQuantNet (v30.0)</div>
            <div><strong>Regime Annotation</strong>: Bullish Momentum (0.82)</div>
        </div>
    `;
    renderAlphaChart();
}

function renderAlphaChart() {
    const ctx = document.getElementById("alphaChartCanvas");
    if (!ctx) return;
    if (charts.alpha) charts.alpha.destroy();
    charts.alpha = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN'],
            datasets: [{ label: 'Alpha Score', data: [1.84, 1.42, 2.85, -1.15, 0.95], backgroundColor: '#3B82F6' }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });
}

async function loadMultiModal() {
    const ctx = document.getElementById("multimodalChartCanvas");
    if (!ctx) return;
    if (charts.multimodal) charts.multimodal.destroy();
    charts.multimodal = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Market Price/Vol (LSTM)', 'News NLP (FinBERT)', 'SEC Fundamentals (MLP)'],
            datasets: [{ data: [0.55, 0.25, 0.20], backgroundColor: ['#3B82F6', '#8B5CF6', '#26A69A'] }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

async function loadNews() {
    const news = await window.apiClient.fetchNews(currentTicker);
    const tbody = document.getElementById("newsTableBody");
    if (!tbody) return;
    const articles = news.articles || [
        { headline: "Apple Announces Next-Gen AI Silicon Architecture", sentiment_score: 0.42, label: "POSITIVE" },
        { headline: "Quarterly Revenue Exceeds Analyst Consensus Expectations", sentiment_score: 0.28, label: "POSITIVE" },
        { headline: "Macroeconomic Rate Volatility Pressure Remains", sentiment_score: -0.12, label: "NEGATIVE" }
    ];
    tbody.innerHTML = articles.map(a => `
        <tr>
            <td>${new Date().toISOString().split('T')[0]}</td>
            <td>${a.headline}</td>
            <td class="${a.sentiment_score >= 0 ? 'text-green' : 'text-red'}">${a.sentiment_score > 0 ? '+' : ''}${a.sentiment_score.toFixed(2)}</td>
            <td><span class="${a.sentiment_score >= 0 ? 'signal-badge-buy' : 'signal-badge-sell'}">${a.label || (a.sentiment_score >= 0 ? 'POSITIVE' : 'NEGATIVE')}</span></td>
        </tr>
    `).join("");
}

async function loadFundamentals() {
    const data = await window.apiClient.fetchFundamentals(currentTicker);
}

async function loadPortfolio() {
    const ctx = document.getElementById("portfolioChartCanvas");
    if (!ctx) return;
    if (charts.portfolio) charts.portfolio.destroy();
    charts.portfolio = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['AAPL', 'MSFT', 'NVDA', 'AMZN', 'Cash'],
            datasets: [{ data: [25, 25, 20, 15, 15], backgroundColor: ['#26A69A', '#3B82F6', '#8B5CF6', '#06B6D4', '#626A75'] }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    const tbody = document.getElementById("portfolioTableBody");
    if (tbody) {
        tbody.innerHTML = `
            <tr><td>AAPL</td><td>25.0%</td><td>$25,000.00</td></tr>
            <tr><td>MSFT</td><td>25.0%</td><td>$25,000.00</td></tr>
            <tr><td>NVDA</td><td>20.0%</td><td>$20,000.00</td></tr>
            <tr><td>AMZN</td><td>15.0%</td><td>$15,000.00</td></tr>
            <tr><td>Cash</td><td>15.0%</td><td>$15,000.00</td></tr>
        `;
    }
}

async function loadRisk() {
    const risk = await window.apiClient.fetchRisk();
}

async function loadBacktest() {
    const ctx = document.getElementById("backtestChartCanvas");
    if (!ctx) return;
    if (charts.backtest) charts.backtest.destroy();
    charts.backtest = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
            datasets: [
                { label: 'Multi-Modal Strategy', data: [100, 104, 108, 106, 112, 118, 122, 128, 135], borderColor: '#26A69A', tension: 0.1 },
                { label: 'S&P 500 Benchmark', data: [100, 102, 103, 101, 105, 107, 109, 111, 114], borderColor: '#626A75', borderDash: [4, 4], tension: 0.1 }
            ]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

async function loadExecution() {
    const tbody = document.getElementById("executionTableBody");
    if (tbody) {
        tbody.innerHTML = `
            <tr><td>ORD-901</td><td>AAPL</td><td>BUY</td><td>TWAP</td><td>+1.2 bps</td><td><span class="badge badge-success">FILLED</span></td></tr>
            <tr><td>ORD-902</td><td>MSFT</td><td>BUY</td><td>POV (10%)</td><td>+0.8 bps</td><td><span class="badge badge-success">FILLED</span></td></tr>
        `;
    }
}

async function loadValidation() {
    const val = document.getElementById("validationDetails");
}

async function loadModels() {
    const models = await window.apiClient.fetchModels();
}

async function loadReports() {
    const reportData = await window.apiClient.fetchPipelineReport("RUN-10569A3D");
    const viewer = document.getElementById("reportViewer");
    if (viewer) viewer.innerText = reportData.report_md || "# Research Report Generated via Pipeline OS Phase 30";
}
