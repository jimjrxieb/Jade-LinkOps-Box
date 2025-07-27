#!/usr/bin/env python3
"""
ZRS Email Sender - Property Management Notifications
=====================================================

Handles sending formatted emails for late notices, maintenance requests, and other property management communications.
"""

import argparse
import json
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ZRSEmailSender:
    """ZRS Property Management Email System"""
    
    def __init__(self):
        """Initialize email sender with ZRS configuration"""
        self.smtp_server = "localhost"  # Use local SMTP for offline mode
        self.smtp_port = 1025  # Local development SMTP port
        self.from_email = "management@zrs-properties.com"
        self.from_name = "ZRS Property Management"
        
    def get_template(self, template_name: str) -> dict:
        """Get email template configuration"""
        templates = {
            "late_notice": {
                "subject": "IMPORTANT: Late Rent Notice - Unit {unit}",
                "body": """Dear {tenant},

This is an official notice that your rent payment for Unit {unit} is OVERDUE.

Amount Due: ${amount}
Days Late: {days} days
Late Fee: $50.00
Total Amount Due: ${total_amount}

Please remit payment immediately to avoid further action. 

If payment is not received within 3 days, we will begin legal proceedings as allowed by your lease agreement and state law.

Contact our office immediately if you need to discuss payment arrangements.

ZRS Property Management
Phone: (555) 123-4567
Email: management@zrs-properties.com

This notice is served in accordance with state tenant law.""",
                "priority": "high"
            },
            
            "maintenance_request": {
                "subject": "Maintenance Request - Unit {unit} - {priority} Priority",
                "body": """ZRS Maintenance Team,

New maintenance request received:

Unit: {unit}
Issue: {issue}
Priority: {priority}
Contact: {contact}
Reported: {timestamp}

Please respond according to our {priority} priority protocols.

{priority_instructions}

ZRS Property Management System""",
                "priority": "normal"
            }
        }
        
        return templates.get(template_name, {})
    
    def format_email(self, template_name: str, **kwargs) -> dict:
        """Format email with template and variables"""
        template = self.get_template(template_name)
        
        if not template:
            raise ValueError(f"Unknown template: {template_name}")
        
        # Calculate additional fields
        if template_name == "late_notice":
            kwargs['total_amount'] = float(kwargs.get('amount', 0)) + 50  # Add $50 late fee
        
        if template_name == "maintenance_request":
            kwargs['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            priority_instructions = {
                "emergency": "IMMEDIATE RESPONSE REQUIRED - Contact on-call technician",
                "high": "Response required within 4 hours",
                "medium": "Response required within 24 hours", 
                "low": "Response required within 72 hours"
            }
            kwargs['priority_instructions'] = priority_instructions.get(kwargs.get('priority', 'medium'), '')
        
        # Format subject and body
        subject = template['subject'].format(**kwargs)
        body = template['body'].format(**kwargs)
        
        return {
            "subject": subject,
            "body": body,
            "priority": template['priority']
        }
    
    def send_email(self, to_email: str, subject: str, body: str, priority: str = "normal") -> dict:
        """Send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add priority header
            if priority == "high":
                msg['X-Priority'] = "1"
                msg['X-MSMail-Priority'] = "High"
            
            # Attach body
            msg.attach(MIMEText(body, 'plain'))
            
            # For offline demo mode, just log the email instead of sending
            logger.info(f"📧 EMAIL SENT (DEMO MODE)")
            logger.info(f"To: {to_email}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Priority: {priority}")
            logger.info("=" * 50)
            
            # Return success response
            return {
                "status": "sent",
                "email_sent": True,
                "timestamp": datetime.now().isoformat(),
                "recipient_email": to_email,
                "message_id": f"zrs-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {
                "status": "failed",
                "email_sent": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_tenant_email(self, unit: str, tenant: str) -> str:
        """Get tenant email address (demo data)"""
        # In real implementation, this would query the tenant database
        tenant_emails = {
            "John Wick": "john.wick@email.com",
            "Bruce Banner": "bruce.banner@email.com", 
            "Tony Stark": "tony.stark@email.com",
            "Peter Parker": "peter.parker@email.com",
            "Diana Prince": "diana.prince@email.com",
            "Clark Kent": "clark.kent@email.com",
            "Natasha Romanoff": "natasha.romanoff@email.com"
        }
        
        return tenant_emails.get(tenant, f"tenant.{unit}@zrs-properties.com")
    
    def get_maintenance_email(self, priority: str) -> str:
        """Get maintenance team email based on priority"""
        maintenance_emails = {
            "emergency": "emergency@zrs-maintenance.com",
            "high": "urgent@zrs-maintenance.com", 
            "medium": "maintenance@zrs-maintenance.com",
            "low": "maintenance@zrs-maintenance.com"
        }
        
        return maintenance_emails.get(priority, "maintenance@zrs-maintenance.com")

def main():
    """Command line interface for ZRS email sender"""
    parser = argparse.ArgumentParser(description="ZRS Property Management Email Sender")
    parser.add_argument("--template", required=True, choices=["late_notice", "maintenance_request"],
                       help="Email template to use")
    parser.add_argument("--tenant", help="Tenant name")
    parser.add_argument("--unit", required=True, help="Unit number")
    parser.add_argument("--amount", type=float, help="Amount due (for late notices)")
    parser.add_argument("--days", type=int, help="Days late (for late notices)")
    parser.add_argument("--issue", help="Maintenance issue description")
    parser.add_argument("--priority", choices=["low", "medium", "high", "emergency"], 
                       default="medium", help="Priority level")
    parser.add_argument("--contact", help="Tenant contact info")
    
    args = parser.parse_args()
    
    # Initialize email sender
    sender = ZRSEmailSender()
    
    try:
        if args.template == "late_notice":
            if not all([args.tenant, args.amount, args.days]):
                print("Error: late_notice requires --tenant, --amount, and --days")
                sys.exit(1)
            
            # Format email
            email_data = sender.format_email(
                template_name="late_notice",
                tenant=args.tenant,
                unit=args.unit,
                amount=args.amount,
                days=args.days
            )
            
            # Send to tenant
            recipient = sender.get_tenant_email(args.unit, args.tenant)
            result = sender.send_email(
                to_email=recipient,
                subject=email_data["subject"],
                body=email_data["body"],
                priority=email_data["priority"]
            )
            
        elif args.template == "maintenance_request":
            if not args.issue:
                print("Error: maintenance_request requires --issue")
                sys.exit(1)
            
            # Format email
            email_data = sender.format_email(
                template_name="maintenance_request",
                unit=args.unit,
                issue=args.issue,
                priority=args.priority,
                contact=args.contact or "No contact provided"
            )
            
            # Send to maintenance team
            recipient = sender.get_maintenance_email(args.priority)
            result = sender.send_email(
                to_email=recipient,
                subject=email_data["subject"],
                body=email_data["body"],
                priority=email_data["priority"]
            )
        
        # Output result as JSON
        print(json.dumps(result, indent=2))
        
        # Exit with appropriate code
        sys.exit(0 if result["email_sent"] else 1)
        
    except Exception as e:
        error_result = {
            "status": "error",
            "email_sent": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()