import time
from textwrap import dedent

import streamlit as st

from api_client import get_base_url, get_incident_trace, start_incident
from components import (
    render_agent_flow,
    render_agent_identity_cards,
    render_architecture_panel,
    render_platform_overview,
    render_trace,
)

st.set_page_config(
    page_title="TITAN Incident Command Center",
    page_icon="🛡️",
    layout="wide",
)

st.markdown(
    dedent(
        """
<style>
:root {
    --bg: #07101f;
    --bg2: #0b1730;
    --panel: linear-gradient(180deg, rgba(10,18,36,0.94) 0%, rgba(12,20,40,0.84) 100%);
    --panel-soft: linear-gradient(180deg, rgba(11,20,38,0.90) 0%, rgba(12,21,40,0.78) 100%);
    --panel-strong: linear-gradient(180deg, rgba(13,24,46,0.96) 0%, rgba(12,20,39,0.92) 100%);
    --border: rgba(148,163,184,0.14);
    --text: #e5eefc;
    --muted: #94a3b8;
    --blue: #60a5fa;
    --green: #22c55e;
    --shadow: 0 18px 48px rgba(0,0,0,0.22);
}


@keyframes titanFadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes titanPulse {
    0% { box-shadow: 0 0 0 0 rgba(96,165,250,0.10); }
    70% { box-shadow: 0 0 0 14px rgba(96,165,250,0.0); }
    100% { box-shadow: 0 0 0 0 rgba(96,165,250,0.0); }
}

@keyframes titanArrowFlow {
    0%, 100% { transform: translateX(0); opacity: 0.65; }
    50% { transform: translateX(5px); opacity: 1; }
}
html, body, [class*="css"] {
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at top left, rgba(37, 99, 235, 0.18), transparent 28%),
        radial-gradient(circle at top right, rgba(14, 165, 233, 0.08), transparent 24%),
        linear-gradient(180deg, #07101f 0%, #081327 100%);
    color: var(--text);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1430 0%, #081124 100%);
    border-right: 1px solid rgba(148,163,184,0.08);
}

.block-container {
    padding-top: 2.2rem;
    padding-bottom: 2rem;
    max-width: 1520px;
}

h1, h2, h3 {
    color: #f8fafc !important;
    letter-spacing: -0.02em;
}

hr {
    border-color: rgba(148,163,184,0.10);
}

.panel-card {
    background: var(--panel-soft);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 22px;
    box-shadow: var(--shadow);
    backdrop-filter: blur(14px);
}

.hero-shell {
    background:
      linear-gradient(90deg, rgba(96,165,250,0.04), rgba(96,165,250,0.00)),
      var(--panel-strong);
    border: 1px solid rgba(96,165,250,0.18);
    border-radius: 28px;
    padding: 30px 32px 34px 32px;
    box-shadow: var(--shadow);
    overflow: hidden;
}

.eyebrow {
    color: #93c5fd;
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.22em;
    text-transform: uppercase;
}

.hero-title {
    color: #f8fafc;
    font-size: 3.4rem;
    line-height: 1.02;
    font-weight: 900;
    letter-spacing: -0.06em;
    margin-top: 10px;
}

.hero-subtitle {
    color: #cbd5e1;
    font-size: 1.06rem;
    line-height: 1.7;
    max-width: 980px;
    margin-top: 14px;
}

.hero-chip-row,
.badge-row,
.tag-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.hero-chip {
    border-radius: 999px;
    padding: 10px 14px;
    font-size: 0.88rem;
    font-weight: 700;
    color: #e2e8f0;
    border: 1px solid rgba(148,163,184,0.14);
    background: rgba(15,23,42,0.36);
}

.kpi-grid {
    display: grid;
    grid-template-columns: 1.3fr 0.85fr 0.85fr 0.85fr 0.9fr;
    gap: 14px;
    margin-top: 1.25rem;
}

.kpi-card {
    background: linear-gradient(180deg, rgba(11,20,38,0.90) 0%, rgba(10,18,35,0.78) 100%);
    border: 1px solid rgba(148,163,184,0.13);
    border-radius: 24px;
    padding: 22px;
    min-height: 134px;
    box-shadow: var(--shadow);
}

.kpi-label {
    color: #94a3b8;
    font-size: 0.76rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 800;
}

.kpi-value {
    color: #f8fafc;
    font-size: 1.05rem;
    font-weight: 800;
    margin-top: 12px;
}

.kpi-sub {
    color: #93c5fd;
    font-size: 0.88rem;
    line-height: 1.65;
    margin-top: 10px;
}

.hypothesis-grid {
    display: grid;
    grid-template-columns: 1.45fr 0.95fr;
    gap: 18px;
    margin-top: 1.15rem;
}

.hypothesis-card {
    background:
        linear-gradient(135deg, rgba(10,18,36,0.96) 0%, rgba(16,27,48,0.84) 100%);
    border: 1px solid rgba(96,165,250,0.18);
    border-radius: 28px;
    padding: 26px 28px;
    box-shadow: var(--shadow);
}

.side-summary-card {
    background: var(--panel-soft);
    border: 1px solid var(--border);
    border-radius: 28px;
    padding: 26px;
    box-shadow: var(--shadow);
}

.section-eyebrow {
    color: #94a3b8;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    font-weight: 800;
}

.big-title {
    color: #f8fafc;
    font-size: 1.9rem;
    line-height: 1.16;
    font-weight: 900;
    letter-spacing: -0.04em;
    margin-top: 12px;
}

.section-body {
    color: #cbd5e1;
    font-size: 0.99rem;
    line-height: 1.75;
    margin-top: 12px;
}

.badge-chip {
    border-radius: 999px;
    padding: 8px 12px;
    font-size: 0.82rem;
    font-weight: 700;
    color: #dbeafe;
    border: 1px solid rgba(148,163,184,0.14);
    background: rgba(15,23,42,0.42);
}

.signal-list {
    margin-top: 18px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.signal-item {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    color: #dbeafe;
    font-size: 0.96rem;
    line-height: 1.6;
}

.signal-dot {
    width: 10px;
    height: 10px;
    border-radius: 999px;
    margin-top: 7px;
    background: linear-gradient(180deg, #38bdf8, #22c55e);
    box-shadow: 0 0 0 6px rgba(56,189,248,0.08);
}

.summary-row {
    display: flex;
    justify-content: space-between;
    gap: 14px;
    padding: 14px 0;
    border-bottom: 1px solid rgba(148,163,184,0.08);
}

.summary-row:last-child {
    border-bottom: none;
}

.summary-key {
    color: #94a3b8;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.10em;
    font-weight: 800;
}

.summary-val {
    color: #f8fafc;
    font-size: 0.98rem;
    font-weight: 800;
    text-align: right;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 1.25rem;
    border-bottom: 1px solid rgba(148,163,184,0.14);
}

.stTabs [data-baseweb="tab"] {
    padding-left: 0.2rem;
    padding-right: 0.2rem;
}

.flow-grid {
    display: grid;
    grid-template-columns: 1.15fr 0.85fr;
    gap: 18px;
    margin-top: 0.85rem;
}

.soft-card {
    background: var(--panel-soft);
    border: 1px solid var(--border);
    border-radius: 26px;
    padding: 24px;
    box-shadow: var(--shadow);
}

.card-title {
    color: #f8fafc;
    font-size: 1rem;
    font-weight: 800;
}

.card-subtitle {
    color: #94a3b8;
    font-size: 0.94rem;
    line-height: 1.7;
    margin-top: 8px;
}

.consensus-row {
    display: grid;
    grid-template-columns: 220px 28px 1fr;
    gap: 14px;
    align-items: start;
    padding: 16px 0;
    border-bottom: 1px solid rgba(148,163,184,0.08);
}

.consensus-row:last-child {
    border-bottom: none;
}

.consensus-left {
    color: #e2e8f0;
    font-size: 0.95rem;
    font-weight: 800;
}

.consensus-arrow {
    color: #60a5fa;
    font-size: 1rem;
    font-weight: 900;
    text-align: center;
}

.consensus-body {
    color: #cbd5e1;
    font-size: 0.96rem;
    line-height: 1.7;
}

.reject-item {
    padding: 14px 0;
    border-bottom: 1px solid rgba(148,163,184,0.08);
    color: #cbd5e1;
    font-size: 0.96rem;
    line-height: 1.7;
}

.reject-item:last-child {
    border-bottom: none;
}

.boundary-shell {
    background: linear-gradient(180deg, rgba(10,18,36,0.94) 0%, rgba(14,18,36,0.90) 100%);
    border: 1px solid rgba(96,165,250,0.14);
    border-radius: 28px;
    padding: 24px;
    box-shadow: var(--shadow);
    margin-top: 1rem;
}

.boundary-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
    margin-top: 18px;
}

.boundary-card {
    background: rgba(12,20,38,0.56);
    border: 1px solid rgba(148,163,184,0.10);
    border-radius: 20px;
    padding: 18px;
}

.boundary-label {
    color: #94a3b8;
    font-size: 0.76rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 800;
}

.boundary-value {
    color: #f8fafc;
    font-size: 0.98rem;
    font-weight: 800;
    line-height: 1.55;
    margin-top: 10px;
}

.dual-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
    margin-top: 1rem;
}

.action-item {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    padding: 16px 18px;
    border-radius: 18px;
    background: rgba(10,18,36,0.40);
    border: 1px solid rgba(148,163,184,0.10);
    color: #e2e8f0;
    font-size: 0.97rem;
    line-height: 1.7;
    margin-top: 12px;
}

.action-index {
    min-width: 30px;
    width: 30px;
    height: 30px;
    border-radius: 999px;
    background: rgba(96,165,250,0.16);
    color: #93c5fd;
    font-size: 0.82rem;
    font-weight: 900;
    display: flex;
    align-items: center;
    justify-content: center;
}

.timeline-shell {
    background: var(--panel-soft);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 18px 18px 20px 18px;
    box-shadow: var(--shadow);
}

.timeline-title {
    color: #f8fafc;
    font-size: 1rem;
    font-weight: 800;
}

.timeline-subtitle {
    color: #94a3b8;
    margin-top: 6px;
    margin-bottom: 14px;
}

.stage-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 12px;
}

.stage-card {
    display: flex;
    align-items: center;
    gap: 12px;
    min-height: 84px;
    padding: 14px 14px;
    border-radius: 18px;
    background: linear-gradient(180deg, rgba(10,18,36,0.80) 0%, rgba(12,20,38,0.72) 100%);
    border: 1px solid rgba(148,163,184,0.10);
}

.stage-num {
    width: 38px;
    height: 38px;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 0.95rem;
    color: #f8fafc;
    background: rgba(255,255,255,0.08);
}

.stage-label {
    color: #f8fafc;
    font-size: 0.96rem;
    font-weight: 800;
}

.stage-state {
    color: #94a3b8;
    font-size: 0.79rem;
    line-height: 1.5;
    margin-top: 2px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.current-stage {
    color: #dbeafe;
    margin-top: 14px;
    font-size: 0.96rem;
    font-weight: 700;
}

.metric-grid-4 {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin-top: 1rem;
}

.metric-box {
    background: rgba(10,18,36,0.42);
    border: 1px solid rgba(148,163,184,0.10);
    border-radius: 18px;
    padding: 18px;
}

.metric-box-label {
    color: #94a3b8;
    font-size: 0.74rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 800;
}

.metric-box-value {
    color: #f8fafc;
    font-size: 1rem;
    font-weight: 800;
    margin-top: 10px;
}

.package-grid {
    display: grid;
    grid-template-columns: 1.1fr 0.9fr;
    gap: 18px;
}

.kv-wrap {
    margin-top: 12px;
}

.kv-row {
    display: flex;
    justify-content: space-between;
    gap: 18px;
    padding: 12px 0;
    border-bottom: 1px solid rgba(148,163,184,0.08);
}

.kv-row:last-child {
    border-bottom: none;
}

.kv-key {
    color: #94a3b8;
    font-size: 0.88rem;
    line-height: 1.5;
}

.kv-val {
    color: #f8fafc;
    font-size: 0.95rem;
    font-weight: 800;
    line-height: 1.5;
    text-align: right;
}

.orch-strip {
    display: grid;
    grid-template-columns: 1fr 44px 1fr 44px 1fr 44px 1fr 44px 1fr;
    gap: 12px;
    align-items: center;
}

.orch-card {
    background: rgba(10,18,36,0.42);
    border: 1px solid rgba(148,163,184,0.10);
    border-radius: 20px;
    padding: 18px;
    min-height: 128px;
}

.orch-arrow {
    color: #60a5fa;
    font-size: 1.4rem;
    font-weight: 900;
    text-align: center;
}

.orch-node-title {
    color: #f8fafc;
    font-size: 1rem;
    font-weight: 800;
}

.orch-node-sub {
    color: #cbd5e1;
    font-size: 0.95rem;
    line-height: 1.6;
    margin-top: 10px;
}

@media (max-width: 1180px) {
    .orch-strip {
        grid-template-columns: 1fr;
    }
    .orch-arrow {
        display: none;
    }
    .orch-footer {
        grid-template-columns: 1fr;
    }
}


.authority-timeline {
    display: grid;
    grid-template-columns: 1fr 44px 1fr 44px 1fr;
    gap: 12px;
    align-items: center;
    margin-top: 14px;
}

.authority-stage {
    position: relative;
    background: rgba(10,18,36,0.42);
    border: 1px solid rgba(148,163,184,0.10);
    border-radius: 20px;
    padding: 18px;
    min-height: 118px;
    overflow: hidden;
    animation: titanFadeIn 0.4s ease-out;
}

.authority-stage::after {
    content: "";
    position: absolute;
    inset: 0 auto 0 0;
    width: 4px;
    border-radius: 20px 0 0 20px;
    background: linear-gradient(180deg, rgba(96,165,250,0.95), rgba(34,197,94,0.70));
    opacity: 0.9;
}

.authority-stage-label {
    color: #94a3b8;
    font-size: 0.74rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 800;
}

.authority-stage-value {
    color: #f8fafc;
    font-size: 1rem;
    font-weight: 800;
    margin-top: 10px;
    line-height: 1.4;
}

.authority-stage-sub {
    color: #cbd5e1;
    font-size: 0.92rem;
    line-height: 1.6;
    margin-top: 10px;
}

.authority-arrow {
    color: #60a5fa;
    font-size: 1.35rem;
    font-weight: 900;
    text-align: center;
    animation: titanArrowFlow 1.4s ease-in-out infinite;
}

.authority-highlight {
    border: 1px solid rgba(96,165,250,0.16);
    background: linear-gradient(180deg, rgba(10,18,36,0.72) 0%, rgba(12,20,38,0.56) 100%);
}

.orch-shell {
    background:
        linear-gradient(180deg, rgba(10,18,36,0.94) 0%, rgba(12,20,40,0.82) 100%);
    border: 1px solid rgba(96,165,250,0.16);
    border-radius: 28px;
    padding: 24px;
    box-shadow: var(--shadow);
    margin-top: 0.75rem;
    animation: titanFadeIn 0.45s ease-out;
}

.orch-header {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 14px;
    align-items: center;
    margin-bottom: 16px;
}

.orch-header-left {
    min-width: 260px;
}

.orch-kicker {
    color: #94a3b8;
    font-size: 0.74rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    font-weight: 800;
}

.orch-heading {
    color: #f8fafc;
    font-size: 1.06rem;
    font-weight: 900;
    margin-top: 8px;
}

.orch-summary {
    color: #94a3b8;
    font-size: 0.92rem;
    line-height: 1.7;
    margin-top: 6px;
}

.orch-pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: flex-end;
}

.orch-pill {
    border-radius: 999px;
    padding: 8px 12px;
    font-size: 0.80rem;
    font-weight: 700;
    color: #dbeafe;
    border: 1px solid rgba(96,165,250,0.16);
    background: rgba(59,130,246,0.08);
}

.orch-card {
    position: relative;
    background:
        linear-gradient(180deg, rgba(10,18,36,0.76) 0%, rgba(12,20,38,0.66) 100%);
    border: 1px solid rgba(148,163,184,0.10);
    border-radius: 20px;
    padding: 18px;
    min-height: 144px;
    overflow: hidden;
}

.orch-card::after {
    content: "";
    position: absolute;
    inset: 0 auto 0 0;
    width: 4px;
    border-radius: 20px 0 0 20px;
    background: linear-gradient(180deg, rgba(96,165,250,0.95), rgba(34,197,94,0.70));
    opacity: 0.9;
}

.orch-card-top {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    align-items: flex-start;
}

.orch-stage-chip {
    min-width: 34px;
    width: 34px;
    height: 34px;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(96,165,250,0.14);
    color: #dbeafe;
    font-size: 0.82rem;
    font-weight: 900;
    box-shadow: 0 0 0 7px rgba(96,165,250,0.07);
}

.orch-card.active .orch-stage-chip {
    background: rgba(34,197,94,0.20);
    color: #f8fafc;
    box-shadow: 0 0 0 8px rgba(34,197,94,0.10);
    animation: titanPulse 1.9s infinite;
}

.orch-card.active {
    border-color: rgba(96,165,250,0.20);
    box-shadow: 0 12px 32px rgba(0,0,0,0.18);
    transform: translateY(-1px);
}

.orch-stage-meta {
    color: #94a3b8;
    font-size: 0.74rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 800;
    margin-top: 12px;
}

.orch-arrow {
    color: #60a5fa;
    font-size: 1.45rem;
    font-weight: 900;
    text-align: center;
    opacity: 0.95;
    animation: titanArrowFlow 1.4s ease-in-out infinite;
}

.orch-footer {
    margin-top: 18px;
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 12px;
}

.orch-footer-card {
    background: rgba(10,18,36,0.42);
    border: 1px solid rgba(148,163,184,0.10);
    border-radius: 18px;
    padding: 14px 16px;
}

.orch-footer-label {
    color: #94a3b8;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 800;
}

.orch-footer-value {
    color: #f8fafc;
    font-size: 0.94rem;
    font-weight: 800;
    margin-top: 8px;
    line-height: 1.5;
}


.trace-wrapper {
    margin-top: 12px;
    overflow-x: auto;
}

.trace-table-shell {
    min-width: 1280px;
    border: 1px solid rgba(148,163,184,0.12);
    border-radius: 16px;
    overflow: hidden;
    background: rgba(6, 17, 36, 0.88);
    backdrop-filter: blur(8px);
}

.trace-html-table {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
}

.trace-html-table thead th {
    background: rgba(96,165,250,0.08);
    color: #93c5fd;
    font-weight: 700;
    font-size: 0.82rem;
    text-align: left;
    padding: 14px 16px;
    border-bottom: 1px solid rgba(148,163,184,0.08);
}

.trace-html-table tbody td {
    color: #e2e8f0;
    font-size: 0.82rem;
    padding: 14px 16px;
    border-bottom: 1px solid rgba(148,163,184,0.06);
    vertical-align: top;
    overflow: hidden;
    text-overflow: ellipsis;
}

.trace-html-table tbody tr:hover {
    background: rgba(96,165,250,0.05);
}

.trace-col-timestamp { width: 21%; }
.trace-col-sender { width: 12%; }
.trace-col-responder { width: 12%; }
.trace-col-capability { width: 15%; }
.trace-col-task { width: 15%; }
.trace-col-status { width: 10%; }
.trace-col-summary { width: 15%; }

.trace-cell-nowrap {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.trace-cell-wrap {
    white-space: normal;
    word-break: break-word;
    line-height: 1.55;
}

@media (max-width: 1180px) {
    .trace-table-shell {
        min-width: 1080px;
    }
}

.event-card {
    background: rgba(10,18,36,0.44);
    border: 1px solid rgba(148,163,184,0.10);
    border-radius: 24px;
    padding: 18px 20px;
    margin-top: 14px;
}

.event-top {
    display: flex;
    gap: 14px;
    align-items: flex-start;
}

.event-bullet {
    width: 44px;
    height: 44px;
    min-width: 44px;
    border-radius: 999px;
    background: rgba(148,163,184,0.14);
    color: #f8fafc;
    font-size: 1.1rem;
    font-weight: 900;
    display: flex;
    align-items: center;
    justify-content: center;
}

.event-title {
    color: #f8fafc;
    font-size: 0.98rem;
    font-weight: 800;
}

.event-meta {
    color: #94a3b8;
    font-size: 0.88rem;
    line-height: 1.6;
    margin-top: 4px;
}

.event-body {
    color: #dbeafe;
    font-size: 0.96rem;
    line-height: 1.8;
    margin-top: 14px;
}

.tag {
    border-radius: 999px;
    padding: 8px 12px;
    font-size: 0.80rem;
    font-weight: 700;
    color: #dbeafe;
    border: 1px solid rgba(96,165,250,0.16);
    background: rgba(59,130,246,0.08);
}

.small-muted {
    color: #94a3b8;
    font-size: 0.82rem;
}

.stAlert {
    border-radius: 18px;
}

button[kind="primary"], button[kind="secondary"] {
    border-radius: 14px !important;
}

div[data-testid="stExpander"] {
    border-radius: 20px !important;
    border: 1px solid rgba(148,163,184,0.12) !important;
    background: rgba(10,18,36,0.28) !important;
}

@media (max-width: 1400px) {
    .kpi-grid { grid-template-columns: 1fr 1fr; }
    .hypothesis-grid, .flow-grid, .dual-grid, .package-grid { grid-template-columns: 1fr; }
    .boundary-grid, .metric-grid-4 { grid-template-columns: 1fr 1fr; }
}

@media (max-width: 1180px) {
    .stage-grid, .boundary-grid, .metric-grid-4 { grid-template-columns: 1fr; }
    .consensus-row { grid-template-columns: 1fr; }
    .hero-title { font-size: 2.5rem; }
    .orch-strip { grid-template-columns: 1fr; }
    .orch-arrow { display: none; }
    .authority-timeline { grid-template-columns: 1fr; }
    .authority-arrow { display: none; }
}
</style>
"""
    ),
    unsafe_allow_html=True,
)


def _safe_get(d, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
        if cur is None:
            return default
    return cur


def _safe(value, fallback="Awaiting execution"):
    if value is None or value == "":
        return fallback
    return str(value)


def _title_case(value):
    return _safe(value).replace("_", " ").title()


DEFAULT_HYPOTHESIS = "Possible database connection pool issue"


def infer_root_cause(result, trace):
    candidates = []

    def collect(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                key = str(k).lower()
                if key in {
                    "root_cause",
                    "root_cause_hypothesis",
                    "hypothesis",
                    "cause",
                    "primary_hypothesis",
                    "summary",
                    "analysis",
                    "recommendation",
                    "reason",
                    "finding",
                } and isinstance(v, str):
                    candidates.append(v)
                collect(v)
        elif isinstance(obj, list):
            for item in obj:
                collect(item)

    collect(result or {})
    collect(trace or {})

    for text in candidates:
        if text and len(text.strip()) > 10:
            return text.strip()
    return DEFAULT_HYPOTHESIS


def _parse_percent(value: str) -> float:
    try:
        return float(str(value).replace("%", "").strip())
    except Exception:
        return 0.0


def _parse_seconds(value: str) -> float:
    try:
        return float(str(value).lower().replace("s", "").strip())
    except Exception:
        return 0.0


def normalize_hypothesis(raw_text: str, payload: dict | None = None) -> str:
    text = (raw_text or "").strip()
    lowered = text.lower()
    service = str((payload or {}).get("service", "")).lower()
    error_rate = _parse_percent((payload or {}).get("error_rate", "0"))
    latency = _parse_seconds((payload or {}).get("latency", "0"))

    if any(x in lowered for x in ["connection pool", "pool saturation", "database pool"]):
        if latency >= 5 or error_rate >= 20:
            return "Severe Backend Resource Saturation"
        if "payment" in service:
            return "Database Connection Pool Saturation"
        return "Backend Resource Saturation"

    if any(x in lowered for x in ["configuration drift", "config drift"]):
        return "Configuration Drift Detected"

    if any(x in lowered for x in ["latency", "slow response", "response time"]):
        if "payment" in service:
            return "Service Latency Degradation (Payment Path)"
        return "Service Latency Degradation"

    if any(x in lowered for x in ["memory pressure", "oom", "out of memory"]):
        return "Memory Pressure Detected"

    if any(x in lowered for x in ["network", "dns", "packet loss"]):
        return "Network Path Instability"

    if any(x in lowered for x in ["identity", "auth", "authentication"]):
        return "Identity Path Failure"

    if any(x in lowered for x in ["dependency", "downstream"]):
        return "Downstream Dependency Failure"

    if "payment" in service and latency >= 3.5 and error_rate >= 15:
        return "Payment Path Resource Saturation"

    return text if text else "Root cause under evaluation"


def classify_confidence(raw_text: str) -> str:
    lowered = (raw_text or "").lower()
    if any(x in lowered for x in ["likely", "probable", "high confidence", "recurring", "pattern"]):
        return "High"
    if any(x in lowered for x in ["possible", "suspected", "hypothesis"]):
        return "Medium"
    return "High" if "connection pool" in lowered else "Medium"


def confidence_score(label: str) -> int:
    mapping = {"Low": 45, "Medium": 68, "High": 86}
    return mapping.get(label, 68)


def confidence_bar(label: str) -> str:
    score = confidence_score(label)
    filled = round(score / 10)
    return f"{'█' * filled}{'░' * (10 - filled)} {score}%"


def is_recurring_pattern(raw_text: str) -> bool:
    lowered = (raw_text or "").lower()
    return any(x in lowered for x in ["recurr", "similar incident", "pattern match", "connection pool", "database"])


def get_status_label(result) -> str:
    severity = (_safe_get(result or {}, "detection", "severity", default="") or "").lower()
    if severity == "critical":
        return "Governed escalation active"
    if severity:
        return "Governed A2A execution"
    return "Awaiting incident launch"


def get_mode_label(result) -> str:
    severity = (_safe_get(result or {}, "detection", "severity", default="") or "").lower()
    return "OLYMPUS escalation path" if severity == "critical" else "SENTINEL action path"


def get_execution_level(result) -> str:
    severity = (_safe_get(result or {}, "detection", "severity", default="") or "").lower()
    return "Escalation-governed" if severity == "critical" else "Controlled autonomy"


def build_signal_list(payload, result, hypothesis):
    service = payload.get("service", "service") if payload else "service"
    error_rate = payload.get("error_rate", "n/a") if payload else "n/a"
    latency = payload.get("latency", "n/a") if payload else "n/a"
    severity = (_safe_get(result or {}, "detection", "severity", default=payload.get("severity") if payload else "") or "high").title()

    signals = [
        f"Detector observed elevated service degradation on {service}.",
        f"Incident payload shows error rate at {error_rate} and latency at {latency}.",
        f"Severity path entered governed {severity.lower()} incident handling.",
    ]

    lowered = (hypothesis or "").lower()
    if any(x in lowered for x in ["connection pool", "database", "resource saturation"]):
        signals.append("Pattern signature aligns with backend resource contention and pooled connection stress.")
    elif any(x in lowered for x in ["configuration drift", "config drift"]):
        signals.append("Pattern signature aligns with recent configuration variance and likely operational drift.")
    elif any(x in lowered for x in ["network", "dns", "packet loss"]):
        signals.append("Pattern signature aligns with transport instability or service-to-service network degradation.")
    else:
        signals.append("Multiple agent perspectives converged on a shared root-cause hypothesis.")

    return signals


def build_why_this_matters(payload, hypothesis):
    service = payload.get("service", "the service") if payload else "the service"
    lowered = (hypothesis or "").lower()

    if any(x in lowered for x in ["connection pool", "database", "resource saturation"]):
        return f"{service} can experience cascading latency and error amplification when backend connection capacity becomes constrained."
    if "configuration drift" in lowered:
        return f"{service} can fail unpredictably when live runtime settings diverge from the last known good baseline."
    if any(x in lowered for x in ["network", "dns", "packet loss"]):
        return f"{service} can degrade rapidly when transport paths become unstable, even if the service itself remains healthy."
    if "latency" in lowered:
        return f"{service} is experiencing performance pressure that can widen user-facing response delays and increase failure probability."
    return f"{service} is showing an incident pattern worth resolving early before it expands into broader operational impact."


def build_recommended_actions(hypothesis):
    lowered = (hypothesis or "").lower()

    if any(x in lowered for x in ["connection pool", "database", "resource saturation"]):
        return [
            "Validate active versus maximum database connections and inspect connection wait time.",
            "Review application logs for leaked sessions, unclosed transactions, or retry storms.",
            "Check recent deployment, traffic spike, or configuration changes affecting connection churn.",
            "Prepare rollback, pool resizing, or failover decision path if saturation is confirmed.",
        ]

    if any(x in lowered for x in ["configuration drift", "config drift"]):
        return [
            "Compare live configuration with the last known good baseline.",
            "Review recent deployment, feature flag, or parameter changes affecting runtime behavior.",
            "Identify drift across regions or service replicas.",
            "Prepare controlled rollback if drift is confirmed as the primary incident driver.",
        ]

    if any(x in lowered for x in ["network", "dns", "packet loss"]):
        return [
            "Validate service-to-service network paths and DNS resolution timing.",
            "Inspect recent network policy, routing, or gateway changes.",
            "Check regional skew to isolate transport-layer impact.",
            "Prepare traffic reroute or failover path if instability persists.",
        ]

    return [
        "Validate the strongest runtime indicators that support the current hypothesis.",
        "Review the most recent deployment and infrastructure changes for correlated drift.",
        "Confirm whether the impact profile matches similar prior incidents before remediation.",
        "Escalate through the governed control path if operator confidence remains low.",
    ]


def build_rejected_hypotheses(hypothesis):
    lowered = (hypothesis or "").lower()

    if any(x in lowered for x in ["connection pool", "database", "resource saturation"]):
        return [
            "Network outage rejected — no strong regional skew or infrastructure-wide connectivity signal is present.",
            "Authentication failure rejected — no token, secret, or identity anomaly dominates the incident profile.",
            "Downstream dependency failure rejected — symptoms point to local resource contention rather than external upstream collapse.",
        ]

    if any(x in lowered for x in ["configuration drift", "config drift"]):
        return [
            "Broad infrastructure outage rejected — the incident does not show platform-wide collapse.",
            "Database saturation rejected — current signals do not center on pooled connection exhaustion.",
            "Identity failure rejected — authentication is not the dominant operational symptom.",
        ]

    return [
        "Broad infrastructure outage rejected — current signals do not show multi-service collapse.",
        "Identity path failure rejected — the incident does not center on authentication degradation.",
        "Single noisy metric rejected — the hypothesis is supported by converging agent evidence, not one metric alone.",
    ]


def build_consensus_rows(payload, result, hypothesis):
    service = payload.get("service", "payment-api") if payload else "payment-api"
    severity = (_safe_get(result or {}, "detection", "severity", default=payload.get("severity") if payload else "high") or "high").upper()
    confidence = classify_confidence(hypothesis)
    normalized = normalize_hypothesis(hypothesis, payload)
    target_path = "OLYMPUS escalation" if severity == "CRITICAL" else "SENTINEL execution path"

    return [
        ("Detector → Diagnostician", f"Published normalized incident signal for {service} after threshold breach and handed the case to diagnostics."),
        ("Diagnostician → Knowledge", "Requested historical pattern matching after narrowing the likely fault domain."),
        ("Knowledge → Risk", f"Returned supporting evidence for {normalized} and marked the signature as {'recurring' if is_recurring_pattern(hypothesis) else 'credible'} with {confidence.lower()} confidence."),
        ("Risk → TITAN Governance", f"Validated business impact and blast radius, then recommended governed path selection based on severity {severity}."),
        ("TITAN Governance", f"Consensus accepted. Final outcome routed to {target_path} under policy enforcement rather than single-model discretion."),
    ]


def build_a2a_events(payload, result, trace, hypothesis):
    severity = (_safe_get(result or {}, "detection", "severity", default=payload.get("severity") if payload else "high") or "high").upper()
    service = payload.get("service", "payment-api") if payload else "payment-api"
    error_rate = payload.get("error_rate", "18%") if payload else "18%"
    latency = payload.get("latency", "4.2s") if payload else "4.2s"
    recurring = is_recurring_pattern(hypothesis)
    confidence = classify_confidence(hypothesis)

    risk_body = "Risk level is within governed thresholds. Autonomous action package prepared for controlled execution."
    if severity == "CRITICAL":
        risk_body = "Impact is critical. Governance authority recommends escalation instead of autonomous remediation."

    return [
        {
            "agent": "Detector Agent",
            "meta": "Signal detection · A2A publish",
            "title": "Detector → Diagnostician",
            "body": f"Service {service} crossed degradation thresholds with error rate {error_rate} and latency {latency}. Detector broadcast a structured incident signal to downstream agents.",
            "tags": ["threshold breached", "telemetry normalized", "incident opened"],
        },
        {
            "agent": "Diagnostician Agent",
            "meta": "Root-cause analysis · A2A request",
            "title": "Diagnostician → Knowledge",
            "body": "Diagnostician correlated latency, error pressure, and service impact to eliminate weaker explanations, then requested pattern validation for the narrowed fault domain.",
            "tags": ["symptom clustering", "fault domain narrowed", f"confidence {confidence.lower()}"],
        },
        {
            "agent": "Knowledge Agent",
            "meta": "Operational memory · A2A response",
            "title": "Knowledge → Risk",
            "body": f"Knowledge agent returned the leading hypothesis: {normalize_hypothesis(hypothesis, payload)}. {'A recurring incident signature was detected.' if recurring else 'A comparable operational pattern was identified.'}",
            "tags": ["prior pattern", "operational context", "root-cause candidate"],
        },
        {
            "agent": "Risk Agent",
            "meta": "Impact assessment · Decision support",
            "title": "Risk → TITAN Governance",
            "body": risk_body,
            "tags": [f"severity {severity.lower()}", "blast radius assessed", "governance input ready"],
        },
        {
            "agent": "TITAN Governance",
            "meta": "Authority enforcement · Final decision",
            "title": "Governance boundary crossed",
            "body": "TITAN consolidated the A2A exchange into a governed decision package. The final path was selected by control-plane authority, not by a single model response.",
            "tags": [get_mode_label(result), "deterministic control", "audit ready"],
        },
    ]


def get_decision_package(result, payload, raw_hypothesis):
    detection = result.get("detection", {}) if result else {}
    diagnostics = _safe_get(result or {}, "diagnostics", "result", default={}) or {}
    knowledge = _safe_get(result or {}, "knowledge", "result", default={}) or {}
    risk = _safe_get(result or {}, "risk", "result", default={}) or {}
    remediation = _safe_get(result or {}, "remediation", "result", default={}) or {}
    action_package = remediation.get("action_package", {}) if isinstance(remediation, dict) else {}

    severity = detection.get("severity") or payload.get("severity", "high")
    execution_mode = remediation.get("execution_mode")
    if not execution_mode:
        execution_mode = "olympus-review" if str(severity).lower() == "critical" else "sentinel-ready"

    final_decision = remediation.get("final_decision")
    if not final_decision:
        final_decision = "escalate_for_consensus" if execution_mode == "olympus-review" else "recommend_rollback"

    execution_recommendation = risk.get("execution_recommendation")
    if not execution_recommendation:
        execution_recommendation = "escalate" if str(severity).lower() == "critical" else "allow_with_audit"

    root_cause = normalize_hypothesis(
        diagnostics.get("finding") or diagnostics.get("summary") or raw_hypothesis,
        payload,
    )

    return {
        "incident_id": detection.get("incident_id") or payload.get("incident_id"),
        "service": detection.get("service") or payload.get("service"),
        "region": detection.get("region") or payload.get("region"),
        "severity": severity,
        "root_cause": root_cause,
        "recommended_action": action_package.get("recommended_action") or knowledge.get("recommended_action") or "restore previous connection pool baseline",
        "execution_recommendation": execution_recommendation,
        "final_decision": final_decision,
        "execution_mode": execution_mode,
        "runbook": action_package.get("approved_runbook") or knowledge.get("runbook_id") or "RB-117",
        "action_type": action_package.get("action_type") or "config_rollback",
        "target_service": action_package.get("target_service") or detection.get("service") or payload.get("service"),
        "target_region": action_package.get("target_region") or detection.get("region") or payload.get("region"),
    }


def render_hero(payload, result):
    incident_id = payload.get("incident_id", "—")
    service = payload.get("service", "—")
    severity = (_safe_get(result or {}, "detection", "severity", default=payload.get("severity", "—")) or "—").upper()
    region = payload.get("region", "—")
    status = get_status_label(result)
    mode = get_mode_label(result)

    st.markdown(
        dedent(
            f"""
<div class="hero-shell">
    <div class="eyebrow">TITAN Platform · Governed A2A Incident Operations</div>
    <div class="hero-title">AI Incident Command Center</div>
    <div class="hero-subtitle">
        Enterprise-grade autonomous incident operations with visible coordination, governed decisioning,
        and premium operator clarity.
    </div>
    <div class="hero-chip-row" style="margin-top:18px;">
        <span class="hero-chip">{incident_id}</span>
        <span class="hero-chip">Service: {service}</span>
        <span class="hero-chip">Severity: {severity}</span>
        <span class="hero-chip">Region: {region}</span>
        <span class="hero-chip">Path: {mode}</span>
        <span class="hero-chip">Status: {status}</span>
    </div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )


def render_kpis(payload, result, raw_hypothesis):
    incident_id = payload.get("incident_id", "—")
    service = payload.get("service", "—")
    severity = (_safe_get(result or {}, "detection", "severity", default=payload.get("severity", "high")) or "high").upper()
    region = payload.get("region", "—")
    confidence = classify_confidence(raw_hypothesis)
    status = get_status_label(result)

    st.markdown(
        dedent(
            f"""
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-label">Active Incident</div>
        <div class="kpi-value">{incident_id} · {service}</div>
        <div class="kpi-sub">Readable, premium incident framing without losing the governed A2A workflow underneath.</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Severity</div>
        <div class="kpi-value">{severity}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Region</div>
        <div class="kpi-value">{region}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Confidence</div>
        <div class="kpi-value">{confidence}</div>
        <div class="small-muted" style="margin-top:10px;">{confidence_bar(confidence)}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Decision State</div>
        <div class="kpi-value">{status}</div>
    </div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )


def render_hypothesis_panel(payload, result, raw_hypothesis):
    normalized = normalize_hypothesis(raw_hypothesis, payload)
    confidence = classify_confidence(raw_hypothesis)
    recurring = is_recurring_pattern(raw_hypothesis)
    severity = (_safe_get(result or {}, "detection", "severity", default=payload.get("severity", "high")) or "high").title()
    signals = build_signal_list(payload, result, raw_hypothesis)
    why_this_matters = build_why_this_matters(payload, normalized)

    badges = [
        '<span class="badge-chip">A2A visible</span>',
        f'<span class="badge-chip">Confidence: {confidence}</span>',
        f'<span class="badge-chip">Path: {get_mode_label(result)}</span>',
        f'<span class="badge-chip">Autonomy: {get_execution_level(result)}</span>',
    ]
    if recurring:
        badges.append('<span class="badge-chip">Recurring pattern</span>')

    right_stats = [
        ("Primary inference", normalized),
        ("Incident path", f"Governed {severity.lower()} handling"),
        ("Decision model", "Multi-agent consensus under policy enforcement"),
        ("Operator outcome", "Fast understanding with guided next actions"),
    ]

    signal_html = "".join(
        f'<div class="signal-item"><div class="signal-dot"></div><div>{s}</div></div>'
        for s in signals
    )
    right_html = "".join(
        f'<div class="summary-row"><div class="summary-key">{label}</div><div class="summary-val">{value}</div></div>'
        for label, value in right_stats
    )

    st.markdown(
        dedent(
            f"""
<div class="hypothesis-grid">
    <div class="hypothesis-card">
        <div class="section-eyebrow">Primary Root Cause Hypothesis</div>
        <div class="big-title">{normalized}</div>
        <div class="section-body">
            TITAN surfaces the strongest operational explanation first, then lets the user drill into evidence,
            consensus, and audit detail only when needed.
        </div>
        <div class="badge-row" style="margin-top:16px;">{''.join(badges)}</div>
        <div class="signal-list">{signal_html}</div>
        <div class="section-body" style="margin-top:18px;">
            <span class="section-eyebrow" style="font-size:0.72rem; letter-spacing:0.12em;">Why this matters</span><br/>
            {why_this_matters}
        </div>
    </div>
    <div class="side-summary-card">
        <div class="card-title" style="font-size:1.05rem;">Operator summary</div>
        <div class="card-subtitle">A more executive, less cluttered read of the current incident state.</div>
        <div style="margin-top:14px;">{right_html}</div>
    </div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )


def render_consensus_panel(payload, result, raw_hypothesis):
    rows = build_consensus_rows(payload, result, raw_hypothesis)
    rejected = build_rejected_hypotheses(raw_hypothesis)
    confidence = classify_confidence(raw_hypothesis)

    rows_html = "".join(
        f"""
<div class="consensus-row">
    <div class="consensus-left">{left}</div>
    <div class="consensus-arrow">➜</div>
    <div class="consensus-body">{body}</div>
</div>
"""
        for left, body in rows
    )

    rejected_html = "".join(f'<div class="reject-item">✕ {item}</div>' for item in rejected)

    st.markdown(
        dedent(
            f"""
<div class="flow-grid">
    <div class="soft-card">
        <div class="card-title">Consensus formation</div>
        <div class="card-subtitle">
            This outcome comes from multi-agent convergence under policy enforcement, not a single model answer.
            Current confidence: {confidence}.
        </div>
        <div style="margin-top:12px;">{rows_html}</div>
    </div>
    <div class="soft-card">
        <div class="card-title">Rejected hypotheses</div>
        <div class="card-subtitle">
            Showing what TITAN ruled out builds trust without forcing the operator to read raw traces first.
        </div>
        <div style="margin-top:12px;">{rejected_html}</div>
    </div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )


def render_governance_boundary(result):
    mode = get_mode_label(result)
    status = get_status_label(result)
    severity = (_safe_get(result or {}, "detection", "severity", default="high") or "high").title()

    st.markdown(
        dedent(
            f"""
<div class="boundary-shell">
    <div class="card-title">Governance boundary</div>
    <div class="card-subtitle">
        Agents collaborate up to this point. Final path selection remains with TITAN authority enforcement.
    </div>
    <div class="boundary-grid">
        <div class="boundary-card">
            <div class="boundary-label">Decision authority</div>
            <div class="boundary-value">TITAN control plane</div>
        </div>
        <div class="boundary-card">
            <div class="boundary-label">Policy outcome</div>
            <div class="boundary-value">{mode}</div>
        </div>
        <div class="boundary-card">
            <div class="boundary-label">Severity posture</div>
            <div class="boundary-value">{severity}</div>
        </div>
        <div class="boundary-card">
            <div class="boundary-label">Status</div>
            <div class="boundary-value">{status}</div>
        </div>
    </div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )


def render_governance_and_actions(result, hypothesis):
    severity = (_safe_get(result or {}, "detection", "severity", default="high") or "high").lower()
    actions = build_recommended_actions(hypothesis)

    decision_text = (
        "Autonomous remediation is denied at this stage. TITAN escalates to OLYMPUS because the incident crosses critical risk thresholds."
        if severity == "critical"
        else "Autonomous remediation remains governed and controlled. TITAN can prepare a SENTINEL-ready action package for operator approval."
    )

    left_html = f"""
<div class="soft-card">
    <div class="card-title">Governance decision</div>
    <div class="card-subtitle">
        Not a generic AI answer — a controlled result produced after multi-agent exchange and policy evaluation.
    </div>
    <div class="signal-list" style="margin-top:18px;">
        <div class="signal-item"><div class="signal-dot"></div><div>Input source: multi-agent evidence and pattern convergence</div></div>
        <div class="signal-item"><div class="signal-dot"></div><div>Authority model: deterministic, policy-governed outcome selection</div></div>
        <div class="signal-item"><div class="signal-dot"></div><div>Decision: {decision_text}</div></div>
    </div>
</div>
"""

    actions_html = "".join(
        f'<div class="action-item"><div class="action-index">{i}</div><div>{action}</div></div>'
        for i, action in enumerate(actions, start=1)
    )

    right_html = f"""
<div class="soft-card">
    <div class="card-title">Recommended next actions</div>
    <div class="card-subtitle">Action guidance is kept concise and operator-friendly.</div>
    {actions_html}
</div>
"""

    st.markdown(
        dedent(
            f"""
<div class="dual-grid">
    {left_html}
    {right_html}
</div>
"""
        ),
        unsafe_allow_html=True,
    )


def render_workflow_progress_summary(result, payload, raw_hypothesis):
    package = get_decision_package(result, payload, raw_hypothesis)
    execution_mode = package["execution_mode"]
    current_state = "Escalated to OLYMPUS" if execution_mode == "olympus-review" else "Ready for SENTINEL execution"

    steps = [
        ("Detection", "Completed"),
        ("Diagnostics", "Completed"),
        ("Knowledge", "Completed"),
        ("Risk", "Completed"),
        ("Remediation", "Completed"),
    ]

    cards_html = "".join(
        f"""
<div class="stage-card">
    <div class="stage-num" style="background:#59d46b;">{i + 1}</div>
    <div>
        <div class="stage-label">{label}</div>
        <div class="stage-state">{state}</div>
    </div>
</div>
"""
        for i, (label, state) in enumerate(steps)
    )

    metrics = [
        ("Final Decision", _title_case(package["final_decision"])),
        ("Execution Mode", _title_case(package["execution_mode"])),
        ("Severity", _title_case(package["severity"])),
        ("Runbook", _safe(package["runbook"])),
    ]

    metrics_html = "".join(
        f"""
<div class="metric-box">
    <div class="metric-box-label">{label}</div>
    <div class="metric-box-value">{value}</div>
</div>
"""
        for label, value in metrics
    )

    st.markdown(
        dedent(
            f"""
<div class="soft-card">
    <div class="card-title">Workflow progress</div>
    <div class="card-subtitle">Current state: {current_state}</div>
    <div class="stage-grid" style="margin-top:18px;">{cards_html}</div>
    <div class="metric-grid-4">{metrics_html}</div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )


def render_decision_package(result, payload, raw_hypothesis):
    package = get_decision_package(result, payload, raw_hypothesis)

    left_rows = [
        ("Incident ID", package["incident_id"]),
        ("Service", package["service"]),
        ("Region", package["region"]),
        ("Severity", _title_case(package["severity"])),
        ("Root Cause Hypothesis", package["root_cause"]),
        ("Recommended Action", package["recommended_action"]),
        ("Execution Recommendation", _title_case(package["execution_recommendation"])),
        ("Final Decision", _title_case(package["final_decision"])),
        ("Execution Mode", _title_case(package["execution_mode"])),
    ]

    right_rows = [
        ("Action Type", package["action_type"]),
        ("Target Service", package["target_service"]),
        ("Target Region", package["target_region"]),
        ("Approved Runbook", package["runbook"]),
        ("Recommended Action", package["recommended_action"]),
    ]

    def rows_to_html(rows):
        return "".join(
            f"""
<div class="kv-row">
    <div class="kv-key">{k}</div>
    <div class="kv-val">{v}</div>
</div>
"""
            for k, v in rows
        )

    st.markdown(
        dedent(
            f"""
<div class="package-grid">
    <div class="soft-card">
        <div class="card-title">Operational decision</div>
        <div class="kv-wrap">{rows_to_html(left_rows)}</div>
    </div>
    <div class="soft-card">
        <div class="card-title">Action package</div>
        <div class="kv-wrap">{rows_to_html(right_rows)}</div>
    </div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )

def render_authority_card(title, rows):
    rows_html = "".join(
        f"""
<div class="kv-row">
    <div class="kv-key">{k}</div>
    <div class="kv-val">{_safe(v)}</div>
</div>
"""
        for k, v in rows
    )
    st.markdown(
        dedent(
            f"""
<div class="soft-card" style="margin-top:12px;">
    <div class="card-title">{title}</div>
    <div class="kv-wrap">{rows_html}</div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )


def render_authority_timeline(result):
    authority_path = result.get("authority_path")
    olympus_review = result.get("olympus_review") or {}
    sentinel_execution = result.get("sentinel_execution") or {}

    if not authority_path and not olympus_review and not sentinel_execution:
        return

    titan_outcome = "Decision package finalized under governed policy enforcement."
    olympus_value = "Not required"
    olympus_sub = "Incident did not cross escalation thresholds."
    sentinel_value = "Awaiting release"
    sentinel_sub = "Execution package not yet released."

    if authority_path == "sentinel_only":
        sentinel_value = "Released to SENTINEL"
        sentinel_sub = _safe(sentinel_execution.get("summary"), "Controlled execution completed.")
    elif authority_path == "olympus_only":
        olympus_value = _title_case(olympus_review.get("decision"))
        olympus_sub = _safe(olympus_review.get("rationale"))
        sentinel_value = "Blocked pending review"
        sentinel_sub = _safe(olympus_review.get("next_action"), "Awaiting adjudication.")
    elif authority_path == "olympus_then_sentinel":
        olympus_value = _title_case(olympus_review.get("decision"))
        olympus_sub = _safe(olympus_review.get("rationale"))
        sentinel_value = "Released to SENTINEL"
        sentinel_sub = _safe(sentinel_execution.get("summary"), "Controlled execution completed.")

    st.markdown(
        dedent(
            f"""
<div class="soft-card authority-highlight" style="margin-top:1rem;">
    <div class="card-title">Authority execution timeline</div>
    <div class="card-subtitle">
        Visualizing how TITAN routes governed outcomes to adjudication and execution authorities after final decisioning.
    </div>
    <div class="authority-timeline">
        <div class="authority-stage">
            <div class="authority-stage-label">TITAN</div>
            <div class="authority-stage-value">Governed decision</div>
            <div class="authority-stage-sub">{titan_outcome}</div>
        </div>
        <div class="authority-arrow">➜</div>
        <div class="authority-stage">
            <div class="authority-stage-label">OLYMPUS</div>
            <div class="authority-stage-value">{olympus_value}</div>
            <div class="authority-stage-sub">{olympus_sub}</div>
        </div>
        <div class="authority-arrow">➜</div>
        <div class="authority-stage">
            <div class="authority-stage-label">SENTINEL</div>
            <div class="authority-stage-value">{sentinel_value}</div>
            <div class="authority-stage-sub">{sentinel_sub}</div>
        </div>
    </div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )


def render_authority_results(result):
    authority_path = result.get("authority_path")
    olympus_review = result.get("olympus_review")
    sentinel_execution = result.get("sentinel_execution")

    if not authority_path and not olympus_review and not sentinel_execution:
        return

    st.markdown(
        dedent(
            """
<div class="soft-card authority-highlight" style="margin-top:1rem;">
    <div class="card-title">Authority outcome</div>
    <div class="card-subtitle">
        TITAN routed the decision package to the appropriate downstream authority layer after governance enforcement.
    </div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )

    if authority_path:
        st.markdown(
            dedent(
                f"""
<div class="soft-card" style="margin-top:12px;">
    <div class="card-title">Authority Path</div>
    <div class="card-subtitle">{_title_case(authority_path)}</div>
</div>
"""
            ),
            unsafe_allow_html=True,
        )

    if olympus_review:
        render_authority_card(
            "OLYMPUS Review",
            [
                ("Review ID", olympus_review.get("review_id")),
                ("Decision", _title_case(olympus_review.get("decision"))),
                ("Status", _title_case(olympus_review.get("status"))),
                ("Rationale", olympus_review.get("rationale")),
                ("Next Action", olympus_review.get("next_action")),
            ],
        )

    if sentinel_execution:
        render_authority_card(
            "SENTINEL Execution",
            [
                ("Execution ID", sentinel_execution.get("execution_id")),
                ("Status", _title_case(sentinel_execution.get("status"))),
                ("Action Type", _title_case(sentinel_execution.get("action_type"))),
                ("Target Service", sentinel_execution.get("target_service")),
                ("Target Region", sentinel_execution.get("target_region")),
                ("Runbook", sentinel_execution.get("runbook_id")),
                ("Verification", _title_case(sentinel_execution.get("verification_result"))),
                ("Summary", sentinel_execution.get("summary")),
            ],
        )



def render_a2a_orchestration(result, payload, raw_hypothesis, trace):
    package = get_decision_package(result, payload, raw_hypothesis)
    authority_path = result.get("authority_path")
    olympus_review = result.get("olympus_review") or {}
    sentinel_execution = result.get("sentinel_execution") or {}

    nodes = [
        ("Detection", "Signal intake", "Normalized incident signal and opened governed flow."),
        ("Diagnostics", "Fault analysis", f"Narrowed fault domain to: {package['root_cause']}"),
        ("Knowledge", "Operational memory", f"Matched governed runbook: {package['runbook']}"),
        ("Risk", "Impact assessment", f"Evaluated posture: {_title_case(package['execution_recommendation'])}"),
        ("Remediation", "Decision package", f"Prepared governed outcome: {_title_case(package['final_decision'])}"),
    ]

    authority_label = _title_case(authority_path) if authority_path else "Governed routing pending"
    olympus_label = _title_case(olympus_review.get("decision")) if olympus_review else "Not invoked"
    sentinel_label = _title_case(sentinel_execution.get("status")) if sentinel_execution else "Not released"

    st.markdown(
        dedent(
            f"""
<div class="orch-shell">
    <div class="orch-header">
        <div class="orch-header-left">
            <div class="orch-kicker">Governed A2A orchestration</div>
            <div class="orch-heading">Premium orchestration strip</div>
            <div class="orch-summary">
                A clean, executive-grade view of how TITAN progressed from incident intake to governed action packaging.
            </div>
        </div>
        <div class="orch-pill-row">
            <span class="orch-pill">{get_mode_label(result)}</span>
            <span class="orch-pill">Authority: {authority_label}</span>
            <span class="orch-pill">Execution: {get_execution_level(result)}</span>
        </div>
    </div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )

    cols = st.columns([1, 0.08, 1, 0.08, 1, 0.08, 1, 0.08, 1])
    for idx, (title, meta, sub) in enumerate(nodes):
        active_class = " active" if idx == len(nodes) - 1 else ""
        with cols[idx * 2]:
            st.markdown(
                dedent(
                    f"""
<div class="orch-card{active_class}">
    <div class="orch-card-top">
        <div>
            <div class="orch-node-title">{title}</div>
            <div class="orch-stage-meta">{meta}</div>
        </div>
        <div class="orch-stage-chip">{idx + 1}</div>
    </div>
    <div class="orch-node-sub">{sub}</div>
</div>
"""
                ),
                unsafe_allow_html=True,
            )
        if idx < len(nodes) - 1:
            with cols[idx * 2 + 1]:
                st.markdown('<div class="orch-arrow">➜</div>', unsafe_allow_html=True)

    footer_cols = st.columns(3)
    footer_items = [
        ("Authority Path", authority_label),
        ("OLYMPUS Outcome", olympus_label),
        ("SENTINEL Status", sentinel_label),
    ]
    for col, (label, value) in zip(footer_cols, footer_items):
        with col:
            st.markdown(
                dedent(
                    f"""
<div class="orch-footer-card" style="margin-top:14px;">
    <div class="orch-footer-label">{label}</div>
    <div class="orch-footer-value">{value}</div>
</div>
"""
                ),
                unsafe_allow_html=True,
            )

    events = build_a2a_events(payload, result, trace, raw_hypothesis)

    st.markdown(
        dedent(
            """
<div class="soft-card" style="margin-top:16px;">
    <div class="card-title">A2A coordination experience</div>
    <div class="card-subtitle">
        The collaboration is visible, but condensed into a cleaner, easier-to-scan operator narrative.
    </div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )

    for event in events:
        tags_html = "".join(f'<span class="tag">{tag}</span>' for tag in event["tags"])
        st.markdown(
            dedent(
                f"""
<div class="event-card">
    <div class="event-top">
        <div class="event-bullet">•</div>
        <div>
            <div class="event-title">{event["title"]}</div>
            <div class="event-meta">{event["agent"]} · {event["meta"]}</div>
            <div class="event-body">{event["body"]}</div>
            <div class="tag-row" style="margin-top:14px;">{tags_html}</div>
        </div>
    </div>
</div>
"""
            ),
            unsafe_allow_html=True,
        )

    with st.expander("Agent flow detail", expanded=False):
        col1, col2 = st.columns([1.2, 0.8])
        with col1:
            render_agent_flow(result)
        with col2:
            render_architecture_panel()


def render_live_workflow_bar(current_index: int) -> None:
    steps = [
        ("Detection", "Signal threshold breached"),
        ("Diagnostics", "Symptom pattern evaluation"),
        ("Knowledge", "Historical pattern match"),
        ("Risk", "Impact and blast radius"),
        ("Governance", "Authority-enforced outcome"),
    ]
    current_label = steps[min(current_index, len(steps) - 1)][0] if current_index < len(steps) else "Completed"

    cards = []
    for i, (label, sublabel) in enumerate(steps):
        if current_index >= len(steps):
            state = "completed"
        elif i < current_index:
            state = "completed"
        elif i == current_index:
            state = "active"
        else:
            state = "waiting"

        if state == "completed":
            circle_style = "background:#59d46b; box-shadow:0 0 0 8px rgba(89,212,107,0.10);"
            sub = "Completed"
        elif state == "active":
            circle_style = "background:#53b5ff; box-shadow:0 0 0 8px rgba(83,181,255,0.11);"
            sub = "Running"
        else:
            circle_style = "background:#334155;"
            sub = "Waiting"

        cards.append(
            f"""
<div class="stage-card">
    <div class="stage-num" style="{circle_style}">{i + 1}</div>
    <div>
        <div class="stage-label">{label}</div>
        <div class="stage-state">{sub} · {sublabel}</div>
    </div>
</div>
"""
        )

    st.markdown(
        dedent(
            f"""
<div class="timeline-shell">
    <div class="timeline-title">Live incident execution</div>
    <div class="timeline-subtitle">Compact step-by-step visibility during runtime.</div>
    <div class="stage-grid">{''.join(cards)}</div>
    <div class="current-stage">Current stage: {current_label}</div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )


if "incident_result" not in st.session_state:
    st.session_state.incident_result = None
if "incident_trace" not in st.session_state:
    st.session_state.incident_trace = None
if "run_requested" not in st.session_state:
    st.session_state.run_requested = False
if "pending_payload" not in st.session_state:
    st.session_state.pending_payload = None

with st.sidebar:
    st.markdown(
        dedent(
            """
<div style="margin-bottom:1rem;">
    <div style="font-size:1.6rem;font-weight:800;color:#f8fafc;">Incident Intake</div>
    <div style="margin-top:0.35rem;color:#94a3b8;font-size:0.95rem;line-height:1.7;">
        Launch a governed A2A incident flow through TITAN with the same backend behavior and a cleaner presentation layer.
    </div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )

    incident_id = st.text_input("Incident ID", value="inc-5001")
    service = st.text_input("Service", value="payment-api")
    severity = st.selectbox("Severity", ["high", "critical"])
    region = st.selectbox("Region", ["us-east", "us-west", "eu-west"])
    error_rate = st.text_input("Error Rate", value="18%")
    latency = st.text_input("Latency", value="4.2s")

    st.markdown(
        dedent(
            f"""
<div class="panel-card" style="padding:18px; margin-top:0.8rem;">
    <div style="color:#e2e8f0;font-weight:800;font-size:1rem;">Mode Preview</div>
    <div style="margin-top:10px;color:#94a3b8;font-size:0.94rem;line-height:1.75;">
        Path: {'OLYMPUS escalation path' if severity == 'critical' else 'SENTINEL action path'}<br/>
        Autonomy: {'Escalation-governed' if severity == 'critical' else 'Controlled autonomy'}<br/>
        Experience: premium operator view with drill-down details
    </div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )

    run_clicked = st.button("Launch Incident Flow", use_container_width=True, type="primary")

    st.markdown(
        dedent(
            """
<div class="panel-card" style="padding:18px; margin-top:1rem;">
    <div style="color:#e2e8f0;font-weight:800;font-size:1rem;">Design Goal</div>
    <div style="margin-top:10px;color:#94a3b8;font-size:0.94rem;line-height:1.75;">
        Less repeated static content, stronger visual hierarchy, and clearer separation between summary, decisioning, orchestration, and audit detail.
    </div>
</div>
"""
        ),
        unsafe_allow_html=True,
    )

    if run_clicked:
        st.session_state.pending_payload = {
            "incident_id": incident_id,
            "service": service,
            "severity": severity,
            "region": region,
            "error_rate": error_rate,
            "latency": latency,
        }
        st.session_state.incident_result = None
        st.session_state.incident_trace = None
        st.session_state.run_requested = True

active_payload = st.session_state.pending_payload or {
    "incident_id": incident_id,
    "service": service,
    "severity": severity,
    "region": region,
    "error_rate": error_rate,
    "latency": latency,
}

st.markdown('<div style="height:0.2rem;"></div>', unsafe_allow_html=True)
render_hero(active_payload, st.session_state.incident_result or {})
st.caption(f"Connected backend: {get_base_url()}")
render_platform_overview()

if st.session_state.run_requested and st.session_state.pending_payload:
    with st.expander("Live workflow progress", expanded=True):
        workflow_placeholder = st.empty()

        payload = st.session_state.pending_payload
        incident_id_for_run = payload["incident_id"]
        step_delays = [0.7, 0.8, 0.8, 0.8, 0.7]
        step_toast = [
            "Detection complete",
            "Diagnostics complete",
            "Knowledge correlation complete",
            "Risk evaluation complete",
            "Governance decision in progress",
        ]

        for idx in range(5):
            with workflow_placeholder.container():
                render_live_workflow_bar(idx)
            if idx > 0:
                st.toast(step_toast[idx - 1])
            time.sleep(step_delays[idx])

        st.info("Finalizing governed decision and assembling audit trace...")

        try:
            result = start_incident(payload)
            trace = get_incident_trace(incident_id_for_run)

            st.session_state.incident_result = result
            st.session_state.incident_trace = trace
            st.session_state.run_requested = False
            st.session_state.pending_payload = payload

            with workflow_placeholder.container():
                render_live_workflow_bar(5)

            st.toast("Governance decision applied")
            st.success("Governed incident flow completed. Decision authority enforced by TITAN.")
        except Exception as exc:
            st.session_state.run_requested = False
            st.error(f"Failed to run incident flow: {exc}")

result = st.session_state.incident_result
trace = st.session_state.incident_trace

if result:
    raw_hypothesis = infer_root_cause(result, trace)
    render_kpis(active_payload, result, raw_hypothesis)
    render_hypothesis_panel(active_payload, result, raw_hypothesis)

    if result.get("detection", {}).get("severity") == "critical":
        olympus_review = result.get("olympus_review")

        if olympus_review:
            st.error(
                f"⚠️ Critical incident — routed to OLYMPUS. "
                f"Decision: {_title_case(olympus_review.get('decision'))}."
            )
        else:
            st.error(
                "⚠️ Critical incident — escalated to OLYMPUS for governance review. "
                "Awaiting adjudication."
            )

    tab_overview, tab_orchestration, tab_audit = st.tabs(["Overview", "Orchestration", "Audit Trail"])

    with tab_overview:
        render_consensus_panel(active_payload, result, raw_hypothesis)
        render_governance_boundary(result)
        render_governance_and_actions(result, raw_hypothesis)
        render_workflow_progress_summary(result, active_payload, raw_hypothesis)
        render_authority_timeline(result)
        with st.expander("Decision package", expanded=False):
            render_decision_package(result, active_payload, raw_hypothesis)
        with st.expander("Authority outcome", expanded=True):
            render_authority_results(result)

    with tab_orchestration:
        render_a2a_orchestration(result, active_payload, raw_hypothesis, trace)
        with st.expander("Agent identity cards", expanded=False):
            render_agent_identity_cards(result)

    with tab_audit:
        with st.expander("Trace viewer", expanded=True):
            render_trace(trace or {})
else:
    render_kpis(active_payload, {}, DEFAULT_HYPOTHESIS)
    render_hypothesis_panel(active_payload, {}, DEFAULT_HYPOTHESIS)

    tab_overview, tab_orchestration, tab_audit = st.tabs(["Overview", "Orchestration", "Audit Trail"])

    with tab_overview:
        render_consensus_panel(active_payload, {}, DEFAULT_HYPOTHESIS)
        render_governance_boundary({})
        render_governance_and_actions({}, DEFAULT_HYPOTHESIS)
        st.markdown(
            dedent(
                """
<div class="soft-card" style="margin-top:1rem;">
    <div class="card-title">Ready state</div>
    <div class="card-subtitle">
        Launch an incident from the left panel to activate the governed TITAN experience.
        The UI will surface the root-cause hypothesis, consensus formation, governance boundary,
        next actions, orchestration view, and audit trail in a cleaner operator flow.
    </div>
</div>
"""
            ),
            unsafe_allow_html=True,
        )

    with tab_orchestration:
        st.markdown(
            dedent(
                """
<div class="soft-card">
    <div class="card-title">A2A orchestration preview</div>
    <div class="card-subtitle">
        The orchestration tab will show agent-to-agent progression, step narrative, and architecture detail once an incident is launched.
    </div>
</div>
"""
            ),
            unsafe_allow_html=True,
        )
        render_architecture_panel()

    with tab_audit:
        st.markdown(
            dedent(
                """
<div class="soft-card">
    <div class="card-title">Audit trail preview</div>
    <div class="card-subtitle">
        Raw trace events and structured trace tables appear here after incident execution.
    </div>
</div>
"""
            ),
            unsafe_allow_html=True,
        )