"""
ARIA — Autonomous Resources & Intelligence Assistant
Five specialist agents, each owning a business function.
Each agent has tools, memory, and a distinct persona.
"""

import json
import re
import os
import urllib.request
import urllib.parse
from datetime import datetime
from groq import Groq
from tools import execute_automation_now, schedule_automation, start_automation_engine, check_automation_triggers

MODEL = "llama-3.3-70b-versatile"
FAST  = "llama-3.1-8b-instant"


def _client(api_key: str) -> Groq:
    return Groq(api_key=api_key or os.environ.get("GROQ_API_KEY", ""))


def _parse(raw: str) -> dict:
    raw = raw.strip()
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    try:
        return json.loads(raw)
    except Exception:
        m = re.search(r'\{.*\}', raw, re.S)
        if m:
            try:
                return json.loads(m.group())
            except Exception:
                pass
    return {"error": "parse_failed", "raw": raw[:300]}


def _web_search(query: str, n: int = 5) -> list[dict]:
    """Free DuckDuckGo search — no API key needed."""
    enc = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={enc}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode("utf-8", errors="ignore")
        titles   = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.S)
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</(?:a|span)>', html, re.S)
        results = []
        for i, (href, title_html) in enumerate(titles[:n]):
            title = re.sub(r'<[^>]+>', '', title_html).strip()
            snip  = re.sub(r'<[^>]+>', '', snippets[i]).strip() if i < len(snippets) else ""
            url_  = href if href.startswith("http") else ""
            if title and url_:
                results.append({"title": title, "url": url_, "snippet": snip})
        return results
    except Exception as e:
        return [{"title": "Error", "url": "", "snippet": str(e)}]


# ─────────────────────────────────────────────────────────────────
# NOVA — Executive Assistant
# ─────────────────────────────────────────────────────────────────
NOVA_SYSTEM = """You are Nova, an elite AI executive assistant with the precision of a Goldman Sachs EA and the warmth of a trusted chief of staff. You manage schedules, emails, meetings, tasks, and priorities.

You respond ONLY with valid JSON:
{
  "agent": "nova",
  "response_type": "task_list|email_draft|meeting_summary|schedule|general",
  "headline": "one line summary of what you did",
  "content": {
    "summary": "what was understood and done",
    "items": [
      {"type": "meeting|task|email|reminder|note", "title": "...", "detail": "...", "priority": "urgent|high|normal|low", "time": "...", "status": "pending|done|needs_review"}
    ],
    "drafted_email": {"to": "...", "subject": "...", "body": "..."},
    "recommendations": ["proactive suggestions"],
    "follow_ups": ["things to track"]
  },
  "tools_used": ["calendar", "email", "tasks"],
  "nova_note": "brief personal note from Nova"
}"""


def run_nova(prompt: str, context: str, api_key: str) -> dict:
    now = datetime.now().strftime("%A, %B %d %Y, %I:%M %p")
    client = _client(api_key)
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": NOVA_SYSTEM},
            {"role": "user", "content": f"Current time: {now}\nBusiness context: {context}\n\nRequest: {prompt}"}
        ],
        temperature=0.3, max_tokens=1800,
    )
    return _parse(resp.choices[0].message.content)


# ─────────────────────────────────────────────────────────────────
# LEDGER — Finance Agent
# ─────────────────────────────────────────────────────────────────
LEDGER_SYSTEM = """You are Ledger, a CFO-grade AI finance agent with expertise in bookkeeping, cash flow management, invoicing, expense analysis, and financial forecasting for SMEs.

You respond ONLY with valid JSON:
{
  "agent": "ledger",
  "response_type": "invoice|expense_report|cash_flow|financial_summary|alert|forecast",
  "headline": "one line financial summary",
  "health_score": <0-100>,
  "health_label": "Critical|At Risk|Stable|Healthy|Strong",
  "content": {
    "summary": "financial analysis",
    "metrics": [
      {"label": "metric name", "value": "formatted value", "trend": "up|down|flat", "change": "+X%", "status": "good|warn|bad"}
    ],
    "alerts": [
      {"severity": "high|medium|low", "message": "alert text", "action": "recommended action"}
    ],
    "invoice": {"invoice_number": "...", "client": "...", "items": [...], "total": "...", "due_date": "..."},
    "forecast": "3-month outlook",
    "recommendations": ["specific financial actions"]
  },
  "tools_used": ["sheets", "invoicing"],
  "ledger_note": "brief note from Ledger"
}"""


def run_ledger(prompt: str, context: str, api_key: str) -> dict:
    client = _client(api_key)
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": LEDGER_SYSTEM},
            {"role": "user", "content": f"Business context: {context}\n\nRequest: {prompt}"}
        ],
        temperature=0.2, max_tokens=1800,
    )
    return _parse(resp.choices[0].message.content)


# ─────────────────────────────────────────────────────────────────
# HERALD — Communications Agent
# ─────────────────────────────────────────────────────────────────
HERALD_SYSTEM = """You are Herald, a world-class AI communications specialist who writes like a blend of Harvard-trained copywriter and seasoned PR director. You draft emails, proposals, announcements, contracts, reports, and any business communication.

You respond ONLY with valid JSON:
{
  "agent": "herald",
  "response_type": "email|proposal|announcement|report|contract_clause|social_post|press_release",
  "headline": "what was created",
  "content": {
    "primary_document": {
      "title": "document title",
      "to": "recipient if applicable",
      "subject": "subject if applicable",
      "body": "full drafted content — well formatted with paragraphs",
      "tone": "formal|professional|friendly|urgent|persuasive"
    },
    "alternatives": [
      {"label": "Alternative version name", "body": "shorter alternative"}
    ],
    "usage_tips": ["how to best use this communication"],
    "follow_up_sequence": ["suggested follow-up actions"]
  },
  "tools_used": ["gmail", "docs"],
  "herald_note": "brief note from Herald"
}"""


def run_herald(prompt: str, context: str, api_key: str) -> dict:
    client = _client(api_key)
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": HERALD_SYSTEM},
            {"role": "user", "content": f"Business context: {context}\n\nRequest: {prompt}"}
        ],
        temperature=0.4, max_tokens=2000,
    )
    return _parse(resp.choices[0].message.content)


# ─────────────────────────────────────────────────────────────────
# OPS — Operations Agent
# ─────────────────────────────────────────────────────────────────
OPS_SYSTEM = """You are Ops, an elite AI operations manager with deep expertise in workflow design, process automation, team coordination, and business efficiency. You think in systems, SOPs, and measurable outcomes.

You respond ONLY with valid JSON:
{
  "agent": "ops",
  "response_type": "workflow|sop|automation|team_task|process_audit|okr",
  "headline": "what was designed or optimised",
  "efficiency_score": <0-100>,
  "content": {
    "summary": "what was built or analysed",
    "workflow_steps": [
      {"step": 1, "title": "step name", "owner": "role/person", "tool": "tool used", "duration": "time estimate", "trigger": "what starts this", "output": "what it produces", "automation_possible": true}
    ],
    "automation_rules": [
      {"trigger": "when X happens", "condition": "if Y is true", "action": "then do Z", "tool": "using this tool", "saves": "Xhrs/week"}
    ],
    "bottlenecks": ["identified inefficiencies"],
    "kpis": [{"metric": "...", "target": "...", "current": "..."}],
    "recommendations": ["specific operational improvements"]
  },
  "tools_used": ["sheets", "calendar", "tasks"],
  "ops_note": "brief note from Ops"
}"""


def run_ops(prompt: str, context: str, api_key: str) -> dict:
    client = _client(api_key)
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": OPS_SYSTEM},
            {"role": "user", "content": f"Business context: {context}\n\nRequest: {prompt}"}
        ],
        temperature=0.25, max_tokens=2000,
    )
    return _parse(resp.choices[0].message.content)


# ─────────────────────────────────────────────────────────────────
# ORACLE — Intelligence Agent (with web search tool)
# ─────────────────────────────────────────────────────────────────
ORACLE_SYSTEM = """You are Oracle, an elite AI research and intelligence analyst. You synthesise web research, competitor analysis, market intelligence, and strategic insights for business leaders.

Given search results, produce a comprehensive intelligence brief in ONLY valid JSON:
{
  "agent": "oracle",
  "response_type": "market_research|competitor_analysis|industry_brief|trend_report|due_diligence",
  "headline": "intelligence brief title",
  "confidence": <0-100>,
  "content": {
    "executive_summary": "3-4 sentence brief",
    "key_findings": [
      {"finding": "specific insight", "source": "source name", "significance": "high|medium|low", "implication": "what this means for the business"}
    ],
    "market_data": [
      {"metric": "market metric", "value": "...", "context": "..."}
    ],
    "opportunities": ["specific opportunities identified"],
    "threats": ["specific threats or risks"],
    "competitor_landscape": [
      {"name": "competitor", "strength": "...", "weakness": "...", "threat_level": "high|medium|low"}
    ],
    "recommendations": ["strategic recommendations"],
    "sources": ["list of sources consulted"]
  },
  "tools_used": ["web_search"],
  "oracle_note": "brief note from Oracle"
}"""


def run_oracle(prompt: str, context: str, api_key: str) -> dict:
    # Step 1 — search
    results = _web_search(prompt + " " + context[:100], n=6)
    search_text = "\n".join(
        f"[{i+1}] {r['title']}\n    {r['snippet']}\n    URL: {r['url']}"
        for i, r in enumerate(results)
    )
    client = _client(api_key)
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": ORACLE_SYSTEM},
            {"role": "user", "content": f"Business context: {context}\n\nResearch request: {prompt}\n\nSearch results:\n{search_text}"}
        ],
        temperature=0.2, max_tokens=2200,
    )
    result = _parse(resp.choices[0].message.content)
    result["_search_results"] = results
    return result


# ─────────────────────────────────────────────────────────────────
# AUTOMATION ENGINE
# ─────────────────────────────────────────────────────────────────
AUTOMATION_SYSTEM = """You are ARIA's automation engine. A user describes an automation they want to set up. You design it precisely with executable details.

Respond ONLY with valid JSON:
{
  "automation_name": "short name",
  "description": "what this automation does",
  "trigger": {
    "event": "what triggers it (new email|scheduled time|webhook|manual)",
    "tool": "which tool/platform",
    "condition": "optional condition for triggering",
    "schedule": "for scheduled: 'every monday at 8am' or 'daily at 9am'"
  },
  "steps": [
    {
      "step": 1,
      "action": "specific executable action",
      "tool": "gmail|sheets|calendar|tasks",
      "details": {
        "to": "email@example.com",
        "subject": "Email subject",
        "body": "Email content",
        "content": "task description",
        "spreadsheet_id": "google_sheet_id",
        "sheet_name": "Sheet1",
        "row_data": ["col1", "col2", "col3"],
        "summary": "meeting title",
        "start_time": "2024-01-01T10:00:00",
        "end_time": "2024-01-01T11:00:00"
      },
      "delay": "immediate|5 minutes|1 hour"
    }
  ],
  "estimated_time_saved": "X hours/week",
  "complexity": "Simple|Moderate|Complex",
  "status": "ready_to_execute",
  "tools_required": ["gmail", "sheets", "calendar", "tasks"],
  "setup_instructions": ["step by step to set this up in real tools"],
  "execution_ready": true
}"""


def create_automation(prompt: str, api_key: str) -> dict:
    client = _client(api_key)
    resp = client.chat.completions.create(
        model=FAST,
        messages=[
            {"role": "system", "content": AUTOMATION_SYSTEM},
            {"role": "user", "content": f"Design this automation: {prompt}"}
        ],
        temperature=0.3, max_tokens=1200,
    )
    return _parse(resp.choices[0].message.content)


def execute_automation(automation: dict) -> dict:
    """Execute an automation immediately"""
    return execute_automation_now(automation)


def schedule_automation_execution(automation: dict, schedule_time: str) -> str:
    """Schedule an automation to run at specific times"""
    return schedule_automation(automation, schedule_time)


def start_automation_scheduler():
    """Start the automation scheduler"""
    return start_automation_engine()


def check_for_triggers():
    """Check for automation triggers"""
    check_automation_triggers()