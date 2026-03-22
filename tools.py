"""
ARIA — Tool Integrations for Real Automation
Connects to real business tools and executes automations
"""

import os
import json
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from datetime import datetime, timedelta
import time
import schedule
from typing import Dict, List, Any, Optional
import threading
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pickle
import base64

# ─────────────────────────────────────────────────────────────────
# GMAIL INTEGRATION
# ─────────────────────────────────────────────────────────────────
class GmailTool:
    def __init__(self, credentials_path: str = None):
        self.credentials_path = credentials_path or "gmail_credentials.json"
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993

    def send_email(self, to: str, subject: str, body: str, from_email: str = None) -> bool:
        """Send an email via Gmail SMTP"""
        try:
            # Load credentials
            with open(self.credentials_path, 'r') as f:
                creds = json.load(f)

            from_email = from_email or creds['email']
            password = creds['app_password']  # App-specific password

            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'html'))

            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(from_email, password)
            text = msg.as_string()
            server.sendmail(from_email, to, text)
            server.quit()

            return True
        except Exception as e:
            print(f"Gmail send error: {e}")
            return False

    def check_new_emails(self, since_minutes: int = 5) -> List[Dict]:
        """Check for new emails in the last X minutes"""
        try:
            with open(self.credentials_path, 'r') as f:
                creds = json.load(f)

            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(creds['email'], creds['app_password'])
            mail.select('inbox')

            # Search for emails since X minutes ago
            since_time = (datetime.now() - timedelta(minutes=since_minutes)).strftime("%d-%b-%Y")
            status, messages = mail.search(None, f'SINCE {since_time}')

            emails = []
            if status == 'OK':
                for msg_id in messages[0].split():
                    status, msg_data = mail.fetch(msg_id, '(RFC822)')
                    if status == 'OK':
                        raw_email = msg_data[0][1]
                        email_message = email.message_from_bytes(raw_email)

                        emails.append({
                            'subject': email_message['Subject'],
                            'from': email_message['From'],
                            'to': email_message['To'],
                            'date': email_message['Date'],
                            'body': self._get_email_body(email_message)
                        })

            mail.logout()
            return emails
        except Exception as e:
            print(f"Gmail check error: {e}")
            return []

    def _get_email_body(self, email_message) -> str:
        """Extract email body from email message"""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode()
                elif part.get_content_type() == "text/html":
                    return part.get_payload(decode=True).decode()
        else:
            return email_message.get_payload(decode=True).decode()
        return ""

# ─────────────────────────────────────────────────────────────────
# GOOGLE SHEETS INTEGRATION
# ─────────────────────────────────────────────────────────────────
class GoogleSheetsTool:
    def __init__(self, credentials_path: str = None):
        self.credentials_path = credentials_path or "google_credentials.json"
        self.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.gc = None

    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        if self.gc is None:
            creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_path, self.scope)
            self.gc = gspread.authorize(creds)

    def read_sheet(self, spreadsheet_id: str, sheet_name: str = "Sheet1", range_notation: str = None) -> List[List]:
        """Read data from Google Sheet"""
        try:
            self._authenticate()
            sheet = self.gc.open_by_key(spreadsheet_id).worksheet(sheet_name)
            if range_notation:
                return sheet.get(range_notation)
            else:
                return sheet.get_all_values()
        except Exception as e:
            print(f"Sheets read error: {e}")
            return []

    def write_sheet(self, spreadsheet_id: str, sheet_name: str, data: List[List], start_cell: str = "A1"):
        """Write data to Google Sheet"""
        try:
            self._authenticate()
            sheet = self.gc.open_by_key(spreadsheet_id).worksheet(sheet_name)
            sheet.update(start_cell, data)
            return True
        except Exception as e:
            print(f"Sheets write error: {e}")
            return False

    def append_row(self, spreadsheet_id: str, sheet_name: str, row_data: List):
        """Append a row to Google Sheet"""
        try:
            self._authenticate()
            sheet = self.gc.open_by_key(spreadsheet_id).worksheet(sheet_name)
            sheet.append_row(row_data)
            return True
        except Exception as e:
            print(f"Sheets append error: {e}")
            return False

# ─────────────────────────────────────────────────────────────────
# GOOGLE CALENDAR INTEGRATION
# ─────────────────────────────────────────────────────────────────
class GoogleCalendarTool:
    def __init__(self, credentials_path: str = None):
        self.credentials_path = credentials_path or "google_credentials.json"
        self.api_key = None
        self.calendar_id = None

    def create_event(self, summary: str, start_time: datetime, end_time: datetime,
                    description: str = "", location: str = "") -> bool:
        """Create a calendar event"""
        try:
            # This would need Google Calendar API integration
            # For now, return mock success
            print(f"Calendar: Created event '{summary}' from {start_time} to {end_time}")
            return True
        except Exception as e:
            print(f"Calendar create error: {e}")
            return False

    def get_upcoming_events(self, days_ahead: int = 7) -> List[Dict]:
        """Get upcoming calendar events"""
        try:
            # Mock implementation
            return [
                {
                    'summary': 'Mock Meeting',
                    'start': datetime.now() + timedelta(hours=2),
                    'end': datetime.now() + timedelta(hours=3),
                    'description': 'Mock calendar event'
                }
            ]
        except Exception as e:
            print(f"Calendar get events error: {e}")
            return []

# ─────────────────────────────────────────────────────────────────
# TASK MANAGEMENT INTEGRATION
# ─────────────────────────────────────────────────────────────────
class TaskTool:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("TODOIST_API_KEY")

    def create_task(self, content: str, due_date: str = None, priority: int = 1) -> bool:
        """Create a task in task management system"""
        try:
            # Mock Todoist API call
            print(f"Task: Created '{content}' with priority {priority}")
            return True
        except Exception as e:
            print(f"Task create error: {e}")
            return False

    def get_tasks(self, filter_str: str = None) -> List[Dict]:
        """Get tasks from task management system"""
        try:
            # Mock implementation
            return [
                {'content': 'Mock task', 'due': None, 'priority': 1, 'completed': False}
            ]
        except Exception as e:
            print(f"Task get error: {e}")
            return []

# ─────────────────────────────────────────────────────────────────
# AUTOMATION EXECUTOR
# ─────────────────────────────────────────────────────────────────
class AutomationExecutor:
    def __init__(self):
        self.tools = {
            'gmail': GmailTool(),
            'sheets': GoogleSheetsTool(),
            'calendar': GoogleCalendarTool(),
            'tasks': TaskTool()
        }
        self.running_automations = {}
        self.scheduler_thread = None

    def execute_automation(self, automation: Dict) -> Dict:
        """Execute a single automation"""
        results = {
            'automation_name': automation.get('automation_name'),
            'executed_at': datetime.now().isoformat(),
            'steps_executed': [],
            'success': True,
            'errors': []
        }

        try:
            steps = automation.get('steps', [])
            for step in steps:
                step_result = self._execute_step(step, automation)
                results['steps_executed'].append(step_result)

                if not step_result['success']:
                    results['success'] = False
                    results['errors'].append(step_result['error'])

                # Handle delays between steps
                delay = step.get('delay', 'immediate')
                if delay != 'immediate':
                    if 'minutes' in delay:
                        time.sleep(int(delay.split()[0]) * 60)
                    elif 'hours' in delay:
                        time.sleep(int(delay.split()[0]) * 3600)

        except Exception as e:
            results['success'] = False
            results['errors'].append(str(e))

        return results

    def _execute_step(self, step: Dict, automation: Dict) -> Dict:
        """Execute a single step in an automation"""
        action = step.get('action', '').lower()
        tool = step.get('tool', '').lower()
        details = step.get('details', {})

        result = {
            'step': step.get('step'),
            'action': action,
            'tool': tool,
            'success': False,
            'output': None,
            'error': None
        }

        try:
            if 'email' in action and 'send' in action:
                if tool == 'gmail':
                    success = self.tools['gmail'].send_email(
                        to=details.get('to'),
                        subject=details.get('subject'),
                        body=details.get('body')
                    )
                    result['success'] = success

            elif 'task' in action and 'create' in action:
                if tool == 'tasks':
                    success = self.tools['tasks'].create_task(
                        content=details.get('content'),
                        due_date=details.get('due_date'),
                        priority=details.get('priority', 1)
                    )
                    result['success'] = success

            elif 'sheet' in action or 'spreadsheet' in action:
                if tool == 'sheets':
                    if 'append' in action:
                        success = self.tools['sheets'].append_row(
                            spreadsheet_id=details.get('spreadsheet_id'),
                            sheet_name=details.get('sheet_name', 'Sheet1'),
                            row_data=details.get('row_data', [])
                        )
                        result['success'] = success
                    elif 'write' in action:
                        success = self.tools['sheets'].write_sheet(
                            spreadsheet_id=details.get('spreadsheet_id'),
                            sheet_name=details.get('sheet_name', 'Sheet1'),
                            data=details.get('data', []),
                            start_cell=details.get('start_cell', 'A1')
                        )
                        result['success'] = success

            elif 'calendar' in action or 'event' in action:
                if tool == 'calendar':
                    success = self.tools['calendar'].create_event(
                        summary=details.get('summary'),
                        start_time=datetime.fromisoformat(details.get('start_time')),
                        end_time=datetime.fromisoformat(details.get('end_time')),
                        description=details.get('description'),
                        location=details.get('location')
                    )
                    result['success'] = success

            else:
                result['error'] = f"Unsupported action: {action} with tool: {tool}"

        except Exception as e:
            result['error'] = str(e)

        return result

    def schedule_automation(self, automation: Dict, schedule_time: str):
        """Schedule an automation to run at specific times"""
        automation_id = f"{automation['automation_name']}_{datetime.now().timestamp()}"

        if schedule_time.startswith('every'):
            # Handle recurring schedules like "every monday at 8am"
            if 'monday' in schedule_time.lower():
                schedule.every().monday.at("08:00").do(self._run_scheduled_automation, automation, automation_id)
            elif 'daily' in schedule_time.lower():
                schedule.every().day.at("08:00").do(self._run_scheduled_automation, automation, automation_id)
        else:
            # Handle one-time schedules
            # This would need more sophisticated parsing
            pass

        self.running_automations[automation_id] = automation
        return automation_id

    def _run_scheduled_automation(self, automation: Dict, automation_id: str):
        """Run a scheduled automation"""
        result = self.execute_automation(automation)
        print(f"Scheduled automation {automation_id} executed: {result['success']}")

    def start_scheduler(self):
        """Start the automation scheduler in a background thread"""
        if self.scheduler_thread is None:
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()

    def _scheduler_loop(self):
        """Main scheduler loop"""
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def check_triggers(self):
        """Check for trigger events (emails, webhooks, etc.)"""
        # Check for new emails
        new_emails = self.tools['gmail'].check_new_emails(since_minutes=5)

        for email_data in new_emails:
            # Check if any automation should trigger on this email
            for automation_id, automation in self.running_automations.items():
                trigger = automation.get('trigger', {})
                if trigger.get('event', '').lower().startswith('new email'):
                    # Check conditions
                    condition = trigger.get('condition', '').lower()
                    if not condition or condition in email_data.get('subject', '').lower():
                        # Trigger automation
                        self.execute_automation(automation)

# ─────────────────────────────────────────────────────────────────
# WEBHOOK ENDPOINTS (for external triggers)
# ─────────────────────────────────────────────────────────────────
class WebhookHandler:
    def __init__(self, executor: AutomationExecutor):
        self.executor = executor

    def handle_webhook(self, webhook_data: Dict, automation_id: str) -> Dict:
        """Handle incoming webhook and trigger automation"""
        if automation_id in self.executor.running_automations:
            automation = self.executor.running_automations[automation_id]
            result = self.executor.execute_automation(automation)
            return {'status': 'executed', 'result': result}
        else:
            return {'status': 'error', 'message': 'Automation not found'}

# Global executor instance
executor = AutomationExecutor()

def execute_automation_now(automation: Dict) -> Dict:
    """Execute an automation immediately"""
    return executor.execute_automation(automation)

def schedule_automation(automation: Dict, schedule_time: str) -> str:
    """Schedule an automation"""
    return executor.schedule_automation(automation, schedule_time)

def start_automation_engine():
    """Start the automation engine"""
    executor.start_scheduler()
    return executor

def check_automation_triggers():
    """Check for automation triggers"""
    executor.check_triggers()