#!/usr/bin/env python3
"""
NVDA Stock Price Monitor Agent
Checks NVIDIA stock price every hour and sends SMS notifications
"""

import os
import sys
import time
import argparse
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
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.your_phone_number = os.getenv("YOUR_PHONE_NUMBER")
        
        # Validate Twilio credentials
        if not all([self.twilio_account_sid, self.twilio_auth_token, 
                   self.twilio_phone_number, self.your_phone_number]):
            raise ValueError(
                "Missing Twilio credentials. Please check your .env file.\n"
                "Required: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, "
                "TWILIO_PHONE_NUMBER, YOUR_PHONE_NUMBER"
            )
        
        self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
    
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
    
    def format_message(self, stock_data):
        """Format stock data into SMS message"""
        if not stock_data:
            return "Error: Could not fetch NVDA stock price."
        
        price = stock_data['current_price']
        prev_close = stock_data['previous_close']
        change = stock_data['day_change']
        change_pct = stock_data['day_change_percent']
        timestamp = stock_data['timestamp']
        
        # Determine if price went up or down
        if isinstance(change, (int, float)):
            direction = "📈" if change >= 0 else "📉"
        else:
            direction = "📊"
        
        message = f"""NVDA Stock Update {direction}

Price: ${price:.2f}
Previous Close: ${prev_close:.2f}
Change: ${change:.2f} ({change_pct})

Time: {timestamp}"""
        
        return message
    
    def send_sms(self, message):
        """Send SMS via Twilio"""
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
    
    def check_and_notify(self):
        """Check stock price and send notification"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking {self.stock_symbol} stock price...")
        
        stock_data = self.get_stock_price()
        
        if stock_data:
            message = self.format_message(stock_data)
            print(f"Current price: ${stock_data['current_price']:.2f}")
            self.send_sms(message)
        else:
            error_msg = f"Error: Could not fetch {self.stock_symbol} stock price at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            print(error_msg)
            self.send_sms(error_msg)
    
    def run_minutely(self):
        """Run the agent, checking stock price every hour"""
        print(f"NVDA Stock Agent started. Checking every hour...")
        print(f"Press Ctrl+C to stop.\n")
        
        # Run immediately on start
        self.check_and_notify()
        
        # Then run every hour
        while True:
            try:
                time.sleep(10)  # Wait 10 seconds
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
            agent.run_minutely()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("\nPlease set up your .env file with the required credentials.")
        sys.exit(1)
    except Exception as e:
        print(f"Fatal Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

