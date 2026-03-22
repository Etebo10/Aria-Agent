#!/usr/bin/env python3
"""
ARIA Automation Test Script
Demonstrates real automation execution
"""

import json
from agents import create_automation, execute_automation
from tools import start_automation_engine

def test_automation_execution():
    """Test creating and executing a real automation"""

    # Mock API key (replace with real one)
    api_key = "your-groq-api-key-here"

    # Create a simple automation
    prompt = "When I receive an email from a client, create a task in my to-do list and send a thank you reply"

    print("🤖 Creating automation...")
    automation = create_automation(prompt, api_key)

    print(f"✅ Created: {automation.get('automation_name')}")
    print(f"📋 Description: {automation.get('description')}")
    print(f"🛠️ Tools: {automation.get('tools_required')}")

    # Execute the automation (will use mock implementations)
    print("\n⚡ Executing automation...")
    result = execute_automation(automation)

    print(f"🎯 Success: {result['success']}")
    print(f"📊 Steps executed: {len(result.get('steps_executed', []))}")

    if result.get('errors'):
        print(f"❌ Errors: {result['errors']}")

    return result

def test_scheduled_automation():
    """Test scheduling an automation"""

    # Mock API key
    api_key = "your-groq-api-key-here"

    # Create a scheduled automation
    prompt = "Every Monday at 8am, send me a summary of my tasks"

    print("📅 Creating scheduled automation...")
    automation = create_automation(prompt, api_key)

    # Start the scheduler
    print("🚀 Starting automation engine...")
    executor = start_automation_engine()

    print(f"✅ Automation engine running with {len(executor.running_automations)} automations")

    return automation

if __name__ == "__main__":
    print("🎪 ARIA Automation Test Suite")
    print("=" * 40)

    # Test immediate execution
    print("\n1. Testing Immediate Execution")
    print("-" * 30)
    test_automation_execution()

    # Test scheduling
    print("\n2. Testing Scheduled Automation")
    print("-" * 30)
    test_scheduled_automation()

    print("\n🎉 Test complete! Check the output above for results.")
    print("\n💡 To use real integrations:")
    print("   1. Set up API credentials in config.json")
    print("   2. Run: streamlit run app.py")
    print("   3. Go to Automation Studio tab")
    print("   4. Create and execute real automations!")