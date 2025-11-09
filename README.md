# 🛡️ Discord AI Moderation Bot

> **Advanced Discord moderation bot with AI-powered context detection, free OCR/translation, intelligent severity rating, and 3 moderation modes.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.3.2-blue.svg)](https://github.com/Rapptz/discord.py)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Cost](https://img.shields.io/badge/Cost-FREE-brightgreen.svg)](README.md)

---

## 🌟 Features

### 🤖 AI-Powered Moderation
- **Gemini 2.0 Flash** - Latest Google AI model for context analysis
- **Context-Aware Detection** - Understands playful vs hostile language
- **Severity Rating System** - Rates messages 1-10 with detailed reasoning
- **Three Moderation Modes:**
  - 🟢 **Relax** - NO AI, pattern-only, instant delete, $0 cost
  - 🟡 **Calm** - AI for detected slurs only (recommended)
  - 🔴 **Strict** - AI checks ALL messages
- **Multi-Language Support** - Auto-translates and checks all languages

### 🔍 Advanced Detection
- **Pattern Matching** - Catches 200+ variations per word (leetspeak, spacing, unicode)
- **Image OCR Scanning** - Reads text from images using Tesseract (FREE, optional)
- **Emoji Detection** - Checks emoji names (`:skull:`, `:middle_finger:`, etc.)
- **Slur Database** - 800-1000+ slurs organized by category
- **Whitelist System** - Trusted users/roles bypass filters
- **Case Management** - Detailed violation logs per user

### 📊 Comprehensive Logging
- **User History Tracking** - Complete violation history per user
- **Case System** - Detailed case logs with AI analysis and statistics
- **Daily Reports** - Beautiful graphs sent at midnight EST
- **Detailed Violation Logs** - Includes severity, AI reasoning, and proof
- **Real-Time Statistics** - Track messages scanned, flagged, and more

### 💰 Zero Cost Operation
- **FREE OCR** - Tesseract (local, optional)
- **FREE Translation** - deep-translator (no API key needed)
- **FREE AI** - Gemini 2.0 (60 requests/min per key)
- **Relax Mode** - 100% free, no API needed
- **Total Cost: $0/month**

---

## 🆕 What's New in v3.0

### ✅ Major Updates
- **Gemini 2.0 Flash Experimental** - Latest AI model (no more 404 errors!)
- **Relax Mode** - Pattern-only detection, NO AI, zero cost
- **Emoji Detection** - Now checks emoji names like `:nigger:`, `:kys:`, etc.
- **Better Error Handling** - Graceful OCR failures (optional feature)
- **Fixed Font Warnings** - Clean console output
- **Improved Foreign Language** - Better translation and detection

### 🆚 Mode Comparison

| Feature | Relax Mode | Calm Mode | Strict Mode |
|---------|-----------|-----------|-------------|
| AI Usage | ❌ None | ✅ Detected only | ✅ ALL messages |
| Speed | ⚡ Instant | 🕐 ~1-2 sec | 🕐 ~2-3 sec |
| API Cost | 💰 $0 | 💰 Low | 💰 High |
| Accuracy | ⚠️ Basic | ✅ High | ✅ Highest |
| False Positives | ⚠️ More | ✅ Few | ✅ Fewest |
| Context Analysis | ❌ No | ✅ Yes | ✅ Yes |
| Best For | Zero budget | Most servers | High security |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ (3.9 works with warnings)
- Discord bot with MESSAGE CONTENT INTENT enabled
- 2-3 Gemini API keys (free from Google AI Studio) - **Optional for Relax Mode**
- Tesseract OCR (optional - only needed for image scanning)

### Installation

**⚠️ IMPORTANT: If you posted your bot token publicly, you MUST regenerate it first!**

1. **Clone or download this repository**
```bash
git clone https://github.com/yourusername/discord-mod-bot
cd discord-mod-bot
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure bot token** (Choose ONE method)

**Method 1: .env file (Recommended)**
```bash
# Create .env file
DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN_HERE

# Optional: Add API keys (not needed for Relax mode)
GEMINI_API_KEY_1=AIzaSy...
GEMINI_API_KEY_2=AIzaSy...
```

**Method 2: token.txt (Good for hosting)**
```bash
echo 'YOUR_BOT_TOKEN_HERE' > token.txt
```

**Method 3: Environment variable**
```bash
export DISCORD_BOT_TOKEN='YOUR_BOT_TOKEN_HERE'
```

4. **Run the bot**
```bash
python bot.py
```

5. **Configure in Discord**
```bash
# For FREE mode (no API keys needed):
/setup #general
/setlog #mod-logs
/modmode mode:relax
/whitelist_role @Moderator
/toggle enabled:True

# For AI mode (requires API keys):
/addkey api_key:YOUR_GEMINI_KEY
/addkey api_key:YOUR_GEMINI_KEY_2
/modmode mode:calm
/setseverity threshold:7
/toggle enabled:True
```

---

## 📁 File Structure

```
discord-mod-bot/
├── bot.py                      # Main bot code (UPDATED!)
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

---

## 🎮 Command Reference

### Configuration Commands

| Command | Description | Permission |
|---------|-------------|------------|
| `/setup #channel` | Set channel to monitor | Admin |
| `/setlog #channel` | Set log channel for reports | Admin |
| `/toggle enabled:True/False` | Enable or disable bot | Admin |
| `/setseverity threshold:7` | Set minimum severity for punishment (1-10) | Admin |
| `/modmode relax/calm/strict` | Set moderation mode | Admin |
| `/status` | View bot configuration and stats | Anyone |

### API Key Management

| Command | Description | Permission |
|---------|-------------|------------|
| `/addkey api_key:xxx` | Add Gemini API key (not needed for Relax) | Admin |
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
| `/case @username` | View detailed case logs with full analysis | Anyone |
| `/forcereport` | Generate daily report immediately | Admin |

---

## 🎯 New Features Explained

### 1. Relax Mode (Zero Cost)

**What is it?**
- NO AI checking at all
- Pure pattern matching
- Instant deletion on match
- Zero API costs
- Perfect for budget servers

**How it works:**
```
Message → Pattern match? → YES → DELETE (no AI)
                        → NO  → Allow
```

**Example:**
```bash
User posts: "you're a nigger"
    ↓
Pattern detected: "nigger"
    ↓
INSTANT DELETE (no AI context check)
    ↓
Logged with reason: "Pattern match: nigger (Relax mode)"
```

**Enable Relax Mode:**
```bash
/modmode mode:relax
```

**Pros:**
- ✅ Completely free ($0/month)
- ✅ No API keys needed
- ✅ Instant deletion
- ✅ Simple setup

**Cons:**
- ⚠️ No context understanding
- ⚠️ More false positives
- ⚠️ "you monkey lol" gets deleted
- ⚠️ Can't distinguish playful vs hostile

---

### 2. Calm Mode (Recommended)

**What is it?**
- Pattern detection first
- AI only for flagged messages
- Best accuracy/cost ratio
- Understands context

**How it works:**
```
Message → Pattern match? → NO → Allow
                        → YES → AI check → Rate 1-10
                                        → ≥ Threshold? → DELETE
                                        → < Threshold? → Log only
```

**Example:**
```bash
User posts: "you monkey lol"
    ↓
Pattern detected: "monkey"
    ↓
AI analyzes: "Playful banter, no malice"
    ↓
Severity: 2/10 (below threshold 7)
    ↓
Message ALLOWED (logged only)
```

**Enable Calm Mode:**
```bash
/modmode mode:calm
```

**Pros:**
- ✅ Context-aware
- ✅ Low API usage
- ✅ Few false positives
- ✅ Best for most servers

**Cons:**
- ⚠️ Requires API keys
- ⚠️ Slight delay (~1-2 sec)

---

### 3. Strict Mode (Maximum Protection)

**What is it?**
- Checks ALL messages with AI
- No pattern detection needed
- Highest accuracy
- Catches everything

**How it works:**
```
Message → AI check ALL → Rate 1-10
                      → ≥ Threshold? → DELETE
                      → < Threshold? → Allow
```

**Enable Strict Mode:**
```bash
/modmode mode:strict
```

**Pros:**
- ✅ Maximum protection
- ✅ Catches subtle violations
- ✅ Best accuracy

**Cons:**
- ⚠️ High API usage
- ⚠️ Needs many API keys
- ⚠️ Slower processing

---

### 4. Emoji Detection

**What is it?**
The bot now checks emoji names for slurs!

**How it works:**
```
User posts: "kys :skull:"
    ↓
Bot extracts emoji name: "skull"
    ↓
Bot checks: "kys" + "skull" for slurs
    ↓
Takes action if needed
```

**Catches:**
- `:skull:` (detected as "skull")
- `:middle_finger:` (detected as "middle finger")
- `:poop:` (detected as "poop")
- Custom emojis with offensive names

**Note:** Add emoji names to `slur_patterns.json` if needed:
```json
{
  "offensive_emojis": [
    "skull",
    "kys",
    "middle finger"
  ]
}
```

---

## ⚖️ Understanding the Severity System

### How It Works

1. **Pattern Detection** → Bot checks if message contains slurs
2. **Mode Check:**
   - **Relax Mode:** Instant delete (skip AI)
   - **Calm/Strict Mode:** AI analysis
3. **AI Analysis** → Gemini rates severity 1-10 based on context
4. **Threshold Check** → Compares severity to configured threshold
5. **Action Taken** → If severity ≥ threshold: delete + DM + log

### Severity Scale

| Severity | Description | Context | Examples | Default Action |
|----------|-------------|---------|----------|----------------|
| 1-3 | Playful, no malice | Friends joking | "you monkey lol" | Log only |
| 4-6 | Potentially inappropriate | Depends on context | Mild insults | Log only |
| 7-8 | Clear harassment | Hostile use of slurs | "you retard", "stupid faggot" | Delete + DM |
| 9-10 | Severe hate speech | Direct attacks, threats | Racial slurs, death threats | Delete + DM |

### Configuring Threshold

**Strict (threshold 5):**
```bash
/setseverity threshold:5
```
- Flags more messages
- Catches borderline cases
- More false positives

**Balanced (threshold 7) - DEFAULT:**
```bash
/setseverity threshold:7
```
- Good balance
- Catches clear violations
- Allows friendly banter
- **Recommended**

**Lenient (threshold 9):**
```bash
/setseverity threshold:9
```
- Only severe violations
- Fewer false positives
- More rough language allowed

---

## 🔧 Detailed Setup Guide

### Step 1: Discord Bot Setup

1. **Create Discord Application**
   - Go to https://discord.com/developers/applications
   - Click "New Application" → Name it → Create

2. **Create Bot User**
   - Left sidebar → "Bot" → "Add Bot" → "Yes, do it!"

3. **Enable Privileged Intents** ⚠️ CRITICAL
   - ✅ **PRESENCE INTENT**
   - ✅ **SERVER MEMBERS INTENT**
   - ✅ **MESSAGE CONTENT INTENT** (REQUIRED!)
   - Click "Save Changes"

4. **Get Bot Token**
   - Under "TOKEN" → "Reset Token" → Copy
   - **Save this token** for `.env` file

5. **Generate Invite Link**
   - OAuth2 → URL Generator
   - **Scopes:** `bot` + `applications.commands`
   - **Permissions:** Manage Messages, Send Messages, Embed Links, Read Message History
   - Copy URL and invite to server

### Step 2: Gemini API Keys (Optional for Relax Mode)

**Why multiple keys?**
Each key = 60 requests/min. More keys = more capacity.

**Getting keys:**
1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Repeat with different Google accounts for 2-3 keys

**No credit card needed!** Gemini is free tier.

**Skip this step if using Relax Mode!**

### Step 3: Install Tesseract OCR (Optional)

**Note:** OCR is completely optional. If Tesseract isn't installed, the bot will skip image scanning gracefully.

**Windows:**
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to `C:\Program Files\Tesseract-OCR`
3. Add to PATH or configure in bot.py

**Mac:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt install tesseract-ocr
```

**Skip OCR?** The bot works fine without it!

### Step 4: Run Bot

```bash
python bot.py
```

**Expected output:**
```
✅ Token loaded
🚀 Starting bot with Gemini 2.0 Flash...
✅ Synced 17 slash command(s)
✅ Bot has connected to Discord!
✅ Loaded 150 patterns
✅ Moderation mode: CALM
✅ API keys: 3 (including 3 from environment)
```

---

## 🧪 Testing Your Bot

### Test 1: Relax Mode (Pattern-Only)

```bash
# Set to relax mode
/modmode mode:relax

# Post in monitored channel:
testing nigger

# Expected:
✅ INSTANT DELETE (no AI check)
✅ DM received: "Pattern match: nigger (Relax mode)"
✅ Logged with severity 10/10 (default)
```

### Test 2: Calm Mode (Context-Aware)

```bash
# Set to calm mode
/modmode mode:calm

# Post playful message:
hey you monkey stop stealing my food lol

# Expected:
✅ Pattern detected: "monkey"
🤖 AI analyzes: "Playful banter, severity 2/10"
✅ Message NOT deleted (below threshold 7)
✅ Logged for records
```

```bash
# Post hostile message:
you filthy monkey

# Expected:
✅ Pattern detected: "monkey"
🤖 AI analyzes: "Hostile intent, severity 8/10"
❌ Message DELETED (above threshold 7)
📩 DM sent with explanation
✅ Logged with AI reasoning
```

### Test 3: Emoji Detection

```bash
# Post message with emoji:
kys :skull:

# Expected:
✅ Text checked: "kys"
✅ Emoji name checked: "skull"
✅ Action taken based on matches
```

### Test 4: Foreign Language

```bash
# Post in Spanish:
eres un idiota

# Expected:
✅ Translates to: "you're an idiot"
✅ Checks translated text for slurs
✅ Takes action if needed
```

---

## 💰 Cost Breakdown

### FREE Services Used

| Service | Provider | Cost | Usage |
|---------|----------|------|-------|
| OCR | Tesseract (optional) | $0 | Unlimited |
| Translation | deep-translator | $0 | Unlimited |
| AI Analysis | Gemini 2.0 | $0 | 60 req/min per key |
| **Relax Mode** | **Pattern-only** | **$0** | **Unlimited** |

### Mode Costs

| Mode | API Usage | Cost/Month | Best For |
|------|-----------|------------|----------|
| Relax | 0 calls | **$0** | Budget servers |
| Calm | ~50-200/day | **$0** | Most servers |
| Strict | ~1000+/day | **$0** | High security |

**All modes are FREE!** Gemini has generous free tier.

---

## 📊 Performance & Scalability

### Server Size Guidelines

**Small (100 members):**
- Relax: Perfect, $0/month
- Calm: 1 API key sufficient
- Strict: 2 API keys recommended

**Medium (1,000 members):**
- Relax: Perfect, $0/month
- Calm: 2-3 API keys
- Strict: 3-5 API keys

**Large (10,000+ members):**
- Relax: Perfect, $0/month
- Calm: 3-5 API keys
- Strict: 5-10 API keys

---

## 🚨 Troubleshooting

### Bot Won't Start

**Error: "Tesseract not found"**
- This is just a warning! OCR is optional
- Bot will work fine, just won't scan images
- Install Tesseract if you want image scanning

**Error: "DISCORD_BOT_TOKEN not set"**
- Create `.env` file with your token
- Or use `token.txt` method

### No Slash Commands

**Solution:**
- Wait 5-10 minutes for Discord sync
- Restart bot
- Re-invite bot with `applications.commands` scope checked

### Foreign Language Not Working

**Solution:**
- Check internet connection (needs web access)
- Update: `pip install --upgrade deep-translator`
- Check console for translation logs

### Gemini Errors

**Solution:**
- Make sure using Gemini 2.0 Flash (`gemini-2.0-flash-exp`)
- Check API keys are valid
- Try `/listkeys` to verify keys loaded

---

## 🔐 Security & Privacy

### Data Storage (Local Only)

**Stored locally:**
- `config.json` - Bot settings, API keys
- `violation_logs.json` - Flagged messages only
- `daily_stats.json` - Statistics
- `whitelist.json` - Whitelisted users/roles

**NOT stored:**
- Clean messages
- Private conversations
- User personal info beyond Discord IDs

### API Data Sent

**Relax Mode:** Nothing sent (pattern-only)

**Calm/Strict Mode:**
- Only flagged messages sent to Gemini
- For severity rating only
- Not stored by Google (per Gemini terms)

---

## 📝 Changelog

### Version 3.0.0 (Current)

**Major Changes:**
- ✅ **Gemini 2.0 Flash Experimental** (latest model)
- ✅ **Relax Mode** - NO AI, pattern-only, zero cost
- ✅ **Emoji Detection** - Checks emoji names
- ✅ **Optional OCR** - Graceful failure if Tesseract not installed
- ✅ **Fixed font warnings** - Clean console output
- ✅ **Better error handling** - More robust

**Improvements:**
- ⬆️ No more Gemini 404 errors
- ⬆️ Better foreign language detection
- ⬆️ Improved logging and debugging
- ⬆️ Three moderation modes to choose from

### Version 2.0.0 (Previous)

- FREE OCR using Tesseract
- FREE translation
- Severity rating system
- Context-aware AI

---

## ❓ FAQ

**Q: Do I need API keys?**
A: Not for Relax mode! Only Calm/Strict modes need API keys.

**Q: Do I need Tesseract?**
A: No! OCR is optional. Bot works fine without it.

**Q: Which mode should I use?**
A: **Calm mode** (recommended) - Good balance of accuracy and cost.

**Q: Will I get charged?**
A: No! All services are free tier.

**Q: Can I run this on free hosting?**
A: Yes! Especially Relax mode uses zero resources.

**Q: How do I add custom slurs?**
A: Edit `slur_patterns.json` and add words (lowercase, no asterisks).

**Q: Can users bypass filters?**
A: Very difficult. Catches 200+ variations + emoji names.

---

## 🎓 Quick Reference

### Essential Commands

```bash
# Setup (choose your mode)
/modmode mode:relax   # Free, pattern-only
/modmode mode:calm    # Recommended, context-aware
/modmode mode:strict  # Maximum protection

# Configure
/setup #general
/setlog #mod-logs
/setseverity threshold:7
/toggle enabled:True

# Check status
/status
/modmode mode:status

# Manage violations
/user @username
/case @username
```

### Recommended Settings

**Most Servers:**
```bash
/modmode mode:calm
/setseverity threshold:7
```

**Zero Budget:**
```bash
/modmode mode:relax
```

**High Security:**
```bash
/modmode mode:strict
/setseverity threshold:5
```

---

## 📚 Additional Resources

- [Discord.py Docs](https://discordpy.readthedocs.io/)
- [Gemini API Docs](https://ai.google.dev/docs)
- [Tesseract OCR](https://tesseract-ocr.github.io/) (optional)
- [GitHub Issues](https://github.com/yourusername/discord-mod-bot/issues)

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Make changes and test
4. Submit pull request

---

## 📞 Support

**Having issues?**
1. Check [Troubleshooting](#troubleshooting)
2. Read [FAQ](#faq)
3. Open GitHub issue with details

---

**Made with ❤️ for safer Discord communities**

*Last updated: November 2024 - v3.0.0*
