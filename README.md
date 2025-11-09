# 🛡️ Discord AI Moderation Bot

> **Advanced Discord moderation bot with AI-powered context detection, free OCR/translation, and intelligent severity rating system.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.3.2-blue.svg)](https://github.com/Rapptz/discord.py)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Cost](https://img.shields.io/badge/Cost-FREE-brightgreen.svg)](README.md)

---

## 🌟 Features

### 🤖 AI-Powered Moderation
- **Context-Aware Detection** - Understands playful vs hostile language
- **Severity Rating System** - Rates messages 1-10, configurable threshold
- **Smart AI Usage** - Only calls Gemini when slurs detected (saves API quota)
- **Multi-Language Support** - Auto-translates and checks all languages

### 🔍 Advanced Detection
- **Pattern Matching** - Catches 200+ variations per word (leetspeak, spacing, unicode)
- **Image OCR Scanning** - Reads text from images using Tesseract (FREE)
- **Slur Database** - 150+ slurs organized by category
- **Whitelist System** - Trusted users/roles bypass filters

### 📊 Comprehensive Logging
- **User History Tracking** - View complete violation history per user
- **Daily Reports** - Beautiful graphs sent at midnight EST
- **Detailed Violation Logs** - Includes severity, AI analysis, and proof
- **Real-Time Statistics** - Track messages scanned, flagged, and more

### 💰 Zero Cost
- **FREE OCR** - Tesseract (local, no API)
- **FREE Translation** - deep-translator (no API key needed)
- **FREE AI** - Gemini (60 requests/min per key)
- **Total Cost: $0/month**

---

## 📸 Screenshots

### Violation Report
```
🚨 Violation Detected - Severity 8/10

User: @BadUser (123456789)
Channel: #general
Severity: 8/10

Original Message: "you're a retard"
Translated: "you're a retard"

AI Analysis:
Context: hostile
Reason: Clear use of ableist slur with negative intent

⚠️ Action Taken
Message deleted (severity 8 ≥ threshold 7)
```

### Daily Report
Automatically generated graph showing:
- Messages scanned vs flagged
- Hourly activity breakdown
- Clean vs flagged pie chart
- Summary statistics

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Discord bot with MESSAGE CONTENT INTENT enabled
- 2-3 Gemini API keys (free from Google AI Studio)
- Tesseract OCR installed

### Installation

1. **Clone or download this repository**
```bash
git clone https://github.com/yourusername/discord-mod-bot
cd discord-mod-bot
```

2. **Install Tesseract OCR**

**Windows:**
- Download: https://github.com/UB-Mannheim/tesseract/wiki
- Install `tesseract-ocr-w64-setup-5.3.3.exe`
- Add to PATH: `C:\Program Files\Tesseract-OCR`

**Mac:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt update
sudo apt install tesseract-ocr
```

**Verify installation:**
```bash
tesseract --version
```

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file:
```bash
DISCORD_BOT_TOKEN=your_discord_bot_token_here
```

5. **Run the bot**
```bash
python bot.py
```

6. **Configure in Discord**
```bash
/addkey api_key:YOUR_GEMINI_KEY
/setlog #mod-logs
/setup #general
/setseverity threshold:7
/whitelist_role @Moderator
/toggle enabled:True
```

---

## 📁 File Structure

```
discord-mod-bot/
├── bot.py                      # Main bot code
├── pattern_detector.py         # Pattern matching engine
├── slur_patterns.json          # Slur database (150+ words)
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── .gitignore                  # Git ignore rules
├── config.json                 # Bot config (auto-generated)
├── whitelist.json              # Whitelisted users/roles (auto-generated)
├── violation_logs.json         # All violations (auto-generated)
├── daily_stats.json            # Today's stats (auto-generated)
└── README.md                   # This file
```

### File Descriptions

| File | Purpose | Required | Auto-Generated |
|------|---------|----------|----------------|
| `bot.py` | Main bot code | ✅ Yes | ❌ No |
| `pattern_detector.py` | Pattern matching | ✅ Yes | ❌ No |
| `slur_patterns.json` | Slur database | ✅ Yes | ❌ No |
| `requirements.txt` | Dependencies | ✅ Yes | ❌ No |
| `.env` | Your tokens | ✅ Yes | ❌ No |
| `.gitignore` | Git protection | ⚠️ Recommended | ❌ No |
| `config.json` | Bot settings | ✅ Yes | ✅ Yes |
| `whitelist.json` | Whitelist data | ✅ Yes | ✅ Yes |
| `violation_logs.json` | Violation history | ⚠️ Optional | ✅ Yes |
| `daily_stats.json` | Statistics | ⚠️ Optional | ✅ Yes |

---

## 🔧 Detailed Setup Guide

### Step 1: Discord Bot Setup (5 minutes)

1. **Create Discord Application**
   - Go to https://discord.com/developers/applications
   - Click "New Application"
   - Name it (e.g., "Moderation Bot")
   - Click "Create"

2. **Create Bot User**
   - Left sidebar → "Bot"
   - Click "Add Bot" → "Yes, do it!"

3. **Enable Privileged Intents** ⚠️ CRITICAL
   - Scroll to "Privileged Gateway Intents"
   - ✅ Enable **PRESENCE INTENT**
   - ✅ Enable **SERVER MEMBERS INTENT**
   - ✅ Enable **MESSAGE CONTENT INTENT** (REQUIRED!)
   - Click "Save Changes"

4. **Get Bot Token**
   - Under "TOKEN" section
   - Click "Reset Token" (if first time) or "Copy"
   - **Save this token** - you'll need it for `.env`

5. **Generate Invite Link**
   - Left sidebar → "OAuth2" → "URL Generator"
   - **Scopes:** Check `bot` and `applications.commands`
   - **Bot Permissions:** Check:
     - Read Messages/View Channels
     - Send Messages
     - Manage Messages (REQUIRED!)
     - Embed Links
     - Read Message History
     - Use Slash Commands
   - Copy the generated URL

6. **Invite Bot to Server**
   - Paste URL in browser
   - Select your server
   - Click "Authorize"
   - Complete CAPTCHA

---

### Step 2: Gemini API Keys (3 minutes)

**Why multiple keys?**
Each key gets 60 requests/min. More keys = more capacity.

**Getting keys:**
1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Select a Google Cloud project (or create new)
4. Copy the API key
5. **Repeat with different Google accounts** for 2-3 keys total

**No credit card needed!** Gemini API is free tier.

---

### Step 3: Install Tesseract OCR (5 minutes)

**What is Tesseract?**
Free, open-source OCR that runs locally. No API calls, no cost.

**Windows Installation:**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Download `tesseract-ocr-w64-setup-5.3.3.exe`
3. Run installer (default settings OK)
4. Note install path: `C:\Program Files\Tesseract-OCR`
5. Add to PATH:
   - Search "Environment Variables"
   - Edit "Path" variable
   - Add `C:\Program Files\Tesseract-OCR`
   - Click OK
6. **Restart terminal/cmd**

**Mac Installation:**
```bash
brew install tesseract
```

**Linux Installation:**
```bash
sudo apt update
sudo apt install tesseract-ocr
```

**Verify:**
```bash
tesseract --version
```
Should show: `tesseract 5.x.x`

**If Tesseract not found on Windows:**
Add this to top of `bot.py` after imports:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

---

### Step 4: Install Python Dependencies (2 minutes)

**Navigate to bot folder:**
```bash
cd /path/to/discord-mod-bot
```

**Install requirements:**
```bash
pip install -r requirements.txt
```

**What gets installed:**
- `discord.py` - Discord API library
- `google-generativeai` - Gemini AI
- `Pillow` - Image processing
- `pytesseract` - Tesseract wrapper
- `deep-translator` - FREE translation (no API key!)
- `matplotlib` - Graphs for reports
- `pytz` - Timezone handling
- `aiohttp` - Async HTTP requests
- `python-dotenv` - Environment variables

**Troubleshooting:**
- If `pip` not found, try `pip3` or `python -m pip`
- If permission error, add `--user` flag

---

### Step 5: Configure Environment (2 minutes)

**Create `.env` file** in bot folder:
```bash
DISCORD_BOT_TOKEN=paste_your_token_here
```

**Example:**
```bash
DISCORD_BOT_TOKEN=MTIzNDU2Nzg5MDEyMzQ1Njc4.GaBcDe.FgHiJkLmNoPqRsTuVwXyZ123456789
```

**Important:**
- File must be named `.env` (with the dot)
- No spaces around `=`
- No quotes needed
- Keep this file secret!

---

### Step 6: Run the Bot (1 minute)

**Start bot:**
```bash
python bot.py
```

**Expected output:**
```
BotName#1234 has connected to Discord!
Loaded 150 patterns
Whitelisted: 0 users, 0 roles
Severity threshold: 7/10
API keys: 0
```

**Bot should show 🟢 ONLINE in Discord!**

**If errors:**
- Check `.env` file exists and has correct token
- Check Tesseract is installed: `tesseract --version`
- Check all dependencies installed: `pip list`

---

### Step 7: Configure in Discord (3 minutes)

**In any channel where bot can see messages:**

```bash
# 1. Add Gemini API keys (2-3 recommended)
/addkey api_key:AIzaSyABC123...
/addkey api_key:AIzaSyDEF456...
/addkey api_key:AIzaSyGHI789...

# 2. Set log channel (create #mod-logs first)
/setlog #mod-logs

# 3. Set monitored channel
/setup #general

# 4. Set severity threshold (default 7)
# 7 = balanced, 5 = strict, 9 = lenient
/setseverity threshold:7

# 5. Whitelist your moderators (IMPORTANT!)
/whitelist_role @Moderator
/whitelist_role @Admin

# 6. Enable the bot
/toggle enabled:True

# 7. Check everything is configured
/status
```

**Expected `/status` output:**
```
🛡️ Bot Status

Enabled: ✅ Yes
Monitored: #general
Log Channel: #mod-logs
Patterns: 150
API Keys: 3
Severity Threshold: 7/10
Today's Scans: 0
Today's Flags: 0
Total Violations: 0
Whitelisted: 0 users, 2 roles
```

---

## 🧪 Testing Your Bot

### Test 1: Playful Message (Should NOT Delete)

**Post in monitored channel:**
```
hey you monkey stop stealing my food lol
```

**Expected result:**
- ✅ Detected: "monkey"
- 🤖 AI rates: 2-3/10 (playful, no malice)
- 📊 Logged to #mod-logs
- ✅ Message NOT deleted (below threshold 7)
- ✅ No DM sent
- ℹ️ Shows context: "playful"

### Test 2: Clear Slur (SHOULD Delete)

**Post in monitored channel:**
```
testing with nigger
```

**Expected result:**
- ✅ Detected: "nigger"
- 🤖 AI rates: 10/10 (severe slur)
- ❌ Message DELETED immediately
- 📩 You receive DM warning
- 📊 Logged to #mod-logs with severity 10
- ℹ️ Shows context: "hostile"

### Test 3: Context-Dependent

**Post in monitored channel:**
```
stop being such a retard
```

**Expected result:**
- ✅ Detected: "retard"
- 🤖 AI rates: 7-8/10 (hostile use of ableist slur)
- ❌ Deleted (meets threshold 7)
- 📩 DM sent
- 📊 Logged with AI explanation

### Test 4: Whitelisted User

**Moderator with whitelisted role posts:**
```
testing nigger for the bot
```

**Expected result:**
- ✅ User is whitelisted
- ✅ Message NOT deleted
- ✅ No AI check performed
- ✅ Not logged
- 💡 Allows mods to test and discuss violations

### Test 5: Image OCR

**Upload image with text:**
> Image containing: "you're a faggot"

**Expected result:**
- 🖼️ OCR extracts: "you're a faggot"
- ✅ Translates to English
- ✅ Detects: "faggot"
- 🤖 AI rates severity
- ❌ Deleted if ≥ threshold
- 📊 Logged with OCR text included

### Test 6: Foreign Language

**Post in monitored channel:**
```
你是个傻瓜 (Chinese for "you're an idiot")
```

**Expected result:**
- 🌍 Translates to English: "you're an idiot"
- ✅ Checks translated text for slurs
- 🤖 AI rates severity
- 📊 Action taken based on rating

---

## 🎮 Command Reference

### Configuration Commands

| Command | Description | Permission |
|---------|-------------|------------|
| `/setup #channel` | Set channel to monitor | Admin |
| `/setlog #channel` | Set log channel for reports | Admin |
| `/toggle enabled:True/False` | Enable or disable bot | Admin |
| `/setseverity threshold:7` | Set minimum severity for punishment (1-10) | Admin |
| `/modmode strict/calm/status` | Set moderation mode or check status | Admin |
| `/status` | View bot configuration and stats | Anyone |

### API Key Management

| Command | Description | Permission |
|---------|-------------|------------|
| `/addkey api_key:xxx` | Add Gemini API key to rotation | Admin |
| `/listkeys` | View all configured API keys | Admin |
| `/removekey key_number:1` | Remove API key from rotation | Admin |

### Whitelist Management

| Command | Description | Permission |
|---------|-------------|------------|
| `/whitelist_user @user` | Whitelist a user (bypass all filters) | Admin |
| `/unwhitelist_user @user` | Remove user from whitelist | Admin |
| `/whitelist_role @role` | Whitelist entire role | Admin |
| `/unwhitelist_role @role` | Remove role from whitelist | Admin |
| `/whitelist_list` | View all whitelisted users and roles | Anyone |

### Moderation Commands

| Command | Description | Permission |
|---------|-------------|------------|
| `/user @username` | Check violation history for user | Anyone |
| `/forcereport` | Generate daily report immediately | Admin |

---

## ⚖️ Understanding the Severity System

### How It Works

1. **Pattern Detection** → Bot checks if message contains slurs from database
2. **AI Analysis** → If slurs found, Gemini rates severity 1-10 based on context
3. **Threshold Check** → Compares severity to configured threshold (default 7)
4. **Action Taken** → If severity ≥ threshold: delete + DM + log

### Severity Scale

| Severity | Description | Context | Examples | Default Action |
|----------|-------------|---------|----------|----------------|
| 1-3 | Playful, no malice | Friends joking | "you monkey lol" | Log only |
| 4-6 | Potentially inappropriate | Depends on context | Mild insults, unclear intent | Log only |
| 7-8 | Clear harassment | Hostile use of slurs | "you retard", "stupid faggot" | Delete + DM |
| 9-10 | Severe hate speech | Direct attacks, threats | Racial slurs, death threats | Delete + DM |

### Configuring Threshold

**Strict Mode (threshold 5):**
```bash
/setseverity threshold:5
```
- Flags more messages
- Catches borderline cases
- More false positives
- Good for zero-tolerance servers

**Balanced Mode (threshold 7) - DEFAULT:**
```bash
/setseverity threshold:7
```
- Good balance
- Catches clear violations
- Allows friendly banter
- Recommended for most servers

**Lenient Mode (threshold 9):**
```bash
/setseverity threshold:9
```
- Only severe violations
- Fewer false positives
- Allows more rough language
- Good for mature/gaming communities

### AI Reasoning Examples

**Example 1: Playful Context**
```
Message: "dude you're such a monkey haha"
Detected: "monkey"
AI Rating: 2/10
Reason: "Playful banter between users, no malicious intent, 
        using 'monkey' as friendly teasing with 'haha' indicating humor"
Context: playful
Action: Log only (2 < 7)
```

**Example 2: Hostile Context**
```
Message: "you're a fucking retard"
Detected: "retard"
AI Rating: 8/10
Reason: "Clear use of ableist slur with negative intent, 
        combined with profanity directed at individual"
Context: hostile
Action: Delete + DM (8 ≥ 7)
```

**Example 3: Severe Slur**
```
Message: "nigger"
Detected: "nigger"
AI Rating: 10/10
Reason: "Direct use of severe racial slur with no 
        educational or contextual justification"
Context: hostile
Action: Delete + DM (10 ≥ 7)
```

---

## 🎯 Pattern Matching System

### How It Works

You add **one base word** to `slur_patterns.json`:
```json
"nigger"
```

The bot **automatically catches 200+ variations**:
- `nigger`, `nigga`
- `n1gger`, `n1gga` (leetspeak)
- `n i g g e r` (spaced)
- `n.i.g.g.e.r` (dots)
- `n_i_g_g_e_r` (underscores)
- `n1gg3r` (mixed)
- `ηigger` (unicode eta)
- `nіgger` (Cyrillic і)
- And 190+ more!

### Character Substitutions Detected

| Original | Substitutions Caught |
|----------|---------------------|
| `a` | `4`, `@`, `α`, `а` |
| `e` | `3`, `ε`, `е` |
| `i` | `1`, `!`, `l`, `\|`, `ı`, `і` |
| `o` | `0`, `ο`, `о` |
| `s` | `5`, `$`, `ş`, `ѕ` |
| `g` | `9`, `q` |
| `t` | `7`, `+` |
| `b` | `8` |
| And more... | See `pattern_detector.py` |

### Adding Words to Database

**Edit `slur_patterns.json`:**
```json
{
  "racial_ethnic_slurs": [
    "your_word_here",
    "another_word"
  ]
}
```

**Rules:**
- ✅ Lowercase only
- ✅ NO asterisks (use `nigger` not `n*gger`)
- ✅ Base word only (variations caught automatically)
- ✅ One word per line
- ❌ No patterns needed (bot handles it)

---

## 💰 Cost Breakdown

### FREE Services Used

| Service | Provider | Cost | Usage |
|---------|----------|------|-------|
| OCR | Tesseract (local) | $0 | Unlimited |
| Translation | deep-translator | $0 | Unlimited (reasonable use) |
| AI Analysis | Gemini API | $0 | 60 requests/min per key |
| Hosting | Your PC/VPS | $0-5 | Depends on hosting choice |

### Comparison to Paid Alternatives

| Feature | This Bot | Paid Alternative |
|---------|----------|------------------|
| OCR | FREE (Tesseract) | $1.50 per 1,000 images (Google Vision) |
| Translation | FREE (deep-translator) | $20/month + $20 per 1M chars (Google Cloud) |
| AI | FREE (Gemini) | $0.50 per 1M tokens (GPT-4) |
| **Total** | **$0/month** | **$20-50/month** |

### API Quota Management

**Gemini Free Tier:**
- 60 requests per minute per key
- No daily limit
- No credit card required

**Strategy for high-traffic servers:**
- Add 3-5 API keys (different Google accounts)
- Bot automatically rotates when rate limited
- Each key = 60 req/min
- 5 keys = 300 req/min capacity
- More than enough for even large servers

**Typical usage:**
- Small server (100 members): 5-10 API calls/day
- Medium server (1,000 members): 20-50 API calls/day
- Large server (10,000 members): 100-200 API calls/day

**Why so few API calls?**
Bot only calls Gemini when slurs are detected! 99% of messages skip AI entirely.

---

## 📊 Features in Detail

### 1. Context-Aware AI Detection

**Problem:** Traditional bots ban "you monkey" even when playful.

**Solution:** AI understands context:
```
"you monkey lol" → Playful (severity 2) → Allowed
"you filthy monkey" → Hostile (severity 8) → Deleted
```

**How it works:**
- Analyzes full message and tone
- Considers surrounding words
- Detects intent (joking vs attacking)
- Rates on 1-10 scale
- Only punishes above threshold

### 2. FREE Image OCR

**What it does:**
- Extracts text from uploaded images
- Translates extracted text
- Checks for slurs in images
- Catches users trying to bypass text filters

**Powered by Tesseract:**
- Open-source OCR by Google
- Runs locally (no API calls)
- Supports 100+ languages
- Very accurate for clear text

**Example:**
```
User uploads meme with text: "nigger"
→ OCR extracts: "nigger"
→ Translates (if needed)
→ Detects slur
→ AI rates severity
→ Takes action
```

**Limitations:**
- Struggles with very small text
- May miss heavily stylized fonts
- Handwriting hit-or-miss
- Best for screenshots and memes

### 3. FREE Multi-Language Translation

**Powered by deep-translator:**
- Uses Google Translate (unofficial API)
- No API key needed
- No rate limits (reasonable use)
- Supports 100+ languages
- Completely free

**How it works:**
```
Message in Spanish: "eres un idiota"
→ Auto-detects language: Spanish
→ Translates to English: "you're an idiot"
→ Checks English text for slurs
→ Takes action if needed
```

**Supported languages:**
Spanish, French, German, Chinese, Japanese, Korean, Arabic, Russian, Portuguese, Italian, and 90+ more!

### 4. Whitelist System

**Why whitelist?**
- Mods need to discuss violations
- Testing the bot
- Trusted long-time members
- Prevents false positives

**How to use:**
```bash
# Whitelist all mods (recommended)
/whitelist_role @Moderator

# Whitelist specific user
/whitelist_user @TrustedMember

# View who's whitelisted
/whitelist_list

# Remove from whitelist
/unwhitelist_user @User
```

**What happens:**
- Whitelisted users bypass ALL filters
- No AI checks performed
- Not logged
- Can post anything without consequences

### 5. User History Tracking

**Track violations per user:**
```bash
/user @username
```

**Shows:**
- Total violation count
- Last 5 violations with:
  - Timestamp
  - Severity rating
  - Original message
  - Reason for flagging
- Whitelist status

**Use cases:**
- Evidence for bans
- Track repeat offenders
- See if user improving
- Appeal reviews

### 6. Daily Reports

**Automatic reports at midnight EST:**
- Beautiful 4-panel graph
- Overall statistics
- Hourly activity breakdown
- Clean vs flagged pie chart
- Summary statistics

**Manual generation:**
```bash
/forcereport
```

**What's included:**
- Messages scanned today
- Messages flagged today
- Unique users caught
- Flag rate percentage
- Peak activity hour
- API key status
- Whitelist count
- Severity threshold

### 7. API Key Rotation

**Multiple keys = more capacity:**
```bash
/addkey api_key:KEY1
/addkey api_key:KEY2
/addkey api_key:KEY3
```

**Automatic rotation:**
- Bot uses key #1
- Key #1 hits limit → switches to key #2
- Key #2 hits limit → switches to key #3
- Key #3 hits limit → switches back to key #1 (reset)
- Seamless, no downtime!

**Check status:**
```bash
/listkeys
```
Shows which key is currently active.

---

## 🚨 Troubleshooting

### Bot Won't Start

**Error: "DISCORD_BOT_TOKEN not set"**

**Fix:**
- Check `.env` file exists
- File named `.env` (not `.env.txt`)
- Token copied correctly
- No spaces around `=`

**Error: "No module named 'discord'"**

**Fix:**
```bash
pip install -r requirements.txt
```

**Error: "Tesseract not found"**

**Fix (Windows):**
Add to top of `bot.py`:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**Fix (Mac/Linux):**
```bash
which tesseract  # Find path
# Add path to bot.py if needed
```

### Bot Shows Offline

**Check:**
- Token is correct
- Bot invited to server
- MESSAGE CONTENT INTENT enabled in Developer Portal

**Re-invite bot:**
1. Developer Portal → OAuth2 → URL Generator
2. Scopes: `bot` + `applications.commands`
3. Permissions: Include "Manage Messages"
4. Generate URL and invite again

### Commands Don't Show Up

**Solutions:**
- Wait 5-10 minutes for Discord sync
- Restart bot
- Kick bot and re-invite
- Check `applications.commands` scope enabled

### Patterns Not Detecting

**Check pattern count:**
```bash
/status
```
Should show "Patterns: 150+"

**If 0 patterns:**
- Verify `slur_patterns.json` exists
- Check JSON is valid: `python -m json.tool slur_patterns.json`
- Ensure file in same folder as `bot.py`

### Messages Not Being Deleted

**Check:**
- Bot enabled: `/toggle enabled:True`
- Correct channel: `/setup #channel`
- Bot has "Manage Messages" permission
- Bot's role above user's role
- User not whitelisted: `/whitelist_list`
- Severity ≥ threshold: `/status`

### Translation Not Working

**Symptoms:**
- Foreign language messages not detected
- No translation shown in logs

**Fix:**
- Check internet connection (deep-translator needs web access)
- Update: `pip install --upgrade deep-translator`
- Bot will use original text if translation fails

### OCR Not Reading Images

**Common issues:**
- Image quality too low
- Text too small (<12px font)
- Heavily stylized fonts
- Handwriting

**This is normal** - OCR works best on clear, printed text.

### API Keys Getting Rate Limited

**Symptoms:**
- "All API keys rate limited" in logs
- Severity always 10

**Fix:**
```bash
# Add more keys
/addkey api_key:another_key
```

**Check rotation:**
```bash
/listkeys
# Arrow shows active key
```

Bot automatically rotates when limits hit.

### False Positives

**Too strict:**
```bash
/setseverity threshold:8  # More lenient
```

**Still issues:**
- Whitelist trusted users: `/whitelist_user @user`
- Review slur patterns for overreach
- Check AI reasoning in logs

### False Negatives

**Missing violations:**
```bash
/setseverity threshold:6  # More strict
```

**Add missing words:**
Edit `slur_patterns.json` and add new patterns.

---

## 🔐 Security & Privacy

### Data Storage

**What's stored locally:**
- `config.json` - Bot settings, API keys
- `violation_logs.json` - All flagged messages
- `daily_stats.json` - Today's statistics
- `whitelist.json` - Whitelisted users/roles

**What's NOT stored:**
- Clean messages (not logged anywhere)
- Private user info beyond Discord IDs
- Message history (only violations)

### API Data

**Sent to Gemini:**
- Only messages with detected slurs
- For severity rating only
- Not stored by Google (per Gemini terms)

**Sent to Google Translate:**
- Messages for translation
- Anonymous (no user association)
- Standard Google Translate terms apply

**NOT sent anywhere:**
- Clean messages
- Private conversations
- User personal info

### Protecting Your Bot

**NEVER share these:**
- `.env` file (has your Discord token)
- `config.json` (has Gemini API keys)
- `violation_logs.json` (has user data)

**Safe to share:**
- `bot.py`, `pattern_detector.py`
- `requirements.txt`
- `slur_patterns.json` (if you want)
- Documentation files

**Use .gitignore:**
The included `.gitignore` protects sensitive files automatically when using Git.

### Best Practices

1. **Rotate tokens regularly** - Change Discord token every few months
2. **Limit bot permissions** - Only give what's needed
3. **Monitor logs** - Review violation logs for anomalies
4. **Backup data** - Copy logs before major updates
5. **Keep updated** - Update dependencies regularly

---

## 📈 Performance & Scalability

### Resource Usage

**CPU:**
- Idle: ~1-2%
- Processing message: ~5-10%
- OCR scan: ~20-30% (brief spike)

**RAM:**
- Base: ~100-150 MB
- With data: ~200-300 MB
- Max: ~500 MB (large servers)

**Network:**
- Minimal (only API calls)
- ~1-5 KB per message checked
- ~10-50 KB per API call

### Server Size Guidelines

**Small Server (100 members):**
- Messages/day: ~1,000
- API calls/day: ~5-10
- 1 API key sufficient
- Runs on any PC

**Medium Server (1,000 members):**
- Messages/day: ~10,000
- API calls/day: ~20-50
- 2-3 API keys recommended
- Runs on basic VPS

**Large Server (10,000+ members):**
- Messages/day: ~100,000
- API calls/day: ~100-200
- 3-5 API keys recommended
- Dedicated VPS recommended

**Very Large Server (50,000+ members):**
- Messages/day: ~500,000+
- API calls/day: ~500-1000
- 5-10 API keys needed
- Consider multiple bot instances

### Optimization Tips

1. **Multiple API keys** - Add 3-5 for busy servers
2. **Adjust threshold** - Higher threshold = fewer API calls
3. **Selective monitoring** - Don't monitor all channels
4. **Whitelist staff** - Reduces unnecessary checks
5. **Review patterns** - Remove rarely-triggered patterns

---

## 🔄 Updating the Bot

### Updating Dependencies

```bash
pip install --upgrade -r requirements.txt
```

### Updating Slur Database

Edit `slur_patterns.json`:
```json
{
  "your_category": [
    "new_word_here"
  ]
}
```

Restart bot:
```bash
python bot.py
```

### Backing Up Data

**Before updates:**
```bash
cp config.json config.json.backup
cp violation_logs.json violation_logs.json.backup
cp slur_patterns.json slur_patterns.json.backup
```

**Restore if needed:**
```bash
cp config.json.backup config.json
```

---

## 🤝 Contributing

### Reporting Issues

Found a bug? Please include:
- Error message (full text)
- What you were doing
- Expected vs actual behavior
- Python version: `python --version`
- OS: Windows/Mac/Linux

### Suggesting Features

Have an idea? Consider:
- Does it fit the bot's purpose?
- Is it feasible with free APIs?
- Would it benefit most users?

### Pull Requests

1. Fork the repository
2. Create feature branch
3. Make your changes
4. Test thoroughly
5. Submit pull request with description

---

## 📝 Changelog

### Version 2.0.0 (Current)

**Major Changes:**
- ✅ FREE OCR using Tesseract (replaced Google Vision)
- ✅ FREE translation using deep-translator (replaced Google Cloud)
- ✅ Severity rating system (1-10 scale)
- ✅ Context-aware AI detection
- ✅ Configurable threshold per server
- ✅ Smart API usage (only when slurs detected)

**Improvements:**
- ⬆️ 99% reduction in API costs ($20/mo → $0/mo)
- ⬆️ Better accuracy (context understanding)
- ⬆️ Fewer false positives
- ⬆️ Easier setup (no Google Cloud needed)

**Removed:**
- ❌ Google Cloud Translation API
- ❌ Google Cloud Vision API
- ❌ Credit card requirement

### Version 1.0.0 (Legacy)

- Basic slur detection
- Google Cloud OCR
- Google Cloud Translation
- All messages sent to AI
- Fixed punishment (no severity)

---

## ❓ FAQ

### General Questions

**Q: Is this really free?**
A: Yes! All services used are free:
- Tesseract OCR (open source)
- deep-translator (free)
- Gemini API (free tier)
- Total: $0/month

**Q: Do I need a credit card?**
A: No! Unlike old system, no credit card needed.

**Q: Will I get charged?**
A: No. All services are free tier with no upgrade required.

**Q: What's the catch?**
A: No catch! Gemini has rate limits (60/min per key), but multiple keys solve this.

---

### Technical Questions

**Q: Does it work on all operating systems?**
A: Yes! Windows, Mac, and Linux all supported.

**Q: Can I run multiple instances?**
A: Yes, one instance per server or multiple channels.

**Q: Does it support multiple languages?**
A: Yes, 100+ languages via deep-translator.

**Q: How accurate is the OCR?**
A: Very accurate for clear text. Struggles with stylized fonts or handwriting.

**Q: How accurate is the AI?**
A: Very accurate. Gemini understands context and rates severity appropriately.

---

### Moderation Questions

**Q: Can users bypass the filter?**
A: Very difficult. Pattern matching catches 200+ variations per word.

**Q: What if someone reports a false positive?**
A: Check logs with `/user`, review AI reasoning, adjust threshold or whitelist if needed.

**Q: Can I customize the slur list?**
A: Yes! Edit `slur_patterns.json` and add/remove words.

**Q: How do I handle appeals?**
A: Review `/user @username` history, check AI reasoning in logs, reverse if mistake.

**Q: Can I make it stricter/more lenient?**
A: Yes! Use `/setseverity` to adjust threshold (5=strict, 7=balanced, 9=lenient).

---

### Setup Questions

**Q: I can't install Tesseract, help?**
A: See [Step 3: Install Tesseract OCR](#step-3-install-tesseract-ocr-5-minutes) above.

**Q: Commands don't show up?**
A: Wait 10 minutes for Discord sync, or restart bot.

**Q: Bot shows offline?**
A: Check MESSAGE CONTENT INTENT is enabled in Developer Portal.

**Q: "Tesseract not found" error?**
A: Add path to bot.py: `pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`

**Q: How many API keys do I need?**
A: Minimum 1, recommended 2-3, large servers 5+.

---

## 🎓 Advanced Usage

### Custom Severity Thresholds per Channel

**Currently:** One threshold for entire server

**Workaround:** Run multiple bot instances
```bash
# Instance 1: #general (strict)
python bot.py  # threshold 5

# Instance 2: #memes (lenient)
python bot2.py  # threshold 9
```

### Scheduling Reports

**Current:** Reports at midnight EST

**Change timezone:** Edit `bot.py` line ~290:
```python
@tasks.loop(time=time(hour=5, minute=0, tzinfo=pytz.timezone('US/Pacific')))
```

### Export Violations to CSV

**Manual export:**
```python
import json
import csv

with open('violation_logs.json', 'r') as f:
    logs = json.load(f)

with open('violations.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=logs[0].keys())
    writer.writeheader()
    writer.writerows(logs)
```

### Integration with Other Bots

**Webhook notifications:**
Edit `log_violation()` in bot.py to send webhook:
```python
import aiohttp

webhook_url = "https://discord.com/api/webhooks/..."
async with aiohttp.ClientSession() as session:
    await session.post(webhook_url, json={"content": "Violation detected!"})
```

---

## 🌐 Hosting Options

### Option 1: Run on Your PC (FREE)

**Pros:**
- Completely free
- Full control
- Easy to debug

**Cons:**
- PC must stay on
- No redundancy
- Uses your resources

**Best for:** Small servers, testing

---

### Option 2: VPS Hosting ($3-5/month)

**Providers:**
- DigitalOcean ($5/mo)
- Vultr ($2.50/mo)
- Linode ($5/mo)
- Hetzner ($3.50/mo)

**Setup:**
```bash
# SSH into VPS
ssh root@your-vps-ip

# Install Python
sudo apt update
sudo apt install python3 python3-pip tesseract-ocr

# Upload bot files (use SFTP or git clone)
# Install dependencies
pip3 install -r requirements.txt

# Run in background
nohup python3 bot.py &
```

**Best for:** Medium-large servers, 24/7 uptime

---

### Option 3: Free Hosting

**Replit (Limited):**
- Free tier available
- Easy setup
- Limited uptime (pinging needed)

**Railway.app (Limited):**
- Free tier: 500 hours/month
- Sleeps after inactivity
- Good for small servers

**Heroku (Discontinued):**
- Free tier removed
- Not recommended

**Best for:** Very small servers, testing

---

### Option 4: Docker Container

**Dockerfile example:**
```dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y tesseract-ocr

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

**Run:**
```bash
docker build -t discord-mod-bot .
docker run -d --env-file .env discord-mod-bot
```

**Best for:** Advanced users, multiple instances

---

## 📚 Additional Resources

### Official Documentation

- [Discord.py Docs](https://discordpy.readthedocs.io/)
- [Gemini API Docs](https://ai.google.dev/docs)
- [Tesseract OCR Docs](https://tesseract-ocr.github.io/)
- [deep-translator Docs](https://deep-translator.readthedocs.io/)

### Community

- Discord.py Support Server
- GitHub Issues (this repository)
- Stack Overflow (tag: discord.py)

### Related Projects

- Discord Moderation Best Practices
- Other Discord bot templates
- Pattern matching libraries

---

## ⚖️ Legal & Disclaimer

### Terms of Use

This bot is provided "as is" without warranty. Use at your own risk.

**You are responsible for:**
- Compliance with Discord Terms of Service
- Compliance with local laws
- Content of your slur database
- Actions taken based on bot reports
- Privacy of logged data

**Not responsible for:**
- False positives/negatives
- Missed violations
- API service outages
- Data loss
- Moderation decisions

### Privacy Policy

**Data collected:**
- Discord user IDs (violation tracking)
- Message content (violations only)
- Timestamps and channel info

**Data usage:**
- Moderation purposes only
- Stored locally on your server
- Not shared with third parties (except API processing)

**Data retention:**
- Kept indefinitely in `violation_logs.json`
- Can be deleted manually anytime
- Users can request data deletion

**Third-party services:**
- Gemini API: Processes flagged messages only
- Google Translate: Processes all messages for translation
- Both follow their respective privacy policies

### Discord Terms Compliance

This bot complies with Discord's Terms of Service and Bot Guidelines:
- Respects rate limits
- Uses proper intents
- No self-botting
- No token stealing
- No spam

**Your responsibility:**
- Don't use bot to harass
- Don't share tokens
- Follow Discord TOS
- Use appropriately

---

## 🎖️ Credits

**Developed by:** Duck

**Built with:**
- [Discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - Free OCR engine
- [deep-translator](https://github.com/nidhaloff/deep-translator) - Free translation
- [Gemini API](https://ai.google.dev/) - AI analysis
- [Matplotlib](https://matplotlib.org/) - Graphs
- [Pillow](https://python-pillow.org/) - Image processing

**Special thanks:**
- Discord.py community
- Tesseract maintainers
- Google AI team
- Open source contributors

---

## 📄 License

MIT License

Copyright (c) 2025 Duck

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 🚀 Quick Links

- [Installation](#installation)
- [Commands](#command-reference)
- [Testing](#testing-your-bot)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

---

## 📞 Support

**Having issues?**
1. Read [Troubleshooting](#troubleshooting)
2. Check [FAQ](#faq)
3. Review error messages carefully
4. Open GitHub issue with details

**Questions?**
- Check this README first
- Review documentation links
- Ask in Discord.py support server

---

## ⭐ Star This Project

If this bot helped your server, consider:
- ⭐ Starring on GitHub
- 🐛 Reporting bugs
- 💡 Suggesting features
- 📖 Improving documentation
- 🔀 Contributing code

---

**Made with ❤️ for safer Discord communities**

*Last updated: 2025*
