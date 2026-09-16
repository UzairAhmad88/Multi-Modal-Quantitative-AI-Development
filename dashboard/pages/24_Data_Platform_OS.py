"""
Streamlit Page: Quantitative Data Platform, Point-in-Time Store & Feature Store OS.
"""

import streamlit as st
import pandas as pd
import json
import datetime
from data_platform.manager import DataPlatformManager

st.set_page_config(page_title="Quantitative Data Platform OS", page_icon="🗄️", layout="wide")
mgr = DataPlatformManager()

st.title("🗄️ Quantitative Data Platform, PIT Store & Feature Store OS")
st.caption("Point-in-Time Correct Data Management, Feature Store Registry, Dataset Versioning & Lineage")

tabs = st.tabs(["Ingestion & Sources", "Data Quality Audit", "Point-in-Time Query", "Feature Store Catalog", "Dataset Builder & Snapshots"])

with tabs[0]:
    st.subheader("Data Source Connectors & Ingestion Engine")
    col1, col2, col3 = st.columns(3)
    col1.metric("Market Data", "OHLCV Prices", "Daily")
    col2.metric("News NLP Data", "FinBERT Sentiment", "Intraday")
    col3.metric("Fundamentals", "SEC Filings", "Quarterly")

    st.markdown("---")
    c1, c2 = st.columns([1, 2])
    with c1:
        source_type = st.selectbox("Select Data Source", ["market", "news", "fundamentals"])
        symbols = st.multiselect("Select Symbols", ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"], default=["AAPL", "MSFT"])
        if st.button("Run Ingestion Pipeline"):
            if source_type == "market":
                res = mgr.ingest_market_data(symbols)
            elif source_type == "news":
                res = mgr.ingest_news_data(symbols)
            else:
                res = mgr.ingest_fundamental_data(symbols)
            st.success(f"Ingestion completed: {res['status']}")
            st.json(res)

    with c2:
        st.subheader("Symbol Reference Master")
        symbols_list = mgr.symbol_master.list_symbols()
        st.dataframe(pd.DataFrame(symbols_list), use_container_width=True)

with tabs[1]:
    st.subheader("Data Quality Engine & Sanity Check Reports")
    symbols = ["AAPL", "MSFT"]
    mkt = mgr.normalizer.normalize_market(mgr.market_source.fetch(symbols, "2024-01-01", "2026-09-01"))
    val_res = mgr.quality_engine.validate_market(mkt)

    status_color = "green" if val_res["status"] == "PASS" else "orange"
    st.markdown(f"### Current Status: **:{status_color}[{val_res['status']}]**")

    q1, q2, q3 = st.columns(3)
    q1.metric("Rows Inspected", val_res["row_count"])
    q2.metric("Symbols", val_res["symbol_count"])
    q3.metric("Issues Detected", len(val_res["issues"]))

    st.subheader("Quality Checks Detail")
    st.json(val_res["checks"])

    if val_res["issues"]:
        st.warning("Quality Gate Warnings:")
        for issue in val_res["issues"]:
            st.write(f"- {issue}")

with tabs[2]:
    st.subheader("Point-in-Time (PIT) Availability Query Engine")
    st.markdown("Query historical data as it was available at a specific past timestamp (preventing look-ahead bias).")

    pit_symbol = st.selectbox("Select Symbol", ["AAPL", "MSFT", "NVDA"], index=0)
    pit_ts = st.text_input("Prediction Timestamp (UTC)", value="2025-06-15 09:30:00")

    if st.button("Execute Point-In-Time Query"):
        pit_res = mgr.get_point_in_time_data(pit_symbol, pit_ts)
        st.json(pit_res)

with tabs[3]:
    st.subheader("Feature Store Registry & Catalog")
    feats = mgr.feature_registry.list_features()
    df_feats = pd.DataFrame(feats)
    if not df_feats.empty:
        st.dataframe(df_feats[["id", "name", "version", "category", "formula", "dependencies"]], use_container_width=True)

    st.subheader("Feature Sets")
    st.json({
        "technical_v1": mgr.feature_registry.get_feature_set("technical_v1"),
        "multimodal_v1": mgr.feature_registry.get_feature_set("multimodal_v1")
    })

with tabs[4]:
    st.subheader("Dataset Builder, Versioning & Snapshots")
    ds_name = st.text_input("Dataset Name", value="multimodal_daily_v1")
    ds_symbols = st.multiselect("Dataset Symbols", ["AAPL", "MSFT", "NVDA"], default=["AAPL", "MSFT"])

    if st.button("Build Versioned Dataset"):
        with st.spinner("Computing features and creating immutable snapshot..."):
            res = mgr.build_versioned_dataset(ds_symbols, dataset_name=ds_name)
            st.success(f"Built Dataset: {res['dataset_id']}")
            st.json(res)
