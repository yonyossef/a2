#!/usr/bin/env python3
"""
NVDA Stock Price Monitor Agent
Checks NVIDIA stock price every hour and sends SMS/Email notifications
"""

import os
import sys
import time
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yfinance as yf
from datetime import datetime
from twilio.rest import Client
from dotenv import load_dotenv

# Try to import SendGrid (optional)
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

# Load environment variables
load_dotenv()

class NVDAStockAgent:
    def __init__(self):
        """Initialize the stock monitoring agent"""
        self.stock_symbol = "NVDA"
        
        # Notification flags (default to False if not set)
        sms_notify_env = os.getenv("SMS_NOTIFY_ENABLE", "False").strip().lower()
        email_notify_env = os.getenv("EMAIL_NOTIFY_ENABLE", "False").strip().lower()
        
        self.sms_notify_enable = sms_notify_env in ("true", "1", "yes", "on")
        self.email_notify_enable = email_notify_env in ("true", "1", "yes", "on")
        
        # Debug output (can be removed in production)
        print(f"DEBUG: SMS_NOTIFY_ENABLE='{sms_notify_env}' -> {self.sms_notify_enable}")
        print(f"DEBUG: EMAIL_NOTIFY_ENABLE='{email_notify_env}' -> {self.email_notify_enable}")
        
        # Validate at least one notification method is enabled
        if not self.sms_notify_enable and not self.email_notify_enable:
            raise ValueError(
                "At least one notification method must be enabled.\n"
                "Set SMS_NOTIFY_ENABLE=True and/or EMAIL_NOTIFY_ENABLE=True in your .env file."
            )
        
        # SMS/Twilio configuration (only if SMS is enabled)
        self.twilio_client = None
        if self.sms_notify_enable:
            self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
            self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
            self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
            self.your_phone_number = os.getenv("YOUR_PHONE_NUMBER")
            
            # Validate Twilio credentials
            if not all([self.twilio_account_sid, self.twilio_auth_token, 
                       self.twilio_phone_number, self.your_phone_number]):
                raise ValueError(
                    "SMS notifications enabled but missing Twilio credentials.\n"
                    "Required: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, "
                    "TWILIO_PHONE_NUMBER, YOUR_PHONE_NUMBER"
                )
            
            self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
        
        # Email configuration (only if email is enabled)
        if self.email_notify_enable:
            # Check for SendGrid API key first (preferred for cloud platforms)
            self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
            
            print(f"DEBUG: SENDGRID_API_KEY present: {bool(self.sendgrid_api_key)}")
            
            if self.sendgrid_api_key:
                # Using SendGrid API
                self.email_from = os.getenv("EMAIL_FROM", os.getenv("EMAIL_USERNAME", "noreply@example.com"))
                self.email_to = os.getenv("EMAIL_TO")
                
                if not self.email_to:
                    raise ValueError(
                        "Email notifications enabled with SendGrid but missing EMAIL_TO.\n"
                        "Required: SENDGRID_API_KEY, EMAIL_TO"
                    )
                
                if SENDGRID_AVAILABLE:
                    self.sendgrid_client = SendGridAPIClient(self.sendgrid_api_key)
                else:
                    raise ValueError(
                        "SendGrid API key provided but sendgrid package not installed.\n"
                        "Run: pip install sendgrid"
                    )
            else:
                # Fallback to SMTP
                self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
                self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
                self.email_username = os.getenv("EMAIL_USERNAME")
                self.email_password = os.getenv("EMAIL_PASSWORD")
                self.email_to = os.getenv("EMAIL_TO")
                self.sendgrid_client = None
                
                # Validate SMTP credentials
                if not all([self.email_username, self.email_password, self.email_to]):
                    raise ValueError(
                        "Email notifications enabled but missing email credentials.\n"
                        "Required: SENDGRID_API_KEY (preferred) OR (EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_TO)"
                    )
        
        # Print notification configuration
        enabled_methods = []
        if self.sms_notify_enable:
            enabled_methods.append("SMS")
        if self.email_notify_enable:
            enabled_methods.append("Email")
        print(f"Notification methods enabled: {', '.join(enabled_methods)}")
    
    def get_stock_price(self):
        """Fetch current stock price for NVDA"""
        try:
            ticker = yf.Ticker(self.stock_symbol)
            info = ticker.info
            
            # Get current price
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            
            # Get additional info for context
            previous_close = info.get('previousClose', 'N/A')
            day_change = info.get('regularMarketChange', 'N/A')
            day_change_percent = info.get('regularMarketChangePercent', 'N/A')
            
            # Format change percentage
            if isinstance(day_change_percent, float):
                day_change_percent = f"{day_change_percent:.2f}%"
            
            return {
                'symbol': self.stock_symbol,
                'current_price': current_price,
                'previous_close': previous_close,
                'day_change': day_change,
                'day_change_percent': day_change_percent,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            print(f"Error fetching stock price: {e}")
            return None
    
    def format_message(self, stock_data, format_type="text"):
        """Format stock data into message (text for SMS, HTML for email)"""
        if not stock_data:
            if format_type == "html":
                return "<p>Error: Could not fetch NVDA stock price.</p>"
            return "Error: Could not fetch NVDA stock price."
        
        price = stock_data['current_price']
        prev_close = stock_data['previous_close']
        change = stock_data['day_change']
        change_pct = stock_data['day_change_percent']
        timestamp = stock_data['timestamp']
        
        # Determine if price went up or down
        if isinstance(change, (int, float)):
            direction = "📈" if change >= 0 else "📉"
            change_color = "#00ff00" if change >= 0 else "#ff0000"
        else:
            direction = "📊"
            change_color = "#000000"
        
        if format_type == "html":
            return f"""
            <html>
                <body>
                    <h2>NVDA Stock Update {direction}</h2>
                    <p><strong>Price:</strong> ${price:.2f}</p>
                    <p><strong>Previous Close:</strong> ${prev_close:.2f}</p>
                    <p><strong>Change:</strong> <span style="color: {change_color};">${change:.2f} ({change_pct})</span></p>
                    <p><strong>Time:</strong> {timestamp}</p>
                </body>
            </html>
            """
        else:
            return f"""NVDA Stock Update {direction}

Price: ${price:.2f}
Previous Close: ${prev_close:.2f}
Change: ${change:.2f} ({change_pct})

Time: {timestamp}"""
    
    def send_sms(self, message):
        """Send SMS via Twilio"""
        if not self.sms_notify_enable:
            return False
        
        # Safety check: don't try to send if Twilio client wasn't initialized
        if self.twilio_client is None:
            print("Warning: SMS enabled but Twilio client not initialized. Skipping SMS.")
            return False
        
        try:
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_phone_number,
                to=self.your_phone_number
            )
            print(f"SMS sent successfully! SID: {message_obj.sid}")
            return True
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False
    
    def send_email(self, subject, message_text, message_html=None):
        """Send email notification using SendGrid API or SMTP"""
        if not self.email_notify_enable:
            return False
        
        # Use SendGrid API if available (preferred for cloud platforms)
        if hasattr(self, 'sendgrid_client') and self.sendgrid_client is not None:
            try:
                message = Mail(
                    from_email=self.email_from,
                    to_emails=self.email_to,
                    subject=subject,
                    plain_text_content=message_text,
                    html_content=message_html if message_html else None
                )
                
                response = self.sendgrid_client.send(message)
                print(f"Email sent successfully via SendGrid to {self.email_to} (Status: {response.status_code})")
                return True
            except Exception as e:
                error_msg = str(e)
                print(f"Error sending email via SendGrid: {error_msg}")
                
                # Provide helpful error messages
                if "403" in error_msg or "Forbidden" in error_msg:
                    print("\n⚠️  SendGrid 403 Forbidden - Common causes:")
                    print("  1. Sender email not verified in SendGrid")
                    print("     → Go to https://app.sendgrid.com/settings/sender_auth/senders")
                    print("     → Verify your sender email address")
                    print("  2. API key doesn't have 'Mail Send' permissions")
                    print("     → Check API key permissions at https://app.sendgrid.com/settings/api_keys")
                    print(f"  3. Current sender: {self.email_from}")
                
                return False
        
        # Fallback to SMTP
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.email_username
        msg['To'] = self.email_to
        
        # Add text and HTML parts
        text_part = MIMEText(message_text, 'plain')
        msg.attach(text_part)
        
        if message_html:
            html_part = MIMEText(message_html, 'html')
            msg.attach(html_part)
        
        # Try multiple SMTP configurations (some cloud platforms block certain ports)
        smtp_configs = [
            (self.smtp_server, self.smtp_port, 'tls'),  # Standard TLS
            (self.smtp_server, 465, 'ssl'),  # SSL on port 465
            (self.smtp_server, 25, 'tls'),  # Fallback port 25
        ]
        
        last_error = None
        for smtp_host, smtp_port, connection_type in smtp_configs:
            try:
                print(f"Attempting to send email via {smtp_host}:{smtp_port} ({connection_type})...")
                
                if connection_type == 'ssl':
                    # Use SSL connection
                    server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30)
                else:
                    # Use TLS connection
                    server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
                    server.starttls()
                
                server.login(self.email_username, self.email_password)
                server.send_message(msg)
                server.quit()
                
                print(f"Email sent successfully to {self.email_to}")
                return True
                
            except (smtplib.SMTPException, OSError, ConnectionError) as e:
                last_error = e
                print(f"Failed to send via {smtp_host}:{smtp_port} - {e}")
                continue
            except Exception as e:
                last_error = e
                print(f"Unexpected error with {smtp_host}:{smtp_port} - {e}")
                continue
        
        # If all attempts failed
        print(f"Error: All email sending attempts failed. Last error: {last_error}")
        print("Note: Railway may block outbound SMTP connections. Consider using SendGrid API:")
        print("  - Set SENDGRID_API_KEY environment variable")
        print("  - Get API key from https://app.sendgrid.com/settings/api_keys")
        return False
    
    def check_and_notify(self):
        """Check stock price and send notifications"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking {self.stock_symbol} stock price...")
        
        stock_data = self.get_stock_price()
        
        if stock_data:
            print(f"Current price: ${stock_data['current_price']:.2f}")
            
            # Format messages
            text_message = self.format_message(stock_data, format_type="text")
            html_message = self.format_message(stock_data, format_type="html")
            subject = f"NVDA Stock Update - ${stock_data['current_price']:.2f}"
            
            # Send SMS if enabled
            if self.sms_notify_enable:
                self.send_sms(text_message)
            
            # Send Email if enabled
            if self.email_notify_enable:
                self.send_email(subject, text_message, html_message)
        else:
            error_msg = f"Error: Could not fetch {self.stock_symbol} stock price at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            print(error_msg)
            
            # Send error notifications
            if self.sms_notify_enable:
                self.send_sms(error_msg)
            if self.email_notify_enable:
                self.send_email("NVDA Stock Agent Error", error_msg)
    
    def run_hourly(self):
        """Run the agent, checking stock price every hour"""
        print(f"NVDA Stock Agent started. Checking every hour...")
        print(f"Press Ctrl+C to stop.\n")
        
        # Run immediately on start
        self.check_and_notify()
        
        # Then run every hour
        while True:
            try:
                time.sleep(3600)  # Wait 1 hour (3600 seconds)
                self.check_and_notify()
            except KeyboardInterrupt:
                print("\n\nAgent stopped by user.")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='NVDA Stock Price Monitor Agent')
    parser.add_argument('--once', action='store_true', 
                       help='Run once and exit (useful for cron jobs)')
    args = parser.parse_args()
    
    try:
        agent = NVDAStockAgent()
        if args.once:
            # Run once and exit
            agent.check_and_notify()
        else:
            # Run continuously every hour
            agent.run_hourly()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("\nPlease set up your .env file with the required credentials.")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

