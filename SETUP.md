# 🚀 Complete Setup Guide - Free Version

## 🎯 What's New - FREE System

### ✅ Changes Made:
1. **FREE OCR** - Using Tesseract (no Google Cloud needed!)
2. **FREE Translation** - Using deep-translator (no API key needed!)
3. **Smart AI System** - Only uses Gemini when slurs detected
4. **Severity Rating** - 1-10 scale, configurable threshold
5. **Context Aware** - AI knows "you monkey" playfully is fine

### 💰 Cost Breakdown:
- OCR: **FREE** (Tesseract, local)
- Translation: **FREE** (deep-translator, no API)
- AI: **FREE** (Gemini, 60 req/min per key)
- Total: **$0/month**

---

## 📁 Files You Need (8 Files)

```
discord-mod-bot/
├── bot.py                      ✅ Main bot (updated)
├── pattern_detector.py         📥 Pattern matching
├── slur_patterns.json          📥 Your slur list
├── requirements.txt            📥 Dependencies (updated)
├── .env                        📥 Your tokens
├── config.json                 📥 Bot config
├── whitelist.json              📥 Whitelist data
└── .gitignore                  📥 Git protection
```

---

## 🔧 Step 1: Install Tesseract OCR (5 minutes)

Tesseract is FREE, open-source OCR that runs locally (no API needed).

### Windows:
1. Download installer: https://github.com/UB-Mannheim/tesseract/wiki
2. Download `tesseract-ocr-w64-setup-5.3.3.exe`
3. Run installer
4. **IMPORTANT:** Note install path (usually `C:\Program Files\Tesseract-OCR`)
5. Add to PATH:
   - Search "Environment Variables"
   - Edit "Path" variable
   - Add `C:\Program Files\Tesseract-OCR`
6. Restart terminal

### Mac:
```bash
brew install tesseract
```

### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install tesseract-ocr
```

### Verify Installation:
```bash
tesseract --version
```
Should show: `tesseract 5.x.x`

---

## 🔧 Step 2: Install Python Dependencies (2 minutes)

```bash
# Navigate to bot folder
cd /path/to/discord-mod-bot

# Install requirements
pip install -r requirements.txt
```

**What gets installed:**
- `discord.py` - Discord API
- `google-generativeai` - Gemini AI (FREE tier)
- `Pillow` - Image processing
- `pytesseract` - Tesseract wrapper
- `deep-translator` - FREE translation (no API key!)
- `matplotlib` - Graphs
- `pytz` - Timezones
- `python-dotenv` - Environment variables

---

## 🔧 Step 3: Get API Keys (3 minutes)

### Discord Bot Token:
1. https://discord.com/developers/applications
2. Your application → Bot → Copy Token
3. Enable intents:
   - ✅ PRESENCE INTENT
   - ✅ SERVER MEMBERS INTENT
   - ✅ MESSAGE CONTENT INTENT ⚠️ **REQUIRED**

### Gemini API Keys (2-3 keys recommended):
1. https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Repeat with different Google accounts for more keys

**No Google Cloud needed!** Just Gemini API keys.

---

## 🔧 Step 4: Configure .env File (2 minutes)

Create `.env` file:
```bash
DISCORD_BOT_TOKEN=your_discord_token_here
```

**That's it!** No Google Cloud credentials needed.

---

## 🔧 Step 5: Run the Bot (1 minute)

```bash
python bot.py
```

**Expected output:**
```
BotName#1234 has connected to Discord!
Loaded 150 patterns
Severity threshold: 7/10
API keys: 0
```

Bot should show 🟢 ONLINE in Discord!

---

## 🔧 Step 6: Configure in Discord (3 minutes)

```bash
# Add Gemini API keys
/addkey api_key:YOUR_KEY_1
/addkey api_key:YOUR_KEY_2

# Set channels
/setlog #mod-logs
/setup #general

# Set severity threshold (7 = default)
/setseverity threshold:7

# Whitelist mods
/whitelist_role @Moderator

# Enable bot
/toggle enabled:True

# Check status
/status
```

---

## 🎯 Understanding Severity System

### How It Works:

1. **Pattern Detection** → Checks if message contains slurs
2. **AI Analysis** → If slurs found, asks Gemini to rate severity
3. **Threshold Check** → Only punishes if severity ≥ threshold
4. **Action** → Deletes message, DMs user, logs violation

### Severity Scale (1-10):

| Severity | Description | Example | Action |
|----------|-------------|---------|--------|
| 1-3 | Playful, no malice | "you monkey" between friends | Log only |
| 4-6 | Potentially inappropriate | Mild insults | Log only |
| 7-8 | Clear slurs, harassment | Slurs with negative intent | Delete + DM |
| 9-10 | Severe hate speech, threats | Direct attacks, death threats | Delete + DM |

### Configurable Threshold:

```bash
# Strict (flag everything)
/setseverity threshold:5

# Balanced (default)
/setseverity threshold:7

# Lenient (only severe)
/setseverity threshold:9
```

### Example Scenarios:

**Scenario 1: Playful Banter**
```
User: "dude you're such a monkey lmao"
```
- ✅ Detected: "monkey"
- 🤖 AI rates: 2/10 (playful)
- ℹ️ Logged but NOT deleted
- ✅ No DM sent

**Scenario 2: Clear Insult**
```
User: "you're a fucking retard"
```
- ✅ Detected: "retard"
- 🤖 AI rates: 8/10 (hostile)
- ❌ Deleted immediately
- 📩 User gets DM warning
- 📊 Logged to mod channel

**Scenario 3: Severe Slur**
```
User: "nigger"
```
- ✅ Detected: "nigger"
- 🤖 AI rates: 10/10 (severe slur)
- ❌ Deleted immediately
- 📩 User gets DM
- 📊 Logged with high severity flag

---

## 🧪 Testing the Bot

### Test 1: Playful Message (Should NOT Delete)
```
hey you monkey stop stealing my food lol
```
**Expected:**
- ✅ Logged to #mod-logs
- ✅ Shows severity 2-3/10
- ✅ Message stays (not deleted)
- ✅ No DM sent

### Test 2: Clear Slur (SHOULD Delete)
```
Testing with nigger
```
**Expected:**
- ✅ Detected immediately
- ✅ AI rates 10/10
- ✅ Message deleted
- ✅ You get DM
- ✅ Logged to #mod-logs

### Test 3: Context-Dependent
```
stop being such a retard
```
**Expected:**
- ✅ AI rates 7-8/10 (hostile use)
- ✅ Deleted if threshold ≤ 8
- ✅ DM + log

### Test 4: Whitelisted User
Mod posts: "nigger"
**Expected:**
- ✅ Message stays (whitelisted)
- ✅ Not logged
- ✅ No action taken

### Test 5: Image OCR
Upload image with text: "you're a faggot"
**Expected:**
- ✅ OCR extracts text
- ✅ Detects "faggot"
- ✅ AI rates severity
- ✅ Deleted if ≥ threshold

---

## 📊 How FREE Translation Works

### deep-translator Library:
- Uses Google Translate (unofficial API)
- No API key needed
- No rate limits (reasonable use)
- Supports 100+ languages
- Completely free

### Usage in Bot:
```python
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source='auto', target='en')
translated = translator.translate("Hola amigo")
# Returns: "Hello friend"
```

### Advantages:
- ✅ FREE forever
- ✅ No API key needed
- ✅ No rate limits
- ✅ Auto-detects language
- ✅ 100+ languages supported

---

## 🖼️ How FREE OCR Works

### Tesseract OCR:
- Open-source, maintained by Google
- Runs locally on your machine
- No API calls, no costs
- Supports 100+ languages
- Very accurate for clear text

### What It Can Read:
- ✅ Memes with text
- ✅ Screenshots
- ✅ Photos with clear text
- ✅ Signs in images
- ⚠️ Struggles with: handwriting, very small text, stylized fonts

### Usage in Bot:
```python
import pytesseract
from PIL import Image

image = Image.open("screenshot.png")
text = pytesseract.image_to_string(image)
# Returns extracted text
```

---

## 🤖 How AI Severity Check Works

### Only Used When Slurs Detected:
```
Message → Check patterns → Slur found? 
    → NO: Skip AI, message is clean ✅
    → YES: Ask Gemini to rate severity 1-10
        → < threshold: Log only
        → ≥ threshold: Delete + DM + Log
```

### Gemini Prompt:
```
You are a content moderation assistant.
Detected words: [list of slurs found]
Full message: "[the message]"

Rate severity 1-10:
1-3: Playful, no malice
4-6: Potentially inappropriate
7-8: Clear harassment
9-10: Severe hate speech, threats

Consider context, tone, and intent.
```

### API Usage:
- **Without slurs:** 0 API calls (pattern check only)
- **With slurs:** 1 API call per message
- **Typical server:** 10-20 API calls/day
- **Free tier:** 60 requests/minute per key
- **Cost:** $0/month

---

## 🎮 All Commands

### Configuration:
```bash
/setup #channel              # Set monitored channel
/setlog #channel             # Set log channel
/toggle enabled:True         # Enable/disable
/setseverity threshold:7     # Set severity threshold (NEW!)
/status                      # Check configuration
```

### API Keys:
```bash
/addkey api_key:xxx          # Add Gemini key
/listkeys                    # View all keys
/removekey key_number:1      # Remove key
```

### Whitelist:
```bash
/whitelist_user @user        # Whitelist user
/whitelist_role @role        # Whitelist role
/unwhitelist_user @user      # Remove user
/unwhitelist_role @role      # Remove role
/whitelist_list              # View whitelist
```

### Moderation:
```bash
/user @username              # Check violation history
/forcereport                 # Generate report now
```

---

## 🚨 Troubleshooting

### Tesseract Not Found:
**Error:** `pytesseract.pytesseract.TesseractNotFoundError`

**Fix (Windows):**
```python
# Add to top of bot.py after imports
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**Fix (Mac/Linux):**
```bash
which tesseract
# Add path to bot.py if needed
```

### Translation Errors:
**Error:** `deep_translator` fails

**Fix:**
- Check internet connection (needs to access Google Translate)
- Try: `pip install --upgrade deep-translator`
- Fallback: Bot will use original text if translation fails

### OCR Not Reading Images:
- Image quality too low
- Text too small (<12px font)
- Heavily stylized fonts
- **This is normal** - OCR works best on clear text

### Severity Always 10:
- No Gemini API keys added
- All keys rate-limited
- Bot defaults to severity 10 if AI fails

---

## 📈 Performance Expectations

### Small Server (100 members):
- **Scans:** 1,000 messages/day
- **Slurs detected:** 5-10/day
- **Gemini API calls:** 5-10/day
- **Cost:** $0

### Medium Server (1,000 members):
- **Scans:** 10,000 messages/day
- **Slurs detected:** 20-50/day
- **Gemini API calls:** 20-50/day
- **Cost:** $0

### Large Server (10,000 members):
- **Scans:** 100,000 messages/day
- **Slurs detected:** 100-200/day
- **Gemini API calls:** 100-200/day
- **Cost:** $0 (with 2-3 API keys)

---

## ✅ Setup Checklist

- [ ] Tesseract OCR installed
- [ ] Python dependencies installed
- [ ] Discord bot token obtained
- [ ] 2-3 Gemini API keys obtained
- [ ] .env file created
- [ ] Bot runs without errors
- [ ] Bot shows online in Discord
- [ ] Commands added via /addkey
- [ ] Channels configured
- [ ] Severity threshold set
- [ ] Mods whitelisted
- [ ] Bot enabled with /toggle
- [ ] Tested with sample messages
- [ ] Verified severity system works

---

## 🎉 You're Done!

Your bot now:
- ✅ Uses FREE OCR (Tesseract)
- ✅ Uses FREE translation (deep-translator)
- ✅ Smart AI only when needed
- ✅ Rates severity 1-10
- ✅ Understands context
- ✅ Configurable threshold
- ✅ Costs $0/month

**Total cost: FREE! 🎊**
