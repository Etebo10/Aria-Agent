import streamlit as st
import json
import os
from datetime import datetime
from agents import run_nova, run_ledger, run_herald, run_ops, run_oracle, create_automation

st.set_page_config(page_title="ARIA — Business OS", page_icon="◎", layout="wide")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,300;1,400&display=swap');
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>

:root {
  --bg:        #0b0b0f;
  --bg2:       #0f0f15;
  --bg3:       #13131b;
  --bg4:       #171720;
  --card:      #111118;
  --border:    rgba(255,255,255,0.06);
  --border2:   rgba(255,255,255,0.12);
  --blue:      #2563eb;
  --blue2:     #3b82f6;
  --blue-dim:  rgba(37,99,235,0.12);
  --blue-glow: rgba(37,99,235,0.25);
  --text:      #f0f0f8;
  --text2:     #8b8ba8;
  --text3:     #4a4a68;
  --green:     #10b981;
  --green-dim: rgba(16,185,129,0.1);
  --amber:     #f59e0b;
  --amber-dim: rgba(245,158,11,0.1);
  --red:       #ef4444;
  --red-dim:   rgba(239,68,68,0.1);
  --purple:    #8b5cf6;
  --purple-dim:rgba(139,92,246,0.1);
  --cyan:      #06b6d4;
  --cyan-dim:  rgba(6,182,212,0.1);
  --poppins:   'Poppins', sans-serif;
}

/* ── RESPONSIVE CONTAINER ── */
[data-testid="stAppViewContainer"] {
  padding: 0 1.5rem;
}

@media (max-width: 1024px) {
  [data-testid="stAppViewContainer"] {
    padding: 0 1.2rem;
  }
}

@media (max-width: 768px) {
  [data-testid="stAppViewContainer"] {
    padding: 0 1rem;
  }
}

@media (max-width: 480px) {
  [data-testid="stAppViewContainer"] {
    padding: 0 0.75rem;
  }
}

/* ── ANIMATED GRID BG ── */
[data-testid="stAppViewContainer"]::before {
  content: '';
  position: fixed; inset: 0; z-index: 0;
  background-image:
    linear-gradient(rgba(37,99,235,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(37,99,235,0.03) 1px, transparent 1px);
  background-size: 60px 60px;
  animation: grid-drift 20s linear infinite;
  pointer-events: none;
}
@keyframes grid-drift { from { background-position: 0 0; } to { background-position: 60px 60px; } }

/* ── FLOATING ORBS ── */
[data-testid="stAppViewContainer"]::after {
  content: '';
  position: fixed; inset: 0; z-index: 0;
  background:
    radial-gradient(ellipse 400px 300px at 15% 20%, rgba(37,99,235,0.06) 0%, transparent 70%),
    radial-gradient(ellipse 300px 250px at 85% 70%, rgba(139,92,246,0.05) 0%, transparent 70%),
    radial-gradient(ellipse 350px 200px at 50% 90%, rgba(6,182,212,0.04) 0%, transparent 70%);
  pointer-events: none;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
  background: var(--bg2) !important;
  border-right: 1px solid var(--border) !important;
  z-index: 10;
  transition: all 0.3s ease !important;
}

/* Mobile sidebar */
@media (max-width: 1024px) {
  [data-testid="stSidebar"] {
    position: fixed !important;
    left: 0;
    top: 0;
    height: 100vh;
    width: 300px;
    max-width: 85vw;
    overflow-y: auto;
  }
}

[data-testid="stSidebar"] * { color: var(--text) !important; font-family: var(--poppins) !important; }
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextArea textarea,
[data-testid="stSidebar"] .stSelectbox > div {
  background: var(--bg3) !important;
  border: 1px solid var(--border2) !important;
  color: var(--text) !important;
  border-radius: 10px !important;
  font-family: var(--poppins) !important;
  font-size: 13px !important;
}
[data-testid="stSidebar"] .stTextInput input:focus,
[data-testid="stSidebar"] .stTextArea textarea:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 3px var(--blue-dim) !important;
}
[data-testid="stSidebar"] hr { border-color: var(--border) !important; }

/* ── BUTTONS ── */
.stButton > button {
  background: var(--blue) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 10px !important;
  font-family: var(--poppins) !important;
  font-weight: 600 !important;
  font-size: 0.82rem !important;
  letter-spacing: 0.01em !important;
  padding: 0.55rem 1.4rem !important;
  transition: all 0.2s !important;
}
.stButton > button:hover {
  background: var(--blue2) !important;
  transform: translateY(-1px) !important;
}

/* Mobile buttons */
@media (max-width: 768px) {
  .stButton > button { font-size: 0.75rem !important; padding: 0.5rem 1rem !important; }
}
@media (max-width: 480px) {
  .stButton > button { font-size: 0.7rem !important; padding: 0.45rem 0.8rem !important; }
}
.stDownloadButton > button {
  background: var(--green-dim) !important;
  color: var(--green) !important;
  border: 1px solid var(--green) !important;
  border-radius: 10px !important;
  font-family: var(--poppins) !important;
  font-weight: 600 !important;
  font-size: 0.8rem !important;
}

/* ── ARIA HEADER ── */
.aria-header {
  display: flex; 
  align-items: center; 
  justify-content: space-between;
  padding: 1.8rem 0 1.4rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1.5rem;
  position: relative; 
  z-index: 1;
  flex-wrap: wrap;
  gap: 1rem;
}

.aria-logo-wrap { 
  display: flex; 
  align-items: center; 
  gap: 14px; 
  flex: 1;
  min-width: 250px;
}

/* Mobile header */
@media (max-width: 1200px) {
  .aria-header { padding: 1.4rem 0 1.1rem; margin-bottom: 1.2rem; }
  .aria-logo-wrap { gap: 10px; }
}

@media (max-width: 768px) {
  .aria-header { 
    padding: 1rem 0 0.8rem; 
    margin-bottom: 0.8rem;
    justify-content: flex-start;
  }
  .aria-name { font-size: 1.3rem; }
  .aria-tagline { font-size: 0.6rem; }
}

@media (max-width: 480px) {
  .aria-header { 
    padding: 0.8rem 0 0.6rem;
    margin-bottom: 0.6rem;
    gap: 0.5rem;
  }
  .aria-name { font-size: 1.1rem; }
  .aria-tagline { font-size: 0.5rem; }
}
.aria-logo-wrap { display: flex; align-items: center; gap: 14px; }
.aria-orb {
  width: 48px; height: 48px; border-radius: 14px;
  background: var(--blue-dim);
  border: 1px solid var(--blue);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem; color: var(--blue);
  animation: orb-pulse 3s ease-in-out infinite;
}
@keyframes orb-pulse { 0%,100%{box-shadow:0 0 0 0 var(--blue-glow)} 50%{box-shadow:0 0 0 10px transparent} }
.aria-name { font-size: 1.7rem; font-weight: 800; color: var(--text); letter-spacing: -0.02em; }
.aria-tagline { font-size: 0.72rem; font-weight: 400; color: var(--text3); letter-spacing: 0.04em; }

/* ── SIDEBAR TOGGLE BUTTON ── */
.sidebar-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--blue);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  z-index: 100;
  transition: all 0.2s;
  flex-shrink: 0;
  margin-right: 1rem;
}
.sidebar-toggle:hover { 
  background: var(--blue2);
  transform: translateY(-2px);
}
.sidebar-toggle:active {
  transform: translateY(0);
}
.aria-status-bar { display: flex; gap: 20px; align-items: center; flex-wrap: wrap; }

/* Mobile status bar */
@media (max-width: 1200px) {
  .aria-status-bar { gap: 12px; }
}
@media (max-width: 1024px) {
  .aria-status-bar { gap: 8px; }
  .status-chip { font-size: 0.68rem; padding: 4px 10px; }
}
@media (max-width: 768px) {
  .aria-status-bar { 
    gap: 6px; 
    width: 100%; 
    margin-top: 0.8rem;
  }
  .status-chip { font-size: 0.65rem; padding: 3px 8px; }
}
@media (max-width: 480px) {
  .aria-status-bar { flex-direction: column; align-items: flex-start; gap: 4px; }
  .status-chip { font-size: 0.6rem; padding: 2px 6px; }
}
.status-chip {
  display: flex; align-items: center; gap: 6px;
  background: var(--bg3); border: 1px solid var(--border);
  border-radius: 20px; padding: 5px 12px;
  font-size: 0.7rem; font-weight: 500; color: var(--text2);
}
.status-dot { width: 6px; height: 6px; border-radius: 50%; }
.dot-green { background: var(--green); animation: blink 2s infinite; }
.dot-blue  { background: var(--blue); }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ── AGENT CARDS ── */
.agent-grid { 
  display: grid; 
  grid-template-columns: repeat(5, 1fr); 
  gap: 10px; 
  margin-bottom: 1.5rem; 
  position: relative; 
  z-index: 1; 
}

/* ── RESPONSIVE GRID ── */
@media (max-width: 1400px) {
  .agent-grid { grid-template-columns: repeat(4, 1fr); gap: 9px; }
}

@media (max-width: 1200px) {
  .agent-grid { grid-template-columns: repeat(3, 1fr); gap: 8px; }
}

@media (max-width: 768px) {
  .agent-grid { grid-template-columns: repeat(2, 1fr); gap: 7px; }
}

@media (max-width: 480px) {
  .agent-grid { 
    grid-template-columns: repeat(2, 1fr); 
    gap: 6px; 
  }
  .agent-photo { width: 40px; height: 40px; margin: 0 auto 6px; }
  .agent-photo-placeholder { width: 40px; height: 40px; font-size: 1rem; margin: 0 auto 6px; }
  .agent-code { font-size: 0.55rem; }
  .agent-card-name { font-size: 0.75rem; }
  .agent-card-role { font-size: 0.6rem; }
}
.agent-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1rem 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  position: relative; overflow: hidden;
  text-align: center;
}
.agent-card::before {
  content: ''; position: absolute; inset: 0;
  opacity: 0; transition: opacity 0.2s;
  border-radius: 14px;
}
.agent-card:hover { border-color: var(--border2); transform: translateY(-2px); }
.agent-card.active { border-color: var(--agent-color, var(--blue)); }
.agent-card.active::before { opacity: 1; background: var(--agent-bg, var(--blue-dim)); }
.agent-photo {
  width: 52px; height: 52px; border-radius: 50%;
  object-fit: cover; margin: 0 auto 8px;
  border: 2px solid var(--border);
  display: block;
}
.agent-photo-placeholder {
  width: 52px; height: 52px; border-radius: 50%;
  background: var(--bg3); border: 2px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem; margin: 0 auto 8px;
}
.agent-code { font-size: 0.6rem; font-weight: 600; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 3px; }
.agent-card-name { font-size: 0.88rem; font-weight: 700; color: var(--text); margin-bottom: 2px; }
.agent-card-role { font-size: 0.65rem; color: var(--text3); font-weight: 400; line-height: 1.4; }
.agent-status { font-size: 0.6rem; font-weight: 600; margin-top: 6px; }

/* ── CHAT AREA ── */
.chat-container { position: relative; z-index: 1; }
.chat-header {
  display: flex; align-items: center; gap: 12px;
  background: var(--card); border: 1px solid var(--border);
  border-radius: 14px 14px 0 0; padding: 1rem 1.3rem;
  border-bottom: 1px solid var(--border);
}
.chat-agent-badge {
  display: flex; align-items: center; gap: 8px;
  padding: 5px 12px; border-radius: 20px;
  font-size: 0.72rem; font-weight: 600;
}
.chat-history {
  background: var(--bg2); border: 1px solid var(--border); border-top: none;
  min-height: 320px; max-height: 480px; overflow-y: auto;
  padding: 1.2rem;
}

/* Mobile chat */
@media (max-width: 768px) {
  .chat-header { padding: 0.8rem 1rem; gap: 10px; font-size: 0.9rem; }
  .chat-agent-badge { font-size: 0.65rem; padding: 4px 10px; }
  .chat-history { 
    min-height: 250px; 
    max-height: 400px; 
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .chat-header { padding: 0.7rem 0.9rem; gap: 8px; }
  .chat-agent-badge { font-size: 0.6rem; padding: 4px 8px; }
  .chat-history { 
    min-height: 200px; 
    max-height: 350px; 
    padding: 0.8rem;
  }
  .msg-avatar { width: 28px; height: 28px; font-size: 0.7rem; }
}
.msg-wrap { display: flex; gap: 10px; margin-bottom: 1rem; }
.msg-wrap.user { flex-direction: row-reverse; }
.msg-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.8rem; flex-shrink: 0;
}
.msg-bubble {
  max-width: 75%; padding: 0.8rem 1rem;
  border-radius: 14px; font-size: 0.83rem; line-height: 1.6;
}

/* Mobile message bubbles */
@media (max-width: 768px) {
  .msg-bubble { max-width: 85%; font-size: 0.8rem; padding: 0.7rem 0.9rem; }
}
@media (max-width: 480px) {
  .msg-bubble { max-width: 100%; font-size: 0.75rem; }
}
.msg-bubble.user { background: var(--blue); color: #fff; border-radius: 14px 4px 14px 14px; }
.msg-bubble.agent { background: var(--card); border: 1px solid var(--border); color: var(--text); border-radius: 4px 14px 14px 14px; }
.msg-time { font-size: 0.6rem; color: var(--text3); margin-top: 3px; }

/* ── RESULT CARDS ── */
.result-section { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 1.3rem 1.4rem; margin-bottom: 10px; position: relative; z-index: 1; }

/* Mobile result sections */
@media (max-width: 768px) {
  .result-section { padding: 1rem 1.1rem; margin-bottom: 8px; }
}
@media (max-width: 480px) {
  .result-section { padding: 0.8rem 0.9rem; margin-bottom: 6px; }
}
.result-headline { font-size: 1rem; font-weight: 700; color: var(--text); margin-bottom: 4px; }
.result-sub { font-size: 0.75rem; color: var(--text2); margin-bottom: 1rem; }

.metric-strip { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 8px; margin-bottom: 1rem; }

/* Mobile metrics */
@media (max-width: 768px) {
  .metric-strip { grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 8px; }
}
@media (max-width: 480px) {
  .metric-strip { grid-template-columns: repeat(2, 1fr); gap: 6px; }
}
.metric-tile {
  background: var(--bg3); border: 1px solid var(--border);
  border-radius: 10px; padding: 0.8rem 1rem;
}
.metric-tile-label { font-size: 0.62rem; font-weight: 600; color: var(--text3); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px; }
.metric-tile-val { font-size: 1.4rem; font-weight: 800; color: var(--text); line-height: 1; }
.metric-tile-change { font-size: 0.68rem; font-weight: 600; margin-top: 3px; }
.change-up   { color: var(--green); }
.change-down { color: var(--red); }
.change-flat { color: var(--text3); }

.item-row {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 0.7rem 0.9rem; background: var(--bg3);
  border: 1px solid var(--border); border-radius: 10px; margin-bottom: 6px;
}
.item-icon { font-size: 0.9rem; padding-top: 2px; min-width: 20px; }
.item-title { font-size: 0.82rem; font-weight: 600; color: var(--text); margin-bottom: 2px; }
.item-detail { font-size: 0.75rem; color: var(--text2); line-height: 1.5; }
.priority-badge { font-size: 0.58rem; font-weight: 700; padding: 2px 7px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.06em; white-space: nowrap; }
.p-urgent { background: var(--red-dim); color: var(--red); }
.p-high   { background: var(--amber-dim); color: var(--amber); }
.p-normal { background: var(--blue-dim); color: var(--blue2); }
.p-low    { background: var(--bg4); color: var(--text3); }

.alert-row { display: flex; gap: 10px; align-items: flex-start; padding: 0.7rem 0.9rem; border-radius: 10px; margin-bottom: 6px; border: 1px solid transparent; }
.alert-high   { background: var(--red-dim); border-color: rgba(239,68,68,0.2); }
.alert-medium { background: var(--amber-dim); border-color: rgba(245,158,11,0.2); }
.alert-low    { background: var(--green-dim); border-color: rgba(16,185,129,0.2); }

.email-card {
  background: var(--bg3); border: 1px solid var(--border2);
  border-radius: 12px; padding: 1.1rem 1.3rem; margin-bottom: 8px;
}
.email-field { font-size: 0.72rem; color: var(--text3); font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 2px; }
.email-val { font-size: 0.83rem; color: var(--text); margin-bottom: 8px; }
.email-body { font-size: 0.82rem; color: var(--text2); line-height: 1.7; white-space: pre-wrap; border-top: 1px solid var(--border); padding-top: 10px; margin-top: 4px; }

.workflow-step {
  display: flex; gap: 12px; align-items: flex-start;
  padding: 0.8rem 1rem; background: var(--bg3);
  border: 1px solid var(--border); border-radius: 10px; margin-bottom: 6px;
  position: relative;
}
.step-num { width: 28px; height: 28px; border-radius: 50%; background: var(--blue-dim); border: 1px solid var(--blue); display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 700; color: var(--blue); flex-shrink: 0; }
.step-auto { background: var(--green-dim); border-color: var(--green); color: var(--green); }
.step-content { flex: 1; }
.step-title { font-size: 0.82rem; font-weight: 600; color: var(--text); margin-bottom: 2px; }
.step-detail { font-size: 0.73rem; color: var(--text2); }
.step-tool { font-size: 0.62rem; font-weight: 600; color: var(--cyan); margin-top: 3px; }

/* ── AUTOMATION STUDIO ── */
.auto-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 14px; padding: 1.2rem 1.4rem; margin-bottom: 10px;
  position: relative; z-index: 1;
}
.auto-card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.auto-name { font-size: 0.95rem; font-weight: 700; color: var(--text); }
.auto-badge { font-size: 0.62rem; font-weight: 600; padding: 3px 10px; border-radius: 20px; }
.auto-active   { background: var(--green-dim); color: var(--green); }
.auto-inactive { background: var(--bg3); color: var(--text3); }
.auto-trigger { font-size: 0.72rem; color: var(--text2); margin-bottom: 8px; }
.auto-step-mini { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: var(--text2); margin-bottom: 4px; }
.auto-tool-icon { width: 18px; height: 18px; border-radius: 4px; background: var(--blue-dim); display: inline-flex; align-items: center; justify-content: center; font-size: 0.6rem; color: var(--blue); }

/* ── SECTION HEADER ── */
.sec-hdr { display: flex; align-items: center; gap: 10px; margin: 1.5rem 0 0.8rem; position: relative; z-index: 1; }
.sec-hdr-icon { width: 30px; height: 30px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; }
.sec-hdr-title { font-size: 1.05rem; font-weight: 700; color: var(--text); }
.sec-hdr-sub { font-size: 0.72rem; color: var(--text3); font-weight: 400; }

/* ── FINDING CARD ── */
.finding-card { background: var(--bg3); border: 1px solid var(--border); border-left: 3px solid var(--blue); border-radius: 0 10px 10px 0; padding: 0.8rem 1rem; margin-bottom: 6px; }
.finding-title { font-size: 0.82rem; font-weight: 600; color: var(--text); margin-bottom: 3px; }
.finding-detail { font-size: 0.75rem; color: var(--text2); line-height: 1.5; }
.finding-sig { font-size: 0.62rem; font-weight: 600; margin-top: 4px; }
.sig-high   { color: var(--red); }
.sig-medium { color: var(--amber); }
.sig-low    { color: var(--green); }

/* ── TOOLS STRIP ── */
.tools-strip { display: flex; flex-wrap: wrap; gap: 6px; margin: 0.5rem 0; }

/* Mobile tools strip */
@media (max-width: 480px) {
  .tools-strip { gap: 4px; }
  .tool-chip { font-size: 0.6rem; padding: 3px 8px; }
}
.tool-chip { display: flex; align-items: center; gap: 5px; background: var(--bg3); border: 1px solid var(--border); border-radius: 20px; padding: 4px 10px; font-size: 0.65rem; font-weight: 600; color: var(--text2); }
.tool-chip i { font-size: 0.7rem; }

/* ── AGENT NOTE ── */
.agent-note { background: var(--blue-dim); border: 1px solid rgba(37,99,235,0.2); border-radius: 10px; padding: 0.7rem 1rem; margin-top: 8px; font-size: 0.75rem; color: var(--blue2); font-style: italic; }

/* ── HEALTH SCORE ── */
.health-score-wrap { text-align: center; padding: 1rem; }
.health-num { font-size: 3.5rem; font-weight: 800; line-height: 1; }
.health-label { font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 4px; }
.health-bar-bg { background: var(--bg3); height: 6px; border-radius: 3px; margin-top: 8px; }
.health-bar-fg { height: 6px; border-radius: 3px; transition: width 0.6s; }

/* ── TAGS ── */
.tag { display: inline-block; font-size: 0.62rem; font-weight: 600; padding: 3px 8px; border-radius: 6px; margin: 2px 3px 2px 0; }
.tag-blue   { background: var(--blue-dim); color: var(--blue2); }
.tag-green  { background: var(--green-dim); color: var(--green); }
.tag-amber  { background: var(--amber-dim); color: var(--amber); }
.tag-red    { background: var(--red-dim); color: var(--red); }
.tag-purple { background: var(--purple-dim); color: var(--purple); }
.tag-cyan   { background: var(--cyan-dim); color: var(--cyan); }
.tag-gray   { background: var(--bg3); color: var(--text3); }

/* ── STINPUT / TEXTAREA ── */
.stTextArea textarea, .stTextInput input {
  background: var(--bg3) !important; border: 1px solid var(--border2) !important;
  color: var(--text) !important; border-radius: 10px !important;
  font-family: var(--poppins) !important; font-size: 13.5px !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 3px var(--blue-dim) !important;
}

/* Mobile inputs */
@media (max-width: 768px) {
  .stTextArea textarea, .stTextInput input {
    font-size: 12px !important;
    padding: 0.6rem !important;
  }
}

@media (max-width: 480px) {
  .stTextArea textarea, .stTextInput input {
    font-size: 16px !important;
    border-radius: 8px !important;
    padding: 0.5rem !important;
  }
}

label { color: var(--text2) !important; font-family: var(--poppins) !important; font-size: 0.72rem !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.06em !important; }
.stSelectbox > div > div { background: var(--bg3) !important; border-color: var(--border2) !important; color: var(--text) !important; }

/* ── SPINNER ── */
.stSpinner > div { border-top-color: var(--blue) !important; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] { background: var(--bg2) !important; border-bottom: 1px solid var(--border) !important; gap: 4px !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: var(--text2) !important; border-radius: 8px 8px 0 0 !important; font-family: var(--poppins) !important; font-weight: 600 !important; font-size: 0.78rem !important; }
.stTabs [aria-selected="true"] { background: var(--blue-dim) !important; color: var(--blue2) !important; }

/* ── WELCOME HERO ── */
.hero-section {
  text-align: center; padding: 3rem 2rem;
  position: relative; z-index: 1;
}
.hero-orb-big {
  width: 90px; height: 90px; border-radius: 24px;
  background: var(--blue-dim); border: 2px solid var(--blue);
  display: flex; align-items: center; justify-content: center;
  font-size: 2.4rem; color: var(--blue); margin: 0 auto 1.2rem;
  animation: orb-pulse 3s ease-in-out infinite;
}
.hero-title { font-size: 2.8rem; font-weight: 800; color: var(--text); letter-spacing: -0.03em; line-height: 1.1; margin-bottom: 0.6rem; }
.hero-sub { font-size: 1rem; color: var(--text2); font-weight: 400; max-width: 520px; margin: 0 auto 1.5rem; line-height: 1.6; }

/* Mobile hero */
@media (max-width: 768px) {
  .hero-section { padding: 2rem 1.5rem; }
  .hero-title { font-size: 2rem; margin-bottom: 0.5rem; }
  .hero-sub { font-size: 0.9rem; margin-bottom: 1.2rem; }
}
@media (max-width: 480px) {
  .hero-section { padding: 1.5rem 1rem; }
  .hero-orb-big { width: 70px; height: 70px; font-size: 2rem; margin-bottom: 1rem; }
  .hero-title { font-size: 1.5rem; }
  .hero-sub { font-size: 0.8rem; }
}
.hero-feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; max-width: 800px; margin: 0 auto 2rem; text-align: left; }

/* Mobile hero features */
@media (max-width: 768px) {
  .hero-feature-grid { grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 8px; margin-bottom: 1.5rem; }
}
@media (max-width: 480px) {
  .hero-feature-grid { grid-template-columns: 1fr; gap: 6px; margin-bottom: 1rem; }
}
.hero-feature {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 12px; padding: 1rem 1.1rem;
}
.hero-feature-icon { font-size: 1.1rem; margin-bottom: 6px; }
.hero-feature-title { font-size: 0.82rem; font-weight: 700; color: var(--text); margin-bottom: 3px; }
.hero-feature-desc { font-size: 0.72rem; color: var(--text3); line-height: 1.5; }

/* ── FOOTER ── */
.aria-footer { border-top: 1px solid var(--border); padding: 1rem 0; display: flex; justify-content: space-between; margin-top: 3rem; position: relative; z-index: 1; }

/* Mobile footer */
@media (max-width: 768px) {
  .aria-footer { flex-direction: column; gap: 0.5rem; margin-top: 2rem; padding: 0.8rem 0; }
}

@media (max-width: 480px) {
  .aria-footer { margin-top: 1.5rem; padding: 0.6rem 0; }
}
.footer-brand { font-size: 0.78rem; font-weight: 700; color: var(--text3); }
.footer-note  { font-size: 0.65rem; color: var(--text3); }
</style>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>

<script>
(function() {
  let sidebarVisible = true;
  
  function setupToggle() {
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    
    if (!sidebarToggle || !sidebar) return false;
    
    // Remove any existing listeners
    const newToggle = sidebarToggle.cloneNode(true);
    sidebarToggle.parentNode.replaceChild(newToggle, sidebarToggle);
    
    const updatedToggle = document.querySelector('.sidebar-toggle');
    const viewport = window.innerWidth;
    
    // Initialize based on viewport
    if (viewport <= 1024) {
      sidebar.style.display = 'none';
      sidebarVisible = false;
      updatedToggle.innerHTML = '<i class="fa fa-bars"></i>';
    } else {
      sidebar.style.display = 'block';
      sidebarVisible = true;
      updatedToggle.innerHTML = '<i class="fa fa-times"></i>';
    }
    
    updatedToggle.addEventListener('click', function(e) {
      e.preventDefault();
      const sidebar = document.querySelector('[data-testid="stSidebar"]');
      if (!sidebar) return;
      
      sidebarVisible = !sidebarVisible;
      sidebar.style.display = sidebarVisible ? 'block' : 'none';
      sidebar.style.transition = 'all 0.3s ease';
      updatedToggle.innerHTML = sidebarVisible 
        ? '<i class="fa fa-times"></i>' 
        : '<i class="fa fa-bars"></i>';
    });
    
    return true;
  }
  
  // Try to setup immediately
  if (!setupToggle()) {
    // If not ready, wait for DOM
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', setupToggle);
    } else {
      setTimeout(setupToggle, 100);
    }
  }
  
  // Handle window resize
  let resizeTimer;
  window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
      const sidebar = document.querySelector('[data-testid="stSidebar"]');
      const toggle = document.querySelector('.sidebar-toggle');
      if (window.innerWidth > 1024) {
        // Desktop - always show sidebar
        if (sidebar) sidebar.style.display = 'block';
        if (toggle) toggle.innerHTML = '<i class="fa fa-times"></i>';
        sidebarVisible = true;
      }
    }, 250);
  });
})();
</script>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
AGENT_DEFS = {
    "nova":       {"name": "Nova",      "role": "Executive Assistant",    "icon": "fa-user-tie",    "color": "#2563eb", "bg": "rgba(37,99,235,0.1)",    "emoji": "👩‍💼"},
    "ledger":     {"name": "Ledger",    "role": "Finance Agent",          "icon": "fa-chart-line",  "color": "#10b981", "bg": "rgba(16,185,129,0.1)",   "emoji": "📊"},
    "herald":     {"name": "Herald",    "role": "Communications Agent",   "icon": "fa-envelope",    "color": "#8b5cf6", "bg": "rgba(139,92,246,0.1)",   "emoji": "✉️"},
    "ops":        {"name": "Ops",       "role": "Operations Agent",       "icon": "fa-gears",       "color": "#f59e0b", "bg": "rgba(245,158,11,0.1)",   "emoji": "⚙️"},
    "oracle":     {"name": "Oracle",    "role": "Intelligence Agent",     "icon": "fa-magnifying-glass-chart", "color": "#06b6d4", "bg": "rgba(6,182,212,0.1)", "emoji": "🔍"},
}

PHOTOS = {
    "nova":    "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=80&h=80&fit=crop&crop=face",
    "ledger":  "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=80&h=80&fit=crop&crop=face",
    "herald":  "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=80&h=80&fit=crop&crop=face",
    "ops":     "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=80&h=80&fit=crop&crop=face",
    "oracle":  "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=80&h=80&fit=crop&crop=face",
}

for k, v in [
    ("api_key", ""), ("biz_context", ""), ("active_agent", "nova"),
    ("results", {}), ("automations", []), ("chat_history", {}),
]:
    if k not in st.session_state:
        st.session_state[k] = v

def get_result(agent: str):
    return st.session_state.results.get(agent)

def set_result(agent: str, data: dict):
    st.session_state.results[agent] = data

def add_chat(agent: str, role: str, content: str):
    if agent not in st.session_state.chat_history:
        st.session_state.chat_history[agent] = []
    st.session_state.chat_history[agent].append({
        "role": role, "content": content,
        "time": datetime.now().strftime("%I:%M %p")
    })

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:1rem 0 0.5rem'>
      <div style='display:flex;align-items:center;gap:10px'>
        <div style='width:36px;height:36px;border-radius:10px;background:rgba(37,99,235,0.15);border:1px solid #2563eb;display:flex;align-items:center;justify-content:center;font-size:1rem;color:#2563eb'>◎</div>
        <div>
          <div style='font-size:1.1rem;font-weight:800;color:#f0f0f8;letter-spacing:-0.01em'>ARIA</div>
          <div style='font-size:0.58rem;color:#4a4a68;font-weight:500;text-transform:uppercase;letter-spacing:0.1em'>Business OS</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**<i class='fa fa-key'></i> &nbsp;Groq API Key**", unsafe_allow_html=True)
    key = st.text_input("k", type="password", placeholder="gsk_...", label_visibility="collapsed")
    if key: st.session_state.api_key = key
    st.markdown('<a href="https://console.groq.com/keys" target="_blank" style="font-size:0.7rem;color:#2563eb;font-family:Poppins,sans-serif">Get free key →</a>', unsafe_allow_html=True)
    if st.session_state.api_key:
        st.markdown('<div style="font-size:0.72rem;color:#10b981;margin-top:4px;font-family:Poppins,sans-serif"><i class="fa fa-circle-check"></i> Connected</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**<i class='fa fa-building'></i> &nbsp;Business Profile**", unsafe_allow_html=True)
    biz = st.text_area("b", placeholder="Describe your business — industry, size, what you do...", height=90, label_visibility="collapsed")
    if biz: st.session_state.biz_context = biz

    st.markdown("---")
    st.markdown("**<i class='fa fa-bolt'></i> &nbsp;Quick Prompts**", unsafe_allow_html=True)
    quick = {
        "nova":   "Schedule a team standup every Monday 9am, block Thursday afternoons for deep work, and draft a meeting agenda for Friday's quarterly review",
        "ledger": "Our revenue this month is $84,500, expenses $61,200 including payroll $38k, rent $8k, tools $4.2k. 3 invoices overdue: Acme $12k (45 days), TechCorp $8.5k (30 days), Bloom $3.2k (60 days). Give me a full financial health check.",
        "herald": "Write a professional email to a client who hasn't paid their invoice in 60 days. Amount is $12,000. Keep it firm but preserve the relationship. Also draft a shorter follow-up version.",
        "ops":    "Our sales team takes 3 hours to onboard each new client — they manually copy data between 4 spreadsheets, send welcome emails by hand, and create project folders manually. Design an automated workflow.",
        "oracle": "Research the current state of AI adoption in small businesses in 2024 and identify the top 3 opportunities our company should act on.",
    }
    for agent_key, prompt_text in quick.items():
        a = AGENT_DEFS[agent_key]
        if st.button(f"{a['emoji']} {a['name']}", use_container_width=True, key=f"quick_{agent_key}"):
            st.session_state.active_agent = agent_key
            st.session_state[f"prefill_{agent_key}"] = prompt_text
            st.rerun()

    st.markdown("---")
    if st.button("Reset ARIA", use_container_width=True):
        st.session_state.results = {}
        st.session_state.automations = []
        st.session_state.chat_history = {}
        st.rerun()

# ── HEADER ────────────────────────────────────────────────────────────────────
now = datetime.now()
active = st.session_state.active_agent
agents_done = len(st.session_state.results)

st.markdown(f"""
<div class="aria-header">
  <button class="sidebar-toggle" title="Toggle Sidebar"><i class="fa fa-bars"></i></button>
  <div class="aria-logo-wrap">
    <div class="aria-orb"><i class="fa fa-circle-nodes"></i></div>
    <div>
      <div class="aria-name">ARIA</div>
      <div class="aria-tagline">Autonomous Resources & Intelligence Assistant &nbsp;·&nbsp; Business Operating System</div>
    </div>
  </div>
  <div class="aria-status-bar">
    <div class="status-chip"><span class="status-dot dot-green"></span>5 Agents Online</div>
    <div class="status-chip"><i class="fa fa-calendar" style="color:#2563eb;font-size:0.7rem"></i>&nbsp;{now.strftime('%b %d, %Y')}</div>
    <div class="status-chip"><i class="fa fa-check-circle" style="color:#10b981;font-size:0.7rem"></i>&nbsp;{agents_done} Tasks Completed</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── AGENT SELECTOR ────────────────────────────────────────────────────────────
agent_html = '<div class="agent-grid">'
for key, a in AGENT_DEFS.items():
    is_active = key == active
    done = key in st.session_state.results
    agent_html += f"""
    <div class="agent-card {'active' if is_active else ''}"
         style="--agent-color:{a['color']};--agent-bg:{a['bg']}"
         onclick="void(0)">
      <img src="{PHOTOS[key]}" class="agent-photo" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'"/>
      <div class="agent-photo-placeholder" style="display:none;color:{a['color']}"><i class="fa {a['icon']}"></i></div>
      <div class="agent-code" style="color:{a['color']}">{key.upper()}-0{list(AGENT_DEFS.keys()).index(key)+1}</div>
      <div class="agent-card-name">{a['name']}</div>
      <div class="agent-card-role">{a['role']}</div>
      <div class="agent-status" style="color:{'#10b981' if done else a['color']}">{('✓ Ready' if done else '● Standby')}</div>
    </div>"""
agent_html += '</div>'
st.markdown(agent_html, unsafe_allow_html=True)

# Agent switcher buttons
cols = st.columns(5)
for i, (key, a) in enumerate(AGENT_DEFS.items()):
    with cols[i]:
        if st.button(f"{a['emoji']} {a['name']}", key=f"sel_{key}", use_container_width=True):
            st.session_state.active_agent = key
            st.rerun()

st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)

# ── MAIN TABS ─────────────────────────────────────────────────────────────────
tab_agent, tab_auto, tab_hub = st.tabs([
    f"  ◎ Agent Console  ",
    f"  ⚡ Automation Studio  ",
    f"  ◈ Intelligence Hub  ",
])

# ═══════════════════════════════════════════════════════
# TAB 1 — AGENT CONSOLE
# ═══════════════════════════════════════════════════════
with tab_agent:
    a    = AGENT_DEFS[active]
    prev = get_result(active)

    st.markdown(f"""
    <div class="chat-header">
      <img src="{PHOTOS[active]}" style="width:38px;height:38px;border-radius:50%;object-fit:cover;border:2px solid {a['color']}"
           onerror="this.style.display='none'"/>
      <div>
        <div style="font-size:0.92rem;font-weight:700;color:var(--text)">{a['name']}</div>
        <div style="font-size:0.68rem;color:var(--text3)">{a['role']}</div>
      </div>
      <div class="chat-agent-badge" style="background:{a['bg']};color:{a['color']};border:1px solid {a['color']}40;margin-left:auto">
        <i class="fa {a['icon']}"></i> &nbsp;{active.upper()}-0{list(AGENT_DEFS.keys()).index(active)+1}
      </div>
    </div>
    """, unsafe_allow_html=True)

    prefill = st.session_state.pop(f"prefill_{active}", "")
    prompt = st.text_area(
        f"Message {a['name']}",
        value=prefill,
        placeholder=f"Tell {a['name']} what to do...",
        height=100,
        key=f"prompt_{active}",
        label_visibility="collapsed",
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        send = st.button(f"Send to {a['name']}", key=f"send_{active}", use_container_width=True)

    if send and prompt.strip():
        if not st.session_state.api_key:
            st.error("Add your Groq API key in the sidebar.")
        else:
            add_chat(active, "user", prompt)
            with st.spinner(f"{a['name']} is working on it..."):
                ctx = st.session_state.biz_context or "General business"
                try:
                    runners = {"nova": run_nova, "ledger": run_ledger, "herald": run_herald, "ops": run_ops, "oracle": run_oracle}
                    result = runners[active](prompt, ctx, st.session_state.api_key)
                    set_result(active, result)
                    add_chat(active, "agent", result.get("headline", "Task complete."))
                except Exception as e:
                    st.error(f"{a['name']} error: {e}")
            st.rerun()

    # ── RENDER RESULTS ──────────────────────────────────────────
    if prev:
        r = prev
        headline = r.get("headline", "")
        content  = r.get("content", {})

        # Tools used
        tools = r.get("tools_used", [])
        tool_icons = {"calendar":"fa-calendar","email":"fa-envelope","gmail":"fa-envelope","tasks":"fa-list-check","sheets":"fa-table","invoicing":"fa-file-invoice","docs":"fa-file-lines","web_search":"fa-magnifying-glass"}
        tools_html = "".join(f'<div class="tool-chip"><i class="fa {tool_icons.get(t,"fa-plug")}"></i>{t}</div>' for t in tools)

        st.markdown(f"""
        <div class="result-section">
          <div class="result-headline"><i class="fa {a['icon']}" style="color:{a['color']};margin-right:8px"></i>{headline}</div>
          <div class="tools-strip">{tools_html}</div>
        """, unsafe_allow_html=True)

        # ── NOVA ──
        if active == "nova":
            st.markdown(f'<div class="result-sub">{content.get("summary","")}</div>', unsafe_allow_html=True)
            items = content.get("items", [])
            if items:
                type_icons = {"meeting":"fa-calendar-check","task":"fa-list-check","email":"fa-envelope","reminder":"fa-bell","note":"fa-note-sticky"}
                for it in items:
                    pri = it.get("priority","normal")
                    st.markdown(f"""
                    <div class="item-row">
                      <div class="item-icon" style="color:{a['color']}"><i class="fa {type_icons.get(it.get('type','task'),'fa-circle')}"></i></div>
                      <div style="flex:1">
                        <div class="item-title">{it.get('title','')}</div>
                        <div class="item-detail">{it.get('detail','')} {f'· {it.get("time","")}' if it.get('time') else ''}</div>
                      </div>
                      <div><span class="priority-badge p-{pri}">{pri}</span></div>
                    </div>""", unsafe_allow_html=True)

            de = content.get("drafted_email", {})
            if de and de.get("body"):
                st.markdown("**Drafted Email:**")
                st.markdown(f"""
                <div class="email-card">
                  <div class="email-field">To</div><div class="email-val">{de.get('to','')}</div>
                  <div class="email-field">Subject</div><div class="email-val">{de.get('subject','')}</div>
                  <div class="email-body">{de.get('body','')}</div>
                </div>""", unsafe_allow_html=True)

            recs = content.get("recommendations", [])
            if recs:
                tags = " ".join(f'<span class="tag tag-blue"><i class="fa fa-lightbulb"></i> {r2}</span>' for r2 in recs)
                st.markdown(f'<div style="margin-top:8px">{tags}</div>', unsafe_allow_html=True)

        # ── LEDGER ──
        elif active == "ledger":
            hs = r.get("health_score", 50)
            hl = r.get("health_label", "Stable")
            hcolor = {"Strong":"#10b981","Healthy":"#10b981","Stable":"#f59e0b","At Risk":"#ef4444","Critical":"#ef4444"}.get(hl,"#f59e0b")
            metrics = content.get("metrics", [])
            col_h, col_m = st.columns([1, 3])
            with col_h:
                st.markdown(f"""
                <div class="health-score-wrap">
                  <div class="health-num" style="color:{hcolor}">{hs}</div>
                  <div class="health-label" style="color:{hcolor}">{hl}</div>
                  <div class="health-bar-bg"><div class="health-bar-fg" style="width:{hs}%;background:{hcolor}"></div></div>
                  <div style="font-size:0.62rem;color:var(--text3);margin-top:6px;text-transform:uppercase;letter-spacing:0.08em">Financial Health</div>
                </div>""", unsafe_allow_html=True)
            with col_m:
                if metrics:
                    metric_html = '<div class="metric-strip">'
                    for m in metrics[:6]:
                        sc = {"good":"change-up","warn":"change-flat","bad":"change-down"}.get(m.get("status","warn"),"change-flat")
                        metric_html += f"""
                        <div class="metric-tile">
                          <div class="metric-tile-label">{m.get('label','')}</div>
                          <div class="metric-tile-val">{m.get('value','')}</div>
                          <div class="metric-tile-change {sc}">{m.get('change','')}</div>
                        </div>"""
                    metric_html += '</div>'
                    st.markdown(metric_html, unsafe_allow_html=True)

            for alert in content.get("alerts", []):
                sev = alert.get("severity","medium")
                icon = {"high":"fa-triangle-exclamation","medium":"fa-circle-exclamation","low":"fa-circle-info"}.get(sev,"fa-circle")
                acolor = {"high":"var(--red)","medium":"var(--amber)","low":"var(--green)"}.get(sev,"var(--amber)")
                st.markdown(f"""
                <div class="alert-row alert-{sev}">
                  <i class="fa {icon}" style="color:{acolor};padding-top:2px"></i>
                  <div style="flex:1">
                    <div style="font-size:0.8rem;font-weight:600;color:var(--text)">{alert.get('message','')}</div>
                    <div style="font-size:0.72rem;color:var(--text2);margin-top:2px"><i class="fa fa-arrow-right" style="color:{acolor}"></i> {alert.get('action','')}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

            forecast = content.get("forecast","")
            if forecast:
                st.markdown(f'<div class="agent-note"><i class="fa fa-binoculars" style="color:var(--blue2);margin-right:6px"></i>{forecast}</div>', unsafe_allow_html=True)

        # ── HERALD ──
        elif active == "herald":
            doc = content.get("primary_document", {})
            if doc:
                st.markdown(f"""
                <div class="email-card">
                  {'<div class="email-field">To</div><div class="email-val">'+doc.get('to','')+'</div>' if doc.get('to') else ''}
                  {'<div class="email-field">Subject</div><div class="email-val">'+doc.get('subject','')+'</div>' if doc.get('subject') else ''}
                  <div class="email-field">Tone</div><div style="margin-bottom:8px"><span class="tag tag-purple">{doc.get('tone','professional')}</span></div>
                  <div class="email-body">{doc.get('body','')}</div>
                </div>""", unsafe_allow_html=True)

            alts = content.get("alternatives", [])
            if alts:
                st.markdown('<div style="font-size:0.75rem;font-weight:600;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin:10px 0 6px">Alternative versions</div>', unsafe_allow_html=True)
                for alt in alts:
                    with st.expander(alt.get("label","Alternative")):
                        st.markdown(alt.get("body",""), unsafe_allow_html=False)

            tips = content.get("usage_tips", [])
            if tips:
                tags = " ".join(f'<span class="tag tag-purple"><i class="fa fa-lightbulb"></i> {t}</span>' for t in tips)
                st.markdown(f'<div style="margin-top:8px">{tags}</div>', unsafe_allow_html=True)

        # ── OPS ──
        elif active == "ops":
            st.markdown(f'<div class="result-sub">{content.get("summary","")}</div>', unsafe_allow_html=True)
            steps = content.get("workflow_steps", [])
            if steps:
                st.markdown('<div style="font-size:0.72rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px"><i class="fa fa-diagram-project"></i> Workflow</div>', unsafe_allow_html=True)
                for s in steps:
                    is_auto = s.get("automation_possible", False)
                    st.markdown(f"""
                    <div class="workflow-step">
                      <div class="step-num {'step-auto' if is_auto else ''}">{s.get('step','')}</div>
                      <div class="step-content">
                        <div class="step-title">{s.get('title','')} {'<span class="tag tag-green">Auto</span>' if is_auto else ''}</div>
                        <div class="step-detail">{s.get('output','')} · <span style="color:var(--text3)">{s.get('duration','')}</span></div>
                        <div class="step-tool"><i class="fa fa-plug"></i> {s.get('tool','')} · Owner: {s.get('owner','')}</div>
                      </div>
                    </div>""", unsafe_allow_html=True)

            autos = content.get("automation_rules", [])
            if autos:
                st.markdown('<div style="font-size:0.72rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin:12px 0 8px"><i class="fa fa-bolt"></i> Automation Rules</div>', unsafe_allow_html=True)
                for aut in autos:
                    st.markdown(f"""
                    <div class="item-row" style="border-left:3px solid var(--amber)">
                      <i class="fa fa-bolt" style="color:var(--amber);padding-top:2px"></i>
                      <div style="flex:1">
                        <div class="item-title">When: {aut.get('trigger','')}</div>
                        <div class="item-detail">Then: {aut.get('action','')} &nbsp;·&nbsp; <span style="color:var(--green)">{aut.get('saves','')} saved</span></div>
                      </div>
                      <span class="tag tag-cyan">{aut.get('tool','')}</span>
                    </div>""", unsafe_allow_html=True)

        # ── ORACLE ──
        elif active == "oracle":
            st.markdown(f'<div style="font-size:0.85rem;color:var(--text2);line-height:1.65;margin-bottom:1rem">{content.get("executive_summary","")}</div>', unsafe_allow_html=True)
            findings = content.get("key_findings", [])
            if findings:
                st.markdown('<div style="font-size:0.72rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px"><i class="fa fa-lightbulb"></i> Key Findings</div>', unsafe_allow_html=True)
                for f in findings:
                    sig = f.get("significance","medium")
                    st.markdown(f"""
                    <div class="finding-card" style="border-left-color:{'var(--red)' if sig=='high' else 'var(--amber)' if sig=='medium' else 'var(--green)'}">
                      <div class="finding-title">{f.get('finding','')}</div>
                      <div class="finding-detail">{f.get('implication','')}</div>
                      <div class="finding-sig sig-{sig}"><i class="fa fa-circle-dot"></i> {sig.upper()} SIGNIFICANCE · {f.get('source','')}</div>
                    </div>""", unsafe_allow_html=True)

            cols2 = st.columns(2)
            with cols2[0]:
                opps = content.get("opportunities",[])
                if opps:
                    st.markdown('<div style="font-size:0.72rem;font-weight:700;color:var(--green);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px"><i class="fa fa-rocket"></i> Opportunities</div>', unsafe_allow_html=True)
                    for o in opps:
                        st.markdown(f'<div class="item-row" style="border-left:3px solid var(--green)"><i class="fa fa-arrow-trend-up" style="color:var(--green)"></i><div class="item-detail" style="color:var(--text)">{o}</div></div>', unsafe_allow_html=True)
            with cols2[1]:
                threats = content.get("threats",[])
                if threats:
                    st.markdown('<div style="font-size:0.72rem;font-weight:700;color:var(--red);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px"><i class="fa fa-shield-halved"></i> Threats</div>', unsafe_allow_html=True)
                    for t in threats:
                        st.markdown(f'<div class="item-row" style="border-left:3px solid var(--red)"><i class="fa fa-triangle-exclamation" style="color:var(--red)"></i><div class="item-detail" style="color:var(--text)">{t}</div></div>', unsafe_allow_html=True)

            comps = content.get("competitor_landscape",[])
            if comps:
                st.markdown('<div style="font-size:0.72rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin:12px 0 8px"><i class="fa fa-chess-board"></i> Competitor Landscape</div>', unsafe_allow_html=True)
                for c in comps:
                    tl = c.get("threat_level","medium")
                    tcolor = {"high":"var(--red)","medium":"var(--amber)","low":"var(--green)"}.get(tl,"var(--amber)")
                    st.markdown(f"""
                    <div class="item-row">
                      <i class="fa fa-building" style="color:{tcolor}"></i>
                      <div style="flex:1">
                        <div class="item-title">{c.get('name','')}</div>
                        <div class="item-detail"><span style="color:var(--green)">+ {c.get('strength','')}</span> &nbsp; <span style="color:var(--red)">- {c.get('weakness','')}</span></div>
                      </div>
                      <span class="tag tag-{'red' if tl=='high' else 'amber' if tl=='medium' else 'green'}">Threat: {tl}</span>
                    </div>""", unsafe_allow_html=True)

        # Agent note
        note_key = f"{active}_note"
        note = r.get(note_key, "")
        if note:
            st.markdown(f'<div class="agent-note"><img src="{PHOTOS[active]}" style="width:18px;height:18px;border-radius:50%;object-fit:cover;vertical-align:middle;margin-right:6px"/>{note}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Download
        st.download_button(
            f"Download {a['name']}'s Report",
            data=json.dumps(prev, indent=2),
            file_name=f"aria_{active}_report.json",
            mime="application/json",
        )

    elif not prev:
        # Welcome landing
        a_def = AGENT_DEFS[active]
        st.markdown(f"""
        <div style="text-align:center;padding:3rem 2rem;position:relative;z-index:1">
          <img src="{PHOTOS[active]}" style="width:80px;height:80px;border-radius:50%;object-fit:cover;border:3px solid {a_def['color']};margin:0 auto 1rem;display:block"/>
          <div style="font-size:1.5rem;font-weight:800;color:var(--text);margin-bottom:6px">{a_def['name']}</div>
          <div style="font-size:0.85rem;color:var(--text2);margin-bottom:1.5rem">{a_def['role']} &nbsp;·&nbsp; Ready for instructions</div>
          <div style="background:var(--card);border:1px solid var(--border);border-radius:14px;padding:1.2rem;max-width:480px;margin:0 auto;font-size:0.8rem;color:var(--text2);line-height:1.7">
            Use the quick prompts in the sidebar to see {a_def['name']} in action, or type your own instruction above.
          </div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# TAB 2 — AUTOMATION STUDIO
# ═══════════════════════════════════════════════════════
with tab_auto:
    st.markdown("""
    <div class="sec-hdr">
      <div class="sec-hdr-icon" style="background:rgba(245,158,11,0.1);color:#f59e0b"><i class="fa fa-bolt"></i></div>
      <div><div class="sec-hdr-title">Automation Studio</div><div class="sec-hdr-sub">Design workflows that run automatically across your tools</div></div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns([2, 1])
    with col_a:
        auto_prompt = st.text_area(
            "Describe your automation",
            placeholder='e.g. "When a new lead fills our contact form, create a task in my to-do list, send them a welcome email, and add their info to our Google Sheet"',
            height=110,
            label_visibility="collapsed",
        )
    with col_b:
        st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
        if st.button("⚡ Build Automation", use_container_width=True):
            if not st.session_state.api_key:
                st.error("API key needed.")
            elif auto_prompt.strip():
                with st.spinner("Designing your automation..."):
                    result = create_automation(auto_prompt, st.session_state.api_key)
                    st.session_state.automations.insert(0, result)
                st.rerun()

        # Preset automations
        presets = [
            "When a new email arrives from a client, create a task and send an acknowledgement reply within 5 minutes",
            "Every Monday at 8am, pull last week's sales data from Google Sheets and email me a summary report",
            "When an invoice is overdue by 7 days, automatically send a payment reminder email and flag it in our tracker",
            "When I add a new contact to Google Contacts, add them to our CRM spreadsheet and send a welcome email",
        ]
        st.markdown('<div style="font-size:0.68rem;font-weight:600;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin-top:10px;margin-bottom:6px">Quick templates</div>', unsafe_allow_html=True)
        for preset in presets:
            if st.button(f"↗ {preset[:50]}...", use_container_width=True, key=f"pre_{preset[:20]}"):
                st.session_state[f"auto_prefill"] = preset
                st.rerun()

    # Render saved automations
    if st.session_state.automations:
        st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:0.72rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px"><i class="fa fa-list-check"></i> {len(st.session_state.automations)} Automation(s) Created</div>', unsafe_allow_html=True)
        for aut in st.session_state.automations:
            cplx = aut.get("complexity","Moderate")
            cplx_cls = {"Simple":"tag-green","Moderate":"tag-amber","Complex":"tag-red"}.get(cplx,"tag-amber")
            steps_html = "".join(
                f'<div class="auto-step-mini"><div class="auto-tool-icon"><i class="fa fa-plug"></i></div>{s.get("action","")}</div>'
                for s in aut.get("steps",[])[:4]
            )
            tools_req = " ".join(f'<span class="tag tag-blue">{t}</span>' for t in aut.get("tools_required",[]))
            st.markdown(f"""
            <div class="auto-card">
              <div class="auto-card-header">
                <div>
                  <div class="auto-name"><i class="fa fa-bolt" style="color:var(--amber);margin-right:6px"></i>{aut.get('automation_name','Automation')}</div>
                  <div class="auto-trigger"><i class="fa fa-play" style="color:var(--text3);margin-right:4px"></i>{aut.get('trigger',{}).get('event','')}</div>
                </div>
                <div style="text-align:right">
                  <span class="auto-badge auto-active">● Active</span>
                  <div style="font-size:0.65rem;color:var(--green);margin-top:4px"><i class="fa fa-clock"></i> Saves {aut.get('estimated_time_saved','?')}</div>
                  <span class="tag {cplx_cls}" style="margin-top:4px">{cplx}</span>
                </div>
              </div>
              <div style="font-size:0.78rem;color:var(--text2);margin-bottom:8px">{aut.get('description','')}</div>
              {steps_html}
              <div style="margin-top:8px">{tools_req}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:2.5rem;background:var(--card);border:1px solid var(--border);border-radius:14px;margin-top:1rem">
          <div style="font-size:2rem;color:var(--text3);margin-bottom:8px"><i class="fa fa-bolt"></i></div>
          <div style="font-size:0.88rem;font-weight:600;color:var(--text2);margin-bottom:4px">No automations yet</div>
          <div style="font-size:0.75rem;color:var(--text3)">Describe a workflow above and ARIA will design it for you</div>
        </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# TAB 3 — INTELLIGENCE HUB
# ═══════════════════════════════════════════════════════
with tab_hub:
    st.markdown("""
    <div class="sec-hdr">
      <div class="sec-hdr-icon" style="background:rgba(6,182,212,0.1);color:#06b6d4"><i class="fa fa-chart-network"></i></div>
      <div><div class="sec-hdr-title">Intelligence Hub</div><div class="sec-hdr-sub">All agent outputs, cross-referenced and summarised</div></div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.results:
        st.markdown("""
        <div style="text-align:center;padding:3rem;background:var(--card);border:1px solid var(--border);border-radius:14px">
          <div style="font-size:2.5rem;color:var(--text3);margin-bottom:10px"><i class="fa fa-circle-nodes"></i></div>
          <div style="font-size:1rem;font-weight:700;color:var(--text2);margin-bottom:6px">No agent data yet</div>
          <div style="font-size:0.8rem;color:var(--text3);max-width:360px;margin:0 auto">Use the Agent Console tab to run each agent. Their outputs will appear here in a unified view.</div>
        </div>""", unsafe_allow_html=True)
    else:
        # Summary cards
        summary_cols = st.columns(len(st.session_state.results))
        for i, (key, result) in enumerate(st.session_state.results.items()):
            a_def = AGENT_DEFS[key]
            with summary_cols[i]:
                st.markdown(f"""
                <div class="result-section" style="border-top:3px solid {a_def['color']};text-align:center;padding:1rem">
                  <img src="{PHOTOS[key]}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;border:2px solid {a_def['color']};margin:0 auto 6px;display:block"/>
                  <div style="font-size:0.82rem;font-weight:700;color:var(--text)">{a_def['name']}</div>
                  <div style="font-size:0.65rem;color:var(--text3);margin-bottom:6px">{a_def['role']}</div>
                  <span class="tag tag-green"><i class="fa fa-check"></i> Complete</span>
                </div>""", unsafe_allow_html=True)

        # Cross-agent insights
        if len(st.session_state.results) >= 2:
            st.markdown('<div style="font-size:0.72rem;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin:1.2rem 0 8px"><i class="fa fa-link"></i> Cross-Agent Insights</div>', unsafe_allow_html=True)
            insights = [
                ("Nova + Ops", "fa-calendar-check", "var(--blue)", "Scheduling opportunities identified by Nova can be directly linked to workflow automations from Ops — enabling hands-free calendar management."),
                ("Ledger + Herald", "fa-file-invoice-dollar", "var(--green)", "Ledger's overdue invoice alerts feed directly into Herald's communication drafts — automated payment chase emails ready to send."),
                ("Oracle + Nova", "fa-magnifying-glass-chart", "var(--cyan)", "Oracle's market intelligence can inform Nova's calendar priorities — schedule strategy sessions when key insights arrive."),
            ]
            for title, icon, color, insight in insights:
                if all(k in st.session_state.results for k in title.lower().split(" + ")):
                    st.markdown(f"""
                    <div class="finding-card" style="border-left-color:{color}">
                      <div class="finding-title"><i class="fa {icon}" style="color:{color};margin-right:6px"></i>{title}</div>
                      <div class="finding-detail">{insight}</div>
                    </div>""", unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="aria-footer">
  <div class="footer-brand">◎ ARIA — Autonomous Resources & Intelligence Assistant</div>
  <div class="footer-note"><i class="fa fa-lock"></i> Your data is never stored &nbsp;·&nbsp; Free · Groq LLaMA · 5 Specialist Agents</div>
</div>
""", unsafe_allow_html=True)