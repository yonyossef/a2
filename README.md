# NVDA Stock Price Monitor Agent

An AI agent that checks NVIDIA (NVDA) stock price every hour and sends SMS and/or Email notifications.

## Features

- ✅ Fetches real-time NVDA stock price using Yahoo Finance
- ✅ Optional SMS notifications via Twilio
- ✅ Optional Email notifications via SMTP
- ✅ Runs automatically every hour
- ✅ Shows current price, previous close, and daily change
- ✅ Beautiful formatted messages with emojis
- ✅ Flexible notification configuration (enable/disable SMS or Email independently)

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Choose Notification Method(s)

You can enable SMS notifications, Email notifications, or both. At least one must be enabled.

#### Option A: SMS Notifications (via Twilio)

If you want SMS notifications, set `SMS_NOTIFY_ENABLE=True` in your `.env` file and follow the Twilio setup below.

#### Option B: Email Notifications

If you want Email notifications, set `EMAIL_NOTIFY_ENABLE=True` in your `.env` file and follow the Email setup below.

#### Option C: Both

You can enable both by setting both flags to `True` in your `.env` file.

### 2A. Set Up Twilio Account (For SMS)

#### Step 1: Create a Twilio Account

1. Go to https://www.twilio.com/try-twilio
2. Click "Sign up" or "Start Free Trial"
3. Fill out the registration form:
   - Enter your email address
   - Create a password
   - Enter your name
4. Verify your email address (check your inbox)
5. Complete the phone verification (they'll send you a code via SMS)

#### Step 2: Get Your Account Credentials

1. After logging in, you'll be taken to the Twilio Console Dashboard
2. On the dashboard, you'll see your **Account SID** and **Auth Token**
   - **Account SID**: Starts with "AC" (e.g., ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)
   - **Auth Token**: Click the eye icon to reveal it (keep this secret!)
3. Copy both values - you'll need them for your `.env` file

#### Step 3: Get a Twilio Phone Number

1. In the Twilio Console, go to **Phone Numbers** → **Manage** → **Buy a number**
2. Click "Get a number" (free trial accounts get one free number)
3. Select your country and area code
4. Choose a number and click "Buy"
5. Copy the phone number (it will be in E.164 format like +1234567890)

#### Step 4: Verify Your Phone Number (For Trial Accounts)

1. In the Twilio Console, go to **Phone Numbers** → **Verified Caller IDs**
2. Click "Add a new Caller ID"
3. Enter your personal phone number (the one you want to receive SMS on)
4. Twilio will send you a verification code via SMS
5. Enter the code to verify your number

**Important Notes:**
- Free trial accounts can only send SMS to verified phone numbers
- Trial accounts have a credit limit (usually enough for testing)
- Phone numbers must be in E.164 format: `+[country code][number]` (e.g., `+14155551234` for US)

### 2B. Set Up Email (For Email Notifications)

#### For Gmail Users:

1. **Enable 2-Factor Authentication** on your Google account
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification if not already enabled

2. **Generate an App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Enter "NVDA Stock Agent" as the name
   - Click "Generate"
   - Copy the 16-character password (you'll use this as `EMAIL_PASSWORD`)

3. **Use your Gmail address** as `EMAIL_USERNAME`

#### For Other Email Providers:

- **Outlook/Hotmail:** Use `smtp-mail.outlook.com` on port `587`
- **Yahoo:** Use `smtp.mail.yahoo.com` on port `587`
- **Custom SMTP:** Check your email provider's SMTP settings

**Important:** Most email providers require an "App Password" or "Application Password" instead of your regular password for SMTP access.

### 3. Configure Environment Variables

1. Copy the template file to create your `.env` file:
   ```bash
   cp env_template.txt .env
   ```

2. Edit `.env` and configure your notification methods:
   ```bash
   nano .env
   # or use your preferred text editor
   ```

3. **Enable notification methods:**
   ```
   SMS_NOTIFY_ENABLE=False
   EMAIL_NOTIFY_ENABLE=True
   ```

4. **If SMS is enabled, add Twilio credentials:**
   ```
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_PHONE_NUMBER=+1234567890
   YOUR_PHONE_NUMBER=+1234567890
   ```
   
   **Important**: 
   - Phone numbers must be in E.164 format: `+[country code][number]`
   - Example for US: `+14155551234`
   - Example for UK: `+447911123456`
   - No spaces, dashes, or parentheses

5. **If Email is enabled, add email credentials:**
   ```
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   EMAIL_USERNAME=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password_here
   EMAIL_TO=recipient@example.com
   ```
   
   - `EMAIL_USERNAME`: Your email address (sender)
   - `EMAIL_PASSWORD`: App password (not your regular password!)
   - `EMAIL_TO`: Recipient email address (can be the same as EMAIL_USERNAME)
   - `SMTP_SERVER` and `SMTP_PORT`: Defaults to Gmail if not specified

### 4. Run the Agent

```bash
python nvda_stock_agent.py
```

The agent will:
- Check the stock price immediately
- Then check every hour automatically
- Send notifications (SMS and/or Email) each time based on your configuration

Press `Ctrl+C` to stop the agent.

## Hosting Options - Running 24/7

You have several options to run the agent continuously. Choose the one that best fits your needs:

### Option 1: Local Machine (Linux/WSL - systemd) ⭐ Recommended for WSL

If you're running Linux or WSL2 and want to keep it running on your local machine:

#### For WSL2 (Windows Subsystem for Linux):

**Note:** WSL2 doesn't support systemd by default. Use one of these methods:

**Method A: Using Helper Scripts (Easiest)**
```bash
# Start the agent
./start_agent.sh

# Stop the agent
./stop_agent.sh

# View logs
tail -f nvda_agent.log
```

**Method B: Using nohup (Manual)**
```bash
# Run in background
nohup python3 nvda_stock_agent.py > nvda_agent.log 2>&1 &

# Check if it's running
ps aux | grep nvda_stock_agent

# Stop it
pkill -f nvda_stock_agent.py
```

**Method C: Using screen (Better for monitoring)**
```bash
# Install screen if needed
sudo apt-get install screen

# Start a screen session
screen -S nvda_agent

# Run the agent
python3 nvda_stock_agent.py

# Detach: Press Ctrl+A then D
# Reattach: screen -r nvda_agent
# Kill: screen -X -S nvda_agent quit
```

**Method D: Using tmux (Alternative to screen)**
```bash
# Install tmux if needed
sudo apt-get install tmux

# Start tmux session
tmux new -s nvda_agent

# Run the agent
python3 nvda_stock_agent.py

# Detach: Press Ctrl+B then D
# Reattach: tmux attach -t nvda_agent
```

#### For Native Linux (with systemd):

```bash
# Create service file
sudo nano /etc/systemd/system/nvda-agent.service
```

Add this content (update paths and username):
```ini
[Unit]
Description=NVDA Stock Price Monitor Agent
After=network.target

[Service]
Type=simple
User=yonyossef
WorkingDirectory=/home/yonyossef/a2
ExecStart=/usr/bin/python3 /home/yonyossef/a2/nvda_stock_agent.py
Restart=always
RestartSec=10
Environment="PATH=/usr/bin:/usr/local/bin"

[Install]
WantedBy=multi-user.target
```

Then:
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (starts on boot)
sudo systemctl enable nvda-agent.service

# Start the service
sudo systemctl start nvda-agent.service

# Check status
sudo systemctl status nvda-agent.service

# View logs
sudo journalctl -u nvda-agent.service -f
```

### Option 2: Using Cron (Runs every hour)

If you prefer the script to run once per hour instead of continuously:

```bash
# Edit crontab
crontab -e

# Add this line (runs every hour at minute 0)
0 * * * * cd /home/yonyossef/a2 && /usr/bin/python3 /home/yonyossef/a2/nvda_stock_agent.py --once >> /home/yonyossef/a2/cron.log 2>&1
```

### Option 3: Cloud Hosting (Free/Paid Options)

#### A. Render (Free Tier Available) ⭐ Easiest Cloud Option

1. Sign up at https://render.com
2. Create a new "Background Worker"
3. Connect your GitHub repo (or use their CLI)
4. Set environment variables in the dashboard
5. Deploy!

**Pros:** Free tier, easy setup, automatic deployments  
**Cons:** Free tier spins down after inactivity (not ideal for hourly checks)

#### B. Railway (Free Trial) ⭐ Recommended for Cloud Hosting

**Installation:**

```bash
# Install Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Verify installation
railway --version
```

**Deployment Steps:**

1. **Sign up and Login:**
   ```bash
   # Login to Railway (opens browser)
   railway login
   ```
   - If you don't have an account, sign up at https://railway.app
   - The CLI will open your browser for authentication

2. **Initialize Railway Project:**
   ```bash
   cd /home/yonyossef/a2
   railway init
   ```
   - Choose "Empty Project" when prompted
   - Give it a name (e.g., "nvda-stock-agent")

3. **Set Environment Variables:**
   ```bash
   # Enable notification methods
   railway variables set SMS_NOTIFY_ENABLE=False
   railway variables set EMAIL_NOTIFY_ENABLE=True
   
   # If SMS is enabled, set Twilio credentials
   railway variables set TWILIO_ACCOUNT_SID=your_account_sid
   railway variables set TWILIO_AUTH_TOKEN=your_auth_token
   railway variables set TWILIO_PHONE_NUMBER=+1234567890
   railway variables set YOUR_PHONE_NUMBER=+1234567890
   
   # If Email is enabled, set email credentials
   railway variables set SMTP_SERVER=smtp.gmail.com
   railway variables set SMTP_PORT=587
   railway variables set EMAIL_USERNAME=your_email@gmail.com
   railway variables set EMAIL_PASSWORD=your_app_password
   railway variables set EMAIL_TO=recipient@example.com
   ```

4. **Deploy:**
   ```bash
   railway up
   ```
   - This will build and deploy your project
   - Railway will detect Python and install dependencies from `requirements.txt`

5. **Monitor Your Deployment:**
   ```bash
   # View logs
   railway logs
   
   # Open dashboard in browser
   railway open
   ```

**Alternative: Deploy from GitHub (Web UI)**

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `a2` repository
4. Add environment variables in the dashboard (Settings → Variables)
5. Railway will automatically deploy!

**Pros:** 
- Simple CLI and web interface
- Good free trial ($5 credit)
- Automatic deployments from GitHub
- Easy environment variable management

**Cons:** 
- Paid after trial credit runs out (~$5-10/month for always-on service)

#### C. Heroku (Paid)

1. Sign up at https://www.heroku.com
2. Install Heroku CLI
3. Create app and deploy:
   ```bash
   heroku create nvda-stock-agent
   heroku config:set TWILIO_ACCOUNT_SID=... TWILIO_AUTH_TOKEN=...
   git push heroku main
   ```

**Pros:** Reliable, well-documented  
**Cons:** No free tier anymore

#### D. DigitalOcean App Platform (Paid)

1. Sign up at https://www.digitalocean.com
2. Create App → Choose Python
3. Connect repo and set environment variables
4. Deploy!

**Pros:** Reliable, good pricing  
**Cons:** Paid service (~$5/month minimum)

#### E. AWS/GCP/Azure (Advanced)

For more control, you can use:
- **AWS EC2** or **Lambda** (with EventBridge for scheduling)
- **Google Cloud Run** or **Compute Engine**
- **Azure Container Instances** or **Functions**

These require more setup but offer more flexibility.

### Option 4: VPS (Virtual Private Server)

If you want full control:

**Popular VPS Providers:**
- **DigitalOcean Droplets** ($4-6/month)
- **Linode** ($5/month)
- **Vultr** ($2.50/month)
- **Hetzner** (€4/month)

**Setup on VPS:**
1. Create a droplet/instance
2. SSH into it
3. Install Python and dependencies
4. Clone your code
5. Set up systemd service (see Option 1)
6. Done!

### Quick Start for WSL2 Users

The easiest way to run on WSL2:

```bash
# Make sure scripts are executable (already done)
# Start the agent
./start_agent.sh

# Check if running
ps aux | grep nvda_stock_agent

# View live logs
tail -f nvda_agent.log

# Stop when needed
./stop_agent.sh
```

The agent will run in the background and automatically restart if your WSL session is active. Note: If you close WSL or restart Windows, you'll need to start it again.

### Recommendation

- **For WSL2/Local:** Use helper scripts (`./start_agent.sh`) or `screen`/`tmux`
- **For Cloud (Free):** Try Railway or Render
- **For Cloud (Paid):** DigitalOcean App Platform
- **For Full Control:** VPS with systemd service

## Notification Message Format

### SMS Format

You'll receive SMS messages like this:

```
NVDA Stock Update 📈

Price: $125.50
Previous Close: $124.30
Change: $1.20 (0.97%)

Time: 2024-01-15 14:30:00
```

### Email Format

Email notifications include both plain text and HTML formatting with color-coded price changes (green for up, red for down).

## Troubleshooting

### "At least one notification method must be enabled" error
- Make sure you have `SMS_NOTIFY_ENABLE=True` and/or `EMAIL_NOTIFY_ENABLE=True` in your `.env` file
- At least one notification method must be enabled

### "Missing Twilio credentials" error (SMS)
- Make sure `SMS_NOTIFY_ENABLE=True` is set
- Verify your `.env` file contains all required Twilio variables
- Check that variable names match exactly (case-sensitive)

### "Missing email credentials" error (Email)
- Make sure `EMAIL_NOTIFY_ENABLE=True` is set
- Verify your `.env` file contains: `EMAIL_USERNAME`, `EMAIL_PASSWORD`, and `EMAIL_TO`
- For Gmail, make sure you're using an App Password, not your regular password

### SMS not received
- Verify your phone number is correct in E.164 format
- For Twilio trial accounts, make sure you've verified your phone number
- Check Twilio Console for any error messages

### Email not received
- Check your spam/junk folder
- Verify you're using an App Password (not your regular password) for Gmail
- Check SMTP server and port settings
- Verify `EMAIL_TO` address is correct
- Check email provider's SMTP requirements (some require App Passwords)

### Stock price fetch errors
- Check your internet connection
- Yahoo Finance API may be temporarily unavailable (rare)

## License

MIT License - Feel free to modify and use as needed!

