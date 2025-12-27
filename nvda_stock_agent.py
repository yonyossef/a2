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
            self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
            self.email_username = os.getenv("EMAIL_USERNAME")
            self.email_password = os.getenv("EMAIL_PASSWORD")
            self.email_to = os.getenv("EMAIL_TO")
            
            # Validate email credentials
            if not all([self.email_username, self.email_password, self.email_to]):
                raise ValueError(
                    "Email notifications enabled but missing email credentials.\n"
                    "Required: EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_TO"
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
        """Send email notification"""
        if not self.email_notify_enable:
            return False
        
        try:
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
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_username, self.email_password)
                server.send_message(msg)
            
            print(f"Email sent successfully to {self.email_to}")
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
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

