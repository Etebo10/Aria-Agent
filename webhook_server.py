"""
ARIA — Webhook Server for Automation Triggers
Handles external triggers for automations
"""

from flask import Flask, request, jsonify
import json
import os
from tools import WebhookHandler, AutomationExecutor

app = Flask(__name__)

# Initialize webhook handler
executor = AutomationExecutor()
webhook_handler = WebhookHandler(executor)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "ARIA Webhook Server"})

@app.route('/webhook/<automation_id>', methods=['POST'])
def handle_webhook(automation_id):
    """Handle webhook triggers for automations"""
    try:
        webhook_data = request.get_json() or {}
        result = webhook_handler.handle_webhook(webhook_data, automation_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/trigger/email', methods=['POST'])
def handle_email_trigger():
    """Handle email-based triggers"""
    try:
        email_data = request.get_json()
        # This would integrate with email providers like SendGrid, Mailgun, etc.
        # For now, simulate trigger
        executor.check_triggers()
        return jsonify({"status": "processed", "message": "Email trigger checked"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/trigger/calendar', methods=['POST'])
def handle_calendar_trigger():
    """Handle calendar-based triggers"""
    try:
        calendar_data = request.get_json()
        # This would integrate with Google Calendar webhooks
        return jsonify({"status": "processed", "message": "Calendar trigger processed"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/automations', methods=['GET'])
def list_automations():
    """List all running automations"""
    automations = list(executor.running_automations.keys())
    return jsonify({"automations": automations})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)