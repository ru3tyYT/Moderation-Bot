# bot.py - Complete version with ALL features for dedicated hosting (BotHosting.net/EAS)
import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import os
import google.generativeai as genai
import asyncio
from datetime import datetime, time
import pytz
import io

# Fix matplotlib warnings
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'DejaVu Sans'

from collections import defaultdict
import aiohttp
from PIL import Image
import pytesseract
import emoji as emoji_lib
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
import re

# Keepalive for hosting stability
try:
    from keepalive import keep_alive, start_self_ping
    KEEPALIVE_AVAILABLE = True
except ImportError:
    KEEPALIVE_AVAILABLE = False

load_dotenv()

from pattern_detector import PatternDetector# bot.py - Fixed version with Gemini 2.0 Flash and Relax Mode
import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import os
import google.generativeai as genai
import asyncio
from datetime import datetime, time
import pytz
import io

# Fix matplotlib warnings
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'DejaVu Sans'

from collections import defaultdict
import aiohttp
from PIL import Image
try:
    import pytesseract
    # Try to run tesseract to verify it's actually installed
    try:
        pytesseract.get_tesseract_version()
        TESSERACT_AVAILABLE = True
        print("✅ Tesseract OCR detected and working")
    except Exception as e:
        TESSERACT_AVAILABLE = False
        print(f"⚠️ Tesseract not properly configured: {e}")
        print("ℹ️ OCR disabled (optional feature) - Install from: https://github.com/tesseract-ocr/tesseract")
except ImportError:
    TESSERACT_AVAILABLE = False
    print("⚠️ pytesseract package not installed - OCR disabled (optional feature)")

from deep_translator import GoogleTranslator
from dotenv import load_dotenv
import re

load_dotenv()

from pattern_detector import PatternDetector

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
detector = PatternDetector()

CONFIG_FILE = "config.json"
SLURS_FILE = "slur_patterns.json"
LOGS_FILE = "violation_logs.json"
STATS_FILE = "daily_stats.json"
WHITELIST_FILE = "whitelist.json"

config = {
    "enabled": False,
    "monitored_channel_id": None,
    "log_channel_id": None,
    "gemini_api_keys": [],
    "current_key_index": 0,
    "severity_threshold": 7,
    "mod_mode": "calm"  # calm, strict, or relax
}

slur_patterns = []
violation_logs = []
whitelist = {"users": [], "roles": []}
daily_stats = {
    "messages_scanned": 0,
    "messages_flagged": 0,
    "users_caught": set(),
    "hourly_scans": defaultdict(int),
    "date": str(datetime.now().date())
}

def load_config():
    global config
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            loaded = json.load(f)
            config.update(loaded)
    if "severity_threshold" not in config:
        config["severity_threshold"] = 7
    if "mod_mode" not in config:
        config["mod_mode"] = "calm"

def save_config():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def load_slur_patterns():
    global slur_patterns
    patterns = []
    if os.path.exists(SLURS_FILE):
        try:
            with open(SLURS_FILE, 'r') as f:
                data = json.load(f)
            for category, words in data.items():
                if not category.startswith('_'):
                    patterns.extend([w for w in words if not w.startswith('_')])
            slur_patterns = patterns
            print(f"✅ Loaded {len(slur_patterns)} patterns from database")
        except Exception as e:
            print(f"❌ Error loading patterns: {e}")
    else:
        print(f"⚠️ Warning: {SLURS_FILE} not found")

def load_whitelist():
    global whitelist
    if os.path.exists(WHITELIST_FILE):
        with open(WHITELIST_FILE, 'r') as f:
            whitelist = json.load(f)
    else:
        whitelist = {"users": [], "roles": []}

def save_whitelist():
    with open(WHITELIST_FILE, 'w') as f:
        json.dump(whitelist, f, indent=4)

def load_api_keys_from_env():
    """Load Gemini API keys from environment variables"""
    env_keys = []
    
    for i in range(1, 21):
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key and key.strip():
            env_keys.append(key.strip())
    
    single_key = os.getenv("GEMINI_API_KEY")
    if single_key and single_key.strip() and single_key not in env_keys:
        env_keys.append(single_key.strip())
    
    if env_keys:
        added_count = 0
        for key in env_keys:
            if key not in config["gemini_api_keys"]:
                config["gemini_api_keys"].append(key)
                added_count += 1
        
        if added_count > 0:
            save_config()
            print(f"✅ Loaded {added_count} API key(s) from environment")
    
    return len(env_keys)

def is_whitelisted(user: discord.Member) -> bool:
    if user.id in whitelist["users"]:
        return True
    user_role_ids = [role.id for role in user.roles]
    for role_id in whitelist["roles"]:
        if role_id in user_role_ids:
            return True
    return False

def load_logs():
    global violation_logs
    if os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, 'r') as f:
            violation_logs = json.load(f)

def save_logs():
    with open(LOGS_FILE, 'w') as f:
        json.dump(violation_logs, f, indent=4)

def load_stats():
    global daily_stats
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            data = json.load(f)
            data["users_caught"] = set(data.get("users_caught", []))
            if data.get("date") != str(datetime.now().date()):
                daily_stats = {
                    "messages_scanned": 0,
                    "messages_flagged": 0,
                    "users_caught": set(),
                    "hourly_scans": defaultdict(int),
                    "date": str(datetime.now().date())
                }
            else:
                daily_stats = data
                daily_stats["hourly_scans"] = defaultdict(int, data.get("hourly_scans", {}))

def save_stats():
    stats_to_save = daily_stats.copy()
    stats_to_save["users_caught"] = list(daily_stats["users_caught"])
    with open(STATS_FILE, 'w') as f:
        json.dump(stats_to_save, f, indent=4)

def get_current_gemini_model():
    """FIXED: Use gemini-2.0-flash-exp (latest model)"""
    if not config["gemini_api_keys"]:
        return None
    current_key = config["gemini_api_keys"][config["current_key_index"]]
    genai.configure(api_key=current_key)
    return genai.GenerativeModel('gemini-2.0-flash-exp')

def rotate_api_key():
    if len(config["gemini_api_keys"]) <= 1:
        return False
    config["current_key_index"] = (config["current_key_index"] + 1) % len(config["gemini_api_keys"])
    save_config()
    print(f"🔄 Rotated to API key #{config['current_key_index'] + 1}")
    return True

def contains_slur(text):
    """Check if text contains potential slurs (with plural/variant support)"""
    if not text:
        return False, []
    
    # Check original text
    found, matches = detector.check_text(text, slur_patterns)
    if found:
        return True, matches
    
    # Check normalized text
    normalized = detector.normalize_text(text)
    found_norm, matches_norm = detector.check_text(normalized, slur_patterns)
    
    # Also check for common plurals and variants
    all_matches = list(set(matches + matches_norm))
    
    # Manual plural check for missed cases
    text_lower = text.lower()
    for pattern in slur_patterns:
        # Check exact match
        if pattern in text_lower:
            if pattern not in all_matches:
                all_matches.append(pattern)
        # Check plural (add 's')
        if pattern + 's' in text_lower:
            if pattern not in all_matches:
                all_matches.append(pattern)
        # Check with apostrophe s ('s)
        if pattern + "'s" in text_lower:
            if pattern not in all_matches:
                all_matches.append(pattern)
        # Check with -es ending
        if pattern + 'es' in text_lower:
            if pattern not in all_matches:
                all_matches.append(pattern)
    
    return len(all_matches) > 0, all_matches

async def check_severity_with_gemini(text, detected_words):
    """Use Gemini to rate severity 1-10"""
    max_retries = len(config["gemini_api_keys"]) if config["gemini_api_keys"] else 1
    
    for attempt in range(max_retries):
        try:
            gemini_model = get_current_gemini_model()
            if not gemini_model:
                return {"is_harmful": True, "severity": 10, "reason": "No API key", "context": "unknown"}
            
            prompt = f"""You are a content moderation assistant. Analyze this message for harmful intent.

Detected words: {', '.join(detected_words)}
Full message: "{text}"

Rate the severity from 1-10:
- 1-3: Playful banter, friendly joking, no malice
- 4-6: Potentially inappropriate but context matters
- 7-8: Clear insults, slurs with negative intent
- 9-10: Severe hate speech, death threats

Respond ONLY with valid JSON:
{{
    "is_harmful": true/false,
    "severity": 1-10,
    "reason": "brief explanation",
    "context": "playful/neutral/hostile"
}}"""

            response = gemini_model.generate_content(prompt)
            result_text = response.text.strip()
            
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            result["severity"] = int(result.get("severity", 10))
            
            print(f"✅ AI Analysis: Severity {result['severity']}/10 - {result.get('context')} - {result.get('reason')}")
            
            return result
            
        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "quota" in error_msg or "rate limit" in error_msg:
                print(f"⚠️ API key #{config['current_key_index'] + 1} rate limited. Rotating...")
                if rotate_api_key():
                    continue
            else:
                print(f"❌ Gemini API error: {e}")
            
            if attempt == max_retries - 1:
                return {"is_harmful": True, "severity": 10, "reason": f"API error: {str(e)}", "context": "unknown"}
    
    return {"is_harmful": True, "severity": 10, "reason": "All keys exhausted", "context": "unknown"}

async def translate_text_free(text):
    """IMPROVED: Better translation with error handling"""
    if not text or not text.strip():
        return text, 'unknown'
    
    try:
        translator = GoogleTranslator(source='auto', target='en')
        translated = translator.translate(text)
        
        source_lang = 'auto'
        if translated.strip().lower() == text.strip().lower():
            source_lang = 'en'
        
        return translated, source_lang
        
    except Exception as e:
        print(f"⚠️ Translation error: {e}")
        return text, 'unknown'

async def ocr_image_free(image_url):
    """Extract text from image using Tesseract OCR (optional)"""
    if not TESSERACT_AVAILABLE:
        return None
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status != 200:
                    return None
                image_data = await resp.read()
        
        image = Image.open(io.BytesIO(image_data))
        text = pytesseract.image_to_string(image)
        
        if text and text.strip():
            return text.strip()
        return None
        
    except Exception as e:
        print(f"⚠️ OCR error (optional feature): {e}")
        return None

def extract_emoji_names(text):
    """Extract ALL emoji names from Discord emoji format - COMPREHENSIVE"""
    if not text:
        return []
    
    emoji_names = []
    
    # Pattern 1: Standard Discord emojis :emoji_name:
    # Matches: :skull:, :middle_finger:, :kys:, etc.
    standard_pattern = r':([a-zA-Z0-9_\-]+):'
    standard_matches = re.findall(standard_pattern, text)
    emoji_names.extend(standard_matches)
    
    # Pattern 2: Custom Discord emojis <:name:id> or <a:name:id>
    # Matches: <:pepe:123456>, <a:dance:789012>
    custom_pattern = r'<a?:([a-zA-Z0-9_\-]+):\d+>'
    custom_matches = re.findall(custom_pattern, text)
    emoji_names.extend(custom_matches)
    
    # Pattern 3: Unicode emoji (actual emoji characters) - OPTIONAL
    # This catches 😀 😂 💀 🖕 etc. - only if emoji library available
    try:
        import emoji as emoji_lib
        # Extract emoji and get their names
        for char in text:
            try:
                if char in emoji_lib.EMOJI_DATA:
                    emoji_name = emoji_lib.EMOJI_DATA[char].get('en', '').replace(':', '').strip()
                    if emoji_name:
                        emoji_names.append(emoji_name)
            except:
                # Skip this character if any error
                continue
    except ImportError:
        # Emoji library not installed - that's OK, skip unicode emoji detection
        pass
    except Exception:
        # Any other error - skip unicode emoji detection
        pass
    
    # Process all emoji names into multiple variations
    processed_names = []
    for name in emoji_names:
        if not name:
            continue
            
        # Original name
        processed_names.append(name)
        
        # Lowercase
        processed_names.append(name.lower())
        
        # Uppercase
        processed_names.append(name.upper())
        
        # Replace underscores with spaces
        processed_names.append(name.replace('_', ' '))
        processed_names.append(name.lower().replace('_', ' '))
        processed_names.append(name.upper().replace('_', ' '))
        
        # Replace hyphens with spaces
        processed_names.append(name.replace('-', ' '))
        processed_names.append(name.lower().replace('-', ' '))
        
        # Remove special characters
        clean_name = name.replace('_', '').replace('-', '')
        processed_names.append(clean_name)
        processed_names.append(clean_name.lower())
        
        # Split by underscore/hyphen and add individual words
        parts = re.split(r'[_\-]', name)
        for part in parts:
            if len(part) > 1:  # Skip single characters
                processed_names.append(part)
                processed_names.append(part.lower())
    
    # Remove duplicates while preserving order
    seen = set()
    unique_names = []
    for name in processed_names:
        if name and name not in seen:
            seen.add(name)
            unique_names.append(name)
    
    return unique_names

async def log_violation(message, reason, translated_text, severity_result=None, ocr_text=None):
    violation = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": message.author.id,
        "user_name": str(message.author),
        "channel_id": message.channel.id,
        "channel_name": message.channel.name,
        "message_content": message.content,
        "translated_text": translated_text,
        "ocr_text": ocr_text,
        "reason": reason,
        "severity": severity_result.get("severity") if severity_result else 10,
        "ai_analysis": severity_result,
        "attachments": [att.url for att in message.attachments]
    }
    
    violation_logs.append(violation)
    save_logs()
    
    daily_stats["messages_flagged"] += 1
    daily_stats["users_caught"].add(message.author.id)
    save_stats()
    
    if not config.get("log_channel_id"):
        return
    
    log_channel = bot.get_channel(config["log_channel_id"])
    if not log_channel:
        return
    
    severity = severity_result.get("severity", 10) if severity_result else 10
    if severity >= 9:
        color = discord.Color.dark_red()
    elif severity >= 7:
        color = discord.Color.red()
    elif severity >= 5:
        color = discord.Color.orange()
    else:
        color = discord.Color.yellow()
    
    embed = discord.Embed(
        title=f"🚨 Violation Detected - Severity {severity}/10",
        color=color,
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="User", value=f"{message.author.mention} ({message.author.id})", inline=False)
    embed.add_field(name="Channel", value=message.channel.mention, inline=True)
    embed.add_field(name="Severity", value=f"**{severity}/10**", inline=True)
    
    if message.content:
        original_content = message.content[:1000] if len(message.content) <= 1000 else message.content[:1000] + "..."
        embed.add_field(name="Original Message", value=f"```{original_content}```", inline=False)
    
    if translated_text and translated_text != message.content:
        translated_preview = translated_text[:1000] if len(translated_text) <= 1000 else translated_text[:1000] + "..."
        embed.add_field(name="Translated", value=f"```{translated_preview}```", inline=False)
    
    if ocr_text:
        ocr_preview = ocr_text[:1000] if len(ocr_text) <= 1000 else ocr_text[:1000] + "..."
        embed.add_field(name="Text from Image", value=f"```{ocr_preview}```", inline=False)
    
    if severity_result:
        embed.add_field(
            name="AI Analysis", 
            value=f"**Context:** {severity_result.get('context', 'unknown')}\n**Reason:** {severity_result.get('reason', 'N/A')}", 
            inline=False
        )
    
    if message.attachments:
        embed.add_field(name="Attachments", value="\n".join([att.url for att in message.attachments]), inline=False)
        for att in message.attachments:
            if att.content_type and att.content_type.startswith('image'):
                embed.set_thumbnail(url=att.url)
                break
    
    threshold = config.get("severity_threshold", 7)
    if severity >= threshold:
        embed.add_field(name="⚠️ Action Taken", value=f"Message deleted (severity {severity} ≥ threshold {threshold})", inline=False)
    else:
        embed.add_field(name="ℹ️ No Action", value=f"Logged only (severity {severity} < threshold {threshold})", inline=False)
    
    embed.set_footer(text=f"User ID: {message.author.id} | Mode: {config.get('mod_mode', 'calm')}")
    
    await log_channel.send(embed=embed)

async def generate_daily_report():
    if not config.get("log_channel_id"):
        return
    
    log_channel = bot.get_channel(config["log_channel_id"])
    if not log_channel:
        return
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'Daily Moderation Report - {daily_stats["date"]}', fontsize=16, fontweight='bold')
    
    categories = ['Messages\nScanned', 'Messages\nFlagged', 'Unique\nUsers']
    values = [daily_stats["messages_scanned"], daily_stats["messages_flagged"], len(daily_stats["users_caught"])]
    colors = ['#5865F2', '#ED4245', '#FEE75C']
    ax1.bar(categories, values, color=colors, edgecolor='black', linewidth=1.5)
    ax1.set_title('Overall Statistics', fontweight='bold')
    ax1.set_ylabel('Count')
    for i, v in enumerate(values):
        ax1.text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')
    
    hours = list(range(24))
    scans_per_hour = [daily_stats["hourly_scans"].get(str(h), 0) for h in hours]
    ax2.plot(hours, scans_per_hour, marker='o', linewidth=2, markersize=6, color='#5865F2')
    ax2.fill_between(hours, scans_per_hour, alpha=0.3, color='#5865F2')
    ax2.set_title('Messages Scanned Per Hour', fontweight='bold')
    ax2.set_xlabel('Hour (24h format)')
    ax2.set_ylabel('Messages Scanned')
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(range(0, 24, 2))
    
    if daily_stats["messages_scanned"] > 0:
        clean = daily_stats["messages_scanned"] - daily_stats["messages_flagged"]
        flagged = daily_stats["messages_flagged"]
        sizes = [clean, flagged]
        labels = [f'Clean\n({clean})', f'Flagged\n({flagged})']
        colors_pie = ['#57F287', '#ED4245']
        explode = (0, 0.1)
        ax3.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%', 
                startangle=90, explode=explode, textprops={'fontweight': 'bold'})
        ax3.set_title('Clean vs Flagged Messages', fontweight='bold')
    else:
        ax3.text(0.5, 0.5, 'No data yet', ha='center', va='center', fontsize=12)
        ax3.set_title('Clean vs Flagged Messages', fontweight='bold')
    
    ax4.axis('off')
    summary_text = f"""
    DAILY SUMMARY
    ━━━━━━━━━━━━━━━━━━━━━━━━━
    
    Messages Scanned: {daily_stats["messages_scanned"]}
    Messages Flagged: {daily_stats["messages_flagged"]}
    Unique Users: {len(daily_stats["users_caught"])}
    Flag Rate: {(daily_stats["messages_flagged"] / daily_stats["messages_scanned"] * 100) if daily_stats["messages_scanned"] > 0 else 0:.2f}%
    Peak Hour: {max(daily_stats["hourly_scans"].items(), key=lambda x: x[1])[0] if daily_stats["hourly_scans"] else "N/A"}:00
    API Keys: {len(config["gemini_api_keys"])}
    Whitelisted: {len(whitelist["users"])} users, {len(whitelist["roles"])} roles
    Severity Threshold: {config.get("severity_threshold", 7)}/10
    Moderation Mode: {config.get("mod_mode", "calm").upper()}
    """
    ax4.text(0.1, 0.9, summary_text, fontsize=11, verticalalignment='top', 
             family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    
    file = discord.File(buffer, filename='daily_report.png')
    embed = discord.Embed(title="📊 Daily Moderation Report", description=f"Report for **{daily_stats['date']}**",
                          color=discord.Color.blue(), timestamp=datetime.utcnow())
    embed.set_image(url="attachment://daily_report.png")
    embed.set_footer(text="Next report in 24 hours")
    
    await log_channel.send(embed=embed, file=file)
    
    daily_stats["messages_scanned"] = 0
    daily_stats["messages_flagged"] = 0
    daily_stats["users_caught"] = set()
    daily_stats["hourly_scans"] = defaultdict(int)
    daily_stats["date"] = str(datetime.now().date())
    save_stats()

@tasks.loop(time=time(hour=5, minute=0, tzinfo=pytz.timezone('US/Eastern')))
async def daily_report_task():
    await generate_daily_report()

@bot.event
async def on_ready():
    load_config()
    load_slur_patterns()
    load_logs()
    load_stats()
    load_whitelist()
    
    env_key_count = load_api_keys_from_env()
    
    try:
        synced = await bot.tree.sync()
        print(f'✅ Synced {len(synced)} slash command(s)')
    except Exception as e:
        print(f'❌ Failed to sync commands: {e}')
    
    daily_report_task.start()
    print(f'✅ {bot.user} has connected to Discord!')
    print(f'✅ Loaded {len(slur_patterns)} patterns')
    print(f'✅ Whitelisted: {len(whitelist["users"])} users, {len(whitelist["roles"])} roles')
    print(f'✅ Severity threshold: {config.get("severity_threshold", 7)}/10')
    print(f'✅ Moderation mode: {config.get("mod_mode", "calm").upper()}')
    print(f'✅ API keys: {len(config["gemini_api_keys"])} (including {env_key_count} from environment)')
    
    # Optional features status
    if TESSERACT_AVAILABLE:
        print(f'✅ OCR: Enabled')
    
    if config.get("mod_mode") == "relax":
        print(f'ℹ️ RELAX MODE: Pattern-only detection, no AI usage')

@bot.tree.command(name="setseverity", description="Set severity threshold")
@app_commands.describe(threshold="Minimum severity to delete (1-10, default 7)")
async def setseverity(interaction: discord.Interaction, threshold: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return
    
    if threshold < 1 or threshold > 10:
        await interaction.response.send_message("❌ Must be 1-10.", ephemeral=True)
        return
    
    config["severity_threshold"] = threshold
    save_config()
    
    mode_desc = "🔴 Strict" if threshold <= 5 else ("🟡 Balanced" if threshold <= 7 else "🟢 Lenient")
    
    embed = discord.Embed(
        title="⚖️ Threshold Updated",
        description=f"**{threshold}/10** ({mode_desc})",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="Effect",
        value=f"Messages rated **≥{threshold}/10** will be deleted\nBelow {threshold}/10 logged only",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="modmode", description="Set moderation mode")
@app_commands.describe(mode="Mode to set")
@app_commands.choices(mode=[
    app_commands.Choice(name="strict - Check ALL with AI", value="strict"),
    app_commands.Choice(name="calm - Check detected only with AI", value="calm"),
    app_commands.Choice(name="relax - NO AI, pattern-only", value="relax"),
    app_commands.Choice(name="status - View current mode", value="status")
])
async def modmode(interaction: discord.Interaction, mode: str):
    if mode == "status":
        current = config.get("mod_mode", "calm")
        embed = discord.Embed(title="⚙️ Moderation Mode Status", color=discord.Color.blue())
        embed.add_field(name="Current Mode", value=f"**{current.upper()}**", inline=False)
        
        if current == "strict":
            embed.add_field(
                name="📋 Description",
                value="• ALL messages sent to AI\n• Highest accuracy\n• Most API usage",
                inline=False
            )
        elif current == "calm":
            embed.add_field(
                name="📋 Description",
                value="• Only detected slurs sent to AI\n• Good accuracy\n• Moderate API usage",
                inline=False
            )
        else:  # relax
            embed.add_field(
                name="📋 Description",
                value="• NO AI checking\n• Pattern-only detection\n• ZERO API usage\n• Instant deletion on match",
                inline=False
            )
        
        embed.add_field(name="Threshold", value=f"{config.get('severity_threshold', 7)}/10", inline=True)
        embed.add_field(name="API Keys", value=f"{len(config['gemini_api_keys'])}", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return
    
    config["mod_mode"] = mode
    save_config()
    
    if mode == "strict":
        embed = discord.Embed(
            title="🔴 Strict Mode Enabled",
            description="ALL messages will be checked with AI",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Details",
            value="• Every message → AI analysis\n• Maximum protection\n• High API usage",
            inline=False
        )
    elif mode == "calm":
        embed = discord.Embed(
            title="🟡 Calm Mode Enabled",
            description="Only detected slurs checked with AI",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="Details",
            value="• Pattern detection first\n• AI only for flagged messages\n• Moderate API usage",
            inline=False
        )
    else:  # relax
        embed = discord.Embed(
            title="🟢 Relax Mode Enabled",
            description="NO AI - Pattern-only detection",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Details",
            value="• NO AI checking\n• Instant delete on pattern match\n• ZERO API usage\n• No context analysis",
            inline=False
        )
        embed.add_field(
            name="⚠️ Warning",
            value="This mode may have more false positives since there's no AI context analysis",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="case", description="View user violation logs")
@app_commands.describe(user="User to check")
async def case(interaction: discord.Interaction, user: discord.User):
    user_violations = [log for log in violation_logs if log["user_id"] == user.id]
    
    if not user_violations:
        embed = discord.Embed(title="📋 No Cases", description=f"{user.mention} has clean record",
                              color=discord.Color.green())
        embed.set_thumbnail(url=user.display_avatar.url)
        if user.id in whitelist["users"]:
            embed.add_field(name="Status", value="⚪ Whitelisted", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    embed = discord.Embed(title=f"📋 Cases: {user.name}",
                          description=f"**ID:** {user.id}\n**Total:** {len(user_violations)}",
                          color=discord.Color.red())
    embed.set_thumbnail(url=user.display_avatar.url)
    
    severities = [v.get("severity", 0) for v in user_violations]
    avg = sum(severities) / len(severities) if severities else 0
    embed.add_field(name="Stats", value=f"Avg: {avg:.1f}/10\nMax: {max(severities) if severities else 0}/10", inline=False)
    
    for i, v in enumerate(user_violations[-5:], 1):
        case_num = len(user_violations) - 5 + i
        timestamp = datetime.fromisoformat(v["timestamp"]).strftime("%Y-%m-%d %H:%M")
        severity = v.get("severity", "?")
        content = v["message_content"][:100] + "..." if len(v["message_content"]) > 100 else v["message_content"]
        
        embed.add_field(name=f"Case #{case_num}",
                        value=f"**{timestamp}** | Severity: {severity}/10\n`{content}`", inline=False)
    
    if len(user_violations) > 5:
        embed.set_footer(text=f"Showing last 5 of {len(user_violations)}")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="whitelist_user")
@app_commands.describe(user="User to whitelist")
async def whitelist_user(interaction: discord.Interaction, user: discord.User):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return
    if user.id in whitelist["users"]:
        await interaction.response.send_message(f"⚠️ Already whitelisted.", ephemeral=True)
        return
    whitelist["users"].append(user.id)
    save_whitelist()
    await interaction.response.send_message(f"✅ Whitelisted {user.mention}", ephemeral=True)

@bot.tree.command(name="unwhitelist_user")
@app_commands.describe(user="User to remove")
async def unwhitelist_user(interaction: discord.Interaction, user: discord.User):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return
    if user.id not in whitelist["users"]:
        await interaction.response.send_message(f"⚠️ Not whitelisted.", ephemeral=True)
        return
    whitelist["users"].remove(user.id)
    save_whitelist()
    await interaction.response.send_message(f"✅ Removed {user.mention}", ephemeral=True)

@bot.tree.command(name="whitelist_role")
@app_commands.describe(role="Role to whitelist")
async def whitelist_role(interaction: discord.Interaction, role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return
    if role.id in whitelist["roles"]:
        await interaction.response.send_message(f"⚠️ Already whitelisted.", ephemeral=True)
        return
    whitelist["roles"].append(role.id)
    save_whitelist()
    await interaction.response.send_message(f"✅ Whitelisted {role.mention}", ephemeral=True)

@bot.tree.command(name="unwhitelist_role")
@app_commands.describe(role="Role to remove")
async def unwhitelist_role(interaction: discord.Interaction, role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return
    if role.id not in whitelist["roles"]:
        await interaction.response.send_message(f"⚠️ Not whitelisted.", ephemeral=True)
        return
    whitelist["roles"].remove(role.id)
    save_whitelist()
    await interaction.response.send_message(f"✅ Removed {role.mention}", ephemeral=True)

@bot.tree.command(name="whitelist_list")
async def whitelist_list(interaction: discord.Interaction):
    embed = discord.Embed(title="⚪ Whitelist", color=discord.Color.blue())
    
    if whitelist["users"]:
        users = [f"<@{uid}> ({uid})" for uid in whitelist["users"][:10]]
        if len(whitelist["users"]) > 10:
            users.append(f"... and {len(whitelist['users']) - 10} more")
        embed.add_field(name=f"Users ({len(whitelist['users'])})", value="\n".join(users), inline=False)
    else:
        embed.add_field(name="Users", value="None", inline=False)
    
    if whitelist["roles"]:
        roles = [f"<@&{rid}> ({rid})" for rid in whitelist["roles"][:10]]
        if len(whitelist["roles"]) > 10:
            roles.append(f"... and {len(whitelist['roles']) - 10} more")
        embed.add_field(name=f"Roles ({len(whitelist['roles'])})", value="\n".join(roles), inline=False)
    else:
        embed.add_field(name="Roles", value="None", inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="addkey")
@app_commands.describe(api_key="Gemini API key")
async def addkey(interaction: discord.Interaction, api_key: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return
    if api_key in config["gemini_api_keys"]:
        await interaction.response.send_message("⚠️ Key already exists.", ephemeral=True)
        return
    config["gemini_api_keys"].append(api_key)
    save_config()
    await interaction.response.send_message(f"✅ Added key! Total: {len(config['gemini_api_keys'])}", ephemeral=True)

@bot.tree.command(name="listkeys")
async def listkeys(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return
    if not config["gemini_api_keys"]:
        await interaction.response.send_message("⚠️ No keys configured.", ephemeral=True)
        return
    
    key_list = "\n".join([
        f"{'➡️' if i == config['current_key_index'] else '  '} Key #{i+1}: {key[:10]}...{key[-4:]}" 
        for i, key in enumerate(config["gemini_api_keys"])
    ])
    await interaction.response.send_message(f"**API Keys ({len(config['gemini_api_keys'])})**:\n```{key_list}```", ephemeral=True)

@bot.tree.command(name="removekey")
@app_commands.describe(key_number="Key number to remove")
async def removekey(interaction: discord.Interaction, key_number: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return
    if key_number < 1 or key_number > len(config["gemini_api_keys"]):
        await interaction.response.send_message(f"❌ Invalid. Must be 1-{len(config['gemini_api_keys'])}", ephemeral=True)
        return
    
    config["gemini_api_keys"].pop(key_number - 1)
    if config["current_key_index"] >= len(config["gemini_api_keys"]) and config["gemini_api_keys"]:
        config["current_key_index"] = 0
    save_config()
    await interaction.response.send_message(f"✅ Removed key #{key_number}", ephemeral=True)

@bot.tree.command(name="user")
@app_commands.describe(user="User to check")
async def check_user(interaction: discord.Interaction, user: discord.User):
    user_violations = [log for log in violation_logs if log["user_id"] == user.id]
    
    if not user_violations:
        embed = discord.Embed(title="✅ Clean Record", description=f"{user.mention} has no violations",
                              color=discord.Color.green())
        embed.set_thumbnail(url=user.display_avatar.url)
        if user.id in whitelist["users"]:
            embed.add_field(name="Status", value="⚪ Whitelisted", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    embed = discord.Embed(title=f"📋 History: {user.name}",
                          description=f"**Total:** {len(user_violations)} violations",
                          color=discord.Color.red())
    embed.set_thumbnail(url=user.display_avatar.url)
    
    for i, v in enumerate(user_violations[-5:], 1):
        timestamp = datetime.fromisoformat(v["timestamp"]).strftime("%Y-%m-%d %H:%M")
        severity = v.get("severity", "?")
        content = v["message_content"][:80] + "..." if len(v["message_content"]) > 80 else v["message_content"]
        embed.add_field(
            name=f"#{len(user_violations) - 5 + i}",
            value=f"**{timestamp}** | {severity}/10\n`{content}`",
            inline=False
        )
    
    if len(user_violations) > 5:
        embed.set_footer(text=f"Showing last 5 of {len(user_violations)}")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="setup")
@app_commands.describe(channel="Channel to monitor")
async def setup(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return
    config["monitored_channel_id"] = channel.id
    save_config()
    await interaction.response.send_message(f"✅ Monitoring {channel.mention}", ephemeral=True)

@bot.tree.command(name="setlog")
@app_commands.describe(channel="Log channel")
async def setlog(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return
    config["log_channel_id"] = channel.id
    save_config()
    await interaction.response.send_message(f"✅ Log channel: {channel.mention}", ephemeral=True)

@bot.tree.command(name="toggle")
@app_commands.describe(enabled="Enable or disable")
async def toggle(interaction: discord.Interaction, enabled: bool):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return
    config["enabled"] = enabled
    save_config()
    status = "✅ ENABLED" if enabled else "❌ DISABLED"
    await interaction.response.send_message(f"Bot is now **{status}**", ephemeral=True)

@bot.tree.command(name="status")
async def status(interaction: discord.Interaction):
    monitored = bot.get_channel(config.get("monitored_channel_id"))
    log_ch = bot.get_channel(config.get("log_channel_id"))
    mod_mode = config.get("mod_mode", "calm")
    
    embed = discord.Embed(title="🛡️ Bot Status", color=discord.Color.blue())
    embed.add_field(name="Enabled", value="✅ Yes" if config["enabled"] else "❌ No", inline=True)
    embed.add_field(name="Mode", value=f"**{mod_mode.upper()}**", inline=True)
    embed.add_field(name="Threshold", value=f"{config.get('severity_threshold', 7)}/10", inline=True)
    embed.add_field(name="Monitored", value=monitored.mention if monitored else "Not set", inline=True)
    embed.add_field(name="Log Channel", value=log_ch.mention if log_ch else "Not set", inline=True)
    embed.add_field(name="Patterns", value=str(len(slur_patterns)), inline=True)
    embed.add_field(name="API Keys", value=str(len(config["gemini_api_keys"])), inline=True)
    embed.add_field(name="Today's Scans", value=str(daily_stats["messages_scanned"]), inline=True)
    embed.add_field(name="Today's Flags", value=str(daily_stats["messages_flagged"]), inline=True)
    embed.add_field(name="Whitelist", value=f"{len(whitelist['users'])} users, {len(whitelist['roles'])} roles", inline=False)
    
    if mod_mode == "relax":
        embed.add_field(name="ℹ️ Relax Mode", value="NO AI - Pattern-only, instant delete", inline=False)
    elif mod_mode == "strict":
        embed.add_field(name="⚠️ Strict Mode", value="ALL messages checked with AI", inline=False)
    else:
        embed.add_field(name="ℹ️ Calm Mode", value="Only detected slurs checked with AI", inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="forcereport")
async def forcereport(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admin only.", ephemeral=True)
        return
    await interaction.response.send_message("⏳ Generating report...", ephemeral=True)
    await generate_daily_report()

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if not config["enabled"] or message.channel.id != config.get("monitored_channel_id"):
        return
    
    if isinstance(message.author, discord.Member) and is_whitelisted(message.author):
        return
    
    try:
        daily_stats["messages_scanned"] += 1
        current_hour = datetime.now().hour
        daily_stats["hourly_scans"][str(current_hour)] += 1
        save_stats()
        
        mod_mode = config.get("mod_mode", "calm")
        
        # ============================================
        # STRICT MODE: Check ALL messages with AI
        # NO pattern detection, NO pre-filtering
        # ============================================
        if mod_mode == "strict":
            print(f"[STRICT MODE] Checking message with AI (no pattern filtering)")
            
            # Extract emojis for context
            emoji_names = extract_emoji_names(message.content)
            emoji_text = " ".join(emoji_names) if emoji_names else ""
            full_text = message.content
            if emoji_text:
                full_text += " [emojis: " + emoji_text + "]"
            
            if emoji_names:
                print(f"[STRICT] Found {len(emoji_names)} emoji(s): {emoji_names[:10]}")
            
            # Translate if needed
            translated_text = full_text
            if full_text:
                try:
                    translated_text, detected_lang = await translate_text_free(full_text)
                    if detected_lang != "en" and detected_lang != "unknown":
                        print(f"[STRICT] Translated: {detected_lang} → en")
                except Exception as e:
                    print(f"[STRICT] Translation failed: {e}")
                    translated_text = full_text
            
            # OCR check if image present
            ocr_text = None
            if TESSERACT_AVAILABLE and message.attachments:
                for attachment in message.attachments:
                    if attachment.content_type and attachment.content_type.startswith('image'):
                        try:
                            ocr_text = await ocr_image_free(attachment.url)
                            if ocr_text:
                                print(f"[STRICT] OCR: '{ocr_text[:50]}'")
                                translated_ocr, _ = await translate_text_free(ocr_text)
                                translated_text += f"\n[Image text: {translated_ocr}]"
                        except:
                            pass
            
            # Send EVERYTHING to AI for analysis
            print(f"[STRICT] Sending to Gemini: '{translated_text[:100]}...'")
            severity_result = await check_severity_with_gemini(
                translated_text or "empty message",
                ["content check - strict mode"]
            )
            
            severity = severity_result.get("severity", 0)
            threshold = config.get("severity_threshold", 7)
            
            print(f"[STRICT] AI returned severity: {severity}/10 (threshold: {threshold})")
            print(f"[STRICT] AI context: {severity_result.get('context')} | Reason: {severity_result.get('reason')}")
            
            # Take action if meets threshold
            if severity >= threshold:
                try:
                    await message.delete()
                    print(f"[STRICT] ❌ DELETED (severity {severity} ≥ {threshold})")
                except Exception as e:
                    print(f"[STRICT] Delete failed: {e}")
                
                # Send DM
                try:
                    dm_embed = discord.Embed(
                        title="⚠️ Message Removed - Strict Mode",
                        description="Your message was flagged by AI moderation",
                        color=discord.Color.red()
                    )
                    dm_embed.add_field(
                        name="AI Analysis",
                        value=f"**Severity:** {severity}/10\n**Reason:** {severity_result.get('reason', 'Flagged by AI')}",
                        inline=False
                    )
                    dm_embed.add_field(name="Server", value=message.guild.name, inline=True)
                    dm_embed.add_field(name="Channel", value=message.channel.name, inline=True)
                    dm_embed.set_footer(text="Strict mode - All messages checked | Contact mods if mistake")
                    await message.author.send(embed=dm_embed)
                except:
                    pass
                
                # Log violation
                reason = f"Strict mode AI check: Severity {severity}/10 - {severity_result.get('reason')}"
                await log_violation(message, reason, translated_text, severity_result, ocr_text)
            else:
                print(f"[STRICT] ✅ ALLOWED (severity {severity} < {threshold})")
            
            # Exit here - strict mode processing complete
            return
        
        # ============================================
        # CALM/RELAX MODE: Pattern detection first
        # ============================================
        
        # Extract ALL emoji names (comprehensive)
        emoji_names = extract_emoji_names(message.content)
        # ============================================
        # CALM/RELAX MODE: Pattern detection first
        # ============================================
        
        # Extract ALL emoji names (comprehensive)
        emoji_names = extract_emoji_names(message.content)
        emoji_text = " ".join(emoji_names) if emoji_names else ""
        
        if emoji_names:
            print(f"[EMOJI] Detected {len(emoji_names)} emoji name(s)")
            print(f"[EMOJI] Names: {emoji_names[:10]}")  # Show first 10
        
        # Combine message content with emoji names for comprehensive checking
        full_text = message.content
        if emoji_text:
            full_text += " " + emoji_text
        
        # Translate message (including emoji text)
        translated_text = ""
        detected_lang = "unknown"
        
        if full_text:
            try:
                translated_text, detected_lang = await translate_text_free(full_text)
                if detected_lang != "en" and detected_lang != "unknown":
                    print(f"[TRANSLATE] {detected_lang} → en: '{full_text[:50]}...' → '{translated_text[:50]}...'")
            except Exception as e:
                print(f"⚠️ Translation failed: {e}")
                translated_text = full_text
        
        # STRICT MODE: Check ALL messages with AI (no pattern detection needed)
        if mod_mode == "strict":
            print(f"[STRICT MODE] Sending ALL messages to AI (no pre-filtering)")
            
            # Send everything to AI
            severity_result = await check_severity_with_gemini(
                translated_text or full_text,
                ["general content check"]  # No specific slurs detected, checking everything
            )
            severity = severity_result.get("severity", 0)
            threshold = config.get("severity_threshold", 7)
            
            print(f"[AI] Severity: {severity}/10 (threshold: {threshold})")
            
            # Only flag if AI rates it high enough
            if severity >= threshold:
                try:
                    await message.delete()
                    print(f"[ACTION] Deleted (severity {severity} ≥ {threshold})")
                except Exception as e:
                    print(f"❌ Delete failed: {e}")
                
                # Send DM
                try:
                    dm_embed = discord.Embed(
                        title="⚠️ Message Removed",
                        description="Your message was removed by moderation",
                        color=discord.Color.red()
                    )
                    dm_embed.add_field(
                        name="Reason",
                        value=f"Severity: **{severity}/10**\n{severity_result.get('reason', 'Inappropriate content')}",
                        inline=False
                    )
                    dm_embed.add_field(name="Server", value=message.guild.name, inline=True)
                    dm_embed.add_field(name="Channel", value=message.channel.name, inline=True)
                    dm_embed.set_footer(text="Contact moderators if this is a mistake")
                    await message.author.send(embed=dm_embed)
                except:
                    pass
                
                reason = f"AI detected: Severity {severity}/10 (Strict mode - all messages checked)"
                await log_violation(message, reason, translated_text, severity_result, None)
            else:
                print(f"[ACTION] Allowed (severity {severity} < {threshold})")
            
            return  # Done with strict mode processing
        
        # CALM/RELAX MODE: Pattern detection first
        # Check for slurs in BOTH original and translated (including emoji names)
        has_slur_original, found_slurs_original = contains_slur(full_text)
        has_slur_translated, found_slurs_translated = contains_slur(translated_text)
        
        has_slur = has_slur_original or has_slur_translated
        all_found_slurs = list(set(found_slurs_original + found_slurs_translated))
        
        # OCR for images (optional - only if Tesseract available)
        ocr_text = None
        if TESSERACT_AVAILABLE and message.attachments:
            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith('image'):
                    try:
                        ocr_text = await ocr_image_free(attachment.url)
                        if ocr_text:
                            print(f"[OCR] Extracted: '{ocr_text[:100]}'")
                            translated_ocr, _ = await translate_text_free(ocr_text)
                            
                            has_slur_ocr_orig, found_slurs_ocr_orig = contains_slur(ocr_text)
                            has_slur_ocr_trans, found_slurs_ocr_trans = contains_slur(translated_ocr)
                            
                            if has_slur_ocr_orig or has_slur_ocr_trans:
                                has_slur = True
                                all_found_slurs.extend(found_slurs_ocr_orig + found_slurs_ocr_trans)
                                all_found_slurs = list(set(all_found_slurs))  # Remove duplicates
                                print(f"[OCR] Slurs found: {found_slurs_ocr_orig + found_slurs_ocr_trans}")
                            
                            translated_text += f"\n[Image text: {translated_ocr}]"
                    except Exception as e:
                        print(f"⚠️ OCR error: {e}")
        elif not TESSERACT_AVAILABLE and message.attachments:
            # Silently skip OCR if images present but Tesseract not available
            pass
        
        # If slurs detected
        if has_slur:
            all_found_slurs = list(set(all_found_slurs))
            print(f"[DETECT] Found {len(all_found_slurs)} slur(s): {all_found_slurs[:5]}...")  # Show first 5
            
            if emoji_names:
                print(f"[DETECT] (Checked {len(emoji_names)} emoji name(s))")
            
            # RELAX MODE: No AI, instant delete
            if mod_mode == "relax":
                print(f"[RELAX MODE] Instant delete (no AI check)")
                severity_result = {
                    "is_harmful": True,
                    "severity": 10,
                    "reason": f"Pattern match: {', '.join(all_found_slurs[:3])} (Relax mode - no AI)",
                    "context": "pattern-only"
                }
                
                try:
                    await message.delete()
                    print(f"[ACTION] Deleted message from {message.author}")
                except Exception as e:
                    print(f"❌ Delete failed: {e}")
                
                # Send DM
                try:
                    dm_embed = discord.Embed(
                        title="⚠️ Message Removed",
                        description="Your message contained prohibited content",
                        color=discord.Color.red()
                    )
                    dm_embed.add_field(
                        name="Reason",
                        value=f"Pattern match: {', '.join(all_found_slurs[:3])}\n(Relax mode - instant removal)",
                        inline=False
                    )
                    dm_embed.add_field(name="Server", value=message.guild.name, inline=True)
                    dm_embed.add_field(name="Channel", value=message.channel.name, inline=True)
                    dm_embed.set_footer(text="Contact moderators if this is a mistake")
                    await message.author.send(embed=dm_embed)
                except:
                    pass
                
                reason = f"Pattern match: {', '.join(all_found_slurs[:5])} (Relax mode)"
                await log_violation(message, reason, translated_text, severity_result, ocr_text)
                
            # CALM MODE: Use AI for detected slurs only
            else:  # calm mode
                print(f"[CALM MODE] Checking detected slurs with AI...")
                severity_result = await check_severity_with_gemini(
                    translated_text or full_text, 
                    all_found_slurs
                )
                severity = severity_result.get("severity", 10)
                threshold = config.get("severity_threshold", 7)
                
                print(f"[AI] Severity: {severity}/10 (threshold: {threshold})")
                
                # Take action if severity meets threshold
                if severity >= threshold:
                    try:
                        await message.delete()
                        print(f"[ACTION] Deleted (severity {severity} ≥ {threshold})")
                    except Exception as e:
                        print(f"❌ Delete failed: {e}")
                    
                    # Send DM
                    try:
                        dm_embed = discord.Embed(
                            title="⚠️ Message Removed",
                            description="Your message was removed by moderation",
                            color=discord.Color.orange()
                        )
                        dm_embed.add_field(
                            name="Reason",
                            value=f"Severity: **{severity}/10**\n{severity_result.get('reason', 'Inappropriate content')}",
                            inline=False
                        )
                        dm_embed.add_field(name="Server", value=message.guild.name, inline=True)
                        dm_embed.add_field(name="Channel", value=message.channel.name, inline=True)
                        dm_embed.set_footer(text="Contact moderators if this is a mistake")
                        await message.author.send(embed=dm_embed)
                    except:
                        pass
                else:
                    print(f"[ACTION] Logged only (severity {severity} < {threshold})")
                
                reason = f"Detected: {', '.join(all_found_slurs[:5])} - Severity: {severity}/10"
                await log_violation(message, reason, translated_text, severity_result, ocr_text)
            
    except Exception as e:
        print(f"❌ Error processing message: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    
    if not TOKEN:
        if os.path.exists("token.txt"):
            with open("token.txt", "r") as f:
                TOKEN = f.read().strip()
            print("✅ Loaded token from token.txt")
        else:
            print("=" * 50)
            print("❌ ERROR: DISCORD_BOT_TOKEN not set")
            print("=" * 50)
            print("\n⚠️ CRITICAL: Reset your token first!")
            print("Your token was posted publicly in chat.")
            print("\n1. Go to https://discord.com/developers/applications")
            print("2. Your Bot → Bot → Reset Token")
            print("3. Copy NEW token")
            print("4. Add to .env or token.txt")
            print("=" * 50)
            exit(1)
    
    print(f"✅ Token loaded")
    print(f"🚀 Starting bot with Gemini 2.0 Flash...")
    
    # Start keepalive server if available
    if KEEPALIVE_AVAILABLE:
        keep_alive()
        start_self_ping()
        print("✅ Keepalive server started - bot will stay online")
    else:
        print("ℹ️ Keepalive not available (optional) - install Flask to enable")
    
    bot.run(TOKEN)
