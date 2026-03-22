# ARIA — Autonomous Resources & Intelligence Assistant

A comprehensive business operating system with 5 AI specialist agents and a fully functional automation platform.

## 🎯 Features

### 🤖 Specialist Agents
- **Nova** — Executive Assistant (scheduling, emails, tasks, priorities)
- **Ledger** — Finance Agent (bookkeeping, cash flow, invoicing, forecasting)
- **Herald** — Communications Agent (emails, proposals, reports, contracts)
- **Ops** — Operations Agent (workflows, automation, process optimization)
- **Oracle** — Intelligence Agent (market research, competitor analysis, strategic insights)

### ⚡ Automation Studio (REAL Automations!)
Unlike typical "design-only" tools, ARIA's Automation Studio creates **actually executable** automations that connect to real business tools:

#### Supported Integrations
- **Gmail** — Send emails, check incoming emails, automated responses
- **Google Sheets** — Read/write data, append rows, update spreadsheets
- **Google Calendar** — Create events, check schedules
- **Task Management** — Create tasks, manage to-do lists

#### Automation Types
- **Email Triggers** — "When I receive a client email, create a task and send an acknowledgement"
- **Scheduled Workflows** — "Every Monday at 8am, pull sales data and email a report"
- **Contact Management** — "When a new contact is added, update CRM and send welcome email"
- **Invoice Automation** — "When invoice is overdue, send payment reminder and flag in tracker"

#### Real Execution Features
- **Immediate Execution** — Run automations on-demand with one click
- **Scheduled Automations** — Set recurring workflows (daily, weekly, etc.)
- **Trigger Monitoring** — Automatic checking for email/webhook triggers
- **Execution History** — Track all automation runs with success/failure status
- **Webhook Endpoints** — External service integration via REST API

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys
```bash
# Copy config template
cp config_template.json config.json

# Edit with your API keys
# Required: Groq API key
# Optional: Gmail, Google Sheets, Todoist for automations
```

### 3. Run the Application
```bash
streamlit run app.py
```

### 4. Start Webhook Server (for external triggers)
```bash
python webhook_server.py
```

## 🔧 Configuration

### Required Credentials
- **Groq API Key** — For AI agent responses
- **Gmail App Password** — For email automations
- **Google Service Account** — For Sheets/Calendar integration
- **Todoist API Token** — For task management

### Google Setup
1. **Gmail**: Enable 2FA, generate App Password
2. **Google Sheets/Calendar**: Create Service Account, download credentials JSON
3. **Todoist**: Get API token from developer settings

## 📡 Webhook Integration

The webhook server provides REST endpoints for external triggers:

```bash
# Health check
GET /health

# Trigger automation by ID
POST /webhook/{automation_id}

# Email trigger (from services like SendGrid)
POST /trigger/email

# Calendar trigger
POST /trigger/calendar

# List active automations
GET /automations
```

## 🎨 Interface

- **Agent Console** — Run individual AI agents
- **Automation Studio** — Design and execute real automations
- **Intelligence Hub** — Cross-reference agent outputs

## 🔒 Security

- API keys stored locally (never transmitted)
- No data storage or logging
- All processing happens client-side
- Free and open-source

## 📈 Use Cases

- **Small Business Automation** — Invoice processing, customer follow-ups
- **Sales Team Support** — Lead nurturing, CRM updates
- **Executive Assistance** — Calendar management, email prioritization
- **Operations Optimization** — Workflow automation, reporting
- **Market Intelligence** — Competitor monitoring, trend analysis

---

**Built with Streamlit, Groq LLaMA, and real API integrations**